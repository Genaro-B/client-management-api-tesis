# -*- coding: utf-8 -*-
"""Tests de enriquecimiento de vocabulario del clasificador NLU (mejora v6).

Motivación (gap medido): el dataset original estaba demasiado "clonado" a los
patrones del matcher determinístico. Frases naturales con vocabulario de
negocio distinto (facturar, plata, guita, ingresos, números, balance) caían en
`no-entendido` porque la confianza quedaba por debajo del umbral (0.55) o el
argmax apuntaba a la intención equivocada.

Estrategia de esta mejora (TDD): **enriquecer el dataset** con familias de
sinónimos nuevas por intención, SIN bajar el umbral (se preserva 0.55). Se
verifica además que no se generen falsos positivos sobre las frases
`no-entendido` ya presentes en el dataset.

Criterios cubiertos:
  1. La cascada (servicio) resuelve correctamente el vocabulario nuevo.
  2. Las frases fuera de tema siguen siendo `no-entendido` y el matcher
     determinístico no cambia para las frases que YA matcheaba.
  3. Typos ("stok") en lo posible se rescatan.
  4. Cero falsos positivos sobre las frases `no-entendido` del dataset.
"""
import json
import os

import pytest

from src.services.admin_bot.admin_bot_service import AdminBotService
from src.services.admin_bot.admin_intent_router import (
    INTENT_NO_ENTENDIDO,
    AdminIntentRouter,
)
from src.services.admin_bot.nlu import classifier as clf_mod
from src.services.admin_bot.nlu.classifier import NluClassifier

# Umbral de trabajo: el default documentado. La mejora NO baja el umbral.
UMBRAL = 0.55

# Frases con vocabulario "de negocio" que el matcher NO reconoce y que el
# clasificador DEBE rescatar (criterio 1).
VOCABULARIO_NUEVO = [
    ("cuanto facturamos hoy", "ventas-hoy"),
    ("quiero ver los numeros del negocio", "metricas-generales"),
    ("necesito saber la plata que entro hoy", "ventas-hoy"),
    ("cuanta guita entro hoy", "ventas-hoy"),
]

# Frases fuera de tema que DEBEN seguir siendo no-entendido (criterio 2).
FUERA_DE_TEMA = [
    "hola buenos dias",
    "qué clima hace en marte",
]


def _frases_no_entendido_dataset():
    """Lee las frases etiquetadas `no-entendido` del dataset versionado."""
    ruta = os.path.join(os.path.dirname(clf_mod.__file__), "dataset.json")
    with open(ruta, encoding="utf-8") as fh:
        return json.load(fh)[INTENT_NO_ENTENDIDO]


# ---------------------------------------------------------------------------
# Criterio 1 (precondición): el matcher determinístico NO reconoce estas frases,
# así que el rescate proviene SIEMPRE del clasificador.
# ---------------------------------------------------------------------------


def test_router_no_reconoce_vocabulario_nuevo():
    router = AdminIntentRouter()
    for texto, _ in VOCABULARIO_NUEVO:
        assert router.match(texto) == INTENT_NO_ENTENDIDO, (
            f"El matcher ya reconoce {texto!r}: la prueba de rescate no aplica."
        )


# ---------------------------------------------------------------------------
# Criterio 1: la cascada real (servicio) resuelve el vocabulario nuevo.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("texto,esperado", VOCABULARIO_NUEVO)
def test_cascada_service_resuelve_vocabulario_nuevo(
    monkeypatch, db_session, texto, esperado
):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", str(UMBRAL))
    intent, respuesta = AdminBotService(db_session).resolver(texto)
    assert intent == esperado
    # La respuesta la produce el handler real, no el fallback de no-entendido.
    assert "No entendí" not in respuesta


@pytest.mark.parametrize("texto,esperado", VOCABULARIO_NUEVO)
def test_clasificar_rescata_vocabulario_nuevo(texto, esperado):
    """A nivel clasificador: intención correcta con confianza >= umbral."""
    intent, conf = clf_mod.clasificar(texto, UMBRAL)
    assert intent == esperado
    assert conf >= UMBRAL, f"{texto!r}: confianza {conf:.2f} < {UMBRAL}"


# ---------------------------------------------------------------------------
# Criterio 2: fuera de tema sigue siendo no-entendido (clasificador y cascada).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("texto", FUERA_DE_TEMA)
def test_clasificar_fuera_de_tema_no_entendido(texto):
    intent, _ = clf_mod.clasificar(texto, UMBRAL)
    assert intent == INTENT_NO_ENTENDIDO


@pytest.mark.parametrize("texto", FUERA_DE_TEMA)
def test_cascada_fuera_de_tema_no_entendido(monkeypatch, db_session, texto):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", str(UMBRAL))
    intent, respuesta = AdminBotService(db_session).resolver(texto)
    assert intent == INTENT_NO_ENTENDIDO
    assert "No entendí" in respuesta


@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("¿cuántos clientes nuevos hay este mes?", "clientes-nuevos-mes"),
        ("hubo clientes registrados este mes", "clientes-nuevos-mes"),
        ("qué productos tienen stock bajo", "stock-bajo"),
        ("productos sin stock", "stock-bajo"),
        ("cuántas interacciones hubo hoy", "interacciones-hoy"),
        ("interacciones de hoy", "interacciones-hoy"),
        ("cuál es el producto más vendido", "producto-top"),
        ("cómo vamos con el negocio", "metricas-generales"),
        ("resumen del negocio", "metricas-generales"),
        ("cuántas ventas hubo hoy", "ventas-hoy"),
        ("quiero ver el ticket del cliente 5", "ticket-cliente"),
    ],
)
def test_matcher_deterministico_sin_cambios(texto, esperado):
    """El matcher sigue resolviendo igual las frases que YA reconocía."""
    assert AdminIntentRouter().match(texto) == esperado


# ---------------------------------------------------------------------------
# Criterio 3: typos leves ("stok") se intentan rescatar.
# ---------------------------------------------------------------------------


def test_typo_stok_rescata_stock_bajo(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", str(UMBRAL))
    intent, _ = AdminBotService(db_session).resolver("cuanto stok queda")
    assert intent == "stock-bajo"


# ---------------------------------------------------------------------------
# TRIANGULATE: más paráfrasis reales, typos extra y ruido adicional.
# ---------------------------------------------------------------------------

# Paráfrasis adicionales por familia de vocabulario (mínimo 2 por intención).
PARAFRASIS_EXTRA = [
    # ventas-hoy (plata / guita / facturar / ingresos / recaudar)
    ("cuanta plata entro hoy", "ventas-hoy"),
    ("cuanto facturamos en el dia", "ventas-hoy"),
    ("cuanto se recaudo hoy", "ventas-hoy"),
    ("cuanto dinero ingreso hoy", "ventas-hoy"),
    ("que facturacion hubo hoy", "ventas-hoy"),
    # metricas-generales (números / balance / gestión)
    ("quiero ver el balance general", "metricas-generales"),
    ("como vienen los numeros del negocio", "metricas-generales"),
    ("los numeros de la gestion", "metricas-generales"),
    ("dame el estado general del negocio", "metricas-generales"),
    # stock-bajo (stock / inventario)
    ("cuanto stock queda", "stock-bajo"),
    ("cuanto inventario queda", "stock-bajo"),
    ("cuanto stock me queda", "stock-bajo"),
]

# Typos adicionales (incluyendo uno "pesado": quanto stok qeda).
TYPOS_EXTRA = [
    ("quanto stok qeda", "stock-bajo"),
    ("cuanto facturamo hoy", "ventas-hoy"),
    ("cuanta plata entro oy", "ventas-hoy"),
]

# Ruido adicional: debe seguir siendo no-entendido.
RUIDO_EXTRA = [
    "cual es la capital de Francia",
    "dame la receta de milanesas",
    "cuanto es 2 mas 2",
    "quien gano el partido",
    "cantame una cancion",
]


@pytest.mark.parametrize("texto,esperado", PARAFRASIS_EXTRA)
def test_parafrasis_extra_resueltas(texto, esperado):
    intent, conf = clf_mod.clasificar(texto, UMBRAL)
    assert intent == esperado
    assert conf >= UMBRAL, f"{texto!r}: confianza {conf:.2f} < {UMBRAL}"


@pytest.mark.parametrize("texto,esperado", TYPOS_EXTRA)
def test_typos_extra_resueltos(texto, esperado):
    intent, conf = clf_mod.clasificar(texto, UMBRAL)
    assert intent == esperado
    assert conf >= UMBRAL, f"{texto!r}: confianza {conf:.2f} < {UMBRAL}"


@pytest.mark.parametrize("texto", RUIDO_EXTRA)
def test_ruido_extra_sigue_no_entendido(texto):
    intent, _ = clf_mod.clasificar(texto, UMBRAL)
    assert intent == INTENT_NO_ENTENDIDO


@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("cuanta plata entro hoy", "ventas-hoy"),
        ("quiero ver el balance general", "metricas-generales"),
        ("cuanto stock queda", "stock-bajo"),
    ],
)
def test_cascada_parafrasis_extra(monkeypatch, db_session, texto, esperado):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", str(UMBRAL))
    intent, respuesta = AdminBotService(db_session).resolver(texto)
    assert intent == esperado
    assert "No entendí" not in respuesta


# ---------------------------------------------------------------------------
# Criterio 4: cero falsos positivos sobre las frases no-entendido del dataset.
# ---------------------------------------------------------------------------


def test_sin_falsos_positivos_en_no_entendido_dataset():
    clf = NluClassifier()
    fallos = []
    for frase in _frases_no_entendido_dataset():
        intent, conf = clf.classify(frase, UMBRAL)
        if intent != INTENT_NO_ENTENDIDO:
            fallos.append(f"{frase!r} -> {intent} ({conf:.2f})")
    assert not fallos, "Falsos positivos:\n" + "\n".join(fallos)
