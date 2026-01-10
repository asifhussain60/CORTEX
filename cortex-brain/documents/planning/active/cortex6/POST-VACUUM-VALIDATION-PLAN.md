# Post-Vacuum Validation Plan

**Date:** 2026-01-10  
**Status:** 🔍 READY FOR EXECUTION  
**Purpose:** Verify cortex6 folder integrity after vacuum cleanup and provide recovery protocol

---

## 🎯 Validation Objectives

1. ✅ Verify all critical files are accessible and readable
2. ✅ Confirm requirements folder is intact
3. ✅ Validate execution structure
4. ✅ Test navigation from primary documents
5. ✅ Confirm git remote has clean version
6. ⚠️ Provide recovery protocol if needed files were deleted

---

## 📋 Phase 1: Critical File Validation

### Requirements Folder Validation

```bash
cd /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/cortex6

# Test 1: Verify requirements files exist
echo "=== Test 1: Requirements Files ==="
ls -lh requirements/
test -f requirements/CX6-requirements.yaml && echo "✅ CX6-requirements.yaml exists" || echo "❌ MISSING"
test -f requirements/CX6-acceptance-criteria.yaml && echo "✅ CX6-acceptance-criteria.yaml exists" || echo "❌ MISSING"

# Test 2: Verify file sizes (should be 54KB and 304KB)
echo -e "\n=== Test 2: File Size Verification ==="
du -h requirements/CX6-requirements.yaml
du -h requirements/CX6-acceptance-criteria.yaml

# Test 3: Verify files are readable
echo -e "\n=== Test 3: File Readability ==="
head -5 requirements/CX6-requirements.yaml && echo "✅ CX6-requirements.yaml readable" || echo "❌ UNREADABLE"
head -5 requirements/CX6-acceptance-criteria.yaml && echo "✅ CX6-acceptance-criteria.yaml readable" || echo "❌ UNREADABLE"
```

**Expected Output:**
```
✅ CX6-requirements.yaml exists
✅ CX6-acceptance-criteria.yaml exists
54K requirements/CX6-requirements.yaml
304K requirements/CX6-acceptance-criteria.yaml
✅ CX6-requirements.yaml readable
✅ CX6-acceptance-criteria.yaml readable
```

---

### Master Plan Validation

```bash
# Test 4: Verify master plan exists
echo "=== Test 4: Master Plan ==="
test -f artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml && echo "✅ Master plan exists" || echo "❌ MISSING"

# Test 5: Verify plan readability
echo -e "\n=== Test 5: Plan Readability ==="
head -20 artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml && echo "✅ Master plan readable" || echo "❌ UNREADABLE"
```

**Expected Output:**
```
✅ Master plan exists
✅ Master plan readable
```

---

### Execution Structure Validation

```bash
# Test 6: Verify execution folder structure
echo "=== Test 6: Execution Structure ==="
test -d execution && echo "✅ execution/ exists" || echo "❌ MISSING"
test -f execution/README.md && echo "✅ execution/README.md exists" || echo "❌ MISSING"
test -f execution/config.yaml && echo "✅ execution/config.yaml exists" || echo "❌ MISSING"
test -f execution/plan-index.yaml && echo "✅ execution/plan-index.yaml exists" || echo "❌ MISSING"
test -d execution/dashboard && echo "✅ execution/dashboard/ exists" || echo "❌ MISSING"
test -d execution/phases && echo "✅ execution/phases/ exists" || echo "❌ MISSING"
test -d execution/tracking && echo "✅ execution/tracking/ exists" || echo "❌ MISSING"

# Test 7: Count execution files
echo -e "\n=== Test 7: Execution File Count ==="
find execution -type f | wc -l
```

**Expected Output:**
```
✅ execution/ exists
✅ execution/README.md exists
✅ execution/config.yaml exists
✅ execution/plan-index.yaml exists
✅ execution/dashboard/ exists
✅ execution/phases/ exists
✅ execution/tracking/ exists
(file count should be > 10)
```

---

### Navigation Document Validation

```bash
# Test 8: Verify navigation documents
echo "=== Test 8: Navigation Documents ==="
test -f 00-SOURCE-OF-TRUTH-README.md && echo "✅ 00-SOURCE-OF-TRUTH-README.md exists" || echo "❌ MISSING"
test -f 00-FOLDER-STRUCTURE-GUIDE.md && echo "✅ 00-FOLDER-STRUCTURE-GUIDE.md exists" || echo "❌ MISSING"
test -f QUICK-REFERENCE.md && echo "✅ QUICK-REFERENCE.md exists" || echo "❌ MISSING"

# Test 9: Verify navigation document readability
echo -e "\n=== Test 9: Navigation Readability ==="
head -10 00-SOURCE-OF-TRUTH-README.md && echo "✅ Source of truth readable" || echo "❌ UNREADABLE"
```

**Expected Output:**
```
✅ 00-SOURCE-OF-TRUTH-README.md exists
✅ 00-FOLDER-STRUCTURE-GUIDE.md exists
✅ QUICK-REFERENCE.md exists
✅ Source of truth readable
```

---

## 📋 Phase 2: Git Remote Verification

```bash
# Test 10: Verify git remote has vacuum commit
echo "=== Test 10: Git Remote Status ==="
cd /Users/asifhussain/PROJECTS/CORTEX
git log origin/CORTEX-5.5 --oneline -5 | grep "VACUUM"

# Test 11: Verify remote branch is up-to-date
echo -e "\n=== Test 11: Remote Sync Status ==="
git status | grep "up to date"

# Test 12: Pull from remote to verify no conflicts
echo -e "\n=== Test 12: Remote Pull Test ==="
git pull origin CORTEX-5.5 --dry-run
```

**Expected Output:**
```
✅ VACUUM commit found in remote log
✅ Branch up to date with remote
✅ No conflicts on pull
```

---

## 📋 Phase 3: Content Verification

```bash
# Test 13: Verify folder structure matches documented structure
echo "=== Test 13: Folder Structure Verification ==="
cd /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/cortex6
tree -L 2 -d

# Test 14: Count files in each directory
echo -e "\n=== Test 14: File Count by Directory ==="
echo "Root: $(ls -1 *.md 2>/dev/null | wc -l) markdown files"
echo "Requirements: $(ls -1 requirements/ 2>/dev/null | wc -l) files"
echo "Analysis: $(ls -1 analysis/ 2>/dev/null | wc -l) files"
echo "Artifacts: $(ls -1 artifacts/ 2>/dev/null | wc -l) files"
echo "Summaries: $(ls -1 summaries/ 2>/dev/null | wc -l) files"

# Test 15: Verify archive deletion
echo -e "\n=== Test 15: Archive Deletion Verification ==="
test ! -d archive && echo "✅ archive/ successfully deleted" || echo "❌ archive/ still exists"
```

**Expected Output:**
```
Root: 4 markdown files (including VACUUM-REPORT)
Requirements: 2 files
Analysis: 3 files
Artifacts: 1 files
Summaries: 7 files
✅ archive/ successfully deleted
```

---

## 📋 Phase 4: Functional Testing

```bash
# Test 16: Test plan viewer dashboard access
echo "=== Test 16: Dashboard Access ==="
test -f execution/dashboard/plan-viewer.html && echo "✅ Dashboard HTML exists" || echo "❌ MISSING"
test -x execution/dashboard/serve-dashboard.sh && echo "✅ Dashboard server script executable" || echo "❌ NOT EXECUTABLE"

# Test 17: Verify YAML parsing
echo -e "\n=== Test 17: YAML Validation ==="
python3 -c "import yaml; yaml.safe_load(open('requirements/CX6-requirements.yaml'))" && echo "✅ requirements YAML valid" || echo "❌ YAML INVALID"
python3 -c "import yaml; yaml.safe_load(open('requirements/CX6-acceptance-criteria.yaml'))" && echo "✅ acceptance criteria YAML valid" || echo "❌ YAML INVALID"
python3 -c "import yaml; yaml.safe_load(open('artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml'))" && echo "✅ master plan YAML valid" || echo "❌ YAML INVALID"
```

**Expected Output:**
```
✅ Dashboard HTML exists
✅ Dashboard server script executable
✅ requirements YAML valid
✅ acceptance criteria YAML valid
✅ master plan YAML valid
```

---

## ⚠️ Recovery Protocol (If Validation Fails)

### Scenario 1: Critical File Missing

If any critical file is missing (requirements, master plan, execution structure):

```bash
# Step 1: Check git history
cd /Users/asifhussain/PROJECTS/CORTEX
git log --all --full-history -- "cortex-brain/documents/planning/active/cortex6/<missing-file-path>"

# Step 2: Identify commit before deletion
git log --oneline --all -- "cortex-brain/documents/planning/active/cortex6/<missing-file-path>" | head -1

# Step 3: Restore specific file
git checkout <commit-hash> -- "cortex-brain/documents/planning/active/cortex6/<missing-file-path>"

# Step 4: Commit restoration
git add "cortex-brain/documents/planning/active/cortex6/<missing-file-path>"
git commit -m "🔧 RESTORE: Recover critical file <filename>"
git push origin CORTEX-5.5
```

### Scenario 2: Requirements Folder Corrupted

```bash
# Restore entire requirements folder from git
cd /Users/asifhussain/PROJECTS/CORTEX
git log --oneline -- "cortex-brain/documents/planning/active/cortex6/requirements/" | head -5

# Find commit before vacuum (should be before 3f9b037b4)
git checkout 757788305 -- "cortex-brain/documents/planning/active/cortex6/requirements/"

# Commit restoration
git add cortex-brain/documents/planning/active/cortex6/requirements/
git commit -m "🔧 RESTORE: Recover requirements folder"
git push origin CORTEX-5.5
```

### Scenario 3: Execution Structure Missing

```bash
# Pull execution structure from remote
cd /Users/asifhussain/PROJECTS/CORTEX
git fetch origin CORTEX-5.5
git checkout origin/CORTEX-5.5 -- "cortex-brain/documents/planning/active/cortex6/execution/"

# If remote doesn't have it, restore from previous commit
git log --oneline -- "cortex-brain/documents/planning/active/cortex6/execution/" | head -5
git checkout <commit-hash> -- "cortex-brain/documents/planning/active/cortex6/execution/"

# Commit restoration
git add cortex-brain/documents/planning/active/cortex6/execution/
git commit -m "🔧 RESTORE: Recover execution folder"
git push origin CORTEX-5.5
```

### Scenario 4: Complete Folder Restoration

If validation completely fails and full restoration is needed:

```bash
# Nuclear option: restore entire cortex6 folder from commit before vacuum
cd /Users/asifhussain/PROJECTS/CORTEX

# Identify commit before vacuum (757788305 is before 3f9b037b4)
git log --oneline CORTEX-5.5 | grep -B 1 "VACUUM"

# Restore entire folder
git checkout 757788305 -- "cortex-brain/documents/planning/active/cortex6/"

# Review what was restored
git status

# Commit full restoration
git add cortex-brain/documents/planning/active/cortex6/
git commit -m "🔧 RESTORE: Full cortex6 folder restoration from pre-vacuum state"
git push origin CORTEX-5.5
```

---

## 📊 Validation Checklist

Run all validation commands and check off:

- [ ] **Test 1:** Requirements files exist
- [ ] **Test 2:** File sizes correct (54KB, 304KB)
- [ ] **Test 3:** Files readable
- [ ] **Test 4:** Master plan exists
- [ ] **Test 5:** Plan readable
- [ ] **Test 6:** Execution structure complete
- [ ] **Test 7:** Execution file count > 10
- [ ] **Test 8:** Navigation documents exist
- [ ] **Test 9:** Navigation readable
- [ ] **Test 10:** VACUUM commit in remote
- [ ] **Test 11:** Branch synced
- [ ] **Test 12:** No pull conflicts
- [ ] **Test 13:** Folder structure matches
- [ ] **Test 14:** File counts match expected
- [ ] **Test 15:** Archive deleted
- [ ] **Test 16:** Dashboard accessible
- [ ] **Test 17:** YAML files valid

---

## 🎯 Success Criteria

**Validation PASSES if:**
- ✅ All 17 tests pass
- ✅ Requirements folder intact (2 files, 358KB total)
- ✅ Master plan accessible
- ✅ Execution structure complete
- ✅ Navigation documents readable
- ✅ Git remote synced
- ✅ No YAML parsing errors

**Validation FAILS if:**
- ❌ Any critical file missing (requirements, master plan)
- ❌ Execution structure incomplete
- ❌ YAML files unparseable
- ❌ Git remote out of sync

---

## 🚀 Next Steps After Validation

### If Validation PASSES:
1. ✅ Mark vacuum operation as complete
2. ✅ Update CORTEX 6.0 progress tracker
3. ✅ Proceed with epic execution
4. ✅ Archive this validation plan

### If Validation FAILS:
1. ⚠️ Execute recovery protocol (see Scenario 1-4 above)
2. ⚠️ Re-run validation tests
3. ⚠️ Document what went wrong
4. ⚠️ Update vacuum procedures for future operations

---

## 📝 Validation Execution Log

**Date:** ___________  
**Executor:** ___________  
**Time Taken:** ___________  

**Results:**
```
Test 1:  [ PASS / FAIL ]
Test 2:  [ PASS / FAIL ]
Test 3:  [ PASS / FAIL ]
Test 4:  [ PASS / FAIL ]
Test 5:  [ PASS / FAIL ]
Test 6:  [ PASS / FAIL ]
Test 7:  [ PASS / FAIL ]
Test 8:  [ PASS / FAIL ]
Test 9:  [ PASS / FAIL ]
Test 10: [ PASS / FAIL ]
Test 11: [ PASS / FAIL ]
Test 12: [ PASS / FAIL ]
Test 13: [ PASS / FAIL ]
Test 14: [ PASS / FAIL ]
Test 15: [ PASS / FAIL ]
Test 16: [ PASS / FAIL ]
Test 17: [ PASS / FAIL ]
```

**Overall Status:** [ PASS / FAIL ]  
**Recovery Actions Taken:** ___________  
**Notes:** ___________

---

**Validation Plan Created:** 2026-01-10  
**Git Commit Reference:** 3f9b037b4 (VACUUM commit)  
**Previous Commit:** 757788305 (pre-vacuum state)
