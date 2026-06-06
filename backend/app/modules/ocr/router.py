import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models.user import User
from app.shared.models.document import Document, OCRResult
from app.modules.ocr.service import OCRService
from app.modules.ocr.schemas import OCRResultResponse, OCRProcessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post("/process/{document_id}", response_model=OCRProcessResponse)
async def process_document_ocr(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import select
    stmt = select(Document).where(
        Document.id == document_id,
        Document.user_id == current_user.id
    )
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Documento nao encontrado")

    if document.status == "processing":
        raise HTTPException(status_code=400, detail="Documento ja esta sendo processado")

    if document.status == "processed":
        return OCRProcessResponse(
            sucesso=True,
            mensagem="Documento ja foi processado",
            resultado=await _get_existing_result(document_id, db)
        )

    background_tasks.add_task(OCRService.process_document, document_id, db)

    return OCRProcessResponse(
        sucesso=True,
        mensagem="Processamento OCR iniciado",
        resultado=None
    )


@router.get("/result/{document_id}")
async def get_ocr_result(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await OCRService.get_ocr_result(document_id, db)
    if not result:
        status = await OCRService.get_document_status(document_id, db)
        if status == "pending":
            return {"status": "pending", "mensagem": "Documento aguardando processamento"}
        elif status == "processing":
            return {"status": "processing", "mensagem": "Documento sendo processado"}
        elif status == "error":
            return {"status": "error", "mensagem": "Erro no processamento"}
        return {"status": "not_found", "mensagem": "Documento nao encontrado"}

    return OCRResultResponse(
        id=result.id,
        document_id=result.document_id,
        texto_extraido=result.texto_extraido,
        confianca=result.confianca,
        engine_utilizada=result.engine_utilizada,
        status=result.status,
        created_at=result.created_at
    )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "OCR"}


async def _get_existing_result(document_id: int, db: AsyncSession) -> Optional[OCRResultResponse]:
    result = await OCRService.get_ocr_result(document_id, db)
    if not result:
        return None
    return OCRResultResponse(
        id=result.id,
        document_id=result.document_id,
        texto_extraido=result.texto_extraido,
        confianca=result.confianca,
        engine_utilizada=result.engine_utilizada,
        status=result.status,
        created_at=result.created_at
    )
