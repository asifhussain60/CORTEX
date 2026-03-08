# CORTEX Feedback — Phase 142: PO Change Intelligence Orchestration

**Generated:** 2026-03-08
**Session:** Design Session — PO Decision-Support Orchestration Layer
**Phase:** 142 (PLANNED)
**Priority:** P1
**Sweep ID:** SWEEP-142-PO-CHANGE-INTELLIGENCE

---

## Executive Summary

Phase 142 introduces a **Product Owner Change Intelligence Orchestration Layer** — 3 new orchestrators, 7 reusable Workflow Composer templates, and 1 new primitive that enable structured PO decision-support workflows. The design reuses 11 existing CORTEX components (55% coverage already built) and fills genuine gaps in the change-intelligence pipeline. No existing orchestrators are duplicated.

---

## Documentation Updates Required

### 1. `canonical_enums.py` — New Intent Types

Add 2 new `IntentType` enum values:

| Intent | Value | Keywords |
|---|---|---|
| `CHANGE_INTELLIGENCE` | `"CHANGE_INTELLIGENCE"` | `change-analyze`, `compare process`, `capability-summary`, `what does the system do` |
| `REQUIREMENTS` | `"REQUIREMENTS"` | `requirements`, `acceptance criteria`, `generate requirements`, `what needs to change` |

**Total intent types after:** 34 (up from 32)

---

### 2. `CORTEX.prompt.md` — §5 Execution Modes Table

Add these rows to the execution modes table:

```
| CHANGE_INTELLIGENCE | "change-analyze", "compare process" | ChangeIntelligenceOrchestrator | ✅ | cortex-po-orchestrator.md |
| REQUIREMENTS | "requirements", "acceptance criteria" | RequirementsOrchestrator | ✅ | cortex-po-orchestrator.md |
```

---

### 3. `copilot-instructions.md` — Architecture Section

Update metrics:

| Metric | Old Value | New Value |
|---|---|---|
| Intent Types | 32 | 34 |
| Orchestrator files | 309 | 311+ |
| Planned phases | 1 | 2 |

Add to Intent → Workflow Routing table:

```
| CHANGE_INTELLIGENCE | `po/process-discovery.yaml` (+ composed templates) | `primitives/governance/challenge-gate.yaml` |
| REQUIREMENTS | `po/requirements-synthesis.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
```

Add to Quick Command Reference:

```
| `/change-analyze` | PO change intelligence — process discovery, comparison, recommendations | Varies by sub-command |
| `/requirements` | Generate implementation-ready requirements from change intent | 6 stages |
| `/training` | Generate role-based training documentation from changes | 5 stages |
| `/capability-summary` | Generate system capability inventory | 5 stages |
```

---

### 4. `workflow-composer-spec.yaml` — Intent Routing Section

Add to `intent_routing:` block:

```yaml
CHANGE_INTELLIGENCE:
  workflow_ref: 'po/process-discovery'
  pre_gate: 'primitives/governance/challenge-gate'
  convergence: null  # analysis-only — no code modification
  agent: 'cortex-po-orchestrator.md'

REQUIREMENTS:
  workflow_ref: 'po/requirements-synthesis'
  pre_gate: 'primitives/governance/holistic-validation-gate'
  convergence: null  # analysis-only
  agent: 'cortex-po-orchestrator.md'
```

Add to `tier_2_mode_workflows.catalogue:` a new `po:` category:

```yaml
po:
  - process-discovery.yaml
  - best-practice-comparison.yaml
  - change-recommendation.yaml
  - roi-analysis.yaml
  - requirements-synthesis.yaml
  - training-doc-generation.yaml
  - capability-summary.yaml
```

Add to `tier_1_primitives.catalogue.analysis:`:

```yaml
- gap-comparison.yaml
```

---

### 5. `AGENT-INDEX.md` — New Agent Entry

Add agent entry:

```
| cortex-po-orchestrator.md | CHANGE_INTELLIGENCE, REQUIREMENTS | PO decision-support and change intelligence | ~3,000 |
```

---

### 6. New Orchestrator Files

| File | Purpose |
|---|---|
| `cortex/orchestrators/domain/change_intelligence_orchestrator.py` | Owns: process discovery, best-practice comparison, change recommendations, ROI analysis, capability summaries |
| `cortex/orchestrators/domain/requirements_orchestrator.py` | Owns: requirements accuracy — business/functional/NFR decomposition + acceptance criteria |
| Enhancement to existing `TrainerOrchestrator` | New `po_training` operation mode for role-based training doc generation |

---

### 7. New Workflow Templates (7 files)

All in `cortex-registry/workflows/templates/po/`:

| Template | Purpose | Reused Components |
|---|---|---|
| `process-discovery.yaml` | Current-state process documentation | `lens-ast-scan`, `intelligence-injection`, LENS RuleExtractor |
| `best-practice-comparison.yaml` | Gap analysis: current vs target state | Composes `process-discovery`, `cortex_knowledge`, `gap-comparison` primitive |
| `change-recommendation.yaml` | Idea evaluation + feasibility | `impact-assessment`, `challenge-gate` |
| `roi-analysis.yaml` | LOE-to-ROI conversion | Adapted `ROICompositeScorer` |
| `requirements-synthesis.yaml` | Structured requirements generation | Composes `sdlc/requirements-analysis`, `holistic-validation-gate` |
| `training-doc-generation.yaml` | Role-based training materials | LENS diff analysis, `ContentLibraryEngine` |
| `capability-summary.yaml` | System capability inventory | Composes `process-discovery`, `cortex_git` |

---

### 8. New Primitive

| File | Purpose |
|---|---|
| `cortex-registry/workflows/templates/primitives/analysis/gap-comparison.yaml` | Compare current-state model against target-state pattern, produce structured gap list with severity scores |

---

### 9. New Knowledge YAMLs

| File | Purpose |
|---|---|
| `cortex-registry/knowledge/best-practices/business/po-change-intelligence.yaml` | PO change intelligence best practices |
| `cortex-registry/knowledge/best-practices/business/requirements-best-practices.yaml` | Requirements engineering best practices |

---

### 10. `MasterOrchestrator` Routing Updates

Add to `INTENT_TRIGGER_MAP` in `cortex/orchestrators/core/master_orchestrator.py`:

```python
IntentType.CHANGE_INTELLIGENCE: ChangeIntelligenceOrchestrator,
IntentType.REQUIREMENTS: RequirementsOrchestrator,
```

---

### 11. Display Name Map Addition

Add to breadcrumb display name map in `copilot-instructions.md`, `CORTEX.prompt.md`, and `cortex-response-templates.md`:

| Class Name | Display Name |
|---|---|
| ChangeIntelligenceOrchestrator | Change Analyst |
| RequirementsOrchestrator | Requirements Engineer |

---

## Orchestration Chain (Conceptual)

```
📥 PO Request
 │
 ├─ "What does the system do?"
 │   → ChangeIntelligenceOrchestrator
 │     → po/process-discovery → po/capability-summary
 │       → Inline: Current-State Documentation
 │
 ├─ "Compare current process to best practice"
 │   → ChangeIntelligenceOrchestrator
 │     → po/process-discovery → po/best-practice-comparison
 │       → Inline: Gap Analysis + Recommendations
 │
 ├─ "Generate requirements for this change"
 │   → RequirementsOrchestrator
 │     → po/requirements-synthesis (composes sdlc/requirements-analysis)
 │       → Inline: Business + Functional + NFR + AC
 │
 ├─ "What's the ROI of this change?"
 │   → ChangeIntelligenceOrchestrator
 │     → po/roi-analysis (adapts ROICompositeScorer)
 │       → Inline: ROI Artifact with Priority Tier
 │
 ├─ "Should we build this idea?"
 │   → ChangeIntelligenceOrchestrator
 │     → po/change-recommendation (composes impact + challenge)
 │       → Inline: Recommendation + Risk + Feasibility
 │
 └─ "Create training docs for this change"
     → TrainerOrchestrator (enhanced)
       → po/training-doc-generation
         → Inline: Role-Based Training Materials
```

**Traceability spine:**
`process-discovery` → `best-practice-comparison` → `change-recommendation` → `requirements-synthesis` → implementation (existing TDD pipeline) → `training-doc-generation`

---

## Phase Dependencies

| Phase | Dependency |
|---|---|
| Phase 142 | No hard dependencies — can run independently of Phase 141 |
| Phase 141 | Deep Intelligence Wiring — enhances IntelligenceFacade (benefits 142 but not required) |

---

## Sub-Phase Execution Order

| Sub-Phase | Title | Duration Est. | GAPs |
|---|---|---|---|
| 142-a | Intent Types + Routing | 2 hours | 3 |
| 142-b | Gap Comparison Primitive | 1 hour | 1 |
| 142-c | PO Workflow Templates (7) | 4 hours | 7 |
| 142-d | ChangeIntelligenceOrchestrator | 4 hours | 3 |
| 142-e | RequirementsOrchestrator | 3 hours | 3 |
| 142-f | TrainerOrchestrator Enhancement | 2 hours | 2 |
| 142-g | Agent, Knowledge & Prompts | 2 hours | 3 |
| **Total** | | **~18 hours** | **20 GAPs** |

---

## Design Pillar Evaluation

| Pillar | Score | Evidence |
|---|---|---|
| **Extensibility** | ✅ High | 7 templates reusable across all 3 orchestrators + future PO workflows |
| **Scalability** | ✅ High | Workflow Composer supports 600+ templates — 7 additions negligible |
| **Accuracy** | ✅ High | LENS-powered discovery + ROICompositeScorer = data-driven |
| **Collaboration** | ✅ High | PO ↔ Dev ↔ QA ↔ Training traceability through artifact chain |
| **Maintainability** | ✅ High | 3 orchestrators (not 7) — clean ownership boundaries |

---

## Files Created This Session

| File | Type | Purpose |
|---|---|---|
| `cortex-registry/planning/phases/planned/phase-142-po-change-intelligence.yaml` | Phase Detail | Full phase plan with 20 GAPs, 7 sub-phases, TDD sequences |
| `cortex-registry/cortex-master.yaml` | Updated | Thin index entry for phase-142, metadata bumped |
| `_workspaces/_feedback/2026-03-08-po-change-intelligence.md` | Feedback | This documentation update guide |
