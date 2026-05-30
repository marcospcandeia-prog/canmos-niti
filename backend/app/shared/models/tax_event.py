import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel


class TaxCategory(str, enum.Enum):
    RENDIMENTO_TRIBUTAVEL = "rendimento_tributavel"
    RENDIMENTO_ISENTO = "rendimento_isento"
    DEDUCAO_MEDICA = "deducao_medica"
    DEDUCAO_EDUCACAO = "deducao_educacao"
    DEDUCAO_DEPENDENTE = "deducao_dependente"
    RETENCAO_FONTE = "retencao_fonte"
    INVESTIMENTO = "investimento"
    IMOVEL = "imovel"
    OUTROS = "outros"


class TaxEvent(BaseModel):
    __tablename__ = "tax_events"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    categoria = Column(Enum(TaxCategory), nullable=False)
    subcategoria = Column(String(100), nullable=True)
    valor = Column(Numeric(15, 2), nullable=False)
    competencia = Column(String(7), nullable=True)  # YYYY-MM
    origem = Column(String(200), nullable=True)
    fonte_pagadora = Column(String(200), nullable=True)
    cnpj_fonte = Column(String(14), nullable=True)
    ano_base = Column(String(4), nullable=True)
    metadata_json = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="tax_events")
    document = relationship("Document", back_populates="tax_events")
