# CORTEX Diagrams (Single Source of Truth)

This folder (`cortex-docs/assets/diagrams`) is the **only** canonical location for diagram prompt “cards” referenced by CORTEX docs and video prompts.

## Rules

- **Flat only:** no subfolders.
- **High value only:** only keep diagrams that explain core system behavior end-to-end.
- **Naming:** `NN-{category}-{short-title}.md` where category is a meaningful word (e.g., `architecture`, `workflow`, `governance`, `testing`, `orchestration`, `audit`).
- **Renderability:** diagrams are Markdown so they can be referenced as `#file:cortex-docs/...` and hosted from `cortex-docs` via GitHub Pages.

## Curated diagram set

- `01-architecture-system-architecture-layers.md`
- `02-architecture-mcp-gateway-architecture.md`
- `03-workflow-sdlc-pipeline.md`
- `04-audit-audit-fix-pipeline.md`
- `05-workflow-tdd-cycle-and-fsm.md`
- `06-governance-sweep-completeness-core-064.md`
- `07-testing-testing-strategy-pyramid.md`
- `08-architecture-package-and-directory-map.md`
- `09-orchestration-request-sequence.md`
- `10-workflow-template-engine.md`

## Adding a new diagram

Only add a new diagram if it is:

- **End-to-end** (useful across the project, not a niche module)
- **Stable** (unlikely to churn every phase)
- **Factual** (no speculative architecture)
