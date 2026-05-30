"""
OCR Worker — processa documentos pendentes em background.
Pode ser chamado via endpoint ou executado como serviço.
"""
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.shared.models import Document, DocumentStatus, OCRStatus, OCRResult
from .pipeline import process_document


async def process_pending_documents():
    """Processa todos os documentos com status UPLOADED."""
    db: Session = SessionLocal()
    try:
        pending = db.query(Document).filter(
            Document.status.in_([DocumentStatus.UPLOADED, DocumentStatus.OCR_DONE])
        ).limit(10).all()

        for doc in pending:
            process_document(str(doc.id), db)
            await asyncio.sleep(0.1)

        return len(pending)
    finally:
        db.close()


def process_document_sync(document_id: str) -> bool:
    """Processa um documento específico de forma síncrona."""
    db: Session = SessionLocal()
    try:
        return process_document(document_id, db)
    finally:
        db.close()
