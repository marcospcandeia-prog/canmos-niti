from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.audit.service import AuditService
from app.modules.users.service import UserService
from app.shared.models.user import User
from app.shared.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        updated = service.update_profile(user.id, nome=data.nome, telefone=data.telefone)
        AuditService.log(db, user.id, "update_profile", "user", user.id, {})
        return UserResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
