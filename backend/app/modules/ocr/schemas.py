from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OCRResultResponse(BaseModel):
    id: int
    document_id: int
    texto_extraido: str
    confianca: Optional[float]
    engine_utilizada: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OCRProcessRequest(BaseModel):
    document_id: int


class OCRProcessResponse(BaseModel):
    sucesso: bool
    mensagem: str
    resultado: Optional[OCRResultResponse]
