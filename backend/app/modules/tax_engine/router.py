from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from app.core.database import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models import User, TaxEvent, TaxCategory
from .calculator import calcular_irpf, TaxInput

router = APIRouter(prefix="/tax", tags=["Tax Engine"])


@router.get("/simulation")
def simulate_irpf(
    ano_base: str = "2024",
    num_dependentes: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Simulação IRPF baseada nos TAX_EVENTS do usuário."""

    def _sum(categoria: TaxCategory) -> Decimal:
        result = db.query(func.sum(TaxEvent.valor)).filter(
            TaxEvent.user_id == current_user.id,
            TaxEvent.categoria == categoria,
        ).scalar()
        return Decimal(str(result or 0))

    inp = TaxInput(
        rendimentos_tributaveis=_sum(TaxCategory.RENDIMENTO_TRIBUTAVEL),
        rendimentos_isentos=_sum(TaxCategory.RENDIMENTO_ISENTO),
        retencoes_fonte=_sum(TaxCategory.RETENCAO_FONTE),
        deducoes_medicas=_sum(TaxCategory.DEDUCAO_MEDICA),
        deducoes_educacao=_sum(TaxCategory.DEDUCAO_EDUCACAO),
        num_dependentes=num_dependentes,
    )

    result = calcular_irpf(inp)

    return {
        "ano_base": ano_base,
        "entradas": {
            "rendimentos_tributaveis": float(inp.rendimentos_tributaveis),
            "rendimentos_isentos": float(inp.rendimentos_isentos),
            "retencoes_fonte": float(inp.retencoes_fonte),
            "deducoes_medicas": float(inp.deducoes_medicas),
            "deducoes_educacao": float(inp.deducoes_educacao),
            "num_dependentes": num_dependentes,
        },
        "modelo_completo": {
            "base_calculo": float(result.base_calculo_completo),
            "deducoes_total": float(result.deducoes_total),
            "ir_devido": float(result.ir_devido_completo),
        },
        "modelo_simplificado": {
            "base_calculo": float(result.base_calculo_simplificado),
            "desconto": float(result.desconto_simplificado),
            "ir_devido": float(result.ir_devido_simplificado),
        },
        "resultado": {
            "modelo_recomendado": result.modelo_recomendado,
            "ir_devido": float(result.ir_devido_final),
            "retencoes_fonte": float(result.retencoes_fonte),
            "restituicao": float(result.restituicao),
            "status": "restituicao" if result.restituicao >= 0 else "imposto_a_pagar",
        },
        "obrigatoriedade": {
            "obrigatorio": result.obrigatorio_declarar,
            "motivos": result.motivos_obrigatoriedade,
        },
        "alertas": result.alertas,
    }


@router.get("/events")
def list_tax_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos os TAX_EVENTS do usuário."""
    events = db.query(TaxEvent).filter(
        TaxEvent.user_id == current_user.id
    ).order_by(TaxEvent.created_at.desc()).all()

    return [
        {
            "id": str(e.id),
            "categoria": e.categoria,
            "subcategoria": e.subcategoria,
            "valor": float(e.valor),
            "origem": e.origem,
            "fonte_pagadora": e.fonte_pagadora,
            "ano_base": e.ano_base,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
