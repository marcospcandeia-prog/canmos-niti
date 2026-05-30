"""
Motor de cálculo tributário IRPF.
DETERMINÍSTICO — rastreável — auditável.
A IA nunca interfere aqui.
"""
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from typing import Optional
from .tables import (
    TABELA_IRPF_2024,
    DEDUCAO_DEPENDENTE_ANUAL,
    DEDUCAO_EDUCACAO_LIMITE,
    DESCONTO_SIMPLIFICADO,
    DESCONTO_SIMPLIFICADO_LIMITE,
)


@dataclass
class TaxInput:
    rendimentos_tributaveis: Decimal = Decimal("0")
    rendimentos_isentos: Decimal = Decimal("0")
    retencoes_fonte: Decimal = Decimal("0")
    deducoes_medicas: Decimal = Decimal("0")
    deducoes_educacao: Decimal = Decimal("0")
    num_dependentes: int = 0
    contribuicao_inss: Decimal = Decimal("0")
    pensao_alimenticia: Decimal = Decimal("0")


@dataclass
class TaxResult:
    # Modelo completo
    base_calculo_completo: Decimal
    ir_devido_completo: Decimal
    deducoes_total: Decimal

    # Modelo simplificado
    base_calculo_simplificado: Decimal
    ir_devido_simplificado: Decimal
    desconto_simplificado: Decimal

    # Resultado final (melhor modelo)
    modelo_recomendado: str
    ir_devido_final: Decimal
    retencoes_fonte: Decimal
    restituicao: Decimal  # positivo = restituição | negativo = a pagar

    # Obrigatoriedade
    obrigatorio_declarar: bool
    motivos_obrigatoriedade: list[str] = field(default_factory=list)

    # Alertas
    alertas: list[str] = field(default_factory=list)


def calcular_irpf(inp: TaxInput) -> TaxResult:
    """Cálculo completo IRPF 2024."""

    # ── Modelo Completo ──────────────────────────────────────
    deducao_dependentes = DEDUCAO_DEPENDENTE_ANUAL * inp.num_dependentes
    deducao_educacao = min(inp.deducoes_educacao, DEDUCAO_EDUCACAO_LIMITE)

    deducoes_total = (
        inp.deducoes_medicas +
        deducao_educacao +
        deducao_dependentes +
        inp.contribuicao_inss +
        inp.pensao_alimenticia
    )

    base_completo = max(inp.rendimentos_tributaveis - deducoes_total, Decimal("0"))
    ir_completo = _aplicar_tabela(base_completo)

    # ── Modelo Simplificado ──────────────────────────────────
    desconto_simp = min(
        inp.rendimentos_tributaveis * DESCONTO_SIMPLIFICADO,
        DESCONTO_SIMPLIFICADO_LIMITE,
    )
    base_simplificado = max(inp.rendimentos_tributaveis - desconto_simp, Decimal("0"))
    ir_simplificado = _aplicar_tabela(base_simplificado)

    # ── Melhor modelo ────────────────────────────────────────
    if ir_completo <= ir_simplificado:
        modelo = "completo"
        ir_final = ir_completo
    else:
        modelo = "simplificado"
        ir_final = ir_simplificado

    restituicao = inp.retencoes_fonte - ir_final

    # ── Obrigatoriedade ──────────────────────────────────────
    motivos, obrigatorio = _verificar_obrigatoriedade(inp)

    # ── Alertas ──────────────────────────────────────────────
    alertas = _gerar_alertas(inp, ir_final, restituicao)

    return TaxResult(
        base_calculo_completo=_arred(base_completo),
        ir_devido_completo=_arred(ir_completo),
        deducoes_total=_arred(deducoes_total),
        base_calculo_simplificado=_arred(base_simplificado),
        ir_devido_simplificado=_arred(ir_simplificado),
        desconto_simplificado=_arred(desconto_simp),
        modelo_recomendado=modelo,
        ir_devido_final=_arred(ir_final),
        retencoes_fonte=_arred(inp.retencoes_fonte),
        restituicao=_arred(restituicao),
        obrigatorio_declarar=obrigatorio,
        motivos_obrigatoriedade=motivos,
        alertas=alertas,
    )


def _aplicar_tabela(base: Decimal) -> Decimal:
    """Aplica alíquota progressiva da tabela IRPF 2024."""
    for faixa in TABELA_IRPF_2024:
        if faixa.limite_superior is None or base <= faixa.limite_superior:
            ir = base * faixa.aliquota - faixa.deducao
            return max(ir, Decimal("0"))
    return Decimal("0")


def _verificar_obrigatoriedade(inp: TaxInput) -> tuple[list[str], bool]:
    motivos = []
    if inp.rendimentos_tributaveis > Decimal("30639.90"):
        motivos.append(f"Rendimentos tributáveis acima de R$ 30.639,90")
    if inp.rendimentos_isentos > Decimal("200000.00"):
        motivos.append("Rendimentos isentos acima de R$ 200.000,00")
    return motivos, len(motivos) > 0


def _gerar_alertas(inp: TaxInput, ir_final: Decimal, restituicao: Decimal) -> list[str]:
    alertas = []
    if inp.deducoes_medicas == 0:
        alertas.append("Nenhuma despesa médica informada — verifique se possui recibos")
    if inp.retencoes_fonte == 0 and inp.rendimentos_tributaveis > 0:
        alertas.append("Nenhuma retenção na fonte detectada — confirme seus informes")
    if restituicao < Decimal("-5000"):
        alertas.append("Imposto a pagar elevado — considere parcelar em até 8 quotas")
    return alertas


def _arred(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
