import logging
from typing import Optional

from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


_llm_instance = None
_embeddings_instance = None


def get_llm():
    global _llm_instance
    if _llm_instance is None:
        try:
            _llm_instance = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_HOST,
                temperature=0.3,
                num_predict=2048,
            )
            logger.info(f"LLM initialized: {settings.OLLAMA_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            _llm_instance = None
    return _llm_instance


def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        try:
            _embeddings_instance = OllamaEmbeddings(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_HOST,
            )
            logger.info("Embeddings initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            _embeddings_instance = None
    return _embeddings_instance


SYSTEM_PROMPT = """Voce e um assistente especializado em imposto de renda brasileiro (IRPF).
Regras:
1. Responda sempre em portugues brasileiro
2. Use linguagem clara e acessivel
3. Se nao souber a resposta, diga que nao sabe
4. Nao invente informacoes fiscais
5. Mencione que e sempre bom consultar um contador para casos complexos
6. Baseie suas respostas na legislacao brasileira vigente"""


class TaxAssistant:

    def __init__(self):
        self.llm = get_llm()
        self.histories: dict[str, list[dict]] = {}

    def get_or_create_history(self, conversation_id: str) -> list[dict]:
        if conversation_id not in self.histories:
            self.histories[conversation_id] = []
        return self.histories[conversation_id]

    async def ask(self, mensagem: str, conversation_id: str) -> dict:
        response = {
            "resposta": "",
            "fontes": [],
            "conversation_id": conversation_id,
        }

        if self.llm is None:
            response["resposta"] = "O assistente de IA nao esta disponivel no momento. Verifique se o Ollama esta em execucao."
            return response

        history = self.get_or_create_history(conversation_id)

        messages = [("system", SYSTEM_PROMPT)]

        for h in history[-6:]:
            messages.append((h["role"], h["content"]))

        messages.append(("human", mensagem))

        try:
            result = self.llm.invoke(messages)
            resposta = result.content

            history.append({"role": "human", "content": mensagem})
            history.append({"role": "assistant", "content": resposta})

            response["resposta"] = resposta
        except Exception as e:
            logger.error(f"LLM invocation error: {e}")
            response["resposta"] = "Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente."

        return response

    async def check_health(self) -> dict:
        llm_ok = self.llm is not None
        if not llm_ok:
            self.llm = get_llm()
            llm_ok = self.llm is not None
        return {
            "llm": llm_ok,
            "model": settings.OLLAMA_MODEL,
        }
