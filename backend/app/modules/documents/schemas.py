"""
Documents Pydantic Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    
    id: int
    user_id: int
    tipo: Optional[str]
    nome_original: str
    storage_path: str
    mime_type: str
    hash_arquivo: str
    status: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 1,
                "tipo": "informe_rendimentos",
                "nome_original": "informe_2025.pdf",
                "storage_path": "users/1/documents/informe_2025.pdf",
                "mime_type": "application/pdf",
                "hash_arquivo": "abc123...",
                "status": "uploaded",
                "created_at": "2026-06-03T22:00:00"
            }
        }
    }


class DocumentResponse(BaseModel):
    """Schema for document details response"""
    
    id: int
    user_id: int
    tipo: Optional[str]
    nome_original: str
    storage_path: str
    mime_type: str
    hash_arquivo: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    # OCR Result (if exists)
    ocr_texto: Optional[str] = None
    ocr_confianca: Optional[float] = None
    ocr_engine: Optional[str] = None
    ocr_status: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 1,
                "tipo": "informe_rendimentos",
                "nome_original": "informe_2025.pdf",
                "storage_path": "users/1/documents/informe_2025.pdf",
                "mime_type": "application/pdf",
                "hash_arquivo": "abc123...",
                "status": "processed",
                "created_at": "2026-06-03T22:00:00",
                "updated_at": "2026-06-03T22:05:00",
                "ocr_texto": "INFORME DE RENDIMENTOS...",
                "ocr_confianca": 0.95,
                "ocr_engine": "paddleocr",
                "ocr_status": "success"
            }
        }
    }


class DocumentListResponse(BaseModel):
    """Schema for document list item"""
    
    id: int
    tipo: Optional[str]
    nome_original: str
    mime_type: str
    status: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "tipo": "informe_rendimentos",
                "nome_original": "informe_2025.pdf",
                "mime_type": "application/pdf",
                "status": "processed",
                "created_at": "2026-06-03T22:00:00"
            }
        }
    }


class DocumentStats(BaseModel):
    """Schema for document statistics"""
    
    total: int = Field(..., description="Total de documentos")
    uploaded: int = Field(..., description="Status: uploaded")
    processing: int = Field(..., description="Status: processing")
    processed: int = Field(..., description="Status: processed")
    error: int = Field(..., description="Status: error")
    
    # By type
    by_type: dict[str, int] = Field(..., description="Contagem por tipo")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 15,
                "uploaded": 2,
                "processing": 1,
                "processed": 11,
                "error": 1,
                "by_type": {
                    "informe_rendimentos": 5,
                    "recibo_medico": 8,
                    "comprovante_educacao": 2
                }
            }
        }
    }


class DocumentDownloadResponse(BaseModel):
    """Schema for document download URL response"""
    
    download_url: str = Field(..., description="URL temporária para download")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "download_url": "http://minio:9000/canmos-documents/users/1/documents/file.pdf?...",
                "expires_in": 3600
            }
        }
    }
