"""
Users Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserProfileResponse(BaseModel):
    """Schema for user profile with extended info"""
    
    # User fields
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
    
    # Profile fields
    profissao: Optional[str] = None
    estado_civil: Optional[str] = None
    possui_dependentes: bool = False
    possui_investimentos: bool = False
    
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
                "updated_at": "2026-06-03T22:00:00",
                "profissao": "Engenheiro de Software",
                "estado_civil": "casado",
                "possui_dependentes": True,
                "possui_investimentos": True
            }
        }
    }


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    
    nome: Optional[str] = Field(None, min_length=3, max_length=255, description="Nome completo")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone")
    profissao: Optional[str] = Field(None, max_length=255, description="Profissão")
    estado_civil: Optional[str] = Field(None, description="Estado civil")
    possui_dependentes: Optional[bool] = Field(None, description="Possui dependentes?")
    possui_investimentos: Optional[bool] = Field(None, description="Possui investimentos?")
    
    @field_validator('estado_civil')
    @classmethod
    def validate_estado_civil(cls, v: Optional[str]) -> Optional[str]:
        """Validate estado_civil options"""
        if v is not None:
            valid_options = ["solteiro", "casado", "divorciado", "viuvo"]
            if v not in valid_options:
                raise ValueError(f'Estado civil deve ser um de: {", ".join(valid_options)}')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "João da Silva Santos",
                "telefone": "11988887777",
                "profissao": "Engenheiro de Software",
                "estado_civil": "casado",
                "possui_dependentes": True,
                "possui_investimentos": True
            }
        }
    }


class PasswordChange(BaseModel):
    """Schema for changing password"""
    
    senha_atual: str = Field(..., description="Senha atual")
    senha_nova: str = Field(..., min_length=8, max_length=100, description="Nova senha (mínimo 8 caracteres)")
    senha_nova_confirmacao: str = Field(..., description="Confirmação da nova senha")
    
    @field_validator('senha_nova_confirmacao')
    @classmethod
    def validate_password_match(cls, v: str, info) -> str:
        """Validate that passwords match"""
        if 'senha_nova' in info.data and v != info.data['senha_nova']:
            raise ValueError('Senhas não conferem')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "senha_atual": "senhaAntiga123",
                "senha_nova": "senhaNova456",
                "senha_nova_confirmacao": "senhaNova456"
            }
        }
    }


class UserStats(BaseModel):
    """Schema for user statistics"""
    
    total_documents: int = Field(..., description="Total de documentos enviados")
    documents_processed: int = Field(..., description="Documentos processados")
    total_tax_events: int = Field(..., description="Total de eventos tributários")
    declarations_count: int = Field(..., description="Total de declarações")
    last_activity: Optional[datetime] = Field(None, description="Última atividade")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_documents": 15,
                "documents_processed": 12,
                "total_tax_events": 45,
                "declarations_count": 2,
                "last_activity": "2026-06-03T22:00:00"
            }
        }
    }
