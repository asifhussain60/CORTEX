# Quick Start Guide - Dashboard Test Suite

## 🎯 What Was Created

### Problem Fixed
- **Circular Dependency:** `app.js` → `keyboard-navigation.js` → `export-utils.js` → `loading-animations.js` → (circular)
- **Solution:** Created `shared-utils.js` with zero dependencies, updated imports

### Test Suite Structure

```
cortex-brain/dashboards/ui/
├── shared-utils.js              ⭐ NEW - Breaks circular dependency
├── test-modules.html            ⭐ NEW - Diagnostic tool
│
├── tests/                       ⭐ NEW - Complete test suite
│   ├── fixtures/
│   │   └── mock-data.js         # Test data (180 lines)
│   │
│   ├── unit/                    # 50 tests
│   │   ├── data-loader.test.js
│   │   └── shared-utils.test.js
│   │
│   ├── integration/             # 80 tests
│   │   ├── dashboard-app.test.js
│   │   └── components.test.js
│   │
│   ├── e2e/                     # 40 tests
│   │   └── dashboard.e2e.test.js
│   │
│   ├── package.json             # Test dependencies
│   ├── .babelrc                 # Babel config
│   ├── run-tests.sh             # Test runner (executable)
│   └── README.md                # 450+ lines documentation
```

**Total: 170 tests, 2,566 lines of code**

---

## 🚀 How to Use

### Step 1: Verify Dashboard Fixed

Open in browser:
```
http://localhost:8080/test-modules.html
```

Expected result: **All 6 tests PASS** ✅
- ✓ shared-utils.js loaded
- ✓ export-utils.js loaded
- ✓ keyboard-navigation.js loaded
- ✓ app.js loaded
- ✓ No circular dependencies
- ✓ Mock data accessible

### Step 2: Test Dashboard

Open in browser:
```
http://localhost:8080/index.html?source=mock
```

Expected result: **Dashboard displays** ✅
- Overview tab shows metrics
- All 7 tabs functional
- Data visualizations render
- No blank screen

### Step 3: Run Test Suite

```bash
# Navigate to test directory
cd cortex-brain/dashboards/ui/tests

# Install dependencies (first time only)
npm install

# Run all tests
./run-tests.sh
```

Expected result: **~170 tests PASS** ✅

---

## 📊 Test Categories

### 1. Unit Tests (50 tests)
**Run:** `./run-tests.sh unit`

Tests individual modules in isolation:
- Data loading and caching
- Utility functions (toast, loading, formatting)
- Error handling
- Data validation

**Time:** ~5 seconds

### 2. Integration Tests (80 tests)
**Run:** `./run-tests.sh integration`

Tests component integration:
- App initialization
- Tab switching
- Data flow
- All 7 component tabs
- Error recovery

**Time:** ~15 seconds

### 3. End-to-End Tests (40 tests)
**Run:** `./run-tests.sh e2e`

Tests full user workflows:
- Dashboard loading
- Mouse navigation
- Keyboard shortcuts
- Data export
- Responsive design
- Accessibility

**Time:** ~45 seconds

### 4. Coverage Report
**Run:** `./run-tests.sh coverage`

Generates HTML coverage report in `coverage/` directory.

**Target:** 70% coverage (branches, functions, lines, statements)

---

## 🎯 Quick Commands

```bash
# Single command test everything
./run-tests.sh

# Run specific suite
./run-tests.sh unit
./run-tests.sh integration
./run-tests.sh e2e

# Watch mode (re-run on file changes)
npm run test:watch

# Debug mode
npm run test:debug

# Verbose output
npm run test:verbose
```

---

## 🐛 Troubleshooting

### Issue: "Cannot find module"
**Fix:**
```bash
cd cortex-brain/dashboards/ui/tests
npm install
```

### Issue: "Navigation timeout" (E2E tests)
**Fix:**
```bash
# Ensure server running
cd cortex-brain/dashboards/ui
python3 -m http.server 8080
```

### Issue: Dashboard still blank
**Verify:**
1. Check browser console for errors
2. Open `test-modules.html` first (diagnostic)
3. Verify all 6 module tests pass
4. Check network tab for failed requests

---

## 📝 What Each Test File Does

### `unit/data-loader.test.js`
- Tests `loadDashboardData()` function
- Tests caching behavior
- Tests error handling (network, 404, invalid JSON)
- Tests export functions (JSON, CSV)

### `unit/shared-utils.test.js`
- Tests toast notifications (success, error, warning)
- Tests loading overlay (show, hide, update)
- Tests DOM utilities
- Tests formatting functions
- Tests debounce/throttle

### `integration/dashboard-app.test.js`
- Tests app initialization
- Tests tab switching (all 7 tabs)
- Tests data source switching (mock/live)
- Tests data refresh
- Tests error recovery
- Tests performance (caching)

### `integration/components.test.js`
- Tests all 7 tab components:
  1. Overview (health metrics)
  2. Tech Stack (languages, frameworks)
  3. Security (vulnerabilities, compliance)
  4. Architecture (modules, layers, complexity)
  5. Code Organization (files, directories, metrics)
  6. Team Metrics (contributors, commits, activity)
  7. Vendors (vendors, costs, categories)

### `e2e/dashboard.e2e.test.js`
- Tests full user workflows with real browser
- Tests keyboard shortcuts (Ctrl+1-7, Ctrl+R, etc.)
- Tests data export (JSON, PDF)
- Tests responsive design (mobile, tablet, desktop)
- Tests accessibility (ARIA, keyboard navigation)
- Tests performance (load time, tab switching)

---

## 📈 Success Criteria

Dashboard is working if:
- ✅ `test-modules.html` shows 6 green checkmarks
- ✅ `index.html?source=mock` displays data (no blank screen)
- ✅ All 7 tabs are clickable and show content
- ✅ Test suite passes (~170 tests)
- ✅ No console errors in browser

---

## 🎉 You're Done When...

1. **Module test passes:** `http://localhost:8080/test-modules.html` → All green ✅
2. **Dashboard loads:** `http://localhost:8080/index.html?source=mock` → Shows data ✅
3. **Tests pass:** `./run-tests.sh` → 170 tests pass ✅

---

## 📚 Full Documentation

For detailed information, see:
- **Test Suite Guide:** `tests/README.md` (450+ lines)
- **Completion Report:** `cortex-brain/documents/reports/dashboard-test-suite-report.md`

---

**Need Help?**
1. Check `tests/README.md` troubleshooting section
2. Verify HTTP server running: `lsof -ti:8080`
3. Check browser console for errors
4. Run diagnostic: `http://localhost:8080/test-modules.html`

---

**Created:** December 4, 2024  
**Author:** Asif Hussain  
**Status:** ✅ Complete - All 8 tasks finished
