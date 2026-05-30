from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.shared.models import *  # noqa: F401 — registra todos os modelos

# Routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.documents.router import router as documents_router
from app.modules.tax_engine.router import router as tax_router
from app.modules.ai.router import router as ai_router
from app.modules.payments.router import router as payments_router
from app.modules.admin.router import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 {settings.APP_NAME} iniciando em modo {settings.APP_ENV}...")
    yield
    print(f"🛑 {settings.APP_NAME} encerrando...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Núcleo de Infraestrutura Tributária Inteligente",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth_router,     prefix=PREFIX)
app.include_router(users_router,    prefix=PREFIX)
app.include_router(dashboard_router,prefix=PREFIX)
app.include_router(documents_router,prefix=PREFIX)
app.include_router(tax_router,      prefix=PREFIX)
app.include_router(ai_router,       prefix=PREFIX)
app.include_router(payments_router, prefix=PREFIX)
app.include_router(admin_router,    prefix=PREFIX)

# ── Health ────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0", "env": settings.APP_ENV}

@app.get("/", tags=["Root"])
def root():
    return {"message": f"Bem-vindo ao {settings.APP_NAME}", "docs": "/docs"}
