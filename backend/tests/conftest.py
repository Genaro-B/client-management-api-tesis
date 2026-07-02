"""Fixtures compartidas para tests de la API.

Provee:
- db_session: sesión SQLite en memoria con todas las tablas creadas
- client: TestClient de FastAPI con BD en memoria y API_KEY configurada
- auth_headers: headers con X-Api-Key válida para endpoints autenticados
- sample_client: un cliente persistido listo para usar en tests
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.base import Base
from src.database.session import get_db
from src.main import create_app
from src.models.client import Client
from src.repositories.client_repo import ClientRepository

TEST_API_KEY = "dev-api-key-123"


@pytest.fixture(scope="function")
def db_session():
    """Crea una sesión SQLite en memoria con todas las tablas creadas.
    Cada test obtiene una BD limpia.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Retorna un TestClient de FastAPI con BD en memoria.
    La dependencia get_db se sobrescribe para usar db_session.
    """
    os.environ["API_KEY"] = TEST_API_KEY
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # db_session se cierra en su fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers():
    """Headers con API key válida para endpoints que requieren autenticación."""
    return {"X-Api-Key": TEST_API_KEY}


@pytest.fixture(scope="function")
def sample_client(db_session):
    """Crea y persiste un cliente de prueba activo."""
    repo = ClientRepository(db_session)
    client = Client(
        nombre="Ana",
        apellido="Garcia",
        email="ana@test.com",
        telefono="+541111111111",
    )
    return repo.create(client)


@pytest.fixture(scope="function")
def sample_inactive_client(db_session):
    """Crea y persiste un cliente inactivo (soft-deleted) de prueba."""
    repo = ClientRepository(db_session)
    client = Client(
        nombre="Inactivo",
        apellido="User",
        email="inactivo@test.com",
        activo=False,
    )
    return repo.create(client)
