# 🚀 MIGRATED — Master Plan Observatory Ready

## 📍 New Location

All planning files have been migrated to the **CORTEX Master Plan Observatory**:

```
cortex-registry/_cortex-master/
├── phases/active/          [Phase 21-23: Active development]
├── phases/completed/       [Phase 7-20.9: Historical phases]
├── enhancements/active/    [ENH-029: Capability Feasibility Gate]
├── dashboard/index.html    [Material.js Observatory]
└── meta/                   [Schemas, references, governance]
```

## 🎯 What Changed

| Aspect | Old Location | New Location | Status |
|--------|--------------|--------------|--------|
| Active Phases | `PHASE-21-*.yaml` | `phases/active/phase-21-*.yaml` | ✅ Migrated |
| Completed Phases | `PHASE-*.yaml` | `phases/completed/{2025,2026}/phase-*.yaml` | ✅ Migrated |
| Enhancements | `ENH-*.yaml` | `enhancements/active/enh-*.yaml` | ✅ Migrated |
| Dashboard | No unified view | `dashboard/index.html` | ✅ Created |
| Registry | Unorganized files | `index.yaml` auto-discovery | ✅ Created |
| Governance | _workspaces/cortex-plan/ | cortex-registry/_cortex-master/ | ✅ Centralized |

## 🔄 File Naming Convention

All YAML files now follow **CORE-028** (kebab-case):

```
BEFORE:                          AFTER:
PHASE-21-JSON-FIRST-REWRITE.yaml → phase-21-json-first-rewrite.yaml
ENH-029-CAPABILITY-GATE.yaml     → enh-029-capability-feasibility-gate.yaml
```

## 📊 Master Plan Statistics

- **Total Phases:** 19
- **Active:** 3 (Phases 21-23)
- **Completed 2026:** 5 (Phases 19-20.9)
- **Completed 2025:** 11 (Phases 7-18)
- **Active Enhancements:** 1 (ENH-029)
- **Completion Rate:** 85% (16/19 completed)

## 🌐 Dashboard Access

Open the observatory:
```
cortex-registry/_cortex-master/dashboard/index.html
```

**Features:**
- 📊 Real-time statistics and progress tracking
- 🎯 Phase timeline with completion rates
- 💡 Active enhancement details and implementation plans
- 🗺️ Development roadmap and strategy
- 📈 Metrics and velocity tracking

## 🚀 Integration Points

**cortex-architect.prompt.md:**
- ✅ Plan Registry Integration section added
- ✅ Dashboard auto-sync on AUDIT variance detection
- ✅ Agent wiring specified in index.yaml

**cortex-auditor.md:**
- ✅ Prompt Sync Validation (architect.prompt.md ↔ CORTEX.prompt.md)
- ✅ P1 check includes Plan Registry coherence

## ⚠️ Archive

Old shell scripts and working notes:
- `_workspaces/cortex-plan/_archive/` — Historical shell scripts (reference only)

## 🎓 Documentation

For detailed architecture:
- [cortex-registry/_cortex-master/index.yaml](../../cortex-registry/_cortex-master/index.yaml) — Full metadata
- [cortex-registry/_cortex-master/meta/](../../cortex-registry/_cortex-master/meta/) — Reference materials
- [Dashboard](../../cortex-registry/_cortex-master/dashboard/index.html) — Visual observatory

---

**Migration Date:** 2026-02-05  
**Migrated Files:** 20 YAML (19 phases + 1 enhancement)  
**Governance:** Single Source of Truth (cortex-registry/ authority maintained)

**Next Steps:** Use `cortex-registry/_cortex-master/` for all planning activities.
