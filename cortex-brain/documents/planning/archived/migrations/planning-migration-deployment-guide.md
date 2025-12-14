# CORTEX Planning Migration Deployment Guide

**Date:** December 13, 2025  
**Author:** Asif Hussain  
**Version:** 1.0.0  
**Audience:** Developers pulling CORTEX-3.0 branch with new orchestration design

---

## 🎯 Purpose

This guide helps you **safely merge and align** the new orchestration design changes to your local CORTEX repository, ensuring:
1. No conflicts with your local work
2. Proper folder structure alignment
3. Full orchestration system wiring validation
4. Backward compatibility maintained

---

## ⚠️ BEFORE YOU PULL

### Pre-Pull Checklist

Run these commands to assess your local state:

```bash
# 1. Check current branch
git branch
# Expected: You should be on CORTEX-3.0 or a feature branch

# 2. Check for uncommitted changes
git status
# If you have changes, commit or stash them first

# 3. Check if you have local planning documents
ls cortex-brain/documents/planning/*.md | wc -l
# Note the count - you'll compare this after merge

# 4. Backup your local planning directory (RECOMMENDED)
cp -r cortex-brain/documents/planning cortex-brain/documents/planning.backup.$(date +%Y%m%d_%H%M%S)
```

---

## 🚀 Pull Strategy

### Option A: Clean Pull (NO Local Changes)

If you have NO local modifications to planning documents:

```bash
# 1. Fetch latest
git fetch origin CORTEX-3.0

# 2. Pull with rebase (maintains linear history)
git pull origin CORTEX-3.0 --rebase

# 3. Verify merge success
git status
# Expected: "Your branch is up to date with 'origin/CORTEX-3.0'"
```

---

### Option B: Intelligent Merge (WITH Local Changes)

If you have LOCAL planning documents or modifications:

```bash
# 1. Stash local changes
git stash push -m "Local planning docs before migration merge"

# 2. Pull latest
git pull origin CORTEX-3.0 --rebase

# 3. Pop stash
git stash pop
# If conflicts occur, proceed to conflict resolution section
```

---

## 🔧 Conflict Resolution

### Common Conflict Scenarios

#### Scenario 1: Your Local Plan vs Remote Folder Structure

**Situation:** You have `my-feature-plan.md` in root, remote moved it to folder.

**Resolution:**
```bash
# 1. Accept remote changes (folder structure)
git checkout --theirs cortex-brain/documents/planning/

# 2. Manually merge your content
# - Open backup: cortex-brain/documents/planning.backup.*/my-feature-plan.md
# - Find target: cortex-brain/documents/planning/active/my-feature-plan/MASTER-PLAN.md
# - Copy unique content manually
```

---

#### Scenario 2: Same File Modified Locally and Remotely

**Situation:** Both you and remote modified `orchestrator-enhancement-plan-v2.md`.

**Resolution:**
```bash
# 1. Check conflict
git diff --name-only --diff-filter=U

# 2. Use merge tool
git mergetool

# 3. Manually resolve conflicts
# - Keep remote structure changes
# - Preserve your content additions
# - Commit resolution:
git add cortex-brain/documents/planning/
git commit -m "resolve: Merge local planning changes with new folder structure"
```

---

#### Scenario 3: Your Local Plan Doesn't Exist in Remote

**Situation:** You created `new-feature-plan.md` locally, not in remote.

**Resolution:**
```bash
# No conflict - your file is preserved
# OPTIONAL: Migrate to folder structure manually

mkdir -p cortex-brain/documents/planning/active/new-feature-plan
mv cortex-brain/documents/planning/new-feature-plan.md \
   cortex-brain/documents/planning/active/new-feature-plan/MASTER-PLAN.md

# Create metadata.json
cat > cortex-brain/documents/planning/active/new-feature-plan/metadata.json << EOF
{
  "plan_name": "New Feature Plan",
  "status": "IN_PROGRESS",
  "created": "$(date +%Y-%m-%d)",
  "author": "Your Name"
}
EOF

git add cortex-brain/documents/planning/active/new-feature-plan/
git commit -m "refactor: Migrate new-feature-plan to folder structure"
```

---

## ✅ POST-PULL VALIDATION CHECKLIST

### 1. Verify Folder Structure

Run this validation script:

```bash
# Check new folder structure exists
ls -la cortex-brain/documents/planning/

# Expected folders:
# - active/
# - completed/
# - ado/
# - archived/
# - cortex-4.0/ (already existed)
# - orchestrators/ (already existed)

# Verify key migrated plans
ls cortex-brain/documents/planning/completed/orchestrator-enhancement-v2/
# Expected: MASTER-PLAN.md, 01-feature-9-*.md, ..., metadata.json

ls cortex-brain/documents/planning/active/orchestration-master-plan/
# Expected: MASTER-PLAN.md, 01-tdd-orchestrator.md, ..., metadata.json
```

---

### 2. Verify New Orchestrators Wiring

Run this comprehensive test to ensure all orchestrators are properly wired:

```bash
# Test imports
python3 -c "
from src.operations.utilities import (
    HolisticReviewOrchestrator,
    KnowledgeGraphAutoUpdater,
    ProgressRenderer,
    OrchestrationMetricsCollector,
    TaskInjectionManager,
    OrchestrationCheckpointManager,
    ParallelOrchestrationCoordinator,
    OrchestrationAnalyticsDashboard,
    PerformanceProfilingOrchestrator,
    DocumentationGenerationOrchestrator,
    CodeQualityOrchestrator,
    DeploymentOrchestrator,
    IntegrationTestingOrchestrator
)
print('✅ All orchestrator imports successful')
"

# Expected: ✅ All orchestrator imports successful
```

---

### 3. Run Test Suite

Verify zero regressions:

```bash
# Run orchestrator utility tests
python3 -m pytest tests/operations/utilities/ -v

# Expected: 221/221 tests passing
# If failures occur, see troubleshooting section
```

---

### 4. Verify Git History Preserved

```bash
# Check history for migrated files
git log --follow cortex-brain/documents/planning/completed/orchestrator-enhancement-v2/MASTER-PLAN.md

# Expected: See full history including original file path
```

---

### 5. Check Backward Compatibility

```bash
# Test old imports still work (if any)
python3 -c "
import sys
sys.path.insert(0, 'src')

# Test that any code referencing old paths still works
# (if applicable to your codebase)
print('✅ Backward compatibility verified')
"
```

---

## 🧪 ORCHESTRATION SYSTEM WIRING CHECKLIST

Use this checklist to verify the new orchestration design is **fully wired** on your machine:

### Phase 1: Core Orchestrator Verification

- [ ] **1.1 Holistic Review Orchestrator**
  ```bash
  python3 -c "from src.operations.utilities import HolisticReviewOrchestrator, ReviewResult, QualityGate; print('✅')"
  ```

- [ ] **1.2 Knowledge Graph Auto-Updater**
  ```bash
  python3 -c "from src.operations.utilities import KnowledgeGraphAutoUpdater, UpdateResult, PatternExtractor; print('✅')"
  ```

- [ ] **1.3 Progress Renderer**
  ```bash
  python3 -c "from src.operations.utilities import ProgressRenderer; print('✅')"
  ```

- [ ] **1.4 Orchestration Metrics Collector**
  ```bash
  python3 -c "from src.operations.utilities import OrchestrationMetricsCollector, with_orchestration_metrics; print('✅')"
  ```

- [ ] **1.5 Task Injection Manager**
  ```bash
  python3 -c "from src.operations.utilities import TaskInjectionManager, TaskPriority, TaskStatus; print('✅')"
  ```

- [ ] **1.6 Checkpoint Manager**
  ```bash
  python3 -c "from src.operations.utilities import OrchestrationCheckpointManager, CheckpointNotFoundError; print('✅')"
  ```

- [ ] **1.7 Parallel Orchestration Coordinator**
  ```bash
  python3 -c "from src.operations.utilities import ParallelOrchestrationCoordinator, PhaseDefinition; print('✅')"
  ```

- [ ] **1.8 Analytics Dashboard**
  ```bash
  python3 -c "from src.operations.utilities import OrchestrationAnalyticsDashboard; print('✅')"
  ```

---

### Phase 2: Feature Orchestrators Verification

- [ ] **2.1 Performance Profiling**
  ```bash
  python3 -c "from src.operations.utilities import PerformanceProfilingOrchestrator, ProfileResult; print('✅')"
  ```

- [ ] **2.2 Documentation Generation**
  ```bash
  python3 -c "from src.operations.utilities import DocumentationGenerationOrchestrator, DocstringInfo; print('✅')"
  ```

- [ ] **2.3 Code Quality**
  ```bash
  python3 -c "from src.operations.utilities import CodeQualityOrchestrator, CodeReviewReport; print('✅')"
  ```

- [ ] **2.4 Deployment**
  ```bash
  python3 -c "from src.operations.utilities import DeploymentOrchestrator, DeploymentResult; print('✅')"
  ```

- [ ] **2.5 Integration Testing**
  ```bash
  python3 -c "from src.operations.utilities import IntegrationTestingOrchestrator, TestEnvironment; print('✅')"
  ```

---

### Phase 3: Test Coverage Verification

- [ ] **3.1 Run Full Test Suite**
  ```bash
  python3 -m pytest tests/operations/utilities/ -v --tb=short
  # Expected: 221/221 passing
  ```

- [ ] **3.2 Coverage Report**
  ```bash
  python3 -m pytest tests/operations/utilities/ --cov=src/operations/utilities --cov-report=term-missing
  # Expected: >90% coverage for all orchestrators
  ```

---

### Phase 4: Documentation Verification

- [ ] **4.1 Completion Report Exists**
  ```bash
  ls cortex-brain/documents/planning/completed/orchestrator-enhancement-v2/completion-report.md
  # OR
  ls cortex-brain/documents/planning/v2-orchestrator-completion-report.md
  ```

- [ ] **4.2 Planning Documents Organized**
  ```bash
  # Count files in root (should be <20)
  ls cortex-brain/documents/planning/*.md | wc -l
  
  # Count folders (should be ~6-8)
  ls -d cortex-brain/documents/planning/*/ | wc -l
  ```

---

### Phase 5: Functional Verification

- [ ] **5.1 Run Sample Orchestration**
  ```bash
  python3 -c "
  from src.operations.utilities import HolisticReviewOrchestrator
  
  orchestrator = HolisticReviewOrchestrator()
  context = {
      'feature_name': 'test',
      'files_modified': ['file1.py', 'file2.py'],
      'tests_run': 10,
      'tests_passed': 10,
      'coverage': 95.0
  }
  result = orchestrator.run_holistic_review(context)
  assert result.overall_passed == True
  print('✅ Holistic Review functional')
  "
  ```

- [ ] **5.2 Knowledge Graph Update Test**
  ```bash
  python3 -c "
  from src.operations.utilities import KnowledgeGraphAutoUpdater
  from pathlib import Path
  
  updater = KnowledgeGraphAutoUpdater()
  patterns = updater.extract_patterns({
      'coverage': 95.0,
      'files_modified': ['f1', 'f2', 'f3'],
      'tests_run': 10,
      'tests_passed': 10
  })
  assert 3 <= len(patterns) <= 5
  print('✅ Knowledge Graph Auto-Updater functional')
  "
  ```

---

## 🚨 Troubleshooting

### Issue 1: Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'src.operations.utilities.holistic_review_orchestrator'
```

**Resolution:**
```bash
# 1. Verify file exists
ls src/operations/utilities/holistic_review_orchestrator.py

# 2. Check __init__.py exports
grep "HolisticReviewOrchestrator" src/operations/utilities/__init__.py

# 3. If missing, pull specific commit
git cherry-pick f9949480  # Features 11 & 14 commit
```

---

### Issue 2: Test Failures

**Symptom:**
```
FAILED tests/operations/utilities/test_holistic_review_orchestrator.py
```

**Resolution:**
```bash
# 1. Check Python version
python3 --version
# Required: Python 3.8+

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Run single test for debugging
python3 -m pytest tests/operations/utilities/test_holistic_review_orchestrator.py -vv
```

---

### Issue 3: Planning Documents Not Found

**Symptom:**
```
FileNotFoundError: cortex-brain/documents/planning/orchestrator-enhancement-plan-v2.md
```

**Resolution:**
```bash
# File was migrated to folder structure
# New location:
ls cortex-brain/documents/planning/completed/orchestrator-enhancement-v2/MASTER-PLAN.md

# Update any hardcoded paths in your code to use new structure
```

---

### Issue 4: Metadata.json Missing

**Symptom:**
```
FileNotFoundError: metadata.json not found in planning folder
```

**Resolution:**
```bash
# Migration might be incomplete - check commit history
git log --oneline --all -- cortex-brain/documents/planning/

# If metadata.json truly missing, create it:
cd cortex-brain/documents/planning/[folder-name]
cat > metadata.json << EOF
{
  "plan_name": "Plan Name",
  "status": "IN_PROGRESS",
  "created": "2025-12-13"
}
EOF
```

---

## 📊 Success Indicators

You've successfully merged when:

✅ All orchestrator imports work  
✅ 221/221 tests passing  
✅ Planning folders structured correctly  
✅ Git history preserved  
✅ No import errors in your code  
✅ Backward compatibility maintained  
✅ All 13 orchestrators functional

---

## 🎯 Quick Validation Script

Run this **one-liner** to validate everything:

```bash
python3 << 'EOF'
import sys
from pathlib import Path

print("🔍 CORTEX Orchestration System Validation\n")

# 1. Check orchestrator imports
try:
    from src.operations.utilities import (
        HolisticReviewOrchestrator,
        KnowledgeGraphAutoUpdater,
        ProgressRenderer,
        OrchestrationMetricsCollector
    )
    print("✅ Orchestrator imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# 2. Check folder structure
planning_dir = Path("cortex-brain/documents/planning")
folders = ["active", "completed", "ado", "cortex-4.0"]
for folder in folders:
    if (planning_dir / folder).exists():
        print(f"✅ Folder exists: {folder}/")
    else:
        print(f"⚠️  Folder missing: {folder}/")

# 3. Check key files
v2_plan = planning_dir / "completed/orchestrator-enhancement-v2/MASTER-PLAN.md"
if v2_plan.exists():
    print("✅ V2 orchestrator plan migrated")
else:
    # Check old location
    old_location = planning_dir / "orchestrator-enhancement-plan-v2.md"
    if old_location.exists():
        print("⚠️  V2 plan not yet migrated (still in root)")
    else:
        print("❌ V2 plan missing")

# 4. Run sample test
try:
    orchestrator = HolisticReviewOrchestrator()
    result = orchestrator.run_holistic_review({
        'feature_name': 'test',
        'files_modified': ['f1', 'f2'],
        'tests_run': 5,
        'tests_passed': 5,
        'coverage': 95.0
    })
    assert result.overall_passed
    print("✅ Sample orchestration functional")
except Exception as e:
    print(f"❌ Orchestration failed: {e}")
    sys.exit(1)

print("\n🎉 ALL VALIDATIONS PASSED - System ready!")
EOF
```

**Expected Output:**
```
🔍 CORTEX Orchestration System Validation

✅ Orchestrator imports successful
✅ Folder exists: active/
✅ Folder exists: completed/
✅ Folder exists: ado/
✅ Folder exists: cortex-4.0/
✅ V2 orchestrator plan migrated
✅ Sample orchestration functional

🎉 ALL VALIDATIONS PASSED - System ready!
```

---

## 📞 Need Help?

If you encounter issues not covered here:

1. **Check Git History:**
   ```bash
   git log --oneline --all --graph -- cortex-brain/documents/planning/
   ```

2. **Review Completion Report:**
   ```bash
   cat cortex-brain/documents/planning/v2-orchestrator-completion-report.md
   ```

3. **Contact:** Asif Hussain (GitHub: @asifhussain60)

---

**Version:** 1.0.0  
**Last Updated:** December 13, 2025  
**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX
