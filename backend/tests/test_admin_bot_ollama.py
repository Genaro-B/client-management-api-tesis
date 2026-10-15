"""Tests de la capa opcional Ollama (cliente + contexto + integración).

NUNCA requieren un servidor Ollama real: `httpx.post` se mockea siempre.
Cubren: éxito con contexto, ConnectError, Timeout y respuesta vacía/rara,
y el fallback graceful del cerebro `ollama`.
"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.services.admin_bot.ollama.client import OllamaError, preguntar
from src.services.admin_bot.ollama.context_builder import construir_contexto
from src.services.admin_bot.admin_bot_service import AdminBotService


def _respuesta_ok(contenido="Hoy hubo 1 venta por $100.00."):
    """Simula una respuesta HTTP de Ollama con contenido."""
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"message": {"content": contenido}}
    return resp


# ---------------------------------------------------------------------------
# Cliente: éxito con contexto
# ---------------------------------------------------------------------------


def test_cliente_exito_devuelve_contenido():
    with patch("src.services.admin_bot.ollama.client.httpx.post", return_value=_respuesta_ok("Hola!") ) as mock_post:
        contenido = preguntar("cuántas ventas hubo hoy", "Contexto: 1 venta")
    assert contenido == "Hola!"
    # Verifica que se envió el modelo, stream:false y el contexto.
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["stream"] is False
    assert "model" in payload
    texto_mensajes = " ".join(m.get("content", "") for m in payload["messages"])
    assert "Contexto: 1 venta" in texto_mensajes
    assert "cuántas ventas hubo hoy" in texto_mensajes


def test_cliente_usa_url_de_config():
    with patch("src.services.admin_bot.ollama.client.httpx.post", return_value=_respuesta_ok()) as mock_post:
        with patch.dict("os.environ", {"OLLAMA_URL": "http://mi-ollama:9999"}):
            preguntar("hola", "ctx")
    url = mock_post.call_args[0][0]
    assert url == "http://mi-ollama:9999/api/chat"


# ---------------------------------------------------------------------------
# Cliente: fallos controlados
# ---------------------------------------------------------------------------


def test_cliente_connect_error_lanza_error_controlado():
    with patch("src.services.admin_bot.ollama.client.httpx.post",
               side_effect=httpx.ConnectError("connection refused")):
        with pytest.raises(OllamaError):
            preguntar("hola", "ctx")


def test_cliente_timeout_lanza_error_controlado():
    with patch("src.services.admin_bot.ollama.client.httpx.post",
               side_effect=httpx.TimeoutException("timed out")):
        with pytest.raises(OllamaError):
            preguntar("hola", "ctx")


def test_cliente_http_status_error_lanza_error_controlado():
    resp = MagicMock()
    resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500", request=MagicMock(), response=MagicMock()
    )
    with patch("src.services.admin_bot.ollama.client.httpx.post", return_value=resp):
        with pytest.raises(OllamaError):
            preguntar("hola", "ctx")


def test_cliente_respuesta_vacia_lanza_error_controlado():
    with patch("src.services.admin_bot.ollama.client.httpx.post",
               return_value=_respuesta_ok("   ")):
        with pytest.raises(OllamaError):
            preguntar("hola", "ctx")


def test_cliente_respuesta_inesperada_lanza_error_controlado():
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {}  # falta "message"
    with patch("src.services.admin_bot.ollama.client.httpx.post", return_value=resp):
        with pytest.raises(OllamaError):
            preguntar("hola", "ctx")


# ---------------------------------------------------------------------------
# Context builder: usa datos reales
# ---------------------------------------------------------------------------


def test_context_builder_incluye_ventas_reales(db_session):
    from datetime import datetime, timezone
    from src.models.client import Client
    from src.models.sale import Sale
    from src.repositories.client_repo import ClientRepository
    from src.repositories.sale_repo import SaleRepository

    c = ClientRepository(db_session).create(Client(nombre="Ana", apellido="G", email="a@x.com"))
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    SaleRepository(db_session).create(Sale(cliente_id=c.id, estado="CONFIRMADO", total=100, fecha=ahora))

    contexto = construir_contexto(db_session, "cuántas ventas hubo hoy", "ventas-hoy")
    assert isinstance(contexto, str)
    assert "1 venta" in contexto


# ---------------------------------------------------------------------------
# Integración: cerebro ollama con fallback
# ---------------------------------------------------------------------------


def test_brain_ollama_exito_usa_contexto(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "ollama")
    with patch("src.services.admin_bot.ollama.client.httpx.post",
               return_value=_respuesta_ok("Respuesta de Ollama con datos.")):
        intent, respuesta = AdminBotService(db_session).resolver("cuántas ventas hubo hoy")
    assert intent == "ventas-hoy"
    assert respuesta == "Respuesta de Ollama con datos."


def test_brain_ollama_connect_error_fallback(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "ollama")
    with patch("src.services.admin_bot.ollama.client.httpx.post",
               side_effect=httpx.ConnectError("refused")):
        intent, respuesta = AdminBotService(db_session).resolver("cuántas ventas hubo hoy")
    # Cae al matcher determinístico: intención reconocida y respuesta real.
    assert intent == "ventas-hoy"
    assert "no hubo ventas" in respuesta.lower()


def test_brain_ollama_timeout_fallback_no_entendido(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "ollama")
    with patch("src.services.admin_bot.ollama.client.httpx.post",
               side_effect=httpx.TimeoutException("timeout")):
        intent, respuesta = AdminBotService(db_session).resolver("qué clima hace en marte")
    assert intent == "no-entendido"
    assert "No entendí" in respuesta


def test_brain_ollama_respuesta_vacia_fallback(monkeypatch, db_session):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "ollama")
    with patch("src.services.admin_bot.ollama.client.httpx.post",
               return_value=_respuesta_ok("")):
        intent, respuesta = AdminBotService(db_session).resolver("cuántas ventas hubo hoy")
    assert intent == "ventas-hoy"
    assert "no hubo ventas" in respuesta.lower()
