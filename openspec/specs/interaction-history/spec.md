# interaction-history Specification

## Purpose
Registrar y consultar las interacciones (mensajes/eventos) recibidas desde los distintos orígenes (bot de Telegram, panel, API) y vincularlas opcionalmente al cliente resuelto vía `clientLookup`.
## Requirements
### Requirement: Registrar una interacción

El sistema SHALL exponer `POST /api/v1/interactions` para persistir una interacción con `source` y `payload` válidos, devolviendo `201` con `{ id, timestamp }`.

#### Scenario: Guardado exitoso
- **GIVEN** un payload válido con `source` y `payload`
- **WHEN** se hace `POST /api/v1/interactions`
- **THEN** responde `201` con `{ id, timestamp }`

### Requirement: Vincular la interacción a un cliente

Al persistir una interacción, si el payload incluye `clientLookup` (`email` o `telefono`) que coincide con un cliente existente, el sistema SHALL setear el `clientId` de la interacción con el id de ese cliente.

#### Scenario: Guardar y vincular a cliente
- **GIVEN** un payload con `clientLookup` (`email` o `telefono`) que coincide con un cliente existente
- **WHEN** se hace `POST /api/v1/interactions`
- **THEN** la interacción persistida tiene `clientId` seteado al cliente resuelto

### Requirement: Validación del payload de interacción

El sistema SHALL rechazar con `400` y los errores de validación correspondientes cuando falte `payload` o `source`.

#### Scenario: Error de validación
- **WHEN** se hace `POST` sin `payload` o sin `source`
- **THEN** responde `400` con los errores de validación

### Requirement: Resolución de cliente por telegram_user_id en clientLookup

El sistema SHALL aceptar la clave `telegram_user_id` dentro de `clientLookup` en `POST /api/v1/interactions`, resolviéndola PRIMERO (antes de `email` y `telefono`) contra la columna `clients.telegram_user_id`. Si coincide, la interacción SHALL quedar vinculada con `clientId` del cliente resuelto.

- Las claves existentes `email` y `telefono` SHALL conservar su comportamiento actual cuando `telegram_user_id` no esté presente o no coincida.
- Si ninguna clave resuelve un cliente, la interacción SHALL persistirse con `clientId = null` (comportamiento actual, sin error).

#### Scenario: Vinculación por telegram_user_id
- **WHEN** se envía una interacción con `clientLookup: {"telegram_user_id": "12345"}` y existe un cliente con esa columna
- **THEN** la interacción persistida tiene `clientId` igual al id de ese cliente

#### Scenario: Prioridad sobre email y telefono
- **WHEN** el `clientLookup` trae `telegram_user_id` que coincide con un cliente y además un `email` que coincide con otro cliente distinto
- **THEN** la interacción se vincula al cliente resuelto por `telegram_user_id`

#### Scenario: Sin coincidencia mantiene el comportamiento actual
- **WHEN** el `clientLookup` trae un `telegram_user_id` inexistente
- **THEN** la interacción se persiste con `clientId = null` y status 201

### Requirement: Listar interacciones filtradas por cliente

El sistema SHALL permitir listar interacciones filtradas por un cliente específico. El endpoint `GET /api/v1/interactions/` SHALL aceptar un query param opcional `client_id` y devolver únicamente las interacciones cuyo `clientId` coincide.

- El filtro SHALL ser combinable con los query params `limit` y `offset` existentes.
- El campo `total` de la respuesta SHALL reflejar el total de interacciones del cliente filtrado (no el total global).
- El orden SHALL continuar siendo de más reciente a más antigua.

#### Scenario: Filtrar por cliente devuelve solo sus interacciones
- **WHEN** se hace GET a `/api/v1/interactions/?client_id=5`
- **THEN** la respuesta contiene únicamente interacciones con `clientId=5`
- **AND** `total` es el conteo de interacciones del cliente 5

#### Scenario: Sin filtro mantiene el comportamiento actual
- **WHEN** se hace GET a `/api/v1/interactions/` sin `client_id`
- **THEN** se devuelven todas las interacciones ordenadas de más reciente a más antigua (comportamiento actual)

#### Scenario: Cliente sin interacciones devuelve lista vacía
- **WHEN** se hace GET a `/api/v1/interactions/?client_id=999` y el cliente 999 no tiene interacciones
- **THEN** `items` es un array vacío y `total` es 0

#### Scenario: Filtro combinado con paginación
- **WHEN** se hace GET a `/api/v1/interactions/?client_id=5&limit=10&offset=10`
- **THEN** se devuelven las interacciones del cliente 5 salteando las primeras 10
- **AND** `total` es el total de interacciones del cliente 5

