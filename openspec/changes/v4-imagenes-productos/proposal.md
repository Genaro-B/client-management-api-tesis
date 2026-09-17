## Why

Los productos son el catálogo de negocio del sistema, pero hoy se muestran como un cuadrado con la inicial del nombre. Sin imagen, el catálogo se siente incompleto tanto en la demo de tesis como en el uso real. Este cambio agrega soporte de imágenes a los productos con almacenamiento LOCAL en filesystem: sin servicios externos, sin API keys, 100% offline — requisito crítico porque la demo no puede fallar por dependencias de terceros. El punto pedagógico central es la arquitectura: se programa contra una interfaz (`ImageStorage`), de modo que Cloudinary u otro proveedor pueda sumarse después como un plugin sin tocar la API ni el frontend.

## What Changes

- Agregar columna `image_url` (string, nullable) a la tabla `products` vía nueva migración Alembic `0007`
- Crear capa de abstracción `ImageStorage` (interfaz) con implementación `LocalImageStorage` para filesystem local
- Servir las imágenes subidas como archivos estáticos desde el backend (ruta `/static/uploads/...`)
- Validar tipo de archivo (JPG/PNG/WebP) y tamaño máximo (2MB) al subir
- Nuevo endpoint de upload (multipart, admin-only) para asociar/reemplazar la imagen de un producto + endpoint para quitarla
- Actualizar schemas `CreateProduct`, `UpdateProduct`, `ProductResponse` con `image_url`
- Frontend: mostrar la imagen del producto en `ProductTable` cuando exista, manteniendo la inicial como fallback
- Frontend: soporte de upload de imagen en el modal de creación y edición de producto (solo admin)
- Nota de diseño: Cloudinary queda documentado como trabajo futuro (plugin de `ImageStorage`), sin tocar API/frontend

## Capabilities

### New Capabilities
- `product-images`: Subida, validación, almacenamiento local y servido de imágenes de productos; columna `image_url`; endpoints de upload/delete

### Modified Capabilities
- `client-management-ui`: la tabla de productos muestra la imagen real con fallback a la inicial; el modal de producto incluye upload/remoción de imagen (solo admin)

## Impact

- **Backend**: migración Alembic `0007`, nuevo módulo de storage (`src/storage/image_storage.py`), configs nuevas en `src/core/config.py`, montado de StaticFiles en `main.py`, endpoints nuevos en `src/api/routes/products.py`
- **Schemas**: `image_url` en `CreateProduct`, `UpdateProduct`, `ProductResponse`
- **Modelo**: `image_url` en `src/models/product.py`
- **Frontend**: `ProductTable.jsx` (celda de imagen + fallback), `ProductFormModal.jsx` (campo de upload), `productService.js` (funciones de upload/delete), `vite.config.js` (proxy de `/static`)
- **Tests**: unit tests del storage + validación, API tests de upload/delete/validación, tests existentes de productos siguen verdes (167 base)