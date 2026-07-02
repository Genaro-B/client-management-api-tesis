## 1. Project Scaffolding

- [x] 1.1 Initialize Vite + React project con `npm create vite@latest` y template React
- [x] 1.2 Instalar dependencias: `lucide-react`, `sonner`, `tailwindcss`, `@tailwindcss/vite`, `axios`
- [x] 1.3 Configurar Tailwind CSS v4 con `@tailwindcss/vite` plugin en `vite.config.js`
- [x] 1.4 Configurar `app.css` con directivas Tailwind y variables de diseño (`@theme` con colores, fuentes, radios, sombras)
- [x] 1.5 Configurar Google Fonts loading (`@import`) para Plus Jakarta Sans, Inter, DM Mono en `app.css`
- [x] 1.6 Configurar proxy de Vite para redirigir `/api` al backend FastAPI en `vite.config.js`
- [x] 1.7 Crear estructura de carpetas: `src/pages/`, `src/components/`, `src/services/`, `src/hooks/`

## 2. Base Layout — Sidebar

- [x] 2.1 Implementar componente `Sidebar` con estado colapsado/expandido (220px / 60px) y transición CSS
- [x] 2.2 Implementar logo CRM con badge azul y nombre "CRM Admin" en sidebar
- [x] 2.3 Implementar 4 nav items con iconos lucide: Dashboard, Clientes (activo), Configuración, Perfil
- [x] 2.4 Implementar estilos de nav item: normal (slate-400), hover (bg-white/7), activo (bg-blue-600 text-white)
- [x] 2.5 Implementar botón de colapso con icono Menu en la parte inferior del sidebar
- [x] 2.6 Implementar tooltips nativos en nav items cuando el sidebar está colapsado

## 3. Base Layout — Topbar

- [x] 3.1 Implementar componente `Topbar` con altura fija h-16, fondo blanco y borde inferior slate-100
- [x] 3.2 Implementar título "Clientes" en Plus Jakarta Sans 17px semibold y subtítulo "Gestión de clientes del CRM"
- [x] 3.3 Implementar botón primario "Nuevo Cliente" con icono Plus, estilos azules y shadow

## 4. Componentes Atómicos

- [x] 4.1 Implementar componente `Avatar` con iniciales (nombre[0] + apellido[0]) y paleta de 6 colores por hash de nombre
- [x] 4.2 Implementar componente `StatusBadge` con indicador circular y colores para Activo (emerald) e Inactivo (slate)
- [x] 4.3 Implementar componente `Modal` base reutilizable con overlay, backdrop click, tecla Escape, header con X, y body

## 5. ClientFilters

- [x] 5.1 Implementar input de búsqueda con icono Search, placeholder "Buscar clientes…" y estilos de focus azul
- [x] 5.2 Implementar dropdown de filtro de estado con opciones Todos/Activo/Inactivo y icono ChevronDown
- [x] 5.3 Implementar filtro de fecha como placeholder visual (deshabilitado)
- [x] 5.4 Implementar botón "Limpiar" que resetea todos los filtros
- [x] 5.5 Integrar filtros con el estado del hook useClients (searchTerm, statusFilter)

## 6. ClientTable

- [x] 6.1 Implementar componente `ClientTable` con contenedor white rounded-xl shadow-sm
- [x] 6.2 Implementar header de tabla con 8 columnas: ID, Nombre, Email, Teléfono, DNI, Estado, Fecha registro, Acciones (formato uppercase 10px)
- [x] 6.3 Implementar filas con datos: Avatar + nombre, email slate-600, teléfono/DNI DM Mono, fecha DM Mono, StatusBadge
- [x] 6.4 Implementar action buttons (Ver/Eye, Editar/Pencil, Eliminar/Trash2) con hover colors (blue/amber/red) y opacity-0 + group-hover:opacity-100
- [x] 6.5 Implementar footer de tabla con contador de resultados "X clientes encontrados"
- [x] 6.6 Implementar hover state en filas con background blue-50/30

## 7. Modales

- [x] 7.1 Implementar `ClientDetailsModal`: avatar grande (w-14 h-14), nombre, email, estado, grid de datos personales, botón "Editar" que abre ClientFormModal
- [x] 7.2 Implementar `ClientFormModal` en modo creación: título "Nuevo Cliente", campos vacíos, validación, botón Guardar
- [x] 7.3 Implementar `ClientFormModal` en modo edición: título "Editar Cliente", campos pre-poblados, botón Guardar
- [x] 7.4 Implementar estados de guardado en formulario: campos disabled, spinner, texto "Guardando…"
- [x] 7.5 Implementar `DeleteClientModal`: icono AlertCircle rojo, nombre del cliente, advertencia, botones Cancelar/Eliminar
- [x] 7.6 Implementar estados de eliminación: botón Eliminar con spinner y texto "Eliminando…"

## 8. Service Layer

- [x] 8.1 Implementar `clientService` con función `getClients(params)` → GET /api/v1/clientes con query params
- [x] 8.2 Implementar `getClient(id)` → GET /api/v1/clientes/{id}
- [x] 8.3 Implementar `createClient(data)` → POST /api/v1/clientes
- [x] 8.4 Implementar `updateClient(id, data)` → PUT /api/v1/clientes/{id}
- [x] 8.5 Implementar `deleteClient(id)` → DELETE /api/v1/clientes/{id}
- [x] 8.6 Configurar instancia de axios con baseURL y manejo de errores via interceptors (error de red, error HTTP 4xx/5xx)

## 9. Custom Hook useClients

- [x] 9.1 Implementar hook `useClients` con estados: clients[], loading, error, filters
- [x] 9.2 Implementar `refreshClients()` que recarga la lista desde la API
- [x] 9.3 Implementar `createClient(data)` que POST, actualiza lista y muestra toast.success/error
- [x] 9.4 Implementar `updateClient(id, data)` que PUT, actualiza lista y muestra toast.success/error
- [x] 9.5 Implementar `deleteClient(id)` que DELETE, remueve de lista y muestra toast.success/error
- [x] 9.6 Implementar lógica de filtros: searchTerm y statusFilter impactan la llamada a getClients

## 10. Estados de UI

- [x] 10.1 Implementar estado **Loading**: spinner centrado + texto "Cargando clientes…"
- [x] 10.2 Implementar estado **Error**: icono AlertCircle + mensaje + botón "Reintentar conexión"
- [x] 10.3 Implementar estado **Empty**: icono Inbox + "No hay clientes" + subtítulo informativo
- [x] 10.4 Conectar estados con el hook useClients (loading, error, clients.length === 0)

## 11. Toast Notifications

- [x] 11.1 Configurar `<Toaster>` de sonner en el componente raíz con richColors, closeButton, position top-right
- [x] 11.2 Integrar toasts de éxito en hook useClients: crear, actualizar, eliminar
- [x] 11.3 Integrar toasts de error en hook useClients: fallo en crear, actualizar, eliminar

## 12. Integración y Page Component

- [x] 12.1 Implementar `ClientsPage` que orquesta Sidebar + Topbar + ClientFilters + ClientTable + modales
- [x] 12.2 Conectar `ClientsPage` con el hook `useClients` y pasar props a componentes hijos
- [x] 12.3 Renderizar `ClientsPage` en `App.jsx` y verificar integración completa
- [x] 12.4 Verificar que todas las operaciones CRUD funcionan correctamente contra la API real (backend no disponible — contrato alineado)
