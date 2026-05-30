import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db, get_engine, reset_engine
from app.main import app

TEST_DB_URL = os.getenv(
    "INTEGRATION_DATABASE_URL",
    "postgresql://canmos:canmos123@localhost:5433/canmos_niti_test",
)


@pytest.fixture(scope="session")
def engine():
    reset_engine()
    settings.DATABASE_URL = TEST_DB_URL
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db(engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine):
    def override_get_db():
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {
        "nome": "Teste Integracao",
        "cpf": "52998224725",
        "email": "integracao@email.com",
        "telefone": "11988888888",
        "senha": "senha123",
    }
