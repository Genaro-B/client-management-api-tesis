## Context

El sistema hoy tiene: `Client` (con `password_hash` nullable para admins y `email NOT NULL UNIQUE`), `Product`, `Interaction` con `clientLookup` (email/telefono) e idempotencia por header, migraciones Alembic secuenciales (`0007` es la última), FastAPI con capas repository/service/router, JWT (`get_current_user` / `require_admin`) y `X-API-Key` (`verify_api_key`) ya existentes. El bot de compras corre en n8n (flujo en `Docs/flujos/`, gitignored por credenciales reales) y hoy solo interactúa con `POST /api/v1/interactions`; no crea ninguna entidad de venta. El panel React (`frontend/src/`) tiene patrones de página/tabla establecidos (`ProductsPage`, `ProductTable`); el dashboard Streamlit (`dashboard/`) es referencia de consultas, no se modifica.

Falta la pieza central: identidad de persona (quién compra) y el registro de la venta (qué, cuándo, cuánto, en qué estado). Sin eso, los módulos 1/3/4/5 de la spec de dashboard no tienen datos.

Restricciones duras del producto (ya decididas, no se reabren): identidad = registro de prospecto NUNCA login; antifraude = estado de orden confirmado por un humano, NO autenticación del comprador; tablas nuevas tipo sale + items; el `dev.db` de desarrollo tiene datos y la migración debe ser backwards compatible.

## Goals / Non-Goals

**Goals:**
- Modelo `sales` + `sale_items` con máquina de estados `PENDIENTE → CONFIRMADO → COMPLETADO` / `CANCELADO`
- Identidad durable: registro único de prospecto en el bot (nombre + apellido + teléfono, sin password) que crea/linkea un `Client` con `password_hash = NULL` y `telegram_user_id` persistido
- Atribución: interacciones y ventas se vinculan al `Client` resuelto (extensión de `clientLookup`)
- Antifraude: todo reporte/ticket/estadística cuenta SOLO `CONFIRMADO` y `COMPLETADO`
- API de ventas con frontera de autenticación clara: escritura del bot con `X-API-Key` (+ idempotencia), transiciones del panel con `JWT`
- Consulta de ticket "qué compró X el día D" (endpoint + intención del asistente)
- Métricas de ventas para los módulos 1/3/4 (resumen, ticket promedio, temporal, top productos) y página Ventas en React
- Contrato de integración n8n documentado (endpoint, payload, headers)
- Migración Alembic `0008` segura sobre `dev.db` con datos + plan de rollback

**Non-Goals:**
- NO login/contraseña/otp del comprador — el registro nunca genera sesión
- NO descuento automático de stock al confirmar/completar una venta (resuelto: NO en v5; pasa a un `v6-stock-movimientos`)
- NO pasarela de pagos, facturación, ni cálculo de impuestos
- NO modificar los flujos n8n en este cambio (solo se define el contrato que deben cumplir)
- NO tocar el dashboard Streamlit (`dashboard/`) ni los módulos 2/6/7/8 de la spec
- NO sistema de roles nuevo: las transiciones de venta usan el gate `require_admin` existente (resuelto)

## Decisions

### 1. Email del prospecto: placeholder `tg{telegram_user_id}@telegram.local` (NO relajar el nullable)
**Decisión**: al registrar un prospecto desde el bot se genera `email = f"tg{telegram_user_id}@telegram.local"`.

- **Por qué**: `Client.email` es `NOT NULL + UNIQUE` con índice único (modelo y migración 0001). El placeholder mantiene el invariante intacto: cero migración sobre la columna, cero cambios en código que asume email no-nulo (`clientLookup` por email, login del panel, listados). El dominio `.local` es auto-documentable (nadie confunde un email real con uno generado) y se puede excluir con un filtro en exportaciones/mostrar "sin email" en el panel.
- **Alternativa descartada**: relajar `email` a nullable exige migración `ALTER TABLE` sobre una columna con índice unique, y obliga a revisar cada consumidor de `client.email` por `None` — más riesgo y más diff por un dato que jamás se usa en el flujo de prospecto.
- **Garantía**: el placeholder usa el `telegram_user_id`, que es único por usuario de Telegram → la unicidad del índice no puede colisionar.

### 2. Identidad: columna `clients.telegram_user_id` + lookup por la columna
**Decisión**: nueva columna `telegram_user_id = Column(String(32), nullable=True, unique=True, index=True)` en `Client`, con método nuevo `ClientRepository.get_by_telegram_user_id`, y extensión de `clientLookup` con la clave `telegram_user_id`.

- **Por qué**: es la única identidad estable que el bot posee (el teléfono depende de cómo el usuario lo tipea: `+54 9 11 5555-5555` vs `1155555555` — normalización frágil). Con la columna, el linkage registro→interacción→venta es O(1) y determinístico; el teléfono sigue siendo un fallback útil para clientes creados antes del cambio.
- **Implementación**:
  - `ClientRepository` suma `get_by_telegram_user_id(valor)` (los existentes `get_by_email` y `get_by_telefono` no se tocan).
  - `ClientLookup` (schema) y `InteractionService.create` aceptan la clave nueva, resuelta PRIMERO (antes de email/telefono).
  - Registro de clientes creados ANTES de este cambio: el registro desde el bot los detecta por teléfono y setea la columna (link, no duplicate).
- **Alternativa descartada**: resolver todo por teléfono exige normalización (falsos negativos por formatos) y no sirve si el usuario escribe el número distinto al registrado.

### 3. Antifraude = máquina de estados de la orden, con filtro único en la capa de query
**Decisión**: `estado` en `String(20)` con valores `PENDIENTE | CONFIRMADO | COMPLETADO | CANCELADO` (default `PENDIENTE`). Toda query de métricas/reportes/tickets pasa por un helper único `SaleRepository.BASE_CONTABLE = ("CONFIRMADO", "COMPLETADO")`.

- **Por qué**: es la defensa pedida sin tocar autenticación: el bot nace en `PENDIENTE`, solo un humano del panel (JWT) lo confirma, y lo no confirmado/cancelado jamás entra en números. Centralizar el filtro en un solo lugar evita el clásico bug de que un endpoint nuevo olvide el filtro y conté pedidos falsos.
- **Transiciones válidas**: `PENDIENTE → CONFIRMADO | CANCELADO`; `CONFIRMADO → COMPLETADO | CANCELADO`; `COMPLETADO` es terminal. Transición inválida → `409`.
- **Alternativa descartada**: login del comprador (rechazado por decisión de producto) o marcar "confirmado" al llegar el pedido (no defiende contra nada).

### 4. Shape de las tablas (mínimo, con precios snapshot)
```text
sales       (id, cliente_id FK->clients, fecha timestamptz default now, total float,
             estado String(20) default PENDIENTE, idempotency_key String unique nullable,
             confirmado_por INT nullable FK->clients, updated_at onupdate)
sale_items  (id, sale_id FK->sales cascade, product_id FK->products,
             cantidad INT, precio_unitario float)
```
- **`precio_unitario` es snapshot** del `Product.precio` al momento de crear la venta: si mañana cambia el precio, el histórico y el ticket no mienten.
- **`total` lo calcula SIEMPRE el servidor** (`Σ cantidad × precio_unitario`) — el cliente (bot) manda `product_id + cantidad`, jamás precios ni totales. Eso también es anti-fraude.
- **`idempotency_key`** replica el patrón de `interactions` (header `X-Idempotency-Key` en la creación desde n8n, que reintenta).
- FK con `ON DELETE RESTRICT` para `clients`/`products` (el soft-delete `activo` ya existe; no se borran filas referenciadas). `sale_items` en cascade.
- **Naming**: clases `Sale`/`SaleItem`, tablas `sales`/`sale_items` — igual que `Client`/`clients`, columnas en español según convención existente.

### 5. Frontera de autenticación de la API de ventas
| Operación | Endpoint | Auth |
|---|---|---|
| Crear venta desde el bot | `POST /api/v1/sales/` | `X-API-Key` + `X-Idempotency-Key` |
| Registro de prospecto | `POST /api/v1/clients/register-bot` | `X-API-Key` |
| Confirmar / completar / cancelar | `POST /api/v1/sales/{id}/confirm\|complete\|cancel` | `JWT` + `require_admin` |
| Listado / detalle / ticket | `GET /api/v1/sales/`, `/sales/{id}`, `/sales/ticket` | `JWT` |
| Métricas de ventas | `GET /api/v1/metrics/ventas` | `JWT` (igual que `/metrics/dashboard`) |

- **Por qué**: espeja exactamente lo que ya existe (`interactions` POST con API-Key, GETs con JWT) — cero conceptos nuevos. El bot nunca tiene JWT (no hay sesión de comprador); el panel nunca usa API-Key.
- **Detalle de rutas**: registrar `GET /sales/ticket` y `GET /sales/` ANTES de `GET /sales/{sale_id}` en el `APIRouter` para que FastAPI no capture `ticket` como `sale_id`.

### 6. Consulta de ticket: endpoint dedicado + intención del asistente
- **Endpoint**: `GET /api/v1/sales/ticket?cliente=<texto>&fecha=<YYYY-MM-DD>` → `{cliente, ventas: [{id, fecha, total, estado, items:[{producto, cantidad, precio_unitario}]}]}`. Búsqueda de cliente por `ILIKE` sobre nombre/apellido; respuesta vacía = 200 con lista vacía.
- **Asistente**: nuevas intenciones `ventas-hoy` y `ticket-cliente` siguiendo el patrón literal de `AdminIntentRouter` (keywords) + `AdminBotService` (datos reales). Para `ticket-cliente`, extracción mínima y determinista: fecha en `hoy`/`ayer`/`dd-mm-yyyy` + nombre por coincidencia contra `clients` (una sola query `ILIKE`). Sin IA, consistente con la filosofía del router.
- **Por qué endpoint dedicado además del intent**: el panel React necesita el dato estructurado (no texto armado), y el endpoint sirve a ambos consumidores — el intent es una capa de fachada textual sobre el mismo service.

### 7. Métricas de ventas: endpoint nuevo, no extender `/metrics/dashboard`
**Decisión**: `GET /api/v1/metrics/ventas?desde=&hasta=` devolviendo `{summary:{ventas, ingresos, ticketPromedio, vsPeriodoAnterior}, serieDiaria:[{fecha, ventas, ingresos}], topProductos:[...], porHorario:[...]}`.

- **Por qué**: el payload actual del dashboard ya es grande y estable (lo consumen specs archivadas); mezclar módulos de interacción con ventas en un mismo response los acopla y los rompe si uno cambia. Endpoints separados = despliegue y testing independientes.
- **Reglas**: solo `BASE_CONTABLE`; `ticketPromedio = ingresos / cantidad de ventas` (0 si no hay ventas); `serieDiaria` con días sin ventas en `0` (mismo criterio de 0-fill que `interactionsTimeline`); comparación con el período inmediatamente anterior de igual duración.
- **Streamlit**: `dashboard/queries.py` queda como referencia de cómo se surfacean los datos; no se modifica.

### 8. Frontend: página `VentasPage` siguiendo patrones existentes
- `frontend/src/services/salesService.js` (list/get/confirm/complete/cancel/ticket/metrics con el axios instance existente), `pages/VentasPage.jsx` (cards de resumen + gráficos + tabla de ventas con botones de confirmación + buscador de tickets), entrada en `config/navigation.js`. Reusa `MetricCard`, `StatusBadge`, toasts de sonner y el gate admin de `useAuth` — mismo shape que `ProductsPage`.
- **Confirmación de venta desde el panel**: fila con estado + botón "Confirmar" (y "Completar"/"Cancelar") que llama al endpoint JWT correspondiente; los detalles de layout fino quedan en tasks.

### 9. Migración `0008` y backwards compatibility (governance HIGH)
- `0008_create_sales_tables.py`: `create_table sales`, `create_table sale_items`, `add_column clients.telegram_user_id` (nullable + unique index). Operaciones 100% aditivas: NO se altera ninguna columna existente, NO se backfill obligatorio (los `Client` viejos quedan con `telegram_user_id = NULL`, que SQLite/unique tolera).
- `dev.db` con datos: las tablas nuevas nacen vacías; ningún cliente/producto existente se toca; los flujos actuales (interacciones, productos, login admin) siguen funcionando sin cambios.
- **Rollback**: `alembic downgrade -1` dropea las 2 tablas y la columna nueva; no hay pérdida de datos porque las tablas son nuevas.
- **Riesgo operativo**: los clientes registrados ANTES de este cambio no tienen `telegram_user_id`; el registro desde el bot los detecta por teléfono y setea la columna (link, no duplicate). Ver escenario en specs.

## Risks / Trade-offs

- [Clientes duplicados si el usuario se registra dos veces con distinto teléfono] → la resolución por `telegram_user_id` (única) tiene prioridad sobre el teléfono; el registro idempotente devuelve el `Client` ya linkeado si la columna ya existe.
- [Alguien agrega un endpoint de métricas y olvida el filtro `BASE_CONTABLE`] → el filtro vive en un solo helper del repository; code review + tests de regresión que insertan `PENDIENTE`/`CANCELADO` y verifican que no aparecen.
- [Precio del producto cambia entre creación y confirmación] → snapshot en `precio_unitario`; la venta no lee `Product.precio` al confirmar.
- [El bot n8n reintenta y crea ventas dobles] → `X-Idempotency-Key` con índice unique, devuelve la venta existente (patrón ya probado en interacciones).
- [Columna `confirmado_por` apunta a un client borrado lógicamente] → es nullable y solo auditiva; el soft-delete no elimina filas.
- [Campos NOT NULL de `Client` (`apellido`) no encajan con "solo nombre"] → el contrato de registro pide `nombre` y `apellido` (n8n pregunta "nombre y apellido" y separa en el primer espacio; si hay una sola palabra, `apellido` queda como string vacío — permitido, es NOT NULL pero admite `''`). Decisión de contrato, documentada en specs.
- [Flujos n8n no versionados: el backend puede cambiar y el flujo romperse en silencio] → el contrato queda escrito en specs/tasks (endpoint, payload, headers); la verificación del flujo es manual en la demo.

## Migration Plan

1. Crear modelo `Sale`/`SaleItem` + columna `telegram_user_id` en `Client`
2. `alembic revision` (`0008`, `down_revision = '0007'`) → `alembic upgrade head` sobre `dev.db`
3. Verificar: tablas creadas, columna presente, `alembic current` = `0008`, tests existentes verdes (base `python run_tests.py`)
4. Deploy dev/demo: sin paso de backfill; datos existentes intactos
5. **Rollback**: `alembic downgrade -1` (dropea tablas nuevas y columna); el código nuevo se revierte con el commit correspondiente

## Decisiones del usuario (cerradas)

1. **Stock**: NO se descarta stock en v5. Pasa a un change `v6-stock-movimientos` con `stock_movements`. [Confirmado por el usuario]
2. **Transiciones de venta**: `confirm/complete/cancel` exigen `require_admin` (governance CRITICAL del dominio); los GETs quedan para cualquier usuario logueado. [Confirmado por el usuario]
3. **Fecha**: el ticket y las métricas se resuelven por `fecha` de creación de la venta (momento de la compra), no por fecha de confirmación. [Confirmado por el usuario]
