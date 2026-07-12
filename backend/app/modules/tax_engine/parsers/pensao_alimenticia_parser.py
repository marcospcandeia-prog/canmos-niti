import re
from decimal import Decimal

from app.modules.tax_engine.parsers.base import BaseParser, ParseResult


class PensaoAlimenticiaParser(BaseParser):
    PALAVRAS_CHAVE = [
        "pensão alimentícia", "pensão", "alimentos", "alimentando",
        "guarda", "menor", "filho", "dependente",
        "sentença", "acórdão", "decisão judicial", "acordo",
        "alimentante", "alimentado", "obrigação alimentar",
        "pensao", "alimenticia", "alimenticia",
    ]

    PADROES = {
        "valor_pensao": r"(?:PENS[ÃA]O|ALIMENTOS?|VALOR\s*DA\s*PENS[ÃA]O)[:\s]*R?\$?\s*([\d.,]+)",
        "porcentagem": r"(\d{1,3}(?:[.,]\d+)?)\s*%\s*(?:DOS?\s*RENDIMENTOS|DO\s*SAL[ÁA]RIO|DA\s*RENDA)",
        "beneficiario": r"(?:BENEFICI[ÁA]RIO|ALIMENTANDO|CRIAN[CÇ]A|MENOR|FILHO)[:\s]*([A-ZÀ-Ú][A-ZÀ-Ú\s]+)",
        "data_inicio": r"(?:IN[ÍI]CIO|VIG[ÊE]NCIA)\s*(?:EM|A\s*PARTIR\s*DE)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})",
    }

    TIPOS = ["pensao_paga", "pensao_recebida"]

    def identificar(self, texto: str) -> float:
        texto_lower = texto.lower()
        matches = sum(1 for p in self.PALAVRAS_CHAVE if p in texto_lower)

        if re.search(r"(?:paga|pago|desconta)", texto_lower) and re.search(r"(?:pens[aã]o|alimentos)", texto_lower):
            matches += 2

        return min(matches / 6.0, 1.0)

    def _detectar_tipo(self, texto: str) -> str:
        texto_lower = texto.lower()
        if any(w in texto_lower for w in ["paga", "pago", "desconta", "descontado", "r$"]):
            return "pensao_paga"
        return "pensao_recebida"

    def parsear(self, texto: str) -> ParseResult:
        result = ParseResult()
        result.confianca_geral = self.identificar(texto)

        tipo = self._detectar_tipo(texto)
        result.add_campo("tipo", tipo, 0.7)

        data_inicio_match = re.search(self.PADROES["data_inicio"], texto, re.IGNORECASE)
        competencia = self._resolver_competencia(
            texto,
            data_str=data_inicio_match.group(1) if data_inicio_match else None,
        )

        valor_match = re.search(self.PADROES["valor_pensao"], texto, re.IGNORECASE)
        if valor_match:
            valor_str = valor_match.group(1).strip().replace(".", "").replace(",", ".")
            try:
                valor = Decimal(valor_str)
                result.add_campo("valor", valor, 0.8, valor_match.group(0))
                result.add_evento(
                    categoria=tipo,
                    valor=valor,
                    competencia=competencia,
                )
            except Exception:
                result.add_erro("Valor da pensao invalido")

        percentual_match = re.search(self.PADROES["porcentagem"], texto, re.IGNORECASE)
        if percentual_match:
            try:
                pct = percentual_match.group(1).replace(",", ".")
                result.add_campo("percentual", Decimal(pct), 0.7)
            except Exception:
                pass

        beneficiario_match = re.search(self.PADROES["beneficiario"], texto, re.IGNORECASE)
        if beneficiario_match:
            result.add_campo("beneficiario", beneficiario_match.group(1).strip(), 0.7)

        if not valor_match:
            result.add_erro("Valor da pensao nao encontrado")

        return result
