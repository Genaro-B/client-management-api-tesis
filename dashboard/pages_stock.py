"""Panel de stock: productos agrupados por semáforo de disponibilidad.

Bandas disjuntas (mismos criterios que el intent stock-bajo del admin bot):
agotados (stock = 0), críticos (0 < stock ≤ umbral) y normales.
"""
import pandas as pd
import streamlit as st

from components import metric_card, safe_load
from db import get_session
from queries import get_stock_summary


@st.cache_data(ttl=60)
def load_stock_summary() -> dict:
    """Resumen de stock cacheado (compartido con el banner del home)."""
    with get_session() as session:
        return get_stock_summary(session)


def _render_group(titulo: str, productos: list[dict], css_class: str,
                  vacio_msg: str) -> None:
    """Encabezado con semáforo de color + tabla del grupo."""
    st.markdown(
        f'<div class="stock-group {css_class}">{titulo}'
        f" · {len(productos)}</div>",
        unsafe_allow_html=True,
    )
    if not productos:
        st.info(vacio_msg)
        return
    df = pd.DataFrame(
        [
            {
                "Nombre": p["nombre"],
                "Stock": p["stock"],
                "Categoría": p["categoria"] or "—",
            }
            for p in productos
        ],
    )
    st.dataframe(df, width="stretch", hide_index=True)


def render_stock_page() -> None:
    """Renderiza el panel completo de stock con conteos y bandas."""
    st.title("📦 Panel de Stock")

    summary = safe_load(load_stock_summary, spinner="Cargando stock…")
    if summary is None:
        return

    counts = summary["counts"]
    total = (
        counts["out_of_stock"] + counts["low_stock"] + counts["normal"]
    )
    if total == 0:
        st.info("Sin datos aún: no hay productos activos en el catálogo.")
        return

    # ── Conteos por grupo (tarjetas unificadas) ───────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("🔴 Agotados", counts["out_of_stock"])
    with c2:
        metric_card("🟡 Críticos", counts["low_stock"])
    with c3:
        metric_card("🟢 Normales", counts["normal"])
    with c4:
        metric_card("Umbral crítico", f"≤ {summary['threshold']}")

    # ── Bandas con semáforo de color ──────────────────────
    _render_group(
        "🔴 AGOTADOS (stock = 0)",
        summary["out_of_stock"],
        "stock-group--out",
        "Sin productos agotados.",
    )
    _render_group(
        "🟡 CRÍTICOS (stock ≤ umbral)",
        summary["low_stock"],
        "stock-group--low",
        "Sin productos con stock crítico.",
    )
    _render_group(
        "🟢 NORMALES (stock > umbral)",
        summary["normal"],
        "stock-group--normal",
        "Sin datos aún: no hay productos en esta banda.",
    )
