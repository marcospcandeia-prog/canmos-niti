from sqlalchemy import JSON, Column, DateTime, String, Text

from app.core.database import Base
from app.core.utils import generate_uuid, utc_now


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(100))
    entity_id = Column(String(100))
    metadata_json = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class AiInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    pergunta = Column(Text)
    resposta = Column(Text)
    modelo_ia = Column(String(50))
    contexto = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=utc_now)
