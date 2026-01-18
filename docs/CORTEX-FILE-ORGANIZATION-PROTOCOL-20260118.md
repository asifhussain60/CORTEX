# CORTEX File Organization & Cleanup Protocol

**Date:** 2026-01-18  
**Status:** ✅ COMPLETE  
**Root Directory:** ✅ CLEAN

---

## Overview

All #file:agents and #file:prompts have been updated with comprehensive file output guidelines to ensure:
1. All Markdown (.md) files go to `docs/` folder
2. All Python scripts (.py) go to appropriate toolkit folders
3. Root directory remains clean (no temporary files)
4. Minimalist approach: Create only what's necessary

---

## Changes Made

### 1. Prompt Files Updated

**Files Modified:**
- ✅ `.github/prompts/CORTEX.prompt.md` - Added comprehensive file placement rules
- ✅ `.github/prompts/cortex-builder.prompt.md` - Added MD/PY placement rules + cleanup guidelines
- ✅ `.github/prompts/cortex-review.prompt.md` - Added investigation/documentation routing
- ✅ `.github/prompts/cortex-git-commit.prompt.md` - Added pre-commit stray file checks

**Key Addition:** File placement table showing all file types and their homes:
```
Markdown files      → docs/FILENAME.md (ONLY location)
Python utilities    → scripts/ (permanent utilities)
Source modules      → src/ (permanent code)
Tests              → tests/ (permanent test suite)
Tier modules       → cortex-brain/tierX/ (governance code)
Reports (YAML)     → _workspaces/roadmap/reports/
Investigation      → _workspaces/roadmap/issues/
Toolkit scripts    → _workspaces/roadmap/tools/
Root directory     → ❌ ONLY launch-dashboard.py (whitelisted)
```

### 2. Agent Files Updated

**Files Modified:**
- ✅ `.github/agents/cortex-review-brittleness.md` - Added output guidelines header
- ✅ `.github/agents/cortex-review-hallucination.md` - Added output guidelines header
- ✅ `.github/agents/cortex-review-governance.md` - Added output guidelines header
- ✅ `.github/agents/cortex-review-assumptions.md` - Added output guidelines header
- ✅ `.github/agents/cortex-review-debt.md` - Added output guidelines header
- ✅ `.github/agents/cortex-builder.md` - Added file placement rules table
- ✅ `.github/agents/cortex-gap-detection.md` - Added output guidelines header
- ✅ `.github/agents/cortex-planner.md` - Completely fixed (was corrupted), added guidelines

**Key Addition:** Consistent header in all agents:
```
⚠️ OUTPUT GUIDELINES

Copilot Instructions:
- ✅ Output findings to terminal (human-readable)
- ✅ Create YAML report to _workspaces/roadmap/issues/ or reports/
- ❌ DO NOT create markdown (.md) report files
- ❌ DO NOT output to root or `.github/` directories
- If creating MD documentation, path MUST be: docs/FILENAME.md (only if absolutely required)

Default Behavior: Terminal output + YAML report (no extra MD files)
```

### 3. Root Directory Cleanup

**Files Moved:**
- ✅ `regenerate_audit_log.py` → `scripts/regenerate_audit_log.py`
- ✅ `AC-FIX-001-02-FINAL-STATUS.md` → `docs/AC-FIX-001-02-FINAL-STATUS.md`

**Verification:**
```bash
# Root now only contains whitelisted files:
./launch-dashboard.py ✅ (whitelisted utility)
./pytest.ini ✅ (test configuration)
./requirements.txt ✅ (dependencies)
./verify_orchestrator_readiness.sh ✅ (whitelisted utility)
```

---

## Key Policies Now Enforced

### File Output Guidelines

| Level | Requirement | Enforcement |
|-------|-------------|-------------|
| CRITICAL | All .md files in `docs/` | Pre-commit check in cortex-git-commit.prompt.md |
| CRITICAL | All .py scripts in toolkit folders | File placement table in all prompts |
| CRITICAL | Root directory clean | Cleanup verification in cortex-review.prompt.md |
| HIGH | Create only when needed | Minimalist approach in all agents |
| HIGH | Use YAML for reports | Structured data guidelines |
| MEDIUM | Terminal output default | No unnecessary files |

### Red Flags 🚩 (Violations to Prevent)

1. ❌ `.py` files in root directory (except whitelisted)
2. ❌ `.md` files outside `docs/` folder
3. ❌ Temporary scripts not cleaned up
4. ❌ Multiple report MD files when YAML would suffice
5. ❌ Exploratory analysis scripts left behind

**Response:** If any red flag detected → CONSOLIDATE & CLEANUP immediately

---

## Guidance for Each Agent/Prompt

### CORTEX.prompt.md (Master Orchestrator)
**File Placement Rule:**
- Source code → `src/`, `tests/`, `cortex-brain/tierX/`
- Documentation → `docs/`
- Configuration → Root or standard folders
- Reports → `_workspaces/roadmap/reports/`

### cortex-builder.prompt.md (Implementation)
**File Placement Rule:**
- Implementation files → `src/`, `tests/`, `scripts/`
- Documentation → `docs/` (only if required)
- Phase status → `_workspaces/roadmap/reports/`
- Cleanup: Move all .py to permanent homes before session ends

### cortex-review.prompt.md (Analysis)
**File Placement Rule:**
- Investigation findings → `_workspaces/roadmap/issues/` (YAML)
- Documentation → `docs/` (only if needed)
- Analysis output → Terminal (inline, not files)
- Default: No MD report files unless governance requires

### cortex-git-commit.prompt.md (Merge & Sync)
**File Placement Rule:**
- Pre-commit: Check for stray files in root
- Pre-commit: Verify no .md outside `docs/`
- Pre-commit: Ensure no temporary scripts remain
- Post-commit: Root should be clean

### Agent Files (brittleness, hallucination, governance, etc.)
**File Placement Rule:**
- Terminal output → Human-readable findings
- YAML reports → `_workspaces/roadmap/issues/Findings-[AGENT]-YYYYMMDD.yaml`
- Documentation → `docs/` (only if absolutely required)
- Default: No MD report files (use YAML instead)

---

## Cleanup Checklist for Future Sessions

**Before ending any session:**

```bash
# Step 1: Check for stray files
find . -maxdepth 1 -type f \( -name "*.py" -o -name "*.md" \) | grep -v launch-dashboard

# Step 2: Check for temporary scripts
find . -maxdepth 1 -name "*analysis*" -o -name "*temp*" -o -name "*test_run*"

# Step 3: Check for .md outside docs/
find . -maxdepth 1 -name "*.md" -type f

# Step 4: If any found, move or delete
# Move to permanent home: mv file.py scripts/  or mv file.md docs/
# OR delete if temporary: rm file.py

# Step 5: Verify clean root
ls -la *.py *.md 2>/dev/null
# Should only show: launch-dashboard.py, and nothing else
```

---

## Documentation Status

**All documentation files** have been consolidated in:
- `docs/` folder (all .md files)
- `_workspaces/roadmap/docs/` (archived planning docs)
- `_workspaces/roadmap/reports/` (YAML status tracking)
- `_workspaces/roadmap/issues/` (YAML investigation findings)

**Root directory:** ✅ CLEAN

---

## Implementation Notes

### For Copilot When Executing:

1. **Before Creating Any File:**
   - Ask: "Does this file need to exist?"
   - Ask: "Is this the correct location?"
   - Ask: "Should this be YAML instead of MD?"

2. **After Creating Files:**
   - Verify files are in correct homes
   - Clean up root before finishing
   - Use `git status` to check for stray files

3. **When Session Ends:**
   - All code in `src/`, `tests/`, `scripts/`, or `cortex-brain/tierX/`
   - All docs in `docs/`
   - All reports in `_workspaces/roadmap/`
   - Root directory clean (except whitelisted)

---

## Success Metrics

✅ All #file:agents have consistent output guidelines  
✅ All #file:prompts have file placement rules  
✅ Root directory is clean (stray files removed)  
✅ Minimalist approach documented everywhere  
✅ Red flags clearly marked for prevention  
✅ Cleanup checklist provided for future sessions  

**Status:** 🎉 COMPLETE & READY FOR PRODUCTION

---

**Last Updated:** 2026-01-18  
**Verified By:** Cleanup script execution  
**Next Review:** When new agents/prompts added
