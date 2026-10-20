## Context

- `backend/src/api/routes/admin_bot.py` (línea 29): `consult` declara `_user: Client = Depends(get_current_user)` — cualquier usuario autenticado (`role="user"` o `role="admin"`) consulta métricas reales del negocio (ventas, stock, clientes, interacciones).
- `backend/src/core/deps.py` (línea 44): `require_admin` YA existe, compone `get_current_user` y lanza `403 "Solo acceso admin"` cuando `user.role != "admin"`. Lo usan `clients.py` (inactive/restore) y `sales.py`, pero NO `admin_bot.py`. Ya está testeado en `test_deps.py` (admin pasa, role user → 403).
- `frontend/src/App.jsx` (líneas 30-36): `AdminBotLauncher` devuelve `null` cuando `!isAdmin` — el gating actual es solo de UI, la API no valida nada (OWASP API5:2023, Broken Function Level Authorization).
- `openspec/specs/auth-jwt/spec.md` (~línea 56): el requisito "Protección de endpoints del panel con Bearer" EXPLICITAMENTE exige `get_current_user` para `admin_bot/consult`. Sin tocar este spec, el código quedaría en conflicto con el spec (el spec sería cómplice de la brecha). El design de `v6-asistente-nlu-local` ya listó "Fix de require_admin (separado)" como fuera de alcance: este change ES ese fix.
- Matiz importante: el login del panel ya restringe a cuentas `role="admin"` (spec auth-jwt, escenario "Cuenta de cliente (role user) intenta loguearse" → 401). Eso NO sustituye la autorización a nivel de endpoint: los tokens vigentes (8 h) sobreviven a un cambio de rol de la cuenta, y el contrato 403 debe existir en la API, no derivarse de una restricción del login (defensa en profundidad).

## Goals / Non-Goals

**Goals:**

- `POST /api/v1/admin-bot/consult` responde `403` para un token con `role != "admin"` y mantiene `401` para token ausente/inválido/vencido.
- Contrato del endpoint idéntico: `{intent, respuesta}`, interacción `source="admin-bot"`, cascada de cerebros intacta.
- Los specs reflejan el comportamiento real: `auth-jwt` modificado (ya no manda `get_current_user` para `admin_bot/consult`) y `admin-bot` con la exigencia de rol documentada.
- Suite backend completa verde (baseline **419 passed** + tests nuevos).

**Non-Goals:**

- Cambios en el frontend (ya oculta el widget a usuarios no admin).
- Cambiar la autenticación de OTROS endpoints: `clients`, `products`, `metrics/dashboard`, `interactions` conservan `get_current_user`.
- Modificar el contrato de respuesta, el logging de interacciones o la cascada de cerebros (matcher → clasificador → Ollama).
- Revocación/rotación de tokens, rate limiting, o cambios en el flujo de login.
- Migraciones de base de datos ni dependencias nuevas.

## Decisions

1. **Reutilizar `require_admin` existente vs. dependencia nueva o chequeo inline.** → Reutilizar: ya está probada (`test_deps.py`), ya la usan `clients`/`sales` y encapsula la lógica en un solo lugar. Alternativas descartadas: (a) `if user.role != "admin"` dentro del handler — mezcla autorización con lógica de negocio y no es reutilizable; (b) crear otra dependencia — duplicaría `require_admin`.
2. **Orden de la cadena de dependencias.** → `Depends(require_admin)` compone `Depends(get_current_user)`: primero se resuelve el token (cualquier fallo → `401`) y recién después se chequea el rol (role≠admin → `403`). El contrato 401 vs 403 queda garantizado sin código adicional.
3. **Spec-first: modificar el spec `auth-jwt` además del código.** → El spec actual autoriza la brecha (`get_current_user` para `admin_bot/consult`). Se MODIFICA el requisito completo (header + texto + escenarios), cambiando SOLO la dependencia de `admin_bot/consult` y agregando los escenarios 401/403 de este endpoint; los demás routers quedan textualmente iguales con `get_current_user`. Alternativa descartada: cambiar solo el código — dejaría un spec mentiroso que regresaría la brecha en la próxima revisión.
4. **Delta secundario en `admin-bot`.** → El requisito "Endpoint de consulta del asistente" define el contrato del endpoint pero no menciona autorización. Se lo MODIFICA (copia completa + bullet de rol admin + escenario 403) para que los tests del endpoint mapeen contra su propio spec. Mantenido mínimo a propósito: la fuente de verdad de autorización sigue siendo `auth-jwt`.
5. **TDD: RED primero.** → Nuevo test con token de un cliente `role="user"` (token mintido con `create_access_token`, mismo patrón que `admin_headers_bearer` pero con `sample_client`): espera `403` y FALLA contra el código actual (devuelve `200`). Recién en GREEN se cambia la dependencia. El 401 sin token ya está cubierto por `test_consult_without_token_returns_401` (se verifica que sigue verde).
6. **Mensaje 403.** → Se reutiliza el `"Solo acceso admin"` que ya emite `require_admin`; no se introduce un mensaje nuevo (no romper el manejo de errores del frontend).

## Risks / Trade-offs

- [Algún flujo llamaba `/consult` con un token no-admin] → Es exactamente el comportamiento a bloquear; el frontend nunca lo hacía (widget admin-only) y el login no emite tokens a cuentas user. → Mitigación: marcado **BREAKING (deseado)** en la propuesta.
- [Romper tests existentes de admin-bot] → Todos los tests de `/consult` usan `admin_headers_bearer` (token admin) o ninguna credencial (401). → Mitigación: gate de suite completa (baseline 419) antes de cerrar.
- [Delta MODIFIED incompleto pierde escenarios al archivar] → Se copió el requisito COMPLETO desde el spec principal y solo se agregó; gate: `openspec validate v7-asistente-admin-only --strict`.
- [Spec duplica la exigencia de rol en `auth-jwt` y `admin-bot`] → Aceptado a propósito: `auth-jwt` es la fuente de la política transversal, `admin-bot` documenta su endpoint. Riesgo de divergencia futuro → mitigado porque ambos cambios se archivan juntos.

## Migration Plan

Sin migración de datos ni pasos de despliegue especiales: es un cambio de dependencia en una ruta + specs + un test. Deploy normal. Rollback: `git revert` del commit (restaura `get_current_user` en `admin_bot/consult` y los specs originales).

## Open Questions

Ninguna — el alcance está cerrado: spec `auth-jwt` + spec `admin-bot` + una dependencia en la ruta + tests TDD + README.
