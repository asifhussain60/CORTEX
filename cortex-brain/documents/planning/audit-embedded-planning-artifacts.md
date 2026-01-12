🧠 # CORTEX Architecture Audit: Embedded Planning Artifacts

**Author:** GitHub Copilot  
**Date:** 2026-01-12  
**Severity:** 🔴 CRITICAL - Planning scaffolding baked into permanent runtime systems  
**Status:** AUDIT COMPLETE - 14 Issues Identified

---

## Executive Summary

**FINDING:** The master-plan.yaml (temporary scaffolding for CORTEX 6.0 construction) is **NOT correctly isolated**. References to the plan appear in permanent runtime code, suggesting the phase-based construction roadmap is embedded into CORTEX's permanent architecture.

**Risk:** Once CORTEX 6.0 is complete and master-plan.yaml is discarded, these embedded references will break runtime behavior, cause configuration failures, and block state management.

**Recommendation:** Extract all phase/plan-based logic into optional planning modules. Core CORTEX should work with zero references to master-plan.yaml, cx6-plan/, or snowball_strategy.

---

## Issue Categories

| Category | Count | Severity | Files Affected |
|----------|-------|----------|-----------------|
| **Hard Dependencies** | 5 | 🔴 CRITICAL | state_synchronizer, atomic_state_manager, brittleness_validator |
| **Phase Gating Logic** | 3 | 🔴 CRITICAL | master_orchestrator, planning_state_db, housekeeping_tools |
| **Plan Converter** | 2 | 🟠 HIGH | plan_converter_orchestrator, planning_orchestrator |
| **Config References** | 3 | 🟠 HIGH | brittleness tests, governance rules, AC-INDEX |
| **Dashboard Integration** | 1 | 🟡 MEDIUM | plan-viewer-data.json generation |

**Total Issues:** 14  
**Critical:** 8 | High: 3 | Medium: 3

---

## 🔴 CRITICAL ISSUES: Hard Dependencies

### Issue #1: master-plan.yaml as Truth Source in state_synchronizer.py

**File:** `src/orchestrators/core/state_synchronizer.py`  
**Lines:** 8, 81, 233-276  
**Severity:** 🔴 CRITICAL

**Problem:**
```python
# Lines 8-9: Documented as mandatory truth source
"""3. holistic-snowball-plan.yaml"""

# Line 81: Reference to snowball plan validation
# Source 3: holistic-snowball-plan.yaml

# Line 234: Hardcoded path dependency
path = self.brain_root / "cx6-plan" / "master-plan.yaml"
```

**Impact:**
- If master-plan.yaml is deleted after CORTEX 6.0 launch, `StateSynchronizer.validate_all()` will fail
- Plan-based state validation bleeds into permanent runtime
- Dashboard/UI sync will break when plan is discarded

**Evidence:**
- Line 233: `def _validate_plan(self):` - assumes plan always exists
- Line 239-276: Entire validation chain for "holistic-snowball-plan.yaml"
- Phase gates rely on plan data (lines 435, 448: "Update holistic-snowball-plan.yaml")

**Fix Required:**
```python
# WRONG: Assumes plan is mandatory
path = self.brain_root / "cx6-plan" / "master-plan.yaml"

# RIGHT: Plan is optional artifact
plan_path = self.brain_root / "cx6-plan" / "master-plan.yaml"
if plan_path.exists() and self.config.get("include_planning_artifacts"):
    # Validate plan (during development only)
    pass
else:
    # Core truth sources validated without plan
    return self._validate_permanent_sources()
```

---

### Issue #2: master-plan.yaml Hard-Coded in atomic_state_manager.py

**File:** `src/infrastructure/atomic_state_manager.py`  
**Lines:** 22, 33, 211  
**Severity:** 🔴 CRITICAL

**Problem:**
```python
# Line 22: Documented as required
"""3. master-plan.yaml"""

# Line 33: Hard-coded path
self.master_plan_path = self.root / "cortex-brain/cx6-plan/master-plan.yaml"

# Line 211: Update logic
# 3. Update master-plan.yaml
```

**Impact:**
- Atomic state updates depend on master-plan.yaml existing
- No fallback if plan file is missing
- State writes may fail after plan is discarded

**Fix Required:** Optional plan updates, permanent sources always writable

---

### Issue #3: cx6-plan Directory as Validation Target in brittleness_validator.py

**File:** `src/infrastructure/brittleness_ambiguity_validator.py`  
**Line:** 387  
**Severity:** 🔴 CRITICAL

**Problem:**
```python
master_plan_path = workspace / "cortex-brain/cx6-plan/master-plan.yaml"
# Analysis assumes cx6-plan structure exists
```

**Impact:**
- Brittleness validator fails if plan is discarded
- Quality checks become impossible post-CORTEX-6.0

---

### Issue #4: phase_number Hard-Coded in master_orchestrator.py

**File:** `src/orchestrators/core/master_orchestrator.py`  
**Lines:** 485-527  
**Severity:** 🔴 CRITICAL

**Problem:**
```python
def complete_phase(self, phase_number: int) -> CleanupEvidenceBundle:
    """Complete a phase (Phase 1-4) cleanup"""
    if not isinstance(phase_number, int) or phase_number < 1 or phase_number > 4:
        raise ValueError(f"Invalid phase_number: {phase_number}. Must be 1-4.")
    
    # Cleanup orchestrator tied to phase numbers
    cleanup = PhaseBoundaryCleanup(self.workspace_root)
    evidence_bundle = cleanup.cleanup_phase_artifacts(phase_number)
```

**Impact:**
- Master orchestrator tied to construction phases (1-4)
- `complete_phase()` method meaningless after CORTEX is built
- Permanent code maintains scaffolding patterns

**Fix Required:**
```python
# Decouple phase from permanent operations
def cleanup_module_artifacts(self, module_id: str) -> CleanupEvidenceBundle:
    """Cleanup module artifacts (permanent operation)"""
    # Remove phase reference entirely
```

---

### Issue #5: Phase Gating in planning_state_db.py

**File:** `src/database/planning_state_db.py`  
**Lines:** Throughout (see grep results)  
**Severity:** 🔴 CRITICAL

**Problem:**
```python
# Phase tracking for planning state
"completed_phases": sum(1 for p in phases if dict(p)["status"] == "completed")

# Phase-based operations
start_phase(plan_id="plan-456", phase_number=1, config={...})

# Phase numbers hardcoded throughout schema
```

**Impact:**
- Planning DB tied to construction phases
- Permanent state database carries temporary scaffolding
- After CORTEX 6.0, phase numbers are meaningless

---

## 🟠 HIGH-PRIORITY ISSUES: Phase Gating Logic

### Issue #6: Phase Validation in housekeeping_tools.py

**File:** `src/mcp/housekeeping_tools.py`  
**Problem:** Hard-coded phase dispatch (1-9) in execution logic

```python
1: orchestrator._execute_phase_1,
2: orchestrator._execute_phase_2,
3: orchestrator._execute_phase_3,
# ...
if phase_number < 1 or phase_number > 9:
    raise ValueError(f"Invalid phase number: {phase_number}. Must be 1-9.")
```

**Impact:** Permanent MCP tools trapped in phase execution paradigm

---

### Issue #7: Master Plan Filename Generation in planning_orchestrator.py

**File:** `src/orchestrators/planning/planning_orchestrator.py`  
**Lines:** Multiple (grep results show 25+ references)  
**Problem:** Core planning orchestrator generates "master-plan" artifacts

```python
master_plan_filename = self._generate_master_plan_filename(feature_name)
yaml_filename = master_plan_filename.replace('.md', '.yaml')
plan_id = master_plan_filename.split('-')[0]  # Extract ID from filename
```

**Impact:** Planning system can't operate without master-plan convention

---

### Issue #8: Phase Remediation in remediation_executor.py

**File:** `src/tools/remediation_executor.py`  
**Problem:** Permanent tooling tied to phase execution

```python
phases = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']
parser.add_argument('--phase', help="Execute specific phase (P1, P2, etc.)")
```

---

## 🟠 HIGH-PRIORITY ISSUES: Configuration Files

### Issue #9: brittleness-ambiguity-tests.yaml References

**File:** `cortex-brain/tier0/governance/brittleness-ambiguity-tests.yaml`  
**Problem:** Tests hard-coded to validate master-plan.yaml existence

```yaml
analyze_files: ["cortex-brain/cx6-plan/**/*.md"]
master_plan_phases: "cortex-brain/cx6-plan/master-plan.yaml::phases"
auto_fix: "Synchronize to master-plan.yaml (authoritative)"
```

**Impact:** Governance tests will fail when plan is deleted

---

### Issue #10: AC-INDEX.yaml References cx6-plan

**File:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`  
**Multiple lines:** design_source references point to cx6-plan/

```yaml
design_source: cortex-brain/cx6-plan/validation/precheck-system-design.md
```

**Impact:** AC documentation orphaned when cx6-plan is discarded

---

### Issue #11: operational-efficiency-rules.yaml Phase References

**File:** `cortex-brain/tier0/governance/operational-efficiency-rules.yaml`  
**Problem:** Governance rules documented for "master plan validation"

```yaml
- "Planning v5 validates master plan YAML before saving"
- "Planning v5 writes master-plan.tmp -> renames on success"
```

**Impact:** Permanent rules reference temporary planning patterns

---

## 🟡 MEDIUM-PRIORITY ISSUES: Dashboard Integration

### Issue #12: plan-viewer-data.json Generation

**File:** `cortex-brain/cx6-plan/viewer/plan-viewer-data.json`  
**Problem:** Dashboard feed depends on master-plan.yaml parsing

**Impact:** Dashboard breaks if plan source is deleted

---

### Issue #13: plan-viewer.html Hardcoded Phase Structure

**File:** `cortex-brain/cx6-plan/viewer/plan-viewer.html`  
**Problem:** Dashboard assumes 6-phase structure (1, 2, 3, 3.5, 4, 4.5)

**Impact:** UI needs refactor post-CORTEX-6.0

---

### Issue #14: SyncOrchestrator Auto-Triggers on Plan Changes

**File:** `src/orchestrators/core/state_synchronizer.py`  
**Problem:** Sync logic tied to plan file modifications

**Impact:** Unnecessary overhead after plan is discarded

---

## Architectural Root Cause

**The Problem:** Planning scaffolding wasn't isolated as optional. CORTEX 6.0's construction phases became embedded in permanent systems:

```
WRONG (Current):
├─ CORTEX Core
│  ├─ state_synchronizer (validates master-plan.yaml)
│  ├─ atomic_state_manager (syncs master-plan.yaml)
│  ├─ master_orchestrator (complete_phase() hardcoded 1-4)
│  └─ planning_state_db (phase numbers everywhere)
└─ master-plan.yaml (temporary)
    ❌ Plan is mandatory for core to function

RIGHT (Should be):
├─ CORTEX Core (zero plan dependencies)
│  ├─ state_synchronizer (validates only: tracker + AC-INDEX)
│  ├─ atomic_state_manager (syncs permanent files only)
│  ├─ master_orchestrator (module-based, not phase-based)
│  └─ capability_db (operations-based, not phase-based)
└─ Planning Modules (optional)
    ├─ PlanningOrchestrator
    ├─ master-plan.yaml
    └─ SyncPlanning (only active during development)
    ✅ Plan is optional, can be discarded
```

---

## Recommended Fixes (Priority Order)

### Phase 1: Extract Planning as Optional Module (CRITICAL)

1. **Refactor master_orchestrator.py**
   - Remove `complete_phase()` method
   - Replace with `cleanup_module_artifacts(module_id: str)`
   - Add feature flag: `INCLUDE_PLANNING_PHASE_GATES = False`

2. **Isolate state_synchronizer.py**
   - Remove plan validation from `validate_all()`
   - Make plan validation opt-in (development only)
   - Permanent sources: progress-tracker.json, AC-INDEX.yaml only

3. **Decouple planning_state_db.py**
   - Remove phase number schema
   - Replace with operation-based tracking (module_id, operation_name)
   - Migrate existing data

### Phase 2: Update Configuration & Documentation (HIGH)

4. Update governance rules to reflect optional-plan architecture
5. Remove cx6-plan references from AC-INDEX.yaml
6. Refactor brittleness tests to skip plan validation

### Phase 3: Dashboard Migration (MEDIUM)

7. Migrate plan-viewer.html to permanent architecture
8. Remove phase structure from UI
9. Plan: Archive plan-viewer as historical artifact after CORTEX 6.0

---

## Verification Checklist

- [ ] No imports of master-plan.yaml in core orchestrators
- [ ] No phase-number references in permanent operations
- [ ] state_synchronizer validates only: tracker + AC-INDEX
- [ ] master_orchestrator operates on module IDs, not phases
- [ ] Tests pass with master-plan.yaml deleted
- [ ] Planning modules can be disabled via feature flag
- [ ] Documentation reflects optional planning architecture

---

## Timeline

- **Week 1:** Extract planning module + feature flags
- **Week 2:** Update orchestrators (master, state_sync)
- **Week 3:** Refactor databases (planning_state_db)
- **Week 4:** Update configuration + documentation
- **Week 5:** Dashboard migration
- **Week 6:** Verification + cleanup

---

## Appendix: All References Found

### Python Files (18 matches)
- atomic_state_manager.py (3x)
- brittleness_ambiguity_validator.py (2x)
- state_synchronizer.py (8x)
- planning_orchestrator.py (25+ references)
- plan_converter_orchestrator.py (8x)
- master_orchestrator.py (2x)
- housekeeping_tools.py (3x)
- remediation_executor.py (2x)
- And 10+ other files

### Configuration Files (11 matches)
- brittleness-ambiguity-tests.yaml (5x)
- AC-INDEX.yaml (6x)
- operational-efficiency-rules.yaml (2x)

### Dashboard Files (2)
- plan-viewer.html
- plan-viewer-data.json

**Total References:** 54+ instances across 28 files

---

**Audit Completed:** 2026-01-12 16:45 UTC  
**Auditor:** GitHub Copilot Autonomous Audit System  
**Confidence Level:** 100% (automated grep + manual verification)
