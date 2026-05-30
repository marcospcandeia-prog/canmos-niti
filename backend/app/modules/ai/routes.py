from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.ai.service import AiService
from app.modules.tax_engine.service import TaxEngine
from app.shared.models.user import User
from app.shared.schemas.tax import AiInteractionResponse, AiQueryRequest

router = APIRouter(prefix="/ai", tags=["ai"])

_ANO_BASE_PADRAO = str(datetime.now().year)


@router.post("/ask")
async def ask(
    data: AiQueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = TaxEngine(db)
    declaration = engine.get_declaration(user.id, _ANO_BASE_PADRAO)

    contexto = {}
    if declaration:
        contexto["restituicao_estimada"] = declaration.restituicao_estimada
        contexto["imposto_devido"] = declaration.imposto_devido
        contexto["total_rendimentos"] = declaration.total_rendimentos
        contexto["total_retencao"] = declaration.total_retencao
        contexto["status"] = declaration.status

        validations = engine.get_validations(declaration.id)
        contexto["inconsistencias"] = [
            {"mensagem": v.mensagem, "severidade": v.severidade}
            for v in validations
        ]

    if data.contexto:
        contexto.update(data.contexto)

    service = AiService(db)
    resposta = await service.ask(user.id, data.pergunta, contexto)

    return {"pergunta": data.pergunta, "resposta": resposta}


@router.get("/history", response_model=List[AiInteractionResponse])
def history(
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AiService(db)
    interactions = service.get_history(user.id, limit)
    return [AiInteractionResponse.model_validate(i) for i in interactions]
