# Spec: client

Full content from the earlier generated spec (inserted here).

## Scenarios

### Create client
- Given valid client data
- When POST /api/v1/clients
- Then returns 201 and client payload with id

### Get client
- Given existing client id
- When GET /api/v1/clients/{id}
- Then returns 200 and client data
