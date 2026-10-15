"""Tests de API del asistente: selección de cerebro end-to-end.

POST /api/v1/admin-bot/consult con distintos valores de ADMIN_BOT_BRAIN.
El contrato NO cambia: request {mensaje}, response {intent, respuesta}.
"""
PREFIX = "/api/v1/admin-bot"

# Frase que el matcher determinístico ignora pero el clasificador rescata.
FRASE_SOLO_CLASIFICADOR = "cuánta gente nueva se anotó este mes"


def test_api_deterministic_misma_respuesta_que_baseline(client, admin_headers_bearer, monkeypatch):
    """Con deterministic, una frase reconocida por el matcher responde igual."""
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "deterministic")
    resp = client.post(f"{PREFIX}/consult", json={"mensaje": "cuántas ventas hubo hoy"},
                       headers=admin_headers_bearer)
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) == {"intent", "respuesta"}
    assert data["intent"] == "ventas-hoy"


def test_api_deterministic_no_usa_clasificador(client, admin_headers_bearer, monkeypatch):
    """Con deterministic, una frase desconocida queda en no-entendido."""
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "deterministic")
    resp = client.post(f"{PREFIX}/consult", json={"mensaje": FRASE_SOLO_CLASIFICADOR},
                       headers=admin_headers_bearer)
    assert resp.status_code == 200
    assert resp.json()["intent"] == "no-entendido"


def test_api_classifier_rescata_end_to_end(client, admin_headers_bearer, monkeypatch):
    """Con classifier (default), el fallback clasifica y responde con datos."""
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", "0.55")
    resp = client.post(f"{PREFIX}/consult", json={"mensaje": FRASE_SOLO_CLASIFICADOR},
                       headers=admin_headers_bearer)
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "clientes-nuevos-mes"
    assert "No entendí" not in data["respuesta"]


def test_api_classifier_umbral_alto_no_entendido(client, admin_headers_bearer, monkeypatch):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", "1.01")
    resp = client.post(f"{PREFIX}/consult", json={"mensaje": FRASE_SOLO_CLASIFICADOR},
                       headers=admin_headers_bearer)
    assert resp.status_code == 200
    assert resp.json()["intent"] == "no-entendido"


def test_api_registra_intent_resuelto(client, admin_headers_bearer, monkeypatch):
    """La interacción registrada usa el intent resuelto (no no-entendido)."""
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "classifier")
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", "0.55")
    client.post(f"{PREFIX}/consult", json={"mensaje": FRASE_SOLO_CLASIFICADOR},
                headers=admin_headers_bearer)
    items = client.get("/api/v1/interactions/", headers=admin_headers_bearer).json()["items"]
    assert items[0]["source"] == "admin-bot"
    assert items[0]["intent"] == "clientes-nuevos-mes"


def test_api_contrato_sin_cambios_422(client, admin_headers_bearer):
    """El contrato sigue validando mensaje vacío con 422."""
    resp = client.post(f"{PREFIX}/consult", json={"mensaje": ""}, headers=admin_headers_bearer)
    assert resp.status_code == 422
