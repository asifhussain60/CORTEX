# 📁 Folder Structure Standards

**Document Type:** Reference  
**Created:** December 13, 2025  
**Author:** Asif Hussain  
**Purpose:** Define mandatory folder structure, naming conventions, and organization patterns for all CORTEX documentation  
**Enforcement:** Required for all documentation generation (manual and automated)

---

## 🎯 Purpose

This document establishes **enforceable standards** for documentation organization to ensure:
- ✅ Consistent structure across all documentation
- ✅ Proper GitHub Pages publishing compatibility
- ✅ Maintainable and scalable documentation
- ✅ Automated generation compatibility (cortex_scribe)
- ✅ Clear navigation and discoverability

---

## 📂 Complete Folder Structure

```
docs/
│
├── index.html                    # ⚠️ PROTECTED: Home page (DO NOT MODIFY directly)
├── mkdocs.yml                    # ⚠️ AUTO-UPDATED: Navigation config
│
├── features/                     # 🎯 User-facing features (20+ pages)
│   ├── index.html               # Category index
│   ├── cortex-lens.html
│   ├── orchestration-metrics.html
│   ├── code-writing.html
│   ├── code-rewrite.html
│   ├── progress-renderer.html
│   ├── timeframe-estimation.html
│   ├── web-testing.html
│   ├── code-documentation.html
│   ├── diagrams-generator.html
│   ├── feature-list-generator.html
│   ├── mkdocs-generator.html
│   ├── executive-summary-generator.html
│   ├── publish-documentation.html
│   ├── vision-context-middleware.html
│   ├── task-injection-manager.html
│   ├── orchestration-analytics.html
│   ├── performance-telemetry.html
│   ├── reverse-engineering.html
│   ├── narrative-consolidator.html
│   ├── business-capability-detector.html
│   └── component-discovery.html
│
├── orchestration/                # 🤖 Orchestrator documentation (15+ pages)
│   ├── index.html               # Category index
│   ├── planning-system.html
│   ├── tdd-implementation.html
│   ├── system-maintenance.html
│   ├── rollback.html
│   ├── master-setup.html
│   ├── error-recovery.html
│   ├── performance-profiling.html
│   ├── cleanup.html
│   ├── refactoring-planning.html
│   ├── feature-planning.html
│   ├── architecture-planning.html
│   ├── documentation-generation.html
│   ├── code-quality.html
│   ├── checkpoint-manager.html
│   └── parallel-coordinator.html
│   └── resource-management.html
│
├── future/                       # 🔮 CORTEX 4.0 preview features (4+ pages)
│   ├── index.html               # Category index
│   ├── code-review.html         # 60% ready, Q2 2026
│   ├── backend-testing.html     # 95% ready, Q1 2026
│   ├── mobile-testing.html      # 30% ready, Q3 2026
│   └── ui-from-figma.html       # 20% ready, Q4 2026
│
├── architecture/                 # 🏗️ System architecture docs (5+ pages)
│   ├── index.html
│   ├── overview.html
│   ├── tier-system.html
│   ├── orchestration-framework.html
│   └── brain-architecture.html
│
└── assets/                       # 🎨 Shared resources
    ├── css/
    │   ├── main.css             # ⭐ Global styles + glassmorphism tokens
    │   └── syntax-highlight.css # Code syntax highlighting
    │
    ├── js/
    │   ├── navigation.js        # Global navigation logic
    │   ├── phase-flow-viz.js    # ♻️ Reusable D3.js: Phase flow
    │   ├── metrics-dashboard-viz.js # ♻️ Reusable D3.js: Metrics
    │   ├── architecture-viz.js  # ♻️ Reusable D3.js: Architecture
    │   ├── timeline-viz.js      # ♻️ Reusable D3.js: Timeline
    │   └── matrix-viz.js        # ♻️ Reusable D3.js: Matrix
    │
    └── images/
        ├── logo.png
        ├── icons/               # Feature/orchestrator icons
        │   ├── lens.svg
        │   ├── metrics.svg
        │   └── ...
        └── screenshots/         # Feature screenshots
            ├── cortex-lens-dashboard.png
            └── ...
```

---

## 📝 File Naming Conventions

### HTML Pages

**Pattern:** `[feature-name].html`

**Rules:**
- ✅ Lowercase only
- ✅ Hyphens for word separation
- ✅ Descriptive and concise
- ❌ NO underscores
- ❌ NO spaces
- ❌ NO camelCase

**Examples:**
```
✅ cortex-lens.html
✅ orchestration-metrics.html
✅ code-writing.html
✅ planning-system.html

❌ CortexLens.html          (camelCase)
❌ cortex_lens.html         (underscore)
❌ cortex lens.html         (space)
❌ CORTEX-LENS.html         (uppercase)
```

### JavaScript Files

**Visualization Scripts:** `[visualization-type]-viz.js`

**Rules:**
- ✅ Suffix with `-viz.js` for D3.js visualizations
- ✅ Use `-util.js` for utility scripts
- ✅ Descriptive names
- ❌ NO generic names like `viz.js`, `script.js`

**Examples:**
```
✅ phase-flow-viz.js
✅ metrics-dashboard-viz.js
✅ architecture-viz.js
✅ navigation-util.js

❌ viz.js                   (too generic)
❌ d3_visualization.js      (underscore)
❌ script1.js               (non-descriptive)
```

### CSS Files

**Rules:**
- ✅ `main.css` for global styles
- ✅ `[component]-styles.css` for component-specific styles
- ❌ NO inline CSS in HTML files
- ❌ DO NOT create separate glassmorphism.css (use tokens in main.css)

**Examples:**
```
✅ main.css                 (global + glassmorphism tokens)
✅ syntax-highlight.css     (code highlighting)
✅ card-styles.css          (component-specific)

❌ glassmorphism.css        (use tokens in main.css instead)
❌ styles.css               (too generic)
```

---

## 🚫 Forbidden Patterns

### Root-Level Documentation Files

**Rule:** NO documentation files in project root

**Forbidden:**
```
❌ CORTEX/summary.md
❌ CORTEX/documentation.md
❌ CORTEX/features.md
❌ CORTEX/README-DOCS.md
```

**Correct:**
```
✅ cortex-brain/documents/summaries/project-summary.md
✅ cortex-brain/documents/reports/feature-report.md
✅ docs/features/feature-list.html
```

### Documentation in cortex-brain/

**Rule:** `cortex-brain/` is for CORTEX's internal brain, NOT user documentation

**Forbidden:**
```
❌ cortex-brain/user-guide.md
❌ cortex-brain/feature-docs/
❌ cortex-brain/api-reference.md
```

**Correct:**
```
✅ docs/features/user-guide.html
✅ docs/architecture/api-reference.html
✅ cortex-brain/documents/planning/    (internal planning ONLY)
```

**Exceptions (Allowed in cortex-brain/):**
- `cortex-brain/documents/planning/` - Project planning documents
- `cortex-brain/documents/scribe/` - Documentation generation plans
- `cortex-brain/documents/reports/` - Internal analysis reports

### Inline CSS

**Rule:** ALL styling must use CSS classes + main.css

**Forbidden:**
```html
❌ <div style="background: rgba(255,255,255,0.05); backdrop-filter: blur(20px);">
❌ <h1 style="color: #00d4ff;">
❌ <section style="padding: 2rem; border-radius: 12px;">
```

**Correct:**
```html
✅ <div class="glass-card">
✅ <h1 class="accent-text">
✅ <section class="content-section">
```

```css
/* main.css */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 2rem;
}
```

### Duplicate D3.js Code

**Rule:** Reuse shared visualization scripts, don't duplicate

**Forbidden:**
```html
❌ <!-- Inline D3.js code in every page -->
<script>
    d3.select("#viz").append("svg")... (200+ lines of D3.js)
</script>
```

**Correct:**
```html
✅ <!-- Use shared script -->
<div id="phase-flow-viz"></div>
<script src="../assets/js/phase-flow-viz.js"></script>
<script>
    renderPhaseFlow("#phase-flow-viz", {
        phases: ["Phase 1", "Phase 2", "Phase 3"]
    });
</script>
```

### Hardcoded Paths

**Rule:** Use relative paths, not absolute paths

**Forbidden:**
```html
❌ <link href="/Users/asifhussain/PROJECTS/CORTEX/docs/assets/css/main.css">
❌ <script src="C:\Projects\CORTEX\docs\assets\js\viz.js">
❌ <img src="file:///docs/images/logo.png">
```

**Correct:**
```html
✅ <link href="../assets/css/main.css">
✅ <script src="../assets/js/phase-flow-viz.js">
✅ <img src="../assets/images/logo.png">
```

---

## ✅ Required Patterns

### Feature Pages Location

**Rule:** ALL user-facing features in `docs/features/`

```
✅ docs/features/cortex-lens.html
✅ docs/features/code-writing.html
✅ docs/features/orchestration-metrics.html
```

### Orchestrator Pages Location

**Rule:** ALL orchestrator documentation in `docs/orchestration/`

```
✅ docs/orchestration/planning-system.html
✅ docs/orchestration/tdd-implementation.html
✅ docs/orchestration/system-maintenance.html
```

### CORTEX 4.0 Preview Location

**Rule:** ALL future/preview features in `docs/future/`

```
✅ docs/future/code-review.html
✅ docs/future/backend-testing.html
✅ docs/future/mobile-testing.html
```

### Shared Visualizations

**Rule:** D3.js scripts in `docs/assets/js/` for reuse

```
✅ docs/assets/js/phase-flow-viz.js
✅ docs/assets/js/metrics-dashboard-viz.js
✅ docs/assets/js/architecture-viz.js
```

### Glassmorphism Styling

**Rule:** CSS design tokens in `main.css`

```css
/* ✅ Correct: main.css */
:root {
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-blur: blur(20px);
}

.glass-card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
}
```

---

## 🗺️ Navigation Categories

### MkDocs Navigation Structure

```yaml
nav:
  - Home: index.md
  
  - Features:
      - Overview: features/index.md
      - CORTEX Lens: features/cortex-lens.md
      - Code Writing: features/code-writing.md
      - Code Rewrite: features/code-rewrite.md
      # ... 20+ features
  
  - Orchestration:
      - Overview: orchestration/index.md
      - Planning System 2.0: orchestration/planning-system.md
      - TDD Mastery: orchestration/tdd-implementation.md
      - System Maintenance: orchestration/system-maintenance.md
      # ... 15+ orchestrators
  
  - Future (CORTEX 4.0):
      - Overview: future/index.md
      - Code Review: future/code-review.md
      - Backend Testing: future/backend-testing.md
      - Mobile Testing: future/mobile-testing.md
      - UI from Figma: future/ui-from-figma.md
  
  - Architecture:
      - Overview: architecture/index.md
      - System Overview: architecture/overview.md
      - Tier System: architecture/tier-system.md
```

### Category Index Pages

**Each category MUST have an index.html:**

```
✅ docs/features/index.html       - Features overview
✅ docs/orchestration/index.html  - Orchestrators overview
✅ docs/future/index.html         - CORTEX 4.0 preview overview
✅ docs/architecture/index.html   - Architecture overview
```

**Index page structure:**
```html
<section class="category-overview">
    <h1>CORTEX Features</h1>
    <p>Comprehensive capabilities and tools...</p>
    
    <div class="feature-grid">
        <a href="cortex-lens.html" class="feature-card glass-card">
            <div class="feature-icon">🔍</div>
            <h3>CORTEX Lens Platform</h3>
            <p>Universal repository intelligence</p>
        </a>
        <!-- More feature cards... -->
    </div>
</section>
```

---

## 🎨 Asset Organization

### CSS Design Tokens

**Location:** `docs/assets/css/main.css`

**Required tokens:**
```css
:root {
    /* Colors */
    --bg-primary: #0a0e27;
    --bg-secondary: #1a1f3a;
    --accent-primary: #00d4ff;
    --accent-secondary: #7b61ff;
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
    
    /* Glassmorphism */
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-blur: blur(20px);
    
    /* Typography */
    --font-primary: 'Segoe UI', 'Inter', sans-serif;
    --font-mono: 'SF Mono', 'Consolas', monospace;
    --font-size-base: 16px;
    --line-height-base: 1.6;
    
    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 2rem;
    --spacing-lg: 3rem;
    --spacing-xl: 4rem;
    
    /* Border Radius */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
}
```

### D3.js Visualization Scripts

**Location:** `docs/assets/js/`

**Naming:** `[visualization-type]-viz.js`

**Export pattern:**
```javascript
// phase-flow-viz.js
function renderPhaseFlow(selector, config) {
    const svg = d3.select(selector)
        .append("svg")
        .attr("width", config.width || 800)
        .attr("height", config.height || 400);
    
    // D3.js visualization logic...
}

// Export for use in HTML pages
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { renderPhaseFlow };
}
```

**Usage in HTML:**
```html
<div id="phase-flow-viz"></div>
<script src="../assets/js/phase-flow-viz.js"></script>
<script>
    renderPhaseFlow("#phase-flow-viz", {
        phases: ["Phase 1", "Phase 2", "Phase 3"],
        width: 1000,
        height: 500
    });
</script>
```

---

## 🚀 Publishing Requirements

### GitHub Pages Configuration

**Branch:** `main` or `gh-pages`  
**Source:** `/docs` folder  
**Custom Domain:** Optional  
**Enforce HTTPS:** ✅ Enabled

### Site Build Validation

**Command:**
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m mkdocs build
```

**Expected output:**
```
INFO     -  Cleaning site directory
INFO     -  Building documentation to directory: /Users/asifhussain/PROJECTS/CORTEX/site
INFO     -  Documentation built in 2.34 seconds
```

**Validation checks:**
- ✅ No build errors
- ✅ No broken links
- ✅ All pages accessible
- ✅ Navigation functional

### Performance Requirements

**Metrics:**
- Page load: <3 seconds
- Time to Interactive: <5 seconds
- Lighthouse Performance: >90
- Lighthouse Accessibility: >95
- Mobile responsive: 100%

**Test command:**
```bash
# Serve locally
python3 -m mkdocs serve

# Preview at: http://127.0.0.1:8000/CORTEX/

# Test performance (Chrome DevTools Lighthouse)
# - Open in Chrome
# - F12 > Lighthouse tab
# - Run audit (Mobile + Desktop)
```

---

## 🔍 Validation Checklist

### Pre-Generation Validation

Before generating new documentation:
- [ ] Verify output path is in `docs/features/`, `docs/orchestration/`, or `docs/future/`
- [ ] Check filename follows `[feature-name].html` pattern
- [ ] Ensure no duplicate pages exist
- [ ] Verify template library available

### Post-Generation Validation

After generating documentation:
- [ ] HTML structure valid (no errors)
- [ ] All sections present (hero, overview, features, usage, integration)
- [ ] D3.js visualizations render correctly
- [ ] Code examples have syntax highlighting
- [ ] Internal links functional
- [ ] Responsive design verified (desktop, tablet, mobile)
- [ ] MkDocs navigation updated
- [ ] Home page index updated

### Site-Wide Validation

Before publishing:
- [ ] MkDocs builds without errors
- [ ] All pages accessible via navigation
- [ ] No broken links (internal or external)
- [ ] Search functionality working
- [ ] Performance metrics met (<3s load)
- [ ] Mobile responsive verified

---

## 📚 References

**Related Documents:**
- [Master Plan: Phase 1 Documentation](../planning/MASTER-PLAN-PHASE-1-DOCUMENTATION.md)
- [Documentation Templates Library](documentation-templates.js)
- [Enhancement Plan: cortex_scribe](../planning/enhancement-plan.md)

**Standards:**
- HTML5 Specification: https://html.spec.whatwg.org/
- CSS Design Tokens: https://www.w3.org/TR/css-variables/
- MkDocs Documentation: https://www.mkdocs.org/
- D3.js Documentation: https://d3js.org/

---

**Created:** December 13, 2025  
**Status:** ✅ Approved - Enforced for all documentation generation  
**Enforcement:** Required for cortex_scribe automation
