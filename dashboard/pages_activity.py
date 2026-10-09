"""Feed de actividad reciente: últimas interacciones como timeline."""
import html
from datetime import datetime

import streamlit as st

from components import safe_load
from db import get_session
from queries import get_recent_activity


@st.cache_data(ttl=60)
def load_recent_activity(limit: int = 20) -> list[dict]:
    with get_session() as session:
        return get_recent_activity(session, limit=limit)


def _format_ts(iso: str | None) -> str:
    """ISO → 'YYYY-MM-DD HH:MM' para mostrar en el feed."""
    if not iso:
        return "—"
    try:
        return datetime.fromisoformat(iso).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso


def render_activity_page() -> None:
    """Timeline de las últimas interacciones: fuente, intent, cliente y payload."""
    st.title("🕒 Actividad Reciente")

    items = safe_load(load_recent_activity, spinner="Cargando actividad…")
    if items is None:
        return
    if not items:
        st.info("Sin datos aún: no hay interacciones registradas.")
        return

    st.caption(f"Últimas {len(items)} interacciones registradas en la base.")

    for item in items:
        source = item["source"] or "—"
        badge_class = "source-badge--bot" if source == "admin-bot" else ""
        intent = item["intent"] or "sin intención"
        cliente = item["client_name"] or "Sin cliente vinculado"
        payload = item["payload"] or "—"

        st.markdown(
            f'<div class="activity-item">'
            f'<div class="activity-meta">'
            f'<span class="source-badge {badge_class}">'
            f"{html.escape(source)}</span>"
            f'<span class="activity-time">{_format_ts(item["timestamp"])}</span>'
            f"</div>"
            f'<div class="activity-main"><strong>{html.escape(intent)}</strong>'
            f' · <span class="activity-client">'
            f"{html.escape(cliente)}</span></div>"
            f'<div class="activity-payload">{html.escape(payload)}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
