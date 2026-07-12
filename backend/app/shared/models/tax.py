"""
Tax Event, Declaration and Validation Models
"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from app.core.database.session import Base
from app.shared.models.base import BaseModel, TimestampMixin


class TaxEvent(Base, BaseModel, TimestampMixin):
    """Tax event extracted from documents or manually entered"""
    
    __tablename__ = "tax_events"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Event Classification
    categoria = Column(String(100), nullable=False, index=True)
    # Categorias: rendimento_trabalho, rendimento_investimento, despesa_medica, 
    # despesa_educacao, doacao, pensao_alimenticia, etc
    
    subcategoria = Column(String(100), nullable=True)
    
    # Financial Data
    valor = Column(Numeric(precision=15, scale=2), nullable=False)  # IMPORTANTE: Float → Numeric para precisão
    
    # Period
    competencia = Column(String(7), nullable=False, index=True)  # YYYY-MM format
    
    # Origin
    origem = Column(String(50), default="ocr", nullable=False)  # ocr, manual, importacao
    
    # Additional metadata (JSONB for flexibility)
    metadata_json = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tax_events")
    document = relationship("Document", back_populates="tax_events")
    
    def __repr__(self) -> str:
        return f"<TaxEvent(id={self.id}, user_id={self.user_id}, categoria={self.categoria}, valor={self.valor})>"


class Declaration(Base, BaseModel, TimestampMixin):
    """Tax declaration (IRPF) for a specific year"""
    
    __tablename__ = "declarations"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Year
    ano_base = Column(Integer, nullable=False, index=True)  # 2025, 2026, etc
    
    # Status
    status = Column(String(50), default="rascunho", nullable=False)  # rascunho, finalizada, enviada
    
    # Calculations
    restituicao_estimada = Column(Numeric(precision=15, scale=2), nullable=True)
    imposto_devido = Column(Numeric(precision=15, scale=2), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="declarations")
    validations = relationship("Validation", back_populates="declaration", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Declaration(id={self.id}, user_id={self.user_id}, ano_base={self.ano_base}, status={self.status})>"


class Validation(Base, BaseModel, TimestampMixin):
    """Validation issues found in declarations"""
    
    __tablename__ = "validations"
    
    declaration_id = Column(Integer, ForeignKey("declarations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Validation Type
    tipo = Column(String(100), nullable=False)
    # Tipos: missing_document, valor_inconsistente, deducao_invalida, cpf_invalido, etc
    
    # Severity
    severidade = Column(String(20), default="info", nullable=False)  # info, warning, error
    
    # Message
    mensagem = Column(Text, nullable=False)
    
    # Relationship
    declaration = relationship("Declaration", back_populates="validations")
    
    def __repr__(self) -> str:
        return f"<Validation(id={self.id}, declaration_id={self.declaration_id}, tipo={self.tipo}, severidade={self.severidade})>"
