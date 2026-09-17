## 1. Migración — columna image_url

- [x] 1.1 Crear migración Alembic `0007_add_image_url_to_products.py` (`revision = '0007'`, `down_revision = '0006'`) agregando `image_url` (String(500), nullable) a `products`
- [x] 1.2 Actualizar `backend/src/models/product.py` — agregar `image_url = Column(String(500), nullable=True)`
- [x] 1.3 Ejecutar `alembic upgrade head` y verificar la columna (productos existentes quedan con `image_url = null`)

## 2. Backend — configuración centralizada

- [x] 2.1 Agregar a `backend/src/core/config.py`: `UPLOAD_DIR` (default `backend/uploads`), `MAX_IMAGE_SIZE` (2MB) y `ALLOWED_IMAGE_TYPES` (jpeg/png/webp)
- [x] 2.2 Crear el directorio `backend/uploads/` (con `.gitkeep` si el repo versiona directorios vacíos)

## 3. Backend — abstracción ImageStorage (TDD: test primero)

- [x] 3.1 Escribir unit tests de `backend/src/storage/image_storage.py`: `detect_image_type()` por magic bytes (JPG `FF D8 FF`, PNG `89 50 4E 47`, WebP `RIFF....WEBP`, bytes desconocidos → None), `LocalImageStorage.validate()` (tipo válido pasa, tipo inválido → error, >2MB → error), `save()` (genera uuid, carpeta por product_id, devuelve URL `/static/uploads/{product_id}/{uuid}.{ext}`), `delete()` (borra archivo, URL inexistente no explota) y guard de path traversal
- [x] 3.2 Implementar `backend/src/storage/image_storage.py`: clase abstracta `ImageStorage` (métodos `save`, `delete`, `validate`) + `LocalImageStorage` + función pura `detect_image_type()` — sin dependencias externas nuevas

## 4. Backend — schemas y servicio de imagen

- [x] 4.1 Actualizar `backend/src/schemas/product.py`: `image_url: Optional[str] = None` en `CreateProduct` y `UpdateProduct`; `image_url: Optional[str]` en `ProductResponse`
- [x] 4.2 Escribir unit tests de `backend/src/services/product_image_service.py` usando un FAKE de `ImageStorage` (dependency injection) — subida exitosa actualiza `image_url`, reemplazo borra archivo anterior, delete setea null, soft-delete conserva imagen
- [x] 4.3 Implementar `backend/src/services/product_image_service.py`: clase `ProductImageService` que recibe `db` + `storage: ImageStorage` (inyectado) y compone validación → storage → repositorio (conoce el patrón de `ProductService` existente)

## 5. Backend — API de upload/delete y servido estático

- [x] 5.1 Agregar a `backend/src/api/routes/products.py`: `POST /{product_id}/image` (multipart, campo `file`, docstring "Solo acceso admin" según convención; 404 si el producto no existe, 415 tipo inválido, 413 >2MB) y `DELETE /{product_id}/image` (idempotente); registrar la inyección de `LocalImageStorage`
- [x] 5.2 Montar estáticos en `backend/src/main.py` `create_app()`: `app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")`
- [x] 5.3 Ampliar `backend/tests/test_products_api.py` (patrón existente con `client` fixture): upload exitoso devuelve `image_url`, tipo inválido → 415, >2MB → 413, producto inexistente → 404, reemplazo de imagen, delete (con y sin imagen previa), soft-delete conserva `image_url`, GET de la URL estática devuelve la imagen y archivo inexistente → 404

## 6. Frontend — service y proxy

- [x] 6.1 Agregar a `frontend/src/services/productService.js`: `uploadProductImage(id, file)` forzando `Content-Type: multipart/form-data` en el request (el instance axios trae JSON por defecto — gotcha conocido) y `deleteProductImage(id)`
- [x] 6.2 Agregar `/static` al proxy de `frontend/vite.config.js` hacia `http://localhost:8000` (hoy solo cubre `/api`)

## 7. Frontend — tabla y modal

- [x] 7.1 Actualizar `frontend/src/components/ProductTable.jsx` (celda Nombre, líneas 39-43): si `product.image_url` renderizar `<img>` thumbnail con `object-cover` + `onError` que cae a la inicial; sin imagen, inicial (comportamiento actual)
- [x] 7.2 Actualizar `frontend/src/components/ProductFormModal.jsx`: campo de archivo + preview solo si `isAdmin` (prop recibida desde `ProductsPage`); validación cliente de tipo (JPG/PNG/WebP) y 2MB antes de enviar; al guardar, capturar el producto retornado por `onSave` y subir la imagen; botón "quitar imagen" en edición; toasts con sonner (patrón existente)
- [x] 7.3 Pasar `isAdmin` al modal desde `frontend/src/pages/ProductsPage.jsx` (ya tiene `isAdmin` de `useAuth`)

## 8. Verificación final

- [x] 8.1 Correr `python run_tests.py` desde `backend/` — todos los tests verdes (base 167 + nuevos de storage/service/API)
- [x] 8.2 Verificar migración: `alembic current` = 0007 y `alembic upgrade head` idempotente
- [ ] 8.3 Verificación manual: subir imagen por Swagger y por el frontend (crear + editar + quitar), fallback en tabla, gate de admin (usuario no admin no ve controles), imagen servida en `/static/uploads/...`
- [x] 8.4 Revisar que la demo funcione offline (sin llamadas a servicios externos)