from typing import List

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CANMOS-NITI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Núcleo de Infraestrutura Tributária Inteligente"

    DATABASE_URL: str = "postgresql://canmos:canmos123@localhost:5432/canmos_niti"
    SECRET_KEY: str = "canmos-niti-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "canmos"
    MINIO_SECRET_KEY: str = "canmos123"
    MINIO_BUCKET: str = "canmos-documents"
    MINIO_SECURE: bool = False
    STORAGE_LOCAL_PATH: str = "./local_storage"

    OLLAMA_HOST: str = "localhost"
    OLLAMA_PORT: int = 11434

    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024

    CORS_ORIGINS: str = "http://localhost:3000"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    RATE_LIMIT_MAX: int = 200
    RATE_LIMIT_WINDOW: int = 60

    OCR_ENGINE: str = "auto"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    @property
    def ollama_base_url(self) -> str:
        return f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
