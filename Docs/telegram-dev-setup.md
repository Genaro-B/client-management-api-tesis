# Telegram Integration — Developer Setup

Guía para configurar el entorno de desarrollo e integrar Telegram con la API
usando n8n y ngrok.

## Prerrequisitos

- Python 3.14+ con las dependencias del backend instaladas
- [n8n](https://docs.n8n.io/hosting/installation/) (instalado localmente o via Docker)
- [ngrok](https://ngrok.com/download) (cuenta gratuita)
- Un bot de Telegram y su token (de [@BotFather](https://t.me/BotFather))

---

## 1. Configuración del backend

### 1.1 Variables de entorno

Crear o editar `backend/.env`:

```env
DATABASE_URL=sqlite:///./dev.db
API_KEY=dev-api-key-123
```

> **Importante**: la `API_KEY` es la clave que n8n enviará en el header
> `X-Api-Key`. En desarrollo usamos un valor fijo; en producción debe ser
> una clave segura y secreta.

### 1.2 Ejecutar migraciones

```bash
cd backend
python -m alembic upgrade head
```

### 1.3 Iniciar el servidor

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`.

---

## 2. Exponer el backend con ngrok

ngrok crea un túnel HTTPS hacia tu servidor local para que Telegram y n8n
puedan alcanzarlo.

```bash
ngrok http 8000
```

Tomar nota de la URL generada, por ejemplo:

```
Forwarding  https://a1b2c3d4e5f6.ngrok.io → http://localhost:8000
```

A partir de ahora la API es accesible desde internet en:

```
https://a1b2c3d4e5f6.ngrok.io/api/v1/interactions/
```

> **Tips**:
> - Con la cuenta gratuita de ngrok la URL cambia cada vez que reinicias.
> - Usa `ngrok http 8000 --host-header=localhost:8000` si hay problemas con el host header.
> - Para producción, configura un dominio estático en ngrok o un reverse proxy.

---

## 3. Configurar el Webhook de Telegram

### 3.1 Crear un bot (si no tenés uno)

1. Abrí Telegram y buscá [@BotFather](https://t.me/BotFather).
2. Enviá `/newbot` y seguí las instrucciones.
3. Guardá el **token** que te da (formato: `123456:ABC-DEF1234ghIkl...`).

### 3.2 Configurar el webhook

Reemplazá `<TOKEN>` y la URL de ngrok en el siguiente comando:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://a1b2c3d4e5f6.ngrok.io/rest/webhook/telegram-webhook",
    "allowed_updates": ["message"]
  }'
```

Donde:
- `https://a1b2c3d4e5f6.ngrok.io` es la URL de ngrok.
- `/rest/webhook/telegram-webhook` es la ruta del Webhook node de n8n
  (n8n expone sus webhooks en `/rest/webhook/<path>`).

### 3.3 Verificar el webhook

```bash
curl -X GET "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

Deberías ver `"has_custom_certificate": false` y `"pending_update_count": 0`.

---

## 4. Configurar n8n

### 4.1 Iniciar n8n

```bash
n8n start
```

Por defecto corre en `http://localhost:5678`.

### 4.2 Importar el flujo

1. Abrí `http://localhost:5678` en el navegador.
2. **Workflows** → **Add Workflow** → **Import from File**.
3. Seleccioná `Docs/telegram-n8n-flow.json`.
4. Configurá las variables de entorno en n8n:
   - **Settings** → **Environment Variables** → agregá:
     - `API_KEY`: `dev-api-key-123`
     - `API_URL`: `https://a1b2c3d4e5f6.ngrok.io` (tu URL de ngrok)

### 4.3 Activar el workflow

1. Hacé clic en **Active** en la esquina superior derecha.
2. El Webhook node ahora está escuchando en:
   ```
   https://a1b2c3d4e5f6.ngrok.io/rest/webhook/telegram-webhook
   ```

### 4.4 Verificar con un mensaje

Enviale un mensaje a tu bot de Telegram. Deberías ver en los logs de n8n
que el flujo se ejecuta y la API recibe el POST.

---

## 5. Testing con curl

Podés probar la API directamente sin Telegram ni n8n:

### 5.1 POST exitoso (201)

```bash
curl -X POST http://localhost:8000/api/v1/interactions/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: dev-api-key-123" \
  -H "X-Idempotency-Key: tg-42" \
  -d '{
    "source": "telegram",
    "payload": "{\"message_id\":42,\"text\":\"Hola, necesito info\"}",
    "user": "987654321"
  }'
```

Respuesta esperada:

```json
{
  "id": 1,
  "timestamp": "2026-06-29T20:00:00Z"
}
```

### 5.2 Idempotencia (409)

Repetí el mismo curl (mismo `X-Idempotency-Key`). Deberías recibir:

```json
{
  "detail": "Interaction with idempotency_key 'tg-42' already exists"
}
```

Con código **409 Conflict**.

### 5.3 Sin API Key (401)

```bash
curl -X POST http://localhost:8000/api/v1/interactions/ \
  -H "Content-Type: application/json" \
  -d '{"source": "telegram", "payload": "{}"}'
```

Respuesta: **401** con `"Invalid or missing API key"`.

### 5.4 API Key inválida (401)

```bash
curl -X POST http://localhost:8000/api/v1/interactions/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: wrong-key" \
  -d '{"source": "telegram", "payload": "{}"}'
```

Respuesta: **401**.

---

## 6. Arquitectura del flujo completo

```
Telegram
   │
   ▼  (webhook HTTPS)
n8n Webhook Node
   │
   ├── Set Headers (X-Api-Key, X-Idempotency-Key, Content-Type)
   │
   ├── Build Body (source, user, payload)
   │
   ▼  (POST HTTP)
FastAPI /api/v1/interactions/
   │
   ├── verify_api_key (valida X-Api-Key)
   ├── InteractionService.create (valida + idempotencia)
   ├── InteractionRepository.save (persiste en BD)
   │
   ▼
201 Created / 409 Conflict / 400 Bad Request / 401 Unauthorized
```

## 7. Troubleshooting

| Problema | Causa probable | Solución |
|----------|---------------|----------|
| Telegram responde `404 Not Found` | La URL del webhook no apunta a n8n | Verificá que ngrok esté corriendo y la URL incluya `/rest/webhook/telegram-webhook` |
| n8n responde `500` | Error en la expresión de mapeo | Revisá los logs de ejecución en n8n |
| API responde `401` | `X-Api-Key` no coincide | Verificá `API_KEY` en `.env` del backend y en las env vars de n8n |
| API responde `409` | Mismo `X-Idempotency-Key` enviado dos veces | Es comportamiento esperado para evitar duplicados |
| ngrok no inicia | Puerto ocupado o falta de permisos | Probá `ngrok http 8001` si cambiás el puerto |
