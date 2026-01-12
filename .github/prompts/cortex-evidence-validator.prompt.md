# Evidence-Based Status Validation Prompt (Plan-Integrated)

**Version:** 3.0.0  
**Author:** Asif Hussain  
**Date:** 2026-01-12  
**Purpose:** Fast, automated validation of AC-ID completion claims against test evidence with plan integration

---



## 🔗 MASTERORCHESTRATOR DELEGATION

**All implementation delegated to unified orchestrator:**

```bash
# Execute via MasterOrchestrator (central control)
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
```

**MasterOrchestrator handles:**
- ✅ Load governance rules (tier0/tier1/tier2/tier3)
- ✅ Validate against SKULL rules
- ✅ Create TodoManager tasks
- ✅ Execute tasks in dependency order
- ✅ Update progress-tracker.json (atomic writes)
- ✅ Enforce phase gates
- ✅ Return structured results

**Do NOT:**
- ❌ Directly modify progress-tracker.json
- ❌ Directly modify AC-INDEX.yaml
- ❌ Call sync_plan_viewer_data.py multiple times
- ❌ Manipulate state outside MasterOrchestrator

---
## 🛡️ REGRESSION PREVENTION PROTOCOL (UNIFIED)

**Before any operation, verify critical state files:**

```python
# 🛡️ UNIFIED REGRESSION CHECK
import json, yaml, sys

errors = []
try:
    ac_index = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
    if not ac_index.get('schema_version'): errors.append("AC-INDEX missing schema_version")
except Exception as e: errors.append(f"AC-INDEX parse error: {e}")

try:
    tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
    if not tracker.get('current_phase'): errors.append("tracker missing current_phase")
except Exception as e: errors.append(f"tracker parse error: {e}")

try:
    plan = yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
    if not plan.get('plan_metadata'): errors.append("master-plan missing plan_metadata")
except Exception as e: errors.append(f"master-plan parse error: {e}")

if errors:
    print("❌ REGRESSION DETECTED:\n" + "\n".join([f"  - {e}" for e in errors]))
    sys.exit(1)
print("✅ Regression check passed.")
```

## 🔗 PLAN INTEGRATION (CRITICAL)

**This validator ensures cx6-plan consistency:**

| Plan Asset | Validation Role |
|------------|-----------------|
| `master-plan.yaml` | Phase sequencing, AC-ID dependencies |
| `AC-INDEX.yaml` | AC-ID definitions (count must match tracker) |
| `progress-tracker.json` | Completion claims (must have test evidence) |
| `plan-viewer-data.json` | Dashboard data (must sync from tracker) |

**Validation Chain:**
```
AC-INDEX (defines) → progress-tracker (claims) → tests (proves) → plan-viewer (displays)
```

---


## 🎯 Core Principle

**SINGLE SOURCE OF TRUTH:** Test execution results (PASSED/FAILED) = AC completion evidence.

No speculation. No file checks. No proxy metrics. **Only test results count.**

---

## ⚡ ONE-COMMAND VALIDATION

```bash
# The entire validation workflow in one command
python3 scripts/audit_based_evidence_validator.py --fast --sync
```

**What happens:**
1. Run all tests: `pytest tests/ -v --tb=no -q`
2. Parse PASSED/FAILED by AC-ID marker
3. Update tracker.json with evidence only
5. Display verification summary

**Output:** One-line summary + verification rate
```
✅ Verified 77/102 AC-IDs (75.5%) | 1360 tests passing | Dashboard synced
```

---

## 🚀 Fast Validation Loop (For Phase Implementation)

**Before each feature commit:**

```bash
# 1. Run only tests for current phase
AC_PATTERN="AC-ORCH-*"  # Example: Pattern for Phase 2
python3 -m pytest tests/ -k "$AC_PATTERN" -v --tb=short

# 2. Quick validation for this phase
python3 scripts/audit_based_evidence_validator.py --phase current --sync

# 3. If ≥80% verified → commit allowed. If <80% → block commit
```

**Exit codes:**
- `0` = Verification rate ≥ 80% (proceed)
- `1` = Verification rate < 80% (block)
- `2` = Invalid phase (error)

---

## � Evidence Extraction (Efficient)


