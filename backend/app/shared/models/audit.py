"""
Audit Log Model (LGPD Compliance)
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from app.core.database.session import Base
from app.shared.models.base import BaseModel, TimestampMixin


class AuditLog(Base, BaseModel, TimestampMixin):
    """Audit log for LGPD compliance and security tracking"""
    
    __tablename__ = "audit_logs"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    # Nullable because some actions may not have user (e.g., system actions)
    
    # Action Details
    action = Column(String(50), nullable=False, index=True)
    # Actions: CREATE, UPDATE, DELETE, LOGIN, LOGOUT, UPLOAD, DOWNLOAD, EXPORT, etc
    
    # Entity Affected
    entity = Column(String(100), nullable=True, index=True)
    # Entities: users, documents, tax_events, declarations, etc
    
    entity_id = Column(Integer, nullable=True)
    
    # Additional Context (flexible JSON)
    metadata_json = Column(JSON, nullable=True)
    # Example: {"ip": "192.168.1.1", "user_agent": "...", "changes": {...}}
    
    # Relationship
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action}, entity={self.entity})>"
