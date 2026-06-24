"""Test de integración para endpoint POST /api/v1/clients."""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.base import Base
from src.database.session import get_db
from src.api.routes.clients import router

# Crear app de prueba con el mismo router que usa la app real
app = FastAPI()
app.include_router(router, prefix="/api/v1/clients")


@pytest.fixture
def client():
    """Crea app de prueba con BD SQLite en memoria y retorna TestClient."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        """Sobrescribe get_db para usar la BD en memoria del test."""
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Aplicar override de dependencia en la app de prueba
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Limpiar overrides después del test
    app.dependency_overrides.clear()


def test_post_creates(client):
    resp = client.post(
        "/api/v1/clients/",
        json={"nombre": "Juan", "apellido": "Perez", "email": "e@x.com"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "e@x.com"
    assert data["nombre"] == "Juan"
    assert data["apellido"] == "Perez"
    assert "id" in data
    assert "fecha_registro" in data
    assert data["activo"] is True
