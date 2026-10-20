## Why

`POST /api/v1/admin-bot/consult` expone métricas reales del negocio (ventas, stock, clientes, interacciones) a cualquier usuario autenticado: la ruta usa `get_current_user` y no valida rol, mientras que el frontend solo oculta el widget (`AdminBotLauncher` devuelve `null` si no es admin) — el gating actual es de UI, no de API. Es un caso de Broken Function Level Authorization (OWASP API5:2023). `require_admin` ya existe en `src/core/deps.py` y lo usan `clients/inactive`, `clients/{id}/restore` y los endpoints de ventas; falta aplicarlo acá. Además, el spec `auth-jwt` EXPLICITAMENTE exige `get_current_user` para `admin_bot/consult`, así que el spec (no solo el código) tiene que cambiar.

## What Changes

- **BREAKING (deseado)** — `POST /api/v1/admin-bot/consult` pasa de `get_current_user` a `require_admin`: un token con `role="user"` recibe `403`; sin token o con token inválido/vencido sigue respondiendo `401`.
- Los routers `clients`, `products`, `metrics/dashboard` y `GET /interactions` conservan `get_current_user` (cero cambios).
- **Spec `auth-jwt` (delta MODIFIED):** el requisito "Protección de endpoints del panel con Bearer" pasa a exigir `require_admin` SOLO para `admin_bot/consult` y agrega el escenario `403`.
- **Spec `admin-bot` (delta MODIFIED):** el requisito "Endpoint de consulta del asistente" documenta la exigencia de `role="admin"` con su escenario `403`.
- **Sin cambios de contrato del endpoint:** respuesta `{intent, respuesta}`, registro de interacción con `source="admin-bot"` y cascada de cerebros intactas.
- **Sin cambios de frontend** (ya está admin-gated), sin migraciones de BD, sin dependencias nuevas.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `auth-jwt`: requisito "Protección de endpoints del panel con Bearer" — `admin_bot/consult` MUST exigir `require_admin` (401 sin/inválido, 403 a role≠admin); los demás routers mantienen `get_current_user`.
- `admin-bot`: requisito "Endpoint de consulta del asistente" — el endpoint SHALL exigir un token de un usuario con `role="admin"` (nuevo escenario 403).

## Impact

- **Backend**: `backend/src/api/routes/admin_bot.py` (import + dependencia, una línea efectiva); `backend/tests/test_admin_bot_api.py` (+1 test: token role user → 403). `src/core/deps.py` NO se toca (`require_admin` ya existe y ya está testeado en `test_deps.py`).
- **Frontend**: sin cambios.
- **Docs**: `README.md` — tabla de endpoints (~línea 231, Auth `Bearer` → `Bearer + Admin`), sección del asistente (~línea 438) y conteo de tests de `test_admin_bot_api.py` (~línea 292).
- **Comportamiento**: solo cambia el caso role≠admin en `/admin-bot/consult` (justamente el que debe fallar). Suite backend: baseline **419 passed** → 419 + tests nuevos.
