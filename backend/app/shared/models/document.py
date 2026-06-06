"""
Document and OCRResult Models
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database.session import Base
from app.shared.models.base import BaseModel, TimestampMixin


class Document(Base, BaseModel, TimestampMixin):
    """Document uploaded by user"""
    
    __tablename__ = "documents"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document Type
    tipo = Column(String(100), nullable=True)  # informe_rendimentos, recibo_medico, comprovante_educacao, etc
    
    # File Information
    nome_original = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)  # MinIO path
    mime_type = Column(String(100), nullable=False)
    hash_arquivo = Column(String(64), nullable=False, index=True)  # SHA256
    
    # Processing Status
    status = Column(String(50), default="uploaded", nullable=False)  # uploaded, processing, processed, error
    
    # Relationships
    user = relationship("User", back_populates="documents")
    ocr_result = relationship("OCRResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    tax_events = relationship("TaxEvent", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, user_id={self.user_id}, tipo={self.tipo}, status={self.status})>"


class OCRResult(Base, BaseModel, TimestampMixin):
    """OCR extraction result"""
    
    __tablename__ = "ocr_results"
    
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # OCR Output
    texto_extraido = Column(Text, nullable=True)
    confianca = Column(Float, nullable=True)  # 0.0 to 1.0
    engine_utilizada = Column(String(50), nullable=False)  # paddleocr, tesseract
    
    # Status
    status = Column(String(50), default="pending", nullable=False)  # pending, success, failed
    
    # Relationship
    document = relationship("Document", back_populates="ocr_result")
    
    def __repr__(self) -> str:
        return f"<OCRResult(id={self.id}, document_id={self.document_id}, engine={self.engine_utilizada}, status={self.status})>"
