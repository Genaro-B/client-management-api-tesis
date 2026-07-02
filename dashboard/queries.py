"""Query functions for the Streamlit dashboard.

All functions receive an open SQLAlchemy session and return plain Python
objects (dicts, lists) — no ORM objects leak to the presentation layer.
The caller (app.py) is responsible for acquiring/releasing the session.
"""

from datetime import date, timedelta

from sqlalchemy import cast, Date, func
from sqlalchemy.orm import Session

# db.py already set up sys.path when imported — safe to import backend models
from src.models import Client, Interaction


# ═══════════════════════════════════════════════════════════
# Metrics
# ═══════════════════════════════════════════════════════════

def get_metrics_summary(session: Session) -> dict:
    """Return summary metrics for the dashboard cards.

    Returns:
        dict with keys: total_clients, active_clients, inactive_clients,
                        total_interactions, interactions_today,
                        interactions_this_week
    """
    total_clients = session.query(Client).count()
    active_clients = (
        session.query(Client).filter(Client.activo.is_(True)).count()
    )
    inactive_clients = total_clients - active_clients

    total_interactions = session.query(Interaction).count()

    today = date.today()
    week_ago = today - timedelta(days=7)

    interactions_today = (
        session.query(Interaction)
        .filter(cast(Interaction.timestamp, Date) == today)
        .count()
    )

    interactions_this_week = (
        session.query(Interaction)
        .filter(cast(Interaction.timestamp, Date) >= week_ago)
        .count()
    )

    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "inactive_clients": inactive_clients,
        "total_interactions": total_interactions,
        "interactions_today": interactions_today,
        "interactions_this_week": interactions_this_week,
    }


def get_interactions_timeline(session: Session) -> list[dict]:
    """Return daily interaction counts for the last 30 days.

    Returns:
        list of {"date": "YYYY-MM-DD", "count": int} — every day in the
        range is present; days without interactions have count=0.
    """
    thirty_days_ago = date.today() - timedelta(days=30)

    rows = (
        session.query(
            cast(Interaction.timestamp, Date).label("day"),
            func.count(Interaction.id).label("count"),
        )
        .filter(cast(Interaction.timestamp, Date) >= thirty_days_ago)
        .group_by(cast(Interaction.timestamp, Date))
        .order_by(cast(Interaction.timestamp, Date))
        .all()
    )

    counts_by_day: dict[date, int] = {row.day: row.count for row in rows}

    timeline = []
    for i in range(31):  # 0…30 inclusive = 31 days
        day = thirty_days_ago + timedelta(days=i)
        timeline.append({
            "date": day.isoformat(),
            "count": counts_by_day.get(day, 0),
        })

    return timeline


def get_interactions_by_source(session: Session) -> list[dict]:
    """Return interaction counts grouped by source.

    Returns:
        list of {"source": str, "count": int} ordered by count desc.
    """
    rows = (
        session.query(
            Interaction.source,
            func.count(Interaction.id).label("count"),
        )
        .group_by(Interaction.source)
        .order_by(func.count(Interaction.id).desc())
        .all()
    )
    return [{"source": row.source, "count": row.count} for row in rows]


def get_top_intents(session: Session, limit: int = 5) -> list[dict]:
    """Return the top N most frequent intents.

    Args:
        limit: how many intents to return (default 5).

    Returns:
        list of {"intent": str, "count": int} ordered by count desc.
    """
    rows = (
        session.query(
            Interaction.intent,
            func.count(Interaction.id).label("count"),
        )
        .filter(Interaction.intent.isnot(None))
        .group_by(Interaction.intent)
        .order_by(func.count(Interaction.id).desc())
        .limit(limit)
        .all()
    )
    return [{"intent": row.intent, "count": row.count} for row in rows]


# ═══════════════════════════════════════════════════════════
# CRUD — Clients
# ═══════════════════════════════════════════════════════════

def _client_to_dict(client: Client) -> dict:
    """Convert a Client ORM instance to a plain dict."""
    return {
        "id": client.id,
        "nombre": client.nombre,
        "apellido": client.apellido,
        "telefono": client.telefono,
        "email": client.email,
        "fecha_registro": (
            client.fecha_registro.isoformat()
            if client.fecha_registro
            else None
        ),
        "activo": client.activo,
        "role": client.role,
    }


def get_clients(session: Session) -> list[dict]:
    """Return all clients ordered by ID as plain dicts."""
    clients = session.query(Client).order_by(Client.id).all()
    return [_client_to_dict(c) for c in clients]


def create_client(session: Session, data: dict) -> dict | None:
    """Create a new client from a dict and return it as a plain dict.

    The dict keys should match Client column names (nombre, apellido,
    email, telefono, activo, etc.).
    """
    client = Client(**data)
    session.add(client)
    session.flush()  # persist so client.id is populated
    session.refresh(client)  # ensure all defaults are loaded
    return _client_to_dict(client)


def update_client(session: Session, client_id: int, data: dict) -> dict | None:
    """Update client fields and return the updated client as a plain dict.

    Only keys present in ``data`` and existing as model attributes are updated.
    Returns None if the client is not found.
    """
    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        return None
    for key, value in data.items():
        if hasattr(client, key):
            setattr(client, key, value)
    session.flush()
    session.refresh(client)
    return _client_to_dict(client)


def delete_client(session: Session, client_id: int) -> bool:
    """Delete a client by ID.

    Returns True if deleted, False if not found.
    """
    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        return False
    session.delete(client)
    session.flush()
    return True


# ═══════════════════════════════════════════════════════════
# Interactions
# ═══════════════════════════════════════════════════════════

def _interaction_to_dict(i: Interaction) -> dict:
    """Convert an Interaction ORM instance to a plain dict."""
    return {
        "id": i.id,
        "clientId": i.clientId,
        "user": i.user,
        "source": i.source,
        "payload": i.payload,
        "intent": i.intent,
        "result": i.result,
        "idempotency_key": i.idempotency_key,
        "timestamp": i.timestamp.isoformat() if i.timestamp else None,
    }


def get_client_interactions(
    session: Session, client_id: int,
) -> list[dict]:
    """Return all interactions for a given client, newest first, as plain dicts."""
    interactions = (
        session.query(Interaction)
        .filter(Interaction.clientId == client_id)
        .order_by(Interaction.timestamp.desc())
        .all()
    )
    return [_interaction_to_dict(i) for i in interactions]
