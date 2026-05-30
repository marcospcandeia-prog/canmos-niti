import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel


class DocumentType(str, enum.Enum):
    INFORME_RENDIMENTOS = "informe_rendimentos"
    RECIBO_MEDICO = "recibo_medico"
    DESPESA_EDUCACAO = "despesa_educacao"
    EXTRATO_BANCARIO = "extrato_bancario"
    EXTRATO_CORRETORA = "extrato_corretora"
    DARF = "darf"
    NOTA_FISCAL = "nota_fiscal"
    OUTROS = "outros"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    OCR_DONE = "ocr_done"
    CLASSIFIED = "classified"
    TAX_EVENTS_CREATED = "tax_events_created"
    ERROR = "error"


class Document(BaseModel):
    __tablename__ = "documents"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tipo = Column(Enum(DocumentType), default=DocumentType.OUTROS, nullable=False)
    nome_original = Column(String(500), nullable=False)
    storage_path = Column(String(1000), nullable=False)
    mime_type = Column(String(100), nullable=False)
    hash_arquivo = Column(String(64), nullable=False)
    tamanho_bytes = Column(String(20), nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    ano_base = Column(String(4), nullable=True)

    user = relationship("User", back_populates="documents")
    ocr_result = relationship("OCRResult", back_populates="document", uselist=False)
    tax_events = relationship("TaxEvent", back_populates="document")
