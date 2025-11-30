# Next Steps Formatting Violations Report

**Total Violations:** 2

## Violation Summary

### MISSING_READY_PROMPT (1 violations)

**.github\prompts\modules\template-guide.md:354**
- **Detected Pattern:** complex_projects
- **Expected Pattern:** complex_projects
- **Fix:** Add after checkboxes: 'Ready to proceed with all phases, or focus on a specific phase?'

### NUMBERED_LIST_IN_COMPLEX_WORK (1 violations)

**.github\prompts\modules\template-guide.md:457**
- **Detected Pattern:** violation
- **Expected Pattern:** complex_projects
- **Fix:** Replace numbered list with checkboxes grouped into phases. Add 'Ready to proceed with all phases, or focus on a specific phase?' prompt.


## Pattern Reference

### ✅ Pattern 1: Simple Tasks
```markdown
🔍 Next Steps:
   1. First action
   2. Second action
   3. Third action
```

### ✅ Pattern 2: Complex Projects
```markdown
🔍 Next Steps:
   ☐ Phase 1: Discovery (Tasks 1-3)
   ☐ Phase 2: Implementation (Tasks 4-7)
   
   Ready to proceed with all phases, or focus on a specific phase?
```

### ✅ Pattern 3: Parallel Work
```markdown
🔍 Next Steps:
   Track A: Fix Python config (30 min)
   Track B: Update documentation (45 min)
   
   These tracks are independent and can run in parallel.
   Which track(s) shall I start with? (You can choose multiple or ALL)
```

---

**Reference:** `.github/prompts/modules/response-format.md`