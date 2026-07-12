import asyncio
import logging
import os

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config.settings import get_settings
from app.modules.storage.minio_service import get_minio_service
from app.shared.models.document import Document, OCRResult

logger = logging.getLogger(__name__)

POLL_INTERVAL = int(os.getenv("OCR_POLL_INTERVAL", "10"))
settings = get_settings()


async def get_db_session() -> AsyncSession:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return session_factory()


async def call_ocr_api(file_data: bytes) -> tuple[str | None, float | None, str]:
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


async def process_document(document_id: int, db: AsyncSession):
    try:
        stmt = select(Document).where(Document.id == document_id)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            logger.error(f"Document {document_id} not found")
            return

        document.status = "processing"
        await db.commit()

        minio_service = get_minio_service()
        file_data = minio_service.download_file(document.storage_path)

        if not file_data:
            document.status = "error"
            await db.commit()
            logger.error(f"Failed to download file for document {document_id}")
            return

        texto, confianca, engine = await call_ocr_api(file_data)

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
        logger.info(f"Document {document_id}: {document.status}")

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        try:
            await db.rollback()
            stmt = select(Document).where(Document.id == document_id)
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()
            if document:
                document.status = "error"
                await db.commit()
        except Exception:
            pass


async def poll_pending_documents():
    while True:
        try:
            db = await get_db_session()
            try:
                stmt = (
                    select(Document)
                    .where(Document.status == "pending")
                    .limit(5)
                )
                result = await db.execute(stmt)
                pending = result.scalars().all()

                for doc in pending:
                    logger.info(f"Processing pending document {doc.id}")
                    await process_document(doc.id, db)
            finally:
                await db.close()
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
