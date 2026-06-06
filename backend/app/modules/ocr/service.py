import io
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import get_settings
from app.modules.storage.minio_service import get_minio_service
from app.shared.models.document import Document, OCRResult
from app.modules.ocr.engines.paddleocr_engine import extract_text_paddleocr
from app.modules.ocr.engines.tesseract_engine import extract_text_tesseract

logger = logging.getLogger(__name__)
settings = get_settings()


class OCRService:

    @staticmethod
    async def process_document(
        document_id: int,
        db: AsyncSession
    ) -> Optional[OCRResult]:
        stmt = select(Document).where(Document.id == document_id)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            return None

        document.status = "processing"
        await db.commit()

        try:
            minio_service = get_minio_service()
            file_data = minio_service.download_file(document.storage_path)

            if not file_data:
                document.status = "error"
                await db.commit()
                logger.error(f"Failed to download file for doc {document_id}")
                return None

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
            await db.commit()
            await db.refresh(ocr_result)

            return ocr_result

        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            document.status = "error"
            await db.commit()
            return None

    @staticmethod
    async def process_document_by_url(
        file_data: bytes,
        db: AsyncSession,
        document_id: int
    ) -> Optional[OCRResult]:
        texto, confianca = await extract_text_paddleocr(file_data)

        engine = "paddleocr"
        if not texto:
            texto, confianca = await extract_text_tesseract(file_data)
            engine = "tesseract"

        if not texto:
            return None

        ocr_result = OCRResult(
            document_id=document_id,
            texto_extraido=texto,
            confianca=confianca,
            engine_utilizada=engine,
            status="success"
        )

        db.add(ocr_result)
        await db.commit()
        await db.refresh(ocr_result)

        return ocr_result

    @staticmethod
    async def get_ocr_result(
        document_id: int,
        db: AsyncSession
    ) -> Optional[OCRResult]:
        stmt = select(OCRResult).where(OCRResult.document_id == document_id).order_by(OCRResult.created_at.desc())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_document_status(
        document_id: int,
        db: AsyncSession
    ) -> Optional[str]:
        stmt = select(Document.status).where(Document.id == document_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
