import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "novo@teste.com",
        "cpf": "52998224725",
        "senha": "senha12345",
        "nome": "Novo Usuario",
        "lgpd_consent": True,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "novo@teste.com"
    assert data["nome"] == "Novo Usuario"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_missing_lgpd(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "semlgpd@teste.com",
        "cpf": "52998224725",
        "senha": "senha12345",
        "nome": "Sem LGPD",
        "lgpd_consent": False,
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: dict):
    response = await client.post("/auth/register", json={
        "email": "teste@teste.com",
        "cpf": "12345678909",
        "senha": "senha12345",
        "nome": "Duplicado",
        "lgpd_consent": True,
    })
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_cpf(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "cpfinvalido@teste.com",
        "cpf": "11111111111",
        "senha": "senha12345",
        "nome": "CPF Invalido",
        "lgpd_consent": True,
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: dict):
    response = await client.post("/auth/login", json={
        "email": "teste@teste.com",
        "senha": "senha12345",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 900


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: dict):
    response = await client.post("/auth/login", json={
        "email": "teste@teste.com",
        "senha": "senha_errada",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post("/auth/login", json={
        "email": "naoexiste@teste.com",
        "senha": "senha12345",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user: dict, token: str):
    response_login = await client.post("/auth/login", json={
        "email": "teste@teste.com",
        "senha": "senha12345",
    })
    refresh_token = response_login.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post("/auth/refresh", json={
        "refresh_token": "token_invalido_aqui",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_client: AsyncClient):
    response = await auth_client.post("/auth/logout")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
