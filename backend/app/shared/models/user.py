"""
User and UserProfile Models
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database.session import Base
from app.shared.models.base import BaseModel, TimestampMixin


class User(Base, BaseModel, TimestampMixin):
    """User model for authentication and profile"""
    
    __tablename__ = "users"
    
    # UUID for external references (not exposing internal ID)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid4, index=True)
    
    # Personal Information
    nome = Column(String(255), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=True)
    
    # Authentication
    senha_hash = Column(String(255), nullable=False)
    
    # Status
    status = Column(String(20), default="active", nullable=False)  # active, inactive, suspended
    
    # LGPD
    lgpd_consent_at = Column(DateTime, nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    tax_events = relationship("TaxEvent", back_populates="user", cascade="all, delete-orphan")
    declarations = relationship("Declaration", back_populates="user", cascade="all, delete-orphan")
    ai_interactions = relationship("AIInteraction", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, cpf={self.cpf}, email={self.email})>"


class UserProfile(Base, BaseModel, TimestampMixin):
    """Extended user profile information"""
    
    __tablename__ = "user_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Professional/Personal Info
    profissao = Column(String(255), nullable=True)
    estado_civil = Column(String(50), nullable=True)  # solteiro, casado, divorciado, viuvo
    possui_dependentes = Column(Boolean, default=False, nullable=False)
    possui_investimentos = Column(Boolean, default=False, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, profissao={self.profissao})>"
