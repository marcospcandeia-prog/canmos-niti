import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def extract_text_tesseract(file_data: bytes) -> tuple[Optional[str], Optional[float]]:
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(file_data))

        text = pytesseract.image_to_string(image, lang='por')
        confidence_data = pytesseract.image_to_data(image, lang='por', output_type=pytesseract.Output.DICT)

        confidences = [int(c) for c in confidence_data['conf'] if c != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        logger.info(f"Tesseract: extracted {len(text)} chars, confidence={avg_confidence:.2f}")
        return text.strip(), avg_confidence

    except ImportError:
        logger.warning("pytesseract not available")
        return None, None
    except Exception as e:
        logger.error(f"Tesseract extraction error: {e}")
        return None, None
