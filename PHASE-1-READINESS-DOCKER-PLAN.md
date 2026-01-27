# CORTEX Docker-Plan - Phase 1 Readiness Guide

**Date:** 2026-01-27  
**Phase:** Component Analysis & Inventory Discovery  
**Status:** 🟢 **READY FOR EXECUTION**  
**Estimated Duration:** 4 hours

---

## 🎯 Phase 1 Objective

Analyze actual component dependencies and generate precise deletion manifests for the subtraction approach.

**This phase is ANALYSIS-ONLY** - no code deletion occurs in Phase 1. This makes it low-risk and safe to execute.

---

## 📋 Phase 1 Tasks (from Master Plan)

### Task 1.1: Python Code Structure Analysis
**Objective:** Map all Python files and their dependencies

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
find . -name "*.py" -type f | sort > /tmp/all_python_files.txt
# Result: Complete list of 1,592 Python files
```

**Deliverable:** Full Python file inventory with:
- File paths
- Import chains
- Module dependencies
- Deletion safety ratings

### Task 1.2: Test File Mapping
**Objective:** Identify which tests apply to essential components

```bash
find tests/ -name "*.py" -type f | sort > /tmp/all_test_files.txt
# Result: 537 test files mapped
```

**Deliverable:**
- Test coverage map
- Tests for essential vs. non-essential components
- Cleanup candidates

### Task 1.3: Documentation Inventory
**Objective:** Identify which docs to keep/remove

```bash
find docs/ -name "*.md" -type f | wc -l
# Result: ~753 MD files
```

**Deliverable:**
- Doc retention criteria
- Deletion candidates

### Task 1.4: Wiring System Audit
**Objective:** Identify all 7 wiring systems

**Known Systems:**
1. Database-backed registry (cortex/orchestrators/core/database_registry.py)
2. YAML wiring (cortex/wiring/specifications/)
3. Legacy bootstrap (cortex/bootstrap.py)
4. Configuration wiring (cortex/config/)
5. MCP adapter wiring (cortex/mcp/adapters/)
6. Domain wiring (cortex_brain/domain/)
7. Test fixture wiring (tests/fixtures/)

**Phase 1 Task:** Catalog all 7 and mark for consolidation

---

## 🚀 Execution Methods

### Method 1: Full Automated Phase 1 (RECOMMENDED)
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
chmod +x _workspaces/docker-plan/migrate-to-docker-clean.sh

# DRY-RUN FIRST (see what would happen)
./migrate-to-docker-clean.sh --dry-run --phase 1

# If satisfied, execute Phase 1
./migrate-to-docker-clean.sh --phase 1
```

**Advantages:**
- Fully automated
- Generates complete reports
- Configurable (all options available)
- No manual steps

**Output:** Reports in `logs/migration-YYYYMMDD_HHMMSS.log`

### Method 2: Manual Phase 1 Steps
```bash
# 1. Analyze Python structure
cd /Users/asifhussain/PROJECTS/CORTEX
python3 << 'EOF'
import os
import ast

python_files = []
for root, dirs, files in os.walk('.'):
    # Skip __pycache__, .git, venv
    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', '.venv']]
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            python_files.append(path)

print(f"Total Python files: {len(python_files)}")
for f in sorted(python_files)[:20]:
    print(f"  {f}")
EOF

# 2. Test file inventory
find tests -name "test_*.py" | wc -l

# 3. Wiring system audit
find . -name "*wiring*" -o -name "*registry*" | grep -E "\.py$"
```

---

## 📊 Expected Phase 1 Outputs

The migration script will generate:

### 1. Component Inventory Report
```
components/
  ├── python_inventory.yaml
  ├── test_inventory.yaml
  ├── doc_inventory.yaml
  └── wiring_systems.yaml
```

### 2. Dependency Graph
```
dependency_graph/
  ├── import_chains.yaml
  ├── circular_dependencies.txt
  └── deletion_candidates.yaml
```

### 3. Analysis Report
```
phase1_report.txt
  - File counts (before/after)
  - Dependency analysis
  - Risk assessment
  - Deletion safety ratings
```

### 4. Git Diff Preview
```
migration_preview.diff
  - What would be deleted (preview)
  - Impact analysis
  - Rollback plan
```

---

## 🔍 Key Outputs to Review After Phase 1

### 1. Python File Reduction Plan
**Current:** 1,592 files → **Target:** ~500 files (68% reduction)

Expected breakdown:
- cortex/ core: ~300 files (keep)
- cortex_brain/ core: ~100 files (keep)
- cortex/ non-essential: ~800 files (DELETE)
- cortex_brain/ non-essential: ~200 files (DELETE)
- Legacy orchestrators: ~150 files (DELETE)
- Experimental features: ~42 files (DELETE)

### 2. Test File Reduction Plan
**Current:** 537 files → **Target:** ~200 files (63% reduction)

Expected breakdown:
- Core tests: ~120 files (keep)
- Integration tests: ~50 files (keep)
- Wiring tests: ~30 files (KEEP - essential for Docker migration)
- Non-applicable tests: ~337 files (DELETE)

### 3. Documentation Reduction Plan
**Current:** 753 files → **Target:** ~20 files (97% reduction)

Expected breakdown:
- Essential user docs: ~10 files (keep)
- Architecture docs: ~5 files (keep)
- API docs: ~5 files (keep)
- Legacy/draft docs: ~733 files (DELETE)

### 4. Wiring System Consolidation Plan
**Current:** 7 competing systems → **Target:** 1 system (Git-backed YAML)

System to keep:
- Git-backed YAML wiring (cortex/wiring/specifications/wiring.yaml)

Systems to remove:
- Database-backed registry (ephemeral only in Docker)
- Legacy bootstrap
- Config-based wiring
- MCP adapter wiring (restructured)
- Domain wiring (consolidated)
- Test fixture wiring (consolidated)

---

## ⏸️ Review Checkpoints in Phase 1

Phase 1 includes built-in checkpoints:

1. **After inventory (Hour 1):**
   - Review file counts and distribution
   - Verify no critical files in deletion candidates
   - Decision: Continue or adjust plan?

2. **After dependency analysis (Hour 2.5):**
   - Review import chains
   - Verify no critical circular dependencies
   - Decision: Continue or refactor dependencies first?

3. **After deletion plan generation (Hour 3.5):**
   - Review which files would be deleted
   - Verify safety ratings
   - Decision: Ready for Phase 2 (actual deletion)?

4. **Before completion (Hour 4):**
   - Final validation
   - Generate reports
   - Create Phase 1 checkpoint

---

## 🛡️ Safety Features Built Into Phase 1

✅ **No Code Changes Yet**
- Phase 1 is analysis-only
- No files are deleted
- No branches created
- No commits made

✅ **Rollback Available**
- Easy git checkout to undo any experiments
- Phase 0 checkpoint available at: `phase0-docker-plan-validation-20260127`

✅ **Dry-Run Available**
- Use `--dry-run` flag to preview everything
- See what would be done without actually doing it
- No risk of accidental changes

✅ **Logging**
- All Phase 1 steps logged to: `logs/migration-YYYYMMDD_HHMMSS.log`
- Review log after completion
- Upload to audit trail

---

## 📈 Success Criteria for Phase 1

Phase 1 is successful when:

- ✅ All 1,592 Python files analyzed
- ✅ All 537 test files categorized
- ✅ All 753 documentation files reviewed
- ✅ All 7 wiring systems identified
- ✅ Dependency graphs generated
- ✅ Deletion safety ratings assigned
- ✅ Rollback procedures documented
- ✅ Phase 1 checkpoint created
- ✅ Reports generated and validated

---

## 📝 Phase 1 Execution Checklist

Before starting Phase 1:

- [ ] Phase 0 checkpoint verified (`phase0-docker-plan-validation-20260127`)
- [ ] Git working tree clean
- [ ] Migration script executable
- [ ] Python dependencies available
- [ ] Sufficient disk space (~1-2 GB for analysis)
- [ ] Read this readiness guide
- [ ] Decided on: Full-automated vs. manual approach

**Start Phase 1 when:** All items above are checked ✅

---

## 🚀 Quick Start Commands

### Option A: Dry-Run (Safe Preview)
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
./migrate-to-docker-clean.sh --dry-run --phase 1
```

**Output:** See what would happen without making changes  
**Time:** 10-15 minutes  
**Risk:** ZERO ✅

### Option B: Execute Phase 1
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
./migrate-to-docker-clean.sh --phase 1
```

**Output:** Complete analysis + reports  
**Time:** 4 hours  
**Risk:** LOW ✅ (analysis-only, no deletion)

### Option C: Execute with Skip Tests
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
./migrate-to-docker-clean.sh --phase 1 --skip-tests
```

**Output:** Faster analysis (no test validation)  
**Time:** 2-3 hours  
**Risk:** MEDIUM ⚠️ (less thorough)

---

## 📞 Decision Point

**You are ready to start Phase 1 now.**

Would you like to:

1. **Run Phase 1 dry-run** - See preview (10-15 min, zero risk)
2. **Execute Phase 1 fully** - Complete analysis (4 hours)
3. **Review master plan first** - Take more time to plan
4. **Skip to Phase 2** - Start actual deletion (not recommended without Phase 1)

---

**Ready to proceed?** Use one of the quick-start commands above.

---

**Document:** CORTEX Docker-Plan Phase 1 Readiness  
**Generated:** 2026-01-27  
**Authority:** DeploymentOrchestrator  
**Status:** Ready for execution ✅
