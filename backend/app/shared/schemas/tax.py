from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class DeclarationResponse(BaseModel):
    id: str
    user_id: str
    ano_base: str
    status: str
    restituicao_estimada: float
    imposto_devido: float
    total_rendimentos: float
    total_retencao: float
    qtd_dependentes: float = 0.0
    total_deducao_dependentes: float = 0.0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ValidationResponse(BaseModel):
    id: str
    declaration_id: str
    tipo: Optional[str] = None
    severidade: str
    mensagem: Optional[str] = None
    metadata_json: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AiInteractionResponse(BaseModel):
    id: str
    user_id: str
    pergunta: Optional[str] = None
    resposta: Optional[str] = None
    modelo_ia: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AiQueryRequest(BaseModel):
    pergunta: str
    contexto: Optional[dict] = None
