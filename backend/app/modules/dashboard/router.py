"""
Dashboard Router
Summary and metrics for user
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models.tax import Declaration
from app.shared.models.document import Document
from app.shared.models.tax import TaxEvent
from app.shared.models.user import User

router = APIRouter()


@router.get(
    "/summary",
    summary="Dashboard Summary",
    description="Resumo geral do dashboard do usuário"
)
async def get_dashboard_summary(
    ano_base: int = Query(2025, description="Ano base para filtros"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard summary for user
    
    Returns:
    - Restituição estimada
    - Total documentos
    - Total tax events
    - Declarações
    """
    # Get declaration for year
    stmt = select(Declaration).where(
        Declaration.user_id == current_user.id,
        Declaration.ano_base == ano_base
    )
    result = await db.execute(stmt)
    declaration = result.scalar_one_or_none()
    
    # Count documents
    stmt = select(func.count(Document.id)).where(Document.user_id == current_user.id)
    result = await db.execute(stmt)
    total_documents = result.scalar() or 0
    
    # Count processed documents
    stmt = select(func.count(Document.id)).where(
        Document.user_id == current_user.id,
        Document.status == "processed"
    )
    result = await db.execute(stmt)
    documents_processed = result.scalar() or 0
    
    # Count tax events for year
    stmt = select(func.count(TaxEvent.id)).where(
        TaxEvent.user_id == current_user.id,
        TaxEvent.competencia.like(f"{ano_base}-%")
    )
    result = await db.execute(stmt)
    tax_events_count = result.scalar() or 0
    
    # Sum rendimentos
    stmt = select(func.sum(TaxEvent.valor)).where(
        TaxEvent.user_id == current_user.id,
        TaxEvent.competencia.like(f"{ano_base}-%"),
        TaxEvent.categoria == "rendimento_trabalho"
    )
    result = await db.execute(stmt)
    total_rendimentos = result.scalar() or 0
    
    # Build summary
    summary = {
        "ano_base": ano_base,
        "restituicao_estimada": float(declaration.restituicao_estimada) if declaration else 0.0,
        "imposto_devido": float(declaration.imposto_devido) if declaration else 0.0,
        "total_rendimentos": float(total_rendimentos),
        "documentos_enviados": total_documents,
        "documentos_processados": documents_processed,
        "total_tax_events": tax_events_count,
        "status_declaracao": declaration.status if declaration else None,
        "alertas": []
    }
    
    # Add alerts
    if documents_processed < total_documents:
        summary["alertas"].append({
            "severidade": "info",
            "mensagem": f"{total_documents - documents_processed} documento(s) aguardando processamento"
        })
    
    if tax_events_count == 0:
        summary["alertas"].append({
            "severidade": "warning",
            "mensagem": "Nenhum evento tributário encontrado. Envie seus documentos!"
        })
    
    return summary
