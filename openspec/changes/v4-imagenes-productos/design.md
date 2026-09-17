## Context

Los productos son el catálogo de negocio y hoy se muestran en el frontend como un cuadrado azul con la inicial del nombre (`ProductTable.jsx` líneas 39-43). No existe ningún mecanismo de imágenes: la tabla `products` no tiene columna de imagen, el backend no sirve archivos estáticos y el frontend no tiene UI de upload.

El proyecto es una demo de tesis que DEBE funcionar offline y sin fallar; por eso se descarta Cloudinary y cualquier servicio externo con API keys. El backend es FastAPI + SQLAlchemy con capas repository/service/router ya establecidas (ver `Docs/architecture.md`), migraciones Alembic numeradas (`0006` es la última) y 167 tests verdes corriendo con `python run_tests.py`. El frontend es React 18 + Vite + Tailwind 4 con toasts de sonner y gate de admin vía `useAuth().isAdmin` (`user.role === 'admin'`). El proxy de Vite solo cubre `/api`, así que servir imágenes exige tocar `vite.config.js`.

Punto pedagógico central del cambio: programar contra una interfaz (`ImageStorage`) para que el almacenamiento sea intercambiable — Cloudinary hoy no, pero mañana sí, sin tocar API ni frontend.

## Goals / Non-Goals

**Goals:**
- Abstracción `ImageStorage` (interfaz) + implementación `LocalImageStorage` sobre filesystem local
- Columna `image_url` (string nullable) en `products` vía migración Alembic `0007`
- Endpoint de upload multipart (solo admin, según convención existente) con validación de tipo (JPG/PNG/WebP) y tamaño (máx. 2MB)
- Endpoint para quitar la imagen de un producto
- Servir las imágenes como estáticos desde el backend (`/static/uploads/...`)
- Exponer `image_url` en `CreateProduct` / `UpdateProduct` / `ProductResponse`
- Frontend: `ProductTable` muestra la imagen real con fallback a la inicial; `ProductFormModal` permite subir/quitar imagen (crear y editar)
- Tests unit + API para storage, validación y endpoints (TDD estricto)

**Non-Goals:**
- No se integra Cloudinary ni ningún servicio externo (queda documentado como trabajo futuro)
- No se crea sistema de autenticación/token en backend (no existe hoy en ningún router; el gate de admin es frontend por diseño actual)
- No se agregan miniaturas redimensionadas ni procesamiento de imagen (sin PIL/imagemagick)
- No se agregan imágenes a otros recursos (clientes, interacciones)
- No se modifica el flujo del bot de Telegram ni de n8n

## Decisions

### 1. Interfaz `ImageStorage` + `LocalImageStorage` (dependency inversion)
**Decisión**: Nuevo módulo `backend/src/storage/image_storage.py` con:

```python
class ImageStorage(ABC):
    @abstractmethod
    def save(self, image_bytes: bytes, content_type: str, product_id: int) -> str: ...
    @abstractmethod
    def delete(self, url: str) -> None: ...
    @abstractmethod
    def validate(self, image_bytes: bytes, content_type: str) -> None: ...
```

`LocalImageStorage` implementa IO sobre filesystem dentro de `UPLOAD_DIR`, genera nombre `{uuid4().hex}.{ext}` en carpeta `uploads/{product_id}/`, y devuelve la URL pública `/static/uploads/{product_id}/{uuid}.{ext}`. La validación vive en la interfaz (contrato común), lo que fuerza a cualquier implementación futura a respetar tipo/tamaño.

- **Pros**: el servicio y la API dependen SOLO de la interfaz; los tests inyectan un fake/mock de storage (demo perfecta de dependency inversion); Cloudinary = nueva clase, cero cambios en service/API/frontend
- **Contras**: una capa adicional de indirección (justificada: es el punto pedagógico del cambio)
- **Alternativa**: helper suelto en el service sin interfaz — más corto pero acopla el servicio al filesystem y rompe el objetivo del cambio

### 2. Endpoint de upload separado vs multipart en create/update
**Decisión**: Endpoints dedicados `POST /api/v1/products/{product_id}/image` (multipart, campo `file`) y `DELETE /api/v1/products/{product_id}/image`.

- **Pros**: no rompe los endpoints JSON existentes (`POST /products/`, `PATCH /products/{id}`) ni los schemas pydantic; el flujo frontend queda simple: crear/editar producto (JSON) → si hay archivo seleccionado, subirlo
- **Contras**: dos llamadas al backend en vez de una (aceptable para el demo)
- **Alternativa**: form-data mixto en create/update — rompe compatibilidad con los tests existentes y complica los schemas

### 3. Servido de estáticos: `StaticFiles` mount + proxy en Vite
**Decisión**: `app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")` en `create_app()` de `src/main.py`, y agregar `/static` al proxy de `vite.config.js` (hoy solo proxy de `/api`).

- **Pros**: FastAPI sirve las imágenes sin lógica extra; en producción la URL del backend funciona tal cual; el frontend renderiza `image_url` directamente
- **Contras**: requiere tocar el proxy de Vite para desarrollo
- **Alternativa**: endpoint `GET /api/v1/products/images/{filename}` con `FileResponse` — funciona sin tocar Vite pero mezcla estáticos con API y ensucia el contrato REST

### 4. Validación: tipo por content-type + magic bytes, tamaño máx. 2MB
**Decisión**: `validate()` rechaza:
- Tipo: `content_type` ∈ {image/jpeg, image/png, image/webp} Y extensión derivada del tipo Y header de magic bytes (`FF D8 FF` para JPG, `89 50 4E 47` para PNG, `RIFF....WEBP` para WebP). La detección por magic bytes es una función pura `detect_image_type(bytes) -> Optional[str]` en el módulo de storage — ideal para unit tests TDD.
- Tamaño: `len(image_bytes) > 2MB` rechazado.

Errores: tipo inválido → 415 Unsupported Media Type; tamaño excedido → 413 Payload Too Large; producto inexistente → 404.

- **Alternativa**: solo content-type (lo que manda el cliente) — trivial de falsear; validar magic bytes es barato y hace la demo robusta

### 5. `image_url` guarda la URL pública, no el path local
**Decisión**: La columna almacena `/static/uploads/{product_id}/{uuid}.{ext}`. El frontend la usa directo como `src`. `LocalImageStorage.delete(url)` resuelve URL → path local con guard de path traversal (`resolve()` y verificar que quede dentro de `UPLOAD_DIR`).

- **Razón**: la URL pública es lo único que le importa al resto del sistema; si mañana hay Cloudinary, `image_url` será una URL completa y el frontend no cambia ni una línea

### 6. Reemplazo y soft-delete
**Decisión**:
- Subir imagen a un producto que ya tiene una → se elimina el archivo anterior y se guarda el nuevo (una sola imagen por producto)
- Remover imagen (`DELETE`) → borra archivo y setea `image_url = None`
- Soft delete del producto → conserva archivo e `image_url` (el producto es restaurable; no hay hard delete en el flujo actual)

### 7. Gate de admin
**Decisión**: Mismo patrón que el resto del CRUD de productos hoy: el frontend oculta/muestra los controles con `isAdmin` (`AuthContext.jsx` → `user.role === 'admin'`), y los endpoints llevan docstring "Solo acceso admin" como convención documentada. No se construye middleware de auth en backend en este cambio (no existe en ningún router del proyecto; es deuda conocida, ver riesgos).

## Risks / Trade-offs

- **Backend sin enforcement real de admin** → Cualquiera con acceso a la API puede subir imágenes. Mitigación: es la misma convención que los endpoints CRUD existentes; se documenta como deuda y candidato a change futuro (sistema de tokens). Para la demo, el gate de UI es suficiente.
- **Archivos huérfanos en disco** (upload falla a medio camino, downgrade de migración) → Mitigación: nombre UUID + carpeta por producto facilita limpieza manual; el downgrade solo dropea la columna y se documenta que los archivos quedan (no crítico para demo).
- **Hard delete futuro dejaría archivos huérfanos** → Mitigación: carpeta por `product_id` permite borrado en cascada cuando exista ese flujo.
- **2MB en demo con imágenes grandes de cámara** → Mitigación: se valida en frontend ANTES de subir (mismo límite) para dar feedback inmediato; el límite es configurable en `src/core/config.py`.
- **Cabecera JSON por defecto en axios del frontend** → El instance de `productService.js` setea `Content-Type: application/json`; el upload debe forzar `multipart/form-data` (axios fija el boundary automáticamente al pasar `FormData`). Gotcha conocido, se contempla en tasks.

## Migration Plan

1. Crear migración `0007_add_image_url_to_products.py` (`down_revision = '0006'`): `op.add_column('products', sa.Column('image_url', sa.String(length=500), nullable=True))`
2. Actualizar modelo `Product` con `image_url = Column(String(500), nullable=True)` (no rompe filas existentes: nullable)
3. `alembic upgrade head` → verificar columna
4. Rollback: `alembic downgrade 0006` (dropea la columna; los archivos subidos quedan en disco — inocuo)