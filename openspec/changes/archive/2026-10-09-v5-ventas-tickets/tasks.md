## 1. Migración Alembic `0008` — tablas de ventas + identidad Telegram

- [x] 1.1 Crear migración Alembic `0008_create_sales_tables.py` (`revision = '0008'`, `down_revision = '0007'`): `create_table sales` (id, cliente_id FK->clients, fecha server_default now, total, estado String(20) default 'PENDIENTE', idempotency_key String unique nullable, confirmado_por FK->clients nullable, updated_at nullable) y `create_table sale_items` (id, sale_id FK->sales ondelete CASCADE, product_id FK->products, cantidad INT, precio_unitario FLOAT) con índices
- [x] 1.2 Agregar a la misma migración `add_column clients.telegram_user_id` (String(32), nullable) + índice unique; en `downgrade` dropear tablas y columna en orden inverso
- [x] 1.3 Actualizar `backend/src/models/client.py` (`telegram_user_id`) y crear `backend/src/models/sale.py` (`Sale`, `SaleItem`); registrar en `backend/src/models/__init__.py`
- [x] 1.4 Ejecutar `alembic upgrade head` sobre `dev.db` y verificar: tablas creadas, columna presente, clientes existentes con `telegram_user_id = null`, `alembic current` = `0008`

## 2. Repositories de ventas y lookup por telegram

- [x] 2.1 Escribir tests de `backend/src/repositories/sale_repo.py`: constante `BASE_CONTABLE = ("CONFIRMADO", "COMPLETADO")`, `create` con items, `get_by_idempotency_key`, `list` con filtros estado/cliente_id/rango de fechas + paginación
- [x] 2.2 Implementar `backend/src/repositories/sale_repo.py` siguiendo el estilo de `interaction_repo.py`/`product_repo.py`
- [x] 2.3 Test + implement de `ClientRepository.get_by_telegram_user_id(valor)` en `backend/src/repositories/client_repo.py` (devuelve cliente o None)

## 3. Registro de prospecto (TDD)

- [x] 3.1 Tests de `backend/src/services/registration_service.py`: registro nuevo crea `Client` con `password_hash=None`, `role='user'`, `activo=True`, email placeholder `tg{id}@telegram.local`; segundo registro con mismo `telegram_user_id` devuelve el existente sin duplicar; registro con teléfono de cliente preexistente (sin columna) vincula y setea `telegram_user_id`; nombre de una sola palabra deja `apellido=''`
- [x] 3.2 Implementar `backend/src/services/registration_service.py` (usa `ClientRepository`, compone validación → persistencia, patrón de `client_service.py`)
- [x] 3.3 Tests API de `POST /api/v1/clients/register-bot` en `backend/tests/`: 201 en alta, 200 en re-registro idempotente, 401 sin `X-API-Key`, 422 sin campos requeridos
- [x] 3.4 Agregar el endpoint en `backend/src/api/routes/clients.py` con `Depends(verify_api_key)` + schema `RegisterBotRequest` en `backend/src/schemas/client.py`

## 4. `clientLookup` por `telegram_user_id` (TDD)

- [x] 4.1 Tests de `InteractionService.create`: con `clientLookup.telegram_user_id` que coincide linkea `clientId`; prioridad sobre `email`/`telefono` cuando ambos coinciden con clientes distintos; clave inexistente persiste `clientId = null` con 201; claves email/telefono existentes siguen funcionando igual
- [x] 4.2 Extender `ClientLookup` en `backend/src/schemas/interaction.py` con `telegram_user_id: Optional[str]` y la resolución PRIMERO en `backend/src/services/interaction_service.py:81-93`

## 5. Servicio de ventas y máquina de estados (TDD)

- [x] 5.1 Tests de `backend/src/services/sale_service.py`: `create_from_bot` calcula `total` server-side desde `Product.precio` (ignora totales/precios del payload), snapshot de precio en items, estado inicial `PENDIENTE`, idempotencia por `idempotency_key` (devuelve venta previa), 404 si el `telegram_user_id` no resuelve cliente, 400 si producto inactivo/inexistente
- [x] 5.2 Tests de transiciones: `PENDIENTE→CONFIRMADO` setea `confirmado_por`, `CONFIRMADO→COMPLETADO`, `PENDIENTE/CONFIRMADO→CANCELADO`, transiciones inválidas lanzan excepción de dominio (→ 409 en API)
- [x] 5.3 Tests de queries contables: helper de base contable excluye `PENDIENTE`/`CANCELADO` de listado de métricas y de ticket
- [x] 5.4 Implementar `backend/src/services/sale_service.py` (excepciones de dominio al estilo de `interaction_service.py`: `ValidationError`, `TransitionError`, `IdempotencyConflict`)

## 6. API de ventas

- [x] 6.1 Crear `backend/src/api/routes/sales.py` + `backend/src/schemas/sale.py`: `POST /` (`verify_api_key` + header `X-Idempotency-Key`, 201/200/404/400/409), `GET /` (JWT, filtros + paginación), `GET /{sale_id}` (JWT, detalle con items y nombre de cliente), `POST /{sale_id}/confirm|complete|cancel` (JWT, 409 en transición inválida) — registrar `GET /ticket` y `GET /` ANTES de `GET /{sale_id}`
- [x] 6.2 `GET /api/v1/sales/ticket?cliente=&fecha=` (JWT): resolución `ILIKE` de cliente, ventas de la fecha en base contable con items; `200` con lista vacía si no hay datos
- [x] 6.3 Registrar el router en `backend/src/main.py` con prefix `/api/v1/sales`
- [x] 6.4 Tests API de `backend/tests/test_sales_api.py` (patrón `client` fixture existente): creación con API-Key, idempotencia, 401 sin key, transiciones JWT, 409, ticket, listado filtrado

## 7. Métricas de ventas (módulos 1/3/4)

- [x] 7.1 Tests de `GET /api/v1/metrics/ventas`: `summary` (ventas, ingresos, ticketPromedio, vsPeriodoAnterior) solo con base contable; `serieDiaria` con 0-fill de días vacíos; `topProductos` top 5; `porHorario`; default últimos 30 días; parámetros `desde`/`hasta`
- [x] 7.2 Implementar `GET /ventas` en `backend/src/api/routes/metrics.py` (mismo estilo que `/dashboard`, `Depends(get_current_user)`)
- [x] 7.3 Tests API en `backend/tests/` cubriendo: PENDIENTE/CANCELADO no cuentan, ticketPromedio = 0 sin ventas

## 8. Asistente administrativo — intenciones de ventas

- [x] 8.1 Tests de `AdminIntentRouter` (`backend/tests/`): detecta `ventas-hoy` ("cuántas ventas hubo hoy", "ventas del día") y `ticket-cliente` ("qué compró María ayer", "ticket de María del 01-10-2026"); textos sin ventas no caen en otra intención existente
- [x] 8.2 Agregar los patrones al `PATTERNS` de `backend/src/services/admin_bot/admin_intent_router.py` + actualizar el fallback `_no_entendido`
- [x] 8.3 Tests de `AdminBotService`: handler `ventas-hoy` cuenta solo base contable; handler `ticket-cliente` extrae fecha (`hoy`/`ayer`/`dd-mm-yyyy`) y nombre (`ILIKE`) y lista productos/cantidades/total; sin datos responde "no se encontraron ventas"
- [x] 8.4 Implementar los handlers en `backend/src/services/admin_bot/admin_bot_service.py` reusando `SaleService`/queries (datos reales, patrón existente)

## 9. Frontend — página Ventas

- [x] 9.1 Crear `frontend/src/services/salesService.js`: `listSales`, `getSale`, `confirmSale`, `completeSale`, `cancelSale`, `searchTicket`, `getVentasMetrics` (axios instance existente)
- [x] 9.2 Crear `frontend/src/pages/VentasPage.jsx`: cards (`MetricCard`) de ventas/ingresos/ticket promedio/variancia, gráfico de `serieDiaria`, tabla de ventas con `StatusBadge` + acciones confirmar/completar/cancelar (toasts sonner, patrón `ProductsPage`)
- [x] 9.3 Agregar buscador de tickets (cliente + fecha) que consume `searchTicket` y muestra cliente + items
- [x] 9.4 Registrar la página en `frontend/src/config/navigation.js` y en el router de `App.jsx`; reusar layout/gate admin existente
- [x] 9.5 Tests de frontend según convención existente (`*.test.jsx` con vitest): render de cards, acciones de transición, estado de error

## 10. Contrato n8n y verificación final

- [x] 10.1 Documentar el contrato de integración en `Docs/` (archivo nuevo): `POST /api/v1/clients/register-bot` y `POST /api/v1/sales/` — endpoint, payload exacto, headers (`X-API-Key`, `X-Idempotency-Key`), códigos de respuesta; aclarar que los JSON de `Docs/flujos/` NO se commitean (gitignored, credenciales reales)
- [x] 10.2 Correr la suite completa con `python run_tests.py` — todo verde sin regresiones (base existente)
- [x] 10.3 Smoke manual dev: registrar prospecto → crear venta PENDIENTE → confirmar desde panel → verificar que `GET /metrics/ventas` y el ticket la incluyen, y que una PENDIENTE/CANCELADA no aparece
- [x] 10.4 Revisar que `alembic downgrade -1` + `upgrade head` funciona sobre `dev.db` (rollback real)
