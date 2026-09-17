## ADDED Requirements

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