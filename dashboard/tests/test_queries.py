"""Tests TDD de las consultas nuevas del dashboard.

Cobertura mínima pedida (2 casos por función: happy path + edge):
- get_stock_summary: agrupamiento por semáforo / base vacía / todos
  agotados / umbral personalizado.
- get_recent_activity: join con cliente + orden desc / base vacía /
  límite + truncado de payload.
"""
from datetime import datetime, timedelta

from queries import get_recent_activity, get_stock_summary
from src.models.client import Client
from src.models.interaction import Interaction
from src.models.product import Product


# ── Helpers ────────────────────────────────────────────────

def _producto(session, nombre, stock, categoria="General", activo=True):
    producto = Product(
        nombre=nombre,
        precio=10.0,
        stock=stock,
        categoria=categoria,
        activo=activo,
    )
    session.add(producto)
    session.commit()
    return producto


def _cliente(session, nombre, apellido):
    cliente = Client(
        nombre=nombre,
        apellido=apellido,
        email=f"{nombre}.{apellido}@mail.com".lower(),
    )
    session.add(cliente)
    session.commit()
    return cliente


def _interaccion(session, source="webhook", payload="hola", intent=None,
                 cliente=None, timestamp=None):
    interaccion = Interaction(
        source=source,
        payload=payload,
        intent=intent,
        clientId=cliente.id if cliente else None,
        timestamp=timestamp or datetime(2026, 10, 1, 8, 0, 0),
    )
    session.add(interaccion)
    session.commit()
    return interaccion


# ── get_stock_summary ──────────────────────────────────────

def test_stock_summary_agrupa_por_semaforo(db_session):
    _producto(db_session, "Café espresso", stock=0, categoria="Bebidas")
    _producto(db_session, "Fernet Branca", stock=2, categoria="Bebidas")
    _producto(db_session, "Yerba Mate", stock=5, categoria="Secos")
    _producto(db_session, "Azúcar", stock=50, categoria="Secos")
    # Inactivo con stock crítico: no debe aparecer en ninguna banda.
    _producto(db_session, "Vino viejo", stock=1, categoria="Bebidas",
              activo=False)

    resumen = get_stock_summary(db_session)

    assert resumen["threshold"] == 5
    assert [p["nombre"] for p in resumen["out_of_stock"]] == ["Café espresso"]
    # low_stock ordenado por stock ascendente (lo más urgente primero).
    assert [p["nombre"] for p in resumen["low_stock"]] == [
        "Fernet Branca", "Yerba Mate",
    ]
    assert [p["nombre"] for p in resumen["normal"]] == ["Azúcar"]
    assert resumen["counts"] == {
        "out_of_stock": 1,
        "low_stock": 2,
        "normal": 1,
        "alert": 3,
    }
    assert resumen["out_of_stock"][0]["categoria"] == "Bebidas"


def test_stock_summary_base_vacia(db_session):
    resumen = get_stock_summary(db_session)

    assert resumen["out_of_stock"] == []
    assert resumen["low_stock"] == []
    assert resumen["normal"] == []
    assert resumen["counts"] == {
        "out_of_stock": 0,
        "low_stock": 0,
        "normal": 0,
        "alert": 0,
    }


def test_stock_summary_todos_agotados(db_session):
    _producto(db_session, "Alfajor", stock=0)
    _producto(db_session, "Gaseosa", stock=0)
    _producto(db_session, "Snack", stock=0)

    resumen = get_stock_summary(db_session)

    assert len(resumen["out_of_stock"]) == 3
    assert resumen["low_stock"] == []
    assert resumen["normal"] == []
    assert resumen["counts"]["alert"] == 3


def test_stock_summary_acepta_umbral_personalizado(db_session):
    _producto(db_session, "Mate criollo", stock=3)
    _producto(db_session, "Termo", stock=10)

    resumen = get_stock_summary(db_session, threshold=3)

    assert resumen["threshold"] == 3
    assert [p["nombre"] for p in resumen["low_stock"]] == ["Mate criollo"]
    assert [p["nombre"] for p in resumen["normal"]] == ["Termo"]


# ── get_recent_activity ────────────────────────────────────

def test_recent_activity_une_cliente_y_ordena_desc(db_session):
    ana = _cliente(db_session, "Ana", "Pérez")
    luis = _cliente(db_session, "Luis", "Gómez")
    base = datetime(2026, 10, 1, 12, 0, 0)

    _interaccion(db_session, source="telegram", payload="quiero comprar",
                 intent="comprar", cliente=ana, timestamp=base)
    _interaccion(db_session, source="webhook", payload="evento n8n",
                 intent="consulta", cliente=luis,
                 timestamp=base + timedelta(hours=1))
    _interaccion(db_session, source="api", payload="sin cliente vinculado",
                 cliente=None, timestamp=base + timedelta(hours=2))

    actividad = get_recent_activity(db_session)

    assert [a["source"] for a in actividad] == ["api", "webhook", "telegram"]
    assert actividad[0]["client_name"] is None
    assert actividad[1]["client_name"] == "Luis Gómez"
    assert actividad[2]["client_name"] == "Ana Pérez"
    assert actividad[2]["payload"] == "quiero comprar"
    assert actividad[1]["intent"] == "consulta"
    assert actividad[0]["intent"] is None
    assert actividad[2]["timestamp"] == "2026-10-01T12:00:00"


def test_recent_activity_base_vacia(db_session):
    assert get_recent_activity(db_session) == []


def test_recent_activity_respeta_limit_y_trunca_payload(db_session):
    payload_largo = "x" * 500
    base = datetime(2026, 10, 1, 9, 0, 0)
    for i in range(3):
        _interaccion(db_session, payload=payload_largo,
                     timestamp=base + timedelta(minutes=i))

    actividad = get_recent_activity(db_session, limit=2)

    assert len(actividad) == 2
    # Más reciente primero.
    assert actividad[0]["timestamp"] == "2026-10-01T09:02:00"
    # Payload truncado: 140 chars + caracter de continuación.
    assert len(actividad[0]["payload"]) == 141
    assert actividad[0]["payload"].endswith("…")
