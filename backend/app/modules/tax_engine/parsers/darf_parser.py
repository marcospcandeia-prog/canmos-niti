import re
from decimal import Decimal

from app.modules.tax_engine.parsers.base import BaseParser, ParseResult


class DARFParser(BaseParser):
    PALAVRAS_CHAVE = [
        "darfs", "documento de arrecadação", "receita federal",
        "código de receita", "imposto pago", "paguei",
        "boleto", "arrecadação", "código da receita",
        "valor do documento", "data de vencimento", "autenticação",
    ]

    PADROES = {
        "codigo_receita": r"(?:CÓDIGO|Código|CODIGO)[:\s]*(\d{4})",
        "valor": r"(?:VALOR|Valor|TOTAL)[:\s]*R?\$?\s*([\d.,]+)",
        "vencimento": r"(?:VENCIMENTO|Vencimento|DATA|Data)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})",
        "periodo_apuracao": r"(?:PERÍODO|Periodo|MÊS|Mês|COMPETÊNCIA|Competencia)[:\s]*(\d{2}[/-]\d{4})",
        "cpf_cnpj": r"(\d{3}\.?\d{3}\.?\d{3}-?\d{2})$",
        "autenticacao": r"(?:AUTENTICAÇÃO|Autenticação|AUTENTICACAO)[:\s]*([A-Z0-9]+)",
    }

    CODIGOS_IRPF = ["0211", "0588", "1708", "0190", "0561", "0473", "0504"]

    def identificar(self, texto: str) -> float:
        texto_lower = texto.lower()
        matches = sum(1 for p in self.PALAVRAS_CHAVE if p in texto_lower)

        for codigo in self.CODIGOS_IRPF:
            if codigo in texto:
                matches += 2
                break

        if "6012" in texto or "darfs" in texto_lower:
            matches += 1

        return min(matches / 6.0, 1.0)

    def parsear(self, texto: str) -> ParseResult:
        result = ParseResult()
        result.confianca_geral = self.identificar(texto)

        codigo = None
        for c in self.CODIGOS_IRPF:
            if c in texto:
                codigo = c
                result.add_campo("codigo_receita", codigo, 0.9)
                break

        periodo_match = re.search(self.PADROES["periodo_apuracao"], texto, re.IGNORECASE)
        competencia = self._resolver_competencia(
            texto,
            periodo_str=periodo_match.group(1) if periodo_match else None,
        )

        valor_match = re.search(self.PADROES["valor"], texto, re.IGNORECASE)
        if valor_match:
            valor_str = valor_match.group(1).strip().replace(".", "").replace(",", ".")
            try:
                valor = Decimal(valor_str)
                result.add_campo("valor_pago", valor, 0.8, valor_match.group(0))
                result.add_evento(
                    categoria="imposto_pago",
                    valor=valor,
                    competencia=competencia,
                )
            except Exception:
                result.add_erro("Valor invalido no DARF")

        if periodo_match:
            result.add_campo("periodo_apuracao", periodo_match.group(1).strip(), 0.7)

        if not valor_match:
            result.add_erro("Valor nao encontrado no DARF")

        return result
