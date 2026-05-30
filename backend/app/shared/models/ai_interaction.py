from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class AIInteraction(BaseModel):
    __tablename__ = "ai_interactions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    pergunta = Column(Text, nullable=False)
    resposta = Column(Text, nullable=True)
    modelo_ia = Column(String(100), nullable=True)
    contexto = Column(String(200), nullable=True)  # ex: "document:uuid" ou "dashboard"

    user = relationship("User", back_populates="ai_interactions")
