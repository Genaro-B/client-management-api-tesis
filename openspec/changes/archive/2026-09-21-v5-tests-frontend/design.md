# Design: Tests Frontend

## Context

El frontend (`frontend/`, React 18 + Vite 5 + Tailwind 4, JSX plano) no tiene suite de tests: cero dependencias de testing, cero script `test`, cero configuración. El backend sí tiene una suite sólida (pytest, 65 tests, documentada en README con tabla de cobertura); el frontend es la única capa sin verificación automatizada. El código existente es estable y ya está spec-ado en `openspec/specs/client-management-ui/` — este change agrega UNA CAPA NUEVA de verificación sin tocar comportamiento.

Restricciones del entorno:
- `vite@^5.4.0` → **Vitest 2.x obligatorio** (Vitest 3+ exige Vite 6). Fijar `vitest@^2.1.8`.
- `@vitejs/plugin-react@^4.3.0` compatible con Vitest 2.
- React 18.3.1 → `@testing-library/react@^16` con su peer `@testing-library/dom@^10`.
- jsdom no implementa `window.matchMedia` → mock requerido (lo usa `useTheme`).
- Los textos de la UI y de las aserciones van en español (convención del repo: UI 100% es-AR).

## Goals / Non-Goals

**Goals:**
- Suite de tests con Vitest + RTL + jsdom que corra con `npm test`, aislada del backend.
- Cobertura mínima real: 1 hook (`useTheme`), 1 servicio (`authService`), 5+ componentes (`Pagination`, `StatusBadge`, `Avatar`, `Modal`, `ThemeToggle`), `AuthContext` y página `LoginPage`.
- Tests co-locados junto al fuente (`useTheme.test.js` al lado de `useTheme.js`) — patrón estándar Vitest, fácil de descubrir.
- README documentado: fila ✅ + tabla de cobertura + comando, estilo backend.

**Non-Goals:**
- NO tocar la lógica de producción (cero cambios en componentes/páginas/services existentes; los tests que revelen bugs se reportan, no se parchean en este change salvo decisión explícita).
- NO testear todos los componentes (22) ni todas las páginas (7) — suite representativa, no exhaustiva.
- NO configurar coverage con umbral obligatorio en CI.
- NO migrar a TypeScript, ni cambiar React Router u otra dependencia.
- NO crear pipeline de CI nuevo (el repo ya tiene `tests.yml` para backend; extenderlo queda fuera de alcance).

## Decisions

### D1. Vitest 2.x configurado DENTRO de `vite.config.js` (no archivo aparte)
- **Decisión**: importar `defineConfig` desde `vitest/config` en el `vite.config.js` existente y agregar la key `test`. Un solo archivo de config; los plugins/react/tailwind y el proxy `/api` quedan intactos porque `vitest/config` re-exporta el `defineConfig` de Vite.
- **Alternativas**: `vitest.config.js` separado (duplica config, hay que mergear plugins a mano — descartado); `vitest@3` (incompatible con Vite 5 — descartado por constraint).
- Config resultante:
  ```js
  import { defineConfig } from 'vitest/config'
  import react from '@vitejs/plugin-react'
  import tailwindcss from '@tailwindcss/vite'

  export default defineConfig({
    plugins: [react(), tailwindcss()],
    server: { proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true }, '/static': { target: 'http://localhost:8000', changeOrigin: true } } },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: ['./src/test/setup.js'],
    },
  })
  ```
- `globals: true` → `describe/it/expect` globales, sin imports repetidos por archivo; `@testing-library/react` hace auto-cleanup vía `afterEach` global de Vitest.

### D2. Setup global en `frontend/src/test/setup.js`
```js
import '@testing-library/jest-dom'

// jsdom no implementa matchMedia — useTheme lo necesita
window.matchMedia = window.matchMedia || ((query) => ({
  matches: false,
  media: query,
  addEventListener: () => {},
  removeEventListener: () => {},
  addListener: () => {},
  removeListener: () => {},
  dispatchEvent: () => false,
}))

afterEach(() => {
  localStorage.clear()
  sessionStorage.clear()
  document.documentElement.classList.remove('dark')
})
```
- `localStorage`/`sessionStorage` existen en jsdom pero persisten entre tests → limpieza obligatoria para `useTheme` (key `crm_theme`) y `authService` (key `crm_user`).
- `document.documentElement.classList.remove('dark')` evita contaminación de clases entre tests.

### D3. Patrón de mock de axios para servicios (`vi.mock` + `vi.hoisted`)
`authService` crea un instance de axios a nivel de módulo (`axios.create({...})`). Patrón:
```js
const mocks = vi.hoisted(() => ({
  create: vi.fn(),
  post: vi.fn(),
  get: vi.fn(),
}))
vi.mock('axios', () => ({
  default: { create: mocks.create, ... },
}))
```
- `authService.test.js`: `mocks.create.mockReturnValue({ post: mocks.post, ... })` y se asertan llamadas (`/auth/login`, payload `{ email }`) + mapeo de respuesta (id, email, nombre, role).
- `AuthContext.test.js`: se mockea DIRECTAMENTE el módulo servicio (`vi.mock('../services/authService.js')`) en vez de axios — más simple y aísla el contexto: `login` mockeado resuelve un usuario, `getStoredUser` mockeado devuelve sesión previa. Mismo criterio para `sonner` (`vi.mock('sonner', () => ({ toast: { success: vi.fn(), error: vi.fn() } }))`).

### D4. Mocks para páginas
- `LoginPage.test.jsx`: `vi.mock('../hooks/useAuth.js')` devolviendo un `useAuth` controlado (login/loading/error/setError) + `MemoryRouter` (no hay server de backend ni Router real; `useNavigate` necesita el Router). NO se renderiza `AuthProvider` real — se prueba la página aislada.
- Alternativa evaluada: renderizar `LoginPage` con `AuthProvider` real + `authService` mockeado. Descartada: duplica el coverage del `AuthContext.test` sin aportar valor; el test de la página debe enfocarse en el contrato visual/interacción.

### D5. Convenciones de tests (repo)
- Archivos co-locados: `src/hooks/useTheme.test.js`, `src/components/Pagination.test.jsx`, `src/state/AuthContext.test.jsx`, etc. — los de JSX usan `.test.jsx` por consistencia con los fuentes.
- Aserciones en español, assertEquals sobre comportamiento observable (texto visible, disabled, llamadas, clases `dark` en `<html>`), NO sobre implementación interna.
- Interacciones con `@testing-library/user-event` (`userEvent.setup()`), nunca `fireEvent` salvo casos específicos.
- Queries por rol/texto (`getByRole('button', { name: ... })`, `getByText`) — accesibilidad primero.
- Cada archivo: tests de comportamiento real; mínimo 2-3 casos con triángulos (happy path + edge case).

### D6. Matriz de archivos de test planificada (objetivo ~29 tests)

| Archivo | Tests | Cubre |
|---------|-------|-------|
| `src/hooks/useTheme.test.js` | 4 | init desde localStorage (`dark`/`light`), fallback a `matchMedia`, toggle + persistencia, clase `dark` en `<html>` |
| `src/services/authService.test.js` | 3 | login → POST `/api/v1/auth/login` con `{ email }` + mapeo de respuesta; `getStoredUser` (null sin sesión / parseo); `saveUser` → roundtrip con storage |
| `src/components/Pagination.test.jsx` | 4 | rango "Mostrando X–Y de Z"; Anterior disabled en página 1; Siguiente llama `onPageChange(page+1)`; sin controles cuando `totalPages === 1` |
| `src/components/StatusBadge.test.jsx` | 3 | `activo=true` → "Activo"; `activo=false` → "Inactivo"; `activo=1` (número) → "Activo" |
| `src/components/Avatar.test.jsx` | 3 | iniciales "JP" para Juan Pérez; uppercase; `src` → renderiza `<img>` con alt |
| `src/components/Modal.test.jsx` | 3 | renderiza title/children; Escape → `onClose`; click backdrop → `onClose`; click X → `onClose` (4 asserts en 3 tests) |
| `src/components/ThemeToggle.test.jsx` | 2 | muestra Moon en claro y Sun en oscuro; click invierte (usa `useTheme` real + setup matchMedia) |
| `src/state/AuthContext.test.jsx` | 5 | init restaura usuario de `getStoredUser`; login ok setea user + toast; login error setea error y relanza; logout limpia user + sessionStorage + toast; `isAdmin`/`isAuthenticated` derivados |
| `src/pages/LoginPage.test.jsx` | 3 | render del form; submit con email válido llama `login` y navega a `/dashboard`; quick login admin llama login con `admin@utn.edu.ar` |
| **Total** | **~30** | 1 hook + 1 servicio + 5 componentes + 1 context + 1 página |

> La cantidad exacta la define la implementación (TDD: cada archivo arranca RED y se cierra GREEN). La tabla del README refleja los números finales reales.

### D7. README (mismo estilo que sección backend)
1. En "Próximas Implementaciones": mover la fila `Tests Frontend` al bloque ✅ Implementado → `| **Tests Frontend** | ✅ Implementado | Suite de tests con Vitest + React Testing Library: hooks, servicios, componentes, contexto y páginas (~30 tests en jsdom). |`
2. En `## 🧪 Tests`, después del bloque backend, agregar subsección:
   ```markdown
   ### Tests Frontend

   | Archivo | Tests | ¿Qué cubre? |
   |---------|-------|-------------|
   | `src/hooks/useTheme.test.js` | 4 | Tema: localStorage, matchMedia, toggle, clase dark |
   | ... | ... | ... |

   **Total: ~30 tests · jsdom · sin backend**

   ```bash
   cd frontend
   npm install        # primera vez (instala devDeps de testing)
   npm test           # corrida única
   npm run test:watch # modo watch
   ```
   ```

## Risks / Trade-offs

- **[Versión incorrecta de Vitest]** → Fijar `vitest@^2.1.8` explícitamente en la instalación; el smoke test (task 1.5) valida que el runner arranca con la config antes de escribir tests.
- **[Tests frágiles por estado global compartido]** → Setup central limpia storage y clase `dark` en `afterEach`; cada test usa `userEvent.setup()` fresca.
- **[`@testing-library/react@16` exige `@testing-library/dom` como peer]** → Instalarla explícitamente para evitar warnings de peer deps de npm.
- **[Mock demasiado acoplado a axios (`create` + métodos)]** → Si un service cambia de patrón, hay que actualizar su mock; mitigado mockeando el servicio directo en tests de nivel superior (AuthContext) y axios solo en el test del servicio.
- **[Logica de producción con bug descubierto por los tests]** → Se reporta como issue; NO se cambia lógica de producción dentro de este change salvo decisión explícita del usuario (non-goal).

## Migration Plan

1. Instalar devDeps → 2. Config vitest + setup → 3. Escribir/cerrar tests por capa (hooks → services → componentes → context → página) → 4. README.
2. Rollback: revert de los commits del change (config aditiva, files de test removibles, cero impacto en build de producción). El build (`npm run build`) verificado al final garantiza que la config de Vitest no rompió Vite.

## Open Questions

- Ninguna bloqueante. Decisión menor a confirmar en apply: si `npm test -- --coverage` se usa solo ad-hoc (sin umbral en CI) — default: sí, solo ad-hoc.