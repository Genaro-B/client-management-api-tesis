from fastapi import FastAPI

# Main application factory and entrypoint
# This file wires together routers and middleware according to Docs/architecture.md
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    The function centralizes application construction so tests can import
    `create_app` and instantiate an app without side effects.
    """
    app = FastAPI(title="Client Management API")

    # Import and include routers. Routers are defined under src.api.routes
    # to follow the project structure mandated in Docs/architecture.md.
    from src.api.routes import clients as clients_router_module

    # Mount the clients router under the API v1 prefix
    app.include_router(clients_router_module.router, prefix="/api/v1/clients", tags=["clients"])

    return app


app = create_app()

# If run directly, uvicorn can import `app` from this module:
# uvicorn src.main:app --reload
