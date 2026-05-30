import enum
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_ANNUAL = "premium_annual"


class User(BaseModel):
    __tablename__ = "users"

    nome = Column(String(200), nullable=False)
    cpf = Column(String(11), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=True)
    senha_hash = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    lgpd_consent = Column(Boolean, default=False, nullable=False)
    lgpd_consent_at = Column(String(50), nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    documents = relationship("Document", back_populates="user")
    tax_events = relationship("TaxEvent", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    ai_interactions = relationship("AIInteraction", back_populates="user")
