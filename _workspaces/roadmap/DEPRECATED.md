# ⚠️ DEPRECATED: Roadmap Folder

**Date:** 2026-01-27  
**Authority:** CORTEX Master Orchestrator  
**Status:** ARCHIVED - DO NOT USE

---

## 🚫 This Folder is Deprecated

The `_workspaces/roadmap/` tracking system has been **superseded** by the Docker-first migration plan.

### Migration Path

| Old System | New System | Status |
|------------|------------|--------|
| `cortex-impl-map.yaml` | `_workspaces/docker-plan/migration-phases-plan.yaml` | ✅ Migrated |
| `phases/*.yaml` | `_workspaces/docker-plan/PHASE-*.yaml` | ✅ Consolidated |
| Manual tracking | Docker-plan execution logs | ✅ Automated |

---

## 📍 Use This Instead

**CANONICAL TRACKING SYSTEM:**
```
_workspaces/docker-plan/
├── migration-phases-plan.yaml          # Master plan (Phases 0-6 + 7.1-7.4)
├── docker-plan-index.md                # Navigation hub
├── PHASE-7-FUTURE-ENHANCEMENTS.yaml    # Enhancement phases
└── PHASE-*-*.md                        # Completion reports
```

**Entry Point:** `/Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/docker-plan-index.md`

---

## 🗄️ Archive Reason

**Why Deprecated:**
1. **Drift Prevention:** Single source of truth eliminates tracking conflicts
2. **Docker-First:** New architecture requires new tracking approach
3. **Execution Alignment:** Docker-plan has automated validation gates
4. **Duplication:** cortex-impl-map.yaml (5194 lines) had significant overlap with docker-plan

**Decision Authority:** Docker Migration Phase 0-6 completion (100%)

---

## ⚡ Quick Reference

**Before (DEPRECATED):**
```bash
# ❌ OLD - Don't update this
_workspaces/roadmap/cortex-impl-map.yaml
```

**After (CURRENT):**
```bash
# ✅ NEW - Use this
_workspaces/docker-plan/migration-phases-plan.yaml
```

---

## 📚 Historical Value

This folder is **preserved for archaeology** but should not be modified:
- Contains historical phase definitions from pre-Docker era
- Useful for understanding evolution of CORTEX requirements
- Reference for gap analysis and lessons learned

**Archive Date:** 2026-01-27  
**Last Valid Version:** v3.9-machine-autonomous-tracks-synced (2026-01-21)

---

## ✅ What to Do

1. **For new phases:** Add to `migration-phases-plan.yaml` or create `PHASE-7.X-*.yaml` in `docker-plan/`
2. **For tracking:** Update phase status in `migration-phases-plan.yaml`
3. **For acceptance criteria:** Define inline in phase specs (no separate AC files)
4. **For reports:** Create completion reports in `docker-plan/` (e.g., `PHASE-6-FINAL-STATUS-REPORT.md`)

---

**Questions?** See `docker-plan-index.md` for complete navigation.
