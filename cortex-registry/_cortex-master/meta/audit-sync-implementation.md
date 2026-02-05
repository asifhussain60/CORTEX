# AUDIT Sync Implementation Guide

**Version:** 1.0 | **Date:** 2026-02-05 | **Phase:** 6 | **Status:** Documented

## Overview

PHASE 6 implements event-driven synchronization between AUDIT mode and the Master Plan Observatory dashboard. When AUDIT mode detects variance in plan execution, the dashboard automatically updates with latest metrics.

## Sync Mechanism

### Variance Detection Thresholds

| Variance Level | Threshold | Action |
|---|---|---|
| **Critical** | >20% | Silent auto-sync (no user notification) |
| **Warning** | 10-20% | Notify user + sync |
| **Acceptable** | <10% | No action needed |

### Event Flow

```
AUDIT Mode Execution
    ↓
Variance Analysis (compare phases vs expected)
    ↓
Calculate variance score (0-100%)
    ↓
Variance > 20%? 
    ├─ YES → Silent auto-sync (trigger PLAN_SYNC event)
    └─ NO → Continue with variance > 10%?
         ├─ YES → Warn user + update dashboard
         └─ NO → No action
    ↓
Update: cortex-registry/_cortex-master/dashboard/data/plan-summary.json
    ↓
Emit: PLAN_SYNC_COMPLETE event
    ↓
Dashboard listeners refresh (via JavaScript poll)
```

### Integration Points

1. **cortex-auditor.md (P1 Check)**
   - Add Plan Registry Coherence check
   - Calculate variance based on:
     - Active phase status changes
     - Enhancement adoption tracking
     - Completion rate variance
     - Timeline deviations

2. **AUDIT Mode Output**
   - Display variance percentage in executive summary
   - Show which metrics changed
   - Notify of silent sync (if >20%)

3. **Dashboard (index.html)**
   - Poll plan-summary.json every 60 seconds
   - Auto-refresh tabs when data changes
   - Show sync timestamp in footer

### Variance Calculation Formula

```
Variance Score = |Current State - Expected State| / Expected State × 100

Where:
- Current State: Actual phase completion + enhancement adoption
- Expected State: Target metrics from index.yaml
```

### Auto-Sync Debounce

- **Debounce Interval:** 60 seconds (prevent excessive updates)
- **Check Interval:** 5 minutes (AUDIT runs every 5 min by default)
- **Result:** Max 1 sync per 60-second window

## Implementation Checklist

### Step 1: Create plan-summary.json (Data Container)
```yaml
Location: cortex-registry/_cortex-master/dashboard/data/plan-summary.json
Format: JSON (embedded in dashboard or standalone)
Content:
  - Active phases (3 entries)
  - Completed phases (16 entries)
  - Active enhancements (1 entry)
  - Statistics (completion %, last updated timestamp)
  - Variance metrics
```

### Step 2: Update cortex-auditor.md
```yaml
Add P1 Check:
  - Name: "Plan Registry Coherence"
  - Target: index.yaml + plan-summary.json sync
  - Validation: Compare phase status with actual development
  - Variance Calculation: Score and threshold checks
```

### Step 3: Create AUDIT Sync Logic
```yaml
Location: cortex/orchestrators/core/plan_registry_sync.py (NEW)
Functions:
  - calculate_variance()
  - should_trigger_sync()
  - update_dashboard_metrics()
  - emit_sync_event()
```

### Step 4: Dashboard JavaScript Polling
```javascript
// Add to dashboard/index.html (already template-ready)
setInterval(() => {
  fetch('./data/plan-summary.json')
    .then(r => r.json())
    .then(data => updateDashboard(data))
}, 60000); // Poll every 60 seconds
```

### Step 5: Git Event Capture
```yaml
After sync:
  - Log variance score to governance audit trail
  - Record sync event with timestamp
  - Track adoption metrics
  - Enable historical trending
```

## Dashboard Update Data Structure

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2026-02-05T14:37:22Z",
    "variance_score": 5.2,
    "variance_threshold": 10.0,
    "silent_sync": false
  },
  "statistics": {
    "total_phases": 19,
    "active_phases": 3,
    "completed_phases": 16,
    "active_enhancements": 1,
    "completion_rate": 85
  },
  "active_phases": [
    {
      "number": 21,
      "name": "JSON-First Rewrite",
      "progress": 35,
      "priority": "P0",
      "started": "2026-02-01"
    },
    {
      "number": 22,
      "name": "ASK Mode System",
      "progress": 25,
      "priority": "P0",
      "started": "2026-02-03"
    },
    {
      "number": 23,
      "name": "Static Dashboard Generator",
      "progress": 40,
      "priority": "P0",
      "started": "2026-02-04"
    }
  ],
  "active_enhancements": [
    {
      "id": "ENH-029",
      "name": "Capability Feasibility Gate",
      "priority": "P1",
      "progress": 0,
      "phases": 4,
      "effort_days": 12
    }
  ]
}
```

## Monitoring & Verification

### Health Checks
- ✅ Variance calculation accuracy (manual test vs formula)
- ✅ Sync timing meets debounce constraints
- ✅ Dashboard data always fresh within 60s
- ✅ No cascade sync loops

### Logs to Verify
```
AUDIT Mode:
  - "Variance calculated: 5.2% (ACCEPTABLE)"
  - "Variance 23% detected - triggering silent sync"
  - "Plan registry sync completed"

Dashboard:
  - "Poll returned fresh data: 2026-02-05T14:37:22Z"
  - "Dashboard updated with new metrics"
```

## Phase 6 Timeline

| Task | Duration | Status |
|---|---|---|
| Create plan-summary.json | 30 min | ⚪ Pending |
| Update cortex-auditor.md | 20 min | ⚪ Pending |
| Implement sync logic (Python) | 1 hour | ⚪ Pending |
| Add dashboard polling | 15 min | ⚪ Pending |
| Testing & verification | 30 min | ⚪ Pending |
| **Total** | **~2.5 hours** | ⚪ Pending |

## Success Criteria

✅ AUDIT mode detects >20% variance and silently syncs  
✅ Dashboard refreshes automatically every 60 seconds  
✅ Variance scores logged to governance audit trail  
✅ No cascade sync loops or performance degradation  
✅ All metrics accurately reflect current state  
✅ Integration tests passing (dashboard polling)

## Next Steps

1. Create `cortex-registry/_cortex-master/dashboard/data/plan-summary.json`
2. Implement variance detection in cortex-auditor.md
3. Create plan_registry_sync.py with core logic
4. Test dashboard polling and data freshness
5. Verify governance audit trail captures all events
6. Final git commit with Phase 6 complete marker

---

**Ready for Implementation:** Phase 6 architecture documented and ready for autonomous execution.
