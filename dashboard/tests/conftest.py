"""Fixtures compartidas para los tests de las consultas del dashboard.

Replica el patrón de backend/tests/conftest.py (SQLite en memoria con
StaticPool) pero sin tocar FastAPI: solo Base + modelos del backend.

Además agrega backend/ y dashboard/ a sys.path para que `queries` y
`src.models` sean importables desde los tests.
"""
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

DASHBOARD_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = DASHBOARD_DIR.parent / "backend"

for _path in (str(BACKEND_DIR), str(DASHBOARD_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# noqa: F401 — importar los modelos registra sus tablas en Base.metadata
from src.database.base import Base
from src.models.client import Client
from src.models.interaction import Interaction
from src.models.product import Product


@pytest.fixture(scope="function")
def db_session():
    """Sesión SQLite en memoria con todas las tablas del backend creadas."""
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
