# CORTEX File Organization Quick Reference

**Last Updated:** 2026-01-18  
**Status:** ✅ CLEAN - All docs_md folders removed  
**Phases:** 25 consolidated in authoritative location

---

## 🎯 The Golden Rule

**All documentation → `docs/` folder ONLY**  
**All phase specs → `_workspaces/roadmap/phases/` ONLY**  

---

## ✅ Correct Locations

### Markdown Documentation
```
✅ docs/
   ├── AC-FIX-001-02-*.md
   ├── CORTEX-*.md
   ├── cortex-*.md
   └── (all .md files here)
```

### Phase Specifications  
```
✅ _workspaces/roadmap/phases/
   ├── phase-01.yaml
   ├── phase-02.yaml
   ├── ...
   ├── phase-06-ecosystem.yaml
   ├── phase-07-intent-router.yaml
   └── (25 total phases)
```

### Status & Reports
```
✅ _workspaces/roadmap/reports/
   └── *.yaml (status tracking files)

✅ _workspaces/roadmap/issues/
   └── Findings-*.yaml (investigation reports)
```

### Implementation Code
```
✅ src/
   └── (Python source files)

✅ tests/
   └── (Test files)
```

---

## ❌ FORBIDDEN Locations

```
❌ docs_md/                (NEVER create this)
❌ docs/docs_md/           (NEVER create this)
❌ root directory          (for .md files)
❌ .github/                (for documentation)
❌ _workspaces/            (except phases/, reports/, issues/, tools/)
```

---

## Pre-Commit Checklist

**Before any git commit, verify:**

```bash
# 1. NO docs_md folders exist
find . -type d -name "docs_md" 2>/dev/null
# Expected: (empty - nothing found)

# 2. ALL .md files in docs/
find . -name "*.md" -not -path "./docs/*" -not -path "./.git/*" 2>/dev/null
# Expected: (empty - nothing found)

# 3. ALL phase YAMLs in _workspaces/roadmap/phases/
ls _workspaces/roadmap/phases/phase-*.yaml | wc -l
# Expected: 25 (or more)

# 4. Root is clean
ls -la | grep -E "\.md$|docs_md"
# Expected: (empty - nothing found)
```

---

## If docs_md/ Appears

**Immediately:**
1. Stop work
2. Delete the folder: `rm -rf docs_md/`
3. Move any files inside to correct location (`docs/`)
4. Find what created it
5. Fix that code/prompt/agent
6. Verify folder is gone
7. Continue work

---

## Supported Commands

**All 11 files (4 prompts + 7 agents) have been updated with:**
- ❌ FORBIDDEN marker for `docs_md/`
- ✅ Correct file locations documented
- ✅ Pre-commit verification guidance
- ✅ "Fix immediately if found" action guidance

### Files with Prevention Enabled:

**Prompts (4):**
- `docs/CORTEX.prompt.md`
- `docs/cortex-builder.prompt.md`
- `docs/cortex-review.prompt.md`
- `docs/cortex-git-commit.prompt.md`

**Agents (7):**
- `.github/agents/cortex-builder.md`
- `.github/agents/cortex-review-brittleness.md`
- `.github/agents/cortex-review-hallucination.md`
- `.github/agents/cortex-review-governance.md`
- `.github/agents/cortex-review-assumptions.md`
- `.github/agents/cortex-review-debt.md`
- `.github/agents/cortex-gap-detection.md`
- `.github/agents/cortex-planner.md`

---

## Documentation References

**For full details, see:**
- `docs/CORTEX-DOCS_MD-CLEANUP-20260118.md` - Executive summary
- `docs/CORTEX-DOCS_MD-VERIFICATION-REPORT.md` - Verification & completion status
- `_workspaces/roadmap/_archives/docs_md_cleanup_20260118/` - Archived historical files

---

## Quick Summary

| Item | Before | After |
|------|--------|-------|
| docs_md folders | 2 found | ✅ 0 (deleted) |
| Duplicate phase YAMLs | In 3 locations | ✅ 1 location only |
| Total phase specs | 17, 17, 25 | ✅ 25 (consolidated) |
| Prevention measures | 0 files | ✅ 11 files updated |
| Archive preservation | Not done | ✅ 15MB archived safely |
| Documentation | Missing | ✅ 2 detailed reports created |

---

## Questions?

Refer to:
1. `docs/CORTEX-DOCS_MD-CLEANUP-20260118.md` - Full cleanup report
2. `docs/CORTEX-DOCS_MD-VERIFICATION-REPORT.md` - Verification details
3. Check any of 11 updated prompts/agents for current rules

---

**STATUS: ✅ PRODUCTION READY**

No docs_md folders. All phases consolidated. Prevention in place. Safe to continue development.
