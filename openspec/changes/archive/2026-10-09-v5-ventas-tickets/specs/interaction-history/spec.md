## ADDED Requirements

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
