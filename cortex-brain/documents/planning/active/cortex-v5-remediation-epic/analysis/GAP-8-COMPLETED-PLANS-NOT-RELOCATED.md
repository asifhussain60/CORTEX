# GAP-8: Completed Plans Not Relocated Automatically

**Date:** 2026-01-06  
**Priority:** P1_HIGH  
**Impact:** MEDIUM  
**Effort:** LOW (1 day)

---

## 🎯 Problem Statement

When a plan is completed, the Master Orchestrator or Planning Orchestrator does NOT automatically move it from `cortex-brain/documents/planning/active/` to `cortex-brain/documents/planning/completed/`. This requires manual intervention and creates organizational clutter.

---

## 🔍 Evidence

### Current State
```
cortex-brain/documents/planning/active/
├── cortex-v5-remediation-epic/               ✅ ACTIVE (correct)
├── enterprise-python-audit-logger-with-self-healing/  ❌ COMPLETED (should be relocated)
```

### Expected Behavior
When a plan reaches 100% completion or status changes to "completed":
1. Orchestrator should detect completion
2. Automatically archive the plan folder
3. Move to `cortex-brain/documents/planning/completed/`
4. Update database tracking (if applicable)
5. Generate completion report

### Actual Behavior
Plans remain in `active/` indefinitely, even after completion. User must manually move them.

---

## 🐛 Root Causes

### Cause 1: No Completion Detection in Planning Orchestrator

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`

The Planning Orchestrator creates plans but has no logic to:
- Detect when a plan reaches 100% completion
- Monitor plan status changes
- Trigger relocation on completion

### Cause 2: Missing Post-Completion Hook

**File:** `src/orchestrators/master_orchestrator.py`

The Master Orchestrator doesn't have a post-execution hook to:
- Check if plan is complete after execution
- Archive completed plan folders
- Update tracking metadata

### Cause 3: No Plan Lifecycle Management

The system lacks a **Plan Lifecycle Manager** component that handles:
- Plan states: draft → active → in-progress → completed → archived
- State transitions and validations
- Automatic folder relocation based on state
- Completion criteria checking

---

## 🎯 Comprehensive Fix Strategy

### Fix 1: Add Completion Detection (0.5 days) - P02.11

**Create:** `src/orchestrators/planning/plan_lifecycle_manager.py`

```python
"""
Plan Lifecycle Manager
Handles plan state transitions and automatic relocation.
"""

from pathlib import Path
import shutil
import json
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PlanLifecycleManager:
    """Manages plan lifecycle from creation to archival."""
    
    ACTIVE_DIR = Path("cortex-brain/documents/planning/active")
    COMPLETED_DIR = Path("cortex-brain/documents/planning/completed")
    ARCHIVE_DIR = Path("cortex-brain/archives/planning")
    
    STATES = ["draft", "active", "in_progress", "completed", "archived"]
    
    def __init__(self):
        self.active_dir = self.ACTIVE_DIR
        self.completed_dir = self.COMPLETED_DIR
        self.archive_dir = self.ARCHIVE_DIR
    
    def check_completion(self, plan_name: str) -> bool:
        """
        Check if a plan has reached completion.
        
        Checks:
        1. Progress = 100%
        2. All phases marked complete
        3. Status = "completed" in metadata
        
        Returns:
            True if plan is complete
        """
        plan_path = self.active_dir / plan_name
        
        if not plan_path.exists():
            return False
        
        # Check 1: README or main plan file status
        readme = plan_path / "README.md"
        if readme.exists():
            content = readme.read_text()
            if "Status:** ✅ COMPLETED" in content or "Status:** ✅ COMPLETE" in content:
                return True
        
        # Check 2: Tracking JSON (if exists)
        tracking_dir = plan_path / "tracking"
        if tracking_dir.exists():
            progress_files = list(tracking_dir.glob("*progress*.json"))
            for progress_file in progress_files:
                try:
                    data = json.loads(progress_file.read_text())
                    if data.get("status") == "completed" and data.get("overall_progress") == 100:
                        return True
                except Exception as e:
                    logger.warning(f"Could not parse {progress_file}: {e}")
        
        # Check 3: Main plan file
        plan_files = list(plan_path.glob("A*.md"))
        if plan_files:
            content = plan_files[0].read_text()
            if "Status:** ✅ COMPLETED" in content or "100%" in content:
                # Additional validation: check for completion markers
                if "# 🎉 CONGRATULATIONS" in content or "COMPLETION REPORT" in content:
                    return True
        
        return False
    
    def relocate_completed_plan(self, plan_name: str, dry_run: bool = False) -> Dict[str, any]:
        """
        Move completed plan to completed directory.
        
        Args:
            plan_name: Name of the plan directory
            dry_run: If True, only simulate (don't actually move)
        
        Returns:
            dict with status and details
        """
        src = self.active_dir / plan_name
        dst = self.completed_dir / plan_name
        
        result = {
            "plan_name": plan_name,
            "source": str(src),
            "destination": str(dst),
            "dry_run": dry_run,
            "success": False,
            "message": ""
        }
        
        # Validation
        if not src.exists():
            result["message"] = f"Source not found: {src}"
            return result
        
        if dst.exists():
            result["message"] = f"Destination already exists: {dst}"
            return result
        
        if not self.check_completion(plan_name):
            result["message"] = f"Plan not complete: {plan_name}"
            return result
        
        if dry_run:
            result["success"] = True
            result["message"] = f"[DRY RUN] Would move {src} → {dst}"
            return result
        
        # Execute move
        try:
            self.completed_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            
            # Create relocation metadata
            metadata = {
                "plan_name": plan_name,
                "relocated_at": datetime.now().isoformat(),
                "source": str(src),
                "destination": str(dst),
                "reason": "Plan marked as completed"
            }
            
            metadata_file = dst / ".relocation-metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))
            
            result["success"] = True
            result["message"] = f"Successfully relocated: {plan_name}"
            logger.info(f"✅ Relocated completed plan: {plan_name}")
            
        except Exception as e:
            result["message"] = f"Error relocating plan: {e}"
            logger.error(f"❌ Failed to relocate {plan_name}: {e}")
        
        return result
    
    def scan_and_relocate_completed(self, dry_run: bool = True) -> Dict[str, any]:
        """
        Scan active directory for completed plans and relocate them.
        
        Returns:
            Statistics about relocation
        """
        stats = {
            "scanned": 0,
            "completed": 0,
            "relocated": 0,
            "errors": 0,
            "dry_run": dry_run,
            "plans": []
        }
        
        if not self.active_dir.exists():
            return stats
        
        for item in self.active_dir.iterdir():
            if not item.is_dir():
                continue
            
            stats["scanned"] += 1
            plan_name = item.name
            
            if self.check_completion(plan_name):
                stats["completed"] += 1
                result = self.relocate_completed_plan(plan_name, dry_run=dry_run)
                stats["plans"].append(result)
                
                if result["success"]:
                    stats["relocated"] += 1
                else:
                    stats["errors"] += 1
        
        return stats
    
    def generate_completion_report(self, plan_name: str) -> Optional[Path]:
        """
        Generate a completion report for a relocated plan.
        
        Returns:
            Path to generated report
        """
        plan_path = self.completed_dir / plan_name
        
        if not plan_path.exists():
            logger.error(f"Plan not found in completed: {plan_name}")
            return None
        
        report_path = plan_path / "COMPLETION-REPORT.md"
        
        report_content = f"""# Plan Completion Report

**Plan:** {plan_name}  
**Completed:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Status:** ✅ COMPLETED  
**Location:** `cortex-brain/documents/planning/completed/{plan_name}/`

---

## 📊 Summary

This plan has been automatically relocated from active to completed directory by the Plan Lifecycle Manager.

---

## 📁 Artifacts

All plan artifacts have been preserved:
- Context and analysis
- Implementation artifacts
- Reports and documentation
- Tracking metadata

---

## 🔗 Recovery

If this plan needs to be reactivated:

```bash
mv cortex-brain/documents/planning/completed/{plan_name} \\
   cortex-brain/documents/planning/active/
```

---

**Generated by:** Plan Lifecycle Manager  
**Timestamp:** {datetime.now().isoformat()}
"""
        
        report_path.write_text(report_content)
        logger.info(f"✅ Generated completion report: {report_path}")
        return report_path
```

### Fix 2: Integration with Master Orchestrator (0.25 days) - P02.12

**Update:** `src/orchestrators/master_orchestrator.py`

Add post-execution hook:

```python
from src.orchestrators.planning.plan_lifecycle_manager import PlanLifecycleManager

class MasterOrchestrator:
    def __init__(self, ...):
        # ... existing init ...
        self.lifecycle_manager = PlanLifecycleManager()
    
    def _post_execution_hook(self, result: Dict[str, any]) -> None:
        """
        Execute post-processing after orchestrator completes.
        
        Checks:
        - Is this a planning operation?
        - Did it complete successfully?
        - Is the plan now 100% complete?
        """
        if not result.get("success"):
            return
        
        # Extract plan name from result (if applicable)
        plan_name = result.get("plan_name") or result.get("feature_name")
        
        if not plan_name:
            return
        
        # Check if plan is complete
        if self.lifecycle_manager.check_completion(plan_name):
            logger.info(f"🎉 Plan '{plan_name}' detected as complete!")
            
            # Relocate to completed directory
            relocation_result = self.lifecycle_manager.relocate_completed_plan(
                plan_name, 
                dry_run=False
            )
            
            if relocation_result["success"]:
                # Generate completion report
                report = self.lifecycle_manager.generate_completion_report(plan_name)
                result["completion_report"] = str(report) if report else None
                result["relocated"] = True
                logger.info(f"✅ Plan '{plan_name}' relocated to completed directory")
            else:
                logger.warning(f"⚠️  Could not relocate plan: {relocation_result['message']}")
```

### Fix 3: Add CLI Command (0.25 days) - P02.13

**Add to:** `src/main.py` or orchestrator routing

Support command:
```bash
python3 -m src.main "relocate completed plans"
```

This will:
1. Scan active directory
2. Detect completed plans
3. Relocate to completed directory
4. Generate reports

---

## 📋 Implementation Plan

### Phase P02.11: Plan Lifecycle Manager (0.5 days)

**Deliverables:**
- `src/orchestrators/planning/plan_lifecycle_manager.py`
- Completion detection logic (3 validation methods)
- Relocation logic with dry-run mode
- Completion report generation

**Tests:**
- Unit tests for completion detection
- Relocation with/without dry-run
- Edge cases (plan not found, already exists, not complete)

### Phase P02.12: Master Orchestrator Integration (0.25 days)

**Deliverables:**
- Post-execution hook in Master Orchestrator
- Automatic completion detection
- Automatic relocation on completion

**Tests:**
- Integration test: Create plan → Mark complete → Verify relocation
- Test: Incomplete plan should NOT relocate

### Phase P02.13: CLI Command (0.25 days)

**Deliverables:**
- CLI command: `relocate completed plans`
- Batch relocation support
- Statistics reporting

**Tests:**
- CLI command execution
- Batch relocation of multiple plans
- Dry-run mode

---

## ✅ Acceptance Criteria

### Plan Lifecycle Manager (P02.11)
- [ ] PlanLifecycleManager class created
- [ ] check_completion() validates 3 criteria (status, progress, markers)
- [ ] relocate_completed_plan() moves folder and creates metadata
- [ ] scan_and_relocate_completed() processes all active plans
- [ ] generate_completion_report() creates report in completed directory

### Master Orchestrator Integration (P02.12)
- [ ] Post-execution hook detects completion
- [ ] Automatic relocation on 100% completion
- [ ] Completion report generated automatically
- [ ] User notified of relocation in response

### CLI Command (P02.13)
- [ ] `relocate completed plans` command works
- [ ] Dry-run mode shows what would be relocated
- [ ] Statistics displayed (scanned, completed, relocated, errors)
- [ ] Manual relocation option available

---

## 🎯 Success Metrics

**Before:**
```
cortex-brain/documents/planning/active/
├── cortex-v5-remediation-epic/               ✅ ACTIVE (21% progress)
├── enterprise-python-audit-logger-with-self-healing/  ❌ COMPLETED (100%, but stuck in active)
```

**After:**
```
cortex-brain/documents/planning/active/
├── cortex-v5-remediation-epic/               ✅ ACTIVE (21% progress)

cortex-brain/documents/planning/completed/
├── enterprise-python-audit-logger-with-self-healing/  ✅ RELOCATED AUTOMATICALLY
    └── COMPLETION-REPORT.md                  ✅ AUTO-GENERATED
```

---

## 📊 Impact on Epic Timeline

**Phase P02 Extension:**
- Original: 10.5 days (with P02.1-P02.10)
- New: 11.5 days (add P02.11-P02.13)
- **Total addition:** +1 day

**Updated P02 Sub-phases:**
- P02.1-P02.3: Core Planning v6 (3.5d)
- P02.4-P02.5: Fix GAP-1 (3d)
- P02.6: TodoManager Integration (1d)
- P02.7: Remove RESUMER (0.5d)
- P02.8: Orphaned Plan Cleanup (0.5d) ✅ COMPLETE
- P02.9: Folder Validation (0.5d)
- P02.10: Cleanup Command (0.5d)
- **P02.11: Plan Lifecycle Manager (0.5d)** ← **GAP-8 (NEW)**
- **P02.12: Master Orch Integration (0.25d)** ← **GAP-8 (NEW)**
- **P02.13: Relocate CLI Command (0.25d)** ← **GAP-8 (NEW)**

**New P02 Total:** 11.5 days

---

## 🔗 Related Gaps

- **GAP-7:** Incorrect Plan Locations - GAP-8 ensures proper lifecycle management
- **GAP-1:** Continuation Context - Better state tracking helps with continuation

**Dependencies:**
- GAP-8 should be implemented AFTER GAP-7 (cleanup first, then add automation)

---

## 📝 Documentation Updates

Update these files:
1. **brain-protection-rules.yaml** - Add PLAN_LIFECYCLE_MANAGEMENT rule
2. **planning-system-4.0-manifest.yaml** - Document lifecycle states
3. **CORTEX.prompt.md** - Add completion detection step
4. **master-orchestrator.yaml** - Add post-execution hooks

---

## 🎯 Benefits

1. **Automatic Organization** - No manual intervention needed
2. **Clean Active Directory** - Only active plans remain
3. **Completion Tracking** - Clear visibility of completed work
4. **Historical Record** - Completed plans preserved with metadata
5. **Recovery Support** - Easy to reactivate if needed

---

## 🎉 Summary

**GAP-8** addresses the lack of **automatic plan lifecycle management**. When a plan reaches completion:

✅ **Detection:** Automatic via 3 validation methods  
✅ **Relocation:** Moves from active → completed  
✅ **Reporting:** Generates completion report  
✅ **Tracking:** Updates metadata and state  
✅ **CLI:** Manual batch processing available  

**Fix involves:**
1. Create Plan Lifecycle Manager (0.5d)
2. Integrate with Master Orchestrator (0.25d)
3. Add CLI command (0.25d)

**Total:** 1 day

**Priority:** P1_HIGH (important for organization, but not blocking execution)

---

**Generated by:** GitHub Copilot (CORTEX v5.2.0)  
**Date:** 2026-01-06  
**Epic:** cortex-v5-remediation-epic  
**Phase:** P02 (Planning Orchestrator v6)
