# 🔬 Sub-Plan 04: AST Scanning Integration in Planning

**Plan ID:** ast-scanning-planning  
**Parent:** CORTEX-5.0  
**Duration:** 3-4 days  
**Status:** ⏸️ BLOCKED

---

## 📊 Progress

**Overall:** `░░░░░░░░░░` **0%** ⏸️ BLOCKED

## 🎯 Objective

Integrate AST scanning in Planning v5 Phase 0 (Discovery) for architectural analysis.

**Gap:** Section 2.4 (0% implemented)

**Success Criteria:**
- ✅ AST scan runs in Phase 0
- ✅ Function/class/import counts extracted
- ✅ Duplicate code detected
- ✅ Orphaned code detected
- ✅ Results saved to `context/ast-analysis.json`
- ✅ All 5 AST tests passing

---

## 🏗️ Implementation

### Tasks
1. Integrate Python AST library
2. Scan codebase in Phase 0
3. Detect duplicates
4. Find orphaned functions
5. Generate ast-analysis.json
6. Write 5 AST tests

### Files
- `src/orchestrators/planning/ast_scanner.py`
- `src/orchestrators/planning/duplicate_detector.py`
- `src/orchestrators/planning/orphan_detector.py`
- `tests/orchestrators/planning/test_ast_scanning.py`

---

## ✅ Definition of Done

- [ ] AST scanning integrated
- [ ] Duplicates detected
- [ ] Orphans found
- [ ] Results in context/ast-analysis.json
- [ ] All 5 tests pass

---

**Status:** ⏸️ BLOCKED (Planning tests needed)  
**Blocks:** Sub-Plan 05

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
