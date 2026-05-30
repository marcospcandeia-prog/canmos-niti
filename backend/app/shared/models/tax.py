import enum

from sqlalchemy import JSON, Column, DateTime, Enum, Float, String, Text

from app.core.database import Base
from app.core.utils import generate_uuid, utc_now


class DeclarationStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    COMPLETED = "completed"
    FILED = "filed"


class ValidationSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Declaration(Base):
    __tablename__ = "declarations"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    ano_base = Column(String(4), nullable=False)
    status = Column(Enum(DeclarationStatus), default=DeclarationStatus.DRAFT)
    restituicao_estimada = Column(Float, default=0.0)
    imposto_devido = Column(Float, default=0.0)
    total_rendimentos = Column(Float, default=0.0)
    total_retencao = Column(Float, default=0.0)
    qtd_dependentes = Column(Float, default=0.0)
    total_deducao_dependentes = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class Validation(Base):
    __tablename__ = "validations"

    id = Column(String, primary_key=True, default=generate_uuid)
    declaration_id = Column(String, nullable=False, index=True)
    tipo = Column(String(100))
    severidade = Column(Enum(ValidationSeverity), default=ValidationSeverity.INFO)
    mensagem = Column(Text)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=utc_now)
