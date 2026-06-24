from fastapi import FastAPI

# Fábrica de la aplicación y punto de entrada principal
# Este archivo conecta routers y middleware según Docs/architecture.md
def create_app() -> FastAPI:
    """Crear y configurar la aplicación FastAPI.

    La función centraliza la construcción de la aplicación para que los tests
    puedan importar `create_app` e instanciar una app sin efectos secundarios.
    """
    app = FastAPI(title="Client Management API")

    # Importar e incluir routers. Los routers están definidos en src.api.routes
    # para seguir la estructura de proyecto establecida en Docs/architecture.md.
    from src.api.routes import clients as clients_router_module

    # Montar el router de clientes bajo el prefijo de API v1
    app.include_router(clients_router_module.router, prefix="/api/v1/clients", tags=["clients"])

    return app


app = create_app()

# Si se ejecuta directamente, uvicorn puede importar `app` desde este módulo:
# uvicorn src.main:app --reload
