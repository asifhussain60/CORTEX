# Dashboard Design Reference
**Version:** 2.0 | **Updated:** 2026-02-04 | **Source:** Git History Analysis (7+ days)

## Overview

This folder contains the **definitive design specifications** for CORTEX Enterprise Repository Intelligence Dashboards, extracted from comprehensive git history analysis spanning 50+ commits over 7 days of development.

**Theme:** Dark Blue Glassmorphism  
**Tabs:** 13 comprehensive tabs for all audiences  
**Visualizations:** D3.js, ECharts, Chart.js  
**Assets:** External CSS files (main.css, glass-*.css)  
**Logo:** `CORTEX-logo-200.png` (200×200, left-justified with glow effect)

---

## 🎯 Target Audiences

| Audience | Focus Areas | Tabs |
|----------|-------------|------|
| **Executive** | Strategic overview, vendor risk, ROI | Overview, Vendors, Impact |
| **Product Owner** | Feature inventory, use cases, roadmap | Use Cases, Overview, Timeline |
| **Dev Manager** | Team productivity, quality, debt | Quality, Testing, Timeline |
| **Software Engineer** | Architecture, dependencies, patterns | Architecture, Dependencies, Patterns |
| **Leader** | Risk assessment, security, compliance | Security, Vulnerabilities, Impact |

---

## 🏗️ Architecture Decision

### External CSS (Approved Strategy)

```
company/dashboards/
├── assets/
│   ├── css/
│   │   ├── main.css                 # 251KB - Master theme
│   │   ├── glass-design-tokens.css  # CSS variables & tokens
│   │   ├── glass-base-patterns.css  # Glassmorphism patterns
│   │   ├── glass-ui-components.css  # Buttons, cards, tabs
│   │   ├── glass-animations.css     # Shimmer, glow, float
│   │   └── cortex-glass-system.css  # Core glass system
│   └── images/
│       ├── CORTEX-logo-200.png      # Header logo (200×200)
│       └── CORTEX-logo-64.png       # Favicon
├── repos/
│   ├── cortex/index.html
│   ├── kashkole/index.html
│   └── ksessions/index.html
├── data/
│   └── *.json                       # Repository analysis data
└── generate_dashboards.py           # Enterprise generator
```

### Why External CSS?

| Benefit | Impact |
|---------|--------|
| ✅ **Theme Consistency** | Single source of truth for all dashboards |
| ✅ **Maintainability** | Update once, apply everywhere |
| ✅ **Smaller HTML** | Dashboards ~50KB instead of ~300KB |
| ✅ **Browser Caching** | CSS cached across dashboard views |
| ✅ **Approved Pattern** | Matches `approved-orchestrator-view/index.html` |

---

## 🎨 Design System

### CSS Variables (from `main.css`)

```css
:root {
    /* Colors - Dark Mode Palette */
    --bg-primary: #0a0e27;
    --bg-secondary: #1a1f3a;
    --glass-bg: rgba(26, 31, 58, 0.7);
    --glass-border: rgba(255, 255, 255, 0.1);
    
    /* Accent Colors */
    --accent-primary: #00d4ff;    /* Cyan */
    --accent-secondary: #7b61ff;  /* Purple */
    
    /* Text Colors */
    --text-primary: #ffffff;
    --text-secondary: #a0a6c0;
    
    /* Status Colors */
    --success: #00ff88;
    --warning: #ffa500;
    --danger: #ff4444;
    --info: #3b82f6;
    
    /* Effects */
    --shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    --glow: 0 0 20px rgba(0, 212, 255, 0.3);
}
```

### Glassmorphism Effects

```css
.glass-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: var(--shadow);
}
```

### Logo with Glow Animation

```css
.logo-container img {
    width: 200px;
    height: 200px;
    filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.3));
    animation: logoGlow 3s ease-in-out infinite alternate;
}

@keyframes logoGlow {
    0% { filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.3)); }
    100% { filter: drop-shadow(0 0 30px rgba(0, 212, 255, 0.5)); }
}
```

---

## 📑 Tab Structure (13 Tabs)

| # | Tab | Icon | Audience | Content |
|---|-----|------|----------|---------|
| 1 | **Overview** | 📊 | All | Health score, metrics, audience cards |
| 2 | **Architecture** | 🏗️ | Engineer | Layer diagram, module breakdown |
| 3 | **Quality** | ✅ | Dev Manager | Complexity, duplication, debt |
| 4 | **Vulnerabilities** | 🛡️ | All | OWASP findings, code smells |
| 5 | **Security** | 🔒 | Leader | Secrets scan, compliance |
| 6 | **Dependencies** | 📦 | Engineer | Packages, versions, graph |
| 7 | **Testing** | 🧪 | Dev Manager | Coverage, test inventory |
| 8 | **Patterns** | 🎨 | Engineer | Design patterns, anti-patterns |
| 9 | **Use Cases** | 📋 | Product Owner | Business capabilities |
| 10 | **Timeline** | 📅 | All | Commit history, contributors |
| 11 | **Impact** | 💥 | Leader | Blast radius, risk assessment |
| 12 | **Vendors** | 🏢 | Executive | Third-party, license compliance |
| 13 | **Database** | 🗄️ | Engineer | ER diagrams, table stats |

---

## 💼 Business Language Enhancement

### BusinessTranslator (from commit `1e6bfd2b8`)

Transforms technical terminology into executive-friendly language:

```python
USE_CASE_MAPPING = {
    "crud": {"title": "📝 Manage organizational data", "icon": "📝"},
    "reporting": {"title": "📊 Track key performance indicators", "icon": "📊"},
    "authentication": {"title": "🔐 Secure user access", "icon": "🔐"},
    "api": {"title": "🔌 Connect with other systems", "icon": "🔌"},
    "workflow": {"title": "⚡ Automate business processes", "icon": "⚡"},
}
```

### Audience-Specific Descriptions

| Audience | Focus |
|----------|-------|
| Executive | Strategic overview of system health and business value |
| Product Owner | Feature inventory and development velocity metrics |
| Dev Manager | Team productivity, code quality, and technical debt |
| Engineer | Architecture, dependencies, and implementation details |
| Leader | Risk assessment, security posture, and modernization status |

---

## 📊 Visualization Libraries

| Library | Version | Use Cases |
|---------|---------|-----------|
| **D3.js v7** | Primary | Treemaps, force graphs, Sankey diagrams |
| **ECharts** | Secondary | Gauges, heatmaps, sunbursts |
| **Chart.js v4** | Tertiary | Bar charts, line charts, radar |

### Embedded vs CDN

```html
<!-- CDN (Recommended for file:// compatibility) -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<!-- For offline, embed inline -->
<script>/* D3.js v7 inline */</script>
```

---

## 🔑 Key Git Commits

| Commit | Date | Description |
|--------|------|-------------|
| `3144a4a4a` | Feb 1 | **Glassmorphism domain dashboards** - D3.js, 10 tabs, CORTEX logo glow |
| `fc2194696` | Feb 1 | **DashboardThemeTemplate** (1,100 lines) - SSOT for design |
| `1e6bfd2b8` | Feb 1 | **BusinessTranslator** - LLM content enhancement |
| `615805c9b` | Feb 1 | **Comprehensive 8-tab dashboard** - D3.js force graphs, lazy loading |
| `eeb039277` | Feb 2 | **GPT-enhanced dashboard** - 9 tabs, ECharts, comprehensive testing |
| `b6d7d2b09` | Feb 4 | **Self-contained HTML** - Embedded data, no external deps |

### Quick Lookup Commands

```bash
# View glassmorphism implementation
git show 3144a4a4a

# View DashboardThemeTemplate (1,100 lines SSOT)
git show fc2194696:company/dashboards/core/dashboard_theme.py

# View BusinessTranslator
git show 1e6bfd2b8:company/dashboards/tooling/data_collectors/business_translator.py

# View approved orchestrator CSS pattern
cat _workspaces/approved-orchestrator-view/assets/css/main.css | head -100
```

---

## 📁 Asset Locations

### CSS Files (from approved-orchestrator-view)

| File | Size | Purpose |
|------|------|---------|
| `main.css` | 251KB | Master theme with all variables |
| `glass-design-tokens.css` | 14KB | CSS custom properties |
| `glass-base-patterns.css` | 12KB | Glassmorphism patterns |
| `glass-ui-components.css` | 12KB | Cards, buttons, tabs |
| `glass-animations.css` | 11KB | Shimmer, glow, float effects |
| `cortex-glass-system.css` | 2KB | Core glass utilities |

### Image Assets

| File | Size | Purpose |
|------|------|---------|
| `CORTEX-logo-200.png` | 22KB | Header logo (200×200) |
| `CORTEX-logo-64.png` | 7KB | Favicon |

---

## 🚀 Usage

### Generate Dashboards

```bash
cd company/dashboards
python generate_dashboards.py
```

### View Dashboard

```bash
# Open directly in browser (file:// protocol)
open repos/cortex/index.html

# Or serve locally
python -m http.server 8888
# Visit http://localhost:8888/repos/cortex/index.html
```

---

## ✅ Quality Gates

| Check | Requirement |
|-------|-------------|
| HTML5 Syntax | Valid, zero errors |
| CSS Loading | All 6 CSS files load correctly |
| Logo Display | 200×200 with glow effect |
| Tab Navigation | All 13 tabs functional |
| Responsive | Mobile (480px), Tablet (768px), Desktop |
| WCAG AA | Contrast compliance verified |

---

## 📋 Implementation Checklist

- [x] External CSS references (main.css, glass-*.css)
- [x] CORTEX logo 200×200 left-justified with glow
- [x] Title right of logo with tagline
- [x] 13 comprehensive tabs
- [x] BusinessTranslator for use cases
- [x] Audience-specific cards in Overview
- [x] Embedded JSON data for interactivity
- [x] Health badge with color coding
- [x] Responsive design (mobile-first)
- [x] D3.js CDN integration

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `company/dashboards/generate_dashboards.py` | Enterprise generator |
| `_workspaces/approved-orchestrator-view/index.html` | Reference implementation |
| `docs/assets/images/cortex-logo-200.png` | Source logo |
| `_workspaces/cortex-plan/PHASE-23-STATIC-DASHBOARD-GENERATOR.yaml` | Phase plan |

---

*Generated from comprehensive git history analysis (Feb 1-4, 2026)*
