#!/usr/bin/env python3
"""Phase 70 S1: Gap Triage & Decision Framework - Execution Tasks

This script generates the decision matrix for all identified alignment gaps.
Each gap is classified with an explicit resolution decision.

Usage:
    python scripts/phase-70-gap-triage.py

Output:
    - gap-triage-matrix.yaml (decisions for all gaps)
    - gap-implementation-backlog.md (prioritized tasks)
    
Author: CORTEX Framework (Autonomous Execution)
AC-ID: AC-PHASE70-S1-001
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class ResolutionOption(Enum):
    IMPLEMENT = "IMPLEMENT"
    REMOVE = "REMOVE_FROM_WIRING"
    DEFER = "MARK_PLANNED"
    DELETE_TEST = "DELETE_TEST"
    IMPLEMENT_TEST = "IMPLEMENT_TEST"


@dataclass
class GapDecision:
    gap_id: str
    gap_type: str
    component: str
    priority: str
    resolution: str
    rationale: str
    effort_hours: float
    target_phase: Optional[str] = None
    owner: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    notes: Optional[str] = None


def generate_gap_decisions() -> list[GapDecision]:
    """Generate decision matrix for all identified gaps."""
    
    decisions = [
        # ====================================================================
        # P0/P1 WIRED_NOT_IMPLEMENTED: Domain Orchestrators
        # ====================================================================
        GapDecision(
            gap_id="WIRED-001",
            gap_type="WIRED_NOT_IMPLEMENTED",
            component="RefactoringOrchestrator",
            priority="P1",
            resolution="IMPLEMENT",
            rationale="Already partially implemented in cortex/refactoring/. Need to move to cortex/orchestrators/domain/ and wire fully. Domain-tier orchestrator critical for refactoring workflows.",
            effort_hours=8,
            target_phase="phase-70",
            acceptance_criteria="✅ Full specification coverage with tests, MCP adapter, LENS integration, wired in wiring.yaml",
            owner="CORTEX-Autonomous",
        ),
        GapDecision(
            gap_id="WIRED-002",
            gap_type="WIRED_NOT_IMPLEMENTED",
            component="PlanningOrchestrator",
            priority="P1",
            resolution="IMPLEMENT",
            rationale="Domain-tier orchestrator wired but not found in cortex/orchestrators/domain/. TDD implementation needed. High-value for multi-phase planning workflows.",
            effort_hours=12,
            target_phase="phase-70",
            acceptance_criteria="✅ TDD (test before code), MCP adapter, LENS integration, EnforcementOrchestrator gate passing",
            owner="CORTEX-Autonomous",
        ),
        
        # ====================================================================
        # P1 STUB TESTS: assert True Patterns (Sample - Bulk decisions)
        # ====================================================================
        GapDecision(
            gap_id="STUB-001",
            gap_type="STUB_TEST",
            component="tests/unit/visualization/test_spa_phase_b.py (27 tests)",
            priority="P1",
            resolution="DELETE_TEST",
            rationale="Placeholder tests with no real assertions (assert True, 'Phase B gate' comments). No implementation exists. Safe to delete.",
            effort_hours=0.5,
            target_phase="phase-70",
            acceptance_criteria="✅ Tests deleted, verified no broken imports",
            owner="CORTEX-Autonomous",
            notes="Identified in initial audit: 27x 'assert True' with documentation-only assertions",
        ),
        GapDecision(
            gap_id="STUB-002",
            gap_type="STUB_TEST",
            component="tests/unit/domain_brain/test_synthesis_domain_integration.py (8+ tests)",
            priority="P1",
            resolution="DELETE_TEST",
            rationale="8 consecutive 'assert True' at lines 1066-1094. No real test logic. Safe to delete.",
            effort_hours=0.5,
            target_phase="phase-70",
            acceptance_criteria="✅ Tests deleted, coverage metrics updated",
            owner="CORTEX-Autonomous",
        ),
        GapDecision(
            gap_id="STUB-003",
            gap_type="STUB_TEST",
            component="tests/test_phase_52_s1_4_integration.py:172",
            priority="P1",
            resolution="DELETE_TEST",
            rationale="Single 'assert True' in phase integration test. No real assertion value.",
            effort_hours=0.25,
            target_phase="phase-70",
            acceptance_criteria="✅ Test deleted",
            owner="CORTEX-Autonomous",
        ),
        GapDecision(
            gap_id="STUB-004",
            gap_type="STUB_TEST",
            component="tests/unit/core/orchestrator/test_production_validation.py (9 tests)",
            priority="P1",
            resolution="DELETE_TEST",
            rationale="All 9 tests are 'assert True' with environment-dependent comments. No production-grade assertions. Delete and document expectations.",
            effort_hours=0.5,
            target_phase="phase-70",
            acceptance_criteria="✅ Tests deleted, environment validation documented separately",
            owner="CORTEX-Autonomous",
        ),
        
        # ====================================================================
        # P1 SKIPPED TESTS: Excessive Skip Markers (257 total)
        # ====================================================================
        GapDecision(
            gap_id="SKIP-001",
            gap_type="SKIPPED_TEST",
            component="tests/orchestrators/capacity/__init__.py (40+ pytest.skip)",
            priority="P1",
            resolution="DELETE_TEST",
            rationale="40+ consecutive 'pytest.skip(\"Implementation pending\")' in capacity tests. Phase 12 feature not scheduled. Delete tests and move to phase-70 if needed.",
            effort_hours=1,
            target_phase="phase-72-future",
            acceptance_criteria="✅ Tests deleted or moved to separate test file marked 'pending-phase-12'",
            owner="CORTEX-Autonomous",
            notes="All tests in capacity/__init__.py are skipped - entire file can be archived",
        ),
        GapDecision(
            gap_id="SKIP-002",
            gap_type="SKIPPED_TEST",
            component="tests/_legacy_broken/ (8 files with pytest.skip)",
            priority="P1",
            resolution="DELETE_TEST",
            rationale="Entire _legacy_broken directory contains skipped legacy tests. Should be archived, not kept in active test suite.",
            effort_hours=0.5,
            target_phase="phase-70",
            acceptance_criteria="✅ Directory moved to tests/_archived_legacy/ or deleted entirely",
            owner="CORTEX-Autonomous",
        ),
        
        # ====================================================================
        # P2 STUB CODE: NotImplementedError in Production (25+ instances)
        # ====================================================================
        GapDecision(
            gap_id="STUB-CODE-001",
            gap_type="STUB_CODE",
            component="cortex/orchestrators/capacity/capacity_orchestrators.py:47",
            priority="P2",
            resolution="DEFER",
            rationale="CapacityOrchestrator: 'raise NotImplementedError(\"Implementation pending - Phase 12 CAP-1\")'. Phase 12 is future. Mark stub status in wiring.yaml.",
            effort_hours=0.25,
            target_phase="phase-72",
            acceptance_criteria="✅ Wiring.yaml annotated: status='stub', phase-target='phase-72'",
            owner="CORTEX-Autonomous",
            notes="Legitimate future feature - not a bug",
        ),
        GapDecision(
            gap_id="STUB-CODE-002",
            gap_type="STUB_CODE",
            component="cortex_brain/tier2/governance/cost_tracking.py (STUB IMPLEMENTATION comment)",
            priority="P2",
            resolution="DEFER",
            rationale="CostTracker: Documented stub for Phase E. Add to roadmap with explicit status.",
            effort_hours=0.25,
            target_phase="phase-e-future",
            acceptance_criteria="✅ Wiring.yaml has 'CostTrackerOrchestrator' marked as 'planned'",
            owner="CORTEX-Autonomous",
        ),
        
        # ====================================================================
        # P2 WIRED_NOT_IMPLEMENTED: Support Orchestrators (23 missing)
        # ====================================================================
        GapDecision(
            gap_id="WIRED-003",
            gap_type="WIRED_NOT_IMPLEMENTED",
            component="ContextCrystallizationLayerEnhanced (P90)",
            priority="P2",
            resolution="DEFER",
            rationale="Phase 49 already has ContextCrystallizationLayer. Enhanced version is future optimization. Keep in wiring as 'planned'.",
            effort_hours=0,
            target_phase="phase-75-future",
            acceptance_criteria="✅ Wiring.yaml: status='planned', notes='optimization track'",
            owner=None,
        ),
        GapDecision(
            gap_id="WIRED-004",
            gap_type="WIRED_NOT_IMPLEMENTED",
            component="ContentExtractionEngine (P88)",
            priority="P2",
            resolution="DEFER",
            rationale="Future content processing feature. Evaluate need after phase-70. Keep in wiring as 'planned'.",
            effort_hours=0,
            target_phase="phase-76-future",
            acceptance_criteria="✅ Wiring.yaml marked as 'planned', ROI evaluation pending",
            owner=None,
        ),
        # ... (23 total support orchestrators - use bulk decision template)
        GapDecision(
            gap_id="WIRED-005-TO-025",
            gap_type="WIRED_NOT_IMPLEMENTED",
            component="21 additional support orchestrators (P67-P90)",
            priority="P2",
            resolution="DEFER",
            rationale="Bulk decision: High-priority support features (P76+) should be implemented on-demand. Keep in wiring with 'planned' status. Prioritize by ROI when scheduling.",
            effort_hours=0,
            target_phase="phase-71-onward",
            acceptance_criteria="✅ All 21 marked as 'planned' in wiring.yaml with ROI scores and phase targets",
            owner="CORTEX-Architect",
            notes="Use cortex-architect review cycle for quarterly prioritization",
        ),
        
        # ====================================================================
        # P3 IMPLEMENTED_NOT_WIRED: Orphaned Components (154 instances)
        # ====================================================================
        GapDecision(
            gap_id="ORPHAN-001-TO-154",
            gap_type="IMPLEMENTED_NOT_WIRED",
            component="154 orphaned implementations (test helpers, adapters, internal classes)",
            priority="P3",
            resolution="MARK_INTERNAL",
            rationale="Bulk decision: Most are test helpers, adapters, or internal utilities. Add 'internal_only: true' to wiring.yaml. Delete if unused after grep verification.",
            effort_hours=2,
            target_phase="phase-70-s3",
            acceptance_criteria="✅ Grep search confirms no external callers for each, marked as internal or deleted",
            owner="CORTEX-Autonomous",
            notes="Batch process using audit_alignment.py output as reference",
        ),
    ]
    
    return decisions


def save_gap_matrix(decisions: list[GapDecision]) -> None:
    """Save gap decision matrix to YAML file."""
    output_path = Path("cortex-registry/_cortex-master/phase-70-gap-triage-matrix.yaml")
    
    gap_matrix = {
        "version": "1.0",
        "created": "2026-02-10",
        "phase": "phase-70-s1",
        "ac_id": "AC-PHASE70-S1-001",
        "total_gaps": len(decisions),
        "decisions": [asdict(d) for d in decisions],
    }
    
    with open(output_path, "w") as f:
        yaml.dump(gap_matrix, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Gap matrix saved: {output_path}")


def generate_implementation_backlog(decisions: list[GapDecision]) -> str:
    """Generate prioritized implementation backlog markdown."""
    
    output = """# Phase 70 S1: Gap Triage - Implementation Backlog

**AC-ID:** AC-PHASE70-S1-001  
**Created:** 2026-02-10  
**Updated:** 2026-02-10  
**Status:** GENERATED (READY FOR AUTONOMOUS EXECUTION)

---

## Executive Summary

| Category | Count | Resolution | Timeline |
|----------|-------|-----------|----------|
| P0/P1 Gaps | 4 | IMPLEMENT + DELETE | Phase 70 S2 (Immediate) |
| P1 Stub Tests | 620 | DELETE or IMPLEMENT | Phase 70 S2 (Bulk cleanup) |
| P1 Skipped Tests | 257 | DELETE or ARCHIVE | Phase 70 S2 (1-2 days) |
| P2 STUB Code | 25 | DEFER (mark status) | Phase 70 S3 (Documentation) |
| P2 Wired-Not-Impl | 23 | DEFER (planned) | Phase 70 S3 (Wiring updates) |
| P3 Orphaned | 154 | MARK_INTERNAL | Phase 70 S3 (Cleanup) |
| **TOTAL** | **1,083** | **100% Decided** | **3-5 weeks** |

---

## Phase 70 S2: IMMEDIATE ACTION ITEMS (P0/P1 - Week 1-2)

### 1. IMPLEMENT: RefactoringOrchestrator

**Gap ID:** WIRED-001  
**Component:** RefactoringOrchestrator  
**Priority:** P1  
**Status:** 🔴 WIRED_NOT_IMPLEMENTED (exists in cortex/refactoring but not cortex/orchestrators)  
**Effort:** 8 hours  
**Owner:** CORTEX-Autonomous  

**Decision:** IMPLEMENT + MOVE

```yaml
task:
  id: "TASK-70-S2-001"
  title: "Implement RefactoringOrchestrator (Move from cortex/refactoring → cortex/orchestrators/domain)"
  acceptance_criteria:
    - "Move implementation to cortex/orchestrators/domain/refactoring_orchestrator.py"
    - "Add full MCP adapter in cortex/mcp/adapters/"
    - "Wire in wiring.yaml with full metadata"
    - "20+ tests covering all operations"
    - "LENS integration verified"
    - "EnforcementOrchestrator validation passing"
  effort_hours: 8
  tdd_required: true
  steps:
    - "Write test_refactoring_orchestrator_core.py (specs)"
    - "Move cortex/refactoring/orchestrator.py → cortex/orchestrators/domain/refactoring_orchestrator.py"
    - "Adapt to IOrchestrator interface"
    - "Create MCP adapter"
    - "Add LENS integration"
    - "Update wiring.yaml"
    - "Run full test suite"
    - "Commit: 'Phase 70 S2: Implement RefactoringOrchestrator'"
```

### 2. IMPLEMENT: PlanningOrchestrator

**Gap ID:** WIRED-002  
**Component:** PlanningOrchestrator  
**Priority:** P1  
**Status:** 🔴 WIRED_NOT_IMPLEMENTED  
**Effort:** 12 hours  
**Owner:** CORTEX-Autonomous  

**Decision:** IMPLEMENT (TDD from scratch)

```yaml
task:
  id: "TASK-70-S2-002"
  title: "Implement PlanningOrchestrator (TDD from scratch)"
  acceptance_criteria:
    - "Core PlanningOrchestrator class with IOrchestrator interface"
    - "Phase planning logic (predecessor analysis, critical path)"
    - "Risk assessment integration"
    - "MCP tool adapter"
    - "LENS integration for plan enrichment"
    - "25+ tests (85%+ coverage)"
    - "EnforcementOrchestrator validation passing"
  effort_hours: 12
  tdd_required: true
  steps:
    - "Write test_planning_orchestrator_spec.py (all acceptance criteria)"
    - "RED: Watch tests fail"
    - "GREEN: Implement cortex/orchestrators/domain/planning_orchestrator.py"
    - "REFACTOR: Extract utilities, add LENS integration"
    - "Create MCP adapter"
    - "Update wiring.yaml"
    - "Commit: 'Phase 70 S2: Implement PlanningOrchestrator'"
```

### 3. DELETE: Stub Tests (Bulk Operation)

**Gap ID:** STUB-001 through STUB-004  
**Type:** STUB_TEST (assert True patterns)  
**Count:** 620 tests  
**Priority:** P1  
**Decision:** DELETE (no implementation value)  

```yaml
task:
  id: "TASK-70-S2-003"
  title: "Delete 620 Stub Tests (assert True patterns)"
  acceptance_criteria:
    - "grep -rn 'assert True' tests/ → 0 results"
    - "No import errors after deletion"
    - "Test count: 4459 → 3839"
    - "Coverage metrics updated"
  effort_hours: 4
  steps:
    - "Run: python scripts/audit_alignment.py > baseline.txt"
    - "Find all 'assert True' locations: grep -rn 'assert True' tests/ | tee stub-tests.txt"
    - "Delete files/functions with no real assertions"
    - "Run pytest to verify no import errors"
    - "Run: python scripts/audit_alignment.py > after-cleanup.txt"
    - "Commit: 'Phase 70 S2: Delete 620 stub tests (assert True patterns)'"
```

### 4. ARCHIVE: Skipped Tests (257 skip markers)

**Gap ID:** SKIP-001, SKIP-002  
**Type:** SKIPPED_TEST  
**Count:** 257 tests  
**Priority:** P1  
**Decision:** DELETE or ARCHIVE  

```yaml
task:
  id: "TASK-70-S2-004"
  title: "Archive 257 Skipped Tests (pytest.skip markers)"
  acceptance_criteria:
    - "tests/_archived_legacy/ created with skipped tests"
    - "Active test suite: skip count < 10"
    - "No 'pytest.skip(\"Implementation pending\")' in active tests"
    - "Documented which phases will re-activate these"
  effort_hours: 2
  steps:
    - "Create tests/_archived_legacy/ directory"
    - "Move tests/orchestrators/capacity/__init__.py → tests/_archived_legacy/"
    - "Move tests/_legacy_broken/* → tests/_archived_legacy/"
    - "Document in tests/_archived_legacy/README.md which phases restore these"
    - "Run pytest (should show fewer skips)"
    - "Commit: 'Phase 70 S2: Archive 257 skipped tests (pending features)'"
```

---

## Phase 70 S3: DEFERRED ACTIONS (P2 - Week 2-3)

### 5. MARK_INTERNAL: Orphaned Components (154 instances)

**Gap ID:** ORPHAN-001-TO-154  
**Type:** IMPLEMENTED_NOT_WIRED  
**Count:** 154 components  
**Priority:** P3  
**Decision:** Mark as internal_only or delete if unused  

```yaml
task:
  id: "TASK-70-S3-001"
  title: "Audit & Mark 154 Orphaned Implementations"
  acceptance_criteria:
    - "Each component: grep -rn 'ComponentName' --include='*.py' verified for external callers"
    - "Update wiring.yaml: add 'internal_only: true' or 'status: deprecated'"
    - "Delete truly unused components (no external callers)"
    - "Document orphaned patterns for team learning"
  effort_hours: 3
  steps:
    - "Run audit_alignment.py to get orphaned list"
    - "For each: grep -rn 'ClassName' cortex/ --include='*.py' | grep -v 'test' | grep -v 'self' count"
    - "If count == 1 (only def): mark 'internal_only' or delete"
    - "If count > 1: mark 'internal_only' (has callers)"
    - "Update wiring.yaml with status annotations"
    - "Commit: 'Phase 70 S3: Audit orphaned implementations, mark internal/deprecated'"
```

### 6. DEFER: Support Orchestrators (23 wired-not-impl)

**Gap ID:** WIRED-003 through WIRED-025  
**Type:** WIRED_NOT_IMPLEMENTED (support tier)  
**Count:** 23 orchestrators  
**Priority:** P2  
**Decision:** Keep in wiring.yaml as 'planned', prioritize by ROI  

```yaml
task:
  id: "TASK-70-S3-002"
  title: "Update wiring.yaml: Mark 23 Support Orchestrators as 'Planned'"
  acceptance_criteria:
    - "All 23 have status: 'planned' annotation"
    - "Each has phase-target documented (e.g., phase-71, phase-75)"
    - "ROI scores reviewed and realistic"
    - "wiring.yaml validates without errors"
  effort_hours: 1
  steps:
    - "Edit wiring.yaml"
    - "Find all support orchestrators without implementation"
    - "Add: status: planned, phase_target: phase-7X"
    - "Add: rationale: {{explanation}}"
    - "Validate YAML"
    - "Commit: 'Phase 70 S3: Mark 23 support orchestrators as planned'}"
```

### 7. DEFER: STUB Code (25+ instances)

**Gap ID:** STUB-CODE-001, STUB-CODE-002  
**Type:** STUB_CODE (NotImplementedError + TODO)  
**Count:** 25+ instances  
**Priority:** P2  
**Decision:** Document future phase targets, keep marked as 'TODO - Phase X'  

```yaml
task:
  id: "TASK-70-S3-003"
  title: "Document STUB Code: Target Future Phases"
  acceptance_criteria:
    - "Every NotImplementedError message includes phase target"
    - "Every TODO comment includes issue tracker reference"
    - "Documented in phase roadmap where stubs will be implemented"
  effort_hours: 1
  steps:
    - "grep -rn 'NotImplementedError' cortex/ --include='*.py' | grep -v test"
    - "Update each message: 'Implementation pending - Phase X (scheduled Y quarter)'"
    - "grep -rn '# TODO' cortex/ --include='*.py' | grep -v test"
    - "Update each TODO: '# TODO (Phase X): {{description}}'"
    - "Update phase roadmap to list known stubs"
    - "Commit: 'Phase 70 S3: Document STUB code targets'}"
```

---

## Phase 70 S4: CONTINUOUS MONITORING (Week 3-4)

### 8. IMPLEMENT: CI/CD Automation

**Gap ID:** CI-001  
**Type:** CONTINUOUS_VALIDATION  
**Decision:** Implement automated alignment gate  

```yaml
task:
  id: "TASK-70-S4-001"
  title: "Implement CI/CD Alignment Gate (GitHub Actions)"
  acceptance_criteria:
    - "alignment-check.yml created in .github/workflows/"
    - "Runs on: push (main/develop), schedule (weekly)"
    - "Fails if P0/P1 gaps detected"
    - "Slack notification on failure"
    - "Status badge shows alignment score"
  effort_hours: 4
  steps:
    - "Create .github/workflows/alignment-check.yml"
    - "Add: python scripts/audit_alignment.py --strict"
    - "Add: Slack notification integration"
    - "Test locally: github actions act"
    - "Commit: 'Phase 70 S4: Add CI/CD alignment gate'"
```

---

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Wiring Gaps | 25 | 0 (resolved or deferred) |
| Stub Tests | 620 | 0 (deleted) |
| Skipped Tests | 257 | <10 (legitimate only) |
| STUB Code | 25+ | Documented with phase targets |
| Alignment Score | 62% | 95%+ |
| Production Ready | ❌ | ✅ |

---

## Next Steps

1. **Execute TASK-70-S2-001 through S2-004** (Week 1-2)
   - Focus on P0/P1 (blocking production)
   - Autonomous execution with daily status reports

2. **Execute TASK-70-S3-001 through S3-003** (Week 2-3)
   - Clean up P2/P3 gaps
   - Document decisions for team learning

3. **Execute TASK-70-S4-001** (Week 3-4)
   - Activate continuous monitoring
   - Prevent future regressions

4. **Production Readiness Signal**
   - All P0/P1 complete
   - CI/CD gates active
   - Team trained on alignment discipline

---

**Phase 70 S1 Complete:** Gap Triage Matrix Generated ✅  
**Ready for:** Autonomous S2 Execution  
**Estimated Completion:** 2026-03-31  
**Authorization:** cortex-architect.prompt.md v15.0
"""
    
    return output


def main():
    """Generate and save Phase 70 S1 decisions."""
    print("🚀 Phase 70 S1: Gap Triage & Decision Framework")
    print("=" * 60)
    
    # Generate decisions
    decisions = generate_gap_decisions()
    
    # Save gap matrix
    save_gap_matrix(decisions)
    
    # Generate implementation backlog
    backlog_md = generate_implementation_backlog(decisions)
    backlog_path = Path("cortex-registry/_cortex-master/phase-70-implementation-backlog.md")
    backlog_path.write_text(backlog_md)
    print(f"✅ Implementation backlog saved: {backlog_path}")
    
    # Print summary
    print(f"\n📊 DECISION MATRIX SUMMARY")
    print(f"Total Gaps Decided: {len(decisions)}")
    
    implement_count = len([d for d in decisions if d.resolution == "IMPLEMENT"])
    delete_count = len([d for d in decisions if d.resolution in ["DELETE_TEST", "DELETE"]])
    defer_count = len([d for d in decisions if d.resolution in ["DEFER", "MARK_PLANNED", "MARK_INTERNAL"]])
    
    print(f"  - IMPLEMENT: {implement_count}")
    print(f"  - DELETE: {delete_count}")
    print(f"  - DEFER/MARK: {defer_count}")
    
    print(f"\n📋 Phase 70 S1 Complete: All gaps have explicit decisions")
    print(f"✅ Ready for: Autonomous S2 Execution (IMPLEMENT phase)")
    print(f"\nAC-COMPLETE: AC-PHASE70-S1-001 ✅")


if __name__ == "__main__":
    main()
