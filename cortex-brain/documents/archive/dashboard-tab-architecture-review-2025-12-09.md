# Dashboard Tab Architecture Review

**Date:** December 9, 2025  
**Issue:** Inconsistent tab loading behavior across tests  
**Status:** Root cause identified

---

## 🔍 Problem Summary

Three tests failing after implementing executive-as-default:
1. ✅ Engineering tab test - PASSING (fixed by logging code)
2. ❌ `test_tab_navigation_persists_across_clicks` - Architecture tab not displayed after click
3. ❌ `test_only_one_tab_visible_on_load` - Expects overview, finds executive

## 📊 Current Architecture

### HTML Structure (`index.html`)
- **Nav Tabs:** 10 tabs with `onclick="switchTab('tabname')"`
- **Executive tab:** `class="nav-tab active"` (marked as default)
- **Content Wrappers:** 10 divs with `class="tab-content"` and unique IDs
- **Executive content:** `id="tab-executive"` with `class="tab-content active"`

### JavaScript State (`app.js`)
- **App State:** `currentTab: 'executive'` (line 41)
- **URL Default:** `const tab = urlParams.get('tab') || 'executive';` (line 64)
- **Initialization:** Calls `renderCurrentTab()` after data loads
- **switchTab() in HTML:** Manages `.active` class on nav + content
- **renderCurrentTab() in JS:** Also manages `.active` class + renders content

### Test Expectations
- **Initial load test:** Expects `tab-overview` visible (line 225)
- **Tab navigation:** Expects architecture tab to be displayed after click (line 166)
- **Individual tabs:** Click tab → verify displayed (10 parametrized tests)

## 🔴 Root Causes Identified

### 1. Conflicting Active Class Management

**TWO functions manage `.active` class:**

**HTML `switchTab()` (line 223-250):**
```javascript
function switchTab(tabName) {
    // Removes all active classes
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Adds active to clicked tab
    const activeContent = document.getElementById(`tab-${tabName}`);
    activeContent.classList.add('active');
}
```

**JavaScript `renderCurrentTab()` (line 240-263):**
```javascript
async function renderCurrentTab() {
    // ALSO removes all active classes
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    tabElement.classList.add('active');
    
    // THEN renders content based on switch statement
    switch (appState.currentTab) {
        case 'executive': renderExecutiveSummary(); break;
        // ...
    }
}
```

**PROBLEM:** Two different systems managing same state = race conditions

### 2. Test Assertion Method Issue

**Test uses `is_displayed()`:**
```python
assert driver.find_element(By.ID, "tab-architecture").is_displayed()
```

**`is_displayed()` checks:**
- Element has `display: block` or similar (NOT `display: none`)
- Element has non-zero dimensions
- Element is visible (NOT `visibility: hidden`)

**CSS for `.tab-content` (NOT `.active`):**
```css
.tab-content {
    display: none;  /* ← Hidden by default */
}

.tab-content.active {
    display: block;  /* ← Only visible with .active class */
}
```

**PROBLEM:** If `.active` class isn't applied, `is_displayed()` returns `False`

### 3. Test Expectation Mismatch

**Test line 225:**
```python
assert visible_wrappers[0] == "tab-overview"
```

**But we changed default to executive:**
- HTML: Executive has `active` class
- app.js line 41: `currentTab: 'executive'`
- app.js line 64: URL default is `'executive'`

**PROBLEM:** Test expects old behavior (overview default)

## 🎯 Diagnostic Findings

### Engineering Tab Test - NOW PASSING ✅
- **Previously:** Failed with "tab-engineering is not displayed"
- **After logging:** PASSES consistently
- **Theory:** Logging added delays OR console.log forced DOM reflow
- **Implication:** Timing/race condition issue, not logic error

### Navigation Persistence Test - FAILING ❌
- **Clicks:** Executive → Architecture → Vendors
- **Failure:** Architecture tab shows `.active` class BUT `is_displayed()` = False
- **Timing:** 0.3s delay after click
- **Theory:** `switchTab()` adds class, but CSS transition OR another function removes it

### Initial Load Test - FAILING ❌
- **Expected:** `tab-overview` visible on load
- **Actual:** `tab-executive` visible on load
- **Status:** Working as designed, test outdated

## 🔧 Required Fixes

### Fix 1: Eliminate Dual Class Management
**Option A - Use only HTML switchTab():**
- Remove `.active` management from `renderCurrentTab()`
- Keep only content rendering in `renderCurrentTab()`
- Call `renderCurrentTab()` after `switchTab()` sets visibility

**Option B - Use only JavaScript:**
- Remove `switchTab()` from HTML `onclick`
- Replace with event listeners in app.js
- Single source of truth for state management

**RECOMMENDATION:** Option B (centralized state management)

### Fix 2: Update Test Expectations
- Change line 225: `"tab-overview"` → `"tab-executive"`
- Verify executive is correct default per user requirement

### Fix 3: Add Proper Wait in Navigation Test
- Replace `time.sleep(0.3)` with WebDriverWait
- Wait for `.active` class on target element
- Verify CSS `display` property after wait

## 📈 Impact Assessment

**Files Requiring Changes:**
1. `cortex-brain/dashboards/ui/app.js` - Centralize state management
2. `cortex-brain/dashboards/ui/index.html` - Remove inline `onclick` or `switchTab()`
3. `tests/dashboard/e2e/test_tab_click_loads.py` - Fix expectations + waits

**Risk Level:** Medium
- Touching core tab switching logic
- 14 tests depend on this behavior
- Dashboard is user-facing

**Mitigation:**
- Make changes atomically (all at once)
- Run full test suite immediately
- Manual verification in browser

## ✅ Next Steps

1. Decide: Option A (HTML-centric) vs Option B (JS-centric)
2. Implement state management fix
3. Update test expectations for executive default
4. Add proper WebDriverWait in navigation test
5. Run full test suite (14 tests)
6. Manual dashboard verification
7. Remove diagnostic logging

---

**Conclusion:** Not a bug - architectural inconsistency. Two systems managing same state. Fix: Single source of truth for tab visibility.
