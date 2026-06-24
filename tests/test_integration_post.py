import pytest
from fastapi.testclient import TestClient
from src.api.v1.clients import router
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base


app = FastAPI()
app.include_router(router.router, prefix="/clients")


@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    # monkeypatch SessionLocal in router
    import src.api.v1.clients.router as r
    r.SessionLocal = Session
    with TestClient(app) as c:
        yield c


def test_post_creates(client):
    resp = client.post("/clients/", json={"nombre":"J","apellido":"K","email":"e@x.com"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "e@x.com"
