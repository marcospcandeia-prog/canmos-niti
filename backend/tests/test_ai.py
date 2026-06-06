import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient

from app.shared.models.ai import AIInteraction


@pytest.fixture(autouse=True)
def reset_ai_singletons():
    import app.modules.ai.router as ai_router
    import app.modules.ai.service as ai_service
    ai_router._assistant = None
    ai_service._llm_instance = None
    ai_service._embeddings_instance = None


@pytest.fixture
def mock_chat_ollama():
    with patch('app.modules.ai.service.ChatOllama') as mock:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="Resposta do assistente tributário")
        mock.return_value = mock_instance
        yield mock


@pytest.mark.asyncio
async def test_chat_unauthorized(client: AsyncClient):
    response = await client.post("/ai/chat", json={"mensagem": "teste"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_success(auth_client: AsyncClient, mock_chat_ollama):
    response = await auth_client.post("/ai/chat", json={
        "mensagem": "Como declarar rendimentos?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["resposta"] == "Resposta do assistente tributário"
    assert "conversation_id" in data
    assert data["model"] == "llama3.2:3b"
    assert isinstance(data["fontes"], list)


@pytest.mark.asyncio
async def test_chat_creates_interaction_in_db(auth_client: AsyncClient, mock_chat_ollama, db_session):
    response = await auth_client.post("/ai/chat", json={
        "mensagem": "Quanto de imposto vou pagar?"
    })
    assert response.status_code == 200
    data = response.json()

    from sqlalchemy import select
    stmt = select(AIInteraction).where(
        AIInteraction.conversation_id == data["conversation_id"]
    )
    result = await db_session.execute(stmt)
    interaction = result.scalar_one_or_none()
    assert interaction is not None
    assert interaction.pergunta == "Quanto de imposto vou pagar?"
    assert interaction.resposta == "Resposta do assistente tributário"


@pytest.mark.asyncio
async def test_chat_with_existing_conversation(auth_client: AsyncClient, mock_chat_ollama):
    conv_id = "test-conversation-123"
    response = await auth_client.post("/ai/chat", json={
        "mensagem": "Primeira pergunta",
        "conversation_id": conv_id,
    })
    assert response.status_code == 200
    assert response.json()["conversation_id"] == conv_id

    response2 = await auth_client.post("/ai/chat", json={
        "mensagem": "Segunda pergunta",
        "conversation_id": conv_id,
    })
    assert response2.status_code == 200
    assert response2.json()["conversation_id"] == conv_id

    # Same conversation, history preserved
    assert mock_chat_ollama.return_value.invoke.call_count == 2


@pytest.mark.asyncio
async def test_chat_handles_llm_error(auth_client: AsyncClient, mock_chat_ollama):
    mock_chat_ollama.return_value.invoke.side_effect = Exception("Ollama timeout")

    response = await auth_client.post("/ai/chat", json={
        "mensagem": "teste erro"
    })
    assert response.status_code == 200
    data = response.json()
    assert "ocorreu um erro" in data["resposta"].lower()


@pytest.mark.asyncio
async def test_health_online(auth_client: AsyncClient, mock_chat_ollama):
    response = await auth_client.get("/ai/health")
    assert response.status_code == 200
    data = response.json()
    assert data["llm"] is True
    assert data["service"] == "ai"
    assert "model" in data


@pytest.mark.asyncio
async def test_health_offline(auth_client: AsyncClient):
    with patch('app.modules.ai.service.get_llm', return_value=None):
        import app.modules.ai.router as ai_router
        import app.modules.ai.service as ai_service
        ai_router._assistant = None
        ai_service._llm_instance = None

        response = await auth_client.get("/ai/health")
        assert response.status_code == 200
        data = response.json()
        assert data["llm"] is False


@pytest.mark.asyncio
async def test_clear_history(auth_client: AsyncClient):
    response = await auth_client.post("/ai/clear")
    assert response.status_code == 200
    assert response.json()["mensagem"] == "Historico limpo"


@pytest.mark.asyncio
async def test_conversations_empty(auth_client: AsyncClient):
    response = await auth_client.get("/ai/conversations")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_conversation_messages_empty(auth_client: AsyncClient):
    response = await auth_client.get("/ai/conversations/test-123/messages")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_conversation_messages_after_chat(auth_client: AsyncClient, mock_chat_ollama):
    conv_id = "msg-test-conv"
    await auth_client.post("/ai/chat", json={
        "mensagem": "Minha pergunta",
        "conversation_id": conv_id,
    })

    response = await auth_client.get(f"/ai/conversations/{conv_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Minha pergunta"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Resposta do assistente tributário"


@pytest.mark.asyncio
async def test_health_unauthorized(client: AsyncClient):
    response = await client.get("/ai/health")
    assert response.status_code == 200  # Health endpoint does not require auth
