## Context

El backend del módulo de gestión de clientes está completo (FastAPI + SQLAlchemy + Alembic) con los endpoints REST en `/api/v1/clients`. No existe ningún frontend en el proyecto.

La UI debe implementarse como una aplicación standalone React 18 + Vite + Tailwind CSS v4, siguiendo el sistema de diseño definido en `Docs/desing-system.md` y la especificación de componentes en `Docs/frontend-spec.md`.

El proyecto es greenfield — no hay configuración previa de Vite, React, Tailwind o cualquier dependencia frontend.

## Goals / Non-Goals

**Goals:**
- Crear una SPA React 18 con Vite como bundler
- Implementar el layout dashboard: Sidebar colapsable + Topbar + área de contenido
- Implementar la pantalla de gestión de clientes con tabla de 8 columnas, avatares con iniciales y badges de estado
- Implementar filtros de búsqueda (texto, estado, fecha)
- Implementar 3 modales: Ver detalle, Crear/Editar cliente, Eliminar con confirmación
- Implementar service layer para llamadas a la API REST
- Implementar custom hook `useClients` para estado y lógica de negocio
- Cubrir todos los estados de UI: loading, error, empty, success notifications
- Usar Tailwind CSS v4 para estilos (sin CSS modules ni styled-components)
- Usar lucide-react para iconografía
- Usar sonner para notificaciones toast

**Non-Goals:**
- No incluye autenticación ni login (queda para otro change)
- No incluye despliegue ni configuración de producción (Docker, CI/CD)
- No incluye testing automatizado (se abordará en change separado)
- No incluye otros módulos del CRM (solo clientes)
- No incluye paginación server-side (se entrega con paginación básica o scroll)
- No incluye i18n ni multi-idioma

## Decisions

### 1. Vite + React como stack frontend
**Decisión**: Usar Vite con template React y JavaScript (no TypeScript por ahora).
**Razón**: Vite es el estándar moderno para SPA con React. Ofrece HMR rápido, build optimizado y configuración mínima. Se usará JSX en lugar de TSX para reducir fricción inicial.
**Alternativa considerada**: Create React App (deprecado), Next.js (overkill para SPA simple).

### 2. Tailwind CSS v4 con @tailwindcss/vite plugin
**Decisión**: Usar Tailwind CSS v4 con el plugin oficial de Vite.
**Razón**: Tailwind v4 cambió a un modelo CSS-first sin `tailwind.config.js`. El plugin `@tailwindcss/vite` se integra directamente con Vite. Las variables CSS personalizadas se definen en `app.css` con `@theme`.
**Alternativa considerada**: CSS Modules (más boilerplate), styled-components (runtime overhead).

### 3. Font loading con Google Fonts vía CSS @import
**Decisión**: Cargar Plus Jakarta Sans, Inter y DM Mono mediante `@import url()` en `app.css`.
**Razón**: Las tres fuentes son de Google Fonts. El approach `@import` es simple, evita config adicional y funciona out-of-the-box con Vite. Se usarán weights 400, 500, 600, 700 según requiera el sistema de diseño.
**Alternativa considerada**: fontsource npm packages (más bundles, sin diferencia práctica).

### 4. Sin router (single-page dashboard)
**Decisión**: No usar React Router. La aplicación es una sola pantalla de dashboard.
**Razón**: El alcance es una única pantalla de gestión de clientes. Introducir un router agrega complejidad innecesaria. Si en el futuro se agregan más pantallas, se puede incorporar React Router.
**Alternativa considerada**: React Router DOM (innecesario para una sola vista).

### 5. Estado local con custom hooks, no estado global
**Decisión**: Usar el custom hook `useClients` con `useState` y `useEffect` para toda la lógica de estado. Sin Redux, Zustand ni Context API.
**Razón**: El estado es local a una sola pantalla. No hay estado compartido entre rutas. Un custom hook es suficiente y evita dependencias adicionales.
**Alternativa considerada**: Zustand (innecesario para estado local), Redux (overkill).

### 6. Estructura de carpetas plana por tipo
**Decisión**: `src/pages/`, `src/components/`, `src/services/`, `src/hooks/`.
**Razón**: Sigue la especificación de `Docs/frontend-spec.md`. Es el estándar para proyectos React pequeños/medianos. Evita sobre-arquitectura inicial.
**Alternativa considerada**: Feature folders (mejor para proyectos grandes, premature optimization acá).

### 7. Axios como HTTP client
**Decisión**: Usar `axios` en lugar de `fetch` nativo para las llamadas a la API.
**Razón**: axios maneja automáticamente la serialización JSON, tiene mejor manejo de errores HTTP (los 4xx/5xx son rejected promises, no requieren check manual de `response.ok`), permite interceptors para logging/headers, y tiene una API más limpia para agregar query params y headers.
**Alternativa considerada**: fetch nativo (más boilerplate, error handling manual), ky (menos conocido).

### 8. API base URL vía constante
**Decisión**: Definir `API_BASE_URL = '/api/v1'` como constante en el service layer.
**Razón**: El backend está en el mismo origen (o se proxy con Vite). Usar una constante permite cambiarla fácilmente. En desarrollo, Vite proxy redirige `/api` al backend.
**Alternativa considerada**: Variables de entorno VITE_API_URL (se puede agregar después si es necesario).

### 9. Nombres de endpoints en español (clientes)
**Decisión**: Los endpoints en el service se llaman `getClients`, `getClient`, `createClient`, `updateClient`, `deleteClient`, pero la URL es `/api/v1/clientes` (como está implementado en el backend).
**Razón**: Coherencia con el backend existente que expone `/clientes`. Los nombres de funciones en inglés siguen convención de código.

### 10. Modal como componente genérico reutilizable
**Decisión**: Crear un componente `Modal` base que maneje overlay, backdrop click, tecla Escape, y transiciones. Los modales específicos (ClientDetailsModal, ClientFormModal, DeleteClientModal) lo usan.
**Razón**: Los tres modales comparten la misma estructura (overlay, backdrop, shell, header, body). Extraer un componente base evita duplicación.
**Alternativa considerada**: Headless UI Dialog (dependencia externa innecesaria).

### 11. Avatar con paleta de colores por id % 6
**Decisión**: Calcular el color del avatar basado en `client.id % 6` usando un array de 6 pares de colores Tailwind.
**Razón**: Especificado en el sistema de diseño. Da variedad visual determinística sin almacenar preferencias.
**Alternativa considerada**: Colores aleatorios (inconsistentes entre renders), colores fijos (sin variedad).

## Risks / Trade-offs

- **[Risk] APIs cambian en el backend**: Si el backend modifica la estructura de la respuesta, el frontend se rompe. → **Mitigación**: El service layer centraliza todas las llamadas; los cambios se hacen en un solo lugar.
- **[Trade-off] Sin TypeScript**: JSX puro sin tipos significa menos seguridad en desarrollo. → **Mitigación**: El equipo conoce bien la estructura de datos; se puede migrar a TypeScript en un change futuro.
- **[Risk] Tailwind v4 es reciente**: Hay menos ejemplos y la configuración cambió respecto a v3. → **Mitigación**: La configuración es más simple (CSS-first), no se necesitan plugins complejos.
- **[Trade-off] Sin tests**: No hay red de seguridad para refactors. → **Mitigación**: Se prioriza entrega rápida; testing se agenda como change separado.
- **[Risk] Sin router**: Si se agregan más pantallas, habrá que refactorizar. → **Mitigación**: Agregar React Router es un cambio no disruptivo cuando sea necesario.
