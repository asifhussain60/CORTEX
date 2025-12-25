# 🚀 Quick Start Guide

## Problem: CORS Error (Data Load Failed)

**Symptom:** Opening `dashboard.html` directly shows "Data Load Failed" error

**Root Cause:** Browsers block loading local JSON files via `file://` protocol (CORS security)

**Solution:** Use a web server instead

---

## ✅ How to View Dashboard

### Option 1: Python HTTP Server (Recommended)
```bash
cd cortex-brain/documents/analysis/INTELLIGENT-UX-DEMO
python3 -m http.server 8080
```

Then open: **http://localhost:8080/dashboard.html**

### Option 2: NPM Script (Alternative)
```bash
cd cortex-brain/documents/analysis/INTELLIGENT-UX-DEMO
npm run serve
```

Then open: **http://localhost:8080/dashboard.html**

### Option 3: VS Code Live Server
1. Install "Live Server" extension in VS Code
2. Right-click `dashboard.html` → "Open with Live Server"

---

## 🧪 Run Playwright Tests

### Prerequisites
```bash
# Install dependencies (one-time)
npm install
npx playwright install
```

### Run Tests

**Interactive UI Mode (Best for development):**
```bash
npm run test:ui
```

**Headless Mode (CI/CD):**
```bash
npm test
```

**Headed Mode (Watch tests run):**
```bash
npm run test:headed
```

**Debug Mode (Step through tests):**
```bash
npm run test:debug
```

**View Last Report:**
```bash
npm run test:report
```

---

## 📊 What Gets Tested

### Coverage: 133 Tests Across 6 Dashboard Tabs
1. **Data Loading** (10 tests) - JSON fetch, validation, error handling
2. **Executive Summary** (17 tests) - Scores, metadata, metrics
3. **Architecture** (14 tests) - Component graph, relationships
4. **Quality** (18 tests) - Heatmap, code smells, refactoring
5. **Roadmap** (20 tests) - Sankey diagram, tasks, timeline
6. **Performance** (19 tests) - Flamegraph, bottlenecks, optimization
7. **Security** (22 tests) - Risk matrix, vulnerabilities, compliance
8. **Visual Regression** (13 tests) - Screenshot comparisons

### Browser Coverage: 5 Browsers
- ✅ Chromium (Desktop)
- ✅ Firefox (Desktop)
- ✅ WebKit (Desktop)
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 12)

---

## 🔧 Troubleshooting

### "Cannot find module '@playwright/test'"
**Solution:** Run `npm install` in the INTELLIGENT-UX-DEMO directory

### "Error: browserType.launch: Executable doesn't exist"
**Solution:** Run `npx playwright install` to download browser binaries

### "Failed to load analysis-data.json"
**Solution:** Start web server (see "How to View Dashboard" above)

### Port 8080 Already in Use
**Solution:** Kill existing server or use different port:
```bash
python3 -m http.server 8081
# Then update baseURL in playwright.config.js
```

---

## 📁 Project Structure

```
INTELLIGENT-UX-DEMO/
├── dashboard.html              # Main dashboard UI
├── analysis-data.json          # Real CORTEX project data
├── assets/
│   ├── css/styles.css         # Dashboard styling
│   └── js/visualizations.js   # D3.js rendering logic
├── tests/
│   ├── fixtures/test-helpers.js  # Shared utilities
│   ├── 01-data-loading.spec.js
│   ├── 02-executive-summary.spec.js
│   ├── 03-architecture-tab.spec.js
│   ├── 04-quality-tab.spec.js
│   ├── 05-roadmap-tab.spec.js
│   ├── 06-performance-tab.spec.js
│   ├── 07-security-tab.spec.js
│   └── 08-visual-regression.spec.js
├── playwright.config.js        # Test configuration
├── package.json               # Dependencies
└── jsconfig.json              # TypeScript/IDE config
```

---

## 🎯 Key Features

### Real Data Integration
- ✅ NO mock data fallbacks
- ✅ Validates against actual CORTEX metrics
- ✅ Error UI provides troubleshooting steps

### Test Assertions
- **Metadata:** Project name, version, 247 files, 45,623 lines
- **Scores:** Overall: 72, Complexity: 68, Maintainability: 75, Test: 70
- **Architecture:** 6 components, 8 relationships, force-directed graph
- **Quality:** 8 code smells, complexity heatmap, refactoring backlog
- **Roadmap:** 7 tasks, Sankey flow diagram
- **Performance:** 5 bottlenecks, flamegraph visualization
- **Security:** 2 critical, 4 high, 6 medium vulnerabilities

---

## 🚀 Next Steps

1. **Start Server:** `python3 -m http.server 8080`
2. **View Dashboard:** Open http://localhost:8080/dashboard.html
3. **Run Tests:** `npm run test:ui` (interactive mode)
4. **Review Report:** Test results in `test-results/html-report/`

---

**Status:** ✅ All setup complete - Ready to view and test!
