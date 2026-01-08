# feat03 & feat04 Implementation Plan

**Date:** 2026-01-08  
**Priority:** CRITICAL - Blocks Epic Completion  
**Estimated Time:** 4-6 hours  

---

## 🎯 Implementation Strategy

**Approach:** Minimal Viable Implementation (MVI)  
Focus on fixing the integration test failures and enabling orchestrator registration.

### Phase 1: feat03-governance (MVI - 2 hours)

**Goal:** Create GovernanceMerger class for integration tests

**Deliverables:**
1. `src/orchestrators/core/governance_merger.py` - Basic GovernanceMerger class
2. `tests/unit/test_governance_merger.py` - 10 basic tests
3. Update integration tests to use GovernanceMerger

**Skip for Now (defer to 6.1):**
- Full 4-category system
- SKULL rule migration
- Unified Instruction Set complexity

### Phase 2: feat04-core-orchestration (MVI - 2 hours)

**Goal:** Add orchestrator registration system to MasterOrchestrator

**Deliverables:**
1. Add `register_orchestrator()` to MasterOrchestrator
2. Add `workspace_root` parameter to TodoOrchestrator
3. Fix 8 failing integration tests
4. Verify all 805 tests pass

---

## ✅ Execution Checklist

- [ ] Create minimal GovernanceMerger class
- [ ] Add TodoOrchestrator workspace_root support
- [ ] Fix integration test signatures
- [ ] Run full test suite
- [ ] Update TODO tracker
- [ ] Commit and push

---

**Estimated Completion:** 09:45 (current 09:35)
