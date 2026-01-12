# Plan Viewer Data Flow Architecture

## 🎯 Single Source of Truth

```
progress-tracker.json (source of truth)
         ↓
    [sync script]
         ↓
plan-viewer-data.json
         ↓
    [browsers read]
         ↓
plan-viewer.html (displays dashboard)
```

## 📋 Data Files

### Canonical (Production)
- **`cortex-brain/tier1/tracking/progress-tracker.json`**
  - Master state file
  - Contains all AC-ID tracking, phase status, completion counts
  - Updated by: `audit_based_evidence_validator.py --fix`
  - Updated by: Implementation orchestrators (TDD-Master)

- **`cortex-brain/cx6-plan/viewer/plan-viewer-data.json`**
  - Dashboard feed derived from progress-tracker.json
  - Format: Phase objects with completion percentages
  - Updated by: `scripts/sync_plan_viewer_data.py`
  - Read by: plan-viewer.html

### Specialized Data
- **`cortex-brain/cx6-plan/viewer/audit-logs-aggregated.json`**
  - Aggregated audit logs for audit-log-viewer.html
  - Separate from plan tracking

## 🌐 HTML Viewers

### Primary Dashboard
- **`plan-viewer.html`** (PRODUCTION)
  - Reads: `plan-viewer-data.json`
  - Purpose: Complete CORTEX 6.0 progress dashboard
  - Features: Phase breakdown, AC-ID listing, completion tracking

### Specialized Viewers
- **`audit-log-viewer.html`** (FUNCTIONAL)
  - Reads: `audit-logs-aggregated.json`
  - Purpose: Audit log exploration and analysis

- **`core-rules-viewer.html`** (FUNCTIONAL)
  - Purpose: Governance rules browser

## 🔄 Update Workflow

### After Implementation
```bash
# 1. Implementation orchestrator runs (TDD-Master)
python3 -m src.main "implement AC-XXXX"

# 2. Tests run and pass
python3 -m pytest tests/ -k "AC-XXXX"

# 3. Tracker updated with evidence
python3 scripts/audit_based_evidence_validator.py --fix

# 4. Dashboard synced (CRITICAL)
python3 scripts/sync_plan_viewer_data.py

# 5. Refresh browser to see dashboard update
# (plan-viewer.html reads latest plan-viewer-data.json)
```

### Manual Sync
```bash
# If you update progress-tracker.json manually:
python3 scripts/sync_plan_viewer_data.py

# If you want to verify dashboard matches tracker:
python3 scripts/sync_plan_viewer_data.py --verify
```

## ⚠️ Critical Rules

1. **NEVER edit plan-viewer-data.json directly**
   - Always sync from progress-tracker.json
   - Use: `python3 scripts/sync_plan_viewer_data.py`

2. **NEVER create alternative data files**
   - Single source of truth: progress-tracker.json
   - Deleted files (cleanup 2026-01-12):
     - `cortex-brain/dashboards/plan-data.json` (stale copy)
     - `cortex-brain/cx6-plan/viewer/plan-data.json` (stale copy)

3. **NEVER hardcode completion percentages in HTML**
   - Read from plan-viewer-data.json
   - Data is the source, HTML is the display

4. **Always verify data consistency**
   - Run: `python3 scripts/sync_plan_viewer_data.py`
   - Check: Tracker → Dashboard feed → HTML viewer

## 📊 Data Consistency Check

```bash
# Verify all 3 layers match:
# 1. progress-tracker.json (source)
# 2. plan-viewer-data.json (feed)
# 3. plan-viewer.html displays (view)

python3 << 'EOF'
import json
from pathlib import Path

tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
dashboard = json.load(open('cortex-brain/cx6-plan/viewer/plan-viewer-data.json'))

# Compare Phase 2 (example)
t_phase2 = [p for p in tracker.get('completed_phases', []) if p['number'] == 2][0]
d_phase2 = [p for p in dashboard.get('phases', []) if p['id'] == 2][0]

assert t_phase2['completed_count'] == d_phase2['ac_ids_complete']
assert t_phase2['total_ac_count'] == d_phase2['ac_ids_total']
print("✅ Data consistency verified")
EOF
```

## 🗑️ Cleanup (2026-01-12)

**Deleted redundant files that could cause confusion:**
- Duplicate plan viewers (cortex-plan-viewer, plan-viewer-enhanced, plan-viewer-remote)
- Prototype HTML viewers (15 files, 480KB removed)
- Stale data copies (plan-data.json in both dashboards and viewer directories)

**Result:**
- Cleaner viewer directory
- Single canonical data source
- No conflicting files
- Dashboard now shows real progress from tracker
