"""
Serviço de IA Tributária — Ollama + LangChain.
A IA é copiloto: explica, orienta, resume.
Nunca interfere no Tax Engine.
"""
from typing import Generator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from .prompts import SYSTEM_PROMPT_TRIBUTARIO


def _build_llm(streaming: bool = False) -> ChatOllama:
    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.3,
        streaming=streaming,
    )


def chat_tributario(
    pergunta: str,
    contexto_usuario: str = "",
    documentos_resumo: str = "",
) -> str:
    """Resposta completa (não-streaming)."""
    llm = _build_llm(streaming=False)

    system = SYSTEM_PROMPT_TRIBUTARIO.format(
        contexto_usuario=contexto_usuario or "Nenhum contexto disponível",
        documentos_resumo=documentos_resumo or "Nenhum documento processado ainda",
    )

    messages = [
        SystemMessage(content=system),
        HumanMessage(content=pergunta),
    ]

    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Serviço de IA temporariamente indisponível. Erro: {str(e)[:100]}"


def chat_tributario_stream(
    pergunta: str,
    contexto_usuario: str = "",
    documentos_resumo: str = "",
) -> Generator[str, None, None]:
    """Stream de tokens para resposta em tempo real."""
    llm = _build_llm(streaming=True)

    system = SYSTEM_PROMPT_TRIBUTARIO.format(
        contexto_usuario=contexto_usuario or "Nenhum contexto disponível",
        documentos_resumo=documentos_resumo or "Nenhum documento processado ainda",
    )

    messages = [
        SystemMessage(content=system),
        HumanMessage(content=pergunta),
    ]

    try:
        for chunk in llm.stream(messages):
            if chunk.content:
                yield chunk.content
    except Exception as e:
        yield f"\n[Erro no serviço de IA: {str(e)[:100]}]"


def build_user_context(user, tax_events: list, documents: list) -> tuple[str, str]:
    """Constrói contexto do usuário para o prompt."""
    ctx = f"Nome: {user.nome}\nPlano: {user.subscription_plan}"
    if hasattr(user, "profile") and user.profile:
        p = user.profile
        ctx += f"\nProfissão: {p.profissao or 'não informada'}"
        ctx += f"\nDependentes: {'sim' if p.possui_dependentes else 'não'}"
        ctx += f"\nInvestimentos: {'sim' if p.possui_investimentos else 'não'}"

    docs_resumo = f"Documentos: {len(documents)} enviados\n"
    if tax_events:
        cats = {}
        for e in tax_events:
            cats[str(e.categoria)] = cats.get(str(e.categoria), 0) + float(e.valor)
        for cat, total in cats.items():
            docs_resumo += f"- {cat}: R$ {total:,.2f}\n"

    return ctx, docs_resumo
