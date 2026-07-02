"""Router de métricas para el dashboard.

Expone GET /dashboard con datos agregados de clientes e interacciones.
Sin autenticación (como otros endpoints GET del sistema).
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.models.client import Client
from src.models.interaction import Interaction

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
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
