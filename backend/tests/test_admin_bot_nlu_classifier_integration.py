"""Tests de integración de la cascada de cerebros del asistente.

Verifica `AdminBotService.resolver(texto) -> (intent, respuesta)`:
- modo `deterministic`: SOLO matcher (comportamiento idéntico al actual);
- modo `classifier` (default): matcher primero, clasificador como fallback;
- umbral: confianza < umbral -> no-entendido;
- el matcher nunca es pisado por el clasificador.
"""
from src.services.admin_bot.admin_bot_service import AdminBotService


# Frase que el matcher determinístico NO reconoce pero el clasificador sí.
FRASE_SOLO_CLASIFICADOR = "cuánta gente nueva se anotó este mes"
INTENT_ESPERADO = "clientes-nuevos-mes"


# ---------------------------------------------------------------------------
# Modo deterministic: comportamiento idéntico al actual
# ---------------------------------------------------------------------------


def test_deterministic_matchea_frase_existente(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "deterministic")
    intent, respuesta = AdminBotService(db_session).resolver("cuántas ventas hubo hoy")
    assert intent == "ventas-hoy"
    assert isinstance(respuesta, str) and respuesta


def test_deterministic_no_usa_clasificador(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "deterministic")
    intent, respuesta = AdminBotService(db_session).resolver(FRASE_SOLO_CLASIFICADOR)
    assert intent == "no-entendido"
    assert "No entendí" in respuesta


def test_deterministic_fuera_de_tema_no_entendido(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "deterministic")
    intent, _ = AdminBotService(db_session).resolver("qué clima hace en marte")
    assert intent == "no-entendido"


# ---------------------------------------------------------------------------
# Modo classifier (default): matcher primero + fallback clasificador
# ---------------------------------------------------------------------------


def test_classifier_matcher_primero_sin_cambios(monkeypatch, db_session):
    """Frase que el matcher reconoce: el resultado no cambia con classifier."""
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    intent, _ = AdminBotService(db_session).resolver("cuántas ventas hubo hoy")
    assert intent == "ventas-hoy"


def test_classifier_rescata_frase_que_matcher_ignora(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", "0.55")
    intent, respuesta = AdminBotService(db_session).resolver(FRASE_SOLO_CLASIFICADOR)
    assert intent == INTENT_ESPERADO
    # La respuesta la produce el handler real (no es el fallback de no-entendido).
    assert "No entendí" not in respuesta


def test_classifier_umbral_alto_retorna_no_entendido(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", "1.01")
    intent, respuesta = AdminBotService(db_session).resolver(FRASE_SOLO_CLASIFICADOR)
    assert intent == "no-entendido"
    assert "No entendí" in respuesta


def test_classifier_fuera_de_tema_no_entendido(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", "0.55")
    intent, _ = AdminBotService(db_session).resolver("qué clima hace en marte")
    assert intent == "no-entendido"


def test_classifier_default_sin_env(monkeypatch, db_session):
    """Sin definir ADMIN_BOT_BRAIN, el default es classifier."""
    monkeypatch.delenv("ADMIN_BOT_BRAIN", raising=False)
    monkeypatch.delenv("ADMIN_BOT_NLU_THRESHOLD", raising=False)
    intent, _ = AdminBotService(db_session).resolver(FRASE_SOLO_CLASIFICADOR)
    assert intent == INTENT_ESPERADO
