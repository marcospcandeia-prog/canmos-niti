from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse
from .service import register_user, login_user, refresh_tokens

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(data, db)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(data, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return refresh_tokens(data.refresh_token, db)


@router.post("/logout")
def logout():
    # Com JWT stateless, logout é gerenciado no cliente
    return {"message": "Logout realizado com sucesso"}
