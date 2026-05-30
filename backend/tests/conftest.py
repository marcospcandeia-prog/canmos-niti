import os

import pytest

os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ACCESS_KEY"] = "test"
os.environ["MINIO_SECRET_KEY"] = "test"
os.environ["MINIO_BUCKET"] = "test-bucket"

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import (
    Base,
    get_db,
    get_engine,
    init_db,
    reset_engine,
)
from app.core.security import hash_password
from app.main import app
from app.shared.models.tax import Declaration, DeclarationStatus
from app.shared.models.user import User, UserStatus

TEST_DATABASE_URL = "sqlite:///test.db"
_SESSION_LOCAL = None
_TABLES = []


def get_test_session_local():
    global _SESSION_LOCAL
    if _SESSION_LOCAL is None:
        from sqlalchemy.orm import sessionmaker
        _SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SESSION_LOCAL


def override_get_db():
    db = get_test_session_local()()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    global _TABLES
    reset_engine()
    _SESSION_LOCAL = None
    settings.DATABASE_URL = TEST_DATABASE_URL
    init_db()
    _TABLES = [t for t in Base.metadata.sorted_tables]
    yield
    get_engine().dispose()


@pytest.fixture(autouse=True)
def clear_db():
    yield
    engine = get_engine()
    with engine.begin() as conn:
        for table in reversed(_TABLES):
            conn.execute(table.delete())


@pytest.fixture(autouse=True)
def mock_services():
    with (
        patch("app.modules.storage.service.StorageService._minio_available", return_value=False),
        patch("app.modules.ocr.service.OcrService.process_document", new_callable=AsyncMock),
    ):
        yield


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    session = get_test_session_local()()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user_data():
    return {
        "nome": "Usuario Teste",
        "cpf": "52998224725",
        "email": "teste@email.com",
        "telefone": "11999999999",
        "senha": "senha123",
    }


@pytest.fixture
def test_user(db):
    user = User(
        nome="Usuario Teste",
        cpf="52998224725",
        email="teste@email.com",
        telefone="11999999999",
        senha_hash=hash_password("senha123"),
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user_data):
    client.post("/auth/register", json=test_user_data)
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "senha": test_user_data["senha"],
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_declaration(db, test_user):
    decl = Declaration(
        user_id=test_user.id,
        ano_base="2024",
        status=DeclarationStatus.PENDING,
        total_rendimentos=50000.0,
        total_retencao=7500.0,
        qtd_dependentes=0.0,
        total_deducao_dependentes=0.0,
        restituicao_estimada=1250.0,
        imposto_devido=6250.0,
    )
    db.add(decl)
    db.commit()
    db.refresh(decl)
    return decl
