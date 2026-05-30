"""
Tabelas oficiais IRPF — atualizadas 2024.
Fonte: RFB — Instrução Normativa 2.178/2024.
TOTALMENTE DETERMINÍSTICO. Nunca usar IA aqui.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TaxBracket:
    limite_superior: Decimal  # None = sem limite
    aliquota: Decimal
    deducao: Decimal


# Tabela IRPF 2024 — Base anual
TABELA_IRPF_2024 = [
    TaxBracket(Decimal("26963.20"),  Decimal("0.000"), Decimal("0.00")),
    TaxBracket(Decimal("33919.80"),  Decimal("0.075"), Decimal("2023.74")),
    TaxBracket(Decimal("45012.60"),  Decimal("0.150"), Decimal("4764.06")),
    TaxBracket(Decimal("55976.16"),  Decimal("0.225"), Decimal("8148.39")),
    TaxBracket(None,                  Decimal("0.275"), Decimal("10956.47")),
]

# Deduções legais 2024
DEDUCAO_DEPENDENTE_ANUAL = Decimal("2275.08")       # por dependente
DEDUCAO_EDUCACAO_LIMITE = Decimal("3561.50")        # limite por pessoa
DEDUCAO_INSS_MAX = Decimal("0")                     # sem limite (real)
DEDUCAO_PENSAO_ALIMENTICIA = Decimal("0")           # sem limite (judicial)

# Desconto simplificado
DESCONTO_SIMPLIFICADO = Decimal("0.20")             # 20% da base
DESCONTO_SIMPLIFICADO_LIMITE = Decimal("16754.34")  # teto 2024
