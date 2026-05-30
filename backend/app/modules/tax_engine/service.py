from typing import List

from sqlalchemy.orm import Session

from app.shared.models.document import TaxEvent
from app.shared.models.tax import (
    Declaration,
    DeclarationStatus,
    Validation,
    ValidationSeverity,
)
from app.shared.models.user import UserProfile


class TaxEngine:
    TRIBUTATION_TABLE = {
        "base": 22597.20,
        "first": (22597.21, 28281.65, 0.075, 1693.72),
        "second": (28281.66, 37543.18, 0.15, 3814.43),
        "third": (37543.19, 46613.33, 0.225, 6625.81),
        "fourth": (46613.34, float("inf"), 0.275, 8963.36),
    }

    DEDUCAO_POR_DEPENDENTE = 2275.08

    def __init__(self, db: Session):
        self.db = db

    def calculate(self, user_id: str, ano_base: str) -> Declaration:
        events = (
            self.db.query(TaxEvent)
            .filter(TaxEvent.user_id == user_id)
            .all()
        )

        total_rendimentos = self._sum_rendimentos(events)
        total_retencao = self._sum_retencao(events)
        qtd_dependentes = self._count_dependentes(events, user_id)
        total_deducao = round(qtd_dependentes * self.DEDUCAO_POR_DEPENDENTE, 2)
        renda_pos_deducao = max(0, total_rendimentos - total_deducao)
        imposto_devido = self._calculate_irpf(renda_pos_deducao)
        restituicao = max(0, total_retencao - imposto_devido)

        declaration = (
            self.db.query(Declaration)
            .filter(
                Declaration.user_id == user_id,
                Declaration.ano_base == ano_base,
            )
            .first()
        )

        if not declaration:
            declaration = Declaration(
                user_id=user_id,
                ano_base=ano_base,
                total_rendimentos=total_rendimentos,
                total_retencao=total_retencao,
                qtd_dependentes=qtd_dependentes,
                total_deducao_dependentes=total_deducao,
                imposto_devido=imposto_devido,
                restituicao_estimada=restituicao,
                status=DeclarationStatus.PENDING,
            )
            self.db.add(declaration)
        else:
            declaration.total_rendimentos = total_rendimentos
            declaration.total_retencao = total_retencao
            declaration.qtd_dependentes = qtd_dependentes
            declaration.total_deducao_dependentes = total_deducao
            declaration.imposto_devido = imposto_devido
            declaration.restituicao_estimada = restituicao

        self.db.commit()
        self.db.refresh(declaration)

        validations = self._validate(declaration, events)
        for v in validations:
            self.db.add(v)
        self.db.commit()

        return declaration

    def _sum_rendimentos(self, events: List[TaxEvent]) -> float:
        total = 0.0
        for event in events:
            if event.categoria in ("rendimento", "Rendimento"):
                try:
                    total += float(event.valor)
                except (ValueError, TypeError):
                    pass
        return total

    def _sum_retencao(self, events: List[TaxEvent]) -> float:
        total = 0.0
        for event in events:
            if event.categoria in ("retencao", "Retenção", "IRRF"):
                try:
                    total += float(event.valor)
                except (ValueError, TypeError):
                    pass
        return total

    def _count_dependentes(self, events: List[TaxEvent], user_id: str) -> int:
        qtd = 0
        for event in events:
            if event.categoria in ("dependente", "Dependente"):
                try:
                    qtd += int(float(event.valor))
                except (ValueError, TypeError):
                    qtd += 1

        if qtd == 0:
            profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if profile and profile.possui_dependentes == "sim":
                qtd = 1

        return qtd

    def _calculate_irpf(self, renda_total: float) -> float:
        if renda_total <= self.TRIBUTATION_TABLE["base"]:
            return 0.0

        for key in ("first", "second", "third", "fourth"):
            min_val, max_val, rate, deduction = self.TRIBUTATION_TABLE[key]
            if min_val <= renda_total <= max_val:
                return round(renda_total * rate - deduction, 2)

        return round(
            renda_total * self.TRIBUTATION_TABLE["fourth"][2]
            - self.TRIBUTATION_TABLE["fourth"][3],
            2,
        )

    def _validate(self, declaration: Declaration, events: List[TaxEvent]) -> List[Validation]:
        validations = []

        if declaration.total_rendimentos <= 0:
            validations.append(
                Validation(
                    declaration_id=declaration.id,
                    tipo="rendimento_zero",
                    severidade=ValidationSeverity.WARNING,
                    mensagem="Nenhum rendimento encontrado. Verifique os documentos enviados.",
                )
            )

        if declaration.total_rendimentos > self.TRIBUTATION_TABLE["base"] and declaration.total_retencao <= 0:
            validations.append(
                Validation(
                    declaration_id=declaration.id,
                    tipo="obrigatoriedade_irpf",
                    severidade=ValidationSeverity.WARNING,
                    mensagem="Rendimentos acima do limite de isenção. É obrigatório declarar IRPF.",
                )
            )

        if declaration.restituicao_estimada > 10000:
            validations.append(
                Validation(
                    declaration_id=declaration.id,
                    tipo="restituicao_alta",
                    severidade=ValidationSeverity.INFO,
                    mensagem=f"Restituição estimada de R$ {declaration.restituicao_estimada:.2f}. Valide as informações.",
                )
            )

        if declaration.qtd_dependentes > 0:
            validations.append(
                Validation(
                    declaration_id=declaration.id,
                    tipo="deducao_dependentes",
                    severidade=ValidationSeverity.INFO,
                    mensagem=f"Considerados {int(declaration.qtd_dependentes)} dependente(s) com dedução total de R$ {declaration.total_deducao_dependentes:.2f}.",
                    metadata_json={
                        "qtd_dependentes": declaration.qtd_dependentes,
                        "deducao_por_dependente": self.DEDUCAO_POR_DEPENDENTE,
                        "total_deducao": declaration.total_deducao_dependentes,
                    },
                )
            )

        if not events:
            validations.append(
                Validation(
                    declaration_id=declaration.id,
                    tipo="sem_eventos",
                    severidade=ValidationSeverity.ERROR,
                    mensagem="Nenhum evento tributário encontrado. Envie documentos para análise.",
                )
            )

        return validations

    def get_declaration(self, user_id: str, ano_base: str) -> Declaration:
        declaration = (
            self.db.query(Declaration)
            .filter(
                Declaration.user_id == user_id,
                Declaration.ano_base == ano_base,
            )
            .first()
        )
        return declaration

    def get_validations(self, declaration_id: str) -> List[Validation]:
        return (
            self.db.query(Validation)
            .filter(Validation.declaration_id == declaration_id)
            .all()
        )
