# Proposal: Login JWT con password (v6-login-jwt)

## Why

El login actual es **email-only**: `POST /api/v1/auth/login` deja entrar a cualquiera que conozca un email activo, sin password ni token. Es una vulnerabilidad crítica: los endpoints de clientes, productos y métricas están abiertos, y cualquier GET del sistema expone datos del negocio. El README ya lo marca como deuda (`Autenticación con password — Pendiente`). Este change la cierra: password real (bcrypt), sesión por JWT y protección de los endpoints del panel.

## What Changes

- **BREAKING** `POST /api/v1/auth/login`: ahora exige `{email, password}`, valida hash bcrypt y devuelve `{access_token, token_type, user}` (JWT HS256, sin refresh token).
- **BREAKING** Respuesta de login: `AuthResponse` pasa a `{access_token, token_type, user: UserOut}` (antes era el user plano).
- Columna `password_hash` + flag `password_change_required` en `Client` (modelo + migración de la BD local).
- Script `scripts/migrate_passwords.py`: setea password por defecto `cambiar123` a todos los clientes existentes con `password_change_required=1`; también permite setear/actualizar password de un usuario del panel (role admin) por email.
- Endpoint `POST /api/v1/auth/change-password` (requiere JWT + password actual) para el flujo de cambio obligatorio.
- Protección JWT (Bearer) en routers: `clients`, `products`, `metrics`, `admin_bot`, y GET `interactions`. `POST /interactions` (n8n/Telegram) queda con `X-Api-Key` — NO se rompe el flujo n8n.
- Login público; token con expiración de 8 hs configurable por env.
- Frontend: `authService.login(email, password)`, token en `sessionStorage`, interceptor de axios que agrega `Authorization: Bearer`, `AuthContext` adaptado manteniendo la API `login/logout/isAdmin/isAuthenticated`, redirección a cambio de password cuando `password_change_required`.
- README: sección de endpoints/auth/seguridad/README actualizada.
- Tests: `test_auth_api.py` reescrito (password + JWT + change-password) + protección JWT en clients/products/metrics.

## Capabilities

### New Capabilities
- `auth-jwt`: autenticación con email+password (bcrypt), emisión/validación de tokens JWT, cambio de password obligatorio y protección de endpoints del panel.

### Modified Capabilities
- None — no hay spec previa de auth en `openspec/specs/` (`client-management-ui`, `dashboard-metrics`, `frontend-testing`, `interaction-history` no cambian sus requisitos).

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `backend/src/api/routes/auth.py` | Modificado | Login con password + `change-password` |
| `backend/src/schemas/client.py` | Modificado | `LoginRequest(email,password)`, `AuthResponse`, `ChangePasswordRequest`, `UserOut` |
| `backend/src/models/client.py` | Modificado | `password_hash`, `password_change_required` |
| `backend/src/core/security.py` | Nuevo | bcrypt hash/verify, JWT encode/decode |
| `backend/src/core/deps.py` | Nuevo | `get_current_user`, `require_admin` |
| `backend/src/core/auth.py` | Sin cambio | `verify_api_key` sigue para n8n |
| `backend/src/api/routes/{clients,products,metrics,admin_bot,interactions}.py` | Modificado | Deps JWT |
| `backend/requirements.txt` | Modificado | `bcrypt`, `PyJWT` |
| `backend/scripts/` | Nuevo | `migrate_passwords.py` |
| `frontend/src/services/authService.js` | Modificado | login con password, token, interceptor |
| `frontend/src/state/AuthContext.jsx` | Modificado | manejo de token + cambio de password |
| `README.md` | Modificado | docs de auth |

## Risks

| Riesgo | Likelihood | Mitigación |
|--------|------------|------------|
| Romper flujo n8n (POST /interactions) | Baja | Se toca solo el GET; el POST conserva `X-Api-Key` |
| Usuarios con password default sin cambiarla | Media | Flag `password_change_required` + obligación en frontend |
| SECRET_KEY default en producción | Alta | Vars de entorno `JWT_SECRET_KEY` documentadas en README |
| Clientes (role user) intentando loguearse | Media | Login admitido SOLO para role admin (decisión documentada) |

## Rollback Plan

1. Revertir el commit del change (`git revert`).
2. Volver a correr el script con `--rollback` (drop de columnas opcional) o simplemente regenerar `dev.db`: el sistema sigue funcionando con login email-only si se restaura `auth.py` y se quitan los `Depends` JWT.
3. Si hubo tokens emitidos, expiran solos en ≤8 hs; sin refresh token no hay sesiones persistentes que invalidar.

## Dependencies

- `bcrypt` y `PyJWT` nuevos en `requirements.txt` (no instalados hoy en el venv).
- BD local existente (`dev.db` / `client_management.db`): migración idempotente por script, sin alembic.

## Success Criteria

- [ ] `pytest` backend verde: login con password, protección JWT en clients/products/metrics, change-password.
- [ ] `POST /interactions` sigue funcionando solo con `X-Api-Key` (test existente intacto).
- [ ] Login sin token o con token inválido → 401 en endpoints protegidos.
- [ ] Login con password default → `password_change_required: true` y flujo de cambio funciona.
- [ ] Frontend: suite Vitest verde; calls salen con `Authorization: Bearer`.
- [ ] README actualizado (endpoints, env vars, seguridad).