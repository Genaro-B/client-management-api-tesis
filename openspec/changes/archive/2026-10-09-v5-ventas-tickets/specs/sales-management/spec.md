## ADDED Requirements

### Requirement: Modelo de venta con ítems y precios snapshot

El sistema SHALL persistir las ventas en las tablas `sales` y `sale_items`. Cada `sale` SHALL tener `cliente_id` (FK a `clients`), `fecha` (default `now`), `total`, `estado`, `idempotency_key` (unique, nullable) y `confirmado_por` (nullable). Cada `sale_item` SHALL tener `sale_id` (FK con cascade), `product_id` (FK), `cantidad` y `precio_unitario`.

- `precio_unitario` SHALL ser el snapshot de `Product.precio` al momento de crear la venta; posteriores cambios de precio del producto NO modifican ventas ya creadas.
- `total` SHALL calcularse SIEMPRE en el servidor como `Σ (cantidad × precio_unitario)`; el cliente nunca envía precios ni totales.

#### Scenario: Creación con precios tomados del catálogo
- **WHEN** se crea una venta con items `[{product_id: 1, cantidad: 2}]` y el producto 1 tiene precio 100
- **THEN** cada `sale_item` queda con `precio_unitario = 100` y la venta con `total = 200`

#### Scenario: Cambio de precio posterior no altera la venta
- **WHEN** existe una venta creada y luego el precio del producto sube a 150
- **THEN** el `precio_unitario` de la venta y su `total` siguen siendo los originales

#### Scenario: El total lo calcula el servidor
- **WHEN** el payload de creación incluye un campo `total` o `precio` enviados por el cliente
- **THEN** el sistema ignora esos campos y responde con el `total` calculado a partir de `Product.precio`

### Requirement: Máquina de estados de la venta (antifraude)

Las ventas SHALL nacer en estado `PENDIENTE` y transicionar solo por las rutas válidas: `PENDIENTE → CONFIRMADO | CANCELADO`, `CONFIRMADO → COMPLETADO | CANCELADO`. `COMPLETADO` SHALL ser terminal. Cualquier otra transición SHALL responder `409`.

- Solo un usuario autenticado con JWT (panel) SHALL poder ejecutar transiciones; el bot jamás crea ventas confirmadas.
- Al confirmar/completar, el sistema SHALL registrar `confirmado_por` con el `id` del usuario JWT.

#### Scenario: Venta creada desde el bot queda PENDIENTE
- **WHEN** el bot envía `POST /api/v1/sales/` con API-Key válida
- **THEN** la venta se persiste con `estado = "PENDIENTE"` y `confirmado_por = null`

#### Scenario: Confirmación exitosa
- **WHEN** un usuario JWT envía `POST /api/v1/sales/{id}/confirm` sobre una venta `PENDIENTE`
- **THEN** el estado pasa a `CONFIRMADO` y `confirmado_por` queda seteado con el id del usuario

#### Scenario: Transición inválida responde conflicto
- **WHEN** se envía `POST /api/v1/sales/{id}/confirm` sobre una venta `CANCELADO` o `COMPLETADO`
- **THEN** la respuesta tiene status 409 y el estado no cambia

#### Scenario: Cancelación desde PENDIENTE y desde CONFIRMADO
- **WHEN** se envía `POST /api/v1/sales/{id}/cancel` sobre una venta `PENDIENTE` o `CONFIRMADO`
- **THEN** el estado pasa a `CANCELADO` y la venta queda excluida de toda métrica

### Requirement: Creación de venta desde el bot con idempotencia

El sistema SHALL exponer `POST /api/v1/sales/` protegido con header `X-API-Key`, aceptando `X-Idempotency-Key` opcional. El payload SHALL identificar al cliente por `telegram_user_id` (preferente) o `cliente_id`, y llevar `items: [{product_id, cantidad}]`.

- Si el `X-Idempotency-Key` ya existe, el endpoint SHALL devolver la venta previa (status 200) en lugar de duplicar.
- Si el `telegram_user_id` no corresponde a un cliente registrado, el endpoint SHALL responder `404`.
- Si un `product_id` no existe o está inactivo, SHALL responder `400`.

#### Scenario: Venta idempotente ante reintentos de n8n
- **WHEN** el bot envía dos veces la misma creación con el mismo `X-Idempotency-Key`
- **THEN** existe una única venta y la segunda respuesta devuelve la venta creada previamente

#### Scenario: Cliente no registrado
- **WHEN** se envía una venta con un `telegram_user_id` sin cliente vinculado
- **THEN** la respuesta tiene status 404 y no se crea ninguna venta

#### Scenario: Sin API-Key
- **WHEN** se envía `POST /api/v1/sales/` sin header `X-API-Key`
- **THEN** la respuesta tiene status 401

### Requirement: Operaciones de consulta y transición con JWT

El sistema SHALL exponer `GET /api/v1/sales/` (listado con filtros `estado`, `cliente_id`, `fecha_desde`, `fecha_hasta` y paginación), `GET /api/v1/sales/{id}` (detalle con items) y los endpoints de transición `POST /api/v1/sales/{id}/confirm`, `/complete` y `/cancel` — todos protegidos con JWT (`get_current_user`).

- La ruta `GET /api/v1/sales/ticket` SHALL registrarse ANTES de `GET /api/v1/sales/{sale_id}` en el router para evitar capturas indebidas.

#### Scenario: Listado filtrado por estado
- **WHEN** se hace GET a `/api/v1/sales?estado=PENDIENTE` con JWT
- **THEN** la respuesta contiene solo ventas `PENDIENTE` con su total

#### Scenario: Detalle con items
- **WHEN** se hace GET a `/api/v1/sales/{id}` con JWT
- **THEN** la respuesta incluye datos de la venta, nombre del cliente y la lista de items con producto, cantidad y precio_unitario

#### Scenario: Acceso sin JWT
- **WHEN** se llama cualquier endpoint de este requisito sin `Authorization: Bearer`
- **THEN** la respuesta tiene status 401

### Requirement: Atribución de la venta al cliente registrado

La creación de la venta SHALL resolver el `cliente_id` con prioridad: `telegram_user_id` → `cliente_id` explícito. La venta SHALL quedar siempre vinculada a un `Client` existente (nunca huérfana).

#### Scenario: Resolución por telegram_user_id
- **WHEN** se crea una venta con `telegram_user_id: "12345"` y el cliente con esa columna existe
- **THEN** la venta queda con `cliente_id` igual al id de ese cliente

#### Scenario: Sin identidad resoluble no se crea la venta
- **WHEN** el payload no trae `telegram_user_id` válido ni `cliente_id`
- **THEN** la respuesta tiene status 404 y no se persiste ninguna venta

### Requirement: Reglas de métricas de ventas (base contable)

Toda query de métricas, reportes y tickets de ventas SHALL filtrar por `estado IN ("CONFIRMADO", "COMPLETADO")` usando un único helper compartido (`SaleRepository.BASE_CONTABLE`). Las ventas `PENDIENTE` y `CANCELADO` SHALL estar excluidas de todo número.

#### Scenario: Pedidos falsos no contaminan las métricas
- **WHEN** existen 3 ventas `PENDIENTE` y 2 ventas `CONFIRMADO`
- **THEN** el conteo de ventas de cualquier métrica es 2

#### Scenario: Ventas canceladas excluidas
- **WHEN** una venta pasa de `CONFIRMADO` a `CANCELADO`
- **THEN** deja de contar en ingresos, ticket promedio y series temporales

### Requirement: Consulta de ticket por cliente y fecha

El sistema SHALL exponer `GET /api/v1/sales/ticket?cliente=<texto>&fecha=<YYYY-MM-DD>` (JWT) que devuelva el cliente resuelto y las ventas de ese día con sus items.

- El cliente SHALL resolverse por coincidencia `ILIKE` sobre `nombre`/`apellido`; sin coincidencias → `200` con lista vacía.
- Solo ventas de la base contable (CONFIRMADO/COMPLETADO) y de la fecha indicada SHALL aparecer.

#### Scenario: Ticket completo
- **WHEN** se consulta `?cliente=maria&fecha=2026-10-01` y María compró 2 productos ese día (venta CONFIRMADO)
- **THEN** la respuesta incluye nombre de cliente, la venta con su total y los items con producto, cantidad y precio_unitario

#### Scenario: Sin ventas en la fecha
- **WHEN** la consulta es válida pero no hay ventas ese día
- **THEN** la respuesta tiene status 200 con `ventas: []`

### Requirement: Consultas de ventas en el asistente administrativo

El `AdminIntentRouter` SHALL reconocer las intenciones nuevas `ventas-hoy` y `ticket-cliente` (pattern matching determinístico, mismo estilo que las existentes), y el `AdminBotService` SHALL responderlas con datos reales de la base contable.

- Para `ticket-cliente`, la extracción de entidad SHALL ser determinista: fecha (`hoy` / `ayer` / `dd-mm-yyyy`) y nombre (coincidencia `ILIKE` contra `clients`), sin IA.

#### Scenario: Ventas de hoy desde el asistente
- **WHEN** se envía "cuántas ventas hubo hoy" y hay 4 ventas confirmadas hoy
- **THEN** la respuesta menciona la cantidad real (4) y solo cuenta la base contable

#### Scenario: Ticket de un cliente desde el asistente
- **WHEN** se envía "qué compró María ayer" y María compró el día anterior
- **THEN** la respuesta lista los productos comprados, cantidades y total

#### Scenario: Cliente o fecha sin datos
- **WHEN** se envía "qué compró Pedro el 01-01-2020" sin ventas
- **THEN** la respuesta informa que no se encontraron ventas para ese cliente/fecha
