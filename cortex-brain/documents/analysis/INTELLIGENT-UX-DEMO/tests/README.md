# Intelligent UX Dashboard - Test Suite

## Overview
Comprehensive Playwright UI test suite for the CORTEX Intelligent UX Enhancement Dashboard. Tests validate all 6 tabs with **real data** from `analysis-data.json` (NO mock data).

## Test Structure

```
tests/
├── fixtures/
│   └── test-helpers.js          # Shared test utilities
├── 01-data-loading.spec.js      # Data loading & integration (10 tests)
├── 02-executive-summary.spec.js # Tab 1: Executive Summary (17 tests)
├── 03-architecture-tab.spec.js  # Tab 2: Architecture (14 tests)
├── 04-quality-tab.spec.js       # Tab 3: Quality (18 tests)
├── 05-roadmap-tab.spec.js       # Tab 4: Roadmap (20 tests)
├── 06-performance-tab.spec.js   # Tab 5: Performance (19 tests)
├── 07-security-tab.spec.js      # Tab 6: Security (22 tests)
└── 08-visual-regression.spec.js # Visual snapshots (13 tests)
```

**Total:** 133 tests across 8 test files

## Installation

```bash
cd cortex-brain/documents/analysis/INTELLIGENT-UX-DEMO
npm install
npx playwright install
```

## Running Tests

```bash
# Run all tests
npm test

# Run with UI mode (recommended for development)
npm run test:ui

# Run in headed mode (see browser)
npm run test:headed

# Run specific test file
npx playwright test tests/01-data-loading.spec.js

# Run tests for specific browser
npx playwright test --project=chromium

# Debug mode
npm run test:debug

# Generate and view report
npm run test:report
```

## Test Categories

### 1. Data Loading & Integration (01-data-loading.spec.js)
✅ Validates `analysis-data.json` loading  
✅ Ensures real data is used (not mock)  
✅ Verifies CORTEX project metadata  
✅ Tests data structure integrity  
✅ Confirms correct score values (72, 68, 75, 70)

### 2. Executive Summary Tests (02-executive-summary.spec.js)
✅ Score cards display (4 cards)  
✅ Progress bar animations  
✅ Summary text from real data  
✅ Quick wins list (5 items)  
✅ Critical issues list (5 items)  
✅ Discovery panel behavior  
✅ Dark mode toggle  
✅ Responsive layout

### 3. Architecture Tests (03-architecture-tab.spec.js)
✅ Force-directed graph rendering  
✅ 6 components from real data (tier0-3, agents, orchestrators)  
✅ 8 relationships/connections  
✅ Component list with descriptions  
✅ 4 architectural issues  
✅ God Class detection  
✅ Interactive tooltips  
✅ Graph responsiveness

### 4. Quality Tests (04-quality-tab.spec.js)
✅ Code smells heatmap (8 smells)  
✅ Complexity treemap (6 functions)  
✅ Maintainability bar chart (6 metrics)  
✅ Target lines on charts  
✅ Test coverage: 65%  
✅ Documentation: 72%  
✅ Type safety: 68%  
✅ Color-coding by severity  
✅ Animation transitions

### 5. Roadmap Tests (05-roadmap-tab.spec.js)
✅ Gantt chart rendering (7 tasks)  
✅ Priority matrix with quadrants  
✅ Dependency graph (3 dependencies)  
✅ Task color-coding by priority  
✅ Duration validation (3 days for first task)  
✅ Impact/effort values  
✅ Legend display  
✅ Milestones

### 6. Performance Tests (06-performance-tab.spec.js)
✅ Flamegraph rendering (5 bottlenecks)  
✅ Slowest function: 2500ms  
✅ Sankey diagram (7 data flows)  
✅ Optimization timeline (3 phases)  
✅ Node labels  
✅ Performance metrics  
✅ Highest call count: 5000  
✅ Tooltips on hover

### 7. Security Tests (07-security-tab.spec.js)
✅ Vulnerability counts (2 critical, 4 high, 6 medium)  
✅ Severity bar chart (4 levels)  
✅ OWASP radar chart (5 categories)  
✅ Risk gauge (score: 72)  
✅ SQL Injection detection  
✅ XSS vulnerability  
✅ Compliance status  
✅ Animated gauge  
✅ Color-coded severity

### 8. Visual Regression Tests (08-visual-regression.spec.js)
✅ Executive Summary snapshot  
✅ Architecture Graph snapshot  
✅ Quality Heatmap snapshot  
✅ Complexity Treemap snapshot  
✅ Gantt Chart snapshot  
✅ Priority Matrix snapshot  
✅ Flamegraph snapshot  
✅ Sankey Diagram snapshot  
✅ Security charts snapshots  
✅ Full dashboard snapshot  
✅ Dark mode snapshot  
✅ Mobile view snapshot

## Data Assertions

All tests assert against **real data** from `analysis-data.json`:

| Metric | Expected Value | Source |
|--------|---------------|--------|
| Overall Score | 72 | `scores.overall` |
| Quality Score | 68 | `scores.quality` |
| Performance Score | 75 | `scores.performance` |
| Security Score | 70 | `scores.security` |
| Components | 6 | `architecture.components.length` |
| Relationships | 8 | `architecture.relationships.length` |
| Code Smells | 8 | `quality.codeSmells.length` |
| Complexity Items | 6 | `quality.complexity.length` |
| Roadmap Tasks | 7 | `roadmap.tasks.length` |
| Dependencies | 3 | `roadmap.dependencies.length` |
| Bottlenecks | 5 | `performance.bottlenecks.length` |
| Data Flows | 7 | `performance.dataFlow.length` |
| OWASP Categories | 5 | `security.owasp.length` |
| Critical Vulns | 2 | `security.vulnerabilities.critical` |

## Browser Coverage

- ✅ Chromium (Desktop)
- ✅ Firefox (Desktop)
- ✅ WebKit/Safari (Desktop)
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 12)

## Test Reports

After running tests, view reports at:
- **HTML Report:** `test-results/html-report/index.html`
- **JSON Report:** `test-results/results.json`
- **JUnit Report:** `test-results/junit.xml`

## CI/CD Integration

For GitHub Actions:
```bash
npm run test:ci
```

Generates GitHub-formatted test annotations.

## Debugging Failed Tests

1. **Use UI Mode:** `npm run test:ui` (best for visual debugging)
2. **Check Screenshots:** `test-results/screenshots/`
3. **Watch Videos:** `test-results/` (on failures)
4. **View Traces:** `npx playwright show-trace trace.zip`

## Test Helpers

Located in `tests/fixtures/test-helpers.js`:

- `waitForVisualization(page, selector, timeout)` - Wait for D3 renders
- `switchTab(page, tabName)` - Navigate tabs
- `getD3Elements(page, selector, elementType)` - Count SVG elements
- `setupConsoleErrorTracking(page)` - Track JS errors
- `isInViewport(page, selector)` - Check visibility
- `getComputedStyle(page, selector, property)` - Get CSS values

## Known Issues

- Force-directed graphs have slight position variations (use `maxDiffPixels: 200` for snapshots)
- Animation timing may vary on slower machines (adjust `waitForTimeout` values)
- TypeScript errors in test files are expected (Playwright uses JSDoc annotations)

## Maintenance

- **Update Snapshots:** `npx playwright test --update-snapshots`
- **Update Dependencies:** `npm update`
- **Upgrade Playwright:** `npm install -D @playwright/test@latest && npx playwright install`

## Success Criteria

✅ All 133 tests passing  
✅ 0 console errors during load  
✅ Real data from `analysis-data.json` verified  
✅ All 6 tabs render correctly  
✅ Cross-browser compatibility confirmed  
✅ Mobile responsive layouts validated  
✅ Visual regression baselines established

---

**Author:** Asif Hussain  
**Version:** 1.0.0  
**Last Updated:** December 23, 2025
