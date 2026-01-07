# CORTEX-5.5 Migration Checklist

**Purpose:** Pre-flight checklist before executing migration  
**Version:** 1.0.0  
**Date:** 2026-01-06

---

## ✅ Pre-Migration Checklist

### Environment Validation

- [ ] **Working directory is CORTEX root**
  ```powershell
  pwd  # Should show: D:\PROJECTS\CORTEX
  ```

- [ ] **Git repository is clean**
  ```powershell
  git status  # Should show "nothing to commit, working tree clean"
  ```

- [ ] **PowerShell version is 7+**
  ```powershell
  $PSVersionTable.PSVersion  # Should be 7.x or higher
  ```

- [ ] **Latest CORTEX-5.0 fetched**
  ```powershell
  git checkout CORTEX-5.0
  git pull origin CORTEX-5.0
  ```

- [ ] **Latest main fetched**
  ```powershell
  git checkout main
  git pull origin main
  ```

- [ ] **CORTEX-5.5 branch does not exist** (or willing to delete)
  ```powershell
  git branch --list CORTEX-5.5  # Should be empty or OK to delete
  ```

---

## 📋 Document Review Checklist

- [ ] **MIGRATION-SUMMARY.md** - Executive summary reviewed
- [ ] **CORTEX-5.5-MIGRATION-STRATEGY.md** - Full strategy understood
- [ ] **CORTEX-5.5-EXECUTION-GUIDE.md** - Execution steps clear
- [ ] **00-cortex5-epic.md** - Epic plan with CORTEX-5.0 reference strategy reviewed
- [ ] **create-cortex-5.5-branch.ps1** - Automation script reviewed
- [ ] **pull-from-cortex-5.0.ps1** - Pull tracking system understood

---

## 🚀 Migration Execution Checklist

### Step 1: Run Migration Script

- [ ] **Script executed successfully**
  ```powershell
  .\create-cortex-5.5-branch.ps1
  ```

- [ ] **All 8 steps completed without errors**
  - [ ] Step 1: Environment validated
  - [ ] Step 2: Latest fetched
  - [ ] Step 3: Branch created from main
  - [ ] Step 4: Directory structure created (19 dirs)
  - [ ] Step 5: Essential files copied (~50 files)
  - [ ] Step 6: Epic plan copied
  - [ ] Step 7: Source code copied
  - [ ] Step 8: Phase 1 scaffolding created

### Step 2: Validate Branch

- [ ] **Branch exists and is checked out**
  ```powershell
  git branch  # Should show * CORTEX-5.5
  ```

- [ ] **File count is ~150-180**
  ```powershell
  (git ls-files | Measure-Object).Count  # Should be ~150-180
  ```

- [ ] **Essential files exist**
  - [ ] `src/main.py`
  - [ ] `cortex-brain/brain-protection-rules.yaml`
  - [ ] `src/knowledge/company_knowledge_provider.py`
  - [ ] `.github/prompts/CORTEX.prompt.md`
  - [ ] `cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md`

- [ ] **Phase 1 scaffolding exists**
  - [ ] `src/knowledge/__init__.py`
  - [ ] `src/knowledge/company_knowledge_provider.py`
  - [ ] `src/knowledge/knowledge_merger.py`
  - [ ] `cortex-brain/tier2/company-knowledge/sample_company/architecture.md`
  - [ ] `cortex-brain/tier2/company-knowledge/sample_company/tech-stack.yaml`

- [ ] **Pull tracking system exists**
  - [ ] `pull-from-cortex-5.0.ps1`
  - [ ] `tracking/pulls-from-cortex-5.0.json`

### Step 3: Validate Code

- [ ] **Python syntax check passes**
  ```powershell
  Get-ChildItem -Path "src" -Filter "*.py" -Recurse | ForEach-Object {
      python -m py_compile $_.FullName
  }
  # Should complete without syntax errors
  ```

- [ ] **Requirements file is minimal**
  ```powershell
  Get-Content requirements.txt
  # Should have ~10 core dependencies (not 50+)
  ```

### Step 4: Commit and Push

- [ ] **Changes staged**
  ```powershell
  git add .
  git status  # Should show ~150 files staged
  ```

- [ ] **Commit created with epic reference**
  ```powershell
  git commit -m "feat: Initialize CORTEX-5.5 clean branch with Phase 1 scaffolding

- Essential files only (85% reduction vs CORTEX-5.0)
- Pull from CORTEX-5.0 on demand via pull-from-cortex-5.0.ps1
- Phase 1: Knowledge Extension Layer ready for execution
- Zero technical debt carried forward
- See: cortex-brain/documents/planning/active/cortex5-enhancement-epic/CORTEX-5.5-MIGRATION-STRATEGY.md

Epic: cortex5-enhancement-epic-v2
Phase: 0 (Foundation)"
  ```

- [ ] **Branch pushed to remote**
  ```powershell
  git push -u origin CORTEX-5.5
  ```

---

## ✅ Post-Migration Validation Checklist

### Branch Validation

- [ ] **Branch visible on GitHub**
  - Visit: https://github.com/asifhussain60/CORTEX/tree/CORTEX-5.5

- [ ] **File count is 85% reduction**
  - CORTEX-5.0: ~1000 files
  - CORTEX-5.5: ~150 files
  - Reduction: ~85%

- [ ] **No obsolete files present**
  - [ ] No `cortex_3_0/` directory
  - [ ] No `orchestration_4_0/` directory
  - [ ] No `cortex-sample-apps/` directory
  - [ ] No `backups/` directory
  - [ ] No `docs/` directory (historical)

### Epic Readiness

- [ ] **Epic plan accessible**
  ```powershell
  code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md"
  ```

- [ ] **Phase 1 guide accessible**
  ```powershell
  code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/phases/phase-01-knowledge-extension.md"
  ```

- [ ] **CORTEX-5.0 reference strategy documented**
  - Section in `00-cortex5-epic.md`: "🔄 CORTEX-5.0 Reference Strategy"

- [ ] **Pull tracking system initialized**
  - `tracking/pulls-from-cortex-5.0.json` exists
  - `pull_budget.current_pull_count` = 0
  - `pull_budget.remaining_pulls` = 20

---

## 🎯 Success Criteria Validation

### Migration Success

- [ ] ✅ **Branch Created:** CORTEX-5.5 exists from main base
- [ ] ✅ **File Reduction:** 85% (from ~1000 to ~150 files)
- [ ] ✅ **Phase 1 Ready:** src/knowledge/ scaffolding created
- [ ] ✅ **Epic Accessible:** cortex5-enhancement-epic plan available
- [ ] ✅ **Pull System:** Scripts and tracking in place
- [ ] ✅ **Zero Debt:** No obsolete/orphaned code carried forward

### Code Quality

- [ ] ✅ **No Syntax Errors:** All Python files compile
- [ ] ✅ **Minimal Dependencies:** requirements.txt has ~10 core deps
- [ ] ✅ **Clear Structure:** 19 directories with clear purpose
- [ ] ✅ **Documentation:** All migration docs present

---

## 🚦 Go/No-Go Decision

### GO Criteria (All Must Be True)

- [ ] All pre-migration checks passed
- [ ] Migration script executed successfully
- [ ] Branch validated (file count, structure, code)
- [ ] Commit pushed to remote
- [ ] Epic plan accessible and reviewed
- [ ] Pull tracking system operational

### NO-GO Criteria (Any Triggers Stop)

- [ ] Migration script failed with errors
- [ ] File count >200 (not enough reduction)
- [ ] Python syntax errors in essential files
- [ ] Essential files missing (main.py, brain-protection-rules.yaml, etc.)
- [ ] Epic plan not accessible

---

## 📝 Decision Record

**Date:** _____________  
**Decision:** ☐ GO  ☐ NO-GO  
**Approved By:** _____________  
**Notes:**

---

---

## 🎉 Next Steps (After GO Decision)

1. [ ] **Open Phase 1 Implementation Guide**
   ```powershell
   code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/phases/phase-01-knowledge-extension.md"
   ```

2. [ ] **Set up development environment**
   ```powershell
   pip install -r requirements.txt
   ```

3. [ ] **Start TDD Cycle**
   - [ ] Write failing test for `CompanyKnowledgeProvider.query_architecture()`
   - [ ] Implement minimal code to pass
   - [ ] Refactor while keeping tests green
   - [ ] Repeat for other methods

4. [ ] **Track Progress**
   ```powershell
   code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/tracking/progress-tracker.json"
   # Update after each task completion
   ```

5. [ ] **Update Epic Status**
   - [ ] Change status in `00-cortex5-epic.md` from "NOT STARTED" to "IN PROGRESS"
   - [ ] Update `tracking/progress-tracker.json`: phase 1 status = "IN_PROGRESS"

---

## 🆘 Rollback Plan (If NO-GO)

If migration fails or GO criteria not met:

```powershell
# 1. Delete CORTEX-5.5 branch (local)
git branch -D CORTEX-5.5

# 2. Delete CORTEX-5.5 branch (remote, if pushed)
git push origin --delete CORTEX-5.5

# 3. Return to CORTEX-5.0
git checkout CORTEX-5.0

# 4. Review errors and retry
# - Fix script issues
# - Adjust essential file manifest
# - Re-run migration
```

---

**Checklist Version:** 1.0.0  
**Last Updated:** 2026-01-06  
**Maintained By:** CORTEX Planning System v5
