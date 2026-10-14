## Why

El bot de Telegram permite comprar productos, pero el sistema no tiene modelo de venta ni identidad de persona más allá del `telegram_user_id` que vive aislado en los flujos n8n. No se puede responder "qué compró Juan el lunes", no hay tickets, y los módulos 1 (resumen comercial), 3 (ticket promedio), 4 (análisis temporal) y 5 (reportes) de la spec `Docs/Arreglos adicionales- posibles integraciones.md.txt` están bloqueados porque no existen datos de venta que consultar. Además no hay defensa anti-pedidos-falsos: sin estado de orden, cualquier pedido quedaría directamente "vendido".

## What Changes

- Nuevas tablas `sales` y `sale_items` (migración Alembic `0008`) con máquina de estados `PENDIENTE → CONFIRMADO → COMPLETADO` / `CANCELADO`; solo `CONFIRMADO` y `COMPLETADO` entran en métricas, tickets y estadísticas (antifraude por estado, no por login)
- Registro único de prospecto en el bot (nombre + apellido + teléfono, SIN password): crea o linkea un `Client` con `password_hash = NULL` (el modelo ya lo soporta)
- Nueva columna `clients.telegram_user_id` (nullable + unique) como identidad durable; extensión del mecanismo `clientLookup` existente con la clave `telegram_user_id`
- Email placeholder `tg{telegram_user_id}@telegram.local` en el registro para cumplir el `NOT NULL + UNIQUE` actual de `Client.email` (recomendación única con rationale en design.md)
- Nuevos endpoints de ventas: creación desde el bot (`X-API-Key` + `X-Idempotency-Key`), transiciones de estado (`JWT`), listado/detalle, y consulta de ticket "qué compró X el día D"
- Métricas de ventas `GET /api/v1/metrics/ventas` (ventas, ingresos, ticket promedio, serie temporal, top productos) + página de Ventas en el panel React
- Nuevas intenciones de ventas en el asistente administrativo (patrón existente de `AdminIntentRouter`/`AdminBotService`)
- Contrato de integración n8n documentado (endpoint, payload, headers): los flujos en `Docs/flujos/` NO se commitean (gitignored, credenciales reales)

## Capabilities

### New Capabilities
- `sales-management`: modelo de ventas e ítems, máquina de estados anti-fraude, creación desde bot, transiciones con JWT, consulta de ticket y consultas de ventas en el asistente
- `customer-registration`: registro único de prospecto en el bot (nombre/teléfono sin login), placeholder de email, identidad `telegram_user_id`

### Modified Capabilities
- `dashboard-metrics`: se AGREGAN requisitos de métricas de ventas (endpoint `/metrics/ventas`, serie temporal, top productos, página Ventas en React) — los requisitos existentes del dashboard de interacciones no cambian
- `interaction-history`: se AGREGA el requisito de resolución de cliente por `telegram_user_id` en `clientLookup` (además de email/telefono existentes)

## Impact

- **Backend — modelos/repos**: `backend/src/models/client.py` (columna `telegram_user_id`), nuevos `backend/src/models/sale.py` (`Sale`, `SaleItem`), nuevos repositories `sale_repo.py`, extensión de `client_repo.py` (nuevo `get_by_telegram_user_id`; `get_by_email`/`get_by_telefono` ya existen), `interaction_service.py` (resolución por `telegram_user_id`)
- **Backend — servicios**: nuevo `sale_service.py`, nuevo `registration_service.py`, `admin_intent_router.py` + `admin_bot_service.py` (intenciones de ventas)
- **Backend — API**: nuevo `backend/src/api/routes/sales.py`, `POST /api/v1/clients/register-bot`, `GET /api/v1/metrics/ventas`, registro en `main.py`; schemas nuevos `sale.py`, extensión de `schemas/interaction.py`
- **Migración**: Alembic `0008` (crear 2 tablas + 1 columna sobre `dev.db` con datos existentes — impacto y compatibilidad en design.md)
- **Frontend**: `salesService.js`, `VentasPage.jsx`, entrada de navegación, hooks; patrones existentes `StockPage`/`ProductTable`
- **n8n (externo)**: flujo de registro y "finalizar compra" deben apuntar a los nuevos endpoints — se documenta el contrato, los JSON no se commitean
- **Tests**: unit (services), API (routes), router de intenciones; base existente con `python run_tests.py`
- **Fuera de alcance de código**: Streamlit `dashboard/` queda como referencia de consultas; los módulos 2, 6, 7, 8 de la spec no se tocan
