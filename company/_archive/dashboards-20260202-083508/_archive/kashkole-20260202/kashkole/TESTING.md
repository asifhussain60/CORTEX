# Dashboard Chart Loading Tests

## 🎯 Purpose
Verify that all charts in dashboard-gpt.html load correctly with the lazy loading implementation.

## 📋 Test Files

### 1. test-charts.js (Console Test)
**Quick browser console test**

**Usage:**
1. Open `dashboard-gpt.html` in your browser
2. Open browser developer console (F12)
3. Copy and paste the contents of `test-charts.js`
4. Press Enter to run tests

**What it checks:**
- ✅ Chart containers exist in DOM
- ✅ Containers have proper dimensions
- ✅ ECharts library loaded
- ✅ Chart instances initialized (or pending lazy load)

**Expected output:**
```
🧪 CORTEX Dashboard Chart Tests
==================================================
📊 Running Chart Tests...

✅ PASS Code Smells Chart [Vulnerabilities > Code Smells]
   └─ Chart initialized (400x300px)
⏳ PENDING Anti-Patterns Chart [Vulnerabilities > Anti-Patterns]
   └─ Container exists but chart not yet initialized (lazy loading)
...

==================================================
📊 Test Summary
==================================================
✅ Passed: 9
❌ Failed: 0
📝 Total: 9
```

---

### 2. test-dashboard.html (Visual Test Suite)
**Full automated test with visual UI**

**Usage:**
1. Open `test-dashboard.html` in your browser
2. Tests run automatically
3. View results in color-coded panels

**Features:**
- Real-time test execution
- Visual pass/fail indicators
- Detailed error messages
- Summary statistics

**Test Coverage:**
- 📊 Vulnerabilities Tab: 4 charts
- 🔒 Security Tab: 1 chart
- 📦 Dependencies Tab: 1 chart
- 📈 Quality Tab: 2 charts
- 🧪 Testing Tab: 1 chart

---

## 🚀 Quick Start

### Method 1: Console Test (Fastest)
```bash
# 1. Open dashboard in browser
start dashboard-gpt.html

# 2. In browser console:
# Copy/paste contents of test-charts.js
```

### Method 2: Visual Test Suite
```bash
# Open test dashboard
start test-dashboard.html

# Tests run automatically
# View results in browser
```

---

## 📊 Charts Being Tested

| Chart ID | Chart Name | Tab Location | Type |
|----------|-----------|--------------|------|
| `code-smells-chart` | Code Smells Distribution | Vulnerabilities > Code Smells | Donut |
| `anti-patterns-chart` | Anti-Patterns | Vulnerabilities > Anti-Patterns | Horizontal Bar |
| `security-chart` | OWASP Top 10 | Vulnerabilities > Security | Vertical Bar |
| `best-practices-chart` | Best Practices Compliance | Vulnerabilities > Best Practices | Radar |
| `dep-audit-chart` | Dependency Vulnerabilities | Security > Dependency Audit | Pie |
| `license-chart` | License Distribution | Dependencies | Bar |
| `complexity-chart` | Complexity Distribution | Quality | Bar |
| `duplication-chart` | Duplication by Module | Quality | Gradient Bar |
| `coverage-trend-chart` | Coverage Over Time | Testing | Line/Area |

---

## 🔧 Troubleshooting

### Chart Not Loading?

**1. Check container exists:**
```javascript
document.getElementById('chart-id')
// Should return: <div id="chart-id" style="height: 400px;"></div>
```

**2. Check ECharts loaded:**
```javascript
typeof echarts
// Should return: "object"
```

**3. Check chart configuration:**
```javascript
// In dashboard console:
Object.keys(chartConfigs)
// Should include all 9 chart IDs
```

**4. Check initialization:**
```javascript
echarts.getInstanceByDom(document.getElementById('chart-id'))
// Should return chart instance or null (if lazy loading)
```

**5. Manually trigger initialization:**
```javascript
initializeChart('chart-id')
// Check console for "✓ Chart initialized: chart-id"
```

---

## ✅ Expected Behavior

### Lazy Loading
Charts initialize only when their tab becomes active:

1. **Page Load**: No charts initialized
2. **Click Tab**: Charts in that tab initialize
3. **Click Sub-Tab**: Charts in sub-tab initialize
4. **Subsequent Visits**: Charts already initialized

### Console Logs
You should see initialization logs:
```
✓ Chart initialized: code-smells-chart
✓ Chart initialized: anti-patterns-chart
...
```

---

## 🐛 Common Issues

### Issue 1: All Tests Fail
**Cause:** ECharts library not loaded  
**Fix:** Check network tab for CDN failures

### Issue 2: Charts Pending Forever
**Cause:** Lazy loading not triggered  
**Fix:** Click on each tab to activate charts

### Issue 3: Dimensions 0x0
**Cause:** Container hidden or parent collapsed  
**Fix:** Ensure tab/sub-tab is active

### Issue 4: Syntax Errors
**Cause:** Malformed chartConfigs object  
**Fix:** Check browser console for JavaScript errors

---

## 📝 Test Checklist

Run through this manual checklist:

- [ ] Dashboard loads without errors
- [ ] Overview tab displays
- [ ] Click **Vulnerabilities** tab
  - [ ] Code Smells sub-tab shows chart
  - [ ] Anti-Patterns sub-tab shows chart
  - [ ] Security sub-tab shows chart
  - [ ] Best Practices sub-tab shows chart
- [ ] Click **Security** tab
  - [ ] Dependency Audit sub-tab shows chart
- [ ] Click **Dependencies** tab
  - [ ] License chart visible
- [ ] Click **Quality** tab
  - [ ] Complexity chart visible
  - [ ] Duplication chart visible
- [ ] Click **Testing** tab
  - [ ] Coverage trend chart visible
- [ ] Resize window - charts resize properly

---

## 🎉 Success Criteria

**All tests pass when:**
- ✅ 9/9 chart containers exist in DOM
- ✅ ECharts library loaded successfully
- ✅ Charts initialize on tab activation
- ✅ Charts resize with window
- ✅ No console errors
- ✅ Visual appearance matches design

---

**Version:** 1.0  
**Last Updated:** 2026-02-02  
**Dashboard File:** dashboard-gpt.html  
**Author:** CORTEX Team
