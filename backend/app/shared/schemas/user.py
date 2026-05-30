from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=200)
    cpf: str = Field(..., min_length=11, max_length=14)
    email: EmailStr
    telefone: Optional[str] = None
    senha: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    senha: str


class UserResponse(BaseModel):
    id: str
    uuid: str
    nome: str
    cpf: str
    email: str
    telefone: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfileUpdate(BaseModel):
    profissao: Optional[str] = None
    estado_civil: Optional[str] = None
    possui_dependentes: Optional[bool] = None
    possui_investimentos: Optional[bool] = None


class UserProfileResponse(BaseModel):
    profissao: Optional[str] = None
    estado_civil: Optional[str] = None
    possui_dependentes: Optional[str] = None
    possui_investimentos: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileFull(UserResponse):
    profile: Optional[UserProfileResponse] = None


class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    entity: Optional[str] = None
    entity_id: Optional[str] = None
    metadata_json: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
