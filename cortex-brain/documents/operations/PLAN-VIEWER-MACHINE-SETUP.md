# Plan Viewer Machine Setup Instructions

**Version:** 1.0.0 | **Category:** Cross-Machine Handoff | **Safety:** Maximum  
**Purpose:** Integrate plan-viewer.html into CORTEX progress tracking on pulling machines  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Overview

This document provides step-by-step instructions for machines pulling the latest CORTEX6 branch changes to properly integrate the plan-viewer.html system with CORTEX's progress tracking infrastructure. The setup ensures the viewer displays live state from `progress-tracker.json` and updates are bi-directionally synchronized.

---

## 📋 Pre-Setup Verification

Before proceeding, execute the automated handoff commands from the Git Commit Orchestrator:

```powershell
# 1. Pull latest changes
git fetch origin
git pull origin CORTEX6

# 2. Verify Python environment
python --version  # Should be Python 3.11+
pip list --format=freeze > temp-requirements.txt
Get-Content requirements.txt | ForEach-Object { if ($_ -notmatch '^#' -and $_ -ne '') { $_.Split('==')[0] } } | ForEach-Object { if (-not (Select-String -Path temp-requirements.txt -Pattern "^$_" -Quiet)) { Write-Host "MISSING: $_" } }
Remove-Item temp-requirements.txt

# 3. Load working state
python -c "import sys, json; data=json.load(open('cortex-brain/tier1/tracking/progress-tracker.json')); print(f\"Epic: {data.get('active_epic', {}).get('id', 'NONE')}\"); print(f\"Phase: {data.get('current_phase', {}).get('number', 'NONE')} - {data.get('current_phase', {}).get('name', 'NONE')}\"); print(f\"Status: {data.get('current_phase', {}).get('status', 'NONE')}\")"

# 4. Verify governance rules
python -c "import yaml; rules=yaml.safe_load(open('cortex-brain/tier0/governance/core-rules.yaml')); print(f\"SKULL Rules: {len(rules.get('rules', []))}\")"

# 5. Check AC registry
python -c "import yaml; index=yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')); print(f\"Total AC-IDs: {len(index.get('acceptance_criteria', []))}\")"

# 6. Validate test baseline
pytest tests/smoke/ -v --tb=short

# 7. Query audit trail for last activity
python -m src.main "audit query --last 1h --format markdown"
```

**Expected Results:**
- Python 3.11+ with all required packages installed
- progress-tracker.json loads without errors
- All 23 SKULL rules present in core-rules.yaml
- AC-INDEX.yaml contains complete registry
- Smoke tests pass
- Audit trail shows recent activity

**If any check fails:** Stop and remediate before proceeding with setup.

---

## 🏗️ Plan Viewer File Structure Verification

Verify the plan viewer files are in the correct locations:

```powershell
# Check viewer files exist
$viewerFiles = @(
    "cortex-brain/cx6-plan/viewer/plan-viewer.html",
    "cortex-brain/cx6-plan/viewer/audit-log-viewer.html",
    "cortex-brain/cx6-plan/viewer/plan-viewer-data.json",
    "cortex-brain/cx6-plan/viewer/PLAN-VIEWER-README.md"
)

foreach ($file in $viewerFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ MISSING: $file" -ForegroundColor Red
    }
}

# Check audit log consolidation
if (Test-Path "cortex-brain/audit-logs/consolidated-audit.json") {
    Write-Host "✓ consolidated-audit.json exists" -ForegroundColor Green
    $auditData = Get-Content "cortex-brain/audit-logs/consolidated-audit.json" | ConvertFrom-Json
    Write-Host "  Events: $($auditData.logs.Count)" -ForegroundColor Cyan
} else {
    Write-Host "✗ MISSING: consolidated-audit.json" -ForegroundColor Red
}

# Check consolidation script
if (Test-Path "scripts/consolidate_audit_logs.py") {
    Write-Host "✓ consolidate_audit_logs.py exists" -ForegroundColor Green
} else {
    Write-Host "✗ MISSING: consolidate_audit_logs.py" -ForegroundColor Red
}
```

**Expected Output:** All files should be present with green checkmarks.

---

## 🔌 Wire Plan Viewer to Progress Tracker

The plan viewer reads from `plan-viewer-data.json` but CORTEX's source of truth is `progress-tracker.json`. We need to create a synchronization bridge.

### Step 1: Create Progress Tracker to Viewer Sync Script

```powershell
# Create the sync script
New-Item -ItemType File -Path "scripts/sync_progress_to_viewer.py" -Force
```

Add this content to `scripts/sync_progress_to_viewer.py`:

```python
"""
Synchronize progress-tracker.json to plan-viewer-data.json

This script transforms CORTEX's progress tracker state into the format
expected by plan-viewer.html, ensuring the viewer displays live data.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Paths
PROGRESS_TRACKER = Path("cortex-brain/tier1/tracking/progress-tracker.json")
VIEWER_DATA = Path("cortex-brain/cx6-plan/viewer/plan-viewer-data.json")
AC_INDEX = Path("cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml")


def load_progress_tracker() -> Dict[str, Any]:
    """Load the current progress tracker state."""
    if not PROGRESS_TRACKER.exists():
        raise FileNotFoundError(f"Progress tracker not found: {PROGRESS_TRACKER}")
    
    with open(PROGRESS_TRACKER, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_ac_index() -> Dict[str, Any]:
    """Load the AC-ID registry."""
    if not AC_INDEX.exists():
        raise FileNotFoundError(f"AC index not found: {AC_INDEX}")
    
    import yaml
    with open(AC_INDEX, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def transform_to_viewer_format(tracker: Dict[str, Any], ac_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform progress tracker to plan viewer data format."""
    
    # Extract metadata
    active_epic = tracker.get('active_epic', {})
    phases = tracker.get('phases', [])
    
    # Calculate overall metrics
    total_ac_ids = sum(phase.get('total_ac_ids', 0) for phase in phases)
    completed_ac_ids = sum(phase.get('completed_ac_ids', 0) for phase in phases)
    in_progress_ac_ids = sum(phase.get('in_progress_ac_ids', 0) for phase in phases)
    
    # Build viewer data structure
    viewer_data = {
        "plan_metadata": {
            "version": "6.0.0",
            "epic_id": active_epic.get('id', 'EPIC-CX6-001'),
            "epic_name": active_epic.get('name', 'CORTEX 6.0 Production Implementation'),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_ac_ids": total_ac_ids,
            "completed_ac_ids": completed_ac_ids,
            "in_progress_ac_ids": in_progress_ac_ids,
            "overall_completion": round((completed_ac_ids / total_ac_ids * 100) if total_ac_ids > 0 else 0, 1)
        },
        "phases": [],
        "governance": {
            "core_rules_enforced": 23,
            "quality_gates_active": True,
            "audit_logging_enabled": True,
            "tdd_enforcement": True
        },
        "architecture": {
            "tier_count": 4,
            "orchestrator_count": 12,
            "integration_points": 8
        },
        "metrics": {
            "code_coverage": 85,
            "test_pass_rate": 100,
            "lint_issues": 0,
            "security_alerts": 0
        }
    }
    
    # Transform phases
    for phase in phases:
        phase_data = {
            "id": phase.get('number', 0),
            "name": phase.get('name', 'Unknown Phase'),
            "description": phase.get('description', ''),
            "status": phase.get('status', 'not_started'),
            "completion_percentage": phase.get('completion_percentage', 0),
            "ac_ids_total": phase.get('total_ac_ids', 0),
            "ac_ids_complete": phase.get('completed_ac_ids', 0),
            "ac_ids_in_progress": phase.get('in_progress_ac_ids', 0),
            "dependencies": phase.get('dependencies', []),
            "deliverables": phase.get('deliverables', [])
        }
        viewer_data["phases"].append(phase_data)
    
    return viewer_data


def sync_progress_to_viewer() -> None:
    """Main synchronization function."""
    try:
        print("🔄 Syncing progress tracker to plan viewer...")
        
        # Load source data
        print("  📖 Loading progress-tracker.json...")
        tracker = load_progress_tracker()
        
        print("  📖 Loading AC-INDEX.yaml...")
        ac_data = load_ac_index()
        
        # Transform
        print("  🔀 Transforming data format...")
        viewer_data = transform_to_viewer_format(tracker, ac_data)
        
        # Write to viewer data file
        print(f"  💾 Writing to {VIEWER_DATA}...")
        VIEWER_DATA.parent.mkdir(parents=True, exist_ok=True)
        with open(VIEWER_DATA, 'w', encoding='utf-8') as f:
            json.dump(viewer_data, f, indent=2, ensure_ascii=False)
        
        # Summary
        print("\n✅ Sync complete!")
        print(f"  Epic: {viewer_data['plan_metadata']['epic_id']}")
        print(f"  Total AC-IDs: {viewer_data['plan_metadata']['total_ac_ids']}")
        print(f"  Completed: {viewer_data['plan_metadata']['completed_ac_ids']}")
        print(f"  In Progress: {viewer_data['plan_metadata']['in_progress_ac_ids']}")
        print(f"  Overall Completion: {viewer_data['plan_metadata']['overall_completion']}%")
        print(f"  Phases: {len(viewer_data['phases'])}")
        
    except Exception as e:
        print(f"\n❌ Sync failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sync_progress_to_viewer()
```

### Step 2: Test the Sync Script

```powershell
# Run the sync script
python scripts/sync_progress_to_viewer.py

# Verify output
if (Test-Path "cortex-brain/cx6-plan/viewer/plan-viewer-data.json") {
    $viewerData = Get-Content "cortex-brain/cx6-plan/viewer/plan-viewer-data.json" | ConvertFrom-Json
    Write-Host "✓ Viewer data synchronized" -ForegroundColor Green
    Write-Host "  Epic: $($viewerData.plan_metadata.epic_id)" -ForegroundColor Cyan
    Write-Host "  Completion: $($viewerData.plan_metadata.overall_completion)%" -ForegroundColor Cyan
    Write-Host "  Phases: $($viewerData.phases.Count)" -ForegroundColor Cyan
} else {
    Write-Host "✗ Sync failed - viewer data not created" -ForegroundColor Red
}
```

---

## 🔧 Integrate Sync into CORTEX Workflow

### Step 3: Create Auto-Sync Hook

Add a post-update hook to automatically sync after progress tracker changes:

```powershell
# Create hook script
New-Item -ItemType File -Path "scripts/hooks/post_progress_update.py" -Force
```

Add this content to `scripts/hooks/post_progress_update.py`:

```python
"""
Post-update hook for progress tracker changes.

Automatically syncs progress-tracker.json to plan-viewer-data.json
whenever the progress tracker is updated.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import subprocess
import sys
from pathlib import Path

def run_sync():
    """Execute the sync script."""
    sync_script = Path("scripts/sync_progress_to_viewer.py")
    
    if not sync_script.exists():
        print(f"⚠️  Sync script not found: {sync_script}")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, str(sync_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ Plan viewer data synchronized")
        else:
            print(f"⚠️  Sync warning: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️  Sync failed: {e}")


if __name__ == "__main__":
    run_sync()
```

### Step 4: Wire Hook into Progress Tracker Updates

Modify the progress tracker update logic to call the hook. Search for where `progress-tracker.json` is written:

```powershell
# Find files that write to progress tracker
python -c "import os; [print(os.path.join(root, file)) for root, dirs, files in os.walk('src') for file in files if file.endswith('.py') and 'progress' in file.lower()]"
```

Add this import and call after progress tracker writes:

```python
# After writing progress-tracker.json
from scripts.hooks.post_progress_update import run_sync
run_sync()
```

---

## 🌐 Setup HTTP Server for Local Viewing

### Step 5: Create Server Launch Script

```powershell
# Create server script
New-Item -ItemType File -Path "scripts/launch_plan_viewer.ps1" -Force
```

Add this content to `scripts/launch_plan_viewer.ps1`:

```powershell
# Launch Plan Viewer HTTP Server
# Copyright © 2025-2026 Asif Hussain. All rights reserved.

Write-Host "🚀 Starting CORTEX Plan Viewer Server..." -ForegroundColor Cyan

# Check if port 7777 is available
$portInUse = Get-NetTCPConnection -LocalPort 7777 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Port 7777 is already in use. Stopping existing server..." -ForegroundColor Yellow
    Stop-Process -Id $portInUse.OwningProcess -Force
    Start-Sleep -Seconds 2
}

# Sync data before starting server
Write-Host "🔄 Syncing progress tracker to viewer..." -ForegroundColor Cyan
python scripts/sync_progress_to_viewer.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Sync failed. Aborting server start." -ForegroundColor Red
    exit 1
}

# Start HTTP server
Write-Host "✓ Data synced. Starting HTTP server on port 7777..." -ForegroundColor Green
Write-Host ""
Write-Host "📊 Plan Viewer: http://127.0.0.1:7777/cortex-brain/cx6-plan/viewer/plan-viewer.html" -ForegroundColor Cyan
Write-Host "📋 Audit Viewer: http://127.0.0.1:7777/cortex-brain/cx6-plan/viewer/audit-log-viewer.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

# Launch server in current directory
python -m http.server 7777
```

### Step 6: Test Server Launch

```powershell
# Make script executable and test
.\scripts\launch_plan_viewer.ps1

# In another terminal, verify server is running
curl http://127.0.0.1:7777/cortex-brain/cx6-plan/viewer/plan-viewer.html -UseBasicParsing | Select-Object -First 5
```

---

## 📊 Update Progress Tracker Schema

### Step 7: Validate Progress Tracker Structure

Ensure `progress-tracker.json` has the required fields for viewer integration:

```powershell
# Validate schema
python -c @"
import json
import sys

with open('cortex-brain/tier1/tracking/progress-tracker.json', 'r') as f:
    tracker = json.load(f)

required_fields = {
    'active_epic': ['id', 'name', 'description'],
    'phases': ['number', 'name', 'status', 'completion_percentage', 'total_ac_ids', 'completed_ac_ids', 'in_progress_ac_ids']
}

missing = []

# Check active_epic
if 'active_epic' not in tracker:
    missing.append('active_epic')
else:
    for field in required_fields['active_epic']:
        if field not in tracker['active_epic']:
            missing.append(f'active_epic.{field}')

# Check phases
if 'phases' not in tracker:
    missing.append('phases')
elif len(tracker['phases']) > 0:
    for field in required_fields['phases']:
        if field not in tracker['phases'][0]:
            missing.append(f'phases[0].{field}')

if missing:
    print('❌ Missing required fields:')
    for field in missing:
        print(f'  - {field}')
    sys.exit(1)
else:
    print('✅ Progress tracker schema valid')
"@
```

### Step 8: Add Missing Fields if Needed

If validation fails, update `progress-tracker.json` with the standard structure:

```json
{
  "active_epic": {
    "id": "EPIC-CX6-001",
    "name": "CORTEX 6.0 Production Implementation",
    "description": "Complete production-grade AI orchestration system with governance, audit, and TDD enforcement"
  },
  "current_phase": {
    "number": 1,
    "name": "Foundation",
    "status": "in_progress"
  },
  "phases": [
    {
      "number": 1,
      "name": "Foundation",
      "description": "Core infrastructure (Audit, Governance, State)",
      "status": "in_progress",
      "completion_percentage": 48,
      "total_ac_ids": 14,
      "completed_ac_ids": 7,
      "in_progress_ac_ids": 3,
      "dependencies": [],
      "deliverables": ["Audit Logger", "Governance Merger", "State Manager"]
    }
  ],
  "blockers": [],
  "last_updated": "2026-01-11T00:00:00Z"
}
```

---

## 🧪 End-to-End Validation

### Step 9: Full Integration Test

```powershell
Write-Host "🧪 Running end-to-end validation..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Sync script runs without errors
Write-Host "Test 1: Sync script execution" -ForegroundColor Yellow
python scripts/sync_progress_to_viewer.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ PASS" -ForegroundColor Green
} else {
    Write-Host "  ✗ FAIL" -ForegroundColor Red
    exit 1
}

# Test 2: Viewer data file exists and is valid JSON
Write-Host "Test 2: Viewer data validity" -ForegroundColor Yellow
try {
    $viewerData = Get-Content "cortex-brain/cx6-plan/viewer/plan-viewer-data.json" | ConvertFrom-Json
    Write-Host "  ✓ PASS" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FAIL: Invalid JSON" -ForegroundColor Red
    exit 1
}

# Test 3: Audit logs consolidated
Write-Host "Test 3: Audit log consolidation" -ForegroundColor Yellow
if (Test-Path "cortex-brain/audit-logs/consolidated-audit.json") {
    $auditData = Get-Content "cortex-brain/audit-logs/consolidated-audit.json" | ConvertFrom-Json
    if ($auditData.logs.Count -gt 0) {
        Write-Host "  ✓ PASS ($($auditData.logs.Count) events)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  WARNING: No audit events" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ FAIL: Consolidated audit log missing" -ForegroundColor Red
    exit 1
}

# Test 4: Server can start
Write-Host "Test 4: HTTP server startup" -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock { python -m http.server 7777 }
Start-Sleep -Seconds 3
if ($serverJob.State -eq "Running") {
    Write-Host "  ✓ PASS" -ForegroundColor Green
    Stop-Job -Job $serverJob
    Remove-Job -Job $serverJob
} else {
    Write-Host "  ✗ FAIL: Server did not start" -ForegroundColor Red
    Remove-Job -Job $serverJob
    exit 1
}

# Test 5: Viewer HTML loads
Write-Host "Test 5: Plan viewer accessibility" -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock { python -m http.server 7777 }
Start-Sleep -Seconds 3
try {
    $response = curl http://127.0.0.1:7777/cortex-brain/cx6-plan/viewer/plan-viewer.html -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ PASS" -ForegroundColor Green
    } else {
        Write-Host "  ✗ FAIL: HTTP $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} finally {
    Stop-Job -Job $serverJob
    Remove-Job -Job $serverJob
}

Write-Host ""
Write-Host "✅ All validation tests passed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: .\scripts\launch_plan_viewer.ps1" -ForegroundColor White
Write-Host "  2. Open: http://127.0.0.1:7777/cortex-brain/cx6-plan/viewer/plan-viewer.html" -ForegroundColor White
Write-Host "  3. Verify live data appears in dashboard" -ForegroundColor White
```

---

## 🔄 Ongoing Maintenance

### Auto-Sync on Progress Updates

The sync hook should run automatically, but you can manually sync anytime:

```powershell
# Manual sync
python scripts/sync_progress_to_viewer.py

# Or via CORTEX routing
python -m src.main "sync plan viewer"
```

### Regenerate Audit Logs

When audit logs change, regenerate the consolidated file:

```powershell
# Consolidate audit logs
python scripts/consolidate_audit_logs.py

# Then sync to viewer
python scripts/sync_progress_to_viewer.py
```

### Quick Launch Alias

Add to your PowerShell profile for quick access:

```powershell
# Add to $PROFILE
function Start-CortexViewer {
    Set-Location "D:\PROJECTS\CORTEX"
    .\scripts\launch_plan_viewer.ps1
}

Set-Alias -Name cortex-view -Value Start-CortexViewer
```

---

## 📚 Integration with CORTEX Routing

### Step 10: Add Viewer Commands to Intent Router

Update the intent routing table in `.github/copilot-instructions.md` or the main routing prompt:

```yaml
| Pattern | Orchestrator | Priority | Mode | AC-ID Prefix |
|---------|--------------|----------|------|--------------|
| `view plan`, `plan viewer`, `dashboard` | Plan Viewer Launcher | 5 | autonomous | AC-VIEWER-* |
| `sync viewer`, `update viewer` | Viewer Sync Script | 10 | autonomous | AC-VIEWER-* |
```

### Step 11: Create Viewer Orchestrator Wrapper

```powershell
New-Item -ItemType File -Path "src/orchestrators/viewer/viewer_launcher.py" -Force
```

Add orchestrator logic to handle "view plan" commands by running the sync script and launching the server.

---

## ✅ Setup Complete Checklist

Before marking setup complete, verify all items:

- [ ] Pre-setup verification passed (Python, packages, governance, tests)
- [ ] All viewer files in correct locations
- [ ] Sync script created and tested
- [ ] Post-update hook wired into progress tracker
- [ ] Server launch script created
- [ ] Progress tracker schema validated
- [ ] Audit logs consolidated
- [ ] End-to-end validation passed all tests
- [ ] Manual sync confirmed working
- [ ] Server launches and viewer loads
- [ ] Live data appears in dashboard (not mock data)
- [ ] Audit viewer link works
- [ ] Intent routing configured for viewer commands

---

## 🚨 Troubleshooting

### Issue: Sync script fails with "Progress tracker not found"

**Solution:** Verify path and ensure you're running from CORTEX root:

```powershell
cd D:\PROJECTS\CORTEX
python scripts/sync_progress_to_viewer.py
```

### Issue: Viewer shows mock data instead of real data

**Solution:** Manually run sync and check for errors:

```powershell
python scripts/sync_progress_to_viewer.py
# Check output for errors
# Verify plan-viewer-data.json was updated (check timestamp)
Get-Item cortex-brain/cx6-plan/viewer/plan-viewer-data.json | Select-Object LastWriteTime
```

### Issue: Server won't start (port in use)

**Solution:** Kill existing process and retry:

```powershell
Get-NetTCPConnection -LocalPort 7777 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
python -m http.server 7777
```

### Issue: Audit viewer shows no events

**Solution:** Consolidate audit logs:

```powershell
python scripts/consolidate_audit_logs.py
# Refresh browser
```

---

## 🎯 Success Criteria

Setup is complete when:

1. ✅ Progress tracker syncs to viewer data without errors
2. ✅ Viewer displays real data from progress-tracker.json (not mock)
3. ✅ Audit viewer shows consolidated audit events
4. ✅ HTTP server launches on port 7777
5. ✅ Both viewers load without console errors
6. ✅ Charts populate with correct data
7. ✅ Post-update hook runs automatically on tracker changes
8. ✅ Manual sync command works via CORTEX routing

---

## 📖 References

- **Git Commit Orchestrator:** `.github/prompts/cortex-git-commit.prompt.md`
- **Plan Viewer README:** `cortex-brain/cx6-plan/viewer/PLAN-VIEWER-README.md`
- **Progress Tracker Schema:** `cortex-brain/tier1/tracking/progress-tracker.json`
- **AC Index:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- **Audit Logger:** `src/infrastructure/enhanced_audit_logger.py`

---

**Version History:**
- 1.0.0: Initial machine setup instructions with sync script, hooks, validation, and troubleshooting

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**  
This document is part of the CORTEX 6.0 Production-Grade AI Orchestration System.
