# CORTEX LENS Dashboard - Self-Contained SPA

**Version:** 1.0.0  
**Phase:** 14 - LENS Dashboard Implementation  
**AC-ID:** LENS-DASH-007  
**Authority:** CORE-038 (File Placement), CORE-040 (Documentation Lifecycle)

---

## 📦 Overview

The CORTEX LENS Dashboard is a **self-contained Single Page Application (SPA)** that provides AI-powered code intelligence visualization for any repository. It operates **fully offline** with all dependencies bundled locally.

### Key Features

✅ **Offline-First Architecture** - No external CDN dependencies  
✅ **Lazy-Loaded Modules** - Initial load <200KB, full bundle 1.5MB  
✅ **Context-Aware Tabs** - 5 universal + 3 CORTEX-specific tabs  
✅ **Alpine.js Framework** - 15KB reactive SPA (vs React 130KB)  
✅ **Built-in HTTP Server** - No npm/node required  

---

## 🗂️ Folder Structure

```
cortex-lens/
├── app.py                      # FastAPI server (main entry point)
├── repo-dashboards.html        # Main: Repository browser with tiles
├── cortex-dashboard.html       # Direct: CORTEX 8-tab analysis
├── README.md                   # This file
├── frontend/
│   ├── css/
│   │   └── dashboard-ui.css    # Shared styles
│   └── js/
│       ├── dashboard-app.js    # Shared Alpine.js logic
│       ├── tab-controller.js   # Tab management
│       ├── repo-tiles.js       # Repository grid
│       └── overlay-ui.js       # Overlay system
├── backend/
│   ├── orchestrator.py         # Routes to cortex/visualization/*
│   ├── routes.py               # FastAPI endpoints
│   ├── cache_manager.py        # Manages .cortex/, ~/.cortex/, reports/
│   └── repository_loader.py    # Analyzes and caches repositories
└── tests/
    └── test_*.py               # Dashboard-specific tests
```

---

## 🚀 Quick Start

### 1. Bundle Dependencies (One-Time Setup)

```bash
# Download all dependencies locally (Alpine.js, D3.js, Mermaid, Tailwind)
python3 cortex/visualization/scripts/bundle_dependencies.py

# Verify bundle integrity
python3 cortex/visualization/scripts/bundle_dependencies.py verify
```

### 2. Start Dashboard Server

```bash
# Start server on http://localhost:8888
python3 cortex-lens/app.py

# Custom port
uvicorn cortex-lens.app:app --host 0.0.0.0 --port 8080
```

### 3. Access Dashboards

- **Repository Browser:** http://localhost:8888/
- **CORTEX Direct:** http://localhost:8888/cortex
- **Health Check:** http://localhost:8888/health

---

## 📊 Architecture

### Entry Points

| URL | File | Purpose |
|-----|------|---------|
| `/` | `repo-dashboards.html` | Repository browser with tiles |
| `/cortex` | `cortex-dashboard.html` | CORTEX 8-tab analysis |
| `/api/*` | `app.py` | Data endpoints |
| `/static/*` | `cortex/visualization/static/` | Assets |

### Bundle Strategy

| Bundle | Size | Load Strategy |
|--------|------|---------------|
| Core (Alpine.js + app) | 175KB | Initial load |
| D3.js modules | 250KB | Lazy (Tabs 2, 4, 5, 7, 8) |
| Mermaid module | 850KB | Lazy (Tabs 3, 6) |
| Tailwind CSS | 80KB | Initial load |
| **Total** | **1.5MB** | **Initial: 255KB** |

### Tab Configuration

**Universal Tabs (ALL repositories):**
1. 📦 Repository Overview (business language)
2. 🕸️ Dependency Graph (D3.js call graph)
3. 📊 Class Diagrams (Mermaid UML)
4. 📈 Temporal Analysis (Git timeline)
5. 👥 Author Network (collaboration graph)

**CORTEX-Specific Tabs (CORTEX repository only):**
6. 🧠 Brain Architecture (4-tier structure)
7. ✅ Governance Compliance (CORE rules)
8. 🎼 Orchestrator Constellation (wiring map)

---

## 🔧 API Endpoints

### Repository Management

```bash
# List repositories
GET /api/repositories

# Get dashboard tabs for repository
GET /api/dashboard/tabs/{repo_id}
```

### Module Loading

```bash
# Get lazy loader manifest
GET /api/loader/manifest

# Get lazy loader JavaScript
GET /api/loader/javascript
```

### Health

```bash
# Health check
GET /health
```

---

## 🧪 Testing

```bash
# Run all dashboard tests
python3 -m pytest tests/visualization/scripts/ -v

# Test specific component
python3 -m pytest tests/visualization/scripts/test_bundle_dependencies.py -v
python3 -m pytest tests/visualization/scripts/test_lazy_module_loader.py -v
```

---

## 📁 Output Locations

| Repository Type | Output Path | Gitignored |
|----------------|-------------|------------|
| External repos | `<repo>/.cortex/lens-dashboard/` | Yes |
| CORTEX self-analysis | `reports/lens-dashboard/` | No |
| Remote repos | `~/.cortex/cache/<owner>/<repo>/` | Yes |
| CI artifacts | `$CI_ARTIFACTS_DIR/lens-dashboard/` | Yes |

---

## 🔗 Related Documentation

- [Phase 14 Implementation Plan](_workspaces/docker-plan/PHASE-14-LENS-DASHBOARD-IMPLEMENTATION.yaml)
- [LENS Intelligence System](docs/05-lens-protocol/)
- [Visualization API Reference](docs/06-api-reference/)

---

## 🛠️ Development

### Adding New Tabs

1. Create renderer: `cortex/visualization/renderers/your_renderer.py`
2. Create template: `cortex/visualization/templates/tabs/your_tab.html`
3. Update `TAB_MODULE_REQUIREMENTS` in `lazy_module_loader.py`
4. Add tests: `tests/visualization/renderers/test_your_renderer.py`

### Adding New Dependencies

1. Add to `DEPENDENCIES` in `bundle_dependencies.py`
2. Run bundling script: `python3 cortex/visualization/scripts/bundle_dependencies.py --force`
3. Update `MODULES` in `lazy_module_loader.py`
4. Test bundle: `python3 cortex/visualization/scripts/bundle_dependencies.py verify`

---

## 📝 License

Part of CORTEX project. See root LICENSE for details.

---

**Maintained by:** Asif Hussain  
**Last Updated:** 2026-01-29
