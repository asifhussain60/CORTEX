# Planning Folder Structure Migration Analysis

**Created:** 2025-12-14  
**Author:** GitHub Copilot  
**Context:** Analysis for PLANNING-ARTIFACTS-ORGANIZATION-SYSTEM Phase 6

---

## 📊 Executive Summary

**Current State:** 
- 363 total files across multiple folder structures
- Mix of flat and hierarchical organization
- 28 root-level loose files creating navigation complexity

**Recommendation:** **YES - Roll in all folders** with phased, prioritized migration

**Rationale:**
1. Prevents dual-standard confusion (old flat + new hierarchical)
2. `features/` folder already contains most active work (41 files)
3. Root-level files cause same navigation issues as Phase 1-3 solved
4. Existing folders (`active/`, `completed/`, `archived/`) align with plan lifecycle
5. Migration engine already supports batch processing

---

## 📁 Current Folder Inventory

### Top-Level Planning Folders

| Folder | Files | Purpose | Migration Priority |
|--------|-------|---------|-------------------|
| `features/` | 41 | Feature development plans | **HIGH** (already hierarchical) |
| `active/` | 80 | Currently active plans | **HIGH** |
| `archived/` | 131 | Historical/completed plans | **MEDIUM** |
| `ado/` | 18 | Azure DevOps work items | **HIGH** |
| `completed/` | 11 | Finished plans | **MEDIUM** |
| `orchestrators/` | 15 | Orchestrator-specific plans | **MEDIUM** |
| `enhancements/` | 5 | System enhancement plans | **LOW** |
| `approved/` | 3 | Pre-approved plans | **LOW** |
| `cortex-4.0/` | ? | Future vision documents | **LOW** (keep separate) |

**Root-level loose files:** 28 files (YAML plans, tracking docs, guides)

### Features/ Subfolder Breakdown

| Subfolder | Files | Notes |
|-----------|-------|-------|
| `active/` | 17 | Already has sub-hierarchy |
| `archived/` | 0 | Empty (candidates for vacuum) |
| `completed/` | 2 | Minimal, easy migration |
| `approved/` | 2 | Minimal, easy migration |
| `.archive/` | 6 | Historical backups |
| `phases/` | 12 | Phase-specific docs |
| `benchmark-results/` | 2 | Performance tracking |

---

## 🎯 Migration Strategy Recommendations

### ✅ INCLUDE in Migration (Phases 6-7)

**Phase 6: Primary Folders (Estimated 4h)**

1. **active/** (80 files) - **CRITICAL**
   - Most current work
   - Direct lifecycle alignment with new structure
   - Many are master plans needing folder structure
   - **Action:** Scan for plan files, create folders, migrate artifacts

2. **ado/** (18 files) - **HIGH PRIORITY**
   - ADO work item plans
   - Already follows naming convention (ADO-12345-...)
   - Fits perfectly into new structure
   - **Action:** Treat as master plans, create folders per ADO item

3. **features/active/** (17 files) - **HIGH PRIORITY**
   - Already attempting hierarchical organization
   - Merge into unified `features/{status}/PLAN-xxx/` structure
   - **Action:** Migrate to parent-level features/ with proper folder structure

**Phase 7: Secondary Folders (Estimated 2h)**

4. **archived/** (131 files) - **MEDIUM PRIORITY**
   - Largest volume, but low urgency
   - Good candidate for batch migration
   - **Action:** Run migration in batches of 25, validate after each

5. **completed/** (11 files) - **MEDIUM PRIORITY**
   - Similar to archived, but smaller
   - **Action:** Migrate after active/ completes

6. **orchestrators/** (15 files) - **MEDIUM PRIORITY**
   - Orchestrator-specific planning docs
   - Could be treated as specialized plan type
   - **Action:** Create `features/orchestrators/{PLAN-id}/` or keep flat if not master plans

**Phase 8: Tertiary Folders (Estimated 1h)**

7. **enhancements/** (5 files) - **LOW PRIORITY**
   - Small, self-contained
   - Could remain flat or migrate for consistency
   - **Action:** Evaluate if true plans vs. loose notes

8. **Root-level loose files** (28 files) - **HIGH PRIORITY (cleanup)**
   - Causes navigation issues (original problem statement)
   - Many are orphaned or legacy tracking docs
   - **Action:** 
     - Classify: master plans → migrate to folders
     - Classify: tracking/guides → archive or move to appropriate category
     - Classify: obsolete → vacuum to `.archive/`

### ❌ EXCLUDE from Migration

1. **cortex-4.0/** - Keep separate (future vision, not execution plans)
2. **features/.archive/** - Already archived, no active use
3. **approved/** (3 files) - Too small, keep flat until pattern emerges

---

## 🔍 Key Findings

### Folder Structure Patterns

**Already Using Hierarchical Structure:**
- `features/active/` has sub-hierarchy (dashboard-consolidation/, orchestrator-enhancement/, etc.)
- Shows natural evolution toward folder organization
- Users already expect this pattern

**Lifecycle Folders:**
- `active/`, `completed/`, `archived/` align with plan lifecycle
- New structure already uses this pattern: `features/{status}/PLAN-xxx/`
- Perfect alignment for migration

**Naming Conventions:**
- **Standardized:** `PLAN-YYYY-MM-DD-name` (most common)
- **ADO format:** `ADO-12345-YYYY-MM-DD-name`
- **Legacy format:** Descriptive names without PLAN prefix
- **Migration challenge:** Need to normalize or preserve variants

### Cross-References

**At-Risk References (need update):**
- Plans in `active/` referencing other plans in `active/`
- `features/active/` plans referencing `active/` plans
- ADO items referencing feature plans
- Root-level tracking docs referencing multiple folders

**Mitigation:** PlanningVacuum.fix_broken_references() already implemented

### Duplicate Risks

**High-Risk Areas:**
- `active/` vs `features/active/` - potential overlap
- `completed/` vs `archived/` - unclear distinction
- Root-level files duplicating folder contents

**Mitigation:** DuplicateDetector already implemented (Phase 3)

---

## 📋 Updated Phase 6 Tasks

### Phase 6: Production Migration Execution

**Revised Duration:** 7 hours (was 3h - expanded scope)

**Task 6.1: Primary Folder Migration** (4h)
- Migrate `active/` → 80 files
- Migrate `ado/` → 18 files
- Migrate `features/active/` → 17 files
- Migrate root-level master plans → 15-20 files
- **Total:** ~130 files
- **Strategy:** Batch process, validate after each folder

**Task 6.2: Secondary Folder Migration** (2h)
- Migrate `completed/` → 11 files
- Migrate `archived/` (first 50 files) → 50 files
- **Total:** ~61 files
- **Strategy:** Lower priority, can be background work

**Task 6.3: Cleanup & Vacuum** (1h)
- Run DuplicateDetector on migrated folders
- Run PlanningVacuum to remove empty directories
- Archive orphaned files
- Fix broken cross-references
- Generate migration report

### Phase 7: Remaining Folders (Optional - Post-Phase 6)

**Duration:** 2h

**Task 7.1: Archived Plans Migration**
- Migrate remaining `archived/` files → 81 files
- Low urgency, historical only

**Task 7.2: Orchestrators & Enhancements**
- Migrate `orchestrators/` → 15 files
- Migrate `enhancements/` → 5 files
- Evaluate `approved/` → 3 files

---

## 🎯 Decision Matrix

| Folder | Include? | Priority | Reason |
|--------|----------|----------|--------|
| `active/` | ✅ **YES** | **CRITICAL** | Core active work, lifecycle alignment |
| `ado/` | ✅ **YES** | **HIGH** | ADO integration, already standardized |
| `features/active/` | ✅ **YES** | **HIGH** | Already hierarchical, merge for consistency |
| `archived/` | ✅ **YES** | **MEDIUM** | Prevents dual standards, batch migration |
| `completed/` | ✅ **YES** | **MEDIUM** | Lifecycle completion, small volume |
| `orchestrators/` | ✅ **YES** | **MEDIUM** | Consistency, moderate volume |
| `enhancements/` | ⚠️ **MAYBE** | **LOW** | Small, evaluate if true plans |
| `approved/` | ❌ **NO** | **LOW** | Too small, insufficient pattern |
| `cortex-4.0/` | ❌ **NO** | **N/A** | Future vision, not execution plans |
| Root loose files | ✅ **YES** | **HIGH** | Cleanup critical for navigation |

---

## 📈 Expected Outcomes

**Before Migration:**
```
cortex-brain/documents/planning/
├── active/ (80 loose files)
├── ado/ (18 loose files)
├── completed/ (11 loose files)
├── archived/ (131 loose files)
├── features/
│   ├── active/ (17 mixed files)
│   └── completed/ (2 files)
└── 28 loose files at root
```

**After Migration:**
```
cortex-brain/documents/planning/
├── features/
│   ├── active/
│   │   ├── PLAN-2025-12-08-feature-a/
│   │   │   ├── master-plan.md
│   │   │   ├── README.md
│   │   │   ├── sub-plans/
│   │   │   ├── artifacts/
│   │   │   └── ...
│   │   └── ADO-12345-ticket-name/
│   ├── completed/
│   │   └── PLAN-2025-11-15-completed-feature/
│   └── archived/
│       └── PLAN-2025-09-10-old-feature/
├── orchestrators/ (keep flat or migrate)
├── enhancements/ (keep flat)
├── cortex-4.0/ (unchanged)
└── .archive/ (orphaned files moved here)
```

**Benefits:**
- ✅ Single source of truth for plan organization
- ✅ No navigation confusion (old flat vs. new hierarchical)
- ✅ All plans follow consistent structure
- ✅ Easy to find all artifacts for any plan
- ✅ Lifecycle management built-in (active/completed/archived)
- ✅ Root-level cleanup eliminates navigation pollution

**Metrics:**
- **Files organized:** ~280 files (80 + 18 + 17 + 131 + 11 + 15 + 28 root)
- **Folders created:** ~60-80 plan folders
- **Duplicates handled:** 5-10 expected
- **Empty directories removed:** 3-5 expected
- **Broken references fixed:** 10-15 expected

---

## ⚠️ Risk Assessment

### Low Risk (Mitigated)
- **Data loss:** Git checkpoint before migration + dry-run + validation
- **Duplicate handling:** DuplicateDetector already implemented
- **Broken references:** PlanningVacuum.fix_broken_references() ready
- **Empty directories:** PlanningVacuum.vacuum_empty_directories() ready

### Medium Risk (Needs Attention)
- **Volume:** 280 files is significant, but engine supports batch processing
  - **Mitigation:** Staged migration (Phase 6.1 → 6.2 → 6.3)
- **Cross-references:** Complex web of inter-plan references
  - **Mitigation:** Automated reference updating + manual review option
- **Naming normalization:** Multiple naming conventions
  - **Mitigation:** Scanner detects variants, preserves original names

### Addressed Risks
- ✅ Migration engine complete (Phase 2)
- ✅ Duplicate detection complete (Phase 3)
- ✅ Vacuum utilities complete (Phase 3)
- ✅ All 132 tests passing (100%)

---

## 📝 Recommendations

### Immediate (Phase 6)

1. **Update PLANNING-ARTIFACTS-ORGANIZATION-SYSTEM.yaml:**
   - Expand Phase 6 to include all primary folders
   - Add Phase 7 for secondary folders (optional)
   - Update duration estimates (7h for Phase 6)

2. **Migration Execution Order:**
   ```
   Stage 1: Dry-run on all folders → Review preview
   Stage 2: Migrate active/ (80 files) → Validate
   Stage 3: Migrate ado/ (18 files) → Validate
   Stage 4: Migrate features/active/ (17 files) → Validate
   Stage 5: Migrate root loose files (28 files) → Validate
   Stage 6: Migrate completed/ (11 files) → Validate
   Stage 7: Migrate archived/ (first 50) → Validate
   Stage 8: Run cleanup & vacuum
   ```

3. **Success Metrics:**
   - Zero data loss
   - All tests passing post-migration
   - <5% manual intervention rate
   - All broken references fixed automatically

### Future (Post-Phase 7)

4. **Remaining Folders:**
   - `archived/` (remaining 81 files) - background migration
   - `orchestrators/`, `enhancements/` - evaluate need vs. consistency

5. **Documentation:**
   - Update `cortex-brain/documents/planning/README.md`
   - Create migration guide in `docs/`
   - Update planning orchestrator guide

---

## ✅ Conclusion

**YES - Roll in all folders** following the phased approach:

- **Phase 6 (CRITICAL):** `active/`, `ado/`, `features/active/`, root loose files (~130 files, 4h)
- **Phase 6 Cleanup:** Duplicates, vacuum, references (1h)
- **Phase 7 (OPTIONAL):** `completed/`, `archived/` (first 50), `orchestrators/`, `enhancements/` (~76 files, 2h)

**Total Additional Effort:** 5-7 hours (on top of existing 14h estimate) = **19-21 hours total**

**Key Success Factors:**
1. Staged migration with validation gates
2. Existing migration engine already proven (132/132 tests passing)
3. Git-based rollback for instant recovery
4. Cleanup utilities (DuplicateDetector, PlanningVacuum) already complete

**Final Recommendation:** Execute Phase 6 immediately with all primary folders. Defer Phase 7 as lower-priority background work.
