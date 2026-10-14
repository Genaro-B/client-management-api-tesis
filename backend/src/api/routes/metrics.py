"""Router de métricas para el dashboard.

Expone GET /dashboard con datos agregados de clientes e interacciones.
Sin autenticación (como otros endpoints GET del sistema).
"""
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.core.deps import get_current_user
from src.models.client import Client
from src.models.interaction import Interaction
from src.models.product import Product
from src.models.sale import Sale, SaleItem
from src.repositories.sale_repo import BASE_CONTABLE

router = APIRouter()


def _parse_fecha(valor: Optional[str], default: date) -> date:
    if not valor:
        return default
    return date.fromisoformat(valor)


def _sum_ventas(db: Session, desde: datetime, hasta: datetime):
    """Devuelve (cantidad, ingresos) de la base contable en [desde, hasta)."""
    row = (
        db.query(func.count(Sale.id), func.coalesce(func.sum(Sale.total), 0.0))
        .filter(Sale.estado.in_(BASE_CONTABLE), Sale.fecha >= desde, Sale.fecha < hasta)
        .one()
    )
    return int(row[0] or 0), float(row[1] or 0.0)


def _variacion(actual, anterior) -> float:
    """Variación porcentual del actual respecto del anterior (0 si no hay base)."""
    if anterior == 0:
        return 100.0 if actual > 0 else 0.0
    return round((actual - anterior) / anterior * 100, 2)


@router.get("/ventas")
def get_ventas_metrics(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user: Client = Depends(get_current_user),
):
    """Métricas de ventas (base contable). Default: últimos 30 días."""
    hoy = datetime.now(timezone.utc).date()
    f_hasta = _parse_fecha(hasta, hoy)
    f_desde = _parse_fecha(desde, f_hasta - timedelta(days=29))

    desde_dt = datetime.combine(f_desde, time.min)
    hasta_dt = datetime.combine(f_hasta, time.max)

    ventas_n, ingresos = _sum_ventas(db, desde_dt, hasta_dt)
    ticket_promedio = ingresos / ventas_n if ventas_n else 0

    # Período anterior de igual duración (inmediatamente anterior).
    dias = (f_hasta - f_desde).days + 1
    prev_hasta_dt = desde_dt
    prev_desde_dt = desde_dt - timedelta(days=dias)
    prev_n, prev_ingresos = _sum_ventas(db, prev_desde_dt, prev_hasta_dt)

    # Serie diaria con 0-fill.
    serie_rows = (
        db.query(
            func.date(Sale.fecha).label("fecha"),
            func.count(Sale.id).label("ventas"),
            func.coalesce(func.sum(Sale.total), 0.0).label("ingresos"),
        )
        .filter(Sale.estado.in_(BASE_CONTABLE), Sale.fecha >= desde_dt, Sale.fecha < hasta_dt)
        .group_by(func.date(Sale.fecha))
        .all()
    )
    serie_map = {r.fecha: (r.ventas, float(r.ingresos)) for r in serie_rows}
    serie_diaria = []
    for i in range(dias):
        dia = f_desde + timedelta(days=i)
        key = dia.strftime("%Y-%m-%d")
        v, ing = serie_map.get(key, (0, 0.0))
        serie_diaria.append({"fecha": key, "ventas": v, "ingresos": ing})

    # Top 5 productos de la base contable por cantidad vendida.
    top_rows = (
        db.query(
            Product.nombre.label("producto"),
            func.sum(SaleItem.cantidad).label("cantidad"),
            func.sum(SaleItem.cantidad * SaleItem.precio_unitario).label("ingresos"),
        )
        .join(Sale, Sale.id == SaleItem.sale_id)
        .join(Product, Product.id == SaleItem.product_id)
        .filter(Sale.estado.in_(BASE_CONTABLE), Sale.fecha >= desde_dt, Sale.fecha < hasta_dt)
        .group_by(Product.id, Product.nombre)
        .order_by(func.sum(SaleItem.cantidad).desc())
        .limit(5)
        .all()
    )
    top_productos = [
        {"producto": r.producto, "cantidad": int(r.cantidad), "ingresos": float(r.ingresos or 0)}
        for r in top_rows
    ]

    # Conteo por hora (0..23, con 0-fill).
    hora_rows = (
        db.query(
            func.strftime("%H", Sale.fecha).label("hora"),
            func.count(Sale.id).label("ventas"),
        )
        .filter(Sale.estado.in_(BASE_CONTABLE), Sale.fecha >= desde_dt, Sale.fecha < hasta_dt)
        .group_by(func.strftime("%H", Sale.fecha))
        .all()
    )
    hora_map = {int(r.hora): r.ventas for r in hora_rows if r.hora is not None}
    por_horario = [{"hora": h, "ventas": hora_map.get(h, 0)} for h in range(24)]

    return {
        "summary": {
            "ventas": ventas_n,
            "ingresos": ingresos,
            "ticketPromedio": ticket_promedio,
            "vsPeriodoAnterior": {
                "ventas": _variacion(ventas_n, prev_n),
                "ingresos": _variacion(ingresos, prev_ingresos),
            },
        },
        "serieDiaria": serie_diaria,
        "topProductos": top_productos,
        "porHorario": por_horario,
    }


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), _user: Client = Depends(get_current_user)):
    """Retorna métricas agregadas para el dashboard principal.

    Devuelve: summary, interactionsBySource, interactionsTimeline,
    registrationsByMonth y topIntents en un solo response.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today_start - timedelta(days=7)
    thirty_days_ago = today_start - timedelta(days=30)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    total_clients = (
        db.query(func.count(Client.id))
        .filter(Client.role != "admin")
        .scalar() or 0
    )
    active_clients = (
        db.query(func.count(Client.id))
        .filter(Client.role != "admin", Client.activo.is_(True))
        .scalar() or 0
    )
    inactive_clients = total_clients - active_clients

    total_interactions = (
        db.query(func.count(Interaction.id)).scalar() or 0
    )
    interactions_today = (
        db.query(func.count(Interaction.id))
        .filter(Interaction.timestamp >= today_start)
        .scalar() or 0
    )
    interactions_this_week = (
        db.query(func.count(Interaction.id))
        .filter(Interaction.timestamp >= week_ago)
        .scalar() or 0
    )

    summary = {
        "totalClients": total_clients,
        "activeClients": active_clients,
        "inactiveClients": inactive_clients,
        "totalInteractions": total_interactions,
        "interactionsToday": interactions_today,
        "interactionsThisWeek": interactions_this_week,
    }

    # ------------------------------------------------------------------
    # Interactions by source (GROUP BY source)
    # ------------------------------------------------------------------
    source_rows = (
        db.query(
            Interaction.source,
            func.count(Interaction.id).label("count"),
        )
        .group_by(Interaction.source)
        .all()
    )
    interactions_by_source = {row.source: row.count for row in source_rows}

    # ------------------------------------------------------------------
    # Interactions timeline (last 30 days, fill missing with 0)
    # ------------------------------------------------------------------
    timeline_rows = (
        db.query(
            func.date(Interaction.timestamp).label("date"),
            func.count(Interaction.id).label("count"),
        )
        .filter(Interaction.timestamp >= thirty_days_ago)
        .group_by(func.date(Interaction.timestamp))
        .all()
    )
    timeline_map = {row.date: row.count for row in timeline_rows}

    interactions_timeline = []
    for i in range(29, -1, -1):
        day = today_start - timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        interactions_timeline.append({
            "date": date_str,
            "count": timeline_map.get(date_str, 0),
        })

    # ------------------------------------------------------------------
    # Registrations by month (GROUP BY YYYY-MM)
    # ------------------------------------------------------------------
    reg_rows = (
        db.query(
            func.strftime("%Y-%m", Client.fecha_registro).label("month"),
            func.count(Client.id).label("count"),
        )
        .group_by(func.strftime("%Y-%m", Client.fecha_registro))
        .order_by(func.strftime("%Y-%m", Client.fecha_registro))
        .all()
    )
    registrations_by_month = [
        {"month": r.month, "count": r.count} for r in reg_rows
    ]

    # ------------------------------------------------------------------
    # Top 5 intents (non-null intent, grouped, ordered desc)
    # ------------------------------------------------------------------
    intent_rows = (
        db.query(
            Interaction.intent,
            func.count(Interaction.id).label("count"),
        )
        .filter(Interaction.intent.isnot(None))
        .group_by(Interaction.intent)
        .order_by(func.count(Interaction.id).desc())
        .limit(5)
        .all()
    )
    top_intents = [
        {"intent": r.intent, "count": r.count} for r in intent_rows
    ]

    return {
        "summary": summary,
        "interactionsBySource": interactions_by_source,
        "interactionsTimeline": interactions_timeline,
        "registrationsByMonth": registrations_by_month,
        "topIntents": top_intents,
    }
