# Tasks: v1-interaction-history

1. Create SQLAlchemy Interaction model
   - Acceptance: model file with fields id, clientId, user, source, payload, intent, result, timestamp
   - Verify: importable in python

2. Create Alembic migration
   - Acceptance: migration under alembic/versions creating interactions table and indices
   - Verify: alembic upgrade head

3. Implement repository and service
   - Acceptance: repository.save(payload) and optional linkToClient(clientLookup)
   - Verify: unit tests

4. Implement POST /api/v1/interactions endpoint
   - Acceptance: validates input and persists interaction; resolves clientId if clientLookup provided
   - Verify: curl POST with sample payload returns 201 and id

5. Tests
   - Acceptance: unit + integration tests covering save, link, validation errors
   - Verify: pytest tests/unit tests/integration

6. E2E notes for n8n
   - Provide mapping examples for n8n webhook node to this endpoint
