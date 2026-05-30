from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    tipo: str
    nome_original: str
    mime_type: Optional[str] = None
    hash_arquivo: Optional[str] = None
    tamanho_bytes: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OcrResultResponse(BaseModel):
    id: str
    document_id: str
    texto_extraido: Optional[str] = None
    confianca: Optional[float] = None
    engine_utilizada: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaxEventResponse(BaseModel):
    id: str
    user_id: str
    document_id: str
    categoria: Optional[str] = None
    subcategoria: Optional[str] = None
    valor: Optional[float] = None
    competencia: Optional[str] = None
    origem: Optional[str] = None
    metadata_json: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentResponse):
    ocr_result: Optional[OcrResultResponse] = None
    tax_events: List[TaxEventResponse] = []


class DashboardSummary(BaseModel):
    total_documents: int = 0
    documents_by_status: dict = {}
    total_tax_events: int = 0
    restituicao_estimada: float = 0.0
    imposto_devido: float = 0.0
    alertas: int = 0
    inconsistencies: List[dict] = []
    recent_documents: List[DocumentResponse] = []
