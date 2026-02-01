# CORTEX LENS Dashboard

**Version:** 2.0.0  
**Phase:** 14 - LENS Dashboard Implementation  
**AC-ID:** LENS-DASH-007  
**Architecture:** Static HTML + JSON (No FastAPI Required)

---

## 📦 Overview

The CORTEX LENS Dashboard provides AI-powered code intelligence visualization for any repository. It uses a **Static HTML + JSON architecture** - no backend server required for viewing dashboards.

### Key Features

✅ **Static Architecture** - Pure HTML + JSON, no FastAPI dependency for viewing  
✅ **Dark Glassmorphism Theme** - Elegant dark mode with CSS variables  
✅ **8-Tab CORTEX Analysis** - Full analysis for CORTEX repositories  
✅ **5-Tab External Repos** - Standard analysis for any Python project  
✅ **CLI Generation** - `cortex lens generate` creates JSON data  

---

## 🗂️ Folder Structure

```
cortex-lens/
├── lens-dashboard.html         # Main entry: Repository browser with logo
├── cortex-dashboard.html       # CORTEX 8-tab analysis dashboard
├── cli.py                      # CLI commands for generation
├── README.md                   # This file
├── static/
│   ├── css/
│   │   └── cortex-lens.css     # Dark glassmorphism theme
│   ├── js/
│   │   └── dashboard-app.js    # D3.js visualizations
│   └── assets/
│       └── cortex-logo-200.png # CORTEX logo
├── data/
│   ├── cortex/                 # CORTEX JSON data (8 files)
│   │   ├── overview.json
│   │   ├── dependencies.json
│   │   ├── classes.json
│   │   ├── timeline.json
│   │   ├── impact.json
│   │   ├── brain.json
│   │   ├── governance.json
│   │   └── orchestrators.json
│   └── repos/                  # External repo data
│       └── repos.json          # Registry of analyzed repos
└── backend/                    # Legacy (not used for viewing)
```

---

## 🚀 Quick Start

### 1. View Dashboard (No Setup Required)

```bash
# Start simple HTTP server
cd cortex-lens
python3 -m http.server 8080

# Open in browser
open http://localhost:8080/lens-dashboard.html
```

### 2. Generate Dashboard Data

```bash
# Generate for CORTEX (8 tabs)
python3 cortex-lens/cli.py generate . --cortex

# Generate for external repo (5 tabs)
python3 cortex-lens/cli.py generate /path/to/repo
```

### 3. CLI Commands

```bash
# All commands
python3 cortex-lens/cli.py --help

# Generate dashboard data
python3 cortex-lens/cli.py generate <repo> [--cortex] [--open]

# Serve dashboard
python3 cortex-lens/cli.py serve [--port 8080] [--open]

# Open in browser (auto-starts server)
python3 cortex-lens/cli.py open

# List generated data
python3 cortex-lens/cli.py cache list

# Clear cache
python3 cortex-lens/cli.py cache clear --all
```

---

## 📊 Architecture

### Entry Points

| URL | File | Purpose |
|-----|------|---------|
| `/lens-dashboard.html` | Main entry | Logo hero + repository tiles |
| `/cortex-dashboard.html?repo=cortex` | 8-tab | CORTEX analysis |
| `/cortex-dashboard.html?repo=<slug>` | 5-tab | External repo analysis |

### Tabs

| # | Tab | CORTEX | External | Data Source |
|---|-----|--------|----------|-------------|
| 1 | Overview | ✅ | ✅ | overview.json |
| 2 | Dependencies | ✅ | ✅ | dependencies.json |
| 3 | Classes | ✅ | ✅ | classes.json |
| 4 | Timeline | ✅ | ✅ | timeline.json |
| 5 | Impact | ✅ | ✅ | impact.json |
| 6 | Brain | ✅ | ❌ | brain.json |
| 7 | Governance | ✅ | ❌ | governance.json |
| 8 | Orchestrators | ✅ | ❌ | orchestrators.json |

### Tech Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| SPA Framework | Alpine.js 3.13.3 | Reactive UI, tabs |
| Visualizations | D3.js 7.8.5 | Force graph, timeline |
| Diagrams | Mermaid 10.6.1 | Class diagrams |
| Styling | Custom CSS | Dark glassmorphism |

---

## 🔧 Integration

### LENSDashboardOrchestrator

The orchestrator generates all JSON files from LENS analyzers:

```python
from cortex.orchestrators.support.lens_dashboard_orchestrator import (
    get_lens_dashboard_orchestrator
)

orchestrator = get_lens_dashboard_orchestrator()
result = orchestrator.generate_for_repo(
    repo_path=Path("/path/to/repo"),
    repo_name="my-project",
    is_cortex=False
)

print(result["files_generated"])
# ['overview.json', 'dependencies.json', 'classes.json', ...]
```

### LENS Analyzers Used

- **ASTAnalyzer** - Classes, functions, complexity
- **GitHistoryAnalyzer** - Commits, timeline, authors
- **CommentExtractor** - TODOs, FIXMEs, docstrings

---

## 🎨 Theme Customization

Edit `static/css/cortex-lens.css` to customize:

```css
:root {
    --bg-primary: #0a0e27;        /* Main background */
    --accent-primary: #00d4ff;    /* Cyan accent */
    --accent-secondary: #7b2cbf;  /* Purple accent */
    --glass-bg: rgba(26, 31, 60, 0.8);
}
```

---

## 📝 Phase 14 Status

| Task | Status |
|------|--------|
| Dark CSS Theme | ✅ Complete |
| 8-Tab HTML Dashboard | ✅ Complete |
| JSON Data Files | ✅ Complete |
| D3.js Visualizations | ✅ Complete |
| CLI Commands | ✅ Complete |
| LENSDashboardOrchestrator | ✅ Complete |
| Documentation | ✅ Complete |

**Phase 14 Progress:** 100% ✅

---

## 📚 Related Documentation

- [Phase 18 Enterprise Dashboard System](_workspaces/cortex-plan/PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml) — Current dashboard architecture
- [Phase 14 Implementation Plan (Archived)](_workspaces/cortex-plan/.archive/PHASE-14-LENS-DASHBOARD-IMPLEMENTATION.yaml) — Historical reference
- [LENS Intelligence System](docs/05-lens-protocol/)
- [LENS Analyzers](cortex/brain/analysis/)

---

**Maintained by:** Asif Hussain  
**Last Updated:** 2026-02-01
