## ADDED Requirements

### Requirement: Cliente tiene productos asignados
El sistema SHALL permitir asociar productos del catálogo a un cliente, almacenados como un array JSON en la columna `productos_asignados` de la tabla `clients`.
- Cada entrada SHALL contener: `producto_id` (int), `nombre` (string), `precio` (float), `cantidad` (int >= 1).
- El campo SHALL tener valor por defecto `[]` (array vacío).
- El array SHALL persistirse como JSON válido en la base de datos.
- El campo SHALL estar incluido en la respuesta de `GET /api/v1/clients/:id`.

#### Scenario: Cliente nuevo tiene lista vacía por defecto
- **WHEN** se crea un nuevo cliente
- **THEN** su campo `productos_asignados` es `[]`

#### Scenario: Cliente existente tiene productos asignados
- **WHEN** se consulta un cliente que tiene productos asignados
- **THEN** la respuesta incluye `productos_asignados` con el array de productos

### Requirement: API para gestionar productos asignados
El sistema SHALL proveer endpoints REST para administrar los productos asignados de un cliente.

#### Scenario: Obtener productos asignados de un cliente
- **WHEN** se hace GET a `/api/v1/clients/{id}/productos`
- **THEN** el sistema retorna el array de productos asignados del cliente

#### Scenario: Agregar producto a cliente
- **WHEN** se hace POST a `/api/v1/clients/{id}/productos` con `{ "producto_id": 1, "nombre": "Jabón Líquido", "precio": 4500, "cantidad": 2 }`
- **THEN** el producto se agrega al array de productos asignados del cliente
- **AND** si el producto ya existe en la lista, se incrementa su cantidad

#### Scenario: Reemplazar todos los productos asignados
- **WHEN** se hace PUT a `/api/v1/clients/{id}/productos` con un nuevo array de productos
- **THEN** el array de productos asignados se reemplaza completamente

#### Scenario: Eliminar un producto de la lista
- **WHEN** se hace DELETE a `/api/v1/clients/{id}/productos/{producto_id}`
- **THEN** el producto es removido del array de productos asignados

#### Scenario: Error si cliente no existe
- **WHEN** se hace GET/POST/PUT/DELETE a productos de un cliente inexistente
- **THEN** el sistema retorna 404 con mensaje "Cliente no encontrado"

#### Scenario: Error si producto no existe en la lista al eliminar
- **WHEN** se hace DELETE a `/api/v1/clients/{id}/productos/999` y ese producto no está asignado
- **THEN** el sistema retorna 404 con mensaje "Producto no encontrado en la lista del cliente"

### Requirement: Cantidad mínima de 1 por producto
El sistema SHALL validar que la cantidad de cada producto asignado sea >= 1.

#### Scenario: Cantidad válida
- **WHEN** se agrega un producto con cantidad 2
- **THEN** el sistema lo acepta correctamente

#### Scenario: Cantidad inválida
- **WHEN** se agrega un producto con cantidad 0
- **THEN** el sistema retorna 422 con error de validación

### Requirement: Frontend muestra productos asignados en detalle del cliente
El sistema SHALL mostrar los productos asignados en el modal de detalle del cliente (ClientDetailsModal), con tabla que incluya nombre, precio unitario, cantidad y subtotal.

#### Scenario: Modal de detalle muestra productos asignados
- **WHEN** el usuario abre el detalle de un cliente que tiene productos asignados
- **THEN** se muestra una sección "Productos Asignados" con una tabla de productos
- **AND** la tabla tiene columnas: Producto, Precio Unitario, Cantidad, Subtotal
- **AND** el total general se muestra al pie

#### Scenario: Botón Agregar Producto en modal de detalle
- **WHEN** el usuario hace clic en "Agregar Producto" en el modal de detalle
- **THEN** se abre un selector de productos del catálogo
- **AND** al seleccionar un producto, se agrega a la lista del cliente con cantidad 1
