## ADDED Requirements

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