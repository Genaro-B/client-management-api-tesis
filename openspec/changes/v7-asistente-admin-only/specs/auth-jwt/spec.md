## MODIFIED Requirements

### Requirement: Protección de endpoints del panel con Bearer

Los routers `clients` (todos los endpoints), `products`, `metrics/dashboard` y `GET /interactions` MUST exigir header `Authorization: Bearer <token>` via dependencia `get_current_user`. El endpoint `admin_bot/consult` MUST exigir header `Authorization: Bearer <token>` via dependencia `require_admin` (compuesta sobre `get_current_user`): un request sin header, con token inválido, vencido o de un usuario inexistente MUST responder `401` y NO ejecutar el handler, y un usuario autenticado con `role` distinto de `admin` MUST responder `403` y NO ejecutar el handler. `POST /api/v1/interactions` (usado por n8n/Telegram) MUST seguir autenticándose SOLO con `X-Api-Key` y no debe exigir JWT. `POST /auth/login` y `POST/auth/change-password`... el cambio de password debe exigir JWT.

#### Scenario: Endpoint protegido sin token

- GIVEN un request a `GET /api/v1/clients/` sin header Authorization
- THEN responde `401` y no lista clientes

#### Scenario: Endpoint protegido con token válido

- GIVEN un token JWT válido de un usuario admin activo
- WHEN se hace GET a un endpoint protegido con ese token
- THEN responde `200` con los datos

#### Scenario: Endpoint protegido con token inválido o vencido

- GIVEN un token firmado con otra clave, malformado o vencido
- WHEN se accede a un endpoint protegido
- THEN responde `401`

#### Scenario: n8n sigue funcionando

- GIVEN un request a `POST /api/v1/interactions/` con `X-Api-Key` correcta y sin Bearer
- THEN responde `201` (comportamiento actual intacto)

#### Scenario: Consulta del asistente sin token responde 401

- **WHEN** se hace `POST /api/v1/admin-bot/consult` sin header Authorization
- **THEN** responde `401` y no procesa la consulta

#### Scenario: Consulta del asistente con usuario no admin responde 403

- **WHEN** un usuario autenticado con `role="user"` hace `POST /api/v1/admin-bot/consult` con un token válido
- **THEN** responde `403` y no procesa la consulta
