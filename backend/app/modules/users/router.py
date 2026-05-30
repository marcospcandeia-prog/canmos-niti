from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.database import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models import User, UserProfile

router = APIRouter(prefix="/users", tags=["Users"])


class UserProfileUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    profissao: Optional[str] = None
    estado_civil: Optional[str] = None
    possui_dependentes: Optional[bool] = None
    possui_investimentos: Optional[bool] = None
    possui_imoveis: Optional[bool] = None
    possui_mei: Optional[bool] = None


class UserOut(BaseModel):
    id: str
    nome: str
    email: str
    telefone: Optional[str]
    cpf: Optional[str]
    subscription_plan: str
    status: str
    lgpd_consent: bool

    model_config = {"from_attributes": True}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me")
def update_me(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.nome:
        current_user.nome = data.nome
    if data.telefone:
        current_user.telefone = data.telefone
    if data.cpf:
        current_user.cpf = data.cpf

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        if data.profissao is not None:
            profile.profissao = data.profissao
        if data.estado_civil is not None:
            profile.estado_civil = data.estado_civil
        if data.possui_dependentes is not None:
            profile.possui_dependentes = data.possui_dependentes
        if data.possui_investimentos is not None:
            profile.possui_investimentos = data.possui_investimentos

    db.commit()
    db.refresh(current_user)
    return {"message": "Perfil atualizado com sucesso"}
