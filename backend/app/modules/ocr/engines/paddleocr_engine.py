import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_ocr_instance = None


def get_paddleocr():
    global _ocr_instance
    if _ocr_instance is None:
        try:
            from paddleocr import PaddleOCR
            _ocr_instance = PaddleOCR(use_angle_cls=True, lang='pt', show_log=False)
            logger.info("PaddleOCR initialized successfully")
        except ImportError:
            logger.warning("paddleocr not available")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            return None
    return _ocr_instance


async def extract_text_paddleocr(file_data: bytes) -> tuple[Optional[str], Optional[float]]:
    ocr = get_paddleocr()
    if ocr is None:
        return None, None

    try:
        image_bytes = io.BytesIO(file_data)
        result = ocr.ocr(image_bytes, cls=True)

        if not result or not result[0]:
            return None, None

        texts = []
        confidences = []

        for line in result[0]:
            bbox, (text, confidence) = line
            texts.append(text)
            confidences.append(confidence)

        full_text = '\n'.join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        logger.info(f"PaddleOCR: extracted {len(texts)} lines, confidence={avg_confidence:.2f}")
        return full_text, avg_confidence

    except Exception as e:
        logger.error(f"PaddleOCR extraction error: {e}")
        return None, None
