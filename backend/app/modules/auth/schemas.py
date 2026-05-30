from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
import re


class RegisterRequest(BaseModel):
    model_config = ConfigDict()
    nome: str
    email: EmailStr
    senha: str
    lgpd_consent: bool

    @field_validator("senha")
    @classmethod
    def validate_senha(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres")
        return v

    @field_validator("lgpd_consent")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("É necessário aceitar os termos de privacidade (LGPD)")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    nome: str
    email: str
    subscription_plan: str
    status: str

    model_config = {"from_attributes": True}
