import pytest
from decimal import Decimal

from app.modules.tax_engine.parsers.informe_rendimentos_parser import InformeRendimentosParser
from app.modules.tax_engine.parsers.recibo_medico_parser import ReciboMedicoParser
from app.modules.tax_engine.parsers.comprovante_educacao_parser import ComprovanteEducacaoParser
from app.modules.tax_engine.parsers.darf_parser import DARFParser
from app.modules.tax_engine.parsers.informe_investimentos_parser import InformeInvestimentosParser
from app.modules.tax_engine.parsers.pensao_alimenticia_parser import PensaoAlimenticiaParser
from app.modules.tax_engine.parsers.classificador import classificar_documento, parsear_documento


class TestInformeRendimentosParser:
    def test_identificar_informe(self):
        parser = InformeRendimentosParser()
        texto = """
        INFORME DE RENDIMENTOS - ANO BASE 2025
        FONTE PAGADORA: EMPRESA ABC LTDA - CNPJ: 11.222.333/0001-44
        CPF: 123.456.789-00
        Rendimento Tributável: R$ 60.000,00
        Contribuição Previdenciária: R$ 5.400,00
        Imposto de Renda Retido na Fonte: R$ 4.200,00
        """
        confianca = parser.identificar(texto)
        assert confianca > 0.5

    def test_parsear_informe_completo(self):
        parser = InformeRendimentosParser()
        texto = """
        INFORME DE RENDIMENTOS - ANO BASE 2025
        FONTE PAGADORA: EMPRESA ABC LTDA
        CPF: 123.456.789-00
        Rendimento Tributável: R$ 60.000,00
        Contribuição Previdenciária: R$ 5.400,00
        Imposto de Renda Retido na Fonte: R$ 4.200,00
        """
        result = parser.parsear(texto)
        assert result.sucesso
        assert result.campos["rendimento_tributavel"].valor == Decimal("60000.00")
        assert result.campos["contribuicao_previdencia"].valor == Decimal("5400.00")
        assert result.campos["imposto_retido"].valor == Decimal("4200.00")
        assert len(result.eventos) == 3

    def test_parsear_informe_sem_dados(self):
        parser = InformeRendimentosParser()
        texto = "Texto qualquer sem dados fiscais"
        result = parser.parsear(texto)
        assert not result.sucesso
        assert len(result.erros) > 0

    def test_extrair_cpf(self):
        parser = InformeRendimentosParser()
        texto = "CPF do contribuinte: 529.982.247-25"
        result = parser.parsear(texto)
        assert result.campos.get("cpf") is not None

    def test_identificar_confianca_baixa(self):
        parser = InformeRendimentosParser()
        texto = "texto aleatorio sem nenhuma palavra chave"
        confianca = parser.identificar(texto)
        assert confianca < 0.3


class TestReciboMedicoParser:
    def test_identificar_recibo(self):
        parser = ReciboMedicoParser()
        texto = """
        RECIBO DE HONORÁRIOS MÉDICOS
        Profissional: Dr. João Silva - CRM 12345
        CPF: 111.222.333-44
        Valor: R$ 500,00
        Data: 15/03/2025
        """
        confianca = parser.identificar(texto)
        assert confianca > 0.5

    def test_parsear_recibo_completo(self):
        parser = ReciboMedicoParser()
        texto = """
        RECIBO
        Profissional: Dr. João Silva
        CRM: 12345
        CPF: 111.222.333-44
        Valor: R$ 500,00
        Data: 15/03/2025
        """
        result = parser.parsear(texto)
        assert result.sucesso
        assert result.campos["valor"].valor == Decimal("500.00")
        assert "joão" in result.campos["profissional"].valor.lower()
        assert len(result.eventos) == 1
        assert result.eventos[0]["categoria"] == "despesa_medica"

    def test_parsear_recibo_sem_valor(self):
        parser = ReciboMedicoParser()
        texto = "Recibo qualquer sem dados de valor"
        result = parser.parsear(texto)
        assert not result.sucesso
        assert len(result.erros) > 0


class TestComprovanteEducacaoParser:
    def test_identificar_educacao(self):
        parser = ComprovanteEducacaoParser()
        texto = """
        COMPROVANTE DE MENSALIDADE
        Instituição: Universidade Federal
        Aluno: Maria Souza
        CNPJ: 11.222.333/0001-44
        Valor: R$ 1.200,00
        Período: 2025.1
        """
        confianca = parser.identificar(texto)
        assert confianca > 0.5

    def test_parsear_educacao_completo(self):
        parser = ComprovanteEducacaoParser()
        texto = """
        MENSALIDADE
        Instituição: Universidade Federal do RJ
        Aluno: Maria Souza
        CNPJ: 11.222.333/0001-44
        Valor: R$ 1.200,00
        """
        result = parser.parsear(texto)
        assert result.sucesso
        assert result.campos["valor"].valor == Decimal("1200.00")
        assert len(result.eventos) == 1
        assert result.eventos[0]["categoria"] == "despesa_educacao"


class TestClassificador:
    def test_classificar_informe(self):
        texto = """
        INFORME DE RENDIMENTOS
        FONTE PAGADORA: EMPRESA ABC
        Rendimento Tributável: R$ 60.000,00
        """
        tipo, confianca = classificar_documento(texto)
        assert tipo == "informe_rendimentos"
        assert confianca > 0.3

    def test_classificar_recibo(self):
        texto = """
        RECIBO MÉDICO
        Profissional: Dr. João
        Valor: R$ 500,00
        """
        tipo, confianca = classificar_documento(texto)
        assert tipo == "recibo_medico"
        assert confianca > 0.3

    def test_classificar_educacao(self):
        texto = """
        MENSALIDADE ESCOLAR
        Instituição: Escola ABC
        Valor: R$ 1.200,00
        """
        tipo, confianca = classificar_documento(texto)
        assert tipo == "comprovante_educacao"
        assert confianca >= 0.3

    def test_classificar_texto_aleatorio(self):
        texto = "um texto qualquer sem significado fiscal"
        tipo, confianca = classificar_documento(texto)
        assert tipo is None or confianca < 0.3

    def test_parsear_documento_com_tipo(self):
        texto = "Valor: R$ 500,00 Profissional: Dr. João CRM 12345"
        result = parsear_documento(texto, tipo_documento="recibo_medico")
        assert result is not None

    def test_parsear_documento_sem_tipo(self):
        texto = """
        INFORME DE RENDIMENTOS
        Rendimento Tributável: R$ 60.000,00
        """
        result = parsear_documento(texto)
        assert result is not None


class TestDARFParser:
    def test_identificar_darf(self):
        parser = DARFParser()
        texto = """
        DARF - Documento de Arrecadação
        Código da Receita: 0211 - Imposto de Renda
        Valor do Documento: R$ 1.500,00
        Data de Vencimento: 15/04/2025
        """
        confianca = parser.identificar(texto)
        assert confianca > 0.5

    def test_parsear_darf_completo(self):
        parser = DARFParser()
        texto = """
        DARF - Documento de Arrecadação de Receitas Federais
        Código 0211 - IRPF
        Valor: R$ 1.500,00
        Vencimento: 15/04/2025
        Período de Apuração: 03/2025
        """
        result = parser.parsear(texto)
        assert result.sucesso
        assert result.campos["valor_pago"].valor == Decimal("1500.00")
        assert len(result.eventos) == 1
        assert result.eventos[0]["categoria"] == "imposto_pago"

    def test_parsear_darf_sem_valor(self):
        parser = DARFParser()
        texto = "Texto qualquer sem dados de DARF"
        result = parser.parsear(texto)
        assert not result.sucesso
        assert len(result.erros) > 0


class TestInformeInvestimentosParser:
    def test_identificar_investimentos(self):
        parser = InformeInvestimentosParser()
        texto = """
        INFORME DE INVESTIMENTOS - BANCO XYZ
        Aplicações em Renda Fixa
        Ações negociadas na B3
        """
        confianca = parser.identificar(texto)
        assert confianca >= 0.5

    def test_parsear_investimentos_completo(self):
        parser = InformeInvestimentosParser()
        texto = """
        INFORME DE INVESTIMENTOS - BANCO XYZ
        Aplicações financeiras em renda fixa
        Rendimento Tributável: R$ 2.000,00
        Imposto de Renda Retido: R$ 300,00
        Dividendos Recebidos: R$ 500,00
        """
        result = parser.parsear(texto)
        assert result.sucesso
        assert result.campos["rendimento_tributavel"].valor == Decimal("2000.00")
        assert result.campos["imposto_retido"].valor == Decimal("300.00")
        assert len(result.eventos) == 2

    def test_parsear_investimentos_sem_dados(self):
        parser = InformeInvestimentosParser()
        texto = "Texto sem dados financeiros"
        result = parser.parsear(texto)
        assert not result.sucesso
        assert len(result.erros) > 0


class TestPensaoAlimenticiaParser:
    def test_identificar_pensao(self):
        parser = PensaoAlimenticiaParser()
        texto = "Pensão Alimentícia paga a filho menor - Valor: R$ 1.200,00"
        confianca = parser.identificar(texto)
        assert confianca >= 0.5

    def test_parsear_pensao_paga(self):
        parser = PensaoAlimenticiaParser()
        texto = """
        Pensão Alimentícia paga
        Valor da Pensão: R$ 1.200,00
        Beneficiário: MARIA SOUZA
        Percentual: 30% dos rendimentos
        """
        result = parser.parsear(texto)
        assert result.sucesso
        assert result.campos["valor"].valor == Decimal("1200.00")
        assert result.campos["tipo"].valor == "pensao_paga"
        assert len(result.eventos) == 1
        assert result.eventos[0]["categoria"] == "pensao_paga"

    def test_parsear_pensao_sem_valor(self):
        parser = PensaoAlimenticiaParser()
        texto = "Documento sobre pensao sem valor especificado"
        result = parser.parsear(texto)
        assert not result.sucesso
        assert len(result.erros) > 0

    @pytest.mark.parametrize("texto", [
        "PAGUEI pensao alimenticia para meu filho R$ 800,00",
    ])
    def test_classificar_pensao_paga(self, texto):
        tipo, confianca = classificar_documento(texto)
        assert tipo == "pensao_alimenticia"
        assert confianca > 0.3
