# SDLC Workflow Engine

---
title: SDLC — 7-Phase Software Development Lifecycle
type: capability
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/domain/sdlc_workflow_orchestrator.py
order: 12
---

> CORTEX runs the full SDLC — from requirements analysis through deployment — using YAML workflow templates and knowledge hydration.

---

## 7-Phase Pipeline

The `SDLCWorkflowOrchestrator` maps user intents to lifecycle phases:

| Phase | Template | Description |
|-------|----------|-------------|
| 1. Requirements | `requirements-analysis.yaml` | Stakeholder needs, acceptance criteria |
| 2. Design | `solution-design.yaml` | Architecture, patterns, interfaces |
| 3. Implementation | `implementation-execution.yaml` | TDD-first coding (CORE-008) |
| 4. Testing | `testing-strategy.yaml` | Multi-tier test strategy |
| 5. Security | `security-review.yaml` | Vulnerability scan, threat model |
| 6. Review | `code-review-checklist.yaml` | Quality gate, peer review |
| 7. Deployment | `deployment-pipeline.yaml` | Canary, rollback, monitoring |

---

## Key Features

- **Knowledge Hydration:** Each phase loads domain knowledge from `cortex-registry/knowledge/sdlc/`
- **Security Gates:** Security checks at every phase transition
- **FSM Execution:** `WorkflowEngine` executes templates as finite state machines
- **Scaffold Emission:** `ScaffoldWriter` persists artefacts for downstream steps

---

**Full documentation:** `flat-files/16-sdlc-workflow-engine.md`
**Diagram:** `../assets/diagrams/03-workflow-sdlc-pipeline.md`
