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

# --- Asistente administrativo: cerebros (NLU local + Ollama opcional) ---
# Se leen por llamada (os.getenv es barato) siguiendo el patrón de
# security._bcrypt_rounds(): permite a los tests sobreescribir el entorno
# sin reiniciar el proceso.

def get_admin_bot_brain() -> str:
    """Cerebro del asistente: classifier | deterministic | ollama."""
    return os.getenv("ADMIN_BOT_BRAIN", "classifier").strip().lower()


def get_admin_bot_nlu_threshold() -> float:
    """Umbral mínimo de confianza del clasificador local (NLU)."""
    return float(os.getenv("ADMIN_BOT_NLU_THRESHOLD", "0.55"))


def get_ollama_url() -> str:
    """URL base del servidor Ollama (opcional)."""
    return os.getenv("OLLAMA_URL", "http://localhost:11434")


def get_ollama_model() -> str:
    """Modelo de Ollama a usar (opcional)."""
    return os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


def get_ollama_timeout_seconds() -> int:
    """Timeout en segundos para las llamadas a Ollama."""
    return int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))


# Otras variables de configuración (p.ej. claves secretas, hosts permitidos) pueden añadirse aquí
