import asyncio
import logging
import os

from sqlalchemy import select, update

from app.core.database.session import get_db
from app.modules.storage.minio_service import get_minio_service
from app.modules.ocr.engines.paddleocr_engine import extract_text_paddleocr
from app.modules.ocr.engines.tesseract_engine import extract_text_tesseract
from app.shared.models.document import Document, OCRResult

logger = logging.getLogger(__name__)

POLL_INTERVAL = int(os.getenv("OCR_POLL_INTERVAL", "10"))
OCR_HOST = os.getenv("OCR_HOST", "http://ocr-service:8001")


async def process_document(document_id: int):
    db = next(get_db())

    try:
        stmt = select(Document).where(Document.id == document_id)
        result = db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            logger.error(f"Document {document_id} not found")
            return

        document.status = "processing"
        db.commit()

        minio_service = get_minio_service()
        file_data = minio_service.download_file(document.storage_path)

        if not file_data:
            document.status = "error"
            db.commit()
            logger.error(f"Failed to download file for document {document_id}")
            return

        texto, confianca, engine = None, None, "paddleocr"
        texto, confianca = await extract_text_paddleocr(file_data)

        if not texto:
            engine = "tesseract"
            texto, confianca = await extract_text_tesseract(file_data)

        ocr_result = OCRResult(
            document_id=document.id,
            texto_extraido=texto or "",
            confianca=confianca,
            engine_utilizada=engine,
            status="success" if texto else "failed"
        )

        db.add(ocr_result)
        document.status = "processed" if texto else "error"
        db.commit()
        logger.info(f"Document {document_id}: {document.status}")

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        try:
            db.rollback()
            stmt = select(Document).where(Document.id == document_id)
            result = db.execute(stmt)
            document = result.scalar_one_or_none()
            if document:
                document.status = "error"
                db.commit()
        except Exception:
            pass


async def poll_pending_documents():
    while True:
        try:
            db = next(get_db())

            stmt = (
                select(Document)
                .where(Document.status == "pending")
                .limit(5)
            )
            result = db.execute(stmt)
            pending = result.scalars().all()

            for doc in pending:
                logger.info(f"Processing pending document {doc.id}")
                await process_document(doc.id)

        except Exception as e:
            logger.error(f"Poll error: {e}")

        await asyncio.sleep(POLL_INTERVAL)


def run_worker():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger.info("OCR Worker started, polling every %ds", POLL_INTERVAL)
    asyncio.run(poll_pending_documents())


if __name__ == "__main__":
    run_worker()
