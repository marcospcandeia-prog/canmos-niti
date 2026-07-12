import logging
from typing import Any

from app.modules.tax_engine.parsers import PARSER_REGISTRY
from app.modules.tax_engine.parsers.base import ParseResult

logger = logging.getLogger(__name__)

CONFIANCA_MINIMA = 0.3


def classificar_documento(texto: str) -> tuple[str | None, float]:
    melhor_tipo: str | None = None
    melhor_confianca = 0.0

    for tipo_doc, parser_cls in PARSER_REGISTRY.items():
        parser = parser_cls()
        confianca = parser.identificar(texto)
        if confianca > melhor_confianca:
            melhor_confianca = confianca
            melhor_tipo = tipo_doc

    return melhor_tipo, melhor_confianca


def parsear_documento(texto: str, tipo_documento: str | None = None) -> ParseResult:
    if not tipo_documento:
        tipo_documento, confianca = classificar_documento(texto)
        if tipo_documento and confianca < CONFIANCA_MINIMA:
            result = ParseResult()
            result.add_erro(f"Confianca baixa ({confianca:.2f}) para classificar documento")
            result.confianca_geral = confianca
            return result

    if not tipo_documento:
        result = ParseResult()
        result.add_erro("Nao foi possivel classificar o documento")
        return result

    parser_cls = PARSER_REGISTRY.get(tipo_documento)
    if not parser_cls:
        result = ParseResult()
        result.add_erro(f"Parser nao encontrado para: {tipo_documento}")
        return result

    parser = parser_cls()
    return parser.parsear(texto)


def extrair_eventos_de_ocr(
    documento_id: int,
    texto_ocr: str,
) -> list[dict[str, Any]]:
    result = parsear_documento(texto_ocr)

    if not result.sucesso:
        logger.warning(
            "Falha ao extrair eventos do documento %d: %s",
            documento_id, "; ".join(result.erros),
        )
        return []

    logger.info(
        "Extraidos %d eventos do documento %d (confianca: %.2f)",
        len(result.eventos), documento_id, result.confianca_geral,
    )

    return result.eventos
