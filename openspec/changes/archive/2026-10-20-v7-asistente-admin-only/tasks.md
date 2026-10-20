## 1. Safety net (baseline)

- [x] 1.1 Correr la suite backend completa desde `backend/` (`..\.venv\Scripts\python.exe run_tests.py`) y registrar el baseline: **419 passed** (si algo preexistente falla, detenerse y reportarlo antes de tocar código)

## 2. RED — test que expone la brecha

- [x] 2.1 En `backend/tests/test_admin_bot_api.py` agregar `test_consult_con_token_role_user_devuelve_403`: cliente con `role="user"` (patrón de `sample_client`) + token válido con `create_access_token` → `POST /api/v1/admin-bot/consult` → `403`
- [x] 2.2 Verificar que ya existe `test_consult_without_token_returns_401` (sin token → `401`) y que pasa tal cual
- [x] 2.3 Ejecutar los tests nuevos y confirmar RED: el test de `403` FALLA contra el código actual (que responde `200` para role user)

## 3. GREEN — aplicar la dependencia

- [x] 3.1 En `backend/src/api/routes/admin_bot.py`: cambiar `from src.core.deps import get_current_user` por `from src.core.deps import require_admin` y la dependencia de `consult` de `Depends(get_current_user)` a `Depends(require_admin)` (sin tocar el resto del handler)
- [x] 3.2 Ejecutar los tests nuevos → `403` (role user) y `401` (sin token) en verde

## 4. Regresión — suite completa

- [x] 4.1 Correr la suite backend completa → **419 + tests nuevos, todos verdes** (contrato `{intent, respuesta}`, logging `source="admin-bot"` y cascada intactos)
- [x] 4.2 Confirmar que los tests existentes del asistente siguen verdes: `test_admin_bot_api.py` y `test_admin_bot_brain_api.py` (usan `admin_headers_bearer`, token admin) y `test_deps.py` (`require_admin`)

## 5. Documentación

- [x] 5.1 `README.md` tabla de endpoints (~línea 231): Auth de `POST /api/v1/admin-bot/consult` de `Bearer` → `Bearer + Admin` (mismo estilo que `clients/inactive`)
- [x] 5.2 `README.md` sección del asistente (~línea 438): aclarar que el endpoint exige `role="admin"` (el ejemplo curl de ~línea 491 ya usa Bearer)
- [x] 5.3 `README.md` tabla de tests (~línea 292): actualizar el conteo/Descripción de `test_admin_bot_api.py` si cambió
