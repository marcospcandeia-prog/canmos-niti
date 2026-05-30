from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.audit.service import AuditService
from app.shared.models.user import User
from app.shared.schemas.user import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = AuditService.get_by_user(db, user.id, limit)
    return [AuditLogResponse.model_validate(log) for log in logs]
