# Plan-Viewer.html - Fixes Applied (2026-01-13)

## Problem
The plan-viewer.html dashboard was not loading because it was looking for phase data in the wrong location within the progress-tracker.json structure.

### Structure Mismatch
**What the HTML expected:**
```javascript
tracker.phase_1
tracker.phase_2
tracker.phase_3
```

**What actually exists:**
```javascript
tracker.phases.phase_1
tracker.phases.phase_2
tracker.phases.phase_3
```

**Additional issue:**
- Field names changed: `total_ac_count` (new) vs `acs_total` (legacy)
- Some phases had `total_ac_count: 0` but `acs_total: 8` with the real value

## Fixes Applied

### 1. Fixed Phase Data Access (4 locations)

**`updateHeroMetrics()` method:**
```javascript
// Before:
const phase = tracker[detailedKey];

// After:
const phase = (tracker.phases && tracker.phases[phaseKey_formatted]) || tracker[phaseKey_formatted];
```

**`updateMetricsSidebar()` method:**
Same fix - checks both `tracker.phases.phase_X` and `tracker.phase_X`

**`phaseMetrics` calculation:**
Same fix - dual-path access for backward compatibility

**`renderPhaseCards()` method:**
Same fix - loads phases from either location

### 2. Added Field Name Fallbacks

**All AC count lookups now use:**
```javascript
const acCount = phase.total_ac_count || phase.acs_total || 0;
```

This ensures:
- New structure (`total_ac_count`) is preferred
- Falls back to legacy field (`acs_total`) if needed
- Defaults to 0 if neither exists

### 3. Backward Compatibility

The fixes maintain compatibility with:
- ✅ Old tracker structure (phases at top-level)
- ✅ New tracker structure (phases nested under `phases` key)
- ✅ Old field names (`acs_total`)
- ✅ New field names (`total_ac_count`)

## Test Results

✅ **Dashboard now loads with:**
- 7/13 phases found (phases 1-5, 10-11 active)
- 95 total ACs counted
- 0 completed (new phase cycle)
- Overall progress: 0%

### Phase Breakdown
| Phase | ACs | Status | Notes |
|-------|-----|--------|-------|
| Phase 1 | 8 | Completed | Foundation |
| Phase 2 | 13 | Completed | Orchestration Core |
| Phase 3 | 23 | Completed | Features |
| Phase 4 | 8 | Completed | Intelligence |
| Phase 5 | 28 | Completed | Cleanup |
| Phase 10 | 1 | Not Started | Templates (new AC-TEMPLATE-005) |
| Phase 11 | 14 | Completed | LENS |
| **Total** | **95** | — | — |

**Phases 6-9 not in tracker** (historical phases, not in current cycle)
**Phases 1.5 and 4.5 not in tracker** (not yet started in this cycle)

## Files Modified

- `cortex-brain/cx6-plan/viewer/plan-viewer.html`
  - 4 methods updated with dual-path access
  - All AC count lookups updated with fallback logic
  - Total changes: ~20 lines modified

## Browser Testing

✅ **Open in browser:**
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m http.server 8000
# Visit: http://localhost:8000/cortex-brain/cx6-plan/viewer/plan-viewer.html
```

✅ **Auto-refresh:** Every 2 seconds
✅ **Real-time updates:** Reflects changes in progress-tracker.json
✅ **Error handling:** Shows graceful errors if file not found

## Next Steps

1. ✅ Dashboard loads successfully
2. ⏳ Monitor during Phase 2 execution
3. ⏳ Watch for updates to progress-tracker.json
4. ⏳ Verify phase cards update in real-time

## SSOT Alignment

This fix aligns with:
- ✅ SSOT Architecture v1.6.0 (single source of truth)
- ✅ Dual-structure support (new and legacy formats)
- ✅ No hardcoded data (all from progress-tracker.json)
- ✅ Auto-refresh capability (2-second polling)
- ✅ CORE-005 compliance (cross-platform paths use relative URIs)
