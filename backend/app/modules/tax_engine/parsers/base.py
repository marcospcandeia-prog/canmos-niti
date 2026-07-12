from abc import ABC, abstractmethod
import re
from decimal import Decimal
from typing import Any


def extrair_ano_base(texto: str) -> str | None:
    match = re.search(r"(?:ANO[-\s]?BASE|EXERC[ÍI]CIO|REFERENTE\s*A|ANO)[:\s]*(\d{4})", texto, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"\b(20[12]\d)\b", texto)
    if match:
        return match.group(1)
    return None


def data_para_competencia(data_str: str) -> str | None:
    match = re.match(r"(\d{2})[/-](\d{2})[/-](\d{4})", data_str)
    if match:
        dia, mes, ano = match.groups()
        return f"{ano}-{mes}"
    return None


def periodo_para_competencia(periodo_str: str) -> str | None:
    match = re.match(r"(\d{2})[/-](\d{4})", periodo_str.strip())
    if match:
        mes, ano = match.groups()
        return f"{ano}-{mes}"
    return None


class ParsedField:
    def __init__(self, valor: Any, confianca: float, raw: str = ""):
        self.valor = valor
        self.confianca = confianca
        self.raw = raw


class ParseResult:
    def __init__(self):
        self.campos: dict[str, ParsedField] = {}
        self.eventos: list[dict] = []
        self.erros: list[str] = []
        self.confianca_geral: float = 0.0

    def add_campo(self, nome: str, valor: Any, confianca: float, raw: str = ""):
        self.campos[nome] = ParsedField(valor, confianca, raw)

    def add_evento(self, categoria: str, valor: Decimal, competencia: str, metadata: dict | None = None):
        self.eventos.append({
            "categoria": categoria,
            "valor": valor,
            "competencia": competencia,
            "metadata": metadata or {},
        })

    def add_erro(self, erro: str):
        self.erros.append(erro)

    @property
    def sucesso(self) -> bool:
        return len(self.erros) == 0 and self.confianca_geral > 0.3


class BaseParser(ABC):
    @abstractmethod
    def identificar(self, texto: str) -> float:
        pass

    @abstractmethod
    def parsear(self, texto: str) -> ParseResult:
        pass

    def _resolver_competencia(self, texto: str, data_str: str | None = None, periodo_str: str | None = None) -> str:
        if data_str:
            comp = data_para_competencia(data_str)
            if comp:
                return comp
        if periodo_str:
            comp = periodo_para_competencia(periodo_str)
            if comp:
                return comp
        ano = extrair_ano_base(texto)
        if ano:
            return f"{ano}-12"
        return "0000-00"
