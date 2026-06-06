import os

os.environ["APP_ENV"] = "test"
os.environ["JWT_SECRET"] = "test-secret-key-nao-usar-em-producao"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_ROLE"] = "test-service-role"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ACCESS_KEY"] = "test-access"
os.environ["MINIO_SECRET_KEY"] = "test-secret"
os.environ["OLLAMA_HOST"] = "http://localhost:11434"
os.environ["CORS_ORIGINS"] = '["*"]'

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database.session import get_db, Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def test_user(client):
    response = await client.post("/auth/register", json={
        "email": "teste@teste.com",
        "cpf": "52998224725",
        "senha": "senha12345",
        "nome": "Teste da Silva",
        "lgpd_consent": True,
    })
    return response.json()


@pytest.fixture
async def token(client, test_user):
    response = await client.post("/auth/login", json={
        "email": "teste@teste.com",
        "senha": "senha12345",
    })
    return response.json()["access_token"]


@pytest.fixture
async def auth_client(client, token):
    client.headers["Authorization"] = f"Bearer {token}"
    return client
