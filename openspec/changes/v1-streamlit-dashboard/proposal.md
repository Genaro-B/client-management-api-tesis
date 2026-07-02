## Why

Tener un dashboard liviano que conecta directo a la base de datos, sin pasar por la API REST. Sirve como herramienta interna de administración y visualización — útil para ver métricas, explorar datos, y hacer operaciones rápidas sin depender del frontend React. También funciona como respaldo si el frontend tiene problemas de conexión con la API.

## What Changes

- Nuevo proyecto Streamlit en `dashboard/` que conecta directo a MySQL
- Visualización de métricas: total clientes, activos/inactivos, interacciones, timeline, fuentes, intents
- CRUD de clientes desde el dashboard
- Visualización de interacciones asociadas a cada cliente
- Consulta directa a DB mediante SQLAlchemy (reusa modelos existentes de `backend/src/`)

## Capabilities

### New Capabilities
- `streamlit-dashboard`: Dashboard interno con Streamlit que consulta la base de datos directamente, con visualización de métricas y gestión de clientes

### Modified Capabilities
<!-- No se modifican capabilities existentes — el dashboard es independiente del frontend React y de la API REST -->

## Impact

- Nuevo directorio `dashboard/` con la aplicación Streamlit
- Dependencias nuevas: `streamlit`, `pandas`, `plotly` (o `matplotlib`)
- Reusa modelos SQLAlchemy existentes de `backend/src/`
- No modifica nada del backend existente ni del frontend React
- No afecta la API REST ni los tests actuales
