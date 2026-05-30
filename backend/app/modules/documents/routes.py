from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, get_session_local
from app.core.security import get_current_user
from app.modules.audit.service import AuditService
from app.modules.documents.service import DocumentService
from app.modules.ocr.service import OcrService
from app.shared.models.document import OcrResult, TaxEvent
from app.shared.models.user import User
from app.shared.schemas.document import DocumentDetailResponse, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


def run_ocr_background(document_id: str, file_content: bytes):
    session = get_session_local()()
    try:
        import asyncio
        ocr_service = OcrService(session)
        asyncio.run(ocr_service.process_document(document_id, file_content))
    finally:
        session.close()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tipo: str = Form("outro"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede o limite de {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )

    service = DocumentService(db)
    content = await file.read()

    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede o limite de {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )
    doc = await service.upload(
        user_id=user.id,
        file_content=content,
        filename=file.filename or "documento",
        mime_type=file.content_type or "application/octet-stream",
        tipo=tipo,
    )

    background_tasks.add_task(run_ocr_background, doc.id, content)

    AuditService.log(db, user.id, "upload", "document", doc.id, {"filename": file.filename})
    return DocumentResponse.model_validate(doc)


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    docs = service.list_by_user(user.id, skip, limit)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.delete("/{doc_id}", status_code=204)
def delete_document(
    doc_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    if not service.delete(doc_id, user.id):
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    AuditService.log(db, user.id, "delete", "document", doc_id, {})


@router.get("/{doc_id}", response_model=DocumentDetailResponse)
def get_document(
    doc_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    doc = service.get_by_id(doc_id, user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    ocr = db.query(OcrResult).filter(OcrResult.document_id == doc.id).first()
    events = db.query(TaxEvent).filter(TaxEvent.document_id == doc.id).all()

    return DocumentDetailResponse(
        **DocumentResponse.model_validate(doc).model_dump(),
        ocr_result=ocr,
        tax_events=events,
    )
