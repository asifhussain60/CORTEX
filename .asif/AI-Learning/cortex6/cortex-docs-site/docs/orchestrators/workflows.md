---
title: Workflow Orchestrators
---

CORTEX uses specialized workflow orchestrators. Examples:

- **Planning**: creates structure and a plan — does not implement.
- **TDD**: enforces red→green→refactor; generates tests before code.
- **Investigation**: diagnoses issues; gathers evidence; proposes safe fixes.
- **Sanitization**: scrubs secrets/PII; ensures compliance constraints are met.
- **Maintenance**: refactors, updates dependencies, improves reliability.

Each workflow emits TODOs and metadata; the TODO orchestrator manages execution ordering.
