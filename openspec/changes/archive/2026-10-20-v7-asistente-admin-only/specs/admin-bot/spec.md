## MODIFIED Requirements

### Requirement: Endpoint de consulta del asistente

El sistema SHALL exponer `POST /api/v1/admin-bot/consult` que recibe un JSON `{"mensaje": "<texto libre>"}` y devuelve `{"intent": "<intención>", "respuesta": "<texto armado>"}` con status 200.

- La respuesta SHALL construirse con datos reales obtenidos de la base de datos a través de la misma capa de repositories que usan los endpoints existentes.
- El endpoint SHALL registrar cada consulta como una interacción con `source="admin-bot"` y el `intent` detectado.
- Si el `mensaje` está vacío o ausente, el endpoint SHALL responder con status 422.
- El endpoint SHALL exigir un token JWT válido de un usuario con `role="admin"` (dependencia `require_admin`): sin header o con token inválido SHALL responder `401`, y un usuario autenticado con role distinto de `admin` SHALL recibir `403`.

#### Scenario: Consulta de clientes nuevos responde con datos reales
- **WHEN** se envía "¿cuántos clientes nuevos hay este mes?" y existen 3 clientes registrados en el mes actual
- **THEN** la respuesta tiene `intent: "clientes-nuevos-mes"`
- **AND** la respuesta menciona la cantidad real (3)

#### Scenario: Consulta de stock bajo lista productos bajo umbral
- **WHEN** se envía "productos con stock bajo" y existen productos con stock menor o igual al umbral configurado
- **THEN** la respuesta lista nombre y stock de esos productos

#### Scenario: Consulta de interacciones de hoy responde el conteo real
- **WHEN** se envía "cuántas interacciones hubo hoy" y hay 7 interacciones en el día
- **THEN** la respuesta menciona la cantidad real (7)

#### Scenario: Consulta de producto más vendido responde el top
- **WHEN** se envía "cuál es el producto más vendido"
- **THEN** la respuesta indica el/los productos con mayor cantidad total asignada entre todos los clientes

#### Scenario: Consulta de métricas responde resumen
- **WHEN** se envía "cómo vamos" o "dame las métricas"
- **THEN** la respuesta incluye total de clientes, activos, inactivos, interacciones totales, de hoy y de la semana

#### Scenario: Consulta registrada como interacción
- **WHEN** una consulta es procesada exitosamente
- **THEN** se persiste una interacción con `source="admin-bot"` e `intent` detectado

#### Scenario: Texto no entendido sugiere consultas válidas
- **WHEN** se envía texto irreconocible
- **THEN** la respuesta es un mensaje amigable que lista las consultas que el asistente sí entiende

#### Scenario: Usuario con role user recibe 403
- **WHEN** un usuario autenticado con `role="user"` envía `POST /api/v1/admin-bot/consult` con un token válido
- **THEN** responde `403` y no procesa la consulta
