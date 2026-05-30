"""
Testes do Tax Engine IRPF 2024.
O motor fiscal é determinístico — resultados devem ser 100% previsíveis.
"""
import pytest
from decimal import Decimal
from app.modules.tax_engine.calculator import calcular_irpf, TaxInput


def test_isento_sem_rendimentos():
    """Sem rendimentos = sem imposto = sem obrigatoriedade."""
    result = calcular_irpf(TaxInput())
    assert result.ir_devido_final == Decimal("0.00")
    assert result.obrigatorio_declarar is False


def test_isento_abaixo_limite():
    """Rendimento abaixo do limite de isenção 2024."""
    inp = TaxInput(rendimentos_tributaveis=Decimal("20000.00"))
    result = calcular_irpf(inp)
    assert result.ir_devido_final == Decimal("0.00")


def test_obrigatorio_acima_limite():
    """Rendimento acima de R$ 30.639,90 é obrigatório."""
    inp = TaxInput(rendimentos_tributaveis=Decimal("35000.00"))
    result = calcular_irpf(inp)
    assert result.obrigatorio_declarar is True
    assert result.ir_devido_final > Decimal("0.00")


def test_restituicao_positiva():
    """Retenção maior que IR devido → restituição."""
    inp = TaxInput(
        rendimentos_tributaveis=Decimal("60000.00"),
        retencoes_fonte=Decimal("10000.00"),
    )
    result = calcular_irpf(inp)
    restituicao = result.restituicao
    ir = result.ir_devido_final
    assert restituicao == inp.retencoes_fonte - ir


def test_imposto_a_pagar():
    """IR devido maior que retenção → imposto a pagar."""
    inp = TaxInput(
        rendimentos_tributaveis=Decimal("100000.00"),
        retencoes_fonte=Decimal("5000.00"),
    )
    result = calcular_irpf(inp)
    assert result.restituicao < Decimal("0.00")


def test_deducao_medica_reduz_base():
    """Dedução médica reduz base de cálculo no modelo completo."""
    base = TaxInput(rendimentos_tributaveis=Decimal("80000.00"))
    com_medico = TaxInput(
        rendimentos_tributaveis=Decimal("80000.00"),
        deducoes_medicas=Decimal("15000.00"),
    )
    r_base = calcular_irpf(base)
    r_med = calcular_irpf(com_medico)
    assert r_med.ir_devido_completo < r_base.ir_devido_completo


def test_dependente_reduz_base():
    """Cada dependente deduz R$ 2.275,08 da base."""
    sem = calcular_irpf(TaxInput(rendimentos_tributaveis=Decimal("60000.00")))
    com = calcular_irpf(TaxInput(rendimentos_tributaveis=Decimal("60000.00"), num_dependentes=2))
    diff = sem.base_calculo_completo - com.base_calculo_completo
    assert diff == Decimal("4550.16")  # 2 × 2.275,08


def test_modelo_recomendado_escolhe_menor():
    """Sistema deve recomendar o modelo que resulta em menor imposto."""
    inp = TaxInput(
        rendimentos_tributaveis=Decimal("50000.00"),
        deducoes_medicas=Decimal("500.00"),  # poucas deduções → simplificado melhor
    )
    result = calcular_irpf(inp)
    ir_recomendado = result.ir_devido_final
    assert ir_recomendado == min(result.ir_devido_completo, result.ir_devido_simplificado)


def test_educacao_tem_limite():
    """Dedução de educação é limitada a R$ 3.561,50."""
    inp = TaxInput(
        rendimentos_tributaveis=Decimal("80000.00"),
        deducoes_educacao=Decimal("20000.00"),  # acima do limite
    )
    result = calcular_irpf(inp)
    # Deduções totais não podem incluir mais de 3561.50 de educação
    assert result.deducoes_total <= Decimal("3561.50") + Decimal("1")  # margem


def test_alerta_sem_retencao():
    """Alerta gerado quando há rendimento sem retenção."""
    inp = TaxInput(rendimentos_tributaveis=Decimal("50000.00"), retencoes_fonte=Decimal("0"))
    result = calcular_irpf(inp)
    assert any("retenção" in a.lower() for a in result.alertas)


def test_alerta_imposto_elevado():
    """Alerta de parcelamento para imposto > R$ 5.000."""
    inp = TaxInput(
        rendimentos_tributaveis=Decimal("200000.00"),
        retencoes_fonte=Decimal("0"),
    )
    result = calcular_irpf(inp)
    assert any("parcelar" in a.lower() for a in result.alertas)
