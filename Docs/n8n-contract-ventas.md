# Contrato de integración n8n ↔ API (Ventas)

Documento de contrato para los flujos de n8n que crean **prospectos** y **ventas**
a través de la API. Es solo documentación: no se modifican los JSON de n8n.

- **Base URL (dev):** `http://localhost:8000`
- **Autenticación:** header `X-Api-Key` (los flujos de bot NO usan JWT).
- **Formato:** JSON (`Content-Type: application/json`).

---

## 1. `POST /api/v1/clients/register-bot`

Registra (o vincula) un prospecto de Telegram. Sin login: crea un `Client`
con `password_hash = NULL` y email placeholder `tg{telegram_user_id}@telegram.local`.

### Headers

| Header      | Requerido | Valor                          |
| ----------- | --------- | ------------------------------ |
| `X-Api-Key` | Sí        | API key del entorno (`API_KEY`) |

### Payload

```json
{
  "telegram_user_id": "123456789",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+5491122334455"
}
```

| Campo              | Tipo   | Requerido | Notas                                                        |
| ------------------ | ------ | --------- | ------------------------------------------------------------ |
| `telegram_user_id` | string | Sí        | Identidad durable del usuario en Telegram.                   |
| `nombre`           | string | Sí        | Primer nombre.                                               |
| `apellido`         | string | No ("" )  | Si el usuario tiene una sola palabra, enviar `""`.           |
| `telefono`         | string | No        | Si coincide con un cliente previo, se **vincula** (no duplica). |

### Respuestas

| Código | Cuándo                                                        |
| ------ | ------------------------------------------------------------- |
| `201`  | Alta nueva del prospecto.                                     |
| `200`  | Ya existía (mismo `telegram_user_id`) → **idempotente**.      |
| `401`  | Falta o no coincide `X-Api-Key`.                              |
| `422`  | Falta `telegram_user_id` o `nombre`.                          |

Respuesta (`200`/`201`):

```json
{
  "id": 42,
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+5491122334455",
  "email": "tg123456789@telegram.local",
  "telegram_user_id": "123456789",
  "role": "user",
  "activo": true
}
```

---

## 2. `POST /api/v1/sales/`

Crea una venta en estado `PENDIENTE` (la confirma un humano desde el panel).
El **total lo calcula el servidor** (Σ `cantidad × precio_unitario`): el payload
NUNCA envía precios ni total.

### Headers

| Header              | Requerido | Valor                                             |
| ------------------- | --------- | ------------------------------------------------- |
| `X-Api-Key`         | Sí        | API key del entorno.                              |
| `X-Idempotency-Key` | Recomendado | Clave única del evento (evita duplicados por reintentos). |

### Payload

```json
{
  "telegram_user_id": "123456789",
  "items": [
    { "product_id": 7, "cantidad": 2 },
    { "product_id": 9, "cantidad": 1 }
  ]
}
```

| Campo              | Tipo   | Requerido | Notas                                                          |
| ------------------ | ------ | --------- | -------------------------------------------------------------- |
| `telegram_user_id` | string | Sí¹       | Resuelve el cliente a atribuir la venta.                       |
| `cliente_id`       | int    | Sí¹       | Alternativa al `telegram_user_id` (uso interno/panel).         |
| `items`            | array  | Sí        | Al menos 1 ítem.                                                |
| `items[].product_id` | int  | Sí        | Producto del catálogo.                                          |
| `items[].cantidad`  | int   | Sí        | `> 0`.                                                          |

¹ Se requiere uno de los dos: `telegram_user_id` **o** `cliente_id`.

### Respuestas

| Código | Cuándo                                                        |
| ------ | ------------------------------------------------------------- |
| `201`  | Venta creada (`PENDIENTE`).                                   |
| `200`  | Ya existía esa `X-Idempotency-Key` → devuelve la venta previa.|
| `400`  | Producto inexistente/inactivo o `items` vacío.                |
| `401`  | Falta o no coincide `X-Api-Key`.                              |
| `404`  | El `telegram_user_id`/`cliente_id` no resuelve un cliente.    |
| `422`  | Payload inválido (falta `items`, `cantidad <= 0`, etc.).      |

Respuesta (`200`/`201`):

```json
{
  "id": 101,
  "cliente_id": 42,
  "cliente_nombre": "Juan",
  "fecha": "2026-10-09T14:30:00",
  "total": 250.0,
  "estado": "PENDIENTE",
  "idempotency_key": "tg-123456789-1712345678",
  "confirmado_por": null,
  "items": [
    { "id": 1, "product_id": 7, "producto_nombre": "Widget", "cantidad": 2, "precio_unitario": 100.0 }
  ]
}
```

---

## 3. Endpoints del panel (referencia)

Estos NO los consumen los flujos de n8n (usan JWT del panel):

| Método | Endpoint                                   | Auth  |
| ------ | ------------------------------------------ | ----- |
| GET    | `/api/v1/sales/`                           | JWT   |
| GET    | `/api/v1/sales/ticket?cliente=&fecha=`     | JWT   |
| GET    | `/api/v1/sales/{sale_id}`                  | JWT   |
| POST   | `/api/v1/sales/{sale_id}/confirm`          | JWT admin |
| POST   | `/api/v1/sales/{sale_id}/complete`         | JWT admin |
| POST   | `/api/v1/sales/{sale_id}/cancel`           | JWT admin |
| GET    | `/api/v1/metrics/ventas`                   | JWT   |

Estados de venta: `PENDIENTE → CONFIRMADO → COMPLETADO`; `PENDIENTE|CONFIRMADO → CANCELADO`.
Solo `CONFIRMADO` y `COMPLETADO` cuentan en métricas y tickets (base contable).

---

## 4. Nota de seguridad sobre los flujos JSON

Los archivos de flujos (`Docs/flujos/**/*.json`) contienen credenciales reales
(API keys, tokens de n8n/Telegram) y **no deberían versionarse**.

**Estado verificado del repositorio (no asumido):** al momento de escribir este
documento esos JSON **sí están trackeados** por git:

```
git ls-files Docs | grep '\.json$'
Docs/flujos/Actual/Sistema de Automatizacion v2 - Simple.json
Docs/flujos/Actual/v2-flujo-mejorado.json
Docs/flujos/telegram-n8n-flow.json
```

La regla actual de `.gitignore` (`Docs/*.json`) **solo** cubre el nivel superior
de `Docs/`, no los subdirectorios, por lo que NO ignora `Docs/flujos/`. Para
excluirlos de verdad habría que:

1. Ampliar la regla a `Docs/flujos/**/*.json` (o `Docs/**/*.json`).
2. `git rm --cached` de los JSON ya trackeados.
3. Rotar cualquier credencial que ya haya quedado en el historial.

> Pendiente de decisión del dueño del proyecto: no se tocó `.gitignore` ni los
> JSON en esta iteración (fuera de alcance del cambio `v5-ventas-tickets`).
