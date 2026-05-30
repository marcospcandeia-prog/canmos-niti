import threading
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.shared.models import User, UserProfile
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from .schemas import RegisterRequest, LoginRequest


def register_user(data: RegisterRequest, db: Session) -> dict:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado"
        )

    user = User(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_password(data.senha),
        lgpd_consent=data.lgpd_consent,
        lgpd_consent_at=str(__import__("datetime").datetime.utcnow()),
    )
    db.add(user)
    db.flush()

    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(user)

    # Email boas-vindas em background (não bloqueia o cadastro)
    threading.Thread(
        target=_send_welcome_email, args=(user.email, user.nome), daemon=True
    ).start()

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }


def _send_welcome_email(email: str, nome: str):
    try:
        from app.modules.email.service import send_welcome
        send_welcome(email, nome)
    except Exception:
        pass  # Email falha silenciosamente — não afeta o cadastro


def login_user(data: LoginRequest, db: Session) -> dict:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta suspensa ou inativa"
        )

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }


def refresh_tokens(refresh_token: str, db: Session) -> dict:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }
