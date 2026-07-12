from decimal import Decimal


class Validacao:
    def __init__(self, tipo: str, severidade: str, mensagem: str, campo: str | None = None):
        self.tipo = tipo
        self.severidade = severidade
        self.mensagem = mensagem
        self.campo = campo

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "severidade": self.severidade,
            "mensagem": self.mensagem,
            "campo": self.campo,
        }


LIMITE_ISENCAO = {
    2025: Decimal("2259.20"),
    2024: Decimal("2112.00"),
}

TETO_PREVIDENCIA = {
    2025: Decimal("815.40"),
    2024: Decimal("792.00"),
}

LIMITE_DEDUCAO_MEDICA = None
LIMITE_DEDUCAO_EDUCACAO = {
    2025: Decimal("3541.50"),
    2024: Decimal("3456.00"),
}


class IRPFValidator:
    @staticmethod
    def validar_eventos(eventos: list[dict], ano_base: int) -> list[Validacao]:
        validacoes: list[Validacao] = []

        rendimentos = [e for e in eventos if e.get("categoria", "").startswith("rendimento")]
        deducoes_medicas = [e for e in eventos if e.get("categoria") == "despesa_medica"]
        deducoes_educacao = [e for e in eventos if e.get("categoria") == "despesa_educacao"]
        previdencias = [e for e in eventos if e.get("categoria") == "despesa_previdencia"]

        total_rendimentos = sum(e["valor"] for e in rendimentos)
        total_medicas = sum(e["valor"] for e in deducoes_medicas)
        total_educacao = sum(e["valor"] for e in deducoes_educacao)
        total_previdencia = sum(e["valor"] for e in previdencias)

        if total_rendimentos == Decimal("0"):
            validacoes.append(Validacao(
                "sem_rendimento", "warning",
                "Nenhum rendimento informado para o ano base"
            ))

        if total_rendimentos > Decimal("0") and total_rendimentos <= LIMITE_ISENCAO.get(ano_base, Decimal("2259.20")):
            validacoes.append(Validacao(
                "abaixo_limite_isencao", "info",
                f"Rendimentos abaixo do limite de isencao ({LIMITE_ISENCAO.get(ano_base, 'N/A')})"
            ))

        if total_medicas > Decimal("0"):
            total_alto_med = total_medicas > total_rendimentos * Decimal("0.3")
            if total_alto_med:
                validacoes.append(Validacao(
                    "despesa_medica_alta", "warning",
                    "Despesas medicas ultrapassam 30% dos rendimentos. Poderao ser glosadas pela Receita."
                ))

        limite_edu = LIMITE_DEDUCAO_EDUCACAO.get(ano_base, Decimal("3541.50"))
        if total_educacao > limite_edu:
            validacoes.append(Validacao(
                "deducao_educacao_excedida", "warning",
                f"Despesas com educacao excedem o limite legal de R$ {limite_edu:.2f} "
                f"(informado: R$ {total_educacao:.2f})"
            ))

        teto_prev = TETO_PREVIDENCIA.get(ano_base, Decimal("815.40"))
        if total_previdencia > teto_prev * 12:
            validacoes.append(Validacao(
                "previdencia_acima_teto", "warning",
                "Contribuicao previdenciaria acima do teto anual"
            ))

        if total_medicas > Decimal("0"):
            for e in deducoes_medicas:
                if e["valor"] > Decimal("10000"):
                    validacoes.append(Validacao(
                        "despesa_medica_muito_alta", "info",
                        f"Despesa medica de R$ {e['valor']:.2f} pode requerer comprovacao adicional"
                    ))

        eventos_repetidos = IRPFValidator._detectar_repeticao(eventos)
        validacoes.extend(eventos_repetidos)

        return validacoes

    @staticmethod
    def _detectar_repeticao(eventos: list[dict]) -> list[Validacao]:
        validacoes: list[Validacao] = []
        vistos: dict[str, list[Decimal]] = {}

        for e in eventos:
            chave = f"{e.get('categoria')}"
            if chave not in vistos:
                vistos[chave] = []
            vistos[chave].append(e["valor"])

        for categoria, valores in vistos.items():
            if len(valores) >= 3:
                valores_ordenados = sorted(valores)
                if valores_ordenados[-1] == valores_ordenados[0]:
                    validacoes.append(Validacao(
                        "possivel_repeticao", "warning",
                        f"Detectados {len(valores)} eventos identicos em '{categoria}'. "
                        "Verifique se ha duplicatas."
                    ))

        return validacoes
