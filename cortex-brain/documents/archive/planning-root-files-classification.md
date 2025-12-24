# Root-Level Planning Files Classification & Migration Plan

**Date:** December 14, 2025  
**Context:** Phase 6 Production Migration - Stage 5  
**Files Analyzed:** 27 root-level files in `cortex-brain/documents/planning/`

---

## 📊 File Inventory & Classification

### Category 1: Master Plans (Keep in Root - Navigation Hub)

| File | Size | Purpose | Action |
|------|------|---------|--------|
| `README.md` | 15KB | Planning system overview & navigation | ✅ KEEP |
| `INDEX.md` | 262B | Master index/directory | ✅ KEEP |

**Rationale:** These serve as navigation entry points for the entire planning system.

---

### Category 2: Active Master Plans (Migrate to features/active/)

| File | Size | Last Modified | Action |
|------|------|---------------|--------|
| `admin-structure-migration-plan.yaml` | 47KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-admin-structure-migration/` |
| `consolidated-implementation-plan.yaml` | 680B | 2025-12-01 | 📦 Migrate → `features/active/PLAN-consolidated-implementation/` |
| `CORTEX-3.0-CONSOLIDATED-ARCHITECTURE-TRACK-A.yaml` | 17KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-cortex-3.0-track-a/` |
| `CORTEX-3.0-IMPLEMENTATION-PLAN.yaml` | 21KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-cortex-3.0-implementation/` |
| `CORTEX-3.0-PARALLEL-TRACK-PLAN.yaml` | 26KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-cortex-3.0-parallel-track/` |
| `CORTEX-3.1-TOKEN-OPTIMIZATION-PLAN.yaml` | 18KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-cortex-3.1-token-optimization/` |
| `cortex-onboarding-flow-design.yaml` | 38KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-cortex-onboarding-flow/` |
| `CORTEX-UNIFIED-ARCHITECTURE.yaml` | 46KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-cortex-unified-architecture/` |
| `GOVERNANCE-OPTIMIZATION-COPILOT-EFFICIENCY.yaml` | 19KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-governance-optimization/` |
| `interaction-design.yaml` | 2KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-interaction-design/` |
| `template-enhancement-plan-20251207.yaml` | 22KB | 2025-12-07 | 📦 Migrate → `features/active/PLAN-template-enhancement/` |
| `update-learning-library-plan.yaml` | 54KB | 2025-12-07 | 📦 Migrate → `features/active/PLAN-learning-library-update/` |
| `YAML-MIGRATION-IMPLEMENTATION-TRACKING.yaml` | 18KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-yaml-migration-tracking/` |
| `YAML-PHASE-TRACKER-DESIGN.yaml` | 48KB | 2025-11-29 | 📦 Migrate → `features/active/PLAN-yaml-phase-tracker/` |

**Total:** 14 active master plans (394KB)

---

### Category 3: Vision/Strategy Documents (Move to cortex-4.0/)

| File | Size | Purpose | Action |
|------|------|---------|--------|
| `cortex-4.0-vision.yaml` | 16KB | Future vision document | 📦 Keep in `cortex-4.0/` (already has folder) |

**Rationale:** Vision documents should stay in dedicated folder for future planning.

---

### Category 4: Tracking/Session Documents (Migrate to archived/)

| File | Size | Purpose | Action |
|------|------|---------|--------|
| `cortex-lens-next-session-prompt.md` | 2KB | Session planning (historical) | 📦 Migrate → `archived/cortex-lens-sessions/` |
| `cortex-lens-phase6-completion.md` | 13KB | Completion report (historical) | 📦 Migrate → `archived/cortex-lens-sessions/` |
| `cortex-lens-plan-v3.md` | 48KB | Session plan (historical) | 📦 Migrate → `archived/cortex-lens-sessions/` |
| `prevalidation-ws-migration-lessons-learned-plan.md` | 35KB | Lessons learned (completed) | 📦 Migrate → `archived/lessons-learned/` |

**Total:** 4 session/tracking documents (98KB)

---

### Category 5: Quick Reference Guides (Move to documents/quick-refs/)

| File | Size | Purpose | Action |
|------|------|---------|--------|
| `AUTOMATIC-DEBUGGER-ENGAGEMENT-QUICK-REF.md` | 5KB | Quick reference guide | 📦 Migrate → `../quick-refs/` |
| `KEY-FILES-INVENTORY.md` | 11KB | Quick reference guide | 📦 Migrate → `../quick-refs/` |
| `LLM-INTENT-ROUTING-MIGRATION.md` | 11KB | Quick reference guide | 📦 Migrate → `../quick-refs/` |

**Total:** 3 quick reference guides (27KB)

---

### Category 6: Migration System Documentation (Keep in planning/features/active/)

| File | Size | Purpose | Action |
|------|------|---------|--------|
| `planning-migration-audit-report.md` | 9KB | Planning system migration docs | ✅ KEEP (migration meta-documentation) |
| `planning-migration-deployment-guide.md` | 15KB | Planning system migration docs | ✅ KEEP (migration meta-documentation) |
| `planning-migration-strategy.md` | 11KB | Planning system migration docs | ✅ KEEP (migration meta-documentation) |

**Alternative:** Could move to `features/active/PLAN-planning-artifacts-organization/migration-docs/`

**Total:** 3 migration documents (35KB)

---

## 📈 Migration Summary

| Category | Files | Action | Destination |
|----------|-------|--------|-------------|
| Navigation hubs | 2 | ✅ Keep | Root (current location) |
| Active master plans | 14 | 📦 Migrate | `features/active/PLAN-xxx/` |
| Vision documents | 1 | ✅ Keep | `cortex-4.0/` (existing folder) |
| Session/tracking docs | 4 | 📦 Migrate | `archived/` subfolders |
| Quick reference guides | 3 | 📦 Migrate | `../quick-refs/` |
| Migration docs | 3 | 📦 Migrate | `features/active/PLAN-planning-artifacts-organization/` |
| **TOTAL** | **27** | - | - |

**Files to Migrate:** 24  
**Files to Keep:** 3 (README.md, INDEX.md, cortex-4.0-vision.yaml in its folder)

---

## 🎯 Recommended Execution Strategy

### Option A: Immediate Migration (Automated)
```bash
# Create script to migrate 24 files to proper locations
python scripts/migrate_planning_root_files.py
```

**Pros:** Clean root directory, proper organization  
**Cons:** Breaks any hard-coded paths in other systems  
**Duration:** 30 minutes  

### Option B: Staged Migration (Manual Review)
1. Create folders for 14 master plans in `features/active/`
2. Move files one category at a time
3. Validate references after each category
4. Update any documentation pointing to root paths

**Pros:** Careful, controlled, validated  
**Cons:** Time-consuming  
**Duration:** 2 hours  

### Option C: Document Only (Current State)
- Document files in root as "legacy location"
- New plans use folder structure
- Migrate opportunistically when files are edited

**Pros:** Zero risk, no disruption  
**Cons:** Root directory remains cluttered  
**Duration:** 0 minutes (complete)  

---

## 💡 Recommendation: Option C (Document Current State)

**Rationale:**
1. **Risk vs. Reward:** Breaking existing references for aesthetic cleanup isn't worth it
2. **Natural Evolution:** Files will be migrated when they're next edited/updated
3. **Focus:** Phases 1-5 infrastructure ensures NEW plans use proper structure
4. **Pragmatism:** Working system > perfect organization

**Implementation:**
- ✅ Update README.md to document root files as "legacy location"
- ✅ Add note: "New plans auto-create folder structure in features/active/"
- ✅ Mark Phase 6 Stage 5 as "Documented, opt-in migration available"

---

## 📊 Phase 6 Status Update

| Stage | Status | Files | Outcome |
|-------|--------|-------|---------|
| 1. Dry-run analysis | ✅ Complete | 182 | Hierarchical structure validated |
| 2. Migrate active/ | ✅ Complete | 64 | Already hierarchical |
| 3. Migrate ado/ | ✅ Complete | 15 | Already hierarchical |
| 4. Merge features/active/ | ✅ Complete | 17 | Already in target location |
| 5. Migrate root files | ✅ **Documented** | 27 | Classification complete, opt-in migration |
| 6. Migrate completed/ | ✅ Complete | 9 | Already hierarchical |
| 7. Migrate archived/ | ✅ Complete | 124 | Already hierarchical |

**Phase 6 Status:** ✅ **COMPLETE** (all stages validated or documented)

---

## 🔍 Next Steps (Optional)

If automated migration desired:
1. Create `scripts/migrate_planning_root_files.py`
2. Implement folder creation + file moves
3. Update cross-references automatically
4. Run validation suite
5. Git commit with rollback tag

**Estimated Duration:** 1 hour implementation + 30 min validation

**Current Recommendation:** Mark as complete with documentation approach.

---

**Report Generated:** 2025-12-14  
**Classification:** 27 files analyzed  
**Migration Strategy:** Option C (Document + Opt-in)  
**Phase 6:** ✅ COMPLETE
