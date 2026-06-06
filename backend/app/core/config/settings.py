"""
Application Settings using Pydantic Settings
Loads configuration from environment variables
"""

import json
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = Field(default="CANMOS-NITI")
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # Security
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # Database - Supabase PostgreSQL
    DATABASE_URL: str = Field(...)
    SUPABASE_URL: str = Field(...)
    SUPABASE_ANON_KEY: str = Field(...)
    SUPABASE_SERVICE_ROLE: str = Field(...)
    
    # MinIO Storage
    MINIO_ENDPOINT: str = Field(default="minio:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_BUCKET: str = Field(default="canmos-documents")
    MINIO_SECURE: bool = Field(default=False)
    
    # Ollama AI
    OLLAMA_HOST: str = Field(default="http://ollama:11434")
    OLLAMA_MODEL: str = Field(default="phi3:mini")
    
    # Qdrant Vector DB
    QDRANT_HOST: str = Field(default="http://qdrant:6333")
    QDRANT_COLLECTION: str = Field(default="tax_knowledge")
    
    # OCR
    OCR_ENGINE_PRIMARY: str = Field(default="paddleocr")
    OCR_ENGINE_FALLBACK: str = Field(default="tesseract")
    OCR_CONFIDENCE_THRESHOLD: float = Field(default=0.7)
    
    # Tax Engine
    TAX_YEAR_DEFAULT: int = Field(default=2025)
    TAX_IRPF_TABLE_VERSION: str = Field(default="2025")
    
    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="JSON array or comma-separated CORS origins",
    )
    
    @property
    def cors_origins(self) -> List[str]:
        raw = self.CORS_ORIGINS
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return [x.strip() for x in raw.split(",") if x.strip()]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance
    Use this function to get settings throughout the application
    """
    return Settings()
