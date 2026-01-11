# Plan Viewer Progress Bars Update

**Date:** 2026-01-11  
**Status:** ✓ Complete

## Changes Applied

### 1. Overall Progress Bar (Hero Section)
Added prominent overall progress bar in hero section showing:
- Overall completion percentage (35%)
- AC-IDs completed (36/102)
- Phases completed (1/5)
- Visual progress bar with gradient fill

**Location:** Directly below hero metadata, before content area

### 2. Phase-Level Progress Bars
Enhanced existing phase cards with:
- Individual progress bars per phase
- Color-coded by status (completed/in-progress/blocked)
- AC-ID completion count (e.g., "33/34")
- Percentage display (e.g., "97%")

**Location:** Phase Overview section, each phase card

## Visual Hierarchy

```
Hero Section
├── Metadata (status, AC-IDs, phase, updated)
├── Overall Progress Bar ⭐ NEW
│   ├── Percentage: 35%
│   ├── AC-IDs: 36/102
│   └── Phases: 1/5
└── [Content sections below]

Phase Overview
├── Phase 1 Card
│   ├── Header (name, status badge)
│   ├── Metrics (AC-IDs, progress %)
│   ├── Progress Bar ⭐ ENHANCED
│   └── Description
├── Phase 2 Card (same structure)
└── ...
```

## Technical Details

### Overall Progress Bar
- Height: 12px (larger than phase bars for prominence)
- Color: Gradient (cyber cyan → green)
- Updates dynamically from `plan_metadata.completed_ac_ids`
- Shows both AC-ID and phase completion counts

### Phase Progress Bars
- Height: 8px (standard)
- Color: Status-based (green/orange/red/grey)
- Updates from `phase.completion_percentage`
- Individual per phase

## Files Modified

1. `cortex-brain/cx6-plan/viewer/plan-viewer.html`
   - Added overall progress bar HTML structure
   - Updated `updateHeroSection()` to populate overall progress
   - Enhanced phase card progress bars (already existed)

## Testing Verification

Run `open cortex-brain/cx6-plan/viewer/plan-viewer.html` to verify:
- [ ] Overall progress bar shows 35% (36/102 AC-IDs)
- [ ] Phase 1 progress bar shows 97% (33/34)
- [ ] Phase 1.5 progress bar shows 100% (3/3)
- [ ] Phases 2-4 show 0%
- [ ] Colors match status (green = complete, orange = in progress, grey = not started)

## Integration with State

Progress bars sync with:
- `cortex-brain/tier1/tracking/progress-tracker.json`
- `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- `cortex-brain/cx6-plan/viewer/plan-viewer-data.json`

Updated by state synchronizer to maintain accuracy.

---

**Next:** Test in browser to verify visual appearance and responsiveness.
