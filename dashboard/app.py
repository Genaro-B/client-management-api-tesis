"""Streamlit dashboard for CRM — metrics, clients, stock & activity feed.

Usage (en Windows usar `python -m streamlit`, `streamlit` no está en el PATH):
    cd dashboard/
    pip install -r requirements.txt
    python -m streamlit run app.py

Connects directly to the same database as the FastAPI backend via SQLAlchemy.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ── db.py sets up sys.path + creates the engine ──
from db import get_session

# Backend models — available because db.py already set up sys.path
from src.models import Client

from components import (
    PAGE_ACTIVITY,
    PAGE_CLIENTS,
    PAGE_METRICS,
    PAGE_STOCK,
    PALETTE,
    metric_card,
    render_assistant_box,
    render_stock_alert_banner,
    safe_load,
)
from pages_activity import render_activity_page
from pages_stock import load_stock_summary, render_stock_page
from queries import (
    create_client,
    delete_client,
    get_client_interactions,
    get_clients,
    get_interactions_by_source,
    get_interactions_timeline,
    get_metrics_summary,
    get_top_intents,
    update_client,
)

# ═══════════════════════════════════════════════════════════
# Page configuration
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title="CRM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
# Custom CSS
# ═══════════════════════════════════════════════════════════

st.markdown(
    """
<style>
    /* ── Design tokens: única fuente de verdad de los colores.
       PALETTE en components.py replica estos valores para Plotly
       (que no puede leer variables CSS). Mantener sincronizados. ── */
    :root {
        --color-ink: #0f172a;
        --color-primary: #2563eb;
        --color-primary-hover: #1d4ed8;
        --color-primary-dark: #1e40af;
        --color-primary-light: #3b82f6;
        --color-surface: #f8fafc;
        --color-card: #ffffff;
        --color-border: #e2e8f0;
        --color-text: #1e293b;
        --color-muted: #64748b;
        --color-white: #ffffff;
        --color-sidebar-text: #e2e8f0;
        --color-sidebar-heading: #f1f5f9;
        --color-sidebar-nav-text: #cbd5e1;
        --color-sidebar-nav-hover-bg: rgba(255, 255, 255, 0.07);
        --color-critical: #dc2626;
        --color-critical-soft: #fee2e2;
        --color-warning: #f59e0b;
        --color-warning-soft: #fef3c7;
        --color-warning-strong: #b45309;
        --color-success: #16a34a;
        --color-success-soft: #dcfce7;
        --color-success-strong: #15803d;
    }
    /* Dark sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--color-ink);
        min-width: 260px;
    }
    [data-testid="stSidebar"] .sidebar-content {
        color: var(--color-sidebar-text);
    }
    /* ⚠ Selector interno de Streamlit (clase emotion-cache generada):
       es FRÁGIL porque cambia entre versiones. Se conserva a propósito —
       no reescribir sin verificar la versión de Streamlit objetivo. */
    [data-testid="stSidebar"] .st-emotion-cache-1v7mm3u {
        color: var(--color-sidebar-text);
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--color-sidebar-heading);
    }
    /* Etiquetas de widgets sobre fondo oscuro (input del asistente) */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: var(--color-sidebar-text);
    }
    /* Sidebar nav buttons */
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        border: none !important;
        color: var(--color-sidebar-nav-text) !important;
        justify-content: flex-start !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 1rem !important;
        margin: 0.15rem 0 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: var(--color-sidebar-nav-hover-bg) !important;
        color: var(--color-white) !important;
    }
    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: var(--color-primary) !important;
        color: var(--color-white) !important;
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: var(--color-primary-hover) !important;
    }
    /* Main content area */
    .main > div {
        background-color: var(--color-surface);
        padding: 1.5rem 2rem;
    }
    /* Metric card */
    .metric-card {
        background-color: var(--color-card);
        border-radius: 10px;
        padding: 1.25rem 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
        text-align: center;
        border: 1px solid var(--color-border);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--color-text);
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--color-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.25rem;
    }
    /* Section titles */
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-ink);
        margin: 1.5rem 0 0.75rem 0;
    }
    /* Divider */
    hr {
        margin: 1rem 0;
        border-color: var(--color-border);
    }
    /* Alert banner de stock (home) */
    .alert-banner {
        display: flex;
        align-items: center;
        padding: 0.55rem 1rem;
        border-radius: 8px;
        border-left: 4px solid transparent;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    .alert-banner--warning {
        background-color: var(--color-warning-soft);
        border-left-color: var(--color-warning-strong);
        color: var(--color-warning-strong);
    }
    .alert-banner--critical {
        background-color: var(--color-critical-soft);
        border-left-color: var(--color-critical);
        color: var(--color-critical);
    }
    /* Panel de stock: encabezados con semáforo */
    .stock-group {
        display: flex;
        align-items: center;
        padding: 0.45rem 0.85rem;
        border-radius: 8px;
        border-left: 4px solid transparent;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 1.25rem 0 0.5rem 0;
    }
    .stock-group--out {
        background-color: var(--color-critical-soft);
        border-left-color: var(--color-critical);
        color: var(--color-critical);
    }
    .stock-group--low {
        background-color: var(--color-warning-soft);
        border-left-color: var(--color-warning-strong);
        color: var(--color-warning-strong);
    }
    .stock-group--normal {
        background-color: var(--color-success-soft);
        border-left-color: var(--color-success);
        color: var(--color-success-strong);
    }
    /* Feed de actividad */
    .activity-item {
        background-color: var(--color-card);
        border: 1px solid var(--color-border);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
    }
    .activity-meta {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-bottom: 0.35rem;
    }
    .source-badge {
        display: inline-block;
        padding: 0.1rem 0.55rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        background-color: var(--color-primary);
        color: var(--color-white);
    }
    .source-badge--bot {
        background-color: var(--color-warning-strong);
    }
    .activity-time {
        font-size: 0.78rem;
        color: var(--color-muted);
    }
    .activity-main {
        font-size: 0.92rem;
        color: var(--color-text);
    }
    .activity-main strong {
        color: var(--color-ink);
    }
    .activity-client {
        color: var(--color-muted);
    }
    .activity-payload {
        font-size: 0.82rem;
        color: var(--color-muted);
        margin-top: 0.25rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════
# Cached metric loaders (TTL = 60 s)
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=60)
def load_metrics_summary():
    with get_session() as session:
        return get_metrics_summary(session)


@st.cache_data(ttl=60)
def load_interactions_timeline():
    with get_session() as session:
        return get_interactions_timeline(session)


@st.cache_data(ttl=60)
def load_interactions_by_source():
    with get_session() as session:
        return get_interactions_by_source(session)


@st.cache_data(ttl=60)
def load_top_intents():
    with get_session() as session:
        return get_top_intents(session)


# ═══════════════════════════════════════════════════════════
# Sidebar navigation
# ═══════════════════════════════════════════════════════════

st.sidebar.markdown("# 📊 CRM Dashboard")
st.sidebar.markdown("---")

if "page" not in st.session_state:
    st.session_state.page = PAGE_METRICS

page = st.session_state.page

NAV_PAGES = (PAGE_METRICS, PAGE_CLIENTS, PAGE_STOCK, PAGE_ACTIVITY)
for nav_page in NAV_PAGES:
    if st.sidebar.button(nav_page, width="stretch"):
        st.session_state.page = nav_page
        st.rerun()

st.sidebar.markdown("---")
render_assistant_box(st.sidebar)
st.sidebar.markdown("---")
st.sidebar.caption("v1.0 · Internal Tool · DB directo")


# ═══════════════════════════════════════════════════════════
# Metrics page
# ═══════════════════════════════════════════════════════════

def _render_metrics_page() -> None:
    st.title("📊 Panel de Métricas")

    # ── Banner de alerta de stock (misma query que el panel) ──
    stock_summary = safe_load(
        load_stock_summary, spinner="Cargando alertas de stock…",
    )
    if stock_summary is not None:
        render_stock_alert_banner(stock_summary)

    metrics = safe_load(load_metrics_summary, spinner="Cargando métricas…")
    if metrics is None:
        return

    # ── Metric cards (tarjeta unificada metric_card) ──────
    cards = [
        ("Total Clientes", metrics["total_clients"]),
        ("Activos", metrics["active_clients"]),
        ("Inactivos", metrics["inactive_clients"]),
        ("Interacciones", metrics["total_interactions"]),
        ("Hoy", metrics["interactions_today"]),
        ("Esta Semana", metrics["interactions_this_week"]),
    ]

    cols = st.columns(6)
    for col, (label, value) in zip(cols, cards):
        with col:
            metric_card(label, value)

    # ── Timeline + Source pie ─────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-title">📈 Interacciones (30 días)</div>',
                    unsafe_allow_html=True)
        timeline = safe_load(
            load_interactions_timeline, spinner="Cargando timeline…",
        )
        if timeline is not None:
            df_timeline = pd.DataFrame(timeline)
            fig_line = px.line(
                df_timeline,
                x="date",
                y="count",
                markers=True,
                labels={"date": "Fecha", "count": "Interacciones"},
            )
            fig_line.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                hovermode="x unified",
            )
            fig_line.update_traces(
                line_color=PALETTE["primary_light"],
                marker=dict(size=6, color=PALETTE["primary_light"]),
            )
            st.plotly_chart(fig_line, width="stretch")

    with col_right:
        st.markdown('<div class="section-title">🎯 Por Fuente</div>',
                    unsafe_allow_html=True)
        sources = safe_load(
            load_interactions_by_source, spinner="Cargando fuentes…",
        )
        if sources:
            df_sources = pd.DataFrame(sources)
            fig_pie = px.pie(
                df_sources,
                values="count",
                names="source",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig_pie.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
            )
            fig_pie.update_traces(textinfo="label+percent")
            st.plotly_chart(fig_pie, width="stretch")
        elif sources is not None:
            st.info("No hay interacciones registradas.")

    # ── Top intents ───────────────────────────────────────
    st.markdown('<div class="section-title">🔥 Top 5 Intents</div>',
                unsafe_allow_html=True)
    intents = safe_load(load_top_intents, spinner="Cargando intents…")
    if intents:
        df_intents = pd.DataFrame(intents)
        fig_bar = px.bar(
            df_intents,
            x="intent",
            y="count",
            labels={"intent": "Intento", "count": "Cantidad"},
            color="count",
            color_continuous_scale="Blues",
            text_auto=True,
        )
        fig_bar.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title=None,
            yaxis_title="Cantidad",
        )
        fig_bar.update_traces(
            marker_line_color=PALETTE["primary_dark"],
            marker_line_width=1,
        )
        st.plotly_chart(fig_bar, width="stretch")
    elif intents is not None:
        st.info("No hay intents registrados.")


# ═══════════════════════════════════════════════════════════
# Clients page
# ═══════════════════════════════════════════════════════════

def _init_client_state() -> None:
    """Initialise all session-state keys used by the clients page."""
    for key, default in [
        ("selected_client_id", None),
        ("editing_client_id", None),
        ("show_create", False),
        ("clients_page", 1),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


def load_clients() -> list[dict]:
    """Load all clients — deliberately NOT cached: CRUD must show up right away."""
    with get_session() as session:
        return get_clients(session)


def _render_clients_page() -> None:
    st.title("👥 Gestión de Clientes")
    _init_client_state()

    # ── Search filter ─────────────────────────────────────
    search_term = st.text_input(
        "🔍 Buscar cliente",
        placeholder="Nombre, email o teléfono…",
    )

    # ── Load clients from DB ──────────────────────────────
    all_clients = safe_load(load_clients, spinner="Cargando clientes…")
    if all_clients is None:
        return

    # ── Apply search filter ───────────────────────────────
    if search_term:
        q = search_term.lower()
        all_clients = [
            c
            for c in all_clients
            if q in (c["nombre"] or "").lower()
            or q in (c["apellido"] or "").lower()
            or q in (c["email"] or "").lower()
            or q in (c["telefono"] or "").lower()
        ]

    # ── "New client" button ───────────────────────────────
    if st.button("➕ Nuevo Cliente", type="primary"):
        st.session_state.show_create = True
        st.rerun()

    # ── Create client form ────────────────────────────────
    if st.session_state.show_create:
        with st.expander("Nuevo Cliente", expanded=True):
            with st.form("create_client_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    f_nombre = st.text_input("Nombre *")
                    f_apellido = st.text_input("Apellido *")
                with c2:
                    f_email = st.text_input("Email *")
                    f_telefono = st.text_input("Teléfono")

                f_activo = st.checkbox("Activo", value=True)

                col_submit, col_cancel = st.columns([1, 5])
                with col_submit:
                    submitted = st.form_submit_button("💾 Guardar",
                                                      type="primary")
                with col_cancel:
                    cancelled = st.form_submit_button("Cancelar")

                if submitted:
                    if not f_nombre or not f_apellido or not f_email:
                        st.error("Nombre, Apellido y Email son obligatorios.")
                    else:
                        data = {
                            "nombre": f_nombre,
                            "apellido": f_apellido,
                            "email": f_email,
                            "telefono": f_telefono or None,
                            "activo": f_activo,
                        }
                        try:
                            with st.spinner("Guardando cliente…"):
                                with get_session() as session:
                                    create_client(session, data)
                        except Exception as exc:
                            st.error(f"No se pudo guardar el cliente: {exc}")
                        else:
                            st.success("✅ Cliente creado correctamente.")
                            st.session_state.show_create = False
                            st.cache_data.clear()
                            st.rerun()

                if cancelled:
                    st.session_state.show_create = False
                    st.rerun()

    # ── Client table ──────────────────────────────────────
    if not all_clients:
        st.info("No se encontraron clientes.")
        return

    df_clients = pd.DataFrame(
        [
            {
                "ID": c["id"],
                "Nombre": f"{c["nombre"]} {c["apellido"]}".strip(),
                "Email": c["email"],
                "Teléfono": c["telefono"] or "—",
                "Estado": "✅ Activo" if c["activo"] else "❌ Inactivo",
                "Fecha": c["fecha_registro"][:10]
                if c["fecha_registro"]
                else "—",
            }
            for c in all_clients
        ],
    )

    st.dataframe(
        df_clients,
        width="stretch",
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(width=60),
            "Nombre": st.column_config.TextColumn(width=200),
            "Email": st.column_config.TextColumn(width="1fr"),
            "Teléfono": st.column_config.TextColumn(width=130),
            "Estado": st.column_config.TextColumn(width=110),
            "Fecha": st.column_config.TextColumn(width=110),
        },
    )

    st.markdown("---")

    # ── Actions per client (paginado: 10 por página) ─────
    st.markdown("### Acciones")

    page_size = 10
    total_clients = len(all_clients)
    total_pages = max(1, (total_clients + page_size - 1) // page_size)
    current_page = min(max(st.session_state.clients_page, 1), total_pages)
    st.session_state.clients_page = current_page
    start = (current_page - 1) * page_size
    page_clients = all_clients[start:start + page_size]

    nav_prev, nav_info, nav_next = st.columns([1, 1.5, 1])
    with nav_prev:
        if st.button("← Anterior", disabled=current_page <= 1,
                     width="stretch"):
            st.session_state.clients_page = current_page - 1
            st.rerun()
    with nav_info:
        first = start + 1
        last = start + len(page_clients)
        st.caption(f"Mostrando {first}–{last} de {total_clients}")
    with nav_next:
        if st.button("Siguiente →", disabled=current_page >= total_pages,
                     width="stretch"):
            st.session_state.clients_page = current_page + 1
            st.rerun()

    for client in page_clients:
        full_name = f"{client["nombre"]} {client["apellido"]}".strip()
        row_cols = st.columns([3, 1.1, 1, 1])

        with row_cols[0]:
            st.write(f"**{full_name}** — {client["email"]}")

        with row_cols[1]:
            if st.button("👁 Ver interacciones", key=f"view_{client["id"]}"):
                st.session_state.selected_client_id = client["id"]
                st.session_state.editing_client_id = None
                st.rerun()

        with row_cols[2]:
            if st.button("✏️ Editar", key=f"edit_{client["id"]}"):
                st.session_state.editing_client_id = client["id"]
                st.session_state.selected_client_id = None
                st.session_state.show_create = False
                st.rerun()

        with row_cols[3]:
            if st.button("🗑 Eliminar", key=f"del_{client["id"]}"):
                st.session_state.selected_client_id = None
                st.session_state.editing_client_id = None
                st.session_state[f"confirm_del_{client["id"]}"] = True
                st.rerun()

        # ── Delete confirmation ───────────────────────────
        if st.session_state.get(f"confirm_del_{client["id"]}", False):
            st.warning(f"¿Eliminar a **{full_name}**? Esta acción no se puede deshacer.")
            confirm_cols = st.columns([1, 5])
            with confirm_cols[0]:
                if st.button("✅ Sí, eliminar",
                             key=f"confirm_yes_{client["id"]}"):
                    try:
                        with st.spinner("Eliminando cliente…"):
                            with get_session() as session:
                                deleted = delete_client(session,
                                                        client["id"])
                    except Exception as exc:
                        st.error(f"No se pudo eliminar el cliente: {exc}")
                    else:
                        if deleted:
                            st.success(f"🗑 Cliente **{full_name}** eliminado.")
                        else:
                            st.error("No se encontró el cliente.")
                        st.session_state[f"confirm_del_{client["id"]}"] = False
                        st.cache_data.clear()
                        st.rerun()
            with confirm_cols[1]:
                if st.button("❌ Cancelar",
                             key=f"confirm_no_{client["id"]}"):
                    st.session_state[f"confirm_del_{client["id"]}"] = False
                    st.rerun()

        st.divider()

    # ── Edit form ─────────────────────────────────────────
    if st.session_state.editing_client_id:
        client_id = st.session_state.editing_client_id
        client = None
        try:
            with st.spinner("Cargando cliente…"):
                with get_session() as session:
                    c = (
                        session.query(Client)
                        .filter(Client.id == client_id)
                        .first()
                    )
                    if c:
                        client = {
                            "id": c.id,
                            "nombre": c.nombre,
                            "apellido": c.apellido,
                            "telefono": c.telefono,
                            "email": c.email,
                            "activo": c.activo,
                        }
        except Exception as exc:
            st.error(f"No se pudieron cargar los datos: {exc}")
            return

        if client:
            full_name = f"{client["nombre"]} {client["apellido"]}".strip()
            st.subheader(f"✏️ Editando: {full_name}")

            with st.form("edit_client_form"):
                c1, c2 = st.columns(2)
                with c1:
                    e_nombre = st.text_input("Nombre *", value=client["nombre"])
                    e_apellido = st.text_input("Apellido *",
                                               value=client["apellido"])
                with c2:
                    e_email = st.text_input("Email *", value=client["email"])
                    e_telefono = st.text_input("Teléfono",
                                               value=client["telefono"] or "")

                e_activo = st.checkbox("Activo", value=client["activo"])

                col_save, col_cancel = st.columns([1, 5])
                with col_save:
                    save_clicked = st.form_submit_button("💾 Guardar Cambios",
                                                         type="primary")
                with col_cancel:
                    cancel_clicked = st.form_submit_button("Cancelar")

                if save_clicked:
                    errors = []
                    if not e_nombre:
                        errors.append("Nombre")
                    if not e_apellido:
                        errors.append("Apellido")
                    if not e_email:
                        errors.append("Email")
                    if errors:
                        st.error(f"Faltan campos obligatorios: {', '.join(errors)}")
                    else:
                        data = {
                            "nombre": e_nombre,
                            "apellido": e_apellido,
                            "email": e_email,
                            "telefono": e_telefono or None,
                            "activo": e_activo,
                        }
                        try:
                            with st.spinner("Guardando cambios…"):
                                with get_session() as session:
                                    updated = update_client(session,
                                                            client_id, data)
                        except Exception as exc:
                            st.error(f"No se pudo guardar el cliente: {exc}")
                        else:
                            if updated:
                                st.success("✅ Cliente actualizado correctamente.")
                            else:
                                st.error("No se encontró el cliente.")
                            st.session_state.editing_client_id = None
                            st.cache_data.clear()
                            st.rerun()

                if cancel_clicked:
                    st.session_state.editing_client_id = None
                    st.rerun()
        else:
            st.error("Cliente no encontrado.")
            st.session_state.editing_client_id = None
            st.rerun()

    # ── Interactions view ─────────────────────────────────
    if st.session_state.selected_client_id:
        client_id = st.session_state.selected_client_id
        _render_client_interactions(client_id)


def _render_client_interactions(client_id: int) -> None:
    """Display interactions for a selected client."""
    try:
        with st.spinner("Cargando interacciones…"):
            with get_session() as session:
                client = (
                    session.query(Client)
                    .filter(Client.id == client_id)
                    .first()
                )
                interactions = get_client_interactions(session, client_id)
    except Exception as exc:
        st.error(f"No se pudieron cargar los datos: {exc}")
        return

    if not client:
        st.error("Cliente no encontrado.")
        st.session_state.selected_client_id = None
        st.rerun()
        return

    full_name = f"{client["nombre"]} {client["apellido"]}".strip()
    st.markdown("---")
    st.subheader(f"💬 Interacciones de: {full_name}")

    # Quick metrics (misma tarjeta unificada que la página de Métricas)
    m1, m2 = st.columns(2)
    with m1:
        metric_card("Total Interacciones", len(interactions))
    with m2:
        if interactions:
            last_ts = interactions[0]["timestamp"]
            label = last_ts[:16].replace("T", " ") if last_ts else "—"
        else:
            label = "—"
        metric_card("Última Interacción", label)

    if interactions:
        df = pd.DataFrame(
            [
                {
                    "ID": i["id"],
                    "Fuente": i["source"],
                    "Intento": i["intent"] or "—",
                    "Usuario": i["user"] or "—",
                    "Resultado": i["result"] or "—",
                    "Fecha": i["timestamp"][:16].replace("T", " ")
                    if i["timestamp"]
                    else "—",
                }
                for i in interactions
            ],
        )
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("Este cliente no tiene interacciones registradas.")

    if st.button("🔙 Volver a Clientes"):
        st.session_state.selected_client_id = None
        st.rerun()


# ═══════════════════════════════════════════════════════════
# Page routing
# ═══════════════════════════════════════════════════════════

if page == PAGE_METRICS:
    _render_metrics_page()
elif page == PAGE_CLIENTS:
    _render_clients_page()
elif page == PAGE_STOCK:
    render_stock_page()
elif page == PAGE_ACTIVITY:
    render_activity_page()
