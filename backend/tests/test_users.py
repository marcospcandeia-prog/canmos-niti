import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile(auth_client: AsyncClient):
    response = await auth_client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "teste@teste.com"
    assert "nome" in data
    assert "cpf" in data


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_profile(auth_client: AsyncClient):
    response = await auth_client.put("/users/me", json={
        "nome": "Nome Atualizado",
        "telefone": "11999999999",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Nome Atualizado"


@pytest.mark.asyncio
async def test_update_profile_invalid_data(auth_client: AsyncClient):
    response = await auth_client.put("/users/me", json={
        "email": "novo@email.com",
    })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_success(auth_client: AsyncClient):
    response = await auth_client.post("/users/me/change-password", json={
        "senha_atual": "senha12345",
        "senha_nova": "novaSenha678",
        "senha_nova_confirmacao": "novaSenha678",
    })
    assert response.status_code == 200


async def test_change_password_wrong_current(auth_client: AsyncClient):
    response = await auth_client.post("/users/me/change-password", json={
        "senha_atual": "senha_errada",
        "senha_nova": "novaSenha678",
        "senha_nova_confirmacao": "novaSenha678",
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_stats(auth_client: AsyncClient):
    response = await auth_client.get("/users/me/stats")
    assert response.status_code == 200
    assert "total_documents" in response.json()
    assert "declarations_count" in response.json()


@pytest.mark.asyncio
async def test_delete_account(auth_client: AsyncClient):
    response = await auth_client.delete("/users/me")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_access_after_delete(client: AsyncClient, test_user: dict):
    login = await client.post("/auth/login", json={
        "email": "teste@teste.com",
        "senha": "senha12345",
    })
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    await client.delete("/users/me", headers=headers)

    response = await client.get("/users/me", headers=headers)
    assert response.status_code == 403
