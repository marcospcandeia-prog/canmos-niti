import pytest
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession



@pytest.mark.asyncio
async def test_calculate_empty(auth_client: AsyncClient, db_session: AsyncSession):
    response = await auth_client.post("/tax/calculate/2025")
    assert response.status_code == 200
    data = response.json()
    assert "total_rendimentos" in data
    assert "imposto_devido" in data


@pytest.mark.asyncio
async def test_calculate_with_tax_events(auth_client: AsyncClient, test_user: dict):

    response = await auth_client.post("/tax/calculate/2025")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_calculate_unauthorized(client: AsyncClient):
    response = await client.post("/tax/calculate/2025")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_year(auth_client: AsyncClient):
    response = await auth_client.post("/tax/calculate/2019")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_declaration(auth_client: AsyncClient):
    response = await auth_client.post("/tax/declaration/2025")
    assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_create_declaration_twice(auth_client: AsyncClient):
    await auth_client.post("/tax/declaration/2025")
    response = await auth_client.post("/tax/declaration/2025")
    assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_declaration_response_shape(auth_client: AsyncClient):
    response = await auth_client.post("/tax/declaration/2025")
    assert response.status_code in [200, 201]
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert "ano_base" in data
        assert data["ano_base"] == 2025


def test_tax_table_values():
    from app.modules.tax_engine.calculator import IRPF_TABLE_2025
    assert len(IRPF_TABLE_2025) == 5

    faixa1 = IRPF_TABLE_2025[0]
    assert faixa1["aliquota"] == Decimal("0.00")
    assert faixa1["deducao"] == Decimal("0.00")

    faixa5 = IRPF_TABLE_2025[4]
    assert faixa5["aliquota"] == Decimal("0.275")
    assert faixa5["deducao"] == Decimal("896.00")


@pytest.mark.asyncio
async def test_dashboard_summary(auth_client: AsyncClient):
    response = await auth_client.get("/dashboard/summary?ano_base=2025")
    assert response.status_code == 200
    data = response.json()
    assert "ano_base" in data
    assert "restituicao_estimada" in data
    assert "imposto_devido" in data
    assert "total_rendimentos" in data
    assert "documentos_enviados" in data


@pytest.mark.asyncio
async def test_list_declarations_empty(auth_client: AsyncClient):
    response = await auth_client.get("/tax/declarations")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_declarations_after_create(auth_client: AsyncClient):
    await auth_client.post("/tax/declaration/2025")
    response = await auth_client.get("/tax/declarations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["ano_base"] == 2025
    assert "status" in data[0]
    assert "created_at" in data[0]


@pytest.mark.asyncio
async def test_get_declaration_by_year(auth_client: AsyncClient):
    await auth_client.post("/tax/declaration/2025")
    response = await auth_client.get("/tax/declaration/2025")
    assert response.status_code == 200
    data = response.json()
    assert data["ano_base"] == 2025
    assert data["status"] is not None


@pytest.mark.asyncio
async def test_get_declaration_not_found(auth_client: AsyncClient):
    response = await auth_client.get("/tax/declaration/2020")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_declarations_unauthorized(client: AsyncClient):
    response = await client.get("/tax/declarations")
    assert response.status_code == 401
