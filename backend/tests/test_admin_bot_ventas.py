"""Tests del asistente administrativo: intenciones de ventas."""
from datetime import datetime, timezone

from src.models.client import Client
from src.models.product import Product
from src.models.sale import Sale, SaleItem
from src.repositories.client_repo import ClientRepository
from src.repositories.sale_repo import SaleRepository
from src.services.admin_bot.admin_intent_router import AdminIntentRouter
from src.services.admin_bot.admin_bot_service import AdminBotService


# ---------------------------------------------------------------------------
# Router: detección de intenciones
# ---------------------------------------------------------------------------


def test_router_detecta_ventas_hoy():
    router = AdminIntentRouter()
    assert router.match("¿cuántas ventas hubo hoy?") == "ventas-hoy"
    assert router.match("ventas del día") == "ventas-hoy"


def test_router_detecta_ticket_cliente():
    router = AdminIntentRouter()
    assert router.match("qué compró María ayer") == "ticket-cliente"
    assert router.match("ticket de María del 01-10-2026") == "ticket-cliente"


def test_router_ventas_no_pisa_interacciones_hoy():
    """'ventas hoy' no debe caer en interacciones-hoy (que matchea 'hubo hoy')."""
    router = AdminIntentRouter()
    assert router.match("cuántas ventas hubo hoy") == "ventas-hoy"


# ---------------------------------------------------------------------------
# Service: handlers
# ---------------------------------------------------------------------------


def _cliente(db, nombre="Maria", apellido="Lopez", tg="12345"):
    return ClientRepository(db).create(Client(
        nombre=nombre, apellido=apellido, email=f"{nombre.lower()}@x.com",
        telegram_user_id=tg,
    ))


def _producto(db, nombre="Widget", precio=10.0):
    p = Product(nombre=nombre, descripcion="d", precio=precio, stock=100, activo=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_ventas_hoy_solo_base_contable(db_session):
    c = _cliente(db_session)
    repo = SaleRepository(db_session)
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    repo.create(Sale(cliente_id=c.id, estado="CONFIRMADO", total=100, fecha=ahora))
    repo.create(Sale(cliente_id=c.id, estado="PENDIENTE", total=999, fecha=ahora))

    service = AdminBotService(db_session)
    respuesta = service.respond("ventas-hoy", texto="cuántas ventas hubo hoy")
    assert "1" in respuesta


def test_ventas_hoy_sin_ventas(db_session):
    service = AdminBotService(db_session)
    respuesta = service.respond("ventas-hoy", texto="ventas del día")
    assert "no hubo ventas" in respuesta.lower()


def test_ticket_cliente_lista_productos(db_session):
    c = _cliente(db_session)
    p = _producto(db_session, nombre="Widget", precio=10.0)
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    venta = Sale(cliente_id=c.id, estado="CONFIRMADO", total=30, fecha=ahora)
    venta.items.append(SaleItem(product_id=p.id, cantidad=3, precio_unitario=10.0))
    SaleRepository(db_session).create(venta)

    service = AdminBotService(db_session)
    respuesta = service.respond("ticket-cliente", texto="qué compró Maria hoy")
    assert "Widget" in respuesta
    assert "30" in respuesta


def test_ticket_cliente_sin_datos(db_session):
    service = AdminBotService(db_session)
    respuesta = service.respond("ticket-cliente", texto="qué compró Nadie ayer")
    assert "no se encontraron ventas" in respuesta.lower()
