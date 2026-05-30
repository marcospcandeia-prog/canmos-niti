import pytest

from app.modules.ocr.service import OcrService


class TestOcrExtractText:
    def test_extract_text_empty_content(self, db):
        service = OcrService(db)
        result = service._extract_text(b"")
        assert result == ""

    def test_extract_text_invalid_content(self, db):
        service = OcrService(db)
        result = service._extract_text(b"not an image or pdf")
        assert result == ""


class TestOcrParseTaxEvents:
    def test_parse_rendimento(self, db):
        service = OcrService(db)
        events = service._parse_tax_events(
            "Rendimento R$ 5000,00", user_id="u1", document_id="d1"
        )
        rendimentos = [e for e in events if e.categoria == "rendimento"]
        assert len(rendimentos) >= 1
        assert rendimentos[0].valor == 5000.0

    def test_parse_retencao(self, db):
        service = OcrService(db)
        events = service._parse_tax_events(
            "IRRF R$ 750,00", user_id="u1", document_id="d1"
        )
        retencoes = [e for e in events if e.categoria == "retencao"]
        assert len(retencoes) == 1
        assert retencoes[0].valor == 750.0

    def test_parse_inss(self, db):
        service = OcrService(db)
        events = service._parse_tax_events(
            "INSS R$ 550,00", user_id="u1", document_id="d1"
        )
        inss = [e for e in events if e.categoria == "inss"]
        assert len(inss) == 1
        assert inss[0].valor == 550.0

    def test_parse_dependente(self, db):
        service = OcrService(db)
        events = service._parse_tax_events(
            "Dependente 2", user_id="u1", document_id="d1"
        )
        dep = [e for e in events if e.categoria == "dependente"]
        assert len(dep) == 1
        assert dep[0].valor == 2.0

    def test_parse_no_match_fallback(self, db):
        service = OcrService(db)
        events = service._parse_tax_events(
            "texto aleatório sem padrões", user_id="u1", document_id="d1"
        )
        assert len(events) == 1
        assert events[0].categoria == "nao_classificado"

    def test_parse_multiple_events(self, db):
        service = OcrService(db)
        text = "Rendimento 10000.00\nIRRF 1500.00\nINSS 900.00\nDependente 1"
        events = service._parse_tax_events(text, user_id="u1", document_id="d1")
        categorias = {e.categoria for e in events}
        assert categorias == {"rendimento", "retencao", "inss", "dependente"}

    def test_parse_valor_com_centavos(self, db):
        service = OcrService(db)
        events = service._parse_tax_events(
            "Rendimento R$ 1.234,56", user_id="u1", document_id="d1"
        )
        rend = [e for e in events if e.categoria == "rendimento"]
        assert len(rend) >= 1
        assert rend[0].valor == 1234.56

    def test_parse_salario_pattern(self, db):
        service = OcrService(db)
        events = service._parse_tax_events(
            "Salário R$ 3200,00", user_id="u1", document_id="d1"
        )
        rend = [e for e in events if e.categoria == "rendimento"]
        assert len(rend) >= 1
        assert any(abs(e.valor - 3200.0) < 0.01 for e in rend)

    @pytest.mark.parametrize(
        "texto,esperado",
        [
            ("Provento: 5000", 5000.0),
            ("salario 3000,50", 3000.50),
            ("RENDIMENTO R$ 2500", 2500.0),
        ],
    )
    def test_parse_rendimento_variants(self, db, texto, esperado):
        service = OcrService(db)
        events = service._parse_tax_events(texto, user_id="u1", document_id="d1")
        rend = [e for e in events if e.categoria == "rendimento"]
        assert len(rend) >= 1
        assert any(abs(e.valor - esperado) < 0.01 for e in rend)
