# CORTEX File Organization - Complete Reference

**Status:** ✅ COMPLETE (2026-01-18)  
**Enforcement:** ✅ ACTIVE (All prompts & master plan updated)

---

## Quick Reference

### Where Files Go

| File Type | Location | Example |
|-----------|----------|---------|
| **Markdown Documentation** | `docs/` | `docs/AC-FIX-001.md` |
| **MCP Toolkit Scripts** | `src/mcp/tools/` | `src/mcp/tools/consolidate.py` |
| **Utility Scripts** | `src/mcp/utilities/` | `src/mcp/utilities/helper.py` |
| **Build/Setup Scripts** | `scripts/` | `scripts/setup.py` |
| **Phase Specifications** | `_workspaces/roadmap/phases/` | `phase-01.yaml` |
| **Phase Reports** | `_workspaces/roadmap/reports/` | `phase-status.yaml` |
| **Issue Findings** | `_workspaces/roadmap/issues/` | `findings.yaml` |
| **Source Code** | `src/` | `src/orchestrator.py` |
| **Tests** | `tests/` | `tests/unit/test_x.py` |
| **Tier Modules** | `cortex-brain/tierX/` | `cortex-brain/tier1/agents.py` |

### What's Forbidden ❌

- `.md` files outside `docs/`
- `.py` files in root (except whitelisted)
- `.py` files in `_workspaces/roadmap/`
- `.py` files in `.github/`
- `docs_md/` folder (NEVER create)
- Files scattered across multiple locations

### What's Required ✅

- ALL `.md` files go to `docs/` only
- ALL `.py` scripts go to `src/mcp/tools/` (or appropriate folder)
- ALL YAML files go to authoritative location
- Pre-commit checks before pushing
- Phase lock verification before marking complete

---

## Recent Changes (2026-01-18)

### Files Moved
✅ 3 markdown files from `_workspaces/roadmap/` → `docs/`
✅ 2 Python scripts from `.github/prompts/tools/` → `src/mcp/tools/`

### Prompts Updated
✅ cortex-builder.prompt.md - File locations corrected
✅ CORTEX.prompt.md - Toolkit guidance updated
✅ cortex-git-commit.prompt.md - Pre-commit rules updated
✅ cortex-review.prompt.md - File placement clarified

### Master Plan Updated
✅ MCP Toolkit section added to cortex-master.yaml
✅ Documentation Guidelines section added
✅ Enforcement rules documented

---

## Documentation By Topic

### File Organization
- **FILE-ORGANIZATION-QUICK-REFERENCE.md** - Quick rules & locations
- **FILE-ORGANIZATION-REFACTORING-REPORT.md** - Detailed changes made
- **FILE-ORGANIZATION-REFACTORING-VERIFICATION.md** - Verification results

### Cleanup History
- **CORTEX-DOCS_MD-CLEANUP-20260118.md** - Cleanup actions & findings
- **CORTEX-DOCS_MD-VERIFICATION-REPORT.md** - Cleanup verification details
- **CLEANUP-EXECUTIVE-SUMMARY.md** - Executive summary of cleanup

### Architecture
- **ROADMAP-README.md** - Roadmap structure overview
- **PHASE-0-5-TO-PHASE-1-TRANSITION-STATUS.md** - Transition details

---

## Enforcement Rules

### In Prompts (All 4 Updated)
```yaml
cortex-builder.prompt.md:
  - File placement table includes correct locations
  - Initialization checklist verifies clean state
  - Step 1 loads from docs/ (not _workspaces/roadmap/)

CORTEX.prompt.md:
  - File placement rules updated
  - Toolkit location: src/mcp/tools/
  - Cleanup rules: NO .py in root

cortex-git-commit.prompt.md:
  - Pre-commit cleanup rules
  - File placement table updated
  - Documentation references updated

cortex-review.prompt.md:
  - File placement rules clarified
  - Toolkit location: src/mcp/tools/
  - Creation rules enforced
```

### In cortex-master.yaml
```yaml
mcp_toolkit:
  status: "ACTIVE"
  rule: "Python scripts MUST go to src/mcp/tools/ (not elsewhere)"
  forbidden_locations:
    - Root directory
    - _workspaces/roadmap/
    - _workspaces/
    - .github/
  enforcement: "Scripts in forbidden locations MUST be moved before phase lock"

documentation_guidelines:
  status: "ACTIVE"
  rule: ".md files MUST go to docs/ folder ONLY"
  exceptions: "Phase reports (YAML) go to _workspaces/roadmap/reports/"
  enforcement: "Pre-commit check enforces this"
```

---

## Pre-Commit Verification

**Run before every git commit:**

```bash
# 1. Check for stray .md files outside docs/
find . -path ./docs -prune -o -name "*.md" -type f -print
# Should return: (empty)

# 2. Check for .md files in _workspaces/roadmap/
find _workspaces/roadmap -maxdepth 1 -name "*.md" -type f
# Should return: (empty)

# 3. Check for stray .py files in root (non-whitelisted)
find . -maxdepth 1 -name "*.py" -type f ! -name "launch-dashboard.py" ! -name "verify_orchestrator*"
# Should return: (empty)

# 4. Check for .py files in forbidden locations
find _workspaces -name "*.py" -type f
find .github -name "*.py" -type f
# Should return: (empty)

# 5. Verify scripts in correct location
ls src/mcp/tools/{consolidate,validate_consolidation}.py
# Should list both files
```

---

## Current File Organization

### Root Directory (CLEAN)
```
✅ CORTEX/
   ├── cortex-brain/
   ├── docs/ (all .md files here)
   ├── scripts/ (build scripts)
   ├── src/ (source code)
   ├── tests/ (test suite)
   ├── _workspaces/ (roadmap only - YAML)
   ├── .github/ (prompts, agents)
   ├── launch-dashboard.py (whitelisted)
   ├── verify_orchestrator_readiness.sh (whitelisted)
   ├── pytest.ini
   ├── requirements.txt
   └── README.md (root level OK)
```

### _workspaces/roadmap (YAML ONLY)
```
✅ _workspaces/roadmap/
   ├── cortex-master.yaml (SSOT)
   ├── phases/ (25 YAML files)
   ├── reports/ (YAML status files)
   ├── issues/ (YAML findings)
   ├── _archives/ (historical files)
   └── _archives/docs_md_cleanup_20260118/
```

### docs/ (All Markdown Here)
```
✅ docs/
   ├── ROADMAP-README.md
   ├── PHASE-0-5-TO-PHASE-1-TRANSITION-STATUS.md
   ├── CORTEX-REVIEW-INDEX-20260118.md
   ├── FILE-ORGANIZATION-QUICK-REFERENCE.md
   ├── FILE-ORGANIZATION-REFACTORING-REPORT.md
   ├── FILE-ORGANIZATION-REFACTORING-VERIFICATION.md
   ├── CORTEX-DOCS_MD-CLEANUP-20260118.md
   ├── CORTEX-DOCS_MD-VERIFICATION-REPORT.md
   ├── CLEANUP-EXECUTIVE-SUMMARY.md
   ├── (and all other .md documentation)
   └── FILE-ORGANIZATION-REFERENCE.md (this file)
```

### src/mcp/tools/ (Toolkit Scripts)
```
✅ src/mcp/tools/
   ├── consolidate.py (moved from .github/prompts/tools/)
   ├── validate_consolidation.py (moved from .github/prompts/tools/)
   ├── cortex_vacuum_analyzer.py
   ├── cortex_vacuum_executor.py
   ├── governance_tools.py
   └── (other MCP toolkit scripts)
```

---

## Common Tasks

### "I want to create a new markdown document"
→ Create in `docs/DOCUMENT-NAME.md` (NOT anywhere else)

### "I wrote a Python utility script"
→ Move to `src/mcp/tools/script_name.py` (NOT root, NOT _workspaces/roadmap/)

### "Where should I put my tool?"
→ `src/mcp/tools/` for MCP-exposed tools
→ `src/mcp/utilities/` for helper utilities
→ `scripts/` for build/setup scripts
→ `cortex-brain/tierX/` for tier-specific code

### "I see a file in wrong location"
→ Move it immediately
→ Update references in prompts if needed
→ Verify pre-commit checks pass

### "How do I verify clean state?"
→ Run pre-commit verification commands above
→ All should return empty results

---

## Governance

**All enforcement through:**
1. ✅ **Prompts** - Guidance & rules enforced during development
2. ✅ **Master Plan** - Governance sections document requirements
3. ✅ **Pre-Commit** - Verification commands check compliance
4. ✅ **Phase Lock** - Cannot lock phase with violations

**Violations prevent:**
- Phase lock
- PR merge
- Code commit (if pre-commit checks fail)

**Remediation:**
- Move files to correct location
- Update any references
- Verify pre-commit checks pass
- Retry operation

---

## Questions?

**"Which folder should I use?"**
→ See "Where Files Go" table above or FILE-ORGANIZATION-QUICK-REFERENCE.md

**"Why was this changed?"**
→ See FILE-ORGANIZATION-REFACTORING-REPORT.md for full details

**"What are the rules?"**
→ See cortex-master.yaml (governance sections) or CORTEX.prompt.md

**"How do I verify it's clean?"**
→ Run pre-commit verification commands above

**"What if I have a special case?"**
→ Document in cortex-master.yaml under exceptions
→ Update prompts to reflect the exception
→ Get explicit approval before using

---

## Summary

| Aspect | Status | Details |
|--------|--------|---------|
| File organization | ✅ Complete | All files in correct locations |
| Prompt updates | ✅ Complete | All 4 prompts updated |
| Master plan | ✅ Complete | Governance sections added |
| Documentation | ✅ Complete | 9 comprehensive docs created |
| Verification | ✅ Complete | Clean state verified |
| Enforcement | ✅ Active | All mechanisms in place |

**READY FOR PRODUCTION USE**

---

**Created:** 2026-01-18  
**Status:** ✅ ACTIVE & ENFORCED  
**Next Review:** On next phase completion  
**Maintenance:** Check pre-commit rules before each commit
