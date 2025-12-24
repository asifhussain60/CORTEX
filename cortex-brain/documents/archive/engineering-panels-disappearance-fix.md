# Engineering Tab Panels Disappearance - Root Cause & Fix

## Issue

All panels disappeared from Engineering tab after height balance fix was applied.

## Root Cause

**Duplicate CSS Definition:**
```css
/* First definition at line 137 (CORRECT) */
.stage-content {
    background: var(--glass-bg); 
    border: 1px solid var(--glass-border); 
    /* ... other styles ... */
    display: flex;
    flex-direction: column;
    height: 100%;
}

/* Second definition at line 184 (DUPLICATE - REMOVED) */
.stage-content { 
    position: relative;
    background: var(--glass-bg); 
    /* ... duplicate styles ... */
}
```

**Problem:** The second definition was accidentally left in during the height balance refactor, overriding the first correct definition. This caused layout conflicts.

## Fix Applied

**File:** `cortex-brain/dashboards/ui/styles/engineering-onboarding.css`

**Change:** Removed duplicate `.stage-content` definition at lines 184-194

**Result:**
- Single unified `.stage-content` definition with correct flex layout
- `height: 100%` properly applied
- Panels now visible and properly sized

## Prevention

When doing CSS refactoring:
1. Search for duplicate selectors before applying changes
2. Use `grep` to find all occurrences: `grep -n "^\.stage-content" file.css`
3. Consolidate definitions during refactor, not after

## Testing

✅ Panels visible in Engineering tab
✅ Height balance maintained (all panels equal height)
✅ Scrolling works correctly
✅ Completion button at bottom

---

**Author:** Asif Hussain | **Date:** December 7, 2025
