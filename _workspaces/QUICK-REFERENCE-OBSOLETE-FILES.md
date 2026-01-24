# QUICK REFERENCE: OBSOLETE FILES AT A GLANCE

**Situation:** CORTEX has accumulated 108 obsolete files across the repository that could confuse the master orchestrator and slow initialization.

**Critical Problem:** Knowledge base exists in **3 duplicate locations**, causing stale data risk.

---

## 🔴 THE THREE PROBLEMS

### Problem 1: Knowledge Base Triplication (CRITICAL)
```
Location 1: /cortex/knowledge/best-practices/          ✅ KEEP (canonical, 46 files)
Location 2: /cortex/brain/knowledge/                   ❌ DELETE (stale, 36 files)
Location 3: /cortex/brain/tier3/knowledge/             ❌ DELETE (obsolete, 42+ files)
```
**Impact:** Master orchestrator may load wrong version of governance rules  
**Fix:** Delete Locations 2 & 3 (~1 hour)

---

### Problem 2: Orphaned Migration Scripts (HIGH)
```
11 files from completed folder migration (2025-11)
Examples: migrate_folder_structure.py, migration-validator.py, doc-migrate-automated.py
Status: Finished, never to be run again
Impact: Code clutter, developer confusion
Fix: Delete all (~30 minutes)
```

---

### Problem 3: Stale Test Files (HIGH)
```
5 test files that test non-existent infrastructure:
- test_folder_structure.py
- test_folder_structure_design.py
- test_folder_migration_script.py (and 2 more)

Impact: Test suite bloat, false confidence in coverage
Fix: Delete all (~15 minutes)
```

---

## 📊 FILES BY CATEGORY

| Category | Count | Delete? | Effort |
|----------|-------|---------|--------|
| Knowledge duplicates | 78 | ✅ YES | 1.0h |
| Migration scripts | 11 | ✅ YES | 0.5h |
| Migration tests | 5 | ✅ YES | 0.25h |
| Scaffolders | 2 | ✅ YES | 0.25h |
| Infrastructure (audit) | 2 | ⚠️ AUDIT | 0.5h |
| Config files (audit) | 4 | ⚠️ AUDIT | 0.5h |
| Archive directories | 3 | ⚠️ VAULT | 0.25h |
| Log files | 1 | ✅ YES | 0.05h |
| **TOTAL** | **108** | | **4.5h** |

---

## 📍 WHERE THE DOCUMENTATION IS

In `_workspaces/`:

1. **OBSOLETE-FILES-INVENTORY.md** ← Read this for WHY (detailed analysis)
2. **CLEANUP-ACTION-PLAN.md** ← Read this for HOW (step-by-step commands)
3. **CORTEX-OBSOLETE-FILES-SUMMARY.md** ← This document (quick overview)

---

## ⚡ QUICKSTART (4.5 Hours)

```bash
# 1. Verify nothing will break (15 min)
grep -r "from cortex.brain.knowledge" cortex/ || echo "✓ Safe to delete"

# 2. Backup (5 min)
cp -r cortex/brain/knowledge /backup/knowledge-backup

# 3. Delete (30 min)
rm -rf cortex/brain/knowledge
rm -rf cortex/brain/tier3/knowledge
# [delete 11 migration scripts]
# [delete 5 test files]

# 4. Verify (45 min)
pytest tests/ -v  # Must pass 100%

# 5. Commit (30 min)
git commit -m "AC-REM-KB-001: Remove duplicate knowledge bases"
```

**See CLEANUP-ACTION-PLAN.md for exact commands**

---

## ✅ SUCCESS CRITERIA

After cleanup:
- [ ] No import errors
- [ ] All tests pass
- [ ] Master orchestrator initializes cleanly
- [ ] Knowledge repository loads from Location 1 only
- [ ] Git history preserved (all deletions tracked)

---

## 🔄 IF SOMETHING BREAKS

```bash
# Restore from backup
cp -r /backup/knowledge-backup cortex/brain/knowledge

# Revert commits
git reset --hard HEAD~4
```

See CLEANUP-ACTION-PLAN.md "Rollback Procedure" for details

---

## 📋 CHECKLIST

- [ ] Read OBSOLETE-FILES-INVENTORY.md (critical issues)
- [ ] Read CLEANUP-ACTION-PLAN.md (full procedure)
- [ ] Run pre-flight verification
- [ ] Create backups
- [ ] Execute deletions (in order)
- [ ] Run tests (must pass 100%)
- [ ] Create git commits with AC-IDs
- [ ] Update documentation

---

## 💡 KEY INSIGHT

**Why this matters:** The master orchestrator initializes all knowledge bases at startup. With 3 copies:
- 3x memory bloat
- Context confusion (which location does registry read from?)
- Stale data risk (updates to Location 1 not reflected in 2 & 3)

**Solution:** Keep Location 1 only, delete Locations 2 & 3

---

## 🚀 READY TO START?

**Option A:** Quick and safe
1. Read CLEANUP-ACTION-PLAN.md
2. Run pre-flight verification
3. Execute deletions step-by-step

**Option B:** Understanding first
1. Read OBSOLETE-FILES-INVENTORY.md (why each item is obsolete)
2. Read CLEANUP-ACTION-PLAN.md (how to delete safely)
3. Execute

**Questions?** See full documentation in `_workspaces/`

---

**Total Time:** 4.5 hours | **Risk:** LOW | **Benefit:** Production-Ready System

---

## FILES TO DELETE (COPY-PASTE READY)

### TIER 1: Knowledge Base Duplicates
```bash
rm -rf cortex/brain/knowledge/
rm -rf cortex/brain/tier3/knowledge/
```

### TIER 2: Migration Scripts
```bash
rm -f cortex/scripts-root-archive/migrate_folder_structure.py
rm -f cortex/scripts-root-archive/maintenance/migrate_folder_structure.py
rm -f cortex/scripts-root-archive/migration-validator.py
rm -f cortex/scripts-root-archive/doc-migrate-automated.py
rm -f cortex/scripts-root-archive/create_stubs.py
rm -f cortex/scripts-root-archive/phase_c_stub_generator.py
rm -f cortex/scripts-root-archive/doc-categorization-rules.yaml
rm -f cortex/scripts-root-archive/doc-ignore-list.yaml
```

### TIER 3: Test Files
```bash
rm -f tests/unit/test_folder_structure.py
rm -f tests/unit/test_folder_structure_design.py
rm -f tests/unit/infrastructure/test_folder_structure_design.py
rm -f tests/unit/infrastructure/test_folder_migration_script.py
rm -f tests/unit/test_migration_script.py
```

### TIER 4: Scaffolders & Logs
```bash
rm -f cortex/tools/scaffolder_templates.py
rm -f cortex/tools/orchestrator_scaffolder.py
rm -f cortex/test_audit_trail.log
```

**⚠️ VERIFY PRE-FLIGHT FIRST** (See CLEANUP-ACTION-PLAN.md Section 1)

---

**Status:** Ready for Implementation  
**Governance:** TIER 0 Enforcement  
**Next:** Execute CLEANUP-ACTION-PLAN.md
