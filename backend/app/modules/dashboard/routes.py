from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.shared.models.document import Document, DocumentStatus, TaxEvent
from app.shared.models.tax import Declaration, Validation, ValidationSeverity
from app.shared.models.user import User
from app.shared.schemas.document import DashboardSummary, DocumentResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = db.query(Document).filter(Document.user_id == user.id).all()
    total_docs = len(docs)

    docs_by_status = {}
    for status in DocumentStatus:
        count = sum(1 for d in docs if d.status == status)
        if count > 0:
            docs_by_status[status.value] = count

    recent_docs = sorted(docs, key=lambda d: d.created_at, reverse=True)[:5]

    declaration = (
        db.query(Declaration)
        .filter(
            Declaration.user_id == user.id,
            Declaration.ano_base == str(datetime.now().year - 1),
        )
        .first()
    )

    total_events = db.query(TaxEvent).filter(TaxEvent.user_id == user.id).count()

    inconsistencies = []
    alertas = 0
    restituicao = 0.0
    imposto_devido = 0.0

    if declaration:
        restituicao = declaration.restituicao_estimada
        imposto_devido = declaration.imposto_devido
        validations = (
            db.query(Validation)
            .filter(Validation.declaration_id == declaration.id)
            .all()
        )
        for v in validations:
            inconsistencies.append({
                "tipo": v.tipo,
                "severidade": v.severidade,
                "mensagem": v.mensagem,
            })
            if v.severidade in (ValidationSeverity.WARNING, ValidationSeverity.ERROR, ValidationSeverity.CRITICAL):
                alertas += 1

    return DashboardSummary(
        total_documents=total_docs,
        documents_by_status=docs_by_status,
        total_tax_events=total_events,
        restituicao_estimada=restituicao,
        imposto_devido=imposto_devido,
        alertas=alertas,
        inconsistencies=inconsistencies,
        recent_documents=[DocumentResponse.model_validate(d) for d in recent_docs],
    )
