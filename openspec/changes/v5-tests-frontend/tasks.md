## 1. Configuración de Vitest + setup

- [x] 1.1 Instalar devDependencies en `frontend/`: `npm i -D vitest@^2.1.8 jsdom@^25 @testing-library/react@^16 @testing-library/dom@^10 @testing-library/jest-dom@^6 @testing-library/user-event@^14` (Vitest 2.x obligatorio — Vite del proyecto es 5; `@testing-library/dom` es peer dep de RTL 16)
- [x] 1.2 Actualizar `frontend/vite.config.js`: importar `defineConfig` desde `vitest/config` (re-exporta el de Vite, plugins/proxy intactos) y agregar `test: { environment: 'jsdom', globals: true, setupFiles: ['./src/test/setup.js'] }`
- [x] 1.3 Crear `frontend/src/test/setup.js`: import de `@testing-library/jest-dom`, mock de `window.matchMedia` (jsdom no lo implementa; `useTheme` lo necesita), y `afterEach` que limpie `localStorage`/`sessionStorage` y quite la clase `dark` de `<html>`
- [x] 1.4 Agregar en `frontend/package.json` los scripts `"test": "vitest run"` y `"test:watch": "vitest"`
- [x] 1.5 Smoke test de configuración: correr `npm test` en `frontend/` → el runner arranca con la config (0 specs, sin errores de setup) y `npm run build` sigue verde con la config modificada

## 2. Hooks y servicios

- [x] 2.1 Escribir `frontend/src/hooks/useTheme.test.js` (RED/GREEN): init desde `localStorage` (`crm_theme = 'dark'` → `dark=true`; `'light'` → `false`), fallback a `matchMedia` cuando no hay storage, toggle cambia estado y persiste en localStorage, y el `useEffect` agrega/remueve la clase `dark` en `document.documentElement`
- [x] 2.2 Escribir `frontend/src/services/authService.test.js` con `vi.mock('axios')` (`vi.hoisted` + `create.mockReturnValue({ post, get })`): `login(email)` hace POST a `/api/v1/auth/login` con `{ email }` y mapea la respuesta (id, email, nombre, apellido, role, avatar=null), `getStoredUser` devuelve null sin sesión y parseea el JSON guardado, `saveUser` hace roundtrip con `sessionStorage`
- [x] 2.3 Correr `npm test` → todos los tests de hooks/servicios en verde

## 3. Componentes

- [x] 3.1 Escribir `frontend/src/components/Pagination.test.jsx`: rango "Mostrando X–Y de Z" (ej. 1–20 de 45, y caso total=0), botón Anterior disabled en página 1, click en Siguiente llama `onPageChange(page+1)`, y NO renderiza controles cuando `totalPages === 1`
- [x] 3.2 Escribir `frontend/src/components/StatusBadge.test.jsx`: `activo=true` → "Activo", `activo=false` → "Inactivo", `activo=1` (número) → "Activo"
- [x] 3.3 Escribir `frontend/src/components/Avatar.test.jsx`: iniciales "JP" para "Juan"+"Pérez", uppercase, y con `src` renderiza `<img>` con el alt correcto
- [x] 3.4 Escribir `frontend/src/components/Modal.test.jsx` con `userEvent`: renderiza title y children, Escape invoca `onClose`, click en el backdrop invoca `onClose`, click en el botón X invoca `onClose`
- [x] 3.5 Escribir `frontend/src/components/ThemeToggle.test.jsx` (usa `useTheme` real + matchMedia del setup): muestra Moon en modo claro y Sun en modo oscuro, click del botón invierte el tema
- [x] 3.6 Correr `npm test` → los 5 componentes en verde

## 4. Context y página

- [x] 4.1 Escribir `frontend/src/state/AuthContext.test.jsx` mockeando `../services/authService.js` y `sonner`: init restaura usuario de `getStoredUser`, login exitoso setea user y dispara toast de bienvenida, login con error setea `error` y relanza, logout limpia user/sessionStorage y dispara toast, y `isAdmin`/`isAuthenticated` derivan de `user`
- [x] 4.2 Escribir `frontend/src/pages/LoginPage.test.jsx` mockeando `../hooks/useAuth.js` + `MemoryRouter`: renderiza el form con título "Iniciar sesión", submit con email válido llama `login(email)` y navega a `/dashboard`, quick login de admin llama `login('admin@utn.edu.ar')`, y muestra el error cuando `useAuth` lo provee
- [x] 4.3 Correr `npm test` → suite completa en verde (~30 tests)

## 5. README y verificación final

- [x] 5.1 README — Próximas Implementaciones: mover la fila `Tests Frontend` al bloque ✅ Implementado con descripción actualizada (Vitest + RTL, hooks/servicios/componentes/contexto/páginas)
- [x] 5.2 README — sección `## 🧪 Tests`: agregar subsección "Tests Frontend" con tabla de cobertura (archivo, cantidad de tests, qué cubre — con los números finales reales) y los comandos `npm test` / `npm run test:watch`, en el estilo de la tabla del backend
- [x] 5.3 Correr `npm run build` en `frontend/` → verifica que la config de Vitest (import desde `vitest/config`) no rompió el build de Vite
- [x] 5.4 Verificación final: `npm test` completo en verde (45 tests), `npm run build` verde. **Commit convencional `test(frontend): suite de tests con Vitest + RTL` → a cargo del orquestador (instrucción explícita)**