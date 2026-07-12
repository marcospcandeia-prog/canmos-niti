import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_export_data_unauthorized(client: AsyncClient):
    response = await client.get("/users/me/export")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_data_success(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.get("/users/me/export")
    assert response.status_code == 200

    data = response.json()
    assert "exportado_em" in data
    assert "formato" in data
    assert "dados_pessoais" in data
    assert "documentos" in data
    assert "eventos_fiscais" in data
    assert "declaracoes" in data
    assert "interacoes_ia" in data
    assert "resumo" in data


@pytest.mark.asyncio
async def test_export_data_contains_user_info(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.get("/users/me/export")
    data = response.json()

    assert data["dados_pessoais"]["email"] == "teste@teste.com"
    assert data["dados_pessoais"]["cpf"] == "52998224725"
    assert data["dados_pessoais"]["nome"] == "Teste da Silva"


@pytest.mark.asyncio
async def test_export_data_has_empty_lists_for_new_user(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.get("/users/me/export")
    data = response.json()

    assert data["documentos"] == []
    assert data["eventos_fiscais"] == []
    assert data["declaracoes"] == []
    assert data["interacoes_ia"] == []


@pytest.mark.asyncio
async def test_export_data_resumo_counts(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.get("/users/me/export")
    data = response.json()

    assert data["resumo"]["total_documentos"] == 0
    assert data["resumo"]["total_eventos_fiscais"] == 0
    assert data["resumo"]["total_declaracoes"] == 0
    assert data["resumo"]["total_interacoes_ia"] == 0


@pytest.mark.asyncio
async def test_export_data_format_version(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.get("/users/me/export")
    data = response.json()

    assert data["formato"] == "CANMOS-NITI v1.0"


@pytest.mark.asyncio
async def test_export_data_has_timestamp(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.get("/users/me/export")
    data = response.json()

    assert data["exportado_em"] is not None
    assert "T" in data["exportado_em"]
