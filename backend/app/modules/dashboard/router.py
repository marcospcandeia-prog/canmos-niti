from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, sum as sql_sum
from app.core.database import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models import User, Document, TaxEvent, DocumentStatus, TaxCategory

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Contagem de documentos
    total_docs = db.query(func.count(Document.id)).filter(
        Document.user_id == current_user.id
    ).scalar() or 0

    docs_processados = db.query(func.count(Document.id)).filter(
        Document.user_id == current_user.id,
        Document.status == DocumentStatus.TAX_EVENTS_CREATED,
    ).scalar() or 0

    # TAX_EVENTS — rendimentos tributáveis
    rendimentos = db.query(func.sum(TaxEvent.valor)).filter(
        TaxEvent.user_id == current_user.id,
        TaxEvent.categoria == TaxCategory.RENDIMENTO_TRIBUTAVEL,
    ).scalar() or 0

    # Retenções na fonte
    retencoes = db.query(func.sum(TaxEvent.valor)).filter(
        TaxEvent.user_id == current_user.id,
        TaxEvent.categoria == TaxCategory.RETENCAO_FONTE,
    ).scalar() or 0

    # Deduções
    deducoes_medicas = db.query(func.sum(TaxEvent.valor)).filter(
        TaxEvent.user_id == current_user.id,
        TaxEvent.categoria == TaxCategory.DEDUCAO_MEDICA,
    ).scalar() or 0

    # Restituição estimada (simplificado)
    restituicao_estimada = float(retencoes) - _calcular_ir_devido(float(rendimentos), float(deducoes_medicas))

    return {
        "usuario": {
            "nome": current_user.nome,
            "plano": current_user.subscription_plan,
        },
        "documentos": {
            "total": total_docs,
            "processados": docs_processados,
            "pendentes": total_docs - docs_processados,
        },
        "resumo_fiscal": {
            "rendimentos_tributaveis": float(rendimentos),
            "retencoes_fonte": float(retencoes),
            "deducoes_medicas": float(deducoes_medicas),
            "restituicao_estimada": round(restituicao_estimada, 2),
            "status": _status_restituicao(restituicao_estimada),
        },
        "alertas": _gerar_alertas(total_docs, docs_processados),
    }


def _calcular_ir_devido(rendimentos: float, deducoes: float) -> float:
    """Motor tributário determinístico — tabela IRPF 2024."""
    base_calculo = max(rendimentos - deducoes, 0)
    # Tabela IRPF 2024 (mensal * 12 = anual)
    if base_calculo <= 26963.20:
        return 0
    elif base_calculo <= 33919.80:
        return base_calculo * 0.075 - 2023.74
    elif base_calculo <= 45012.60:
        return base_calculo * 0.15 - 4764.06
    elif base_calculo <= 55976.16:
        return base_calculo * 0.225 - 8148.39
    else:
        return base_calculo * 0.275 - 10956.47


def _status_restituicao(valor: float) -> str:
    if valor > 0:
        return "restituicao"
    elif valor < 0:
        return "imposto_a_pagar"
    return "zero"


def _gerar_alertas(total: int, processados: int) -> list:
    alertas = []
    if total == 0:
        alertas.append({
            "tipo": "info",
            "mensagem": "Envie seus documentos para iniciar a análise tributária"
        })
    elif total > processados:
        alertas.append({
            "tipo": "warning",
            "mensagem": f"{total - processados} documento(s) aguardando processamento"
        })
    return alertas
