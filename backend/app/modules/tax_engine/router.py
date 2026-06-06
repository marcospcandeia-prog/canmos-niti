"""
Tax Engine Router
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.core.middleware.auth import get_current_user
from app.modules.tax_engine.calculator import TaxCalculator
from app.shared.models.tax import Declaration
from app.shared.models.user import User

router = APIRouter()


@router.post(
    "/calculate/{ano_base}",
    summary="Calcular IRPF",
    description="Calcula IRPF para o ano base"
)
async def calculate_irpf(
    ano_base: int = Path(..., ge=2020, description="Ano base (mínimo 2020)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate IRPF for user and year"""
    result = await TaxCalculator.calculate_irpf(current_user, ano_base, db)
    return result


@router.get(
    "/declarations",
    summary="Listar Declarações",
    description="Lista todas as declarações do usuário"
)
async def list_declarations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all declarations for current user"""
    stmt = select(Declaration).where(
        Declaration.user_id == current_user.id
    ).order_by(Declaration.ano_base.desc())
    result = await db.execute(stmt)
    declarations = result.scalars().all()
    return [
        {
            "id": d.id,
            "ano_base": d.ano_base,
            "status": d.status,
            "restituicao_estimada": float(d.restituicao_estimada or 0),
            "imposto_devido": float(d.imposto_devido or 0),
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in declarations
    ]


@router.get(
    "/declaration/{ano_base}",
    summary="Obter Declaração",
    description="Obtém declaração pelo ano base"
)
async def get_declaration(
    ano_base: int = Path(..., ge=2020, description="Ano base (mínimo 2020)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get declaration for a specific year"""
    stmt = select(Declaration).where(
        Declaration.user_id == current_user.id,
        Declaration.ano_base == ano_base
    )
    result = await db.execute(stmt)
    declaration = result.scalar_one_or_none()
    if not declaration:
        raise HTTPException(status_code=404, detail="Declaração não encontrada")
    return {
        "id": declaration.id,
        "ano_base": declaration.ano_base,
        "status": declaration.status,
        "restituicao_estimada": float(declaration.restituicao_estimada or 0),
        "imposto_devido": float(declaration.imposto_devido or 0),
        "created_at": declaration.created_at.isoformat() if declaration.created_at else None,
        "updated_at": declaration.updated_at.isoformat() if declaration.updated_at else None,
    }


@router.post(
    "/declaration/{ano_base}",
    summary="Criar/Atualizar Declaração",
    description="Cria ou atualiza declaração IRPF"
)
async def create_declaration(
    ano_base: int = Path(..., ge=2020, description="Ano base (mínimo 2020)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update declaration"""
    declaration = await TaxCalculator.create_or_update_declaration(
        current_user, ano_base, db
    )
    return {
        "id": declaration.id,
        "ano_base": declaration.ano_base,
        "status": declaration.status,
        "restituicao_estimada": float(declaration.restituicao_estimada or 0),
        "imposto_devido": float(declaration.imposto_devido or 0),
        "created_at": declaration.created_at.isoformat() if declaration.created_at else None,
        "updated_at": declaration.updated_at.isoformat() if declaration.updated_at else None,
    }
