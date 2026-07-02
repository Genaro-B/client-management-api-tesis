# Customer Management UI - Frontend Specification

## 1. Objetivo

Este documento define las reglas de implementación del módulo de administración de clientes del sistema CRM.

La interfaz permite realizar operaciones CRUD sobre clientes consumiendo una API REST:

* Listar clientes
* Buscar clientes
* Filtrar clientes
* Crear clientes
* Consultar detalles
* Actualizar información
* Eliminar clientes

La implementación debe respetar el sistema visual definido en el diseño Figma.

---

# 2. Arquitectura de componentes

La pantalla debe dividirse en componentes reutilizables:

```
src/
 ├── pages/
 │    └── ClientsPage
 │
 ├── components/
 │    ├── Sidebar
 │    ├── Topbar
 │    ├── ClientTable
 │    ├── ClientFilters
 │    ├── ClientDetailsModal
 │    ├── ClientFormModal
 │    ├── DeleteClientModal
 │    ├── StatusBadge
 │    └── Avatar
 │
 ├── services/
 │    └── clientService
 │
 └── hooks/
      └── useClients
```

---

# 3. Layout general

La aplicación utiliza una estructura dashboard:

* Sidebar lateral colapsable.
* Área principal con Topbar.
* Zona de contenido con tabla y filtros.

Distribución:

```
Dashboard
|
├── Sidebar
|
└── Main Content
      |
      ├── Topbar
      |
      ├── Filters
      |
      └── Client Table
```

---

# 4. Sistema visual

## Tipografía

| Uso            | Fuente            |
| -------------- | ----------------- |
| Títulos        | Plus Jakarta Sans |
| Texto general  | Inter             |
| Datos técnicos | DM Mono           |

DM Mono debe utilizarse obligatoriamente para:

* IDs
* DNI
* Teléfonos
* Fechas

---

# 5. Paleta de colores

## Colores principales

| Elemento        | Valor   |
| --------------- | ------- |
| Background      | #f8fafc |
| Texto principal | #0f172a |
| Card            | #ffffff |
| Primario        | #2563eb |
| Error           | #dc2626 |
| Sidebar         | #0f172a |

---

# 6. Componentes principales

## Sidebar

Características:

* Expandido: 220px
* Colapsado: 60px
* Fondo oscuro
* Logo CRM
* Menú con 4 opciones

Estados:

Normal:

* Texto slate-400
* Fondo transparente

Hover:

* Fondo slate-800

Activo:

* Fondo azul
* Texto blanco

---

## Topbar

Elementos:

* Título de sección
* Subtítulo descriptivo
* Botón Nuevo Cliente

Altura:

```
64px
```

---

# 7. Tabla de clientes

Columnas requeridas:

1. ID
2. Nombre
3. Email
4. Teléfono
5. DNI
6. Estado
7. Fecha registro
8. Acciones

Características:

* Cards blancas
* Bordes suaves
* Sombra ligera
* Hover sobre filas

Las acciones aparecen únicamente al pasar el mouse:

* Ver
* Editar
* Eliminar

---

# 8. Modales

## Ver cliente

Debe mostrar:

* Avatar
* Nombre completo
* Datos personales
* Estado
* Fecha creación

Debe incluir acceso directo a edición.

## Editar cliente

Formulario:

Campos:

* Nombre
* Apellido
* Email
* Teléfono
* DNI
* Dirección
* Estado

Estados:

Normal:
Formulario editable.

Guardando:

* Campos bloqueados.
* Spinner visible.
* Texto "Guardando..."

## Eliminar cliente

Debe incluir:

* Alerta visual roja.
* Nombre del cliente.
* Confirmación obligatoria.

Estados:

Eliminando:

* Spinner.
* Botones deshabilitados.

---

# 9. Estados de interfaz

## Loading

Mientras se consulta la API:

Mostrar spinner centrado.

---

## Error

Mostrar:

* Icono de error
* Mensaje descriptivo
* Botón "Reintentar conexión"

---

## Sin resultados

Mostrar:

* Icono vacío
* Mensaje informativo

---

# 10. Notificaciones

Usar sistema Toast mediante Sonner.

Eventos:

Éxito:

* Cliente creado correctamente.
* Cliente actualizado correctamente.
* Cliente eliminado correctamente.

Error:

* Error al guardar.
* Error al eliminar.
* Error de conexión.

---

# 11. Integración API

Servicios requeridos:

GET /clientes

Obtiene listado.

GET /clientes/{id}

Obtiene detalle.

POST /clientes

Crea nuevo cliente.

PUT /clientes/{id}

Actualiza cliente.

DELETE /clientes/{id}

Elimina cliente.

---

# 12. Reglas de implementación

* Todas las acciones destructivas requieren confirmación.
* Los formularios deben validar datos antes de enviar.
* Todas las llamadas API deben manejar loading/error/success.
* Los botones deben mostrar feedback visual.
* Los componentes deben ser reutilizables.
* Mantener separación entre UI y servicios.
