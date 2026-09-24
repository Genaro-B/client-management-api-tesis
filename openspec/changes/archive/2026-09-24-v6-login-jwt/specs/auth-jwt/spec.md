# auth-jwt Specification

## Purpose

Autenticación de usuarios del panel con email + password (bcrypt), emisión/validación de tokens JWT (HS256) y protección de los endpoints de administración. Define también el cambio de password obligatorio tras la migración de usuarios existentes.

## Requirements

### Requirement: Login con email y password

El sistema MUST autenticar usuarios vía `POST /api/v1/auth/login` aceptando `{email, password}`. La password MUST verificarse contra el hash bcrypt almacenado. Si el email no existe, la cuenta está inactiva o la password es incorrecta, el sistema MUST responder `401`. El login SHOULD admitir únicamente cuentas con `role = "admin"` (los `clientes` con role `user` son prospectos del negocio, no usuarios del panel); un role no admin MUST recibir `401` con mensaje genérico (no revelar existencia de la cuenta).

#### Scenario: Login exitoso con password correcta

- GIVEN un cliente activo con `role="admin"`, `password_hash` válido y `password_change_required=false`
- WHEN se hace `POST /api/v1/auth/login` con email y password correctos
- THEN responde `200` con `{access_token, token_type: "bearer", user}`
- AND `user` contiene id, email, nombre, apellido, role y `password_change_required`

#### Scenario: Password incorrecta

- GIVEN un cliente activo con password_hash válido
- WHEN se envía la password incorrecta
- THEN responde `401` con detalle genérico de credenciales inválidas

#### Scenario: Cuenta de cliente (role user) intenta loguearse

- GIVEN un cliente activo con `role="user"`
- WHEN se loguea con credenciales correctas
- THEN responde `401` con detalle genérico

#### Scenario: Email no registrado o cuenta inactiva

- GIVEN un email inexistente o una cuenta con `activo=false`
- WHEN se intenta loguear
- THEN responde `401`

#### Scenario: Formato de request inválido

- GIVEN un payload sin `email` o sin `password`, o email malformado
- WHEN se hace el request
- THEN responde `422`

### Requirement: Emisión de token JWT

El sistema MUST emitir un JWT HS256 firmado con `JWT_SECRET_KEY` (env, default de desarrollo) que contenga el `client_id` como `sub`. El token MUST expirar a los `ACCESS_TOKEN_EXPIRE_MINUTES` minutos (default **480** = 8 horas). El sistema MUST NOT emitir refresh tokens ni permitir revocación manual.

#### Scenario: Token decodificable con expiración

- GIVEN un login exitoso
- WHEN se decodifica el `access_token` con la clave secreta
- THEN el `sub` es el id del usuario y `exp` está entre 1 min y 480 min en el futuro

### Requirement: Protección de endpoints del panel con Bearer

Los routers `clients` (todos los endpoints), `products`, `metrics/dashboard`, `admin_bot/consult` y `GET /interactions` MUST exigir header `Authorization: Bearer <token>` via dependencia `get_current_user`. Un request sin header, con token inválido, vencido o de un usuario inexistente MUST responder `401` y NO ejecutar el handler. `POST /api/v1/interactions` (usado por n8n/Telegram) MUST seguir autenticándose SOLO con `X-Api-Key` y no debe exigir JWT. `POST /auth/login` y `POST /auth/change-password`... el cambio de password debe exigir JWT.

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

### Requirement: Migración de usuarios existentes con password por defecto

El sistema MUST proveer un script idempotente (`backend/scripts/migrate_passwords.py`) que (a) agregue las columnas `password_hash` y `password_change_required` si no existen, y (b) asigne el hash bcrypt de `cambiar123` y `password_change_required=true` a TODO cliente existente con `password_hash IS NULL`. El script MUST aceptar un subcomando `set --email --password` para crear/actualizar la password de una cuenta (p.ej. el admin del panel) y poner `password_change_required=false`. Correr el script dos veces MUST ser seguro (no re-hashear lo ya migrado).

#### Scenario: Migración de clientes existentes

- GIVEN una BD con clientes sin `password_hash` y uno ya migrado
- WHEN se corre `migrate`
- THEN todos los que tenían `NULL` quedan con hash de `cambiar123` y flag `true`
- AND el ya migrado no se re-procesa

#### Scenario: Set de password para admin

- GIVEN un cliente admin existente
- WHEN se corre `set --email admin@x.com --password secreta123`
- THEN su `password_hash` corresponde a `secreta123` y el flag queda `false`

### Requirement: Flujo de cambio de password obligatorio

El sistema MUST exponer `POST /api/v1/auth/change-password` exigiendo JWT válido y payload `{current_password, new_password}` (mínimo 6 caracteres). Debe verificar `current_password` contra el hash; si no coincide MUST responder `401`. Al éxito MUST actualizar el hash, setear `password_change_required=false` y responder `200`. El `UserOut` del login MUST incluir `password_change_required` para que el frontend redirija al cambio en el primer login.

#### Scenario: Cambio de password con flag activo

- GIVEN un usuario logueado con `password_change_required=true` y password actual `cambiar123`
- WHEN envía `{current_password: "cambiar123", new_password: "nuevaSegura1"}`
- THEN responde `200`, el flag queda `false` y el login con `nuevaSegura1` funciona

#### Scenario: Password actual incorrecta

- GIVEN un usuario logueado
- WHEN envía `current_password` incorrecta
- THEN responde `401` y el hash no cambia

#### Scenario: New password demasiado corta

- GIVEN un request con `new_password` de menos de 6 caracteres
- THEN responde `422`