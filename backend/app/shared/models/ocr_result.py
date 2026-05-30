import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class OCREngine(str, enum.Enum):
    PADDLE = "paddleocr"
    TESSERACT = "tesseract"


class OCRStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class OCRResult(BaseModel):
    __tablename__ = "ocr_results"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, unique=True)
    texto_extraido = Column(Text, nullable=True)
    confianca = Column(Float, nullable=True)
    engine_utilizada = Column(Enum(OCREngine), nullable=True)
    status = Column(Enum(OCRStatus), default=OCRStatus.PENDING, nullable=False)
    erro_msg = Column(String(500), nullable=True)

    document = relationship("Document", back_populates="ocr_result")
