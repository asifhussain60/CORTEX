# GAP-7: Incorrect Plan File Locations

**Date:** 2026-01-06  
**Priority:** P0_CRITICAL  
**Impact:** HIGH  
**Effort:** LOW (0.5 days)

---

## 🎯 Problem Statement

Files and directories are being created at the **root** of `cortex-brain/documents/planning/active/` instead of within properly named plan folders. This violates CORTEX's organizational structure and creates clutter.

---

## 🔍 Evidence

### Incorrectly Placed Files (Root Level)

```bash
cortex-brain/documents/planning/active/
├── plan-consolidation-cleanup.md         ❌ WRONG - Should be in a folder
├── CONSOLIDATION-COMPLETE.md             ❌ WRONG - Should be in a folder
```

### Orphaned/Unwanted Plan Directories

These were created due to GAP-1 (Continuation Context Loss) when user tried to continue the epic:

```bash
cortex-brain/documents/planning/active/
├── a19-continue-with-next/               ❌ DELETE - Continuation failure artifact
├── a19-proceed-with-epic/                ❌ DELETE - Continuation failure artifact
├── a19-analyze-autono-execut/            ❌ DELETE - Continuation failure artifact
├── a19-integr-p03-autono/                ❌ DELETE - Continuation failure artifact
├── a19-feature-test-valid/               ❌ DELETE - Test artifact
├── plan-1c439c7b-9f1c-4955-a7e3-b45f21cea8a6/  ❌ DELETE - Orphaned plan
├── plan-1a915241-5e7a-4086-86b4-833f391abe69/  ❌ DELETE - Orphaned plan
├── plan-cac4594d-b8be-4aed-a89f-09567029e9af/  ❌ DELETE - Orphaned plan
├── plan-24ac2aec-664b-4595-87f5-362d30ff77ce/  ❌ DELETE - Orphaned plan
├── plan-3051c6e4-0318-43f6-a70c-900d6f85f02b/  ❌ DELETE - "analyze-autonomous" plan
├── plan-ac6b0bcf-86f3-49fe-b28c-4b9a9c6dab89/  ❌ DELETE - "integrate-p03" plan
```

### Valid Plans (Keep These)

```bash
cortex-brain/documents/planning/active/
├── cortex-v5-remediation-epic/           ✅ VALID - Main epic
├── enterprise-python-audit-logger-with-self-healing/  ✅ VALID - Completed plan
```

---

## 🐛 Root Causes

### Cause 1: Missing Validation in Planning Orchestrator

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`

The Planning Orchestrator creates folders correctly (lines 481, 665, 854, etc.) but doesn't prevent:
1. Creating files at root level
2. Creating plans when continuation should be used
3. Validating folder structure before creation

### Cause 2: GAP-1 Continuation Context Loss

When users say "continue with next epic phase", the system creates NEW plans with names like:
- `a19-continue-with-next` (should have continued cortex-v5-remediation-epic)
- `a19-proceed-with-epic` (should have continued cortex-v5-remediation-epic)
- `a19-analyze-autono-execut` (should have added to existing epic)

This is the **symptom** of GAP-1 that we already identified.

### Cause 3: Manual File Creation

The files `plan-consolidation-cleanup.md` and `CONSOLIDATION-COMPLETE.md` were likely created manually or by a legacy script that doesn't follow the folder structure convention.

---

## 🎯 Comprehensive Fix Strategy

### Fix 1: Immediate Cleanup (0.5 hours)

**Delete orphaned plans and misplaced files:**

```bash
# Backup first (optional)
mkdir -p cortex-brain/archives/planning/cleanup-2026-01-06

# Move orphaned plans to archive
mv cortex-brain/documents/planning/active/a19-continue-with-next \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/a19-proceed-with-epic \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/a19-analyze-autono-execut \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/a19-integr-p03-autono \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/a19-feature-test-valid \
   cortex-brain/archives/planning/cleanup-2026-01-06/

# Move orphaned UUID plans
mv cortex-brain/documents/planning/active/plan-1c439c7b-* \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/plan-1a915241-* \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/plan-cac4594d-* \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/plan-24ac2aec-* \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/plan-3051c6e4-* \
   cortex-brain/archives/planning/cleanup-2026-01-06/

mv cortex-brain/documents/planning/active/plan-ac6b0bcf-* \
   cortex-brain/archives/planning/cleanup-2026-01-06/

# Move misplaced files to appropriate locations
# (These could be moved into a consolidation plan folder if needed)
mv cortex-brain/documents/planning/active/plan-consolidation-cleanup.md \
   cortex-brain/documents/planning/completed/

mv cortex-brain/documents/planning/active/CONSOLIDATION-COMPLETE.md \
   cortex-brain/documents/planning/completed/
```

### Fix 2: Add Validation Middleware (2 hours)

**Create:** `src/orchestrators/planning/validation/folder_structure_validator.py`

```python
"""
Planning Folder Structure Validator
Ensures all plans follow CORTEX organizational standards.
"""

from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FolderStructureValidator:
    """Validates and enforces proper planning folder structure."""
    
    ACTIVE_DIR = Path("cortex-brain/documents/planning/active")
    ARCHIVE_DIR = Path("cortex-brain/archives/planning")
    COMPLETED_DIR = Path("cortex-brain/documents/planning/completed")
    
    REQUIRED_PLAN_FOLDERS = [
        "context",
        "analysis",
        "artifacts",
        "reports",
        "tracking"
    ]
    
    def __init__(self):
        self.active_dir = self.ACTIVE_DIR
    
    def validate_plan_location(self, plan_name: str) -> Dict[str, any]:
        """
        Validate that a plan follows proper folder structure.
        
        Returns:
            dict with 'valid' (bool) and 'issues' (list of strings)
        """
        plan_path = self.active_dir / plan_name
        issues = []
        
        # Check 1: Plan must be in a folder, not a file at root
        if not plan_path.is_dir():
            if plan_path.with_suffix('.md').exists():
                issues.append(f"❌ Plan file at root: {plan_name}.md should be in folder {plan_name}/")
            return {'valid': False, 'issues': issues}
        
        # Check 2: Folder must contain required subdirectories
        for subfolder in self.REQUIRED_PLAN_FOLDERS:
            subfolder_path = plan_path / subfolder
            if not subfolder_path.exists():
                issues.append(f"⚠️  Missing required folder: {subfolder}")
        
        # Check 3: Main plan file should exist
        plan_file = plan_path / f"{plan_name}.md"
        if not plan_file.exists():
            # Try alternate naming (A19 prefix)
            alt_file = list(plan_path.glob("A*.md"))
            if not alt_file:
                issues.append(f"⚠️  No main plan file found (expected {plan_name}.md)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'plan_path': str(plan_path)
        }
    
    def find_orphaned_plans(self) -> List[str]:
        """
        Find plans that were created incorrectly (continuation failures).
        
        Heuristics:
        - Name contains "continue", "proceed", "resume" but isn't an epic
        - Created within last 7 days
        - No EPIC-STATUS.yaml file
        """
        orphaned = []
        
        for item in self.active_dir.iterdir():
            if not item.is_dir():
                # Files at root are ALWAYS wrong
                if item.suffix in ['.md', '.yaml', '.json']:
                    orphaned.append(str(item))
                continue
            
            plan_name = item.name
            
            # Check for continuation failure patterns
            continuation_keywords = ['continue', 'proceed', 'resume', 'next-phase']
            if any(kw in plan_name.lower() for kw in continuation_keywords):
                # This should have been a continuation, not a new plan
                orphaned.append(str(item))
                continue
            
            # Check for orphaned UUID plans (no meaningful name)
            if plan_name.startswith('plan-') and len(plan_name) > 40:
                # Check if it has meaningful content
                readme = item / "README.md"
                if not readme.exists():
                    orphaned.append(str(item))
        
        return orphaned
    
    def find_root_level_files(self) -> List[Path]:
        """Find all files incorrectly placed at root of active directory."""
        root_files = []
        
        for item in self.active_dir.iterdir():
            if item.is_file():
                root_files.append(item)
        
        return root_files
    
    def prevent_root_file_creation(self, file_path: Path) -> bool:
        """
        Prevent creating files at root of active directory.
        
        Returns:
            True if file creation should be blocked
        """
        if file_path.parent == self.active_dir:
            logger.error(f"❌ BLOCKED: Cannot create file at root: {file_path}")
            logger.error(f"   Files must be inside plan folders: {self.active_dir}/<plan-name>/")
            return True
        
        return False
    
    def suggest_correct_location(self, file_name: str, plan_context: Optional[str] = None) -> str:
        """
        Suggest correct location for a file.
        
        Args:
            file_name: Name of the file being created
            plan_context: Optional plan name/ID
        
        Returns:
            Suggested path as string
        """
        if plan_context:
            return f"cortex-brain/documents/planning/active/{plan_context}/{file_name}"
        
        # Guess from filename
        if 'consolidation' in file_name.lower():
            return f"cortex-brain/documents/planning/completed/{file_name}"
        
        return f"cortex-brain/documents/planning/active/<plan-name>/{file_name}"
```

### Fix 3: Add Pre-Flight Check in Planning Orchestrator (1 hour)

**Update:** `src/orchestrators/planning/planning_orchestrator_v5.py`

Add validation before creating any files:

```python
from src.orchestrators.planning.validation.folder_structure_validator import FolderStructureValidator

class PlanningOrchestratorV5:
    def __init__(self, ...):
        # ... existing init ...
        self.folder_validator = FolderStructureValidator()
    
    def _validate_plan_structure(self, feature_name: str) -> None:
        """Validate plan will follow proper folder structure."""
        plan_path = Path(f"cortex-brain/documents/planning/active/{feature_name}")
        
        # Check if file already exists at root (should be folder)
        if self.folder_validator.prevent_root_file_creation(plan_path.with_suffix('.md')):
            raise ValueError(
                f"Cannot create plan: {feature_name}.md exists at root. "
                f"Plans must be folders: cortex-brain/documents/planning/active/{feature_name}/"
            )
        
        logger.info(f"✅ Plan structure validation passed: {feature_name}")
```

### Fix 4: Add Cleanup Command (1 hour)

**Create:** `src/orchestrators/planning/cleanup_orphaned_plans.py`

```python
"""
Cleanup Orphaned Plans
Identifies and archives incorrectly created plans.
"""

from pathlib import Path
import shutil
from datetime import datetime
from src.orchestrators.planning.validation.folder_structure_validator import FolderStructureValidator
import logging

logger = logging.getLogger(__name__)

class OrphanedPlanCleanup:
    """Clean up incorrectly created plans and files."""
    
    def __init__(self, dry_run: bool = True):
        self.validator = FolderStructureValidator()
        self.dry_run = dry_run
        self.archive_dir = Path(f"cortex-brain/archives/planning/cleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    
    def execute_cleanup(self) -> Dict[str, any]:
        """
        Execute cleanup operation.
        
        Returns:
            Statistics about cleanup
        """
        stats = {
            'orphaned_plans': [],
            'root_files': [],
            'total_moved': 0,
            'dry_run': self.dry_run
        }
        
        # Find orphaned plans
        orphaned = self.validator.find_orphaned_plans()
        stats['orphaned_plans'] = orphaned
        
        # Find root level files
        root_files = self.validator.find_root_level_files()
        stats['root_files'] = [str(f) for f in root_files]
        
        if not self.dry_run:
            # Create archive directory
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Move orphaned plans
            for orphan in orphaned:
                src = Path(orphan)
                dst = self.archive_dir / src.name
                shutil.move(str(src), str(dst))
                logger.info(f"📦 Archived: {src} → {dst}")
                stats['total_moved'] += 1
            
            # Move root files to completed
            completed_dir = Path("cortex-brain/documents/planning/completed")
            completed_dir.mkdir(parents=True, exist_ok=True)
            
            for root_file in root_files:
                dst = completed_dir / root_file.name
                shutil.move(str(root_file), str(dst))
                logger.info(f"📦 Moved to completed: {root_file} → {dst}")
                stats['total_moved'] += 1
        
        return stats
```

---

## 📋 Implementation Plan

### Phase 1: Immediate Cleanup (0.5 hours) - Add to P02.8

**Sub-phase:** P02.8 - Orphaned Plan Cleanup

**Tasks:**
1. Create archive directory: `cortex-brain/archives/planning/cleanup-2026-01-06/`
2. Move 11 orphaned plan directories to archive
3. Move 2 root-level files to completed directory
4. Verify active directory structure

**Deliverables:**
- Clean `cortex-brain/documents/planning/active/` with only valid plans
- Archive of deleted plans (for recovery if needed)
- Cleanup report

### Phase 2: Add Validation (2 hours) - Add to P02.9

**Sub-phase:** P02.9 - Folder Structure Validation

**Tasks:**
1. Create `folder_structure_validator.py`
2. Add pre-flight checks to Planning Orchestrator
3. Test validation with invalid paths
4. Document folder structure rules

**Deliverables:**
- `src/orchestrators/planning/validation/folder_structure_validator.py`
- Updated Planning Orchestrator with validation
- Unit tests for validator

### Phase 3: Add Cleanup Command (1 hour) - Add to P02.10

**Sub-phase:** P02.10 - Automated Orphan Detection

**Tasks:**
1. Create `cleanup_orphaned_plans.py`
2. Add CLI command: `python3 -m src.main "cleanup orphaned plans"`
3. Test dry-run mode
4. Document cleanup process

**Deliverables:**
- `src/orchestrators/planning/cleanup_orphaned_plans.py`
- CLI command integration
- Cleanup documentation

---

## ✅ Acceptance Criteria

### Immediate Cleanup (P02.8)
- [ ] All orphaned plans moved to archive
- [ ] Root-level files moved to completed directory
- [ ] Only valid plans remain in active directory
- [ ] Archive contains all deleted items (for recovery)

### Validation (P02.9)
- [ ] FolderStructureValidator class created
- [ ] Prevents file creation at root level
- [ ] Validates required subfolders exist
- [ ] Suggests correct locations for misplaced files

### Cleanup Command (P02.10)
- [ ] `cleanup orphaned plans` command works
- [ ] Dry-run mode shows what would be deleted
- [ ] Archive created with timestamp
- [ ] Cleanup report generated

---

## 🎯 Success Metrics

**Before:**
```
cortex-brain/documents/planning/active/
├── 2 files at root level           ❌
├── 11 orphaned plan directories    ❌
├── 2 valid plans                   ✅
```

**After:**
```
cortex-brain/documents/planning/active/
├── 0 files at root level           ✅
├── 0 orphaned plan directories     ✅
├── 2 valid plans                   ✅

cortex-brain/archives/planning/cleanup-2026-01-06/
├── 11 archived orphaned plans      ✅
```

---

## 📊 Impact on Epic Timeline

**Phase P02 Extension:**
- Original: 8.5 days (with P02.4-P02.7)
- New: 9.5 days (add P02.8-P02.10)
- **Total addition:** +1 day

**Updated P02 Sub-phases:**
- P02.1: Core Planning v6 (2d)
- P02.2: Python Templates (1d)
- P02.3: Task-Aware Plans (0.5d)
- P02.4: Continuation Context (2d) ← GAP-1
- P02.5: Master Orch Detection (1d) ← GAP-1
- P02.6: TodoManager Integration (1d) ← GAP-2
- P02.7: Remove RESUMER (0.5d) ← GAP-3
- P02.8: Orphaned Plan Cleanup (0.5d) ← **GAP-7 (NEW)**
- P02.9: Folder Validation (0.5d) ← **GAP-7 (NEW)**
- P02.10: Cleanup Command (0.5d) ← **GAP-7 (NEW)**

**New P02 Total:** 9.5 days

---

## 🔗 Related Gaps

- **GAP-1:** Continuation Context Loss - Root cause of orphaned plans
- **GAP-2:** TodoManager Integration - Better tracking prevents orphans

**Fix Priority:**
1. Fix GAP-1 first (prevents new orphans)
2. Then fix GAP-7 (cleanup existing orphans)

---

## 📝 Documentation Updates

Update these files:
1. **brain-protection-rules.yaml** - Add FOLDER_STRUCTURE_ENFORCEMENT rule
2. **doc-generation-rules.yaml** - Specify correct plan locations
3. **planning-system-4.0-manifest.yaml** - Document folder structure standards
4. **CORTEX.prompt.md** - Add validation step in planning flow

---

## 🎉 Summary

**GAP-7** is a **structural cleanup issue** caused by:
1. GAP-1 creating orphaned plans
2. Legacy manual file creation
3. Missing validation in Planning Orchestrator

**Fix involves:**
1. ✅ Immediate cleanup (archive orphans)
2. ✅ Add validation (prevent future issues)
3. ✅ Add cleanup command (automated detection)

**Priority:** P0_CRITICAL (but cleanup is MEDIUM priority since GAP-1 fix prevents recurrence)

---

**Generated by:** GitHub Copilot (CORTEX v5.2.0)  
**Date:** 2026-01-06  
**Epic:** cortex-v5-remediation-epic  
**Phase:** P02 (Planning Orchestrator v6)
