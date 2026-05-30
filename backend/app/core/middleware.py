import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings

_RATE_LIMIT_STORE: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(ip: str, max_requests: int = 200, window_seconds: int = 60) -> bool:
    now = time.time()
    window_start = now - window_seconds
    _RATE_LIMIT_STORE[ip] = [t for t in _RATE_LIMIT_STORE[ip] if t > window_start]
    if len(_RATE_LIMIT_STORE[ip]) >= max_requests:
        return False
    _RATE_LIMIT_STORE[ip].append(now)
    return True


def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.ENVIRONMENT == "production":
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)

    if settings.SECRET_KEY == "canmos-niti-super-secret-key-change-in-production-2024":
        logger.warning("SECRET_KEY padrão em uso. Altere para um valor seguro em produção.")

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        if not _check_rate_limit(client_ip, settings.RATE_LIMIT_MAX, settings.RATE_LIMIT_WINDOW):
            return JSONResponse(
                status_code=429,
                content={"detail": "Muitas requisições. Tente novamente em instantes."},
            )
        return await call_next(request)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"},
        )
