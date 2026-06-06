"""
Audit Middleware
LGPD compliance - log all important actions
"""

from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.audit import AuditLog


async def create_audit_log(
    db: AsyncSession,
    user_id: Optional[int],
    action: str,
    entity: Optional[str] = None,
    entity_id: Optional[int] = None,
    metadata: Optional[dict] = None,
    request: Optional[Request] = None
) -> AuditLog:
    """
    Create audit log entry
    
    Args:
        db: Database session
        user_id: User ID (nullable for system actions)
        action: Action performed (CREATE, UPDATE, DELETE, LOGIN, etc)
        entity: Entity affected (users, documents, etc)
        entity_id: Entity ID
        metadata: Additional metadata (JSON)
        request: FastAPI request (for IP, user agent)
        
    Returns:
        Created audit log
    """
    # Build metadata
    audit_metadata = metadata or {}
    
    if request:
        audit_metadata.update({
            "ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "method": request.method,
            "path": str(request.url.path)
        })
    
    # Create audit log
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        metadata_json=audit_metadata
    )
    
    db.add(audit_log)
    await db.commit()
    
    return audit_log
