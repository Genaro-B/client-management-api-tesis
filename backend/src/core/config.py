import os

# Configuración centralizada de la aplicación.
# Lee variables de entorno y provee valores por defecto para desarrollo local.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Umbral de "stock bajo" para el asistente administrativo y alertas.
# Un producto con stock menor o igual a este valor se considera crítico.
LOW_STOCK_THRESHOLD = 5

# Configuración de imágenes de productos (almacenamiento local, 100% offline).
# El directorio de uploads vive dentro de backend/ y puede sobreescribirse
# con la variable de entorno UPLOAD_DIR (útil en tests).
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(_BACKEND_DIR, "uploads"))

# Tamaño máximo de imagen en bytes (2MB).
MAX_IMAGE_SIZE = 2 * 1024 * 1024

# Tipos de imagen permitidos según su content-type.
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Otras variables de configuración (p.ej. claves secretas, hosts permitidos) pueden añadirse aquí
