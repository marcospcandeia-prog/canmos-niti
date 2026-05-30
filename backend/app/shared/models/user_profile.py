from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    profissao = Column(String(100), nullable=True)
    estado_civil = Column(String(50), nullable=True)
    possui_dependentes = Column(Boolean, default=False)
    possui_investimentos = Column(Boolean, default=False)
    possui_imoveis = Column(Boolean, default=False)
    possui_mei = Column(Boolean, default=False)

    user = relationship("User", back_populates="profile")
