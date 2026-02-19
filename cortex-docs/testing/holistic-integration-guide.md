# Holistic Integration Golden Test Suite

**Authority:** Phase 51 — Holistic Integration Testing  
**Status:** Week 3 Complete (25/25 tests implemented, RED phase)  
**Location:** `tests/golden/holistic_integration/`  
**Created:** 2026-02-18  

---

## Overview

The **Holistic Integration Golden Test Suite** validates CORTEX's full request pipeline from MCP entry point through MasterOrchestrator to final execution. These tests ensure that **all subsystems work together cohesively** on every turn, validating:

- **LENS analysis** — workspace-aware code intelligence
- **CCL pre-warming** — context crystallization <300ms
- **Company YAMLs** — domain-specific best practices
- **Governance enforcement** — CORE rules validated
- **Threat modeling** — OWASP + STRIDE security analysis
- **LLM synthesis** — multi-source coherent narratives
- **Challenge gates** — high-risk alternatives presented
- **Holistic validation** — dependency graphs, regression prevention

---

## Architecture

### 4-Stage Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│ Stage -1: RequestRephraseOrchestrator                            │
│   • Intent classification (QUERY, IMPLEMENT, FIX, REFACTOR, etc.)│
│   • Risk assessment (LOW, MEDIUM, HIGH, CRITICAL)                │
│   • Governance rules injection                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1: InteractionOrchestrator                                 │
│   • LENS analysis (AST, Git, comments)                           │
│   • Challenge generation (alternatives for high-risk)            │
│   • Blind spot detection (edge cases, security concerns)         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 2: IntentRouter                                            │
│   • Orchestrator mapping (IMPLEMENT → TDDOrchestrator)           │
│   • Context routing                                              │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3: Intelligence (parallel subsystems)                      │
│   • CCL: Context pre-warming                                     │
│   • CompanyKnowledgeLoader: Domain YAMLs                         │
│   • LENSOrchestrator: Code analysis                              │
│   • ThreatModelingEngine: Security assessment                    │
│   • HolisticValidationOrchestrator: Dependency graphs            │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 4: Execution                                               │
│   • TDDOrchestrator: Test-first development                      │
│   • EnforcementOrchestrator: CORE rules enforcement              │
│   • LLMSynthesisEngine: Coherent output generation               │
└──────────────────────────────────────────────────────────────────┘
```

---

## Test Structure

### Directory Layout

```
tests/golden/holistic_integration/
├── fixtures/
│   └── holistic_integration_harness.py   (420 LOC)
├── scenarios/
│   ├── S01.yaml  ... S10.yaml   (Simple tier)
│   ├── S11.yaml  ... S20.yaml   (Medium tier)
│   └── S21.yaml  ... S25.yaml   (Complex tier)
├── test_holistic_integration_simple.py   (10 tests, S01-S10)
├── test_holistic_integration_medium.py   (10 tests, S11-S20)
└── test_holistic_integration_complex.py  (5 tests, S21-S25)
```

### Test Tiers

| Tier | Tests | Complexity | Performance | Description |
|------|-------|------------|-------------|-------------|
| **Simple** | S01-S10 | Single component | <2s | Intent classification, LENS, governance, threat modeling |
| **Medium** | S11-S20 | Multi-component | <3s | Full pipeline, multi-domain YAMLs, challenge gates, degraded mode |
| **Complex** | S21-S25 | Holistic system | <5s | End-to-end flows, security audits, regression prevention |

---

## Test Scenarios

### Simple Tier (S01-S10)

| ID | Name | Focus |
|----|------|-------|
| **S01** | Simple QUERY without LENS | Intent classification only |
| **S02** | QUERY with LENS analysis | LENS context populated |
| **S03** | IMPLEMENT intent classification | Governance rules injected |
| **S04** | FIX with low-risk assessment | Risk calculation |
| **S05** | REFACTOR with blind spot detection | Edge case identification |
| **S06** | CCL pre-warming success | Context loaded <300ms |
| **S07** | Company YAML loaded (single domain) | Domain best practices |
| **S08** | Governance enforcement (CORE-002 violation) | Request blocked |
| **S09** | Threat model generation (simple) | STRIDE analysis |
| **S10** | LLM synthesis (simple) | Coherent narrative |

### Medium Tier (S11-S20)

| ID | Name | Focus |
|----|------|-------|
| **S11** | IMPLEMENT with LENS + CCL + governance | Full 4-stage pipeline |
| **S12** | Multi-domain best practices | 3 company YAMLs synthesized |
| **S13** | Challenge gate triggered (high-risk) | Alternatives presented |
| **S14** | Holistic validation gate | Dependency graph + regression risk |
| **S15** | LENS + Git history correlation | Recent changes analyzed |
| **S16** | Complex threat model (OWASP Top 10) | All 10 categories checked |
| **S17** | LLM synthesis (complex, 5+ sources) | Multi-source coherence |
| **S18** | Edge case: Missing dependencies | Graceful degradation |
| **S19** | Blind spot: Circular dependency detection | Architecture warning |
| **S20** | Quality concern: Test coverage <80% | CORE-008 enforcement blocks |

### Complex Tier (S21-S25)

| ID | Name | Focus |
|----|------|-------|
| **S21** | Full e2e: IMPLEMENT new feature | All 11 subsystems engaged |
| **S22** | Complex security audit | PCI-DSS + OWASP + STRIDE |
| **S23** | Multi-domain knowledge synthesis | 5+ domains + LENS + Git |
| **S24** | Regression prevention (Phase 48) | Validation blocks breaking change |
| **S25** | Adaptive onboarding (from chat context) | Dynamic template selection |

---

## Running Tests

### Run All Tests

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m pytest tests/golden/holistic_integration/ -v
```

### Run by Tier

```bash
# Simple tier only (S01-S10)
python3 -m pytest tests/golden/holistic_integration/test_holistic_integration_simple.py -v

# Medium tier only (S11-S20)
python3 -m pytest tests/golden/holistic_integration/test_holistic_integration_medium.py -v

# Complex tier only (S21-S25)
python3 -m pytest tests/golden/holistic_integration/test_holistic_integration_complex.py -v
```

### Run Specific Scenario

```bash
# Run S11 only
python3 -m pytest tests/golden/holistic_integration/test_holistic_integration_medium.py::TestHolisticIntegrationMedium::test_s11_full_pipeline_implementation -v
```

### Current Status (Week 3)

All 25 tests are **implemented but in RED phase** (xfail):

```bash
$ python3 -m pytest tests/golden/holistic_integration/ -v
========================= 25 xfailed in 0.13s =========================
```

**Reason:** MasterOrchestrator execution is not yet wired in the harness. Week 4 will transition RED → GREEN.

---

## Harness Features

### HolisticIntegrationHarness

The test harness (`fixtures/holistic_integration_harness.py`) extends `GoldenTestHarness` with:

1. **Component Failure Injection** — Test degraded mode (S18)
2. **Performance Timing Validation** — <2s simple, <3s medium, <5s complex
3. **LLM Output Snapshot Testing** — Semantic similarity for non-deterministic outputs
4. **CCL Pre-warming Validation** — <300ms threshold
5. **Audit Trail Assertions** — AC_START → AC_COMPLETE sequence validation

### Key Methods

```python
class HolisticIntegrationHarness(GoldenTestHarness):
    def execute_holistic_scenario(
        self,
        scenario_id: str,
        failure_config: Optional[ComponentFailureConfig] = None
    ) -> HolisticTestResult:
        """
        Execute a holistic integration scenario.
        
        Returns:
            HolisticTestResult with:
            - execution_completed (bool)
            - components_engaged (list)
            - ccl_prewarmed (bool)
            - company_yamls_loaded (list)
            - governance_rules_applied (list)
            - performance_metrics (PerformanceMetrics)
            - llm_snapshot (LLMOutputSnapshot)
            - audit_events_matched (bool)
        """
```

---

## Definition of Done (Universal)

Every test must validate:

### ✅ Audit Trail
- AC_START marker present for each operation
- AC_COMPLETE marker present
- Sequence correct (START before COMPLETE)
- No orphaned markers

### ✅ Performance
- Simple scenarios: <2s
- Medium scenarios: <3s
- Complex scenarios: <5s

### ✅ Error Handling
- Graceful degradation on component failures
- Error messages user-friendly
- Audit trail logs errors

### ✅ Idempotency
- Run 3 times → same result
- No side effects in test mode
- Deterministic output

---

## Scenario YAML Format

Each scenario is defined in `scenarios/S##.yaml`:

```yaml
id: "S11"
name: "IMPLEMENT with LENS + CCL + governance"
description: "Full Stage 1-4 pipeline"
complexity: "medium"
intent: "IMPLEMENT"
user_request: "Add JWT authentication"

expected_components:
  - "MasterOrchestrator"
  - "InteractionOrchestrator"
  - "CCL"
  - "LENSOrchestrator"
  - "EnforcementOrchestrator"
  - "TDDOrchestrator"

not_expected:
  - "DebugOrchestrator"

expected_audit_events:
  - activity: "AC_START"
    component: "MasterOrchestrator"
  - activity: "INTENT_CLASSIFIED"
    component: "RequestRephraseOrchestrator"
    intent: "IMPLEMENT"
  - activity: "LENS_ANALYSIS_COMPLETE"
    component: "LENSOrchestrator"
  - activity: "AC_COMPLETE"
    component: "MasterOrchestrator"

dod:
  - "Stage -1: Intent classified as IMPLEMENT"
  - "Stage 1: LENS analysis complete"
  - "CCL: Context pre-warmed"
  - "Stage 2: Intent routed to TDDOrchestrator"
  - "Stage 3: Governance validation passed"
  - "Stage 4: Execution plan created"
  - "Audit trail has all AC_START → AC_COMPLETE pairs"

performance:
  max_duration_seconds: 3.0

expected_outcome:
  execution_completed: true
  ccl_prewarmed: true
  governance_rules_count: 5
  company_yamls_count: 3
```

---

## Week 4 Roadmap

### Transition RED → GREEN

1. **Wire MasterOrchestrator Execution**
   - Modify `HolisticIntegrationHarness.execute_holistic_scenario()`
   - Uncomment: `from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator`
   - Replace stub: `execution_completed = False` with actual orchestrator call
   - Capture correlation_id for audit trail queries

2. **Run Full Test Suite**
   ```bash
   python3 -m pytest tests/golden/holistic_integration/ -v --tb=short
   ```
   - Target: 25/25 tests passing
   - Coverage: ≥95% for tested components

3. **Generate Coverage Report**
   ```bash
   python3 -m pytest tests/golden/holistic_integration/ --cov=cortex --cov-report=html
   ```

4. **Create Performance Baseline**
   - Document 90th percentile timings
   - Establish regression thresholds

5. **Update cortex-master.yaml**
   - Phase 51 status → "COMPLETED"
   - Record completion date
   - Note actual vs estimated effort

---

## Related Documentation

- **Phase 51 Plan:** `cortex-registry/planning/phases/planned/phase-51-holistic-integration-golden-test-suite.yaml`
- **Golden Test Framework:** `docs/golden-test-framework-usage.md`
- **Holistic Validation:** `.github/prompts/cortex-architect.prompt.md § Holistic Validation`
- **Phase 48:** Holistic Validation & Challenge Gate (dependency)
- **CORE-008:** TDD mandatory (tests before implementation)

---

## Metrics (Week 3)

| Metric | Value |
|--------|-------|
| **Total Tests** | 25 |
| **Tests Implemented** | 25 (100%) |
| **Tests Passing** | 0 (RED phase, expected) |
| **Tests xfailed** | 25 (waiting for MasterOrchestrator wiring) |
| **Total LOC** | 1,645 |
| **Harness LOC** | 420 |
| **Test LOC** | 1,225 |
| **Scenario YAMLs** | 25 |
| **Test Collection Time** | 0.07s |
| **Test Execution Time** | 0.13s (xfail validation) |

---

## Success Criteria

- ✅ 25/25 scenarios implemented
- ✅ All scenarios have YAML definitions
- ⏳ All tests passing in CI (Week 4)
- ⏳ Coverage ≥95% (Week 4)
- ⏳ Performance baselines met (Week 4)
- ✅ Documentation complete
- ⏳ cortex-master.yaml updated (Week 4)
- ⏳ Phase 51 marked COMPLETED (Week 4)

---

## Notes

- **Test Philosophy:** Zero-mock testing. Real orchestrators, real SQLite, real components.
- **TDD Enforcement:** All tests written BEFORE MasterOrchestrator wiring (RED phase).
- **Determinism:** Fixed random seeds, stable ordering, idempotent execution.
- **Audit Trail:** Every operation logged with AC_START → AC_COMPLETE markers.
- **Performance:** Baselines ensure no regressions in production.
- **Extensibility:** Phase 52 planned for domain-specific test extensions.

**Authority:** Phase 51 — Holistic Integration Golden Test Suite  
**Created:** 2026-02-18  
**Last Updated:** 2026-02-18 (Week 3 Complete)
