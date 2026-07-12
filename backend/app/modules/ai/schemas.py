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
    id: str
    titulo: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: int
    conversation_id: str
    role: str
    content: str
    created_at: datetime
