# Audit Trail Markers - Implementation Patterns

**Version:** 1.0  
**Authority:** CORE-027 (Audit Trail Discipline)  
**Last Updated:** 2026-02-09  
**Compliance Coverage:** 435+ AC markers in cortex/

---

## 🎯 Overview

CORTEX implements comprehensive audit trail tracking via **AC (Acceptance Criteria) markers** that create an immutable record of:
- When operations started
- What was executed
- Whether operations completed successfully

These markers appear in:
1. **Git commit messages** (primary)
2. **Python code comments** (supplementary)
3. **Governance database** (queryable)

---

## 📋 Marker Format

### Standard Pattern

```
AC-<DOMAIN>-<PHASE/COMPONENT>-<OPERATION-ID>
```

### Components

| Component | Format | Example | Purpose |
|-----------|--------|---------|---------|
| **Domain** | 2-4 chars | AUDIT, PHASE, FIX | Categorizes work area |
| **Phase/Component** | numeric or code | 2026-02-09, PHASE43, GENAI | Identifies scope |
| **Operation ID** | 1-3 digits | 001, 01, 1 | Unique sequence per AC |

### Example IDs

```
AC-AUDIT-2026-02-09-001          # Audit operation from 2026-02-09, sequence 001
AC-PHASE43-045                   # Phase 43, AC #045
AC-GENAI-003                     # GenAI component, operation 003
AC-FIX-2026-02-09-001-P0-1       # Fix with checkpoint reference
```

---

## 🔄 Lifecycle - Three-Part Marker

Each significant operation has three markers:

### 1. AC_START - Operation Begins

```python
# AC_START: AC-AUDIT-2026-02-09-001
# Description: Comprehensive codebase health scan
# Scope: Module imports, test environment, exception handling
```

**Location:** Start of operation, clearly visible  
**Purpose:** Signal intent and operation boundary

### 2. AC_EXECUTE - Intermediate Progress (Optional)

```python
# AC_EXECUTE: AC-PHASE43-045
# Step 1: Extract requirements from docs
# Step 2: Generate test cases
# Progress: 50% complete
```

**Location:** Significant milestones within operation  
**Purpose:** Track multi-step progress

### 3. AC_COMPLETE - Operation Finished

```python
# AC_COMPLETE: AC-AUDIT-2026-02-09-001 ✅
# Result: 7481 tests collected, 5 pre-existing errors identified
# Duration: 15 minutes
# Status: SUCCESS (P0: 3 items fixed, P1: ready for next phase)
```

**Location:** End of operation  
**Purpose:** Record final result and outcome

---

## 📍 Placement Locations

### In Python Code (Functions/Classes)

```python
def implement_feature():
    """
    AC_START: AC-PHASE43-045
    Description: Implement feature X with TDD
    """
    # Implementation code...
    
    # AC_COMPLETE: AC-PHASE43-045 ✅ (3 tests passing)
    return result
```

### In Git Commits

```bash
git commit -m "AC-AUDIT-2026-02-09-001-P0-1: Fix cortex.agents module import structure"
```

**Format:** `AC-<ID>[-SUBOP]: Brief description`

### In Configuration/YAML Files

```yaml
# cortex-registry/_cortex-master/audit-action-plan-2026-02-09.yaml
audit_id: "AUDIT-2026-02-09-001"
current_checkpoint: "P0-1-START"

p0_critical_findings:
  - id: "P0-1"
    title: "Module Import Structure Violation"
    checkpoint: "P0-1-COMPLETE"
    # AC markers tracked in commit history
```

---

## ✅ Implementation Checklist

For any significant work item:

- [ ] **AC_START marker** in code or commit message
- [ ] **Descriptive comment** with operation scope
- [ ] **AC_COMPLETE marker** when finished
- [ ] **Success indicator** (✅ for pass, 🔴 for fail)
- [ ] **Results summary** (tests passing, artifacts created)
- [ ] **Duration** or timeline reference

### Example - Complete Audit Trail

```python
# cortex/tools/audit_operation.py

def scan_codebase():
    """
    AC_START: AC-AUDIT-2026-02-09-001
    Description: Full P0-P3 codebase health scan
    Scope: Module imports, test environment, exception handling
    """
    results = {
        "p0_findings": [],
        "p1_findings": [],
        "p2_findings": []
    }
    
    # Execute scan...
    # AC_EXECUTE: AC-AUDIT-2026-02-09-001 (step 1/5 complete - imports checked)
    
    # AC_COMPLETE: AC-AUDIT-2026-02-09-001 ✅
    # Results: 3 P0 items, 5 P1 items, 18 P2 items identified
    # Status: SUCCESS
    # Next: Begin P0-1 remediation
    
    return results
```

---

## 🔍 Query Patterns

### Find All ACs for a Domain

```bash
grep -r "AC_START.*AUDIT" cortex/ --include="*.py"
```

### Track Specific Operation

```bash
git log --all --grep="AC-AUDIT-2026-02-09-001"
```

### Count AC Markers by Type

```bash
grep -r "AC_START\|AC_COMPLETE" cortex/ --include="*.py" | wc -l
```

---

## 📊 Coverage Statistics

| Metric | Value | Target |
|--------|-------|--------|
| **AC markers in cortex/** | 435 | ≥ 400 |
| **Commits with AC prefix** | 10/10 recent | 100% |
| **Files with AC markers** | ~85 | Growing |
| **Governance database entries** | Queryable | ✅ |

---

## 🚨 Common Mistakes to Avoid

### ❌ DON'T

```python
# Missing AC marker
def complex_operation():
    # Just code without audit trail
    return result

# AC marker without description
# AC_START: AC-PHASE43-045

# Incomplete AC marker
# AC_COMPLETE: Phase 43 done
```

### ✅ DO

```python
# Complete AC marker with context
# AC_START: AC-PHASE43-045
# Description: Implement dashboard sync with 3-source verification
# Expected duration: 45 minutes
def complex_operation():
    # Implementation code
    # AC_COMPLETE: AC-PHASE43-045 ✅ (45 min, 12/12 tests passing)
    return result
```

---

## 🔗 Integration Points

### TDD Orchestrator

```python
# cortex/orchestrators/core/tdd_orchestrator.py
# AC markers injected before/after implementation
```

### Governance Database

```python
# cortex/governance/audit_log_manager.py
# Queries: SELECT * FROM audit_log WHERE ac_id LIKE 'AC-AUDIT-%'
```

### Dashboard Sync

```python
# cortex-registry/_cortex-master/dashboard/
# Shows AC marker progress in dashboard HTML
```

---

## 📝 Recent Examples (P0 Audit Session)

```bash
# P0-1: Module Import Fix
AC-AUDIT-2026-02-09-001-P0-1: Fix cortex.agents module import structure

# P0-2: Test Dependencies
AC-AUDIT-2026-02-09-001-P0-2: Install missing test environment dependencies

# P0-3: Exception Handling
AC-AUDIT-2026-02-09-001-P0-3: Fix 7 bare except clauses (CORE-013 compliance)

# Checkpoint Update
AC-AUDIT-2026-02-09-001: Update checkpoint to P1-1-START after P0 completion
```

---

## 🎯 Guidelines for New Work

### For Implementation Tasks

```python
# AC_START: AC-PHASE<N>-<NUM>
# Description: [Clear statement of what will be done]
# Duration estimate: [X minutes/hours]

# ... implementation ...

# AC_COMPLETE: AC-PHASE<N>-<NUM> ✅
# Tests: [X/Y passing]
# Artifacts: [Files created/modified]
```

### For Bug Fixes

```bash
git commit -m "AC-FIX-2026-02-09-001: [Bug description] - CORE-[rule] violation"
```

### For Audit/Review Tasks

```python
# AC_START: AC-AUDIT-<DATE>-<ID>
# Scope: [What's being audited]
# Coverage: [% or scope]

# AC_COMPLETE: AC-AUDIT-<DATE>-<ID> ✅
# Findings: [Summary]
```

---

## 📞 Support

For audit trail questions:
- Reference: CORE-027 in `.github/copilot-instructions.md`
- Implementation: `cortex/governance/audit_log_manager.py`
- Governance: `cortex/orchestrators/core/enforcement_orchestrator.py`

---

**Status:** ✅ Documented | **Last Audit:** 2026-02-09 | **Next Review:** After P1-1 completion
