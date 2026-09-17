## ADDED Requirements

### Requirement: Mostrar imagen del producto en la tabla con fallback

El sistema SHALL mostrar la imagen del producto en la columna Nombre de `ProductTable` cuando `image_url` esté presente; cuando no haya imagen, SHALL mostrar el cuadrado con la inicial (comportamiento actual).

- La imagen SHALL renderizarse como thumbnail (tamaño del cuadrado actual, 32x32, con `object-cover` y bordes redondeados).
- Si la imagen falla al cargar (HTTP error, archivo borrado), SHALL mostrarse la inicial como fallback, sin romper la fila.

#### Scenario: Producto con imagen muestra el thumbnail
- **WHEN** la tabla renderiza un producto con `image_url`
- **THEN** se SHALL mostrar la imagen del producto en lugar de la inicial

#### Scenario: Producto sin imagen muestra la inicial
- **WHEN** la tabla renderiza un producto con `image_url` null
- **THEN** se SHALL mostrar el cuadrado con la inicial (comportamiento actual)

#### Scenario: Error al cargar la imagen muestra la inicial
- **WHEN** el navegador no puede cargar la imagen (archivo inexistente o error de red)
- **THEN** se SHALL mostrar la inicial como fallback y la fila SHALL seguir funcionando

### Requirement: Upload y remoción de imagen en el modal de producto

El sistema SHALL permitir subir y quitar la imagen de un producto desde `ProductFormModal`, tanto en creación como en edición, ÚNICAMENTE para usuarios admin (`isAdmin`).

- Al crear: si el admin seleccionó un archivo, el sistema SHALL crear el producto y luego subir la imagen al endpoint correspondiente.
- Al editar: si el admin seleccionó un archivo, SHALL reemplazar la imagen; si eligió "quitar imagen", SHALL eliminarla.
- Se SHALL mostrar una preview del archivo seleccionado antes de guardar.
- El control de archivo SHALL validar en cliente el mismo límite de tamaño (2MB) y tipos (JPG/PNG/WebP) para feedback inmediato.
- Las operaciones exitosas SHALL mostrar toast de éxito y las fallidas toast de error (patrón sonner existente).
- Los usuarios no admin SHALL NO ver los controles de imagen.

#### Scenario: Crear producto con imagen
- **WHEN** un admin crea un producto y selecciona una imagen válida
- **THEN** el producto se crea
- **AND** la imagen se sube y el producto queda con `image_url`
- **AND** se muestra un toast de éxito

#### Scenario: Editar producto y reemplazar imagen
- **WHEN** un admin edita un producto con imagen y selecciona una imagen nueva
- **THEN** la imagen se reemplaza y el producto queda con el nuevo `image_url`
- **AND** se muestra un toast de éxito

#### Scenario: Quitar imagen desde edición
- **WHEN** un admin edita un producto con imagen y elige quitar la imagen
- **THEN** la imagen se elimina y el producto queda con `image_url` null
- **AND** se muestra un toast de éxito

#### Scenario: Archivo inválido se rechaza en cliente
- **WHEN** un admin selecciona un archivo que no es JPG/PNG/WebP o supera 2MB
- **THEN** el modal SHALL mostrar un error sin enviar el archivo al backend

#### Scenario: Usuario no admin no ve controles de imagen
- **WHEN** un usuario con `isAdmin = false` abre el modal de producto
- **THEN** no SHALL ver el control de subida ni de remoción de imagen