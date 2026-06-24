# Proposal: v1-client-management

## Intent

Implement the initial Client Management API (v1) aligning the domain model and API with Docs/ (domain-model.md, requirements.md). Deliver Pydantic DTOs, OpenAPI examples, Alembic migration, repository/service layer, tests, and Docker-based local development.

## Scope

### In Scope
- Define canonical Client domain model and SQLAlchemy table
- Provide Pydantic DTOs: CreateClient, UpdateClient, ClientResponse
- CRUD endpoints under /api/v1/clients with OpenAPI examples
- Alembic migration and repository/service tests (pytest)
- Docker + docker-compose development configuration and verification commands

### Out of Scope
- Interaction persistence and processing (moved to v1-interaction-history)
- External integrations (Telegram, n8n) — separate changes

## Capabilities

### New Capabilities
- `client-management`: Create, Read, Update, Delete and List clients via REST API

### Modified Capabilities
- `api-spec`: Add OpenAPI examples and DTO definitions for clients (delta in specs/client/spec.md)

## Approach

Use FastAPI with Pydantic DTOs and SQLAlchemy models. Keep domain model and DTOs explicit so controllers/routers only orchestrate. Use Alembic for migrations, Pytest for unit and integration tests. Run MySQL via docker-compose for local verification.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/specs/client/spec.md` | New/Modified | API scenarios and OpenAPI examples |
| `openspec/changes/v1-client-management/` | New/Modified | proposal, design, tasks, delta specs |
| `alembic/versions` | New | migration file to create clients table (task)
| `src/clients` | New | models, repository, service, router (implementation tasks only)

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Email uniqueness constraint causing migration failures | Medium | Add migration to create unique index and test against duplicate cases in pytest |
| Divergence from Docs/ domain model | Low | Use Docs/domain-model.md as source of truth and include examples in OpenAPI specs |

## Rollback Plan

1. Revert the applied migration via alembic downgrade
2. Disable /api/v1/clients router via feature flag or configuration
3. Revert code commits

## Dependencies

- MySQL 8 for integration tests (docker-compose)
- Alembic for migrations

## Success Criteria

- [ ] Clients table created by Alembic migration matching domain model
- [ ] Create/Read/Update/Delete endpoints implemented with DTOs and pass pytest integration tests
- [ ] OpenAPI includes example requests/responses using Docs/openapi examples

Note: The interactions endpoint (POST /api/v1/interactions) is required by the broader product, but its implementation and persistence belong to change `v1-interaction-history`. This change will document the dependency and may include a task to add API contract reference only.
