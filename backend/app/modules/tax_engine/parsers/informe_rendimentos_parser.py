import re
from decimal import Decimal

from app.modules.tax_engine.parsers.base import BaseParser, ParseResult


class InformeRendimentosParser(BaseParser):
    PADROES = {
        "cpf": r"CPF(?:.*?)(\d{3}\.?\d{3}\.?\d{3}-?\d{2})",
        "cnpj": r"CNPJ(?:.*?)(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})",
        "nome_fonte": r"(?:FONTE\s*PAGADORA|EMPREGADOR|EMPRESA)[:\s]*([A-ZÀ-Ú][A-ZÀ-Ú\s]+)",
        "rendimento_tributavel": r"(?:RENDIMENTO\s*(?:TRIBUT[ÁA]VEL|BRUTO|TOTAL)|Sal[ÁA]rio|TOTAL\s*RENDIMENTOS)[:\s]*R?\$?\s*([\d.,]+)",
        "contribuicao_previdencia": r"(?:CONTRIBUI[CÇ][AÃ]O\s*PREVIDENCI[ÁA]RIA|PREVID[ÊE]NCIA|INSS|CONTRIBUI[CÇ][AÃ]O)[:\s]*R?\$?\s*([\d.,]+)",
        "imposto_retido": r"(?:IMPOSTO\s*(?:DE\s*RENDA\s*)?(?:RETIDO|RETIDO\s*NA\s*FONTE|IRRF)|IR\s*RETIDO|IRRF)[:\s]*R?\$?\s*([\d.,]+)",
        "dependentes": r"(?:DEPENDENTES?|N\.?\s*DEP)[:\s]*(\d+)",
        "pensao_alimenticia": r"(?:PENS[ÃA]O\s*ALIMENT[ÍI]CIA|PENS[ÃA]O)[:\s]*R?\$?\s*([\d.,]+)",
        "ano_base": r"(?:ANO[-\s]BASE|EXERC[ÍI]CIO|REFERENTE\s*A)[:\s]*(\d{4})",
    }

    PALAVRAS_CHAVE = [
        "informe de rendimentos", "informe anual", "rendimentos",
        "irrf", "imposto de renda retido", "fonte pagadora",
        "contribuição previdenciária", "rendimento tributável",
    ]

    def identificar(self, texto: str) -> float:
        texto_lower = texto.lower()
        matches = sum(1 for p in self.PALAVRAS_CHAVE if p in texto_lower)
        confianca = min(matches / len(self.PALAVRAS_CHAVE) * 2.0, 1.0)
        return confianca

    def _extrair_valor(self, texto: str, padrao: str) -> Decimal | None:
        match = re.search(padrao, texto, re.IGNORECASE)
        if not match:
            return None
        valor_str = match.group(1).strip()
        valor_str = valor_str.replace(".", "").replace(",", ".")
        try:
            return Decimal(valor_str)
        except Exception:
            return None

    def parsear(self, texto: str) -> ParseResult:
        result = ParseResult()
        result.confianca_geral = self.identificar(texto)

        competencia = self._resolver_competencia(texto)

        cpf_match = re.search(self.PADROES["cpf"], texto)
        if cpf_match:
            result.add_campo("cpf", cpf_match.group(1), 0.9, cpf_match.group(0))

        nome_match = re.search(self.PADROES["nome_fonte"], texto, re.IGNORECASE)
        if nome_match:
            result.add_campo("fonte_pagadora", nome_match.group(1).strip(), 0.8, nome_match.group(0))

        rendimento = self._extrair_valor(texto, self.PADROES["rendimento_tributavel"])
        if rendimento:
            result.add_campo("rendimento_tributavel", rendimento, 0.7)
            result.add_evento(
                categoria="rendimento_trabalho",
                valor=rendimento,
                competencia=competencia,
            )

        previdencia = self._extrair_valor(texto, self.PADROES["contribuicao_previdencia"])
        if previdencia:
            result.add_campo("contribuicao_previdencia", previdencia, 0.7)
            result.add_evento(
                categoria="despesa_previdencia",
                valor=previdencia,
                competencia=competencia,
            )

        irrf = self._extrair_valor(texto, self.PADROES["imposto_retido"])
        if irrf:
            result.add_campo("imposto_retido", irrf, 0.7)
            result.add_evento(
                categoria="imposto_retencao",
                valor=irrf,
                competencia=competencia,
            )

        pensao = self._extrair_valor(texto, self.PADROES["pensao_alimenticia"])
        if pensao:
            result.add_campo("pensao_alimenticia", pensao, 0.6)
            result.add_evento(
                categoria="pensao_alimenticia",
                valor=pensao,
                competencia=competencia,
            )

        if not rendimento and not previdencia and not irrf:
            result.add_erro("Nao foi possivel extrair dados financeiros do informe")

        return result
