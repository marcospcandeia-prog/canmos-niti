"""
AI Interaction Model
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database.session import Base
from app.shared.models.base import BaseModel, TimestampMixin


class AIInteraction(Base, BaseModel, TimestampMixin):
    """AI copilot interactions with users"""
    
    __tablename__ = "ai_interactions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Conversation
    conversation_id = Column(String(36), nullable=True, index=True)
    pergunta = Column(Text, nullable=False)
    resposta = Column(Text, nullable=True)
    
    # Model Used
    modelo_ia = Column(String(50), nullable=False)  # phi3:mini, qwen2, mistral, etc
    
    # Sources consulted
    fontes_consultadas = Column(Text, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="ai_interactions")
    
    def __repr__(self) -> str:
        return f"<AIInteraction(id={self.id}, user_id={self.user_id}, modelo_ia={self.modelo_ia})>"
