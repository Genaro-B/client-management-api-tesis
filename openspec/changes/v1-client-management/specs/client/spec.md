# Spec: client-management (delta)

## Scenarios

1) Create client - happy path
   - Given valid CreateClient payload
   - When POST /api/v1/clients
   - Then response 201 with ClientResponse matching payload and generated id and fechaRegistro

2) Create client - duplicate email
   - Given email already exists
   - When POST /api/v1/clients
   - Then response 400 with error explaining duplicate email

3) Get client - not found
   - When GET /api/v1/clients/{id} for non-existent id
   - Then response 404

4) Update client - partial
   - Given existing client
   - When PATCH /api/v1/clients/{id} with UpdateClient payload
   - Then response 200 with updated fields

5) Delete client
   - When DELETE /api/v1/clients/{id}
   - Then response 204 and subsequent GET returns 404

## DTO definitions (Pydantic)

- CreateClient
  - nombre: string
  - apellido: string
  - telefono?: string
  - email: string (required)

- UpdateClient
  - nombre?: string
  - apellido?: string
  - telefono?: string
  - email?: string
  - activo?: boolean

- ClientResponse
  - id: integer
  - nombre, apellido, telefono, email, fechaRegistro (ISO8601), activo

## OpenAPI examples

Use examples from Docs/openapi/request-examples.md and Docs/openapi/response-examples.md. Ensure the CreateClient example includes nombre, apellido, email.
