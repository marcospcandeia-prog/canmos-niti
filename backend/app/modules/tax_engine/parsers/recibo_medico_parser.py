import re
from decimal import Decimal

from app.modules.tax_engine.parsers.base import BaseParser, ParseResult


class ReciboMedicoParser(BaseParser):
    PALAVRAS_CHAVE = [
        "recibo", "honorários", "consulta", "médico", "odontológico",
        "psicólogo", "fisioterapia", "fonoaudiólogo", "terapia",
        "cirurgia", "exame", "procedimento", "clinica",
        "cbos", "crm", "cro",
    ]

    def identificar(self, texto: str) -> float:
        texto_lower = texto.lower()
        matches = sum(1 for p in self.PALAVRAS_CHAVE if p in texto_lower)
        return min(matches / 6.0, 1.0)

    def parsear(self, texto: str) -> ParseResult:
        result = ParseResult()
        result.confianca_geral = self.identificar(texto)

        valor_match = re.search(
            r"(?:VALOR|R\$|RS|TOTAL|HONORÁRIOS)[:\s]*R?\$?\s*([\d.,]+)",
            texto, re.IGNORECASE
        )
        profissional_match = re.search(
            r"(?:PROFISSIONAL|M[ÉE]DICO|DENTISTA|PSIC[ÓO]LOGO)[:\s]*([A-ZÀ-Ú][A-Za-zÀ-ú\s.]+)",
            texto, re.IGNORECASE
        )
        cpf_match = re.search(r"CPF[:\s]*(\d{3}\.?\d{3}\.?\d{3}-?\d{2})", texto, re.IGNORECASE)
        data_match = re.search(r"(?:DATA|EM)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})", texto, re.IGNORECASE)
        crm_match = re.search(r"(?:CRM|CRO)[:\s]*(\d+)", texto, re.IGNORECASE)

        competencia = self._resolver_competencia(texto, data_str=data_match.group(1) if data_match else None)

        if valor_match:
            valor_str = valor_match.group(1).strip().replace(".", "").replace(",", ".")
            try:
                valor = Decimal(valor_str)
                result.add_campo("valor", valor, 0.8, valor_match.group(0))
                result.add_evento(
                    categoria="despesa_medica",
                    valor=valor,
                    competencia=competencia,
                )
            except Exception:
                result.add_erro("Valor invalido")

        if profissional_match:
            result.add_campo("profissional", profissional_match.group(1).strip(), 0.7)

        if cpf_match:
            result.add_campo("cpf_profissional", cpf_match.group(1), 0.9)

        if crm_match:
            result.add_campo("registro_profissional", crm_match.group(1), 0.8)

        if data_match:
            result.add_campo("data", data_match.group(1), 0.8)

        if not valor_match:
            result.add_erro("Valor nao encontrado no recibo")

        return result
