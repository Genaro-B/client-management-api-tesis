# Spec: interaction-history

## Scenarios

1) Save interaction - happy path
   - Given valid payload with source and payload
   - When POST /api/v1/interactions
   - Then 201 with { id, timestamp }

2) Save and link to client
   - Given payload containing clientLookup (email or telefono) matching existing client
   - When POST /api/v1/interactions
   - Then persisted interaction has clientId set to matched client

3) Validation error
   - When POST with missing payload or source
   - Then 400 with validation errors
