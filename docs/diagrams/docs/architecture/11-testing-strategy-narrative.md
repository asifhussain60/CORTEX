# CORTEX Testing Strategy

This diagram illustrates CORTEX's layered testing methodology.

**Unit Tests** validate individual components in isolation (functions, classes, modules).

**Integration Tests** verify component interactions (agent coordination, tier communication).

**System Tests** validate end-to-end workflows (documentation generation, conversation import).

**Acceptance Tests** confirm user stories meet requirements (planning workflow, setup automation).

Each layer builds on the previous - unit tests run in milliseconds, integration tests in seconds, system tests in tens of seconds. This pyramid ensures fast feedback during development while comprehensive validation before release.

CORTEX enforces "Test Before Claim" - no feature is considered complete until tests pass.