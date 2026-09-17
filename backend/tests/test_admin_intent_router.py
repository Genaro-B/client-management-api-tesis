"""Tests unitarios del matcher determinístico de intenciones administrativas.

El router clasifica texto libre en español en una intención administrativa
usando pattern matching determinístico (palabras clave), sin IA ni ML.
Es una función pura: mismo texto -> misma intención, sin estado ni IO.
"""
import pytest

from src.services.admin_bot.admin_intent_router import AdminIntentRouter


@pytest.fixture
def router():
    return AdminIntentRouter()


# ---------------------------------------------------------------------------
# Escenarios del spec (admin-bot/spec.md — Requirement: Matcher determinístico)
# ---------------------------------------------------------------------------


def test_detecta_clientes_nuevos_mes(router):
    assert router.match("¿cuántos clientes nuevos hay este mes?") == "clientes-nuevos-mes"


def test_detecta_clientes_nuevos_mes_variante(router):
    assert router.match("cómo van los nuevos clientes del mes") == "clientes-nuevos-mes"


def test_detecta_clientes_nuevos_mes_otra_variante(router):
    assert router.match("hubo clientes registrados este mes") == "clientes-nuevos-mes"


def test_detecta_stock_bajo(router):
    assert router.match("qué productos tienen stock bajo") == "stock-bajo"


def test_detecta_stock_bajo_variante(router):
    assert router.match("productos sin stock") == "stock-bajo"


def test_detecta_stock_bajo_otra_variante(router):
    assert router.match("quiero ver el bajo stock del catálogo") == "stock-bajo"


def test_detecta_interacciones_hoy(router):
    assert router.match("cuántas interacciones hubo hoy") == "interacciones-hoy"


def test_detecta_interacciones_hoy_variante(router):
    assert router.match("interacciones de hoy") == "interacciones-hoy"


def test_detecta_producto_mas_vendido(router):
    assert router.match("cuál es el producto más vendido") == "producto-top"


def test_detecta_producto_mas_vendido_variante(router):
    assert router.match("cuál vendió más") == "producto-top"


def test_detecta_producto_mas_vendido_otra_variante(router):
    assert router.match("top producto") == "producto-top"


def test_detecta_metricas_generales(router):
    assert router.match("cómo vamos con el negocio") == "metricas-generales"


def test_detecta_metricas_variante(router):
    assert router.match("dame las métricas") == "metricas-generales"


def test_detecta_metricas_resumen(router):
    assert router.match("resumen del negocio") == "metricas-generales"


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------


def test_texto_irreconocible_cae_en_fallback(router):
    assert router.match("qué clima hace en marte") == "no-entendido"


def test_texto_vacio_cae_en_fallback(router):
    assert router.match("") == "no-entendido"


def test_texto_solo_espacios_cae_en_fallback(router):
    assert router.match("   ") == "no-entendido"


# ---------------------------------------------------------------------------
# Robustez: mayúsculas y tildes
# ---------------------------------------------------------------------------


def test_ignora_mayusculas(router):
    assert router.match("MÉTRICAS DEL NEGOCIO") == "metricas-generales"


def test_ignora_tildes(router):
    # "más" con tilde se normaliza a "mas" y matchea producto-top
    assert router.match("¿cuál es el producto más vendido?") == "producto-top"
    # "métricas" con tilde se normaliza a "metricas" y matchea metricas-generales
    assert router.match("dame las métricas") == "metricas-generales"


# ---------------------------------------------------------------------------
# Especificidad: un patrón genérico no debe robar intenciones específicas
# ---------------------------------------------------------------------------


def test_consulta_de_metricas_no_se_roba_por_este_mes(router):
    """'este mes' como palabra suelta NO debe matchear clientes-nuevos-mes."""
    assert router.match("qué métricas tenemos este mes") == "metricas-generales"