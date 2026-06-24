import os

# Configuración centralizada de la aplicación.
# Lee variables de entorno y provee valores por defecto para desarrollo local.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Otras variables de configuración (p.ej. claves secretas, hosts permitidos) pueden añadirse aquí
