import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.tax_engine.pdf_generator import DeclarationPDF, gerar_pdf_declaracao


class TestDeclarationPDF:
    def test_pdf_creation_with_minimal_data(self):
        user = MagicMock()
        user.nome = "Test User"
        user.cpf = "12345678901"
        user.email = "test@test.com"

        calc_result = {
            "total_rendimentos": Decimal("0"),
            "total_deducoes": Decimal("0"),
            "base_calculo": Decimal("0"),
            "imposto_devido": Decimal("0"),
            "total_retencao": Decimal("0"),
            "restituicao_estimada": Decimal("0"),
            "imposto_pagar": Decimal("0"),
            "status": "rascunho",
            "validacoes": [],
        }

        pdf = DeclarationPDF(user, 2025, calc_result, [])
        pdf.build()
        output = pdf.output()

        assert output is not None
        assert len(output) > 0

    def test_pdf_creation_with_full_data(self):
        user = MagicMock()
        user.nome = "João Silva"
        user.cpf = "12345678901"
        user.email = "joao@test.com"

        calc_result = {
            "total_rendimentos": Decimal("60000.00"),
            "total_deducoes": Decimal("5400.00"),
            "base_calculo": Decimal("54600.00"),
            "imposto_devido": Decimal("8234.56"),
            "total_retencao": Decimal("4200.00"),
            "restituicao_estimada": Decimal("0"),
            "imposto_pagar": Decimal("4034.56"),
            "status": "finalizada",
            "validacoes": [
                {"tipo": "despesa_medica_alta", "severidade": "warning", "mensagem": "Test warning"},
            ],
        }

        event = MagicMock()
        event.categoria = "rendimento_trabalho"
        event.valor = Decimal("60000.00")
        event.competencia = "2025-12"
        event.origem = "ocr"

        pdf = DeclarationPDF(user, 2025, calc_result, [event])
        pdf.build()
        output = pdf.output()

        assert output is not None
        assert len(output) > 0

    def test_pdf_format_currency(self):
        assert DeclarationPDF._fmt(Decimal("1234.56")) == "R$ 1.234,56"
        assert DeclarationPDF._fmt(Decimal("0")) == "R$ 0,00"
        assert DeclarationPDF._fmt(Decimal("1000000.00")) == "R$ 1.000.000,00"

    @pytest.mark.asyncio
    async def test_gerar_pdf_declaracao_returns_none_when_no_declaration(self):
        user = MagicMock()
        user.id = 999
        db = AsyncMock()

        with patch("app.modules.tax_engine.pdf_generator.select"):
            result_mock = MagicMock()
            result_mock.scalar_one_or_none.return_value = None
            db.execute.return_value = result_mock

            pdf_bytes = await gerar_pdf_declaracao(user, 2025, db)
            assert pdf_bytes is None
