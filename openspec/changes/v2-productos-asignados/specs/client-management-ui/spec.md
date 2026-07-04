## MODIFIED Requirements

### Requirement: Modal de detalle de cliente
El sistema SHALL mostrar un modal con la información completa del cliente al hacer clic en "Ver".
- El modal SHALL mostrar avatar grande (56x56px), nombre completo, email y estado.
- El modal SHALL mostrar una grilla de datos: ID, DNI, Teléfono, Dirección, Fecha de registro.
- El modal SHALL mostrar una sección **"Productos Asignados"** con la tabla de productos del cliente.
- El modal SHALL incluir un botón "Editar" que abre el modal de edición.
- El modal SHALL cerrarse al hacer clic en la X, en el backdrop, o con tecla Escape.

#### Scenario: Modal de detalle muestra información del cliente
- **WHEN** el usuario hace clic en "Ver" en una fila de cliente
- **THEN** se abre un modal con el avatar grande del cliente, nombre, email, estado, y todos los datos personales
- **AND** si el cliente tiene productos asignados, se muestra la sección "Productos Asignados"

### Requirement: ClientResponse incluye productos_asignados
El schema de respuesta de clientes SHALL incluir el campo `productos_asignados` como un array de objetos con `producto_id`, `nombre`, `precio` y `cantidad`.

#### Scenario: Cliente sin productos retorna array vacío
- **WHEN** se consulta un cliente sin productos asignados
- **THEN** `productos_asignados` es `[]`

#### Scenario: Cliente con productos retorna array completo
- **WHEN** se consulta un cliente que tiene productos asignados
- **THEN** `productos_asignados` contiene la lista completa de productos
