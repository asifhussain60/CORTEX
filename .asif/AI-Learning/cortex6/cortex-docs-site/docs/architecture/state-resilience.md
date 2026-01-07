---
title: State, Checkpoints, and Recovery
---

CORTEX is designed to survive interruptions:

- **Optimistic locking** prevents silent clobbering of concurrent updates.
- **Checkpoints** allow resuming from the last known-good state.
- **Rollback** enables undo when enforcement fails (tests, lint, resource limits, policy violations).

These primitives are what make “autonomous execution” safe instead of terrifying.
