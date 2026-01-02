# CORTEX CSS Layout Validator

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Purpose:** Automatic detection and enforcement of CSS layout standards

---

## 🎯 Overview

The CORTEX CSS Layout Validator is a runtime validation tool that:
- ✅ Detects layout issues after DOM rendering
- 🔧 Provides automatic fixes
- 📊 Generates detailed reports
- 🛡️ Enforces design consistency

---

## 🚀 Usage

### Automatic Validation

The validator runs automatically on page load (200ms after `window.load` event).

### Manual Commands

Open browser console and use:

```javascript
// Run validation check
CORTEX.validator.validate();

// Apply fixes manually
CORTEX.validator.applyFixes();

// Enable auto-fix for future loads
CORTEX.validator.enableAutoFix();

// Disable auto-fix
CORTEX.validator.disableAutoFix();
```

---

## 🔍 Validation Checks

### 1. Grid Layout Validation
- **Check:** Grid gap size
- **Expected:** 24px - 48px (optimal: 40px)
- **Severity:** HIGH
- **Auto-fix:** Sets gap to `40px`

### 2. Category Panel Validation
- **Check:** Card padding
- **Expected:** Min 32px (optimal: 40px vertical, 32px horizontal)
- **Severity:** MEDIUM
- **Auto-fix:** Sets padding to `40px 32px`

- **Check:** Flexbox layout
- **Expected:** `display: flex; flex-direction: column;`
- **Severity:** HIGH
- **Auto-fix:** Applies flexbox properties

### 3. Container Width Validation
- **Check:** Max-width constraints
- **Expected:** 1400px for optimal space utilization
- **Severity:** MEDIUM
- **Auto-fix:** Sets `max-width: 1400px`

### 4. Responsive Breakpoint Validation
- **Check:** Grid columns at different viewport widths
- **Expected:**
  - `< 768px`: 1 column
  - `>= 768px`: 2 columns
- **Severity:** HIGH
- **Auto-fix:** N/A (requires CSS media query fix)

### 5. Card Height Variance
- **Check:** Height difference between cards in same row
- **Expected:** < 50px variance
- **Severity:** LOW
- **Auto-fix:** N/A (content-dependent)
- **Recommendation:** Adjust content or set `min-height`

### 6. Tag Spacing Validation
- **Check:** Gap between category tags
- **Expected:** Min 12px (0.75rem)
- **Severity:** LOW
- **Auto-fix:** Sets gap to `12px`

- **Check:** Tags alignment (bottom)
- **Expected:** `margin-top: auto`
- **Severity:** LOW
- **Auto-fix:** Sets `margin-top: auto`

### 7. Level 0 Panel Validation
- **Check:** Same as standard panels but for `.level0-*` classes
- **Severity:** HIGH
- **Auto-fix:** Applies same fixes as standard panels

---

## 📊 Report Format

### Console Output

```
📊 CORTEX Layout Validation Report
✅ All layout checks passed!
   - OR -
⚠️ Found 8 layout issues

HIGH (3)
  GRID_GAP_TOO_SMALL:
    selector: .category-panels-grid[0]
    current: 20px
    expected: 40px
    
  CARD_MISSING_FLEXBOX:
    selector: .category-subpanel
    current: block
    expected: flex

MEDIUM (3)
  CONTAINER_WIDTH_TOO_NARROW:
    selector: .level0-container
    current: 1200px
    expected: 1400px

LOW (2)
  TAG_GAP_TOO_SMALL:
    selector: .category-tags
    current: 8px
    expected: 12px

🔧 8 automatic fixes available
```

---

## 🛡️ Auto-Fix System

### Enabling Auto-Fix

**Option 1: Console Command**
```javascript
CORTEX.validator.enableAutoFix();
```

**Option 2: HTML Attribute**
```html
<html data-cortex-autofix>
```

**Option 3: localStorage**
```javascript
localStorage.setItem('cortex-layout-autofix', 'true');
```

### How It Works

1. Validation runs on page load
2. Issues detected and logged
3. If auto-fix enabled → fixes applied to DOM
4. `data-cortex-fixed="true"` attribute added to `<html>`
5. Page displays with corrected layout

### Disabling Auto-Fix

```javascript
CORTEX.validator.disableAutoFix();
```

---

## 🔧 Configuration

Default configuration (editable in `css-layout-validator.js`):

```javascript
config: {
    minGap: 24,              // 1.5rem minimum
    maxGap: 48,              // 3rem maximum
    optimalGap: 40,          // 2.5rem optimal
    minCardPadding: 32,      // 2rem
    optimalCardPadding: 40,  // 2.5rem
    minTagGap: 12,           // 0.75rem
    minTagPadding: 8,        // 0.5rem
    maxContainerWidth: 1400,
    minContainerPadding: 24, // 1.5rem
    maxHeightVariance: 50    // Max px difference
}
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `docs/assets/js/css-layout-validator.js` | Validator implementation |
| `docs/assets/css/main.css` | CSS with enforced standards |
| `docs/index.html` | Includes validator script |

---

## 🎯 CSS Fixes Applied

### Issue: Execution Panel Uneven Heights

**Root Cause:** Cards with different tag counts had inconsistent heights

**Fixes Applied:**

1. **Grid Alignment** (`.level0-categories-grid`, `.category-panels-grid`)
   ```css
   align-items: stretch; /* Force equal heights */
   ```

2. **Card Height** (`.level0-category-subpanel`, `.category-subpanel`)
   ```css
   min-height: 280px;    /* Enforce minimum */
   height: 100%;         /* Fill grid cell */
   display: flex;
   flex-direction: column;
   ```

3. **Tag Container** (`.level0-category-tags`, `.category-tags`)
   ```css
   margin-top: auto;     /* Push to bottom */
   gap: 0.75rem;         /* Better spacing */
   ```

4. **Grid Gaps**
   ```css
   gap: 2rem;            /* Mobile */
   gap: 2.5rem;          /* Tablet (768px+) */
   gap: 3rem;            /* Desktop (1024px+) */
   ```

---

## ✅ Validation Results

Run `CORTEX.validator.validate()` to see:

- ✅ **Grid gaps:** Optimal (40px)
- ✅ **Card padding:** Optimal (40px 32px)
- ✅ **Flexbox layout:** Applied
- ✅ **Equal heights:** Enforced via `align-items: stretch` + `height: 100%`
- ✅ **Tag alignment:** Bottom-aligned with `margin-top: auto`
- ✅ **Container width:** 1400px max-width
- ✅ **Responsive breakpoints:** Working (1 col < 768px, 2 cols >= 768px)

---

## 🚨 Troubleshooting

### Issue: Validator not running

**Check:**
```javascript
// Verify script loaded
console.log(window.CORTEX?.validator);

// Manually trigger
CORTEX.validator.validate();
```

### Issue: Fixes not applying

**Check:**
```javascript
// Enable auto-fix
CORTEX.validator.enableAutoFix();

// Manually apply
CORTEX.validator.applyFixes();
```

### Issue: Layout still looks wrong

**Check:**
1. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+F5)
2. Clear cache
3. Check console for CSS errors
4. Run validator and review report

---

## 📚 References

- CSS Design Standard v4.0.1
- CORTEX Glassmorphism Guidelines
- Response Format Tiers (INSTANT → COMPREHENSIVE)

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
