"""
Authentication Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Schema for user registration"""
    
    nome: str = Field(..., min_length=3, max_length=255, description="Nome completo")
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF (apenas números)")
    email: EmailStr = Field(..., description="Email válido")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone")
    senha: str = Field(..., min_length=8, max_length=100, description="Senha (mínimo 8 caracteres)")
    lgpd_consent: bool = Field(..., description="Consentimento LGPD obrigatório")
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        """Validate CPF format and check digits"""
        if not v.isdigit():
            raise ValueError('CPF deve conter apenas números')
        if len(v) != 11:
            raise ValueError('CPF deve ter 11 dígitos')

        cpf = [int(d) for d in v]
        if all(d == cpf[0] for d in cpf):
            raise ValueError('CPF inválido (todos dígitos iguais)')

        digito1 = sum(cpf[i] * (10 - i) for i in range(9)) % 11
        digito1 = 0 if digito1 < 2 else 11 - digito1
        if digito1 != cpf[9]:
            raise ValueError('CPF inválido')

        digito2 = sum(cpf[i] * (11 - i) for i in range(10)) % 11
        digito2 = 0 if digito2 < 2 else 11 - digito2
        if digito2 != cpf[10]:
            raise ValueError('CPF inválido')

        return v
    
    @field_validator('lgpd_consent')
    @classmethod
    def validate_lgpd_consent(cls, v: bool) -> bool:
        """Validate LGPD consent is True"""
        if not v:
            raise ValueError('Consentimento LGPD é obrigatório')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "João da Silva",
                "cpf": "12345678900",
                "email": "joao@example.com",
                "telefone": "11999999999",
                "senha": "senhaSegura123",
                "lgpd_consent": True
            }
        }
    }


class UserLogin(BaseModel):
    """Schema for user login"""
    
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., description="Senha do usuário")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "joao@example.com",
                "senha": "senhaSegura123"
            }
        }
    }


class Token(BaseModel):
    """Schema for JWT token response"""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    }


class TokenRefresh(BaseModel):
    """Schema for refresh token request"""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class TokenResponse(BaseModel):
    """Schema for new access token response"""
    
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    }


class UserResponse(BaseModel):
    """Schema for user data response (without sensitive info)"""
    
    id: int
    uuid: UUID
    nome: str
    cpf: str
    email: str
    telefone: Optional[str]
    status: str
    lgpd_consent_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "nome": "João da Silva",
                "cpf": "12345678900",
                "email": "joao@example.com",
                "telefone": "11999999999",
                "status": "active",
                "lgpd_consent_at": "2026-06-03T22:00:00",
                "created_at": "2026-06-03T22:00:00",
                "updated_at": "2026-06-03T22:00:00"
            }
        }
    }


class MessageResponse(BaseModel):
    """Generic message response"""
    
    message: str = Field(..., description="Response message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Operação realizada com sucesso"
            }
        }
    }
