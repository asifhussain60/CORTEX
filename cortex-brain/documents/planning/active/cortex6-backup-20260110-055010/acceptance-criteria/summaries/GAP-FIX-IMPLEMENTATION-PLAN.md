# Gap-Fix Orchestrator Implementation Plan

**Date:** 2026-01-09  
**Version:** 1.0.0  
**Status:** READY FOR IMPLEMENTATION  
**Purpose:** Implement gap-fix orchestrator per `cortex-gap-fix.prompt.md` with repeatable plan integration

---

## 🎯 Executive Summary

**Problem:** `cortex-gap-fix.prompt.md` defines 12-phase autonomous pipeline, but NO Python implementation exists. Additionally, `cortex6-planner/` has incorrect structure (00- prefix, wrong root files) that violates AC-ORC-PLAN-002.

**Solution:** 
1. Implement `src/orchestrators/gap_fix/gap_fix_orchestrator.py` (12 phases)
2. Migrate `cortex6-planner/` to approved structure
3. Enable repeatable gap-fix execution during plan execution

**Key Requirements:**
- ✅ Inject remediation as Phase 0 (blocking issues first)
- ✅ Snowball reordering (foundation → complex)
- ✅ Update progress tracker JSON
- ✅ Repeatable (can run multiple times during execution)
- ✅ Conflict detection (Phase 10B - prevent regressions)
- ✅ Test stability validation (Phase 10C - ensure no test breakage)

---

## 📋 Current State Analysis

### ✅ What Exists

| Item | Location | Status |
|------|----------|--------|
| **Prompt Definition** | `.github/prompts/cortex-gap-fix.prompt.md` | ✅ Complete (v1.3.0) |
| **Manual Gap Findings** | `cortex6-planner/search-findings-20260109.yaml` | ✅ Generated manually |
| **Manual Remediation Plan** | `cortex6-planner/CX6-comprehensive-remediation-plan.yaml` | ✅ Generated manually |
| **AC Source of Truth** | `acceptance-criteria/CX6-acceptance-criteria.yaml` | ✅ v14.4.0 (corrected) |

### ❌ What's Missing

| Item | Required Location | Impact |
|------|-------------------|--------|
| **Gap-Fix Orchestrator** | `src/orchestrators/gap_fix/gap_fix_orchestrator.py` | 🔴 BLOCKING - No autonomous execution |
| **Phase 10 Integration** | Method: `inject_findings_into_plan()` | 🔴 BLOCKING - No plan updates |
| **Snowball Reordering** | Method: `reorder_phases_snowball()` | 🔴 BLOCKING - No strategic ordering |
| **Progress Tracker Update** | Method: `update_progress_tracker()` | 🔴 BLOCKING - No JSON updates |
| **Conflict Detection** | Method: `detect_conflicts()` (Phase 10B) | 🔴 BLOCKING - Regression risk |
| **Test Stability Check** | Method: `validate_test_stability()` (Phase 10C) | 🟠 HIGH - Test breakage risk |

---

## 🏗️ Implementation Architecture

### Phase 10: Plan Integration (CRITICAL)

**Purpose:** Inject gap findings into existing plan with snowball ordering

```python
# src/orchestrators/gap_fix/gap_fix_orchestrator.py

from pathlib import Path
from typing import List, Dict
import json
import yaml

class GapFixOrchestrator:
    
    async def phase_10_integrate_with_plan(
        self,
        findings_file: Path,
        remediation_file: Path,
        plan_path: Path
    ) -> Dict:
        """
        Phase 10: Integrate with Feature Plan
        
        Actions:
        1. Load findings and remediation plan
        2. Detect associated plan (cortex6-planner)
        3. Inject remediation as Phase 0 (Critical Blockers)
        4. Reorder existing phases for snowball effect
        5. Update progress tracker JSON
        6. Generate continuation prompt
        7. Archive old plan structure
        
        Returns:
            {
                "plan_found": bool,
                "phase_injected": bool,
                "phases_reordered": int,
                "progress_updated": bool,
                "tasks_added": int
            }
        """
        
        # Step 1: Load remediation plan
        remediation = yaml.safe_load(remediation_file.read_text())
        
        # Step 2: Check if plan exists
        if not plan_path.exists():
            return {"plan_found": False}
        
        # Step 3: Load current plan structure
        progress_tracker = plan_path / "tracking" / "progress-tracker.json"
        if not progress_tracker.exists():
            raise FileNotFoundError(f"Progress tracker not found: {progress_tracker}")
        
        tracker_data = json.loads(progress_tracker.read_text())
        
        # Step 4: Inject remediation as Phase 0
        new_phase_0 = self._create_remediation_phase(remediation)
        
        # Step 5: Reorder existing phases (shift by +1)
        updated_phases = self._inject_phase_0(tracker_data["phases"], new_phase_0)
        
        # Step 6: Apply snowball reordering
        sorted_phases = self._snowball_reorder(updated_phases)
        
        # Step 7: Update progress tracker
        tracker_data["phases"] = sorted_phases
        tracker_data["total_phases"] = len(sorted_phases)
        tracker_data["last_updated"] = datetime.now().isoformat()
        
        progress_tracker.write_text(json.dumps(tracker_data, indent=2))
        
        # Step 8: Generate continuation prompt
        self._generate_continuation_prompt(plan_path, sorted_phases)
        
        return {
            "plan_found": True,
            "phase_injected": True,
            "phases_reordered": len(sorted_phases),
            "progress_updated": True,
            "tasks_added": len(new_phase_0["tasks"])
        }
    
    def _create_remediation_phase(self, remediation: Dict) -> Dict:
        """
        Create Phase 0 from remediation plan (blocking issues only)
        
        Structure:
        {
            "phase_number": 0,
            "phase_name": "Critical Blockers (Gap-Fix)",
            "status": "pending",
            "priority": "P0_CRITICAL",
            "tasks": [
                {
                    "id": "AC-GOV-001",
                    "description": "SKULL rule migration incomplete",
                    "effort_hours": 6,
                    "test_file": "tests/governance/test_skull_migration.py",
                    "acceptance_criteria": ["All 61 SKULL rules migrated"],
                    "snowball_impact": "Unlocks 15 downstream criteria"
                }
            ],
            "estimated_hours": 48,
            "blocking": true
        }
        """
        
        blocking_issues = [
            issue for phase in remediation.get("phases", [])
            for issue in phase.get("issues", [])
            if issue.get("blocking", False)
        ]
        
        return {
            "phase_number": 0,
            "phase_name": "Critical Blockers (Gap-Fix)",
            "status": "pending",
            "priority": "P0_CRITICAL",
            "tasks": blocking_issues,
            "estimated_hours": sum(issue.get("effort_hours", 0) for issue in blocking_issues),
            "blocking": True,
            "injected_by": "gap-fix",
            "injected_at": datetime.now().isoformat()
        }
    
    def _inject_phase_0(self, existing_phases: List[Dict], new_phase_0: Dict) -> List[Dict]:
        """
        Inject Phase 0 and shift existing phases by +1
        
        Before:
        - Phase 0: Foundation Layer
        - Phase 1: TODO Orchestrator
        - Phase 2: Epic Review
        
        After:
        - Phase 0: Critical Blockers (Gap-Fix) ← INJECTED
        - Phase 1: Foundation Layer (was 0)
        - Phase 2: TODO Orchestrator (was 1)
        - Phase 3: Epic Review (was 2)
        """
        
        # Shift existing phases
        shifted_phases = []
        for phase in existing_phases:
            phase_copy = phase.copy()
            phase_copy["phase_number"] += 1
            shifted_phases.append(phase_copy)
        
        # Prepend Phase 0
        return [new_phase_0] + shifted_phases
    
    def _snowball_reorder(self, phases: List[Dict]) -> List[Dict]:
        """
        Reorder phases for snowball effect (foundation → complex)
        
        Priority Order:
        1. Phase 0 (blocking issues) - LOCKED at position 0
        2. Foundation fixes (unlock most downstream work)
        3. Infrastructure (audit, state, database)
        4. Orchestrators (master, planning, epic review)
        5. Agents & Knowledge
        6. Testing & Validation
        7. Performance & Optimization
        
        Algorithm:
        - Phase 0 remains at position 0 (blocking)
        - Remaining phases sorted by "snowball_impact" score
        - Snowball score = (blocking_count × 10) + (dependency_unlock_count × 5) + (test_coverage_gain × 2)
        """
        
        # Lock Phase 0
        phase_0 = phases[0]
        remaining = phases[1:]
        
        # Calculate snowball scores
        scored_phases = []
        for phase in remaining:
            score = self._calculate_snowball_score(phase)
            scored_phases.append((score, phase))
        
        # Sort by score (descending)
        scored_phases.sort(key=lambda x: x[0], reverse=True)
        
        # Reassign phase numbers
        sorted_phases = [phase_0]
        for i, (score, phase) in enumerate(scored_phases, start=1):
            phase["phase_number"] = i
            phase["snowball_score"] = score
            sorted_phases.append(phase)
        
        return sorted_phases
    
    def _calculate_snowball_score(self, phase: Dict) -> int:
        """
        Calculate snowball impact score
        
        Factors:
        - Blocking tasks: +10 per task
        - Dependency unlocks: +5 per unlock
        - Test coverage gain: +2 per percentage point
        - Foundation work: +20 (one-time bonus)
        """
        
        score = 0
        
        # Blocking tasks
        blocking_count = sum(1 for task in phase.get("tasks", []) if task.get("blocking", False))
        score += blocking_count * 10
        
        # Dependency unlocks
        unlocks = phase.get("unlocks_downstream", 0)
        score += unlocks * 5
        
        # Test coverage gain
        coverage_gain = phase.get("test_coverage_gain_percent", 0)
        score += coverage_gain * 2
        
        # Foundation bonus
        if "foundation" in phase.get("phase_name", "").lower():
            score += 20
        
        return score
    
    def _generate_continuation_prompt(self, plan_path: Path, phases: List[Dict]) -> None:
        """
        Generate continuation-prompt.md with updated phase structure
        
        Template:
        ```markdown
        # CORTEX 6.0 Build - Continuation Prompt
        
        **Last Updated:** {timestamp}
        **Current Phase:** {current_phase}
        **Overall Progress:** {progress}%
        
        ## Next Steps
        
        Execute Phase {next_phase}: {next_phase_name}
        
        **Tasks:**
        1. {task_1}
        2. {task_2}
        ...
        
        **Command:**
        ```
        /CORTEX continue cortex6
        ```
        
        ## Phase Sequence (Snowball Ordered)
        
        | Phase | Name | Status | Effort |
        |-------|------|--------|--------|
        | 0 | Critical Blockers | 🔄 NEXT | 48h |
        | 1 | Foundation Layer | ⏳ Pending | 60h |
        | 2 | TODO Orchestrator | ⏳ Pending | 40h |
        ```
        """
        
        # Implementation here...
        pass
```

---

## 🔧 Phase 10B: Conflict Detection (NEW)

**Purpose:** Prevent regressions and contradictions before final sync

```python
def phase_10b_conflict_detection(
    self,
    new_gaps: List[Dict],
    existing_plan: Dict
) -> Dict:
    """
    Phase 10B: Conflict Detection & Validation
    
    Detects:
    1. CONTRADICTORY - New gap contradicts existing task
    2. DUPLICATE - Same criterion, different IDs
    3. REGRESSION_RISK - Gap fix would undo completed work
    4. TDD_MISSING - No test_file specified
    
    Returns:
        {
            "conflicts": [
                {
                    "type": "CONTRADICTORY",
                    "gap_id": "AC-NEW-001",
                    "task_id": "TASK-042",
                    "resolution_required": True
                }
            ],
            "blocking_conflicts": 2,
            "auto_resolved": 1
        }
    """
    
    conflicts = []
    
    for gap in new_gaps:
        # Check contradictions
        for task in existing_plan["phases"]:
            if self._is_contradictory(gap, task):
                conflicts.append({
                    "type": "CONTRADICTORY",
                    "gap_id": gap["id"],
                    "task_id": task["id"],
                    "resolution_required": True
                })
        
        # Check duplicates
        if self._is_duplicate(gap, existing_plan):
            conflicts.append({
                "type": "DUPLICATE",
                "gap_id": gap["id"],
                "existing_id": self._find_duplicate_id(gap, existing_plan),
                "action": "MERGE",
                "resolution_required": False  # Auto-merge
            })
        
        # Check regression risk
        for completed_phase in self._get_completed_phases(existing_plan):
            if self._affects_completed_work(gap, completed_phase):
                conflicts.append({
                    "type": "REGRESSION_RISK",
                    "gap_id": gap["id"],
                    "affected_phase": completed_phase["phase_name"],
                    "severity": "WARNING"
                })
        
        # Check TDD compliance
        if "test_file" not in gap:
            conflicts.append({
                "type": "TDD_MISSING",
                "gap_id": gap["id"],
                "resolution_required": True
            })
    
    return {
        "conflicts": conflicts,
        "blocking_conflicts": sum(1 for c in conflicts if c.get("resolution_required")),
        "auto_resolved": sum(1 for c in conflicts if c.get("action") == "MERGE")
    }
```

---

## 🧪 Phase 10C: Test Stability Validation (NEW)

**Purpose:** Ensure gap-fix changes don't destabilize existing tests

```python
def phase_10c_test_stability_validation(
    self,
    affected_modules: List[str],
    plan_path: Path
) -> Dict:
    """
    Phase 10C: Test Stability Validation
    
    Validates:
    1. All modified modules have test files
    2. No circular test dependencies
    3. Test isolation maintained
    4. AC-to-test traceability exists
    
    Returns:
        {
            "modules_analyzed": 15,
            "test_files_mapped": 15,
            "dependency_depth": 3,
            "tests_affected": 42,
            "new_tests_required": 8,
            "stability_risk": "LOW|MEDIUM|HIGH",
            "coverage_gap": 5  # percentage
        }
    """
    
    # Build test dependency graph
    test_graph = self._build_test_dependency_graph(affected_modules)
    
    # Analyze impact
    affected_tests = self._get_affected_tests(test_graph, affected_modules)
    
    # Check stability
    stability_risk = self._assess_stability_risk(test_graph, affected_tests)
    
    # Check coverage
    coverage_gap = self._calculate_coverage_gap(affected_modules)
    
    return {
        "modules_analyzed": len(affected_modules),
        "test_files_mapped": len(test_graph),
        "dependency_depth": test_graph.max_depth,
        "tests_affected": len(affected_tests),
        "new_tests_required": self._count_new_tests_needed(affected_modules),
        "stability_risk": stability_risk,
        "coverage_gap": coverage_gap
    }
```

---

## 📦 Migration: cortex6-planner Structure

### Current Structure (WRONG)

```
cortex6-planner/
├── 00-cortex6-complete-build.md              ❌ (00- prefix, .md, on root)
├── README.md                                  ❌ (not allowed on root)
├── CX6-comprehensive-remediation-plan.yaml   ❌ (belongs in acceptance-criteria/)
├── search-findings-20260109.yaml             ❌ (belongs in acceptance-criteria/)
├── PLAN-CREATION-SUMMARY.md                  ❌ (on root)
├── analysis/
├── artifacts/
├── context/
├── reports/
└── tracking/
    └── progress-tracker.json                 ✅ (correct)
```

### Target Structure (CORRECT per AC-ORC-PLAN-002)

```
cortex6-planner/
├── continuation-prompt.md                    ✅ ROOT FILE 1
├── thoughts.txt                              ✅ ROOT FILE 2
├── plan-viewer.html                          ✅ ROOT FILE 3 (generated on approval)
├── analysis/
│   └── README.md                            ✅ (moved from root)
├── artifacts/
│   ├── cortex6-build-plan.yaml             ✅ (converted from 00-*.md)
│   └── PLAN-CREATION-SUMMARY.md            ✅ (moved from root)
├── context/
├── reports/
└── tracking/
    └── progress-tracker.json                ✅ (already correct)
```

### Files Moved to acceptance-criteria/

```
acceptance-criteria/
├── CX6-acceptance-criteria.yaml             ✅ (already here)
├── CX6-requirements.yaml                    ✅ (remediation plan, canonical location)
├── search-findings-20260109.yaml            ✅ (moved from cortex6-planner/)
└── archive/
    └── remediation-plan-{date}.yaml         ✅ (archived old versions)
```

---

## ✅ Implementation Checklist

### Phase 1: Gap-Fix Orchestrator Core (8-12 hours)

- [ ] Create `src/orchestrators/gap_fix/`
- [ ] Implement `gap_fix_orchestrator.py` (Phases 0-11)
- [ ] Add Phase 10: `inject_findings_into_plan()`
- [ ] Add Phase 10: `_snowball_reorder()`
- [ ] Add Phase 10: `_update_progress_tracker()`
- [ ] Add Phase 10: `_generate_continuation_prompt()`

### Phase 2: Conflict Detection (4-6 hours)

- [ ] Implement Phase 10B: `detect_conflicts()`
- [ ] Add `_is_contradictory()` logic
- [ ] Add `_is_duplicate()` logic
- [ ] Add `_affects_completed_work()` logic
- [ ] Generate `conflict-report-{timestamp}.yaml`

### Phase 3: Test Stability (4-6 hours)

- [ ] Implement Phase 10C: `validate_test_stability()`
- [ ] Add `_build_test_dependency_graph()`
- [ ] Add `_assess_stability_risk()`
- [ ] Add `_calculate_coverage_gap()`

### Phase 4: Migrate cortex6-planner (2-4 hours)

- [ ] Create `continuation-prompt.md` on root
- [ ] Create `thoughts.txt` on root
- [ ] Move `00-cortex6-complete-build.md` → `artifacts/cortex6-build-plan.yaml` (convert to YAML)
- [ ] Move `README.md` → `analysis/README.md`
- [ ] Move `PLAN-CREATION-SUMMARY.md` → `artifacts/PLAN-CREATION-SUMMARY.md`
- [ ] Move `CX6-comprehensive-remediation-plan.yaml` → `acceptance-criteria/CX6-requirements.yaml`
- [ ] Move `search-findings-20260109.yaml` → `acceptance-criteria/`

### Phase 5: Testing (6-8 hours)

- [ ] Add `tests/orchestrators/test_gap_fix_orchestrator.py`
- [ ] Test Phase 10 integration
- [ ] Test Phase 10B conflict detection
- [ ] Test Phase 10C test stability
- [ ] Test snowball reordering algorithm
- [ ] Test progress tracker updates

### Phase 6: Documentation (2-4 hours)

- [ ] Update `cortex-gap-fix.prompt.md` with implementation notes
- [ ] Add AC-GAPFIX-001 to AC-GAPFIX-007 to `CX6-acceptance-criteria.yaml`
- [ ] Create migration guide for existing plans

---

## 🎯 Acceptance Criteria

### AC-GAPFIX-001: Phase 10 Plan Integration
- [ ] Gap findings injected as Phase 0 (blocking issues)
- [ ] Existing phases shifted by +1
- [ ] Progress tracker JSON updated
- [ ] Continuation prompt regenerated

### AC-GAPFIX-002: Snowball Reordering
- [ ] Phases reordered by snowball score
- [ ] Foundation work prioritized
- [ ] Blocking tasks at top
- [ ] Score formula: `(blocking × 10) + (unlocks × 5) + (coverage × 2)`

### AC-GAPFIX-003: Repeatable Execution
- [ ] Can run gap-fix multiple times during plan execution
- [ ] Detects existing Phase 0 (Gap-Fix) and updates instead of duplicating
- [ ] Archives previous gap-fix findings

### AC-GAPFIX-004: Conflict Detection (Phase 10B)
- [ ] Detects CONTRADICTORY conflicts
- [ ] Detects DUPLICATE criteria
- [ ] Detects REGRESSION_RISK
- [ ] Enforces TDD_ENFORCEMENT (test_file required)
- [ ] Blocks Phase 11 if conflicts found

### AC-GAPFIX-005: Test Stability Validation (Phase 10C)
- [ ] All modified modules have test coverage
- [ ] No circular test dependencies
- [ ] Test isolation verified
- [ ] AC-to-test traceability maintained

### AC-GAPFIX-006: Structure Compliance
- [ ] cortex6-planner/ follows AC-ORC-PLAN-002
- [ ] EXACTLY 3 root files (continuation-prompt.md, thoughts.txt, plan-viewer.html)
- [ ] NO 00- prefixes
- [ ] All plan artifacts in YAML/JSON format

### AC-GAPFIX-007: Audit Logging
- [ ] All Phase 10 operations logged to audit.db
- [ ] Conflict detection logged
- [ ] Snowball reordering logged
- [ ] Progress tracker updates logged

---

## 📊 Estimated Effort

| Phase | Description | Effort |
|-------|-------------|--------|
| 1 | Gap-Fix Orchestrator Core | 8-12h |
| 2 | Conflict Detection (10B) | 4-6h |
| 3 | Test Stability (10C) | 4-6h |
| 4 | Migrate cortex6-planner | 2-4h |
| 5 | Testing | 6-8h |
| 6 | Documentation | 2-4h |
| **TOTAL** | **26-40 hours (3-5 days)** | |

---

## 🚀 Next Steps

1. **Review this plan** - Validate approach with user
2. **Create AC entries** - Add AC-GAPFIX-001 to AC-GAPFIX-007
3. **Implement orchestrator** - Start with Phase 10 core logic
4. **Migrate cortex6-planner** - Fix structure violations
5. **Test end-to-end** - Run gap-fix → verify plan updated

---

## 📚 References

- **Prompt:** `.github/prompts/cortex-gap-fix.prompt.md` (v1.3.0)
- **AC Source:** `acceptance-criteria/CX6-acceptance-criteria.yaml` (v14.4.0)
- **Planning Structure:** AC-ORC-PLAN-002 (approved structure)
- **SKULL Rules:** PLAN_FILE_ORGANIZATION, TDD_ENFORCEMENT
- **Current Plan:** `cortex6-planner/` (needs migration)

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
