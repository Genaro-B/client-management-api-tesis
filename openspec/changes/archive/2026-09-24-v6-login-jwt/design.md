# Design: Login JWT con password (v6-login-jwt)

## Technical Approach

Se reemplaza el login email-only por autenticación real: password hasheada con **bcrypt** + token **JWT HS256** (PyJWT, sin refresh token). El token viaja como `Authorization: Bearer` y protege los routers del panel (`clients`, `products`, `metrics`, `admin_bot`, GET `interactions`). El POST `interactions` (n8n) conserva `X-Api-Key`. Migración de usuarios existentes vía script idempotente: password por defecto `cambiar123` + flag `password_change_required`, obligando al cambio en el primer login vía `POST /auth/change-password`.

## Architecture Decisions

| # | Opción | Tradeoff | Decisión |
|---|--------|----------|----------|
| 1 | **Quién puede loguearse** | Solo admin = panel seguro, pero un role "staff" futuro no entra. Permitir cualquier role = los clients (prospectos del negocio, role `user`) podrían entrar al panel sin sentido | **Solo role `admin`** puede loguearse. El `metrics` router ya excluye `role != 'admin'`; un `user` es un prospecto, no un usuario del sistema. Se documenta en README y se valida en el endpoint (401 genérico). |
| 2 | **Cómo se crean passwords de usuarios del panel** | Endpoint admin-only de creación = expone superficie nueva sin UI que lo use. Script CLI = simple, explícito, reusable para seed y reset | **Script `scripts/migrate_passwords.py`** con subcomandos `migrate` (default `cambiar123` a todos + flag) y `set --email --password` (crea/actualiza hash de un admin, resetea flag). Un admin nuevo del panel se crea seteando su password con `set`; los clients creados por `POST /clients` NO loguean (siguen sin password). |
| 3 | **Cambio de password: validar password actual** | Solo nuevo password = más simple pero un token robado alcanza. Con password actual = más seguro (prueba de posesión) | **`ChangePasswordRequest(current_password, new_password)`** — exige password actual + JWT válido. |
| 4 | **¿Bloquear endpoints si `password_change_required`?** | Bloquear todo = más estricto pero rompe lectura de datos. No bloquear = simple; el frontend redirige | **NO se bloquean endpoints** en backend; el flag viaja en `UserOut` y el frontend redirige al flujo de cambio. Tradeoff documentado (token sigue sirviendo 8 hs aunque no cambie la password). |
| 5 | **Ubicación de la lógica JWT** | Todo en `core/auth.py` = mezcla API key + JWT. Archivos separados = limpieza hexagonal | **`core/security.py`** (bcrypt + JWT puro) y **`core/deps.py`** (deps FastAPI `get_current_user`, `require_admin`). `core/auth.py` no se toca (`verify_api_key` sigue para n8n). |
| 6 | **Brute-force / rate limit** | Necesario en producción | Fuera de scope (tesis); se documenta como deuda en README. |
| 7 | **Refresh token** | Mejor UX, más complejidad | **Sin refresh token**: expiración 8 hs (env `ACCESS_TOKEN_EXPIRE_MINUTES`), login de nuevo al expirar. |

## Data Flow

```
Login:  POST /auth/login {email,password}
        → ClientRepository.get_by_email → role != "admin" → 401
        → verify_password(bcrypt) → 401 si falla → JWT(HS256, sub=client.id, exp=+8h)
        → {access_token, token_type:"bearer", user: UserOut}

Panel:   GET /clients (Authorization: Bearer <jwt>)
        → get_current_user → decode + sub → Client por id → 401/404 si inválido
        → handler → respuesta

n8n:     POST /interactions (X-Api-Key)  ← sin cambio

Cambio:  POST /auth/change-password (Bearer) {current, new}
        → verifica hash actual → setea nuevo hash → flag=False
```

## File Changes

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `backend/src/core/security.py` | Crear | `hash_password`, `verify_password` (bcrypt), `create_access_token`, `decode_token` (PyJWT HS256); lee `JWT_SECRET_KEY` (default dev), `ACCESS_TOKEN_EXPIRE_MINUTES` (480) |
| `backend/src/core/deps.py` | Crear | `get_current_user` (Bearer → Client), `require_admin` |
| `backend/src/models/client.py` | Modificar | `password_hash` (String 255, nullable), `password_change_required` (Boolean, default True) |
| `backend/src/schemas/client.py` | Modificar | `LoginRequest(email, password)`, `AuthResponse(access_token, token_type, user: UserOut)`, `UserOut(id,email,nombre,apellido,role,password_change_required)`, `ChangePasswordRequest(current_password, new_password)` |
| `backend/src/api/routes/auth.py` | Modificar | Login con bcrypt+JWT+validación admin; `POST /change-password` |
| `backend/src/api/routes/clients.py` | Modificar | `Depends(get_current_user)` en todos los endpoints; `require_admin` en inactive/restore |
| `backend/src/api/routes/products.py` | Modificar | `Depends(get_current_user)` |
| `backend/src/api/routes/metrics.py` | Modificar | `Depends(get_current_user)` en `/dashboard` |
| `backend/src/api/routes/admin_bot.py` | Modificar | `Depends(get_current_user)` en `/consult` |
| `backend/src/api/routes/interactions.py` | Modificar | `Depends(get_current_user)` solo en GET `/` |
| `backend/scripts/migrate_passwords.py` | Crear | ALTER TABLE idempotente + seed bcrypt + flag + subcomando `set` |
| `backend/requirements.txt` | Modificar | `bcrypt`, `PyJWT` |
| `backend/tests/conftest.py` | Modificar | fixture `admin_client` (con password), helper `auth_headers_bearer` |
| `frontend/src/services/authService.js` | Modificar | `login(email,password)`, storage de token, interceptor Bearer |
| `frontend/src/state/AuthContext.jsx` | Modificar | login con password, `changePassword`, expiración → logout |
| `frontend/src/pages/LoginPage.jsx` | Modificar | usar password real, quitar texto "sin efecto aún" |
| `README.md` | Modificar | endpoints, env vars `JWT_SECRET_KEY`/`ACCESS_TOKEN_EXPIRE_MINUTES`, sección seguridad |

## Interfaces / Contracts

```python
# core/security.py
def hash_password(p: str) -> str: ...
def verify_password(plain: str, hashed: str) -> bool: ...
def create_access_token(client_id: int) -> str: ...      # HS256, sub, exp, iat
def decode_token(token: str) -> int: ...                  # devuelve client_id, raise 401

# core/deps.py
def get_current_user(authorization=Header(None), db=Depends(get_db)) -> Client: ...
def require_admin(user=Depends(get_current_user)) -> Client: ...  # 403 si role != admin

# schemas
class LoginRequest(BaseModel): email: EmailStr; password: str = Field(min_length=1)
class UserOut(BaseModel): id; email; nombre; apellido; role; password_change_required: bool
class AuthResponse(BaseModel): access_token: str; token_type: str = "bearer"; user: UserOut
class ChangePasswordRequest(BaseModel): current_password: str; new_password: str = Field(min_length=6)
```

## Testing Strategy

| Capa | Qué | Cómo |
|------|-----|------|
| Unit | `security.py` | RED→GREEN: hash/verify roundtrip, token válido/vencido/tamperead |
| API | Login | Password correcta/incorrecta, email no registrado, cuenta inactiva, role user → 401, response contiene access_token+user |
| API | Protección JWT | Sin header / token inválido → 401 en clients, products, metrics, admin_bot, GET interactions; con token válido → 200 |
| API | Change password | Actual incorrecta → 400/401; nueva correcta → flag False y login con nueva |
| API | n8n intacto | `test_interaction_api.py` sin cambios pasa (X-Api-Key) |
| Frontend | authService/AuthContext/LoginPage | Vitest: login manda `{email,password}`, interceptor agrega Bearer, redirect change-password |

## Migration / Rollout

1. Agregar columnas al modelo + `python scripts/migrate_passwords.py migrate` (idempotente: `ALTER TABLE` con try/except, solo procesos filas con `password_hash IS NULL`).
2. `python scripts/migrate_passwords.py set --email genarobusto@gmail.com --password <elegida>` para el admin del panel.
3. Desplegar backend + frontend juntos (login cambia de contrato — **BREAKING**): el frontend viejo rompería, por eso van de la mano.
4. El README documenta password default y obligación de cambio.

## Open Questions

- [ ] ¿Conviene rate-limit de login (slowapi) en esta iteración o queda como deuda? — Recomendado: deuda documentada, no bloquea este change.
- [ ] ¿`require_admin` se aplica ya a todos los endpoints de clients (inactive/restore) o solo `get_current_user`? — Decisión: sí, esos dos ya docstringean "Solo acceso admin".