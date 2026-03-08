# CORTEX Diagrams (Single Source of Truth)

This folder (`cortex-docs/assets/diagrams`) is the **only** canonical location for diagram prompt “cards” referenced by CORTEX docs and video prompts.

## Rules

- **Flat only:** no subfolders.
- **High value only:** only keep diagrams that explain core system behavior end-to-end.
- **Naming:** `NN-diagram-{category}-{short-title}.md` where category is a meaningful word (e.g., `architecture`, `workflow`, `governance`, `testing`, `orchestration`, `audit`).
- **Renderability:** diagrams are Markdown so they can be referenced as `#file:cortex-docs/...` and hosted from `cortex-docs` via GitHub Pages.

## Curated diagram set

### Architecture (system structure)
- `01-diagram-architecture-system-architecture-layers.md` — 5-layer view: IDE → MCP → Orchestration → Intelligence → Governance → Infrastructure
- `02-diagram-architecture-mcp-gateway-architecture.md` — MCP stdio transport: IDE configs, tool registry, JSON-RPC flow
- `08-diagram-architecture-package-and-directory-map.md` — Where every system lives in the repo

### Workflow (how work gets done)
- `03-diagram-workflow-sdlc-pipeline.md` — 7-phase SDLC lifecycle with gates
- `05-diagram-workflow-tdd-cycle-and-fsm.md` — RED→GREEN→REFACTOR cycle + workflow engine state machine
- `10-diagram-workflow-template-engine.md` — 3-tier composition: primitives → templates → composites

### Governance (how quality is guaranteed)
- `06-diagram-governance-sweep-completeness-core-064.md` — Why CORTEX fixes ALL instances, not just the one reported
- `12-diagram-governance-convergence-gate-core-068.md` — The detect→fix→rescan loop that guarantees zero P0/P1
- `15-diagram-governance-rule-enforcement-tiers.md` — 55+ rules, 3 checkpoints, 4-tier precedence hierarchy

### Audit (production readiness)
- `04-diagram-audit-audit-fix-pipeline.md` — 9-stage /audit fix flow with convergence loop

### Testing (confidence pyramid)
- `07-diagram-testing-testing-strategy-pyramid.md` — 5-tier pyramid: preflight → smoke → unit → integration → golden

### Orchestration (request handling)
- `09-diagram-orchestration-request-sequence.md` — Full 4-stage pipeline sequence diagram
- `13-diagram-orchestration-intent-classification-routing.md` — 30+ intent types, confidence routing, orchestrator mapping

### Intelligence (code understanding)
- `11-diagram-intelligence-lens-analysis-pipeline.md` — 4-layer LENS analysis (git → AST → annotations → patterns) + Diamond Facade architecture (IntelligenceFacade single entry: analyze/synthesize/query) + Phase 109 migration state

### Debugging (multi-stack)
- `14-diagram-debugging-multi-stack-pipeline.md` — 8 strategies across Python, JS, C#, SQL, .NET with auto-cleanup

## Adding a new diagram

Only add a new diagram if it is:

- **End-to-end** (useful across the project, not a niche module)
- **Stable** (unlikely to churn every phase)
- **Factual** (no speculative architecture)
- **High value** (includes business impact statement)
