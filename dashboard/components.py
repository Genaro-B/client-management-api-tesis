"""Componentes compartidos del dashboard.

Contiene los design tokens de color (réplica de :root en app.py para
Plotly, que no puede leer variables CSS), la tarjeta de métrica unificada,
la carga segura de datos (spinner + error amigable), el banner de alertas
de stock y la caja del asistente administrativo.
"""
import html

import streamlit as st

# db.py setea sys.path hacia backend/ → los imports de src.* de abajo andan.
from db import get_session

# ── Páginas: fuente única de verdad para navegación y routing ──
PAGE_METRICS = "📊 Métricas"
PAGE_CLIENTS = "👥 Clientes"
PAGE_STOCK = "📦 Stock"
PAGE_ACTIVITY = "🕒 Actividad"

# ── Design tokens ──
# Réplica del bloque :root de app.py. Plotly no puede leer variables CSS,
# así que la paleta vive también en Python: mantener sincronizados.
PALETTE = {
    "ink": "#0f172a",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "primary_dark": "#1e40af",
    "primary_light": "#3b82f6",
    "surface": "#f8fafc",
    "card": "#ffffff",
    "border": "#e2e8f0",
    "text": "#1e293b",
    "muted": "#64748b",
    "white": "#ffffff",
    "sidebar_text": "#e2e8f0",
    "sidebar_heading": "#f1f5f9",
    "sidebar_nav_text": "#cbd5e1",
    "sidebar_nav_hover_bg": "rgba(255, 255, 255, 0.07)",
    "critical": "#dc2626",
    "critical_soft": "#fee2e2",
    "warning": "#f59e0b",
    "warning_soft": "#fef3c7",
    "warning_strong": "#b45309",
    "success": "#16a34a",
    "success_soft": "#dcfce7",
    "success_strong": "#15803d",
}

# ── Admin bot (asistente) ──
# Import tolerante: si el backend no expone el servicio, el dashboard
# degrada con un st.info en vez de romper el arranque.
try:
    from src.services.admin_bot.admin_bot_service import AdminBotService
    from src.services.admin_bot.admin_intent_router import AdminIntentRouter
    from src.services.interaction_service import InteractionService
    _ADMIN_BOT_ERROR: str | None = None
except Exception as exc:  # pragma: no cover
    AdminBotService = None
    AdminIntentRouter = None
    InteractionService = None
    _ADMIN_BOT_ERROR = str(exc)


# ═══════════════════════════════════════════════════════════
# Tarjeta de métrica unificada
# ═══════════════════════════════════════════════════════════

def metric_card(label: str, value) -> None:
    """Renderiza la tarjeta HTML de métrica (Métricas + detalle de cliente)."""
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-value">{html.escape(str(value))}</div>'
        f'<div class="metric-label">{html.escape(str(label))}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════
# Carga segura de datos
# ═══════════════════════════════════════════════════════════

def safe_load(loader, *args,
              message: str = "No se pudieron cargar los datos",
              spinner: str = "Cargando datos…",
              **kwargs):
    """Ejecuta una consulta con spinner y devuelve su valor.

    Ante cualquier excepción muestra un st.error amigable (sin traceback)
    y devuelve None; el caller decide cómo continuar.
    """
    try:
        with st.spinner(spinner):
            return loader(*args, **kwargs)
    except Exception as exc:
        st.error(f"{message}: {exc}")
        return None


# ═══════════════════════════════════════════════════════════
# Banner de alerta de stock (home)
# ═══════════════════════════════════════════════════════════

def render_stock_alert_banner(summary: dict) -> None:
    """Banner slim en el home: stock crítico/agotado, con atajo al panel.

    Recibe el mismo resumen que consume el panel de stock (una sola
    query, sin lógica duplicada). No renderiza nada si no hay alertas.
    """
    counts = summary["counts"]
    alerta = counts["alert"]
    if alerta == 0:
        return

    agotados = counts["out_of_stock"]
    css_class = "alert-banner--critical" if agotados else "alert-banner--warning"
    texto = (
        f"⚠ {alerta} producto{'s' if alerta != 1 else ''} con stock crítico"
        f" ({agotados} agotado{'s' if agotados != 1 else ''})"
    )

    col_texto, col_accion = st.columns([5, 1])
    with col_texto:
        st.markdown(
            f'<div class="alert-banner {css_class}">{texto}</div>',
            unsafe_allow_html=True,
        )
    with col_accion:
        if st.button("Ver stock →", key="banner_ver_stock", width="stretch"):
            st.session_state.page = PAGE_STOCK
            st.rerun()


# ═══════════════════════════════════════════════════════════
# Caja del asistente administrativo (sidebar)
# ═══════════════════════════════════════════════════════════

def render_assistant_box(container) -> None:
    """Input de consulta libre → AdminIntentRouter + AdminBotService.

    Llama al servicio del backend directo (sin HTTP ni login), con la
    misma paridad que POST /admin-bot/consult: detecta intención, responde
    con datos reales y registra la consulta como interacción admin-bot.
    """
    container.markdown("### 🤖 Asistente")

    if _ADMIN_BOT_ERROR:
        container.info(f"Asistente no disponible: {_ADMIN_BOT_ERROR}")
        return

    pregunta = container.text_input(
        "Preguntale al asistente",
        placeholder="¿Cuántos clientes nuevos hay este mes?",
        key="assistant_question",
    )

    if not container.button("Consultar", key="assistant_ask",
                            width="stretch"):
        return

    mensaje = (pregunta or "").strip()
    if not mensaje:
        container.caption("Escribí una consulta antes de consultar.")
        return

    try:
        intent = AdminIntentRouter().match(mensaje)
        with st.spinner("Consultando al asistente…"):
            with get_session() as session:
                respuesta = AdminBotService(session).respond(intent)
                # Registro best-effort (paridad con la API): si falla,
                # la respuesta igual se muestra.
                try:
                    InteractionService(session).create(
                        source="admin-bot",
                        payload=mensaje,
                        intent=intent,
                        result=respuesta[:200],
                    )
                except Exception:
                    pass
    except Exception as exc:
        container.error(f"Asistente no disponible: {exc}")
        return

    container.markdown(f"**Intención:** `{intent}`")
    # Los saltos de línea del servicio se preservan en Markdown
    # con dos espacios finales de por medio.
    container.markdown(respuesta.replace("\n", "  \n"))
