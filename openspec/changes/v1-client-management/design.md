# Design: v1-client-management

## Domain Model (Client)

- id: integer, primary key, autogen
- nombre: string, required
- apellido: string, required
- telefono: string, optional
- email: string, required, unique
- fechaRegistro: datetime, server-set on insert
- activo: boolean, default true

## Pydantic DTOs

- CreateClient
  - nombre: str
  - apellido: str
  - telefono: Optional[str]
  - email: EmailStr (required)

- UpdateClient
  - nombre: Optional[str]
  - apellido: Optional[str]
  - telefono: Optional[str]
  - email: Optional[EmailStr]
  - activo: Optional[bool]

- ClientResponse
  - id: int
  - nombre, apellido, telefono, email, fechaRegistro (ISO8601), activo

## Persistence

- SQLAlchemy declarative model matching fields above
- Unique index on email

## API Endpoints

- POST /api/v1/clients — CreateClient -> ClientResponse (201)
- GET /api/v1/clients/{id} — ClientResponse (200)
- GET /api/v1/clients — list with optional filters (email, activo)
- PATCH /api/v1/clients/{id} — UpdateClient -> ClientResponse (200)
- DELETE /api/v1/clients/{id} — 204

OpenAPI examples must be included using Docs/openapi/request-examples.md and response-examples.md

## Validation rules

- email required on create and must be unique
- telefono optional but if present must match simple pattern (digits, spaces, +, -)

## Migration

- Alembic migration to create clients table with unique index on email and created_at default CURRENT_TIMESTAMP

## Notes

- Do NOT implement interactions storage here; reference POST /api/v1/interactions as a dependency for event emission.
