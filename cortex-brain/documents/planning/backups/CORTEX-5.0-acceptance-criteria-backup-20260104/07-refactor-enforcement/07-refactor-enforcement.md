# 🔄 Sub-Plan 07: REFACTOR Task Enforcement

**Plan ID:** refactor-enforcement  
**Parent:** CORTEX-5.0  
**Duration:** 2 days  
**Status:** ⏸️ BLOCKED

---

## 📊 Progress

**Overall:** `░░░░░░░░░░` **0%** ⏸️ BLOCKED

## 🎯 Objective

Enforce 18+ cleanup tasks in REFACTOR phase of all generated plans.

**Gap:** Section 2.2 (no enforcement)

**Success Criteria:**
- ✅ All plans have ≥18 REFACTOR tasks
- ✅ Task generation automated
- ✅ Whole-file cleanup validated
- ✅ Orphan/duplicate removal tracked

---

## 🏗️ Implementation

### Tasks
1. Create REFACTOR task generator
2. Add task count validation
3. Implement cleanup verification
4. Write tests

### Files
- `src/orchestrators/planning/refactor_task_generator.py`
- `cortex-brain/templates/planning/refactor-checklist.jinja2`

---

## ✅ Definition of Done

- [ ] ≥18 tasks in all plans
- [ ] Task generation automated
- [ ] Validation works

---

**Status:** ⏸️ BLOCKED (Sub-Plan 05 needed)  
**Blocks:** Sub-Plan 08

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
