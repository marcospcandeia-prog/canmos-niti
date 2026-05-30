from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token, get_current_user
from app.modules.audit.service import AuditService
from app.modules.auth.service import AuthService
from app.shared.models.user import User
from app.shared.schemas.user import (
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserProfileFull,
    UserProfileResponse,
    UserProfileUpdate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.register(
            nome=data.nome,
            cpf=data.cpf,
            email=data.email,
            senha=data.senha,
            telefone=data.telefone,
        )
        _, access_token, refresh_token = service.login(data.email, data.senha)
        AuditService.log(db, user.id, "register", "user", user.id, {"email": user.email})
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user, access_token, refresh_token = service.login(data.email, data.senha)
        AuditService.log(db, user.id, "login", "user", user.id, {"email": user.email})
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        new_access, new_refresh = service.refresh_token(data.refresh_token)
        payload = service.db.query(User).filter(
            User.uuid == decode_token(data.refresh_token).get("sub")
        ).first()
        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            user=UserResponse.model_validate(payload),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    AuditService.log(db, user.id, "logout", "user", user.id, {})
    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=UserProfileFull)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AuthService(db)
    profile = service.get_profile(user.id)
    return UserProfileFull(
        **UserResponse.model_validate(user).model_dump(),
        profile=UserProfileResponse.model_validate(profile),
    )


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    data: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    profile = service.update_profile(
        user.id,
        profissao=data.profissao,
        estado_civil=data.estado_civil,
        possui_dependentes=data.possui_dependentes,
        possui_investimentos=data.possui_investimentos,
    )
    AuditService.log(db, user.id, "update_profile", "user", user.id, data.model_dump(exclude_none=True))
    return UserProfileResponse.model_validate(profile)
