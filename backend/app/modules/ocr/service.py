"""
OCR Service — PaddleOCR principal, Tesseract fallback.
Totalmente determinístico. Não usa IA para extração.
"""
import io
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class OCROutput:
    texto: str
    confianca: float
    engine: str


def extract_text_from_bytes(content: bytes, mime_type: str) -> OCROutput:
    """Tenta PaddleOCR primeiro, cai para Tesseract se falhar."""
    if mime_type == "application/pdf":
        content = _pdf_to_image(content)

    result = _try_paddle(content)
    if result:
        return result

    return _try_tesseract(content)


def _pdf_to_image(pdf_bytes: bytes) -> bytes:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        mat = fitz.Matrix(2, 2)  # 2x zoom para melhor OCR
        pix = page.get_pixmap(matrix=mat)
        return pix.tobytes("png")
    except Exception:
        return pdf_bytes


def _try_paddle(content: bytes) -> Optional[OCROutput]:
    try:
        from paddleocr import PaddleOCR
        import numpy as np
        from PIL import Image

        ocr = PaddleOCR(use_angle_cls=True, lang="pt", show_log=False)
        img = Image.open(io.BytesIO(content)).convert("RGB")
        img_array = np.array(img)
        result = ocr.ocr(img_array, cls=True)

        if not result or not result[0]:
            return None

        lines = []
        confidences = []
        for line in result[0]:
            text, conf = line[1]
            lines.append(text)
            confidences.append(conf)

        texto = "\n".join(lines)
        confianca = sum(confidences) / len(confidences) if confidences else 0.0

        return OCROutput(texto=texto, confianca=round(confianca, 4), engine="paddleocr")
    except Exception:
        return None


def _try_tesseract(content: bytes) -> OCROutput:
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(content))
        data = pytesseract.image_to_data(img, lang="por", output_type=pytesseract.Output.DICT)
        words = [w for w, c in zip(data["text"], data["conf"]) if int(c) > 30 and w.strip()]
        confs = [int(c) for c in data["conf"] if int(c) > 30]
        texto = pytesseract.image_to_string(img, lang="por")
        confianca = (sum(confs) / len(confs) / 100) if confs else 0.5

        return OCROutput(texto=texto.strip(), confianca=round(confianca, 4), engine="tesseract")
    except Exception as e:
        return OCROutput(texto="", confianca=0.0, engine="tesseract")
