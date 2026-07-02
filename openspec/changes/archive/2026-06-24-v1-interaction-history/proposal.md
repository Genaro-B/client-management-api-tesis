# Proposal: v1-interaction-history

## Intent

Persist interaction events (incoming webhook events, user messages, external system callbacks) for auditing, analytics and optional replay. Provide an API to receive interactions and store them with optional linkage to clients.

## Scope

### In Scope
- Data model and Alembic migration for Interaction
- POST /api/v1/interactions API endpoint and validation
- Repository, service, and basic business rules for linking to clients when identifiable
- Tests (unit + integration)

### Out of Scope
- Full analytics pipeline or long-term archival (retention policy defined, implemented later)

## Capabilities

### New Capabilities
- `interaction-history`: Persist and query raw interaction events via API

### Modified Capabilities
- None

## Approach

Create an Interaction table capturing raw payload, source, user, intent, result and optional clientId. Provide a simple POST endpoint that accepts JSON payloads with minimal schema and stores them. If client lookup info present, attempt to resolve and store clientId.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/changes/v1-interaction-history/` | New | proposal, design, tasks, specs |
| `alembic/versions` | New | migration for interactions table |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| High throughput causing DB growth | Medium | Add retention and archiving plan; index timestamp and clientId |

## Rollback Plan

- Drop interactions table and revert code changes

## Dependencies

- v1-client-management (optional) for client linking

## Success Criteria

- [ ] POST /api/v1/interactions persists events and returns 201
- [ ] Events can be linked to a client when identifiable
- [ ] Migration passes in CI
