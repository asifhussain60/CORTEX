# ✅ Evidence-Based Status Validation Prompt


**Purpose:** Fast, automated validation of AC-ID completion claims against test evidence  
**Version:** 3.0.0  
**Date:** 2026-01-12  
**Governance:** CORE-002 (no root files), CORE-017 (governance enforcement), CORE-009 (plan organization), CORE-025 (intelligent challenge)  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

**Purpose:** Fast, automated validation of AC-ID completion claims against test evidence  
**Version:** 3.0.0  
**Date:** 2026-01-12  
**Governance:** CORE-002 (no root files), CORE-017 (governance enforcement), CORE-009 (plan organization), CORE-025 (intelligent challenge)  
**Author:** Asif Hussain

---

## 🔗 MASTERORCHESTRATOR DELEGATION

**All validation delegated to unified orchestrator:**

```bash
# Execute via MasterOrchestrator (central control)
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
```

**MasterOrchestrator handles:**
- ✅ Load governance rules (tier0/tier1/tier2/tier3)
- ✅ Validate against SKULL rules
- ✅ Collect test evidence for AC-IDs
- ✅ Execute tasks in dependency order
- ✅ Update progress-tracker.json (atomic writes)
- ✅ Enforce evidence requirements
- ✅ Return structured results

**Do NOT:**
- ❌ Directly modify progress-tracker.json
- ❌ Directly modify AC-INDEX.yaml
- ❌ Accept claims without test evidence
- ❌ Manipulate state outside MasterOrchestrator

---

## 🛡️ REGRESSION PREVENTION (Reference Only)

**Reference:** CORTEX.prompt.md maintains unified regression check via MasterOrchestrator.

**This prompt DOES NOT perform direct file access.** All evidence validation delegated to Python orchestrator:
- ✅ Test result collection and aggregation
- ✅ Evidence bundle validation
- ✅ Atomic state updates

**Why not embed code?** When MasterOrchestrator is updated, validation automatically improves for all prompts (DRY principle).

---

## 🛡️ INTELLIGENT CHALLENGE PROTOCOL (CORE-025)

**Purpose:** Validate evidence requirements against governance and quality standards.

**Implementation:** Delegated to MasterOrchestrator → RequestValidator.

**Reference:** `.github/prompts/CORTEX-ALIGN.prompt.md § INTELLIGENT CHALLENGE PROTOCOL`

---

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


