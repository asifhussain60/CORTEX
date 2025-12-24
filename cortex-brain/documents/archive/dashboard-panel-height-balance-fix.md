# Dashboard Panel Height Balance Fix

## Vision API Analysis

**Screenshot Analysis:**
- Left sidebar (wizard stepper): ~600px visible height
- Middle/Right content area: ~800px of content with internal scroll
- Panels end at different heights creating visual imbalance
- Too much nesting: `.onboarding-container` → `.wizard-content-area` → `.stage-content` → `.stage-content-body`

## Root Cause

1. **Engineering Tab**: Missing height constraints on container
2. **Other Tabs**: No unified height system for panel containers
3. **Excessive Nesting**: Multiple scrollable containers causing layout issues

## Solution Applied

### Engineering Tab (engineering-onboarding.css)

**Container Level:**
```css
.onboarding-container {
    height: calc(100vh - 250px);  /* Fixed height instead of min-height */
    align-items: stretch;          /* All children stretch to full height */
}
```

**Left Panel (Wizard Stepper):**
```css
.wizard-stepper {
    height: 100%;          /* Fill container height */
    overflow-y: auto;      /* Scrollable if content exceeds */
}
```

**Right Panel (Content Area):**
```css
.wizard-content-area {
    height: 100%;          /* Fill container height */
    overflow-y: auto;      /* Scrollable content */
}

.stage-content {
    height: 100%;          /* Fill available space */
    display: flex;
    flex-direction: column;
}

.stage-content-body {
    flex: 1;               /* Grow to fill space */
    overflow-y: auto;      /* Internal scroll for content */
}

.stage-completion-footer {
    margin-top: auto;      /* Push to bottom */
    flex-shrink: 0;        /* Don't shrink */
}
```

## Expected Result

✅ All 3 panels (left nav, middle content, right details) align at same height
✅ Borders visually align at bottom
✅ Natural scrolling within each panel
✅ Completion button stays at bottom of visible area
✅ No layout shift when switching tabs

## Files Modified

1. `cortex-brain/dashboards/ui/styles/engineering-onboarding.css` (lines 3-35, 134-160, 183-205, 227-235)

## Testing Checklist

- [ ] Engineering tab shows balanced heights
- [ ] Left stepper scrolls if stages exceed height
- [ ] Right content scrolls independently
- [ ] Completion button always visible at bottom
- [ ] Responsive on different screen sizes

---

**Author:** Asif Hussain | **Date:** December 7, 2025
