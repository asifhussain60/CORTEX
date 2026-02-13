# Phase 14 - Quick Reference Card
**Status:** NOT_STARTED (1/15 tasks completed)  
**Estimated Effort:** 8-10 days  
**Last Updated:** 2026-01-29  
**Plan File:** `PHASE-14-LENS-DASHBOARD.yaml`

---

## 🎯 Key Architecture Decisions

| Aspect | Decision |
|--------|----------|
| CSS Theme | Dark Glassmorphism from `_workspaces/dashboard` |
| CORTEX Logo | 300x300 hero on index.html |
| Architecture | Static HTML + Pre-generated JSON (NO API) |
| Tabs | All 8 tabs configured |
| Entry Point | index.html = Repo Browser |
| Folder | Single `cortex-lens/` only |

---

## 📁 Target Folder Structure

```
cortex-lens/
├── index.html              # Repository browser + LOGO HERO
├── cortex-dashboard.html   # 8-tab CORTEX analysis
├── cli.py                  # Static site generator CLI
├── README.md
├── static/
│   ├── css/
│   │   └── cortex-lens.css     # Dark glassmorphism
│   ├── js/
│   │   ├── dashboard-app.js    # Alpine.js app
│   │   └── tab-loader.js       # Tab content loader
│   ├── assets/
│   │   └── cortex-logo-200.png # CORTEX logo (300x300 display)
│   └── vendor/ → symlink       # Alpine, D3, Mermaid
├── data/
│   └── cortex/                 # Pre-generated JSON
│       ├── overview.json
│       ├── dependency-graph.json
│       ├── class-diagrams.json
│       ├── temporal-analysis.json
│       ├── impact-analysis.json
│       ├── brain-architecture.json
│       ├── governance-heatmap.json
│       └── orchestrator-constellation.json
└── backend/
    ├── generator.py            # JSON data generator
    └── orchestrator.py         # Simplified orchestration
```

---

## 🏷️ 8 Tab Configuration

```javascript
tabs: [
  { id: 'overview',      label: 'Overview',      icon: '📦' },  // Universal
  { id: 'dependencies',  label: 'Dependencies',  icon: '🕸️' },  // Universal
  { id: 'classes',       label: 'Classes',       icon: '📐' },  // Universal
  { id: 'timeline',      label: 'Timeline',      icon: '📈' },  // Universal
  { id: 'impact',        label: 'Impact',        icon: '💥' },  // Universal
  { id: 'brain',         label: 'Brain',         icon: '🧠' },  // CORTEX only
  { id: 'governance',    label: 'Governance',    icon: '✅' },  // CORTEX only
  { id: 'orchestrators', label: 'Orchestrators', icon: '🎼' }   // CORTEX only
]
```

---

## 🎨 CSS Source

**Primary:** `_workspaces/dashboard/cortex-unified.css`

Key Variables:
```css
:root[data-theme="dark"] {
    --bg-primary: #0a0e27;
    --bg-secondary: #131829;
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --text-primary: #ffffff;
    --accent-primary: #00d4ff;
}
```

---

## ⚡ CLI Commands

```bash
# Generate JSON data for a repository
python cortex-lens/cli.py generate --repo /path/to/repo

# Start static HTTP server
python cortex-lens/cli.py serve --port 8080

# Generate and open in browser
python cortex-lens/cli.py open cortex
```

---

## ✅ Task Checklist

- [x] **001** Cleanup legacy (cortex_lens, v2.html)
- [ ] **002** Finalize folder structure
- [ ] **003** Dark theme CSS
- [ ] **004** index.html (logo hero)
- [ ] **005** cortex-dashboard.html (8 tabs)
- [ ] **006** dashboard-app.js (Alpine)
- [ ] **007** tab-loader.js
- [ ] **008** JSON data schemas
- [ ] **009** generator.py
- [ ] **010** cli.py
- [ ] **011** Sample data for CORTEX
- [ ] **012** Integration testing
- [ ] **013** Documentation
- [ ] **014** Remove FastAPI dependency
- [ ] **015** Vendor symlink

---

## 🚫 Deprecated (DO NOT USE)

- ❌ `cortex_lens/` folder (DELETED)
- ❌ `cortex-dashboard-v2.html` (DELETED)
- ❌ `app.py` FastAPI server (TO DELETE)
- ❌ `backend/routes.py` (TO DELETE)
- ❌ `backend/cache_manager.py` (TO DELETE)

---

## 📋 Acceptance Criteria

**Phase Complete When:**
1. index.html shows CORTEX logo at 300x300 centered ✓
2. Dark glassmorphism theme applied ✓
3. cortex-dashboard.html has all 8 tabs ✓
4. Tab switching works instantly ✓
5. JSON data loads from static files ✓
6. Works with `python -m http.server` ✓
7. No FastAPI dependency for viewing ✓
8. No external CDN dependencies ✓
