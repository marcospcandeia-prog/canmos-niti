import io
import logging
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from app.modules.ocr.engines.paddleocr_engine import extract_text_paddleocr
from app.modules.ocr.engines.tesseract_engine import extract_text_tesseract

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR"])


class OCRResponse(BaseModel):
    texto_extraido: str
    confianca: float
    engine_utilizada: str
    sucesso: bool


@router.post("/process", response_model=OCRResponse)
async def process_ocr(file: UploadFile = File(...)):
    file_data = await file.read()

    texto, confianca, engine = None, None, "paddleocr"
    texto, confianca = await extract_text_paddleocr(file_data)

    if not texto:
        engine = "tesseract"
        texto, confianca = await extract_text_tesseract(file_data)

    if not texto:
        raise HTTPException(
            status_code=422,
            detail="Nao foi possivel extrair texto do documento"
        )

    return OCRResponse(
        texto_extraido=texto,
        confianca=confianca or 0.0,
        engine_utilizada=engine,
        sucesso=True
    )


@router.post("/process/base64", response_model=OCRResponse)
async def process_ocr_base64(data: dict):
    import base64

    file_data_b64 = data.get("file_data")
    if not file_data_b64:
        raise HTTPException(status_code=400, detail="file_data is required")

    try:
        file_data = base64.b64decode(file_data_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 data")

    texto, confianca = await extract_text_paddleocr(file_data)

    engine = "paddleocr"
    if not texto:
        engine = "tesseract"
        texto, confianca = await extract_text_tesseract(file_data)

    if not texto:
        raise HTTPException(
            status_code=422,
            detail="Nao foi possivel extrair texto do documento"
        )

    return OCRResponse(
        texto_extraido=texto,
        confianca=confianca or 0.0,
        engine_utilizada=engine,
        sucesso=True
    )


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "paddleocr": _check_paddleocr(),
        "tesseract": _check_tesseract()
    }


def _check_paddleocr() -> bool:
    try:
        from paddleocr import PaddleOCR
        return True
    except ImportError:
        return False


def _check_tesseract() -> bool:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
