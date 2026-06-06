"""
Base Model Classes and Mixins
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class BaseModel:
    """Base model with common attributes"""
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name"""
        return cls.__name__.lower() + 's'
    
    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
