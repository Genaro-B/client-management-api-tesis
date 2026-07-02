from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Fábrica de la aplicación y punto de entrada principal
# Este archivo conecta routers y middleware según Docs/architecture.md
def create_app() -> FastAPI:
    """Crear y configurar la aplicación FastAPI.

    La función centraliza la construcción de la aplicación para que los tests
    puedan importar `create_app` e instanciar una app sin efectos secundarios.
    """
    app = FastAPI(title="Client Management API")

    # CORS — permitir requests del frontend en desarrollo y producción
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Importar e incluir routers. Los routers están definidos en src.api.routes
    # para seguir la estructura de proyecto establecida en Docs/architecture.md.
    from src.api.routes import clients as clients_router_module
    from src.api.routes import auth as auth_router_module
    from src.api.routes import interactions as interactions_router_module

    # Montar el router de clientes bajo el prefijo de API v1
    app.include_router(clients_router_module.router, prefix="/api/v1/clients", tags=["clients"])
    app.include_router(auth_router_module.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(interactions_router_module.router, prefix="/api/v1/interactions", tags=["interactions"])

    return app


app = create_app()

# Si se ejecuta directamente, uvicorn puede importar `app` desde este módulo:
# uvicorn src.main:app --reload
