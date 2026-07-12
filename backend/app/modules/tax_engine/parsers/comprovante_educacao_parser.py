import re
from decimal import Decimal

from app.modules.tax_engine.parsers.base import BaseParser, ParseResult


class ComprovanteEducacaoParser(BaseParser):
    PALAVRAS_CHAVE = [
        "mensalidade", "escola", "faculdade", "universidade", "curso",
        "educação", "ensino", "matrícula", "anuldade", "semestre",
        "creche", "pré-escola", "fundamental", "médio", "superior",
        "pós-graduação", "mestrado", "doutorado", "especialização",
        "cnpj", "cpf", "instituição", "aluno", "estudante",
        "comprovante", "matriculado", "serie", "ano letivo",
    ]

    def identificar(self, texto: str) -> float:
        texto_lower = texto.lower()
        matches = sum(1 for p in self.PALAVRAS_CHAVE if p in texto_lower)
        return min(matches / 10.0, 1.0)

    def parsear(self, texto: str) -> ParseResult:
        result = ParseResult()
        result.confianca_geral = self.identificar(texto)

        valor_match = re.search(
            r"(?:VALOR|R\$|RS|TOTAL|MENSALIDADE|ANUIDADE)[:\s]*R?\$?\s*([\d.,]+)",
            texto, re.IGNORECASE
        )
        instituicao_match = re.search(
            r"(?:INSTITUIÇÃO|ESCOLA|FACULDADE|UNIVERSIDADE|ESTABELECIMENTO)[:\s]*([A-ZÀ-Ú][A-ZÀ-Ú\s]+)",
            texto, re.IGNORECASE
        )
        aluno_match = re.search(
            r"(?:ALUNO|ESTUDANTE|NOME\s*DO\s*ALUNO)[:\s]*([A-ZÀ-Ú][A-ZÀ-Ú\s]+)",
            texto, re.IGNORECASE
        )
        cnpj_match = re.search(r"CNPJ[:\s]*(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})", texto, re.IGNORECASE)
        periodo_match = re.search(
            r"(?:PERÍODO|ANO|SÉRIE|SEMESTRE)[:\s]*([A-ZÀ-Ú0-9][A-ZÀ-Ú0-9\s]+)",
            texto, re.IGNORECASE
        )

        competencia = self._resolver_competencia(texto)

        if valor_match:
            valor_str = valor_match.group(1).strip().replace(".", "").replace(",", ".")
            try:
                valor = Decimal(valor_str)
                result.add_campo("valor", valor, 0.8, valor_match.group(0))
                result.add_evento(
                    categoria="despesa_educacao",
                    valor=valor,
                    competencia=competencia,
                )
            except Exception:
                result.add_erro("Valor invalido")

        if instituicao_match:
            result.add_campo("instituicao", instituicao_match.group(1).strip(), 0.7)

        if aluno_match:
            result.add_campo("aluno", aluno_match.group(1).strip(), 0.7)

        if cnpj_match:
            result.add_campo("cnpj", cnpj_match.group(1), 0.9)

        if periodo_match:
            result.add_campo("periodo", periodo_match.group(1).strip(), 0.6)

        if not valor_match:
            result.add_erro("Valor nao encontrado no comprovante")

        return result
