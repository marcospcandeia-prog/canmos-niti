import re
from decimal import Decimal

from app.modules.tax_engine.parsers.base import BaseParser, ParseResult


class InformeInvestimentosParser(BaseParser):
    PALAVRAS_CHAVE = [
        "informe de investimentos", "aplicação financeira", "renda fixa",
        "renda variável", "ações", "fundos imobiliários", "tesouro direto",
        "cdb", "lcv", "lci", "lca", "poupança",
        "bovespa", "b3", "custódia", "banco", "corretora",
        "proventos", "dividendos", "juros sobre capital", "jscp",
        "rendimento isento", "rendimento tributado", "prejuízo",
    ]

    def identificar(self, texto: str) -> float:
        texto_lower = texto.lower()
        matches = sum(1 for p in self.PALAVRAS_CHAVE if p in texto_lower)
        return min(matches / 8.0, 1.0)

    def parsear(self, texto: str) -> ParseResult:
        result = ParseResult()
        result.confianca_geral = self.identificar(texto)

        competencia = self._resolver_competencia(texto)

        rendimento_tributavel = re.search(
            r"(?:RENDIMENTO\s*(?:TRIBUT[ÁA]VEL|BRUTO|SUJEITO[^\n]*)|APLICA[CÇ][ÕO]ES?\s*(?:TRIBUT[ÁA]VEL|SUJEITO))[:\s]*R?\$?\s*([\d.,]+)",
            texto, re.IGNORECASE
        )
        if rendimento_tributavel:
            valor_str = rendimento_tributavel.group(1).strip().replace(".", "").replace(",", ".")
            try:
                valor = Decimal(valor_str)
                result.add_campo("rendimento_tributavel", valor, 0.7)
                result.add_evento(categoria="rendimento_investimento", valor=valor, competencia=competencia)
            except Exception:
                result.add_erro("Valor de rendimento tributavel invalido")

        rendimento_isento = re.search(
            r"(?:RENDIMENTO\s*ISENTO|ISENTO[^\n]*|NÃO\s*TRIBUT[ÁA]VEL|NAO\s*TRIBUTAVEL)[:\s]*R?\$?\s*([\d.,]+)",
            texto, re.IGNORECASE
        )
        if rendimento_isento:
            valor_str = rendimento_isento.group(1).strip().replace(".", "").replace(",", ".")
            try:
                valor = Decimal(valor_str)
                result.add_campo("rendimento_isento", valor, 0.7)
            except Exception:
                pass

        imposto_retido = re.search(
            r"(?:IMPOSTO\s*(?:DE\s*RENDA\s*)?RETIDO|IRRF|IR\s*RETIDO)[:\s]*R?\$?\s*([\d.,]+)",
            texto, re.IGNORECASE
        )
        if imposto_retido:
            valor_str = imposto_retido.group(1).strip().replace(".", "").replace(",", ".")
            try:
                valor = Decimal(valor_str)
                result.add_campo("imposto_retido", valor, 0.7)
                result.add_evento(categoria="imposto_retencao", valor=valor, competencia=competencia)
            except Exception:
                pass

        dividendos = re.search(
            r"(?:DIVIDENDOS|PROVENTOS|JSCP|JUROS\s*SOBRE\s*CAPITAL)[:\s]*R?\$?\s*([\d.,]+)",
            texto, re.IGNORECASE
        )
        if dividendos:
            valor_str = dividendos.group(1).strip().replace(".", "").replace(",", ".")
            try:
                valor = Decimal(valor_str)
                result.add_campo("dividendos", valor, 0.6)
            except Exception:
                pass

        if not rendimento_tributavel and not imposto_retido:
            result.add_erro("Dados financeiros nao encontrados no informe de investimentos")

        return result
