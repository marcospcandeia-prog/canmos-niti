from app.modules.tax_engine.parsers.informe_rendimentos_parser import InformeRendimentosParser
from app.modules.tax_engine.parsers.recibo_medico_parser import ReciboMedicoParser
from app.modules.tax_engine.parsers.comprovante_educacao_parser import ComprovanteEducacaoParser
from app.modules.tax_engine.parsers.darf_parser import DARFParser
from app.modules.tax_engine.parsers.informe_investimentos_parser import InformeInvestimentosParser
from app.modules.tax_engine.parsers.pensao_alimenticia_parser import PensaoAlimenticiaParser
from app.modules.tax_engine.parsers.base import BaseParser

__all__ = [
    "BaseParser",
    "InformeRendimentosParser",
    "ReciboMedicoParser",
    "ComprovanteEducacaoParser",
    "DARFParser",
    "InformeInvestimentosParser",
    "PensaoAlimenticiaParser",
]

PARSER_REGISTRY = {
    "informe_rendimentos": InformeRendimentosParser,
    "recibo_medico": ReciboMedicoParser,
    "comprovante_educacao": ComprovanteEducacaoParser,
    "darfs": DARFParser,
    "informe_investimentos": InformeInvestimentosParser,
    "pensao_alimenticia": PensaoAlimenticiaParser,
}


def get_parser(tipo_documento: str) -> BaseParser | None:
    parser_cls = PARSER_REGISTRY.get(tipo_documento)
    if parser_cls:
        return parser_cls()
    return None
