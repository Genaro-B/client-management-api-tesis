# Tasks: Login JWT con password (v6-login-jwt)

> TDD: cada task de código sigue RED (test que falla) → GREEN (mínimo para pasar) → REFACTOR. Safety Net: correr la suite existente antes de tocar archivos.

## Phase 1: Fundación (deps, modelo, security)

- [x] 1.1 Agregar `bcrypt` y `PyJWT` a `backend/requirements.txt` e instalarlos en el venv
- [x] 1.2 RED: `backend/tests/test_security.py` — `hash_password`/`verify_password` (roundtrip, password distinta falla)
- [x] 1.3 GREEN: crear `backend/src/core/security.py` con `hash_password`, `verify_password` (bcrypt)
- [x] 1.4 RED: en `test_security.py`, tests de `create_access_token`/`decode_token` (sub correcto, exp≈480min, token vencido→error, token tamper→error)
- [x] 1.5 GREEN: implementar JWT en `security.py` (HS256, `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` default 480, `sub`=client_id)
- [x] 1.6 Modificar `backend/src/models/client.py`: columnas `password_hash` (String 255 nullable) y `password_change_required` (Boolean default True, server_default "1")
- [x] 1.7 Actualizar `backend/tests/conftest.py`: fixture `sample_admin` (role admin con `password_hash` de "cambiar123") y helper `admin_headers_bearer` (login → token) o generador directo con `create_access_token`

## Phase 2: Endpoint login + change-password (TDD)

- [x] 2.1 RED: reescribir `backend/tests/test_auth_api.py` — login exige `{email,password}`: exitoso devuelve `access_token`+`user`; password incorrecta→401; email no registrado→401; inactiva→401; role user→401; 422 sin password
- [x] 2.2 GREEN: modificar `backend/src/schemas/client.py` (`LoginRequest(email,password)`, `UserOut` con `password_change_required`, `AuthResponse(access_token,token_type,user)`, `ChangePasswordRequest`) y reescribir `POST /login` en `backend/src/api/routes/auth.py` (bcrypt+JWT, solo role admin, 401 genérico)
- [x] 2.3 RED: tests de `POST /auth/change-password` — exige JWT (401 sin token), password actual incorrecta→401, éxito→200 + flag False + login con nueva password, new_password <6→422
- [x] 2.4 GREEN: implementar `POST /auth/change-password` en `auth.py` (deps `get_current_user`)

## Phase 3: Deps JWT + protección de routers

- [x] 3.1 RED: `test_security.py` o `test_deps.py` — `get_current_user`: sin header→401, token inválido/vencido→401, token válido→Client
- [x] 3.2 GREEN: crear `backend/src/core/deps.py` (`get_current_user` con `HTTPBearer`, `require_admin`) — REUTILIZA `decode_token`, no duplica lógica
- [x] 3.3 RED: agregar en `test_clients_api.py` tests 401 sin token en GET/POST `/clients/`; 401 en `test_products_api.py`; 401 en `test_metrics_api.py`; adaptar tests existentes para mandar `admin_headers_bearer`
- [x] 3.4 GREEN: agregar `Depends(get_current_user)` en `clients.py` (todos), `products.py`, `metrics.py` `/dashboard`; `require_admin` en `/inactive` y `/{id}/restore`
- [x] 3.5 GREEN: agregar `Depends(get_current_user)` en `GET /interactions` (solo GET) y `POST /admin-bot/consult`
- [x] 3.6 Verificar que `test_interaction_api.py` sigue verde SIN cambios (POST con X-Api-Key intacto)

## Phase 4: Script de migración

- [x] 4.1 Crear `backend/scripts/migrate_passwords.py`: subcomandos `migrate` (ALTER TABLE idempotente + hash `cambiar123` solo a `password_hash IS NULL` + flag True) y `set --email --password`
- [x] 4.2 Test del script (BD SQLite temp): migración idempotente (correr 2×), `set` actualiza hash y flag False
- [x] 4.3 Correr `migrate` contra `dev.db` real + `set` para el admin del panel (`genarobusto@gmail.com`)

## Phase 5: Frontend

- [x] 5.1 RED: actualizar `frontend/src/services/authService.test.js` — login manda `{email,password}`, guarda `access_token`, interceptor agrega `Authorization: Bearer` (mock de `request.use`)
- [x] 5.2 GREEN: modificar `frontend/src/services/authService.js` (`login(email,password)`, `TOKEN_KEY` en sessionStorage, interceptor en el instance axios)
- [x] 5.3 Actualizar `frontend/src/state/AuthContext.test.jsx` y `AuthContext.jsx`: login con password, `changePassword()`, logout limpia token
- [x] 5.4 Actualizar `frontend/src/pages/LoginPage.test.jsx` y `LoginPage.jsx`: enviar password real, quitar texto "sin efecto aún", redirigir a cambio de password si `password_change_required` (página simple de change-password)

## Phase 6: Docs + verificación final

- [x] 6.1 Actualizar `README.md`: tabla de endpoints con auth JWT, env vars `JWT_SECRET_KEY`/`ACCESS_TOKEN_EXPIRE_MINUTES`, sección Seguridad (password default `cambiar123`, cambio obligatorio, solo admin loguea, n8n con X-Api-Key)
- [x] 6.2 Correr suite completa backend (`dev.db` aislada no se toca): `..\.venv\Scripts\python -m pytest tests/ -v` — 253 passed
- [x] 6.3 Correr suite frontend: `npm test` — 56 passed (9 files)
- [x] 6.4 Verificar smoke manual: login con password default → prompt de cambio → endpoints protegidos con/ sin Bearer