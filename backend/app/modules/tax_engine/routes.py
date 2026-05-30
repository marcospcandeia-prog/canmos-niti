from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.audit.service import AuditService
from app.modules.tax_engine.service import TaxEngine
from app.shared.models.user import User
from app.shared.schemas.tax import DeclarationResponse, ValidationResponse

router = APIRouter(prefix="/tax", tags=["tax"])

_ANO_BASE_PADRAO = str(datetime.now().year)


@router.post("/calculate", response_model=DeclarationResponse)
def calculate(
    ano_base: str = Query(default=_ANO_BASE_PADRAO),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = TaxEngine(db)
    declaration = engine.calculate(user.id, ano_base)
    AuditService.log(db, user.id, "calculate_tax", "declaration", declaration.id, {"ano_base": ano_base})
    return DeclarationResponse.model_validate(declaration)


@router.get("/declaration", response_model=DeclarationResponse)
def get_declaration(
    ano_base: str = Query(default=_ANO_BASE_PADRAO),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = TaxEngine(db)
    declaration = engine.get_declaration(user.id, ano_base)
    if not declaration:
        return DeclarationResponse(
            id="",
            user_id=user.id,
            ano_base=ano_base,
            status="draft",
            restituicao_estimada=0.0,
            imposto_devido=0.0,
            total_rendimentos=0.0,
            total_retencao=0.0,
            qtd_dependentes=0.0,
            total_deducao_dependentes=0.0,
            created_at=datetime.now(),
        )
    return DeclarationResponse.model_validate(declaration)


@router.get("/validations", response_model=List[ValidationResponse])
def get_validations(
    ano_base: str = Query(default=_ANO_BASE_PADRAO),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = TaxEngine(db)
    declaration = engine.get_declaration(user.id, ano_base)
    if not declaration:
        return []
    validations = engine.get_validations(declaration.id)
    return [ValidationResponse.model_validate(v) for v in validations]
