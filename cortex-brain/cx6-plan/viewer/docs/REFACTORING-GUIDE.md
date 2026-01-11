# CORTEX 6.0 HTML Views - Refactoring & Standardization Guide

**Date:** 2026-01-11  
**Version:** 1.0.0  
**Author:** Asif Hussain  
**Purpose:** Complete guide for maintaining consistent design across all HTML views

---

## ✅ Completed Refactorings

### 1. Logo Integration & Header Standardization

**Status:** ✅ COMPLETE

**What Was Done:**
- Copied `CORTEX-logo-200.png` to `cortex-brain/cx6-plan/viewer/assets/images/`
- Created standardized header template: `shared/header-template.html`
- Created header loader utility: `shared/header-loader.js`
- Updated existing HTML files to use new header:
  - `cortex-plan-viewer.html`
  - `phase-detail-viewer.html`

**Header Features:**
- Logo on left (64px height, compact, with glow effect)
- Title and description on same row (maximizes vertical space)
- Design score badge on right (dynamic color based on score)
- Optional breadcrumb navigation
- Responsive design (stacks on mobile)
- Sticky positioning for always-visible navigation

**Usage in New HTML Files:**
```html
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <title>CORTEX 6.0 - Page Title</title>
    
    <!-- CORTEX Global Styles -->
    <link rel="stylesheet" href="shared/cortex-global.css">
</head>
<body>
    <!-- CORTEX Standardized Header -->
    <div id="cortex-header-container"></div>
    
    <script>
        // Configure header for this page
        const cortexHeaderConfig = {
            pageTitle: "Your Page Title",
            pageDescription: "Brief description of this page",
            designScore: "97/95",
            loadScoreFromPlan: true,  // Auto-fetch from master-plan.yaml
            breadcrumbs: [
                { text: "Dashboard", link: "cortex-plan-viewer.html" },
                { text: "Current Page", link: null }
            ]
        };
    </script>
    <script src="shared/header-loader.js"></script>
    
    <!-- Your page content here -->
    
</body>
</html>
```

---

### 2. Global CSS Variables & Styles

**Status:** ✅ COMPLETE

**What Was Done:**
- Created centralized stylesheet: `shared/cortex-global.css`
- Defined CSS custom properties (design tokens) for:
  - Brand colors (cyan, purple, pink, green, yellow)
  - Semantic colors (success, warning, danger, info)
  - Backgrounds (dark, darker, darkest, glass morphism)
  - Typography (font sizes, line heights, families)
  - Spacing (xs, sm, md, lg, xl, 2xl)
  - Border radius (sm, md, lg, xl, full)
  - Shadows (sm, md, lg, glow effects)
  - Z-index layers (dropdown, sticky, modal, etc.)

**Benefits:**
- ✅ Eliminates duplicate CSS across files
- ✅ Consistent color palette across all views
- ✅ Easy theme updates (change one variable, affects all pages)
- ✅ Reduced file sizes (shared styles loaded once)
- ✅ Faster development (reusable utility classes)

**Existing Files to Update:**
1. `cortex-plan-viewer.html` - Add `<link rel="stylesheet" href="shared/cortex-global.css">` (PENDING)
2. `cortex-plan-viewer-v2.html` - Add link, remove duplicate :root{} (PENDING)
3. `phase-detail-viewer.html` - Add link, remove duplicate :root{} (PENDING)

---

## 🔄 Recommended Refactorings (Next Steps)

### 3. Shared JavaScript Utilities

**Priority:** HIGH  
**Effort:** 2-3 hours

**Opportunity:** Many HTML files have duplicate JavaScript code for:
- Chart.js initialization
- Data loading from JSON/YAML
- Audit log fetching
- Progress calculation
- AC-ID badge rendering

**Proposed Solution:**
Create `shared/cortex-utils.js` with:

```javascript
// Chart.js helpers
function createProgressChart(canvasId, data) { /* ... */ }
function createBurndownChart(canvasId, data) { /* ... */ }
function createPhaseDistributionChart(canvasId, data) { /* ... */ }

// Data loading
async function loadMasterPlan() { /* ... */ }
async function loadACIndex() { /* ... */ }
async function loadProgressTracker() { /* ... */ }

// Audit logs
async function fetchAuditLogs(category, level, limit) { /* ... */ }
function renderAuditEntry(entry) { /* ... */ }

// Progress helpers
function calculatePhaseProgress(phase) { /* ... */ }
function calculateOverallProgress() { /* ... */ }

// AC-ID rendering
function renderACBadge(acId, status) { /* ... */ }
function groupACsByCategory(acIds) { /* ... */ }
```

**Files to Update:**
- `cortex-plan-viewer.html` - Extract chart/data functions
- `phase-detail-viewer.html` - Extract progress/rendering functions

---

### 4. Shared Footer Component

**Priority:** MEDIUM  
**Effort:** 1 hour

**Opportunity:** Footer content duplicated across files

**Proposed Solution:**
Create `shared/footer-template.html`:

```html
<footer class="cortex-footer">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-6">
                <p>© 2025-2026 Asif Hussain. All rights reserved.</p>
                <p class="text-muted">CORTEX 6.0 - Production-Grade AI Orchestration</p>
            </div>
            <div class="col-md-6 text-end">
                <a href="https://github.com/asifhussain60/CORTEX" class="footer-link">
                    <i class="bi bi-github"></i> GitHub Repository
                </a>
                <a href="../README.md" class="footer-link">
                    <i class="bi bi-book"></i> Documentation
                </a>
            </div>
        </div>
    </div>
</footer>
```

**Usage:**
```html
<!-- Footer -->
<div id="cortex-footer-container"></div>
<script src="shared/footer-loader.js"></script>
```

---

### 5. Shared Card Components

**Priority:** MEDIUM  
**Effort:** 2 hours

**Opportunity:** Metric cards, phase cards, AC-ID cards all have similar structure

**Proposed Solution:**
Create reusable card templates in `cortex-global.css` (already done partially) and helper functions in `cortex-utils.js`:

```javascript
function createMetricCard(label, value, subtitle, icon) {
    return `
        <div class="card metric-card">
            <i class="${icon}"></i>
            <div class="metric-label">${label}</div>
            <div class="metric-value">${value}</div>
            <div class="metric-subtitle">${subtitle}</div>
        </div>
    `;
}

function createPhaseCard(phase) {
    return `
        <div class="card phase-card ${phase.status}">
            <div class="phase-header">
                <h3>${phase.name}</h3>
                <span class="badge badge-${phase.status}">${phase.status}</span>
            </div>
            <div class="phase-body">
                <p>${phase.description}</p>
                <div class="progress">
                    <div class="progress-bar" style="width: ${phase.completion}%">
                        ${phase.completion}%
                    </div>
                </div>
            </div>
        </div>
    `;
}
```

---

### 6. Responsive Navigation Menu

**Priority:** LOW  
**Effort:** 3 hours

**Opportunity:** No consistent navigation across pages

**Proposed Solution:**
Add navigation menu to header template with links to:
- Dashboard (cortex-plan-viewer.html)
- Phase Details (phase-detail-viewer.html)
- Gap Analysis (gap-analysis.html)
- Architecture Docs (cortex-instructions.html, core-rules-viewer.html)
- MCP Capabilities (mcp-capabilities-explorer.html)

**Mobile Design:** Hamburger menu that slides in from right

---

### 7. Dark/Light Theme Toggle

**Priority:** LOW  
**Effort:** 2 hours

**Opportunity:** All views are dark theme only

**Proposed Solution:**
- Add theme toggle button to header
- Store preference in localStorage
- Update CSS custom properties for light theme
- Add `prefers-color-scheme` media query support

---

## 📁 File Organization (After Refactoring)

```
cortex-brain/cx6-plan/viewer/
├── shared/                           ← All shared components
│   ├── cortex-global.css            ← ✅ COMPLETE
│   ├── header-template.html         ← ✅ COMPLETE
│   ├── header-loader.js             ← ✅ COMPLETE
│   ├── footer-template.html         ← TODO
│   ├── footer-loader.js             ← TODO
│   ├── cortex-utils.js              ← TODO (chart/data helpers)
│   └── nav-menu.js                  ← TODO (navigation)
│
├── assets/
│   ├── images/
│   │   └── CORTEX-logo-200.png      ← ✅ COMPLETE
│   ├── icons/                        ← TODO (custom SVG icons)
│   └── fonts/                        ← TODO (if custom fonts needed)
│
├── data/                             ← Separate data from views
│   ├── plan-data.json               ← Chart.js data source
│   └── audit-loader.js              ← Audit log fetching
│
├── cortex-plan-viewer.html          ← ✅ UPDATED (uses new header)
├── cortex-plan-viewer-v2.html       ← TODO (update to new header)
├── phase-detail-viewer.html         ← ✅ UPDATED (uses new header)
│
└── docs/                             ← Documentation
    ├── HTML-VIEWS-TODO.md           ← Master specification
    └── REFACTORING-GUIDE.md         ← This document
```

---

## 🎯 Refactoring Checklist (Per HTML File)

When updating an existing HTML file to use shared components:

### Step 1: Add Global CSS
```html
<head>
    <!-- Add before any custom styles -->
    <link rel="stylesheet" href="shared/cortex-global.css">
</head>
```

### Step 2: Replace Old Header
```html
<!-- Remove old header HTML -->
<div class="header-glow">...</div>

<!-- Replace with standardized header -->
<div id="cortex-header-container"></div>
<script>
    const cortexHeaderConfig = {
        pageTitle: "...",
        pageDescription: "...",
        designScore: "97/95",
        loadScoreFromPlan: true
    };
</script>
<script src="shared/header-loader.js"></script>
```

### Step 3: Remove Duplicate CSS
```html
<style>
    /* Remove duplicate :root {} variables (now in cortex-global.css) */
    /* Remove duplicate .glass {} styles (now in cortex-global.css) */
    /* Remove duplicate badge styles (now in cortex-global.css) */
    /* Keep ONLY page-specific styles */
</style>
```

### Step 4: Extract Common JavaScript
```html
<script>
    /* Move chart/data functions to shared/cortex-utils.js */
    /* Import utilities: */
</script>
<script src="shared/cortex-utils.js"></script>
```

### Step 5: Update Asset Paths
```html
<!-- Update logo paths -->
<img src="assets/images/CORTEX-logo-200.png">

<!-- Update relative paths if file moved -->
<link rel="stylesheet" href="shared/cortex-global.css">
```

### Step 6: Test Responsiveness
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

### Step 7: Verify Accessibility
- Keyboard navigation works
- Focus indicators visible
- ARIA labels present
- Color contrast meets WCAG AA

---

## 📊 Impact Metrics

### Before Refactoring:
- **Duplicate CSS lines:** ~500 lines across 3 files
- **Duplicate JavaScript:** ~300 lines across 3 files
- **Header HTML:** Repeated in 3 files
- **Maintenance burden:** Update 3 files for every style change

### After Refactoring:
- **Shared CSS:** 1 file (cortex-global.css), 450 lines
- **Shared JavaScript:** 1 file (cortex-utils.js), 250 lines (when complete)
- **Header HTML:** 1 template file, loaded dynamically
- **Maintenance burden:** Update 1 file, affects all views

**Estimated Savings:**
- 40% reduction in total lines of code
- 70% faster to add new pages (copy template + configure)
- 80% faster to update global styles (single file change)

---

## 🔧 Maintenance Guidelines

### When Adding a New HTML View:

1. **Start with template:**
   ```bash
   cp shared/page-template.html new-page.html
   ```

2. **Configure header:**
   ```javascript
   const cortexHeaderConfig = {
       pageTitle: "New Page Title",
       pageDescription: "What this page does",
       designScore: "97/95",
       loadScoreFromPlan: true,
       breadcrumbs: [
           { text: "Dashboard", link: "cortex-plan-viewer.html" },
           { text: "New Page", link: null }
       ]
   };
   ```

3. **Use utility classes:**
   ```html
   <div class="glass card fade-in">
       <div class="card-header gradient-text">Section Title</div>
       <div class="card-body">Content here</div>
   </div>
   ```

4. **Use global colors:**
   ```css
   .custom-element {
       color: var(--cortex-cyan);
       background: var(--glass-bg);
       border: 1px solid var(--glass-border);
   }
   ```

### When Updating Global Styles:

1. **Edit `shared/cortex-global.css`** - Changes affect all views
2. **Test on all HTML pages** - Verify no regressions
3. **Document breaking changes** - Update this guide
4. **Commit with clear message:**
   ```bash
   git add cortex-brain/cx6-plan/viewer/shared/cortex-global.css
   git commit -m "feat(viewer): update badge styles for better contrast"
   ```

---

## 🚀 Next Steps

**Priority 1: Complete Shared Components (Week 1)**
- ✅ Global CSS (cortex-global.css) - DONE
- ✅ Header template (header-template.html + header-loader.js) - DONE
- ⏳ Footer template (footer-template.html + footer-loader.js)
- ⏳ Utilities (cortex-utils.js with chart/data helpers)

**Priority 2: Update Existing Files (Week 2)**
- ⏳ Update cortex-plan-viewer.html (add global CSS link)
- ⏳ Update cortex-plan-viewer-v2.html (new header + remove duplicates)
- ⏳ Update phase-detail-viewer.html (add global CSS link)

**Priority 3: Create New Views (Week 3-4)**
Using HTML-VIEWS-TODO.md as specification:
- ⏳ gap-analysis.html
- ⏳ master-plan.html
- ⏳ cortex-instructions.html
- ⏳ core-rules-viewer.html
- ⏳ governance-architecture.html
- ⏳ mcp-capabilities-explorer.html
- ⏳ orchestration-lifecycle.html
- ⏳ autonomous-execution-deep-dive.html
- ⏳ token-optimization-strategy.html
- ⏳ ado-integration-capabilities.html

**Priority 4: Polish & Enhancements (Week 5)**
- ⏳ Navigation menu
- ⏳ Theme toggle
- ⏳ Search functionality
- ⏳ Keyboard shortcuts

---

## 📚 Related Documents

- `HTML-VIEWS-TODO.md` - Master specification for all HTML views
- `HTML-VIEWS-TODO-ENHANCEMENT-SUMMARY.md` - Recent enhancements documentation
- `../master-plan.yaml` - CORTEX 6.0 implementation roadmap
- `../README.md` - CX6 plan overview

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-11  
**Author:** Asif Hussain  
**Status:** Living document - update as refactorings progress
