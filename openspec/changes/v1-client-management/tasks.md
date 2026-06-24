# Tasks for v1-client-management

1. Define SQLAlchemy model for Client
   - Acceptance: model file exists with fields id, nombre, apellido, telefono, email(unique), fechaRegistro, activo
   - Verify: run python -c "from src.clients.models import Client; print(Client.__tablename__)"

2. Create Alembic migration
   - Acceptance: migration file under alembic/versions creating clients table and unique index on email
   - Verify: docker compose up -d mysql; alembic upgrade head

3. Implement repository + service layer
   - Acceptance: repository with create/get/update/delete methods and transactional behavior
   - Verify: pytest tests/unit/test_client_repository.py

4. Implement FastAPI router and endpoints
   - Acceptance: endpoints under /api/v1/clients with DTOs and response examples
   - Verify: curl examples
     - Create: curl -X POST http://localhost:8000/api/v1/clients -H "Content-Type: application/json" -d '{"nombre":"Juan","apellido":"Perez","email":"juan@example.com"}'

5. Pydantic DTOs and OpenAPI examples
   - Acceptance: CreateClient, UpdateClient, ClientResponse implemented and appear in OpenAPI docs
   - Verify: open http://localhost:8000/docs and inspect models; compare examples in openspec/specs/client/spec.md

6. Tests: unit and integration
   - Acceptance: pytest passes for client unit and integration tests
   - Verify: pytest tests/unit tests/integration -q

7. Dev local (sin Docker)
   - Acceptance: instrucciones claras para ejecutar la aplicación y las pruebas en un entorno virtual local sin Docker
   - Verify: seguir pasos locales descritos abajo y comprobar que pytest pasa y que uvicorn arranca

   Pasos locales recomendados:

   a) Crear y activar virtualenv
      - python -m venv .venv
      - Windows: .\.venv\Scripts\Activate.ps1  (o .\.venv\Scripts\activate)
      - Unix: source .venv/bin/activate

   b) Instalar dependencias
      - python -m pip install --upgrade pip
      - python -m pip install -r requirements.txt

   c) Configurar DB para desarrollo rápido (SQLite en memoria para pruebas)
      - Para pruebas unitarias y de integración rápidas usamos SQLite in-memory (ya configurado en los tests)
      - Para ejecutar la app con una DB local persistente opcionalmente configurar DATABASE_URL en el entorno, por ejemplo:
        set DATABASE_URL="sqlite:///./dev.db"  (Windows PowerShell)
        export DATABASE_URL="sqlite:///./dev.db" (Unix)

   d) Ejecutar migraciones (opcional para SQLite file)
      - alembic upgrade head

   e) Levantar la app localmente
      - uvicorn src.main:app --reload --port 8000

   f) Ejecutar tests
      - pytest -q

   Notas:
   - Las migraciones Alembic y la carpeta docker-compose.dev.yml se mantienen en el repo para uso futuro con Docker/MySQL.
   - Si preferís que la app use MySQL localmente más adelante, setear DATABASE_URL a mysql+pymysql://user:pass@host:3306/dbname

8. Documentation: update OpenAPI examples using Docs/openapi/* files
   - Acceptance: specs/client/spec.md includes request/response examples drawn from Docs/openapi
   - Verify: Compare examples in OpenAPI UI

9. Dependency note
   - Add task item documenting POST /api/v1/interactions API contract and mark as dependency on v1-interaction-history. Do NOT implement it here.

10. Review

   - Code review and API contract review
