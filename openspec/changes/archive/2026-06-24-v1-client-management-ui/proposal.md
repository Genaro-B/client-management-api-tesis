## Why

El backend de gestión de clientes (CRUD completo en FastAPI + SQLAlchemy) ya está implementado y funcional. Falta la interfaz de usuario que permita a los operadores del CRM realizar las operaciones de listar, buscar, crear, editar y eliminar clientes de forma visual. Sin esta UI, el módulo de clientes no es utilizable por usuarios no técnicos.

## What Changes

- Crear una **aplicación frontend standalone** con React 18 + Vite + Tailwind CSS v4
- Implementar el **layout dashboard** completo: Sidebar colapsable, Topbar con título y botón de acción
- Implementar la **pantalla de gestión de clientes** con tabla de 8 columnas (ID, Nombre, Email, Teléfono, DNI, Estado, Fecha registro, Acciones)
- Implementar **filtros** de búsqueda por texto, por estado (Activo/Inactivo) y por fecha
- Implementar **tres modales**: Ver detalle, Editar/Crear cliente, Eliminar con confirmación
- Implementar **servicios de API** para consumir el backend existente en `/api/v1/clients`
- Implementar **todos los estados de UI**: loading, error, empty, success notifications
- Integrar **sonner** para notificaciones toast en operaciones CRUD
- Integrar **lucide-react** para todos los iconos del sistema de diseño

## Capabilities

### New Capabilities
- `client-management-ui`: Pantalla completa de gestión de clientes con tabla, filtros, modales CRUD, estados de carga/error/vacío, y notificaciones toast. Consume la API REST existente en `/api/v1/clients`.

### Modified Capabilities
- Ninguna. No existen specs previas en este proyecto.

## Impact

- **Nuevo proyecto frontend** en la raíz del repositorio (o en `/frontend/`)
- **Dependencias nuevas**: react 18, react-dom 18, lucide-react, sonner, tailwindcss v4, @tailwindcss/vite
- **API existente**: El frontend consumirá los endpoints ya implementados: `GET /api/v1/clients`, `GET /api/v1/clients/{id}`, `POST /api/v1/clients`, `PUT /api/v1/clients/{id}`, `DELETE /api/v1/clients/{id}`
- **Sin impacto en backend**: Solo se añade un consumidor adicional de la API existente
