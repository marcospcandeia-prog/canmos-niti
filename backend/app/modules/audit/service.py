from sqlalchemy.orm import Session

from app.shared.models.audit import AuditLog


class AuditService:
    @staticmethod
    def log(
        db: Session,
        user_id: str,
        action: str,
        entity: str = None,
        entity_id: str = None,
        metadata_json: dict = None,
        ip_address: str = None,
        user_agent: str = None,
    ):
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            metadata_json=metadata_json or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(log)
        db.commit()

    @staticmethod
    def get_by_user(db: Session, user_id: str, limit: int = 50):
        return (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
