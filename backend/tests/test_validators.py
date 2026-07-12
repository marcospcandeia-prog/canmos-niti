from decimal import Decimal

from app.modules.tax_engine.validators.irpf_validator import IRPFValidator, Validacao


class TestIRPFValidator:
    def test_sem_rendimento(self):
        eventos = []
        validacoes = IRPFValidator.validar_eventos(eventos, 2025)
        tipos = [v.tipo for v in validacoes]
        assert "sem_rendimento" in tipos

    def test_abaixo_limite_isencao(self):
        eventos = [
            {"categoria": "rendimento_trabalho", "valor": Decimal("2000.00"), "competencia": "2025-01"},
        ]
        validacoes = IRPFValidator.validar_eventos(eventos, 2025)
        tipos = [v.tipo for v in validacoes]
        assert "abaixo_limite_isencao" in tipos

    def test_acima_limite_isencao(self):
        eventos = [
            {"categoria": "rendimento_trabalho", "valor": Decimal("5000.00"), "competencia": "2025-01"},
        ]
        validacoes = IRPFValidator.validar_eventos(eventos, 2025)
        tipos = [v.tipo for v in validacoes]
        assert "abaixo_limite_isencao" not in tipos

    def test_despesa_medica_alta(self):
        eventos = [
            {"categoria": "rendimento_trabalho", "valor": Decimal("10000.00"), "competencia": "2025-01"},
            {"categoria": "despesa_medica", "valor": Decimal("5000.00"), "competencia": "2025-03"},
        ]
        validacoes = IRPFValidator.validar_eventos(eventos, 2025)
        tipos = [v.tipo for v in validacoes]
        assert "despesa_medica_alta" in tipos

    def test_despesa_medica_normal(self):
        eventos = [
            {"categoria": "rendimento_trabalho", "valor": Decimal("100000.00"), "competencia": "2025-01"},
            {"categoria": "despesa_medica", "valor": Decimal("5000.00"), "competencia": "2025-03"},
        ]
        validacoes = IRPFValidator.validar_eventos(eventos, 2025)
        tipos = [v.tipo for v in validacoes]
        assert "despesa_medica_alta" not in tipos

    def test_deducao_educacao_excedida(self):
        eventos = [
            {"categoria": "despesa_educacao", "valor": Decimal("5000.00"), "competencia": "2025-02"},
        ]
        validacoes = IRPFValidator.validar_eventos(eventos, 2025)
        tipos = [v.tipo for v in validacoes]
        assert "deducao_educacao_excedida" in tipos

    def test_deducao_educacao_normal(self):
        eventos = [
            {"categoria": "despesa_educacao", "valor": Decimal("2000.00"), "competencia": "2025-02"},
        ]
        validacoes = IRPFValidator.validar_eventos(eventos, 2025)
        tipos = [v.tipo for v in validacoes]
        assert "deducao_educacao_excedida" not in tipos

    def test_despesa_medica_muito_alta(self):
        eventos = [
            {"categoria": "despesa_medica", "valor": Decimal("15000.00"), "competencia": "2025-03"},
        ]
        validacoes = IRPFValidator.validar_eventos(eventos, 2025)
        tipos = [v.tipo for v in validacoes]
        assert "despesa_medica_muito_alta" in tipos

    def test_validacao_tem_campos_corretos(self):
        v = Validacao("teste_tipo", "warning", "mensagem de teste", "campo_x")
        d = v.to_dict()
        assert d["tipo"] == "teste_tipo"
        assert d["severidade"] == "warning"
        assert d["mensagem"] == "mensagem de teste"
        assert d["campo"] == "campo_x"
