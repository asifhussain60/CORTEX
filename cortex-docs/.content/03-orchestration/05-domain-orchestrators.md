# Domain Orchestrators

---
title: Domain Orchestrators — Business-Vertical Specialization
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-25
source_of_truth: cortex/orchestrators/domain/
order: 5
---

> **Brain analogy:** Domain orchestrators are **specialized brain regions** for specific types of knowledge — like the fusiform face area recognizes faces, and the parahippocampal place area recognizes places. Each domain orchestrator has deep expertise in a specific engineering or business vertical.

---

## Domain Tier (6 Wired Orchestrators)

**Location:** `cortex/orchestrators/domain/`

All 6 domain orchestrators implement `IOrchestrator` via `OrchestratorProtocolMixin`.

| Class | Path | Description |
|-------|------|-------------|
| **PlanningOrchestrator** | `domain/planning_orchestrator.py` | Structured planning — phase decomposition, gap catalogue, TDD sequence generation |
| **DomainOrchestrator** | `domain/domain_orchestrator.py` | Domain-specific intelligence — LENS analysis with domain knowledge synthesis |
| **RefactoringOrchestrator** | `domain/refactoring_orchestrator.py` | Intelligent refactoring — duplication detection, code smell remediation, CORE-035 |
| **SDLCWorkflowOrchestrator** | `domain/sdlc_workflow_orchestrator.py` | SDLC Intelligence Engine — template selection, knowledge hydration, FSM execution (Phase 79-D) |
| **DashboardOrchestrator** | `domain/dashboard_orchestrator.py` | Static dashboard generation — landing pages, per-repo dashboards, SQLite-backed metrics |
| **EnhancedPlanningOrchestrator** | `domain/enhanced_planning_orchestrator.py` | Advanced planning with ROI scoring, wave decomposition, and audit-driven auto-planning |

---

## How Domain Routing Works

```
[Request arrives at MasterOrchestrator]
     │
     ▼
[IntentRouter: LENS-based classification]
     │
     ├── PLAN     ──▶ PlanningOrchestrator / EnhancedPlanningOrchestrator
     ├── REFACTOR ──▶ RefactoringOrchestrator
     ├── ANALYZE  ──▶ DomainOrchestrator (domain knowledge synthesis)
     ├── SDLC     ──▶ SDLCWorkflowOrchestrator (template selection + FSM)
     └── REPORT   ──▶ DashboardOrchestrator (static site generation)
```

**Practical Example:**
- "Refactor the auth module" → RefactoringOrchestrator applies CORE-035 (no duplicates), semantic rename via Roslyn adapter, duplication detection
- "Plan this sprint" → EnhancedPlanningOrchestrator applies ROI scoring, wave decomposition, generates gap catalogue per CORE-064
- "Generate a dashboard for this repo" → DashboardOrchestrator produces static HTML + SQLite-backed metrics

---

## SDLCWorkflowOrchestrator (Phase 79-D)

The newest domain orchestrator — SDLC Intelligence Engine:

- **Template selection:** Matches SDLC workflows to project type via LENS fingerprinting
- **Knowledge hydration:** Injects domain knowledge from `cortex-registry/knowledge-base/` into workflow context
- **FSM execution:** State machine execution via `WorkflowEngine` (Phase 67)
- **Location:** `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py`

---

## RefactoringOrchestrator

Key capabilities enforcing CORE-035 (single canonical implementation):

| Feature | Detail |
|---------|--------|
| Duplication detection | Identifies duplicate implementations across the codebase |
| Semantic rename | Roslyn by-name symbol rename (Python, C#, TypeScript) — no byte offset |
| Code smell remediation | Long methods, high complexity, poor naming |
| Multi-language | Python, TypeScript/JavaScript, C#/.NET |
| Governance gate | CORE-035 validation before and after refactor |

---

## Practical Examples

**Business Leader:** "6 domain orchestrators means every major engineering workflow has a dedicated engine. Refactoring is safe and auditable. Planning produces measurable deliverables."

**Product Owner:** "EnhancedPlanningOrchestrator scores features by ROI before committing to implementation. PlanningOrchestrator generates phase files to `cortex-registry/planning/phases/planned/` — auto-tracked in `cortex-master.yaml`."

**Developer:** "RefactoringOrchestrator renames symbols by name — not byte offset. I never deal with line number drift. SDLCWorkflowOrchestrator selects the right YAML workflow for my project type and hydrates it with domain knowledge automatically."

---

*Verified against `cortex/orchestrators/domain/` · 25 February 2026 · Phase 83 complete · 6 domain orchestrators*
