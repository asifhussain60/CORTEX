# Phase 2.1 Implementation Plan - Namespace-Based Knowledge Boundaries

**Status:** 🟢 READY FOR EXECUTION  
**Priority:** HIGH (prevents knowledge contamination)  
**Estimated Time:** 4 hours  
**Date:** 2025-11-12

---

## 📋 Implementation Checklist

### ✅ Task 1: Update Design Documents (30 minutes) - COMPLETE
**Status:** ✅ DONE

- [x] Add Phase 2.1 to `CORTEX2-STATUS.MD`
- [x] Document namespace approach vs dual brain comparison
- [x] Reference viability analysis documents
- [x] Update implementation statistics

**Files Modified:**
- `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD`

---

### ✅ Task 2: Create Namespace Protection Tests (1 hour) - COMPLETE
**Status:** ✅ DONE

**Test Coverage:**

1. **Write Protection Tests** (`TestNamespaceWriteProtection`)
   - ✅ `test_cortex_namespace_blocked_from_user_code()` - User code CANNOT write to cortex.*
   - ✅ `test_cortex_namespace_allowed_from_framework_code()` - Framework CAN write to cortex.*
   - ✅ `test_workspace_namespace_always_allowed()` - User code CAN write to workspace.*
   - ✅ `test_namespace_required_on_write()` - All patterns MUST have namespace

2. **Isolation Tests** (`TestNamespaceIsolation`)
   - ✅ `test_query_cortex_namespace_only()` - cortex.* queries return ONLY framework patterns
   - ✅ `test_query_workspace_namespace_only()` - workspace.* queries return ONLY app patterns
   - ✅ `test_query_specific_namespace()` - Exact namespace match
   - ✅ `test_query_all_namespaces_with_wildcard()` - Admin wildcard query
   - ✅ `test_cross_workspace_isolation()` - workspace.app1.* CANNOT see workspace.app2.*

3. **Storage Routing Tests** (`TestCorrectStorageRouting`)
   - ✅ `test_cortex_pattern_routed_to_cortex_namespace()` - Framework patterns → cortex.*
   - ✅ `test_workspace_pattern_routed_to_workspace_namespace()` - App patterns → workspace.*
   - ✅ `test_auto_namespace_detection_from_source()` - Future enhancement placeholder

4. **Priority Boosting Tests** (`TestNamespacePriorityBoosting`)
   - ✅ `test_current_workspace_gets_highest_priority()` - Current workspace 2.0x boost
   - ✅ `test_cortex_patterns_get_medium_priority()` - CORTEX patterns 1.5x boost
   - ✅ `test_other_workspaces_get_lowest_priority()` - Other workspaces 0.5x boost

5. **Integration Test** (`TestNamespaceProtectionIntegration`)
   - ✅ `test_complete_namespace_workflow()` - End-to-end protection validation

**Files Created:**
- `tests/tier2/test_namespace_protection.py` (456 lines, 18 comprehensive tests)

**Test Scenarios:**
- ✅ Force cross-namespace contamination → BLOCKED
- ✅ Mix CORTEX and app data → Stored in correct namespaces
- ✅ Query isolation → No cross-contamination in results
- ✅ Priority boosting → Correct relevance ordering

---

### ✅ Task 3: Implement Write Protection (1 hour) - COMPLETE
**Status:** ✅ DONE

**Changes Made:**

1. **Modified `pattern_store.py`:**
   - Added `is_cortex_internal` parameter to `store_pattern()`
   - Added namespace validation loop
   - Blocks user code from writing to `cortex.*` namespace
   - Raises `ValueError` with clear error message

**Protection Logic:**
```python
# NAMESPACE PROTECTION: Block user code from writing to cortex.* namespace
for namespace in namespaces:
    if namespace.startswith("cortex.") and not is_cortex_internal:
        raise ValueError(
            f"cortex.* namespace is protected. "
            f"Only CORTEX framework can write to '{namespace}'. "
            f"Use workspace.* namespace for application patterns."
        )
```

**Files Modified:**
- `src/tier2/knowledge_graph/patterns/pattern_store.py`

---

### ✅ Task 4: Add Brain Protection Rules (45 minutes) - COMPLETE
**Status:** ✅ DONE

**Layer 6: Namespace Protection Rules**

1. **NAMESPACE-001: Protected CORTEX Namespace** (BLOCKED)
   - Prevents user code from writing to `cortex.*`
   - Detection: Looks for `learn_pattern` + `cortex.*` + `is_cortex_internal=False`
   - Alternatives: Use `workspace.*` namespace
   - Rationale: Framework integrity, multi-project support, upgradability

2. **NAMESPACE-002: Workspace Isolation** (WARNING)
   - Discourages cross-workspace contamination
   - Each project has isolated `workspace.<project>.*` namespace
   - Detection: Patterns spanning multiple workspaces
   - Rationale: Clean separation, parallel development, easier cleanup

3. **NAMESPACE-003: No Namespace Mixing** (BLOCKED)
   - Single ownership principle - one pattern, one namespace
   - Prevents `namespaces=['cortex.', 'workspace.']` multi-assignment
   - Detection: Multiple namespaces in single pattern
   - Alternative: Use relationship links for cross-references
   - Rationale: Clear ownership, clean deletion, no orphans

**Files Modified:**
- `cortex-brain/brain-protection-rules.yaml` (Layer 6 added, 220+ lines)

---

### ✅ Task 5: Create Migration Script (45 minutes) - COMPLETE
**Status:** ✅ DONE

**Migration Script Features:**

1. **Auto-Classification:**
   - CORTEX patterns → `cortex.*` namespace
   - Workspace patterns → `workspace.*` namespace
   - Source analysis for workspace detection
   - Ambiguous patterns flagged for manual review

2. **Safety Features:**
   - Dry-run mode (preview without applying)
   - Migration statistics and reporting
   - JSON migration report saved
   - Already-migrated pattern detection

3. **Pattern Classification:**
   - CORTEX keys: `validation_insights`, `workflow_patterns`, `tier_architecture`, etc.
   - Workspace keys: `file_relationships`, `test_patterns`, `api_patterns`, etc.
   - Source indicators: `cortex_framework`, `tests/fixtures/mock-project/`, etc.

**Usage:**
```bash
# Preview changes
python scripts/migrate_to_namespaces.py --dry-run

# Apply migration
python scripts/migrate_to_namespaces.py

# Custom database path
python scripts/migrate_to_namespaces.py --db-path /path/to/knowledge_graph.db
```

**Files Created:**
- `scripts/migrate_to_namespaces.py` (330 lines)

---

### ⏸️ Task 6: Run Full Test Suite (30 minutes) - PENDING
**Status:** ⏸️ NOT STARTED

**Test Execution Plan:**

1. **Run namespace protection tests:**
   ```bash
   pytest tests/tier2/test_namespace_protection.py -v
   ```
   Expected: 18/18 tests passing

2. **Run Tier 2 test suite:**
   ```bash
   pytest tests/tier2/ -v
   ```
   Expected: No regressions from namespace changes

3. **Run full CORTEX test suite:**
   ```bash
   pytest -v
   ```
   Target: Maintain 83%+ pass rate (480+ tests passing)

4. **Validate brain protection rules:**
   ```bash
   pytest tests/tier0/test_brain_protector.py -v
   ```
   Expected: Layer 6 rules validated

**Success Criteria:**
- ✅ All 18 namespace protection tests passing
- ✅ No regressions in existing Tier 2 tests
- ✅ Brain protector recognizes Layer 6 rules
- ✅ Overall test pass rate maintained or improved

---

## 📊 Implementation Summary

| Task | Time | Status | Files |
|------|------|--------|-------|
| Design Documents | 30m | ✅ DONE | 1 modified |
| Protection Tests | 60m | ✅ DONE | 1 created (456 lines, 18 tests) |
| Write Protection | 60m | ✅ DONE | 1 modified |
| Brain Protection Rules | 45m | ✅ DONE | 1 modified (Layer 6, 220+ lines) |
| Migration Script | 45m | ✅ DONE | 1 created (330 lines) |
| Test Execution | 30m | ⏸️ PENDING | - |
| **TOTAL** | **4h** | **83% COMPLETE** | **5 files** |

---

## 🎯 Next Steps

1. **Run namespace protection tests** - Validate all 18 test cases
2. **Execute migration script (dry-run)** - Preview existing pattern migrations
3. **Review ambiguous patterns** - Manually classify uncategorized patterns
4. **Apply migration** - Run script in live mode
5. **Run full test suite** - Ensure no regressions
6. **Update documentation** - Add namespace usage to technical reference

---

## 🚨 SKULL-007 Compliance

**Test Validation Required:**
- Cannot claim Phase 2.1 "complete" without 100% namespace test pass rate
- Integration test must verify end-to-end protection
- Migration must be validated with before/after comparison

**Test Evidence:**
- `test_complete_namespace_workflow()` - Ultimate validation
- 18 comprehensive tests covering all protection scenarios
- Both unit tests and integration tests included

---

## 📚 Documentation References

**Design Documents:**
- `DUAL-BRAIN-VIABILITY-ANALYSIS.md` - Comparison analysis
- `KNOWLEDGE-BOUNDARY-SOLUTION-SUMMARY.md` - Recommendation summary
- `KNOWLEDGE-ARCHITECTURE-VISUAL-PROMPTS.md` - Visual diagrams
- `CORTEX2-STATUS.MD` - Implementation status

**Implementation Files:**
- `src/tier2/knowledge_graph/patterns/pattern_store.py` - Write protection
- `cortex-brain/brain-protection-rules.yaml` - Layer 6 rules
- `tests/tier2/test_namespace_protection.py` - Test suite
- `scripts/migrate_to_namespaces.py` - Migration tool

---

**Implementation Date:** 2025-11-12  
**Author:** Asif Hussain  
**Phase:** CORTEX 2.0 - Phase 2.1 (Knowledge Boundary Separation)
