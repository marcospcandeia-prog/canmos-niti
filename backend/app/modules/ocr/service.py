import logging
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import get_settings
from app.modules.storage.minio_service import get_minio_service
from app.shared.models.document import Document, OCRResult

logger = logging.getLogger(__name__)
settings = get_settings()


class OCRService:

    @staticmethod
    async def _call_ocr_api(file_data: bytes) -> tuple[Optional[str], Optional[float], str]:
        api_url = f"{settings.OCR_API_HOST}/ocr/process"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    api_url,
                    files={"file": ("document.bin", file_data)},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return (
                        data.get("texto_extraido"),
                        data.get("confianca"),
                        data.get("engine_utilizada", "paddleocr"),
                    )
                logger.error(f"OCR API error {resp.status_code}: {resp.text}")
                return None, None, "paddleocr"
        except httpx.ConnectError:
            logger.warning(f"OCR service not available at {settings.OCR_API_HOST}")
            return None, None, "paddleocr"
        except Exception as e:
            logger.error(f"OCR API call failed: {e}")
            return None, None, "paddleocr"

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

            texto, confianca, engine = await OCRService._call_ocr_api(file_data)

            ocr_result = OCRResult(
                document_id=document.id,
                texto_extraido=texto or "",
                confianca=confianca,
                engine_utilizada=engine,
                status="success" if texto else "failed"
            )

            db.add(ocr_result)

            if texto:
                await OCRService._extrair_eventos(document, texto, db)

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
        texto, confianca, engine = await OCRService._call_ocr_api(file_data)

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
    async def _extrair_eventos(document: Document, texto: str, db: AsyncSession) -> None:
        from app.modules.tax_engine.parsers.classificador import extrair_eventos_de_ocr
        from app.shared.models.tax import TaxEvent

        eventos = extrair_eventos_de_ocr(document.id, texto)

        for evt in eventos:
            tax_event = TaxEvent(
                user_id=document.user_id,
                document_id=document.id,
                categoria=evt["categoria"],
                valor=evt["valor"],
                competencia=evt["competencia"],
                origem="ocr",
                metadata_json=evt.get("metadata"),
            )
            db.add(tax_event)

        if eventos:
            logger.info("Criados %d eventos fiscais para documento %d", len(eventos), document.id)
        else:
            logger.info("Nenhum evento fiscal extraido do documento %d", document.id)

        try:
            from app.modules.ai.rag_service import index_document
            index_document(
                document_id=document.id,
                user_id=document.user_id,
                text=texto,
                metadata={"eventos_extraidos": len(eventos)},
            )
        except Exception as e:
            logger.warning("RAG indexing failed for document %d: %s", document.id, e)

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


async def process_document_background(document_id: int) -> None:
    """Standalone function for background OCR processing.
    Creates its own DB session to avoid sharing the request session."""
    from app.core.database.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await OCRService.process_document(document_id, db)
