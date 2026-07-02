"""Tests de integración para GET /api/v1/metrics/dashboard.

Usa conftest.py compartido: fixture `client` (TestClient con BD en memoria)
y fixture `db_session` (sesión SQLAlchemy para crear datos de prueba).
"""
from datetime import datetime, timedelta, timezone

from src.models.client import Client
from src.models.interaction import Interaction

PREFIX = "/api/v1/metrics"


def test_dashboard_returns_all_sections(client):
    """Verifica que la respuesta tenga las secciones esperadas según spec."""
    resp = client.get(f"{PREFIX}/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "interactionsBySource" in data
    assert "interactionsTimeline" in data
    assert "registrationsByMonth" in data
    assert "topIntents" in data


def test_dashboard_summary_with_data(client, db_session):
    """Crea 3 clientes no-admin + 1 admin, y 10 interacciones.
    Verifica totalClients, activeClients, inactiveClients, totalInteractions,
    interactionsToday e interactionsThisWeek.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today_start - timedelta(days=7)

    # 3 clientes no-admin (2 activos, 1 inactivo) + 1 admin
    for i in range(3):
        db_session.add(Client(
            nombre=f"User{i}", apellido="T",
            email=f"user{i}@x.com", activo=(i != 1),
        ))
    db_session.add(Client(
        nombre="Admin", apellido="X",
        email="admin@x.com", role="admin",
    ))
    db_session.flush()

    # Interacciones: 2 hoy, 3 esta-semana (pero no hoy), 5 viejas = 10 total
    for i in range(2):
        db_session.add(Interaction(
            source="telegram", payload=f'{{"n":{i}}}',
            timestamp=today_start + timedelta(hours=i),
        ))
    for i in range(3):
        db_session.add(Interaction(
            source="api", payload=f'{{"n":{i}}}',
            timestamp=today_start - timedelta(days=i + 1),
        ))
    for i in range(5):
        db_session.add(Interaction(
            source="telegram", payload=f'{{"n":{i}}}',
            timestamp=today_start - timedelta(days=14 + i),
        ))
    db_session.commit()

    resp = client.get(f"{PREFIX}/dashboard")
    assert resp.status_code == 200
    s = resp.json()["summary"]

    assert s["totalClients"] == 3, f"expected 3, got {s['totalClients']}"
    assert s["activeClients"] == 2, f"expected 2, got {s['activeClients']}"
    assert s["inactiveClients"] == 1, f"expected 1, got {s['inactiveClients']}"
    assert s["totalInteractions"] == 10, f"expected 10, got {s['totalInteractions']}"
    assert s["interactionsToday"] == 2, f"expected 2, got {s['interactionsToday']}"
    # interactionsThisWeek = 2 (hoy) + 3 (esta semana pero no hoy) = 5
    assert s["interactionsThisWeek"] == 5, f"expected 5, got {s['interactionsThisWeek']}"


def test_dashboard_returns_empty_timeline_when_no_data(client):
    """Cuando no hay interacciones, el timeline debe tener 30 días con count 0."""
    resp = client.get(f"{PREFIX}/dashboard")
    assert resp.status_code == 200
    timeline = resp.json()["interactionsTimeline"]
    assert len(timeline) == 30, f"expected 30, got {len(timeline)}"
    for entry in timeline:
        assert entry["count"] == 0, f"expected 0 for {entry['date']}, got {entry['count']}"


def test_dashboard_interactions_by_source(client, db_session):
    """Crea interacciones con distintas fuentes y verifica el agrupamiento."""
    db_session.add(Interaction(source="telegram", payload='{"msg":"a"}'))
    db_session.add(Interaction(source="telegram", payload='{"msg":"b"}'))
    db_session.add(Interaction(source="api", payload='{"msg":"c"}'))
    db_session.commit()

    resp = client.get(f"{PREFIX}/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["interactionsBySource"] == {
        "telegram": 2,
        "api": 1,
    }
