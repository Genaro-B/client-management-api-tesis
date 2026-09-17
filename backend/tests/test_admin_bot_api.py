"""Tests de integración del asistente administrativo (POST /api/v1/admin-bot/consult).

Verifica:
- Consulta real por cada intención con datos sembrados (nuevos del mes,
  stock bajo, interacciones hoy, top producto, métricas generales).
- Fallback no-entendido con sugerencias.
- Validación 422 de mensaje vacío/ausente.
- Registro de cada consulta como interacción con source="admin-bot" e intent.
"""
import json
from datetime import datetime, timedelta, timezone

from src.models.client import Client
from src.models.interaction import Interaction
from src.models.product import Product
from src.core.config import LOW_STOCK_THRESHOLD

PREFIX = "/api/v1/admin-bot"


def _now_utc():
    return datetime.now(timezone.utc)


def _hoy_start():
    return _now_utc().replace(hour=0, minute=0, second=0, microsecond=0)


def _mes_start():
    return _now_utc().replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _crear_cliente(db_session, email, **kwargs):
    cliente = Client(
        nombre=kwargs.pop("nombre", "Cliente"),
        apellido=kwargs.pop("apellido", "Test"),
        email=email,
        **kwargs,
    )
    db_session.add(cliente)
    db_session.flush()
    return cliente


def _crear_producto(db_session, nombre, stock, **kwargs):
    producto = Product(nombre=nombre, descripcion="d", precio=100.0, stock=stock, **kwargs)
    db_session.add(producto)
    db_session.flush()
    return producto


# ---------------------------------------------------------------------------
# Consulta por intención con datos reales
# ---------------------------------------------------------------------------


def test_consulta_clientes_nuevos_mes_responde_datos_reales(client, db_session):
    """3 clientes registrados este mes -> respuesta menciona el 3."""
    mes = _mes_start()
    for i in range(3):
        _crear_cliente(
            db_session,
            f"nuevo{i}@x.com",
            nombre=f"Nuevo{i}",
            apellido="Mes",
            fecha_registro=mes + timedelta(days=2, hours=i + 1),
        )
    # Cliente del mes pasado NO debe contar
    _crear_cliente(
        db_session,
        "viejo@x.com",
        nombre="Viejo",
        apellido="Mes",
        fecha_registro=mes - timedelta(days=10),
    )
    # Admin del mes actual NO debe contar
    _crear_cliente(
        db_session,
        "admin@x.com",
        nombre="Admin",
        apellido="X",
        role="admin",
        fecha_registro=mes + timedelta(days=1),
    )
    db_session.commit()

    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "¿cuántos clientes nuevos hay este mes?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "clientes-nuevos-mes"
    assert "3" in data["respuesta"]
    assert "Nuevo0" in data["respuesta"]  # menciona los detalles


def test_consulta_clientes_nuevos_mes_sin_datos(client, db_session):
    """Sin clientes nuevos, la respuesta lo dice sin romperse."""
    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "clientes nuevos del mes"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "clientes-nuevos-mes"
    assert "no" in data["respuesta"].lower() or "0" in data["respuesta"]


def test_consulta_stock_bajo_lista_productos(client, db_session):
    """Productos con stock <= umbral se listan; los demás no."""
    _crear_producto(db_session, "Umbral", stock=LOW_STOCK_THRESHOLD)
    _crear_producto(db_session, "Critico", stock=3)
    _crear_producto(db_session, "Sano", stock=50)
    db_session.commit()

    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "qué productos tienen stock bajo"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "stock-bajo"
    assert "Umbral" in data["respuesta"]
    assert "Critico" in data["respuesta"]
    assert "Sano" not in data["respuesta"]


def test_consulta_stock_bajo_sin_productos(client, db_session):
    """Sin productos bajo el umbral, la respuesta es tranquilizadora."""
    _crear_producto(db_session, "Sano", stock=100)
    db_session.commit()

    resp = client.post(f"{PREFIX}/consult", json={"mensaje": "stock bajo"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "stock-bajo"
    assert "no" in data["respuesta"].lower()


def test_consulta_interacciones_hoy_responde_conteo_real(client, db_session):
    """7 interacciones hoy -> respuesta menciona 7; las de ayer no cuentan."""
    hoy = _hoy_start()
    for i in range(7):
        db_session.add(Interaction(
            source="telegram",
            payload=json.dumps({"n": i}),
            timestamp=hoy + timedelta(hours=i + 1),
        ))
    for i in range(3):
        db_session.add(Interaction(
            source="api",
            payload=json.dumps({"n": i}),
            timestamp=hoy - timedelta(days=1, hours=-i),
        ))
    db_session.commit()

    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "cuántas interacciones hubo hoy"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "interacciones-hoy"
    assert "7" in data["respuesta"]


def test_consulta_producto_mas_vendido_responde_top(client, db_session):
    """Agrega cantidades del JSON productos_asignados y devuelve el top 5."""
    p1 = _crear_producto(db_session, "Producto Uno", stock=100)
    p2 = _crear_producto(db_session, "Producto Dos", stock=100)
    p3 = _crear_producto(db_session, "Producto Tres", stock=100)
    db_session.commit()

    _crear_cliente(
        db_session, "topa@x.com", nombre="Top", apellido="A",
        productos_asignados=[
            {"producto_id": p1.id, "nombre": p1.nombre, "precio": 100.0, "cantidad": 5},
            {"producto_id": p2.id, "nombre": p2.nombre, "precio": 100.0, "cantidad": 3},
        ],
    )
    _crear_cliente(
        db_session, "topb@x.com", nombre="Top", apellido="B",
        productos_asignados=[
            {"producto_id": p1.id, "nombre": p1.nombre, "precio": 100.0, "cantidad": 2},
            {"producto_id": p3.id, "nombre": p3.nombre, "precio": 100.0, "cantidad": 1},
        ],
    )
    db_session.commit()

    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "cuál es el producto más vendido"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "producto-top"
    # Producto Uno suma 5+2=7 -> debe ser el top y aparecer primero
    assert "Producto Uno" in data["respuesta"]
    assert "Producto Dos" in data["respuesta"]
    assert data["respuesta"].index("Producto Uno") < data["respuesta"].index("Producto Dos")


def test_consulta_producto_mas_vendido_sin_asignaciones(client, db_session):
    """Sin productos asignados, la respuesta es informativa."""
    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "producto más vendido"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "producto-top"
    assert "no" in data["respuesta"].lower()


def test_consulta_metricas_responde_resumen(client, db_session):
    """Mismos cálculos de summary que /metrics/dashboard."""
    hoy = _hoy_start()
    for i in range(3):
        _crear_cliente(
            db_session, f"met{i}@x.com", nombre=f"M{i}", apellido="T",
            activo=(i != 1),
        )
    _crear_cliente(
        db_session, "metadmin@x.com", nombre="Admin", apellido="X", role="admin",
    )
    for i in range(2):
        db_session.add(Interaction(
            source="telegram", payload=json.dumps({"n": i}),
            timestamp=hoy + timedelta(hours=i),
        ))
    db_session.commit()

    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "cómo vamos con el negocio"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "metricas-generales"
    texto = data["respuesta"]
    # total clients = 3 (no-admin), activos = 2, inactivos = 1, interacciones totales = 2
    assert "3" in texto
    assert "2" in texto
    assert "1" in texto


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------


def test_texto_no_entendido_sugiere_consultas_validas(client):
    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "qué clima hace en marte"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "no-entendido"
    assert "clientes nuevos" in data["respuesta"].lower()
    assert "stock bajo" in data["respuesta"].lower()


# ---------------------------------------------------------------------------
# Validación 422
# ---------------------------------------------------------------------------


def test_mensaje_vacio_devuelve_422(client):
    resp = client.post(f"{PREFIX}/consult", json={"mensaje": ""})
    assert resp.status_code == 422


def test_mensaje_solo_espacios_devuelve_422(client):
    resp = client.post(f"{PREFIX}/consult", json={"mensaje": "   "})
    assert resp.status_code == 422


def test_mensaje_ausente_devuelve_422(client):
    resp = client.post(f"{PREFIX}/consult", json={})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Registro de la consulta como interacción
# ---------------------------------------------------------------------------


def test_consulta_se_registra_como_interaccion(client, db_session):
    resp = client.post(f"{PREFIX}/consult", json={
        "mensaje": "productos con stock bajo"
    })
    assert resp.status_code == 200

    items = client.get("/api/v1/interactions/").json()["items"]
    assert len(items) == 1
    registro = items[0]
    assert registro["source"] == "admin-bot"
    assert registro["intent"] == "stock-bajo"
    assert "stock bajo" in registro["payload"]


def test_consulta_no_entendida_tambien_se_registra(client, db_session):
    client.post(f"{PREFIX}/consult", json={"mensaje": "hola mundo"})
    items = client.get("/api/v1/interactions/").json()["items"]
    assert len(items) == 1
    assert items[0]["source"] == "admin-bot"
    assert items[0]["intent"] == "no-entendido"