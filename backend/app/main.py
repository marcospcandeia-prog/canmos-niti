"""
CANMOS-NITI - Núcleo de Infraestrutura Tributária Inteligente
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config.settings import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Núcleo de Infraestrutura Tributária Inteligente",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
        "environment": settings.APP_ENV,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "app": settings.APP_NAME,
            "version": "0.1.0",
        }
    )


# Include routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.documents.router import router as documents_router
from app.modules.tax_engine.router import router as tax_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.ocr.router import router as ocr_router
from app.modules.ai.router import router as ai_router

app.include_router(auth_router, prefix="/auth", tags=["Autenticação"])
app.include_router(users_router, prefix="/users", tags=["Usuários"])
app.include_router(documents_router, prefix="/documents", tags=["Documentos"])
app.include_router(tax_router, prefix="/tax", tags=["Tax Engine"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(ocr_router, prefix="", tags=["OCR"])
app.include_router(ai_router, prefix="", tags=["IA"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
