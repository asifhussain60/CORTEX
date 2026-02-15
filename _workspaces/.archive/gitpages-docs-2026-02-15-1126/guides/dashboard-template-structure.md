# Dashboard Template Structure Guide

**Authority:** Phase 32 - Glassmorphism Dashboard Generator Fix  
**Version:** 1.0  
**Updated:** 2026-02-06  
**Status:** ACTIVE

---

## Overview

The CORTEX dashboard template (`company/dashboards/templates/repo-dashboard-glass-v1.html`) is a sophisticated HTML template designed for static dashboard generation with glassmorphism design aesthetic.

**Key Features:**
- ✅ Glassmorphism dark theme (rgba(26, 31, 58, 0.7) background + blur effects)
- ✅ File:// protocol compatible (no external fetches, all data embedded)
- ✅ Responsive MVC architecture (Model-View-Controller separation)
- ✅ 1,380 lines of production-ready HTML/CSS/JavaScript
- ✅ External CSS modularization for maintainability

---

## Template Structure

### Head Section

```html
<!-- Favicon -->
<link href="../../assets/images/CORTEX-logo-64.png" rel="icon">

<!-- CORTEX Glassmorphism Theme (External CSS) -->
<link href="../../assets/css/main.css" rel="stylesheet">
<link href="../../assets/css/glass-design-tokens.css" rel="stylesheet">
<link href="../../assets/css/glass-base-patterns.css" rel="stylesheet">
<link href="../../assets/css/glass-ui-components.css" rel="stylesheet">
<link href="../../assets/css/glass-animations.css" rel="stylesheet">

<!-- Dashboard-Specific Styles -->
<style>
  /* Inline styles for overrides and customization */
</style>
```

**CSS Files:**
- `glass-design-tokens.css` — CSS custom properties (--glass-bg, --accent-primary, etc.)
- `glass-base-patterns.css` — Base component patterns
- `glass-ui-components.css` — UI component styles
- `glass-animations.css` — Animations and transitions

### Body Structure

```html
<body>
  <!-- Header (Logo + Title + Stats) -->
  <div class="dashboard-header">
    <div class="logo-container">
      <img src="../../assets/images/CORTEX-logo-200.png" alt="CORTEX">
    </div>
    <div class="header-content">
      <h1>{Repo Name}</h1>
      <p class="tagline">{Description}</p>
      <div class="header-stats">
        <div class="header-stat">
          <div class="value">{health_score}</div>
          <div class="label">Health</div>
        </div>
        <!-- Additional stats -->
      </div>
    </div>
  </div>

  <!-- Navigation Tabs -->
  <div class="navigation">
    <button class="tab-button active" data-tab="overview">Overview</button>
    <button class="tab-button" data-tab="architecture">Architecture</button>
    <!-- Additional tabs -->
  </div>

  <!-- Content Panels (one per tab) -->
  <div class="content-panels">
    <div id="overview" class="tab-panel active">
      <!-- Overview content -->
    </div>
    <!-- Additional panels -->
  </div>

  <!-- Back Navigation Link -->
  <a href="../../index.html" class="nav-link back-to-landing">← Back to Landing</a>

  <!-- Dashboard Data (Embedded JSON) -->
  <script>
    window.dashboardData = {/* Embedded JSON data */};
  </script>
</body>
```

---

## MVC Architecture

### Model

**Location:** `window.dashboardData` (embedded JSON)

**Structure:**
```javascript
window.dashboardData = {
  repo_slug: "ksessions",
  display_name: "KSESSIONS",
  health_score: 92,
  risk_score: 8,
  overview_metrics: {
    functions: 1245,
    classes: 287,
    critical_issues: 0,
  },
  architecture: [
    { name: "API Layer", module_count: 8, loc: 24500, complexity: 2.3 },
    // ...
  ],
  use_cases: [
    {
      id: "UC-001",
      title: "Multi-tenant session isolation",
      summary: "...",
      persona: "production_owner",
      category: "reliability",
      severity: "high",
    },
  ],
};
```

**Size:** ~10-20KB JSON (embedded directly, no network fetch)

### View

**Rendering Technology:**
- HTML templates with `{...}` placeholders
- CSS via external files (glass-*.css)
- JavaScript for DOM manipulation (deferred rendering)

**Key CSS Classes:**
- `.glass-card` — Glass-effect container with blur
- `.accent-primary` — Cyan text/border (#00d4ff)
- `.accent-secondary` — Purple accent (#7b61ff)
- `.health-badge` — Health status indicator

**Responsive Design:**
- Mobile-first approach (flex-based layouts)
- Grid system for metric cards
- Sticky header (navigation)

### Controller

**Event Handlers:**
1. **Tab Navigation** — Click `.tab-button` → Show corresponding `.tab-panel`
2. **Chart Rendering** — Initialize ChartHost instances for data visualization
3. **Deferred Rendering** — Use `ChartHost` visibility guards to optimize performance
4. **Search/Filter** — Use Fuse.js for client-side search (use-cases.js)
5. **Data Binding** — React-like pattern (update model → re-render view)

**Key JavaScript Objects:**
- `UseCasesManager` — Manages use case display and filtering
- `ChartHost` — Lazy-loads charts when tab becomes visible
- `DashboardController` — Central event coordination

---

## Data Injection Process

**When:** During suite generation (`suite_generator.py`)

**Process:**
1. Load template HTML
2. Replace `window.dashboardData = {}` with actual JSON
3. Update asset paths: `assets/` → `../../assets/`
4. Inject back-to-landing link
5. Inject use-cases tab and scripts
6. Write final HTML to `dist/repos/<slug>/index.html`

**Key Function:** `DashboardSuiteGenerator._inject_dashboard_data()`

---

## Glassmorphism Specifications

**Approved Color Palette:**
```css
:root {
  --glass-bg: rgba(26, 31, 58, 0.7);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-shadow: rgba(0, 0, 0, 0.3);
  
  --text-primary: #ffffff;
  --text-secondary: #a0a6c0;
  
  --accent-primary: #00d4ff;    /* Cyan */
  --accent-secondary: #7b61ff;  /* Purple */
  
  --backdrop-blur: blur(10px);
}
```

**Key Properties:**
- Dark background (26, 31, 58) with 70% opacity
- Subtle white borders (10% opacity)
- Backdrop blur (10px) for glass effect
- Cyan (#00d4ff) and purple (#7b61ff) accents

**Typography:**
- Font family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif
- Font weights: 400 (normal), 600 (semibold), 700 (bold)
- Line height: 1.6 (readability)

---

## Asset Paths

**Repository Structure:**
```
company/dashboards/
├── templates/
│   └── repo-dashboard-glass-v1.html     (This template)
├── assets/
│   ├── css/
│   │   ├── main.css
│   │   ├── glass-*.css (5 files)
│   │   ├── use-cases.css
│   │   └── [other CSS]
│   ├── js/
│   │   ├── use-cases.js
│   │   └── [other JS]
│   ├── vendor/
│   │   ├── fuse.min.js
│   │   ├── gridjs.umd.js
│   │   ├── echarts.min.js
│   │   └── [other libs]
│   └── images/
│       ├── CORTEX-logo-64.png
│       ├── CORTEX-logo-200.png
│       └── CORTEX-logo-512.png
└── repos/
    ├── alist/index.html
    ├── cortex/index.html
    ├── kashkole/index.html
    └── ksessions/index.html
```

**Path Resolution (for repos/<slug>/index.html):**
- Template uses relative paths: `../../assets/css/main.css`
- Generator transforms: `assets/` → `../../assets/` (via `_fix_asset_paths()`)
- Works both via HTTP and file:// protocol

---

## File:// Protocol Compatibility

**Requirements Met:**
- ✅ No `fetch()` or XMLHttpRequest calls
- ✅ All data embedded as JSON in `<script>` tag
- ✅ All assets (CSS, JS, images) loaded via relative file:// URLs
- ✅ No external CDN dependencies (vendor libs included locally)

**Testing:**
```bash
# Test locally
open company/dashboards/repos/ksessions/index.html
# or
open -a "Google Chrome" company/dashboards/repos/ksessions/index.html

# Browser console should show no fetch errors
# All resources should load successfully
```

---

## Troubleshooting

### Assets not loading (file:// mode)

**Problem:** Images/CSS appear broken when opening via `file://`

**Cause:** Path resolution issue or missing assets

**Solution:**
1. Check file:// URL is correct: `file:///Users/asifhussain/PROJECTS/CORTEX/company/dashboards/repos/ksessions/index.html`
2. Verify `company/dashboards/assets/` directory exists
3. Run suite generator to update asset paths: `DashboardSuiteGenerator.generate_suite()`
4. Check browser console for detailed errors

### Charts not rendering

**Problem:** ChartHost containers appear empty

**Cause:** ECharts library not loaded or data not embedded

**Solution:**
1. Verify `window.dashboardData` exists in page source
2. Check `vendor/echarts.min.js` is present
3. Use browser DevTools to inspect chart container visibility
4. Check deferred rendering guards (`ChartHost.isVisible()`)

### Glassmorphism effect not visible

**Problem:** Glassmorphism effects (blur, transparency) not showing

**Cause:** CSS files not loaded or browser doesn't support backdrop-filter

**Solution:**
1. Verify `glass-design-tokens.css` is loaded (DevTools > Network tab)
2. Check CSS file syntax (no parse errors)
3. Test in modern browser (Chrome, Safari, Firefox - all support backdrop-filter)
4. Check system GPU acceleration is enabled

---

## Testing & Validation

**Automated Tests:**
```bash
pytest tests/visualization/spa/test_suite_generator.py -v
```

**Test Categories:**
- Data model validation (5 tests)
- Generator functionality (8 tests)
- GPT spec compliance (9 tests)
- **NEW: Glassmorphism CSS validation (1 test)**

**Manual Testing:**
1. Generate dashboard via Python: `DashboardSuiteGenerator.generate_suite(config)`
2. Open generated HTML: `open dist/repos/<slug>/index.html`
3. Verify visual elements:
   - ✅ Dark glassmorphism background
   - ✅ Cyan (#00d4ff) accents in header
   - ✅ Tab navigation functional
   - ✅ Charts render without lag
   - ✅ Back-to-landing link works

---

## Contributing

When modifying this template:

1. **Test the MVC architecture** — Use existing pilot tests:
   - `tests/dashboard/test_mvc_integration.html` (650 LOC)
   - `tests/dashboard/test_deferred_renderer.html` (503 LOC)

2. **Validate glassmorphism compliance** — Check against approved specifications

3. **Update tests** — Add test case to `test_suite_generator.py`

4. **Run full test suite:**
   ```bash
   pytest tests/visualization/spa/test_suite_generator.py -v
   ```

5. **Regenerate all dashboards** — After template changes:
   ```python
   from cortex.visualization.spa.suite_generator import DashboardSuiteGenerator
   generator = DashboardSuiteGenerator(output_dir=Path("dist"))
   generator.generate_suite(config)
   ```

---

## References

- **Authority:** Phase 32 - Glassmorphism Dashboard Generator Fix
- **Design Standard:** glassmorphism-design-standard.md v4.0
- **Reference Implementation:** company/dashboards/repos/alist/index.html
- **Generator Code:** cortex/visualization/spa/suite_generator.py
- **Tests:** tests/visualization/spa/test_suite_generator.py
