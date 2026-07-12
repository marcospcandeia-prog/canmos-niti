import logging

from qdrant_client.models import PointStruct

from app.modules.ai.rag_service import (
    get_qdrant_client,
    get_embeddings_client,
    VECTOR_SIZE,
)

logger = logging.getLogger(__name__)

LEGISLATION_COLLECTION = "tax_legislation"

IRPF_LEGISLATION = [
    {
        "id": 1,
        "titulo": "Lei 7.713/1988 - Imposto de Renda e Proventos",
        "texto": "Art. 6º Os seguintes rendimentos são isentos do imposto de renda: I - os recebidos por aposentadoria, pensão, transferência para a reserva ou reforma; II - os recebidos por militares das Forças Armadas; III - os recebidos por pensionistas dos militares das Forças Armadas; IV - os proventos de aposentadoria ou reforma recebidos por qualquer pessoa física.",
        "tags": ["isencao", "aposentadoria", "pensão", "reforma"],
    },
    {
        "id": 2,
        "titulo": "Lei 9.250/1996 - Deduções do IRPF",
        "texto": "Art. 8º Podem ser deduzidos do imposto de renda devido na declaração: I - pagamentos efetuados a médicos, dentistas, psicólogos, fisioterapeutas, terapeutas ocupacionais, fonoaudiólogos, hospitais, e as despesas provenientes de exames laboratoriais, serviços radiológicos, aparelhos ortopédicos e próteses ortopédicas e dentárias; II - despesas com instrução do declarante ou de seus dependentes, em estabelecimentos de ensino fundamental, médio e superior.",
        "tags": ["dedução", "médico", "dentista", "psicólogo", "educação", "despesa médica"],
    },
    {
        "id": 3,
        "titulo": "Instrução Normativa RFB 1.500/2014 - Rendimentos Tributáveis",
        "texto": "São rendimentos tributáveis os recebidos de pessoas jurídicas e os recebidos de pessoas físicas quando decorrentes do trabalho não-assalariado, do aluguel ou arrendamento de bens móveis ou imóveis, e de pensões alimentícias recebidas judicialmente.",
        "tags": ["rendimento tributável", "aluguel", "trabalho autônomo", "pensão"],
    },
    {
        "id": 4,
        "titulo": "Lei 9.430/1996 - Tabela Progressiva do IRPF",
        "texto": "A base de cálculo do imposto, na declaração de ajuste, é o valor dos rendimentos tributáveis auferidos no ano-calendário, diminuído das deduções previstas em lei. A tabela progressiva anual para o ano-calendário 2025 considera as seguintes faixas: até R$ 28.909,32 isento; de R$ 28.909,33 até R$ 37.433,88 alíquota de 7,5%; de R$ 37.433,89 até R$ 46.646,76 alíquota de 15%; de R$ 46.646,77 até R$ 55.976,16 alíquota de 22,5%; acima de R$ 55.976,16 alíquota de 27,5%.",
        "tags": ["tabela progressiva", "base de cálculo", "faixas", "alíquota", "isenção"],
    },
    {
        "id": 5,
        "titulo": "Decreto 3.000/1999 - Regulamento do Imposto de Renda (RIR/99)",
        "texto": "Art. 77. São dedutíveis na determinação do lucro real as contribuições para entidades de previdência complementar, desde que o valor não exceda a 12% do total dos rendimentos tributáveis. Art. 78. São também dedutíveis as pensões alimentícias pagas em cumprimento de decisão judicial ou acordo homologado judicialmente.",
        "tags": ["previdência complementar", "pensão alimentícia", "dedução", "12%"],
    },
    {
        "id": 6,
        "titulo": "Instrução Normativa RFB 2.037/2021 - Obrigações Fiscais",
        "texto": "Estão obrigados a apresentar a Declaração de Ajuste Anual do Imposto sobre a Renda da Pessoa Física (DIRPF) relativa ao ano-calendário de 2024, a ser apresentada no exercício de 2025: I - as pessoas físicas residentes no Brasil que receberam rendimentos tributáveis, no ano de 2024, sujeitos a ajuste na declaração, cujos rendimentos tributáveis tenham sido superiores a R$ 28.909,32.",
        "tags": ["obrigação", "declaração", "ajuste anual", "DIRPF", "limite"],
    },
    {
        "id": 7,
        "titulo": "Lei 11.051/2004 - Restituição do Imposto de Renda",
        "texto": "A restituição do imposto de renda será corrigida pela taxa Selic, acumulada mensalmente, a partir do mês seguinte ao do vencimento do prazo para entrega da declaração até o mês anterior ao do pagamento, e de 1% no mês do pagamento. O contribuinte que não entregar a declaração dentro do prazo ficará sujeito à multa de 1% ao mês-calendário ou fração de atraso.",
        "tags": ["restituição", "Selic", "multa", "prazo", "atraso"],
    },
    {
        "id": 8,
        "titulo": "Instrução Normativa RFB 1.756/2017 - Dependentes",
        "texto": "Podem ser considerados dependentes para fins do Imposto de Renda: I - o cônjuge ou companheiro; II - os filhos ou enteados até 21 anos, ou em qualquer idade quando incapacitados física ou mentalmente para o trabalho; III - os filhos ou enteados até 24 anos se ainda estiverem cursando ensino superior ou escola técnica de segundo grau; IV - os irmãos, netos ou bisnetos, sem arrimo dos pais, até 21 anos, ou até 24 anos se cursando ensino superior.",
        "tags": ["dependente", "filho", "cônjuge", "enteado", "irmão", "neto"],
    },
    {
        "id": 9,
        "titulo": "Lei 12.973/2014 - Ganhos de Capital",
        "texto": "Os ganhos de capital auferidos por pessoa física na alienação de bens ou direitos de qualquer natureza estão sujeitos à incidência do imposto de renda. A alíquota básica é de 15% sobre o ganho de capital. Para ganhos superiores a R$ 5.000.000,00 no mês, aplica-se alíquota de 20%; para ganhos acima de R$ 10.000.000,00, alíquota de 22,5%; e acima de R$ 30.000.000,00, alíquota de 25%.",
        "tags": ["ganho de capital", "alienação", "alíquota", "15%", "venda de imóvel"],
    },
    {
        "id": 10,
        "titulo": "Instrução Normativa RFB 838/2008 - Despesas Médicas",
        "texto": "São dedutíveis as despesas médicas realizadas pelo contribuinte com sua saúde ou de seus dependentes, incluindo: consultas médicas, exames, internações, cirurgias, tratamentos, próteses, órteses, planos de saúde. Não há limite de valor para dedução de despesas médicas, mas a dedução não pode exceder os rendimentos tributáveis. Despesas com acompanhante e transporte também são dedutíveis quando comprovadas.",
        "tags": ["despesa médica", "dedução integral", "plano de saúde", "acompanhante", "sem limite"],
    },
]


def index_legislation() -> bool:
    client = get_qdrant_client()
    embeddings = get_embeddings_client()

    if not client or not embeddings:
        logger.warning("Qdrant or embeddings not available for legislation indexing")
        return False

    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if LEGISLATION_COLLECTION not in collection_names:
            from qdrant_client.models import VectorParams, Distance
            client.create_collection(
                collection_name=LEGISLATION_COLLECTION,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info(f"Created legislation collection: {LEGISLATION_COLLECTION}")

        points = []
        for item in IRPF_LEGISLATION:
            vector = embeddings.embed_query(item["texto"])
            point = PointStruct(
                id=item["id"],
                vector=vector,
                payload={
                    "titulo": item["titulo"],
                    "texto": item["texto"],
                    "tags": item["tags"],
                    "tipo": "legislacao",
                },
            )
            points.append(point)

        client.upsert(collection_name=LEGISLATION_COLLECTION, points=points)
        logger.info(f"Indexed {len(points)} legislation articles")
        return True
    except Exception as e:
        logger.error(f"Failed to index legislation: {e}")
        return False


def search_legislation(query: str, limit: int = 3) -> list[dict]:
    client = get_qdrant_client()
    embeddings = get_embeddings_client()

    if not client or not embeddings:
        logger.warning("Qdrant or embeddings not available for legislation search")
        return []

    try:
        query_vector = embeddings.embed_query(query)

        results = client.search(
            collection_name=LEGISLATION_COLLECTION,
            query_vector=query_vector,
            limit=limit,
        )

        sources = []
        for hit in results:
            payload = hit.payload
            sources.append({
                "titulo": payload.get("titulo", ""),
                "texto": payload.get("texto", "")[:500],
                "tags": payload.get("tags", []),
                "score": hit.score,
            })

        logger.info(f"Found {len(sources)} legislation articles for query")
        return sources
    except Exception as e:
        logger.error(f"Failed to search legislation: {e}")
        return []


def check_legislation_available() -> bool:
    client = get_qdrant_client()
    if not client:
        return False

    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        return LEGISLATION_COLLECTION in collection_names
    except Exception:
        return False
