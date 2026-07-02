# Telegram → n8n → API: Field Mapping

Este documento explica cómo el flujo `telegram-n8n-flow.json` mapea los campos de una
actualización de Telegram a una petición `POST /api/v1/interactions/`.

## Visión general

```
Telegram ──webhook──▶ n8n Webhook Node ──▶ Set Headers ──▶ Build Body ──▶ HTTP Request ──▶ API
```

## Mapeo de campos

### Headers

| Header              | Origen                                                    | Expresión n8n                              |
|---------------------|-----------------------------------------------------------|--------------------------------------------|
| `X-Api-Key`         | Variable de entorno `API_KEY`                             | `{{ $env.API_KEY }}`                       |
| `X-Idempotency-Key` | `message.message_id` con prefijo `tg-`                    | `{{ 'tg-' + $json.message.message_id }}`   |
| `Content-Type`      | Fijo                                                      | `application/json`                         |

### Cuerpo de la petición

| Campo     | Origen                            | Expresión n8n                                                |
|-----------|-----------------------------------|--------------------------------------------------------------|
| `source`  | Fijo                              | `"telegram"`                                                 |
| `user`    | `message.from.id` (ID de Telegram)| `{{ $json.message.from.id }}`                                |
| `payload` | Objeto con `message_id`, `text`, `chat_id`, `date` | `{{ JSON.stringify({ message_id, text, chat_id, date }) }}` |

### Ejemplo

Un mensaje de Telegram como:

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 42,
    "from": { "id": 987654321, "is_bot": false, "first_name": "Juan" },
    "chat": { "id": 987654321, "type": "private" },
    "text": "Hola, necesito info sobre el producto X",
    "date": 1719446400
  }
}
```

Genera la siguiente petición a la API:

```http
POST /api/v1/interactions/
X-Api-Key: dev-api-key-123
X-Idempotency-Key: tg-42
Content-Type: application/json

{
  "source": "telegram",
  "user": "987654321",
  "payload": "{\"message_id\":42,\"text\":\"Hola, necesito info sobre el producto X\",\"chat_id\":987654321,\"date\":1719446400}"
}
```

## Idempotencia

El `X-Idempotency-Key` se construye con `message_id` prefijado con `tg-`. Como
`message_id` es único por chat en Telegram, esto asegura que:

- **Primera vez**: la API responde **201 Created** y almacena la interacción.
- **Reintento (mismo mensaje)**: la API responde **409 Conflict** y **no** duplica el registro.
- n8n puede reintentar en caso de fallo de red sin riesgo de duplicados.

## Variables de entorno en n8n

Configurar en n8n (Settings → Environment Variables):

| Variable   | Valor                                           |
|------------|-------------------------------------------------|
| `API_KEY`  | `dev-api-key-123` (o la clave que uses)         |
| `API_URL`  | `https://tu-subdominio.ngrok.io` (en desarrollo)|

## Cómo importar el flujo

1. Abrir n8n → **Workflows** → **Add Workflow** → **Import from File**.
2. Seleccionar `Docs/telegram-n8n-flow.json`.
3. Configurar el **Webhook** node con la URL pública (ver `telegram-dev-setup.md`).
4. Ajustar `$env.API_URL` en el node **HTTP Request** a la URL de ngrok.
5. Activar el workflow.

## Notas

- El campo `payload` **debe ser un string JSON**, no un objeto. Por eso usamos `JSON.stringify()`.
- `intent` y `result` se omiten intencionalmente — el bot de Telegram no los provee.
- `clientLookup` puede añadirse después si se necesita enlazar a un cliente existente.
