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

7. Docker + docker-compose for dev
   - Acceptance: docker-compose.yml with services: app, mysql, alembic (optional)
   - Verify: docker compose up --build; alembic upgrade head

8. Documentation: update OpenAPI examples using Docs/openapi/* files
   - Acceptance: specs/client/spec.md includes request/response examples drawn from Docs/openapi
   - Verify: Compare examples in OpenAPI UI

9. Dependency note
   - Add task item documenting POST /api/v1/interactions API contract and mark as dependency on v1-interaction-history. Do NOT implement it here.

10. Review

   - Code review and API contract review
