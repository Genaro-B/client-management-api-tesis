"""Streamlit dashboard for CRM — metrics overview and client management.

Usage:
    cd dashboard/
    pip install -r requirements.txt
    streamlit run app.py

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
    /* Dark sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        min-width: 260px;
    }
    [data-testid="stSidebar"] .sidebar-content {
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] .st-emotion-cache-1v7mm3u {
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f1f5f9;
    }
    /* Sidebar nav buttons */
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        border: none !important;
        color: #cbd5e1 !important;
        justify-content: flex-start !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 1rem !important;
        margin: 0.15rem 0 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.07) !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }
    /* Main content area */
    .main > div {
        background-color: #f8fafc;
        padding: 1.5rem 2rem;
    }
    /* Metric card */
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.25rem 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.25rem;
    }
    /* Section titles */
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #0f172a;
        margin: 1.5rem 0 0.75rem 0;
    }
    /* Divider */
    hr {
        margin: 1rem 0;
        border-color: #e2e8f0;
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
    st.session_state.page = "📊 Métricas"

page = st.session_state.page

if st.sidebar.button("📊 Métricas", use_container_width=True):
    st.session_state.page = "📊 Métricas"
    st.rerun()
if st.sidebar.button("👥 Clientes", use_container_width=True):
    st.session_state.page = "👥 Clientes"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("v1.0 · Internal Tool · DB directo")


# ═══════════════════════════════════════════════════════════
# Metrics page
# ═══════════════════════════════════════════════════════════

def _render_metrics_page() -> None:
    st.title("📊 Panel de Métricas")

    metrics = load_metrics_summary()

    # ── Metric cards ──────────────────────────────────────
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
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-label">{label}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Timeline + Source pie ─────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-title">📈 Interacciones (30 días)</div>',
                    unsafe_allow_html=True)
        timeline = load_interactions_timeline()
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
            line_color="#3b82f6",
            marker=dict(size=6, color="#3b82f6"),
        )
        st.plotly_chart(fig_line, width="stretch")

    with col_right:
        st.markdown('<div class="section-title">🎯 Por Fuente</div>',
                    unsafe_allow_html=True)
        sources = load_interactions_by_source()
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
        else:
            st.info("No hay interacciones registradas.")

    # ── Top intents ───────────────────────────────────────
    st.markdown('<div class="section-title">🔥 Top 5 Intents</div>',
                unsafe_allow_html=True)
    intents = load_top_intents()
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
            marker_line_color="#1e40af",
            marker_line_width=1,
        )
        st.plotly_chart(fig_bar, width="stretch")
    else:
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
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


def _render_clients_page() -> None:
    st.title("👥 Gestión de Clientes")
    _init_client_state()

    # ── Search filter ─────────────────────────────────────
    search_term = st.text_input(
        "🔍 Buscar cliente",
        placeholder="Nombre, email o teléfono…",
    )

    # ── Load clients from DB ──────────────────────────────
    with get_session() as session:
        all_clients = get_clients(session)

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
    if st.button("➕ Nuevo Cliente", type="primary", use_container_width=False):
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
                        with get_session() as session:
                            create_client(session, data)
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
        use_container_width=True,
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

    # ── Actions per client ────────────────────────────────
    st.markdown("### Acciones")
    for client in all_clients:
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
                    with get_session() as session:
                        deleted = delete_client(session, client["id"])
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
                        with get_session() as session:
                            updated = update_client(session, client_id, data)
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
    with get_session() as session:
        client = (
            session.query(Client)
            .filter(Client.id == client_id)
            .first()
        )
        interactions = get_client_interactions(session, client_id)

    if not client:
        st.error("Cliente no encontrado.")
        st.session_state.selected_client_id = None
        st.rerun()
        return

    full_name = f"{client["nombre"]} {client["apellido"]}".strip()
    st.markdown("---")
    st.subheader(f"💬 Interacciones de: {full_name}")

    # Quick metrics
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Total Interacciones", len(interactions))
    with m2:
        if interactions:
            last_ts = interactions[0]["timestamp"]
            label = last_ts[:16].replace("T", " ") if last_ts else "—"
        else:
            label = "—"
        st.metric("Última Interacción", label)

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
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Este cliente no tiene interacciones registradas.")

    if st.button("🔙 Volver a Clientes"):
        st.session_state.selected_client_id = None
        st.rerun()


# ═══════════════════════════════════════════════════════════
# Page routing
# ═══════════════════════════════════════════════════════════

if page == "📊 Métricas":
    _render_metrics_page()
elif page == "👥 Clientes":
    _render_clients_page()
