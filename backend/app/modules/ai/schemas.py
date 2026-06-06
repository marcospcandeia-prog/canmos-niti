from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatRequest(BaseModel):
    mensagem: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    resposta: str
    conversation_id: str
    model: str
    fontes: list[str] = []


class ConversationCreate(BaseModel):
    titulo: str


class ConversationResponse(BaseModel):
    id: int
    titulo: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
