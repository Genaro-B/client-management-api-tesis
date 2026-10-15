"""Tests unitarios del clasificador local de intenciones (NLU fallback).

El clasificador usa TF-IDF (palabras + n-gramas de caracteres) + regresión
logística, entrenado con un dataset en español rioplatense versionado.
Solo se usa como fallback del matcher determinístico; acá se prueba aislado.
"""
import pytest

from src.services.admin_bot.nlu.classifier import (
    NluClassifier,
    clasificar,
    UMBRAL_DEFAULT,
)
from src.services.admin_bot.admin_intent_router import INTENT_NO_ENTENDIDO


@pytest.fixture(scope="module")
def clf():
    """Un clasificador compartido (entrena una vez por módulo)."""
    return NluClassifier()


# ---------------------------------------------------------------------------
# (a) Frase no vista pero semánticamente cercana
# ---------------------------------------------------------------------------


def test_clasifica_frase_nueva_clientes_nuevos(clf):
    intent, conf = clf.classify("che, cuánta gente nueva se anotó este mes", 0.55)
    assert intent == "clientes-nuevos-mes"
    assert conf >= 0.55


def test_clasifica_frase_nueva_ventas_hoy(clf):
    intent, conf = clf.classify("decime la facturación del día de hoy", 0.55)
    assert intent == "ventas-hoy"
    assert conf >= 0.55


def test_clasifica_frase_nueva_stock(clf):
    intent, conf = clf.classify("hay productos que se están quedando sin unidades", 0.55)
    assert intent == "stock-bajo"
    assert conf >= 0.55


# ---------------------------------------------------------------------------
# (b) Confianza por debajo del umbral -> no-entendido
# ---------------------------------------------------------------------------


def test_confianza_baja_retorna_no_entendido(clf):
    # Con umbral altísimo, cualquier predicción queda por debajo.
    intent, conf = clf.classify("cuántas ventas hubo hoy", 1.01)
    assert intent == INTENT_NO_ENTENDIDO
    assert conf < 1.01


def test_texto_fuera_de_tema_retorna_no_entendido(clf):
    intent, _ = clf.classify("qué clima hace en Marte mañana", 0.55)
    assert intent == INTENT_NO_ENTENDIDO


# ---------------------------------------------------------------------------
# (c) Variantes (sinónimos / typos leves) de intents existentes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("cuantos clientes nuevos hay este mes", "clientes-nuevos-mes"),
        ("que productos tienen stock bajo", "stock-bajo"),
        ("cuantas interacciones hubo hoy", "interacciones-hoy"),
        ("cual es el producto mas vendido", "producto-top"),
        ("como vamos con el negocio", "metricas-generales"),
        ("cuantas ventas hubo hoy", "ventas-hoy"),
        ("que compro Maria ayer", "ticket-cliente"),
        # variantes con typo leve
        ("cuantos cliente nuevos hay este mes", "clientes-nuevos-mes"),
        ("productos con stok bajo", "stock-bajo"),
        ("produto mas vendido", "producto-top"),
    ],
)
def test_variantes_de_intents(clf, texto, esperado):
    intent, _ = clf.classify(texto, 0.55)
    assert intent == esperado


# ---------------------------------------------------------------------------
# (d) Texto vacío / raro -> no rompe
# ---------------------------------------------------------------------------


def test_texto_vacio_retorna_no_entendido(clf):
    intent, conf = clf.classify("", 0.55)
    assert intent == INTENT_NO_ENTENDIDO
    assert conf == 0.0


def test_texto_solo_espacios_retorna_no_entendido(clf):
    intent, conf = clf.classify("     ", 0.55)
    assert intent == INTENT_NO_ENTENDIDO
    assert conf == 0.0


# ---------------------------------------------------------------------------
# Helper de módulo (usa el umbral default de config)
# ---------------------------------------------------------------------------


def test_clasificar_helper_usa_umbral_default(monkeypatch):
    monkeypatch.delenv("ADMIN_BOT_NLU_THRESHOLD", raising=False)
    intent, conf = clasificar("cuantas ventas hubo hoy")
    assert intent == "ventas-hoy"
    assert conf >= UMBRAL_DEFAULT
