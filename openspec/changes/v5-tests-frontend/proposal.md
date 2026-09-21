# Proposal: Tests Frontend

## Why

El frontend (`client-management-ui`, React 18 + Vite 5) no tiene NINGUNA suite de tests: `package.json` carece de script `test`, no hay Vitest, React Testing Library ni jsdom. Hoy cualquier cambio en componentes (Pagination, Modal, ThemeToggle), hooks (useTheme, useClients) o servicios axios se valida sólo de forma manual, con riesgo de regresiones silenciosas. El README ya promete la fila "**Tests Frontend** | ⏳ Pendiente | Suite de tests con Vitest + React Testing Library para componentes y páginas" en Próximas Implementaciones — este change la hace realidad y la marca como ✅ Implementado.

## What Changes

- Configurar **Vitest 2.x** (compatible con Vite 5 del proyecto) en `frontend/vite.config.js`: `environment: 'jsdom'`, `globals: true`, `setupFiles` con jest-dom e importación desde `vitest/config`.
- Crear setup de tests (`frontend/src/test/setup.js`): import de `@testing-library/jest-dom`, mock de `matchMedia` (jsdom no lo implementa y `useTheme` lo necesita), limpieza de `localStorage/sessionStorage` entre tests.
- Agregar devDependencies: `vitest`, `jsdom`, `@testing-library/react`, `@testing-library/dom`, `@testing-library/jest-dom`, `@testing-library/user-event`.
- Agregar scripts `"test": "vitest run"` y `"test:watch": "vitest"`.
- Escribir tests representativos y de valor real (tests co-locados junto al fuente, estilo `hooks/useTheme.test.js`):
  - Hooks: `useTheme` (localStorage + preferencia del sistema + toggle).
  - Servicios: `authService` (axios mockeado).
  - Componentes (5+): `Pagination`, `StatusBadge`, `Avatar`, `Modal`, `ThemeToggle`.
  - Context: `AuthContext` (login ok/error, logout, restauración de sesión) con `authService` y `sonner` mockeados.
  - Página: `LoginPage` (form submit navega, quick login admin, error visible) con `useAuth` mockeado + `MemoryRouter`.
- Documentar en README: mover la fila "Tests Frontend" a ✅ Implementado y agregar subsección "Tests Frontend" en `## 🧪 Tests` con tabla de cobertura (archivo, cantidad, qué cubre) y comandos, siguiendo el estilo de la sección backend.

## Capabilities

### New Capabilities
- `frontend-testing`: suite de tests del panel web (Vitest + RTL + jsdom), cobertura mínima de áreas (hooks, services, 5+ componentes, context o página), tests aislados sin backend y documentación de ejecución en README.

### Modified Capabilities
- None — los requirements de `client-management-ui` no cambian; sólo se agrega verificación automatizada sobre comportamiento existente.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `frontend/package.json` | Modificado | devDeps nuevas + scripts `test`/`test:watch` |
| `frontend/vite.config.js` | Modificado | Config `test` de Vitest (jsdom, globals, setup) — build/proxy intactos |
| `frontend/src/test/setup.js` | Nuevo | Setup global: jest-dom + mock matchMedia + limpieza storage |
| `frontend/src/{hooks,components,state,pages}/**.test.{js,jsx}` | Nuevo | ~9 archivos de test (~29 casos) co-locados junto al fuente |
| `README.md` | Modificado | Fila ✅ + tabla de cobertura + comandos en sección Tests |

## Risks

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Versión de Vitest incompatible con Vite 5 (Vitest 3+ requiere Vite 6) | Med | Fijar `vitest@^2.1` explícitamente; verificar con smoke test de la configuración |
| Tests frágiles por mocks de `matchMedia`/storage mal limpiados | Med | Mock en setup global + limpieza entre tests |
| CI/servidor sin Node para correr la suite | Bajo | Tests corren localmente con `npm test`; no bloquean el build |

## Rollback Plan

- `git revert` del commit del change (o revert manual): restaurar `package.json`, `vite.config.js`, borrar `src/test/` y los `*.test.{js,jsx}`.
- Los tests son archivos aditivos y la config de Vitest convive con el build de Vite — revertir deja el frontend exactamente como estaba (sin deuda).
- Nota: si el change se mergea por partes, cada commit de tests individual es reversible de forma independiente.

## Dependencies

- Node.js 20+ (ya requerido por el proyecto).
- Ninguna dependencia externa de red para correr los tests (axios y servicios se mockean; no se necesita backend ni API corriendo).

## Success Criteria

- [ ] `npm test` corre la suite completa en **jsdom** con **todos los tests en verde** (~29 casos).
- [ ] Cobertura mínima cumplida: 1 hook, 1 servicio, 5+ componentes, AuthContext y 1 página.
- [ ] Los tests pasan sin backend activo (axios mockeado, sin llamadas de red reales).
- [ ] `npm run build` sigue funcionando con la config modificada de Vite.
- [ ] README: fila "Tests Frontend" en ✅ Implementado + tabla de cobertura + comando, en el estilo de la sección backend.