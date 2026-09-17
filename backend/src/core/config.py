import os

# Configuración centralizada de la aplicación.
# Lee variables de entorno y provee valores por defecto para desarrollo local.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Umbral de "stock bajo" para el asistente administrativo y alertas.
# Un producto con stock menor o igual a este valor se considera crítico.
LOW_STOCK_THRESHOLD = 5

# Otras variables de configuración (p.ej. claves secretas, hosts permitidos) pueden añadirse aquí
