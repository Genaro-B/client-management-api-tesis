# Documentación de Flujos n8n

## Índice

1. [Flujo Principal: Sistema de Automatización de Prospectos](#1-flujo-principal-sistema-de-automatización-de-prospectos)
2. [Flujo Auxiliar: Telegram → API Interaction](#2-flujo-auxiliar-telegram--api-interaction)
3. [Consideraciones Generales](#3-consideraciones-generales)

---

## 1. Flujo Principal: Sistema de Automatización de Prospectos

> Archivo: `Docs/Sistema de Automatización de Prospectos.json`  
> Estado: `active: true`

### Diagrama

```
Telegram Trigger
      │
      ▼
  Edit Fields  ──────────────────┐
      │                          │
      ├──► Append row in sheet   │  (paralelo)
      │          │               │
      │          ▼               │
      │       Switch            │
      │      /    |    \        │
      │     /     |     \       │
      │    /      |      \      │
      ▼   ▼      ▼       ▼     │
  Guardar     Send     Send    │
  en API   msg1/comprar msg2   │
                   msg3/default│
                               │
      ◄─────────────────────────┘
```

### Nodos

#### 1.1 Telegram Trigger

- **Tipo**: `n8n-nodes-base.telegramTrigger`
- **Propósito**: Escucha mensajes entrantes del bot de Telegram vía long-polling o webhook
- **Trigger**: Se activa con cualquier mensaje nuevo (`updates: ["message"]`)
- **Salida**: Objeto JSON completo de Telegram con `message`, `from`, `chat`, etc.
- **Credenciales**: `Telegram account` — el token del bot creado con @BotFather

#### 1.2 Edit Fields

- **Tipo**: `n8n-nodes-base.set` (typeVersion 3.4)
- **Propósito**: Extraer y renombrar campos del payload de Telegram para usarlos en los nodos siguientes
- **Outputs**:
  | Variable | Expresión | Descripción |
  |----------|-----------|-------------|
  | `mensaje` | `$json["message"]["text"]` | Texto del mensaje del usuario |
  | `user_id` | `$json["message"]["from"]["id"]` | ID numérico del usuario en Telegram |
  | `message_id` | `$json["message"]["message_id"]` | ID único del mensaje |

#### 1.3 Append row in sheet (Google Sheets)

- **Tipo**: `n8n-nodes-base.googleSheets` (typeVersion 4.7)
- **Propósito**: Persiste cada interacción en Google Sheets para tener un historial accesible desde cualquier lugar
- **Operación**: `append` — agrega una nueva fila al final
- **Columnas**:
  | Columna | Valor | Descripción |
  |---------|-------|-------------|
  | `user_id` | `$json["user_id"]` | ID del usuario en Telegram |
  | `mensaje` | `$json["mensaje"]` | Texto del mensaje |
  | `fecha` | `$now` | Timestamp actual de n8n |
- **Documento**: Google Sheets ID específico (la URL del sheet se configura en el nodo)
- **Credenciales**: `Google Sheets account` — OAuth2 con Google
- **⚠️ Consideraciones**: 
  - Google Sheets tiene un **límite de 10 requests por minuto** en la API gratuita
  - Si el flujo recibe muchos mensajes seguidos, puede fallar por rate limiting
  - La columna `fecha` usa la hora del servidor n8n, no la del mensaje de Telegram

#### 1.4 Guardar en API (HTTP Request)

- **Tipo**: `n8n-nodes-base.httpRequest` (typeVersion 4.2)
- **Propósito**: Envía la interacción al backend FastAPI para persistencia en BD + client lookup
- **Método**: `POST`
- **URL**: `http://localhost:8000/api/v1/interactions/`
- **Headers**:
  | Header | Valor | Propósito |
  |--------|-------|-----------|
  | `X-Api-Key` | `dev-api-key-123` | Autenticación (cambiar en producción) |
  | `X-Idempotency-Key` | `tg-{message_id}` | Evita duplicados si el mensaje se procesa más de una vez |
  | `Content-Type` | `application/json` | Formato del body |
- **Body**:
  ```json
  {
    "source": "telegram",
    "user": "{user_id}",
    "payload": "{\"text\": \"{mensaje}\", \"message_id\": {message_id}}"
  }
  ```
- **⚠️ Consideraciones**:
  - **Usar `127.0.0.1` en vez de `localhost`** en Windows por resolución IPv6 (n8n resuelve `localhost` como `::1` pero FastAPI escucha en IPv4)
  - Si el backend no responde, n8n no reintenta (no tiene `retryOnFail: true`)
  - La `X-Api-Key` está hardcodeada en este flujo — idealmente usar `$env.API_KEY`

#### 1.5 Switch (Router de Intenciones)

- **Tipo**: `n8n-nodes-base.switch` (typeVersion 3.4)
- **Propósito**: Clasifica el mensaje según su contenido para responder distinto
- **Reglas** (orden de evaluación):
  | Ruta | Condición | Respuesta |
  |------|-----------|-----------|
  | 0 (comprar) | `mensaje.toLowerCase()` contiene "comprar" | "Genial 🔥 decime qué producto querés y cantidad" |
  | 1 (precio) | `mensaje.toLowerCase()` contiene "precio" | "Te paso info 👇 ¿qué producto te interesa?" |
  | 2 (default) | `mensaje.toLowerCase()` NO contiene "comprar" | "Hola 👋 decime si querés ver productos o comprar" |
- **⚠️ Nota**: La ruta 2 es un catch-all para TODO lo que no sea "comprar". Esto significa que un mensaje como "gracias" también cae en default. **"precio" tiene prioridad sobre default** solo porque está antes en el switch.

#### 1.6 Send a text message (1, 2, 3)

- **Tipo**: `n8n-nodes-base.telegram`
- **Propósito**: Responder al usuario por Telegram con un mensaje de texto
- **Chat ID**: `$json["user_id"]` — responde siempre al mismo usuario que envió el mensaje
- **Texto**: Cada rama del Switch tiene su propio mensaje
- **Credenciales**: Mismas que el Telegram Trigger

---

## 2. Flujo Auxiliar: Telegram → API Interaction

> Archivo: `Docs/telegram-n8n-flow.json`  
> Propósito: Flujo más simple que solo recibe webhook y POSTea al backend

### Diagrama

```
Webhook (POST /telegram-webhook)
      │
      ▼
  Set Headers (X-Api-Key, X-Idempotency-Key, Content-Type)
      │
      ▼
  Build Request Body (source, user, payload)
      │
      ▼
  POST Interaction (HTTP Request a API)
      │
      ▼
  Respond to Webhook
```

### Nodos

#### 2.1 Telegram Webhook

- **Tipo**: `n8n-nodes-base.webhook`
- **Propósito**: Recibe el POST de Telegram (o de cualquier cliente HTTP)
- **Ruta**: `/telegram-webhook`
- **Método**: `POST`
- **responseData**: `lastNode` — devuelve la salida del último nodo como respuesta

#### 2.2 Set Headers

- **Tipo**: `n8n-nodes-base.set`
- **Propósito**: Prepara los headers que se enviarán al backend
- **Headers**:
  | Header | Valor | Descripción |
  |--------|-------|-------------|
  | `X-Api-Key` | `{{ $env.API_KEY }}` | Lee la API key de las variables de entorno de n8n |
  | `X-Idempotency-Key` | `{{ 'tg-' + $json.message.message_id }}` | Idempotencia basada en message_id |
  | `Content-Type` | `application/json` | Formato JSON |

#### 2.3 Build Request Body

- **Tipo**: `n8n-nodes-base.set`
- **Propósito**: Construye el body que se enviará a la API
- **Campos**:
  ```json
  {
    "source": "telegram",
    "user": "{message.from.id}",
    "payload": "{\"message_id\": {id}, \"text\": \"{text}\", \"chat_id\": {id}, \"date\": {timestamp}}"
  }
  ```
- `payload` se serializa con `JSON.stringify()` para cumplir con el campo Text de la BD

#### 2.4 POST Interaction

- **Tipo**: `n8n-nodes-base.httpRequest`
- **URL**: `{{ $env.API_URL }}/api/v1/interactions/` (con fallback a ngrok URL)
- **Headers**: toma los valores del nodo Set Headers
- **Opciones**: `retryOnFail: true`, `maxTries: 3`, `timeout: 10000ms`
- **⚠️ Consideraciones**:
  - Usa `$env.API_URL` como variable de entorno — configurar en n8n como `http://127.0.0.1:8000`
  - Timeout de 10 segundos, si el backend tarda más, la request falla

#### 2.5 Respond to Webhook

- **Tipo**: `n8n-nodes-base.respondToWebhook`
- **Propósito**: Devuelve la respuesta de la API como response del webhook
- **Respuesta**: `{{ $json }}` — el JSON que devolvió el backend

---

## 3. Consideraciones Generales

### Google Sheets

| Aspecto | Detalle |
|---------|---------|
| **Límites API** | 60 requests/minuto por usuario, 10/min en lecturas gratuitas |
| **Rate limiting** | Si el bot recibe ráfagas de mensajes, Google Sheets puede fallar |
| **Solución** | Agregar un nodo `Wait` entre el trigger y Google Sheets, o desacoplar con una cola |
| **Columnas** | No cambiar el nombre de las columnas en el sheet sin actualizar el nodo |
| **Autenticación** | OAuth2 — el token expira y n8n lo refresca automáticamente |

### Gmail (si se agrega en el futuro)

| Aspecto | Detalle |
|---------|---------|
| **Autenticación** | Requiere OAuth2 con Google Cloud Console |
| **Scopes necesarios** | `https://www.googleapis.com/auth/gmail.send` para enviar |
| **Límites** | 100 requests por 100 segundos por usuario |
| **n8n node** | `n8n-nodes-base.gmail` — soporta send, fetch, reply |
| **⚠️ Precaución** | Las credenciales de Gmail NO deben estar hardcodeadas en el JSON del flujo — usar credenciales de n8n |

### API (FastAPI Backend)

| Aspecto | Detalle |
|---------|---------|
| **URL local** | Usar `http://127.0.0.1:8000` en vez de `localhost` (Windows IPv6) |
| **API Key** | Configurar como variable de entorno en n8n (`$env.API_KEY`), no hardcodear |
| **Idempotencia** | Siempre enviar `X-Idempotency-Key` para evitar duplicados |
| **Timeouts** | El backend responde en <100ms, pero n8n tiene timeout default de 10s |
| **Disponibilidad** | Si el backend no corre, n8n igual procesa el flujo hasta el HTTP Request y falla |

### ngrok

| Aspecto | Detalle |
|---------|---------|
| **URL dinámica** | Cambia cada vez que reiniciás ngrok (excepto con plan pagado) |
| **Actualización** | Hay que desactivar/activar el webhook de Telegram o actualizar la URL en n8n |
| **Comando** | `ngrok http 5678` — expone n8n, NO el backend |
| **Alternativa** | Usar un VPS o tunnel persistente (bore, localtunnel) para URL fija |

### Telegram

| Aspecto | Detalle |
|---------|---------|
| **Token** | NO incluirlo en el JSON exportado — n8n lo guarda en sus credenciales |
| **Webhook vs polling** | n8n usa polling (Telegram Trigger) o webhook según configuración |
| **Rate limits** | Telegram permite ~30 mensajes/segundo a grupos, más a chats individuales |
| **drop_pending_updates** | Usar `deleteWebhook?drop_pending_updates=true` para limpiar mensajes acumulados |

### n8n Credentials (Seguridad)

| Servicio | Tipo de credencial | Recomendación |
|----------|-------------------|---------------|
| Telegram API | Token del bot | Guardar en n8n, NO en el JSON |
| Google Sheets | OAuth2 | Se refresca automáticamente |
| API Key del backend | Variable de entorno | Usar `$env.API_KEY` en n8n |

> ⚠️ **NUNCA** incluir tokens, API keys o contraseñas en los archivos JSON exportados.
> Por eso `Docs/*.json` está en `.gitignore`.
> Las credenciales se configuran directamente en la UI de n8n.
