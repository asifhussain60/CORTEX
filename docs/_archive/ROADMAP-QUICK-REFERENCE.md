# Quick Reference - CORTEX Roadmap Structure (Post-Fix)

## Single Source of Truth

```
_workspaces/roadmap/cortex-master.yaml    ← THE ONLY master plan file
├── phase_tracker:                        ← Current phase status
│   ├── PHASE-01: {locked: true, status: COMPLETED}
│   ├── PHASE-02: {locked: true, status: COMPLETED}
│   └── ... (all phases with locked/status)
└── metadata: {completion_percentage, total_ac_ids, ...}
```

## Key Commands

```bash
# Check what phase to work on
grep "locked: false" _workspaces/roadmap/cortex-master.yaml

# Check phase specifications
cat _workspaces/roadmap/phases/phase-NN.yaml

# Reference v1 (historical patterns)
cat _workspaces/roadmap/_archives/cortex-master-v1.yaml
```

## File Locations Map

| Purpose | Location | Type |
|---------|----------|------|
| Master Plan (SSOT) | `_workspaces/roadmap/cortex-master.yaml` | YAML |
| Phase Specifications | `_workspaces/roadmap/phases/phase-NN.yaml` | YAML |
| Historical Reference | `_workspaces/roadmap/_archives/cortex-master-v1.yaml` | YAML |
| Archived Reports | `_workspaces/roadmap/reports/_archived_reports/` | Markdown |
| Essential Docs | `docs/` | Markdown |
| Builder Agent | `.github/agents/cortex-builder.md` | Markdown |
| Builder Prompt | `.github/prompts/cortex-builder.prompt.md` | Markdown |

## All Agents/Prompts Reference

**All point to:** `_workspaces/roadmap/cortex-master.yaml`

- ✅ `.github/agents/cortex-builder.md`
- ✅ `.github/agents/cortex-review-governance.md`
- ✅ `.github/agents/cortex-gap-detection.md`
- ✅ `.github/agents/cortex-planner.md`
- ✅ `.github/prompts/cortex-builder.prompt.md`
- ✅ `.github/prompts/cortex-review.prompt.md`
- ✅ `.github/prompts/cortex-git-commit.prompt.md`

## What Was Fixed

### Changed
- `.github/agents/cortex-builder.md` - Updated path references
- `.github/agents/cortex-review-governance.md` - Updated path references
- `.github/copilot-instruction.md` - Updated all references

### Cleaned Up
- `docs/` - Removed 300+ temporary artifacts, kept 38 essential files
- `_workspaces/roadmap/phases/` - Removed 8 markdown files (YAML only)
- `_workspaces/roadmap/reports/` - Archived 225 reports to `_archived_reports/`

### Already Correct (No changes)
- `.github/prompts/cortex-builder.prompt.md`
- `.github/prompts/cortex-review.prompt.md`
- `.github/prompts/cortex-git-commit.prompt.md`
- All other agents

## Critical Truth

- **SSOT:** `_workspaces/roadmap/cortex-master.yaml` (ONLY source)
- **Not:** `.github/roadmap/` (does NOT exist, was causing confusion)
- **Not:** Temporary session files or multiple versions
- **Not:** "100% complete" - check phase_tracker for real status

## Going Forward

1. Always reference `_workspaces/roadmap/cortex-master.yaml`
2. Read `phase_tracker` for current status (truth)
3. Consult `phases/phase-NN.yaml` for AC specifications
4. Reference `_archives/cortex-master-v1.yaml` for patterns
5. Archive old reports, don't let them accumulate

---

**Last Updated:** January 18, 2026
**Status:** All references unified to single SSOT
**Issue:** chat01.md incorrect reporting - RESOLVED
