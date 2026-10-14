"""Tests de integración de POST /api/v1/clients/register-bot.

Registro de prospecto desde el bot: X-Api-Key (no JWT), 201 en alta,
200 en re-registro idempotente, 401 sin key, 422 sin campos requeridos.
"""
TEST_API_KEY = "dev-api-key-123"
PREFIX = "/api/v1/clients"


def _payload(telegram_user_id="12345", nombre="Juan", apellido="Perez", telefono="+541122223333"):
    return {
        "telegram_user_id": telegram_user_id,
        "nombre": nombre,
        "apellido": apellido,
        "telefono": telefono,
    }


def test_register_bot_alta_201(client):
    resp = client.post(
        f"{PREFIX}/register-bot",
        json=_payload(),
        headers={"X-Api-Key": TEST_API_KEY},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["telegram_user_id"] == "12345"
    assert data["email"] == "tg12345@telegram.local"
    assert data["role"] == "user"


def test_register_bot_re_registro_200_idempotente(client):
    headers = {"X-Api-Key": TEST_API_KEY}
    first = client.post(f"{PREFIX}/register-bot", json=_payload(), headers=headers)
    assert first.status_code == 201

    second = client.post(f"{PREFIX}/register-bot", json=_payload(), headers=headers)
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]


def test_register_bot_sin_api_key_401(client):
    resp = client.post(f"{PREFIX}/register-bot", json=_payload())
    assert resp.status_code == 401


def test_register_bot_sin_nombre_422(client):
    resp = client.post(
        f"{PREFIX}/register-bot",
        json={"telegram_user_id": "12345"},
        headers={"X-Api-Key": TEST_API_KEY},
    )
    assert resp.status_code == 422


def test_register_bot_vincula_por_telefono(client, admin_headers_bearer):
    """Un cliente previo (sin telegram) con el mismo teléfono se linkea."""
    resp = client.post(
        f"{PREFIX}/",
        json={"nombre": "Cliente", "apellido": "Viejo", "email": "viejo@x.com",
              "telefono": "+549998887777"},
        headers=admin_headers_bearer,
    )
    assert resp.status_code in (200, 201)
    previo_id = resp.json()["id"]

    link = client.post(
        f"{PREFIX}/register-bot",
        json=_payload(telegram_user_id="555", telefono="+549998887777"),
        headers={"X-Api-Key": TEST_API_KEY},
    )
    assert link.status_code == 200
    assert link.json()["id"] == previo_id
    assert link.json()["telegram_user_id"] == "555"
