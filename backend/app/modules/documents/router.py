import hashlib
import uuid
import threading
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models import User, Document, DocumentStatus, OCRResult, OCRStatus
from app.modules.storage.service import upload_file_to_storage
from app.modules.ocr.worker import process_document_sync

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/jpg",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validação de tipo
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de arquivo não suportado. Use: PDF, JPG ou PNG"
        )

    content = await file.read()

    # Validação de tamanho
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Arquivo muito grande. Máximo: 10MB"
        )

    # Hash do arquivo (integridade + dedup)
    file_hash = hashlib.sha256(content).hexdigest()

    # Verificar duplicata
    existing = db.query(Document).filter(
        Document.user_id == current_user.id,
        Document.hash_arquivo == file_hash,
    ).first()
    if existing:
        return {"message": "Documento já enviado anteriormente", "document_id": str(existing.id)}

    # Upload para MinIO
    storage_path = f"users/{current_user.id}/documents/{uuid.uuid4()}/{file.filename}"
    await upload_file_to_storage(content, storage_path, file.content_type)

    # Salvar no banco
    document = Document(
        user_id=current_user.id,
        nome_original=file.filename,
        storage_path=storage_path,
        mime_type=file.content_type,
        hash_arquivo=file_hash,
        tamanho_bytes=str(len(content)),
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    db.flush()

    # Criar registro OCR pendente
    ocr_result = OCRResult(
        document_id=document.id,
        status=OCRStatus.PENDING,
    )
    db.add(ocr_result)
    db.commit()
    db.refresh(document)

    # Disparar OCR em background automaticamente
    doc_id = str(document.id)
    background_tasks.add_task(process_document_sync, doc_id)

    return {
        "message": "Documento enviado com sucesso. Processamento OCR iniciado.",
        "document_id": doc_id,
        "status": document.status,
    }


@router.get("/", response_model=List[dict])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.created_at.desc()).all()

    return [
        {
            "id": str(d.id),
            "nome_original": d.nome_original,
            "tipo": d.tipo,
            "status": d.status,
            "mime_type": d.mime_type,
            "tamanho_bytes": d.tamanho_bytes,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.get("/{document_id}")
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    return {
        "id": str(doc.id),
        "nome_original": doc.nome_original,
        "tipo": doc.tipo,
        "status": doc.status,
        "ocr_status": doc.ocr_result.status if doc.ocr_result else None,
        "created_at": doc.created_at.isoformat(),
    }
