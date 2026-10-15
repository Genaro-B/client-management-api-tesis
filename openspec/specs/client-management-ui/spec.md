# client-management-ui Specification

## Purpose
TBD - created by archiving change v3-mejoras-interfaz-bot-administrativo. Update Purpose after archive.
## Requirements
### Requirement: Layout dashboard con Sidebar colapsable
El sistema SHALL proporcionar un layout dashboard con un Sidebar lateral colapsable y un área principal con Topbar.
- El Sidebar SHALL tener 220px de ancho en estado expandido y 60px en estado colapsado.
- El Sidebar SHALL tener transición suave (`transition-all duration-300 ease-in-out`) al colapsar/expandir.
- El Sidebar SHALL mostrar un logo CRM con badge azul y nombre "CRM Admin".
- El Sidebar SHALL incluir 4 items de navegación: Dashboard (LayoutDashboard), Clientes (Users activo), Configuración (Settings), Perfil (UserCircle).
- El item activo (Clientes) SHALL tener fondo azul (`#2563eb`) y texto blanco.
- Los items inactivos SHALL tener texto `slate-400` y hover con fondo `rgba(255,255,255,0.07)`.
- El Sidebar SHALL tener un botón de colapso en la parte inferior con icono Menu.

#### Scenario: Sidebar colapsa y expande correctamente
- **WHEN** el usuario hace clic en el botón de colapso del Sidebar
- **THEN** el Sidebar cambia de 220px a 60px con transición suave
- **AND** los textos de los nav items se ocultan
- **AND** el tooltip nativo muestra el nombre del item en modo colapsado

### Requirement: Topbar con título y botón de acción
El sistema SHALL mostrar un Topbar con título de sección, subtítulo y botón "Nuevo Cliente".
- El Topbar SHALL tener altura fija de 64px con fondo blanco y borde inferior `slate-100`.
- El título SHALL mostrar "Clientes" en `text-[17px] font-semibold` con fuente Plus Jakarta Sans.
- El subtítulo SHALL mostrar "Gestión de clientes del CRM" en `text-[12px] text-slate-400`.
- El botón "Nuevo Cliente" SHALL ser un botón primario azul con icono Plus de lucide-react.

#### Scenario: Topbar se renderiza con título y botón
- **WHEN** la aplicación carga
- **THEN** se muestra el Topbar con el título "Clientes", subtítulo "Gestión de clientes del CRM" y un botón "Nuevo Cliente"
- **AND** el botón tiene un icono Plus a la izquierda

### Requirement: Tabla de clientes con 8 columnas
El sistema SHALL mostrar una tabla de clientes con las siguientes 8 columnas: ID, Nombre, Email, Teléfono, DNI, Estado, Fecha registro, Acciones.
- La tabla SHALL tener fondo blanco, bordes redondeados (`rounded-xl`) y sombra suave.
- Los encabezados SHALL usar texto uppercase de 10px font-bold con tracking-widest.
- Las columnas ID, Teléfono, DNI y Fecha SHALL usar fuente DM Mono.
- La columna Nombre SHALL incluir un Avatar con iniciales y el nombre completo.
- La columna Estado SHALL mostrar un StatusBadge con indicador de color.
- Las acciones (Ver, Editar, Eliminar) SHALL ser invisibles por defecto y aparecer al hacer hover sobre la fila.

#### Scenario: Tabla muestra datos de clientes correctamente
- **WHEN** la API responde con una lista de clientes
- **THEN** la tabla renderiza una fila por cliente con las 8 columnas requeridas
- **AND** cada fila muestra avatar con iniciales, nombre, email, teléfono, DNI, badge de estado, fecha y botones de acción

#### Scenario: Acciones de fila aparecen al hacer hover
- **WHEN** el usuario pasa el mouse sobre una fila de la tabla
- **THEN** los botones de acción (Ver, Editar, Eliminar) se vuelven visibles con transición suave

### Requirement: Avatar con iniciales y paleta de colores
El sistema SHALL mostrar un avatar circular con las iniciales del cliente y color determinístico basado en `id % 6`.
- El avatar en tabla SHALL ser de 32x32px con fuente 11px font-bold.
- El avatar en modal de detalle SHALL ser de 56x56px con fuente 18px font-bold.
- La paleta SHALL rotar entre 6 colores: blue, violet, emerald, amber, rose, cyan.

#### Scenario: Avatar muestra iniciales correctas
- **WHEN** el cliente tiene nombre "Juan" y apellido "Pérez"
- **THEN** el avatar muestra "JP" en uppercase

#### Scenario: Color de avatar es determinístico por ID
- **WHEN** el cliente tiene ID = 3
- **THEN** el avatar usa el color correspondiente a `3 % 6 = 3` (amber)

### Requirement: StatusBadge con indicador de estado
El sistema SHALL mostrar un badge de estado con indicador circular de color.
- El badge para estado "Activo" SHALL tener fondo `emerald-50`, texto `emerald-700`, anillo `emerald-200` y punto verde (`#10b981`).
- El badge para estado "Inactivo" SHALL tener fondo `slate-100`, texto `slate-500`, anillo `slate-200` y punto gris (`#94a3b8`).
- El badge SHALL ser pill-shaped (`rounded-full`) con padding `py-1 px-2.5`.

#### Scenario: Badge muestra estado Activo correctamente
- **WHEN** el cliente tiene estado "Activo"
- **THEN** el badge muestra texto "Activo" con fondo verde, texto verde y punto verde

#### Scenario: Badge muestra estado Inactivo correctamente
- **WHEN** el cliente tiene estado "Inactivo"
- **THEN** el badge muestra texto "Inactivo" con fondo gris, texto gris y punto gris

### Requirement: Filtros de búsqueda y estado
El sistema SHALL proporcionar filtros para buscar y filtrar clientes.
- El filtro de búsqueda SHALL ser un input con icono Search que filtra por nombre, email, teléfono o DNI.
- El filtro de estado SHALL ser un dropdown con opciones "Todos", "Activo" e "Inactivo".
- El filtro de fecha SHALL NO estar implementado funcionalmente pero SHALL aparecer como placeholder visual.
- El botón "Limpiar" SHALL resetear todos los filtros a su valor por defecto.

#### Scenario: Búsqueda por texto filtra la tabla
- **WHEN** el usuario escribe "Juan" en el campo de búsqueda
- **THEN** la tabla muestra solo los clientes cuyo nombre, email, teléfono o DNI contienen "Juan"

#### Scenario: Filtro por estado filtra la tabla
- **WHEN** el usuario selecciona "Activo" en el filtro de estado
- **THEN** la tabla muestra solo los clientes con estado "Activo"

#### Scenario: Botón Limpiar resetea filtros
- **WHEN** el usuario hace clic en "Limpiar"
- **THEN** el campo de búsqueda se vacía, el filtro de estado vuelve a "Todos" y la tabla muestra todos los clientes

### Requirement: Modal de detalle de cliente
El sistema SHALL mostrar un modal con la información completa del cliente al hacer clic en "Ver".
- El modal SHALL mostrar avatar grande (56x56px), nombre completo, email y estado.
- El modal SHALL mostrar una grilla de datos: ID, DNI, Teléfono, Dirección, Fecha de registro.
- El modal SHALL incluir un botón "Editar" que abre el modal de edición.
- El modal SHALL cerrarse al hacer clic en la X, en el backdrop, o con tecla Escape.

#### Scenario: Modal de detalle muestra información del cliente
- **WHEN** el usuario hace clic en "Ver" en una fila de cliente
- **THEN** se abre un modal con el avatar grande del cliente, nombre, email, estado, y todos los datos personales

#### Scenario: Modal de detalle cierra correctamente
- **WHEN** el modal de detalle está abierto y el usuario hace clic en el backdrop
- **THEN** el modal se cierra

### Requirement: Modal de formulario para crear/editar cliente
El sistema SHALL mostrar un modal con formulario para crear o editar un cliente.
- El formulario SHALL incluir campos: Nombre, Apellido, Email, Teléfono, DNI, Dirección, Estado (select).
- Los campos SHALL usar labels uppercase de 10px con tracking-widest.
- El modal en modo edición SHALL estar pre-poblado con los datos del cliente.
- El botón "Guardar" SHALL mostrar spinner y texto "Guardando…" mientras la operación está en curso.
- Los campos SHALL estar deshabilitados durante el guardado.

#### Scenario: Modal de creación muestra formulario vacío
- **WHEN** el usuario hace clic en "Nuevo Cliente"
- **THEN** se abre un modal con título "Nuevo Cliente" y todos los campos vacíos

#### Scenario: Modal de edición muestra formulario pre-poblado
- **WHEN** el usuario hace clic en "Editar" en una fila de cliente
- **THEN** se abre un modal con título "Editar Cliente" y los campos pre-poblados con los datos del cliente

#### Scenario: Formulario muestra estado de guardado
- **WHEN** el usuario envía el formulario y la operación está en curso
- **THEN** los campos se deshabilitan y el botón muestra un spinner con texto "Guardando…"

### Requirement: Modal de confirmación para eliminar cliente
El sistema SHALL mostrar un modal de confirmación antes de eliminar un cliente.
- El modal SHALL mostrar un icono AlertCircle rojo con texto de advertencia.
- El modal SHALL mostrar el nombre completo del cliente a eliminar.
- El modal SHALL tener botón "Cancelar" (secondary) y "Eliminar" (destructive).
- El botón "Eliminar" SHALL mostrar spinner y texto "Eliminando…" durante la operación.

#### Scenario: Confirmación de eliminación muestra datos del cliente
- **WHEN** el usuario hace clic en "Eliminar" en una fila de cliente
- **THEN** se abre un modal de confirmación con el nombre del cliente y botones "Cancelar" y "Eliminar"

#### Scenario: Eliminación exitosa muestra toast y cierra modal
- **WHEN** el usuario confirma la eliminación y la API responde exitosamente
- **THEN** el modal se cierra, el cliente se elimina de la tabla, y se muestra un toast de éxito

### Requirement: Estados de UI (Loading, Error, Empty)
El sistema SHALL manejar los estados de carga, error y sin resultados.
- **Loading**: SHALL mostrar un spinner centrado con texto "Cargando clientes…" mientras se consulta la API.
- **Error**: SHALL mostrar icono AlertCircle, mensaje de error y botón "Reintentar conexión".
- **Empty**: SHALL mostrar icono Inbox, texto "No hay clientes" y subtítulo "No se encontraron clientes que coincidan con tu búsqueda" cuando no hay resultados.

#### Scenario: Estado loading se muestra durante la carga
- **WHEN** la aplicación está consultando la API
- **THEN** se muestra un spinner centrado con el texto "Cargando clientes…"

#### Scenario: Estado error permite reintentar
- **WHEN** la API responde con error
- **THEN** se muestra un icono de error, mensaje descriptivo y un botón "Reintentar conexión"
- **AND** al hacer clic en "Reintentar conexión" se vuelve a consultar la API

#### Scenario: Estado empty se muestra cuando no hay resultados
- **WHEN** no hay clientes que coincidan con los filtros activos
- **THEN** se muestra un icono Inbox y el mensaje "No hay clientes"

### Requirement: Notificaciones toast con sonner
El sistema SHALL mostrar notificaciones toast para todas las operaciones CRUD usando la librería sonner.
- Operación exitosa SHALL mostrar `toast.success()` con mensaje descriptivo.
- Operación fallida SHALL mostrar `toast.error()` con mensaje descriptivo.
- Las notificaciones SHALL usar `richColors` y `closeButton`.
- Posición SHALL ser top-right.

#### Scenario: Toast de éxito al crear cliente
- **WHEN** la creación de un cliente es exitosa
- **THEN** se muestra un toast con "Cliente creado correctamente"

#### Scenario: Toast de error al editar cliente
- **WHEN** la actualización de un cliente falla
- **THEN** se muestra un toast con "Error al actualizar el cliente"

### Requirement: Service layer para API REST
El sistema SHALL proporcionar un módulo de servicios que centralice todas las llamadas a la API REST.
- `getClients(params)` SHALL hacer GET a `/api/v1/clientes` con filtros query params.
- `getClient(id)` SHALL hacer GET a `/api/v1/clientes/{id}`.
- `createClient(data)` SHALL hacer POST a `/api/v1/clientes` con body JSON.
- `updateClient(id, data)` SHALL hacer PUT a `/api/v1/clientes/{id}` con body JSON.
- `deleteClient(id)` SHALL hacer DELETE a `/api/v1/clientes/{id}`.
- Todos los servicios SHALL usar `fetch` nativo (sin axios).
- Todos los servicios SHALL manejar errores y lanzar excepciones con mensaje descriptivo.

#### Scenario: getClients retorna lista de clientes
- **WHEN** se llama a `getClients()` con parámetros de filtro
- **THEN** se ejecuta un GET a `/api/v1/clientes` con los query params correspondientes
- **AND** retorna el array de clientes parseado

#### Scenario: Servicio maneja error de red
- **WHEN** la API no responde (error de red)
- **THEN** el servicio lanza un error con mensaje "Error de conexión con el servidor"

### Requirement: Custom hook useClients
El sistema SHALL proporcionar un custom hook `useClients` que gestione el estado de la pantalla de clientes.
- `useClients()` SHALL retornar: `{ clients, loading, error, filters, setFilters, selectedClient, setSelectedClient, modalState, openModal, closeModal, createClient, updateClient, deleteClient, refreshClients }`.
- El hook SHALL usar `useState` y `useEffect` para gestionar estado y efectos.
- El hook SHALL llamar a los servicios del service layer.
- El hook SHALL manejar loading state, error state y success state.
- El hook SHALL disparar toast notifications via sonner después de cada operación CRUD.

#### Scenario: useClients carga clientes al montar
- **WHEN** el hook se monta
- **THEN** se llama a `getClients()` con los filtros iniciales
- **AND** loading es `true` durante la carga y `false` al completar
- **AND** clients contiene el array de clientes al finalizar

#### Scenario: useClients maneja error de carga
- **WHEN** la llamada inicial a `getClients()` falla
- **THEN** loading pasa a `false` y error contiene el mensaje de error

#### Scenario: useClients filtra clientes al cambiar filtros
- **WHEN** los filtros cambian (búsqueda o estado)
- **THEN** se llama a `getClients()` con los nuevos filtros y la tabla se actualiza

### Requirement: Paginación en tablas de clientes y productos

El sistema SHALL paginar las tablas de Clientes y Productos de a 20 registros por página, con controles de navegación "← 1 2 3 →".

- La paginación SHALL ser server-side: los hooks envían `limit=20` y `offset` calculado desde la página actual a los endpoints existentes.
- El total de páginas SHALL derivarse del campo `total` que devuelve la API (`ceil(total / 20)`).
- Los controles SHALL incluir botón anterior, página actual, total de páginas y botón siguiente; ambos botones SHALL deshabilitarse en los extremos.
- Al cambiar los filtros de búsqueda, la página SHALL volver a la página 1.
- Se SHALL mostrar el rango visible al pie de la tabla (ej.: "Mostrando 1–20 de 45").
- Al cambiar de página SHALL mostrarse el estado de carga de la tabla.

#### Scenario: La tabla muestra solo 20 registros por página
- **WHEN** hay 45 clientes y la tabla está paginada
- **THEN** la primera página muestra 20 clientes
- **AND** los controles indican página 1 de 3

#### Scenario: Avanzar de página muestra los siguientes registros
- **WHEN** el usuario hace clic en el botón siguiente estando en la página 1
- **THEN** la tabla carga y muestra los registros 21 al 40

#### Scenario: Cambiar filtros reinicia a la página 1
- **WHEN** el usuario está en la página 3 y modifica la búsqueda o el filtro de estado
- **THEN** la tabla vuelve a la página 1 con los resultados filtrados

#### Scenario: Última página deshabilita el botón siguiente
- **WHEN** el usuario está en la última página
- **THEN** el botón siguiente está deshabilitado

### Requirement: Exportar a Excel con confirmación

El sistema SHALL permitir descargar las listas de Clientes y Productos en Excel (.xlsx) desde el botón "Exportar Excel" de la barra superior.

- La exportación SHALL usar los endpoints existentes `GET /api/v1/clients/export` y `GET /api/v1/products/export`.
- Al completar la descarga exitosamente, el sistema SHALL mostrar un toast de éxito.
- Si la descarga falla, el sistema SHALL mostrar un toast de error.

#### Scenario: Exportar clientes descarga el archivo y confirma
- **WHEN** el usuario hace clic en "Exportar Excel" en la pantalla de Clientes y la descarga es exitosa
- **THEN** se descarga el archivo `clientes.xlsx`
- **AND** se muestra un toast de éxito

#### Scenario: Exportar productos descarga el archivo y confirma
- **WHEN** el usuario hace clic en "Exportar Excel" en la pantalla de Productos y la descarga es exitosa
- **THEN** se descarga el archivo `productos.xlsx`
- **AND** se muestra un toast de éxito

#### Scenario: Error al exportar muestra toast de error
- **WHEN** la exportación falla (por ejemplo, el backend no responde)
- **THEN** se muestra un toast de error con el motivo

### Requirement: Historial de interacciones en el detalle del cliente

El sistema SHALL mostrar el historial completo de interacciones del cliente dentro de su modal de detalle, en una sección "Historial de interacciones".

- La sección SHALL cargar las interacciones desde `GET /api/v1/interactions/?client_id=<id>` al abrir el modal.
- Cada interacción SHALL mostrar fecha/hora en formato es-AR, fuente, intent y un resumen del payload.
- SHALL mostrar un estado de carga mientras se consulta la API.
- SHALL mostrar un estado vacío ("Sin interacciones registradas") cuando el cliente no tiene interacciones.
- El historial SHALL ordenarse de más reciente a más antigua.

#### Scenario: El modal muestra las interacciones del cliente
- **WHEN** se abre el modal de detalle de un cliente que tiene interacciones registradas
- **THEN** la sección "Historial de interacciones" lista sus interacciones con fecha/hora, fuente e intent

#### Scenario: Cliente sin interacciones muestra estado vacío
- **WHEN** se abre el modal de detalle de un cliente sin interacciones
- **THEN** la sección muestra "Sin interacciones registradas"

#### Scenario: Error al cargar el historial se muestra en la sección
- **WHEN** la carga del historial de interacciones falla
- **THEN** la sección muestra un mensaje de error con opción de reintentar

### Requirement: Toasts de confirmación en todas las operaciones de gestión

El sistema SHALL mostrar toasts de éxito o error para TODAS las operaciones de gestión: crear, editar y eliminar clientes y productos, exportar a Excel, asignar/quitar productos de un cliente, actualizar cantidades y restaurar clientes o productos inactivos.

#### Scenario: Toast de éxito al restaurar un cliente inactivo
- **WHEN** un cliente inactivo se restaura exitosamente
- **THEN** se muestra un toast de éxito

#### Scenario: Toast de éxito al restaurar un producto inactivo
- **WHEN** un producto inactivo se restaura exitosamente
- **THEN** se muestra un toast de éxito

#### Scenario: Toast de error en operaciones de productos asignados
- **WHEN** una operación sobre productos asignados falla
- **THEN** se muestra un toast de error con el motivo

