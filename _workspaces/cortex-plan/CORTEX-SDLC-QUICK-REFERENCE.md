# CORTEX SDLC Self-Improvement - Quick Reference

**Phase:** SDLC-001 | **Priority:** P0 Critical | **Duration:** 3-4 weeks  
**Source:** sesh01-tdd-break.md digest analysis | **Status:** PLANNED

---

## 🎯 WHY THIS EXISTS

**Phase 21 Failure Analysis** revealed CORTEX cannot properly plan its own features:

| Root Cause | Evidence | Impact |
|------------|----------|--------|
| No Planning Phase | PlanningOrchestrator: 0 calls | Features started without design |
| Shallow Planning | Phases only, no code specs | Schema misalignments at runtime |
| No Cross-Layer Validation | Python vs JS mismatches | 60% of bugs were alignment issues |
| No Post-Phase Review | Phases marked "complete" blindly | Cascading failures for 4+ hours |
| MCP Gateway Bypass | Direct chat skipped governance | All CORTEX rules bypassed |

---

## 🚀 KEY ENHANCEMENTS

### 1. PlanningOrchestrator v4.0

**Current:** Plans phases ("Implement Data Layer")  
**Enhanced:** Plans to code level (files, functions, interfaces)

```python
# NEW: Code-Level Planning
plan = planning_orchestrator.generate_code_level_plan(task, lens_context)
# Returns:
#   - FileSpec: Which files to create/modify
#   - FunctionSpec: Function signatures with types
#   - InterfaceContract: Python ↔ JavaScript alignment
#   - TestSpec: Required tests (TDD-first)

# NEW: Cross-Layer Coherence
report = planning_orchestrator.validate_cross_layer_coherence(plan)
# Checks:
#   - Enum value alignment (CRITICAL vs "critical")
#   - Field name consistency (snake_case vs camelCase)
#   - Type compatibility (Pydantic vs JSON Schema)

# NEW: Post-Phase Review
result = planning_orchestrator.execute_post_phase_review(phase_id)
# Runs:
#   - Phase-specific tests
#   - Cross-layer contracts
#   - LENS analysis for new issues
#   - Gates next phase on pass
```

### 2. InteractionOrchestrator Enhancement

**Current:** IMPLEMENT → TDDOrchestrator (direct)  
**Enhanced:** IMPLEMENT → PlanningOrchestrator → TDDOrchestrator

```
User Request (IMPLEMENT)
    ↓
LENS Context Build
    ↓
Challenge Generation
    ↓
Planning Phase (NEW) ← PlanningOrchestrator
    ├─ Generate CodeLevelPlan
    ├─ Validate Coherence
    └─ Present Plan in DoR
    ↓
User Approval (DoR includes Plan)
    ↓
TDD Execution (per plan)
    ↓
Post-Phase Review (after each phase)
```

### 3. New MCP Tools

| Tool | Purpose |
|------|---------|
| `cortex_generate_code_plan` | Generate code-level plan (no code generation) |
| `cortex_validate_plan_coherence` | Validate cross-layer alignment |
| `cortex_execute_phase_review` | Run post-phase verification |
| `cortex_coordinate_layers` | Coordinate multi-layer design |
| `cortex_validate_integration` | Validate layer integration |

---

## 📊 DATA MODELS

### CodeLevelPlan

```yaml
task_id: "TASK-001"
file_specs:
  - path: "cortex/visualization/adapters/sqlite_adapter.py"
    action: CREATE
    purpose: "SQLite implementation of DashboardDataAdapter"
    estimated_loc: 150
    language: "Python"
    
function_specs:
  - file_path: "cortex/visualization/adapters/sqlite_adapter.py"
    name: "load"
    signature: "def load(self, repo_slug: str) -> DashboardData"
    purpose: "Load dashboard data from SQLite"
    inputs: [{name: repo_slug, type: str}]
    outputs: {type: DashboardData}
    test_cases: [test_load_existing, test_load_missing]
    
interface_contracts:
  - contract_id: "severity_enum_alignment"
    python_side:
      file: "cortex/models/dashboard_schema_v3.py"
      type: "SeverityLevel"
      values: [CRITICAL, HIGH, MEDIUM, LOW, INFO]
    javascript_side:
      file: "spa/js/data/SQLiteDataLayer.js"
      type: "Severity"
      values: [critical, high, medium, low, info]
    field_mappings:
      CRITICAL: critical
      HIGH: high
```

### CoherenceReport

```yaml
status: FAIL
issues:
  - type: ENUM_MISMATCH
    python: "SeverityLevel.HIGH"
    javascript: "Severity.high"
    recommendation: "Add mapping: HIGH → 'high'"
    
  - type: FIELD_NAME_MISMATCH
    python: "type"
    javascript: "category"
    recommendation: "Rename JS field or add alias"
```

---

## 📅 IMPLEMENTATION TIMELINE

| Week | Phases | Deliverables |
|------|--------|--------------|
| **1** | 0-1 | Data models + Code-level planning |
| **2** | 1-2 | Code-level planning + Coherence validation |
| **3** | 3-4 | Post-phase review + Interaction enhancement |
| **4** | 5-6 | MCP tools + Prompt/agent updates |

---

## ✅ SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | ≥ 85% | pytest --cov |
| Schema Misalignments | 0 in production | Contract tests pass |
| Planning Adoption | 100% of IMPLEMENT | Audit trail |
| Time to First Feature | < 2 hours | Request → E2E pass |
| Debugging Reduction | 50% less | Comparison study |
| Plan Iterations | < 2 per DoR | Approval tracking |

---

## 🔗 RELATED FILES

| File | Purpose |
|------|---------|
| [CORTEX-SELF-IMPROVEMENT-SDLC.yaml](./CORTEX-SELF-IMPROVEMENT-SDLC.yaml) | Full specification |
| [PHASE-21-JSON-FIRST-REWRITE.yaml](./PHASE-21-JSON-FIRST-REWRITE.yaml) | Dashboard rewrite plan |
| [enhanced_planning_orchestrator.py](../../cortex/orchestrators/domain/enhanced_planning_orchestrator.py) | Current implementation |
| [interaction_orchestrator.py](../../cortex/orchestrators/core/interaction_orchestrator.py) | Current implementation |

---

## 🚦 QUICK START (After Implementation)

```bash
# 1. Generate code-level plan for a feature
cortex_generate_code_plan --task "Add SQLite adapter" --modules cortex.visualization

# 2. Validate cross-layer coherence
cortex_validate_plan_coherence --plan plan.yaml

# 3. After completing a phase, run review
cortex_execute_phase_review --phase-id "phase-1-data-models"

# 4. Coordinate multi-layer feature
cortex_coordinate_layers --task task.yaml --layers backend,frontend,data
```

---

*Created: 2026-02-04 | Source: Phase 21 failure digest*
