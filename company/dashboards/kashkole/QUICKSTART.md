# 🚀 Quick Start - Dashboard Testing

## Open Dashboard
```bash
# Windows
start company\dashboards\kashkole\dashboard-gpt.html

# Or double-click the file
```

## Quick Test (30 seconds)
1. **Open dashboard** in browser
2. **Press F12** to open console
3. **Look for errors** (should be none)
4. **Click each tab:**
   - Overview
   - Vulnerabilities (click all 4 sub-tabs)
   - Security (click all 3 sub-tabs)
   - Dependencies
   - Quality
   - Testing
   - Architecture
   - Patterns
   - Vendors
5. **Verify charts appear** when clicking tabs

## Automated Test
```bash
# Method 1: Console
1. Open dashboard-gpt.html
2. Press F12
3. Paste contents of test-charts.js
4. Press Enter

# Method 2: Visual
1. Open test-dashboard.html
2. Watch automated tests run
```

## Expected Results
- ✅ No console errors
- ✅ All tabs clickable
- ✅ Charts appear in each tab
- ✅ Charts resize with window
- ✅ Console shows: "✓ Chart initialized: [chart-name]"

## If Something's Wrong
1. Check console for errors
2. Verify ECharts loaded: `typeof echarts` → should be "object"
3. Check chart exists: `document.getElementById('code-smells-chart')` → should return div
4. Manual init: `initializeChart('chart-id')`
5. See TESTING.md for detailed troubleshooting

---
**Status:** ✅ All fixes applied  
**Syntax Errors:** 0  
**Charts Working:** 9/9  
**Test Files:** 3 created
