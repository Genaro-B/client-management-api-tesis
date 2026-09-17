## ADDED Requirements

### Requirement: Subida de imagen de producto

El sistema SHALL permitir subir una imagen para un producto existente vía `POST /api/v1/products/{product_id}/image` con multipart/form-data (campo `file`). Solo acceso admin, según convención existente del CRUD de productos.

- El endpoint SHALL validar el tipo de archivo: solo JPG (`image/jpeg`), PNG (`image/png`) y WebP (`image/webp`), verificando content-type, extensión y magic bytes.
- El endpoint SHALL validar el tamaño: archivos mayores a 2MB SHALL ser rechazados.
- Ante una subida exitosa, el producto SHALL quedar con `image_url` apuntando a la URL pública de la imagen.
- Si el producto ya tenía imagen, el archivo anterior SHALL eliminarse del storage (una sola imagen por producto).
- El tipo de archivo y el tamaño máximo SHALL estar configurados de forma centralizada.

#### Scenario: Subida exitosa asocia la imagen al producto
- **WHEN** un admin sube un PNG válido de 500KB a un producto existente
- **THEN** la respuesta SHALL devolver el producto con `image_url` poblado
- **AND** la imagen queda accesible en su URL pública

#### Scenario: Tipo de archivo inválido es rechazado
- **WHEN** se sube un archivo que no es JPG, PNG ni WebP (ej. GIF, PDF, texto)
- **THEN** el endpoint SHALL responder 415 Unsupported Media Type
- **AND** el producto SHALL quedar sin cambios en `image_url`

#### Scenario: Archivo que supera el tamaño máximo es rechazado
- **WHEN** se sube un archivo de más de 2MB
- **THEN** el endpoint SHALL responder 413 Payload Too Large
- **AND** el producto SHALL quedar sin cambios en `image_url`

#### Scenario: Producto inexistente en el upload
- **WHEN** se sube una imagen a un `product_id` que no existe
- **THEN** el endpoint SHALL responder 404

#### Scenario: Reemplazo de imagen existente
- **WHEN** se sube una imagen válida a un producto que ya tiene `image_url`
- **THEN** el producto SHALL apuntar a la nueva imagen
- **AND** el archivo de la imagen anterior SHALL eliminarse del storage

### Requirement: image_url en el modelo y los responses de producto

El sistema SHALL exponer `image_url` (string nullable) en el modelo `Product` y en los schemas `CreateProduct`, `UpdateProduct` y `ProductResponse`, mediante la migración Alembic `0007`.

- La columna SHALL ser nullable y la migración SHALL ser compatible con filas existentes (productos previos quedan con `image_url = null`).
- `image_url` SHALL contener la URL pública de la imagen (`/static/uploads/...`).

#### Scenario: Producto sin imagen expone image_url null
- **WHEN** se crea un producto sin imagen o un producto previo sin migrar
- **THEN** `image_url` SHALL ser `null` en la respuesta

#### Scenario: Producto con imagen expone su URL pública
- **WHEN** se consulta un producto que tiene imagen
- **THEN** la respuesta SHALL incluir `image_url` con la URL pública completa

#### Scenario: Update parcial no altera la imagen
- **WHEN** se actualiza un producto con imagen modificando solo `precio` o `stock`
- **THEN** `image_url` SHALL permanecer intacto

### Requirement: Servido estático de imágenes

El backend SHALL servir las imágenes subidas como archivos estáticos en `/static/uploads/...` (montado con `StaticFiles` en `create_app()`), accesibles sin autenticación.

#### Scenario: La URL pública devuelve la imagen
- **WHEN** se hace GET a la URL pública de una imagen subida
- **THEN** el backend SHALL devolver el archivo con su content-type de imagen

#### Scenario: Archivo inexistente devuelve 404
- **WHEN** se hace GET a una URL de imagen que no existe en disco
- **THEN** el backend SHALL responder 404

### Requirement: Remoción de imagen

El sistema SHALL permitir quitar la imagen de un producto vía `DELETE /api/v1/products/{product_id}/image` (solo admin).

- La operación SHALL eliminar el archivo del storage y setear `image_url = null`.
- La operación SHALL ser idempotente: si el producto no tenía imagen, responde igual con `image_url = null`.

#### Scenario: Quitar imagen existente
- **WHEN** un admin elimina la imagen de un producto que la tiene
- **THEN** el archivo SHALL eliminarse del storage
- **AND** `image_url` SHALL quedar en `null`

#### Scenario: Quitar imagen de un producto sin imagen
- **WHEN** un admin elimina la imagen de un producto que no la tiene
- **THEN** la respuesta SHALL ser igualmente exitosa con `image_url = null`

### Requirement: Soft-delete conserva la imagen

El sistema SHALL conservar la imagen (archivo y `image_url`) cuando un producto se elimina con soft-delete, de modo que la imagen siga disponible al restaurar el producto.

#### Scenario: Producto soft-deleted conserva su imagen
- **WHEN** un producto con imagen se elimina (soft-delete)
- **THEN** el archivo SHALL permanecer en el storage
- **AND** `image_url` SHALL conservar su valor

#### Scenario: Producto restaurado mantiene la imagen
- **WHEN** un producto previamente eliminado con imagen se restaura
- **THEN** el producto SHALL seguir exponiendo el mismo `image_url` funcional