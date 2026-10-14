"""Router de ventas.

Autenticación por flujo:
- Escritura desde el bot (`POST /`) → `X-Api-Key` (+ `X-Idempotency-Key`).
- Lecturas y transiciones del panel → JWT; confirmar/completar/cancelar
  exigen `role="admin"` (`require_admin`).

Orden de rutas: `GET /ticket` se declara ANTES de `GET /{sale_id}` para que
FastAPI no interprete "ticket" como un id.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy.orm import Session

from src.core.auth import verify_api_key
from src.core.deps import get_current_user, require_admin
from src.database.session import get_db
from src.models.client import Client
from src.models.product import Product
from src.models.sale import Sale
from src.schemas.sale import (
    CreateSale,
    SaleResponse,
    SaleListResponse,
    TicketResponse,
)
from src.services.sale_service import (
    SaleService,
    ValidationError,
    ClientNotFoundError,
    SaleNotFoundError,
    TransitionError,
)

router = APIRouter()


def _serialize(db: Session, sale: Sale) -> dict:
    """Serializa una venta con nombre de cliente y de producto."""
    product_ids = {i.product_id for i in sale.items}
    nombres = {}
    if product_ids:
        for p in db.query(Product).filter(Product.id.in_(product_ids)).all():
            nombres[p.id] = p.nombre
    cliente = db.query(Client).filter(Client.id == sale.cliente_id).first()
    return {
        "id": sale.id,
        "cliente_id": sale.cliente_id,
        "cliente_nombre": cliente.nombre if cliente else None,
        "fecha": sale.fecha,
        "total": sale.total,
        "estado": sale.estado,
        "idempotency_key": sale.idempotency_key,
        "confirmado_por": sale.confirmado_por,
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "producto_nombre": nombres.get(i.product_id),
                "cantidad": i.cantidad,
                "precio_unitario": i.precio_unitario,
            }
            for i in sale.items
        ],
    }


@router.post("/", response_model=SaleResponse, status_code=201)
def create_sale(
    payload: CreateSale,
    response: Response,
    db: Session = Depends(get_db),
    _auth_ok: str = Depends(verify_api_key),
    x_idempotency_key: Optional[str] = Header(None),
):
    """Alta de venta desde el bot. 201 en alta, 200 si es reintento idempotente."""
    service = SaleService(db)
    try:
        sale, created = service.create_from_bot(
            items=[i.model_dump() for i in payload.items],
            telegram_user_id=payload.telegram_user_id,
            cliente_id=payload.cliente_id,
            idempotency_key=x_idempotency_key,
        )
    except ClientNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    response.status_code = 201 if created else 200
    return _serialize(db, sale)


@router.get("/", response_model=SaleListResponse)
def list_sales(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    estado: Optional[str] = Query(None),
    cliente_id: Optional[int] = Query(None, ge=1),
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _user: Client = Depends(get_current_user),
):
    """Listado paginado de ventas (todas, no solo base contable) con filtros."""
    service = SaleService(db)
    items, total = service.list(
        limit=limit,
        offset=offset,
        estado=estado,
        cliente_id=cliente_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return {"items": [_serialize(db, s) for s in items], "total": total}


@router.get("/ticket", response_model=TicketResponse)
def get_ticket(
    cliente: str = Query(..., min_length=1),
    fecha: str = Query(...),
    db: Session = Depends(get_db),
    _user: Client = Depends(get_current_user),
):
    """Ticket del día: ventas contables del cliente (match ILIKE) en `fecha`.

    Devuelve `200` con lista vacía si el cliente no existe o no hay ventas.
    """
    service = SaleService(db)
    found, ventas = service.ticket(cliente, fecha)
    return {
        "cliente": found.nombre if found else None,
        "ventas": [_serialize(db, s) for s in ventas],
    }


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    _user: Client = Depends(get_current_user),
):
    """Detalle de una venta con items y nombre de cliente."""
    service = SaleService(db)
    sale = service.get(sale_id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return _serialize(db, sale)


def _apply_transition(db, sale_id, target, confirmado_por=None):
    service = SaleService(db)
    try:
        sale = service.transition(sale_id, target, confirmado_por=confirmado_por)
    except SaleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransitionError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return _serialize(db, sale)


@router.post("/{sale_id}/confirm", response_model=SaleResponse)
def confirm_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    admin: Client = Depends(require_admin),
):
    """PENDIENTE → CONFIRMADO. Registra quién confirmó. Solo admin."""
    return _apply_transition(db, sale_id, "CONFIRMADO", confirmado_por=admin.id)


@router.post("/{sale_id}/complete", response_model=SaleResponse)
def complete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    _admin: Client = Depends(require_admin),
):
    """CONFIRMADO → COMPLETADO. Solo admin."""
    return _apply_transition(db, sale_id, "COMPLETADO")


@router.post("/{sale_id}/cancel", response_model=SaleResponse)
def cancel_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    _admin: Client = Depends(require_admin),
):
    """PENDIENTE/CONFIRMADO → CANCELADO. Solo admin."""
    return _apply_transition(db, sale_id, "CANCELADO")
