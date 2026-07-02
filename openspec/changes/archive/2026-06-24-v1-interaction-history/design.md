# Design: v1-interaction-history

## Data Model (Interaction)

- id: integer, PK, autogen
- clientId: integer, nullable, FK to clients.id
- user: string (who or which user triggered the interaction)
- source: string (e.g., "telegram", "webhook", "n8n")
- payload: JSON/Text (raw payload)
- intent: string (optional - NLP intent if available)
- result: string (optional - processing result or status)
- timestamp: datetime, server-set

Indexes

- index on (clientId)
- index on (timestamp)

Retention

- Default retention policy: keep 90 days, then archive; implement as future task

API Contract

- POST /api/v1/interactions
  - Body: { source, user?, payload, intent?, result?, clientLookup? }
  - Response: 201 with { id, timestamp }

Validation

- payload required
- source required and limited to known sources
