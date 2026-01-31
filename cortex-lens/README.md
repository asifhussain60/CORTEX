# 🧠 CORTEX LENS Dashboard# CORTEX LENS Dashboard



**Cognitive Repository Analysis & Intelligence Dashboard****Version:** 2.0.0  

**Phase:** 14 - LENS Dashboard Implementation  

A sophisticated, offline-first web dashboard for analyzing CORTEX repository structure, dependencies, orchestrator network, git history, and architectural insights.**AC-ID:** LENS-DASH-007  

**Architecture:** Static HTML + JSON (No FastAPI Required)

---

---

## 📋 Table of Contents

## 📦 Overview

- [Features](#features)

- [Quick Start](#quick-start)The CORTEX LENS Dashboard provides AI-powered code intelligence visualization for any repository. It uses a **Static HTML + JSON architecture** - no backend server required for viewing dashboards.

- [Requirements](#requirements)

- [Installation](#installation)### Key Features

- [Usage](#usage)

- [Dashboard Tabs](#dashboard-tabs)✅ **Static Architecture** - Pure HTML + JSON, no FastAPI dependency for viewing  

- [Data Generation](#data-generation)✅ **Dark Glassmorphism Theme** - Elegant dark mode with CSS variables  

- [Architecture](#architecture)✅ **8-Tab CORTEX Analysis** - Full analysis for CORTEX repositories  

- [Development](#development)✅ **5-Tab External Repos** - Standard analysis for any Python project  

- [Troubleshooting](#troubleshooting)✅ **CLI Generation** - `cortex lens generate` creates JSON data  

- [Performance](#performance)

---

---

## 🗂️ Folder Structure

## ✨ Features

```

### 🎨 **Modern Design**cortex-lens/

- **Dark blue glassmorphism theme** with smooth animations├── lens-dashboard.html         # Main entry: Repository browser with logo

- **Responsive design** for desktop, tablet, and mobile (320px+)├── cortex-dashboard.html       # CORTEX 8-tab analysis dashboard

- **Offline-first** architecture (no CDN dependencies)├── cli.py                      # CLI commands for generation

- **Print-friendly** styles for documentation├── README.md                   # This file

├── static/

### 📊 **6 Interactive Visualizations**│   ├── css/

1. **Overview** - Repository statistics and business context│   │   └── cortex-lens.css     # Dark glassmorphism theme

2. **Dependencies** - Import graph with 1005 modules (D3.js force-directed)│   ├── js/

3. **Orchestrators** - 27 orchestrators network (core/domain/support)│   │   └── dashboard-app.js    # D3.js visualizations

4. **Timeline** - 200 commits scatter plot over time│   └── assets/

5. **Impact** - File change hotspots analysis (415 files)│       └── cortex-logo-200.png # CORTEX logo

6. **Brain** - 4-tier architecture visualization├── data/

│   ├── cortex/                 # CORTEX JSON data (8 files)

### ⚡ **Performance Optimized**│   │   ├── overview.json

- **Node limiting** (500 max) for large dependency graphs│   │   ├── dependencies.json

- **Loading spinners** for smooth UX during rendering│   │   ├── classes.json

- **Lazy rendering** with setTimeout to prevent UI blocking│   │   ├── timeline.json

- **Local D3.js v7.9.0** bundle (273KB, no network requests)│   │   ├── impact.json

│   │   ├── brain.json

### 🔍 **Intelligence Features**│   │   ├── governance.json

- **Circular dependency detection** (3 detected)│   │   └── orchestrators.json

- **Hotspot analysis** (files changed >5 times)│   └── repos/                  # External repo data

- **Author attribution** from git history│       └── repos.json          # Registry of analyzed repos

- **Category-based coloring** (core=cyan, domain=purple, support=green)└── backend/                    # Legacy (not used for viewing)

- **Interactive tooltips** with detailed metadata```



------



## 🚀 Quick Start## 🚀 Quick Start



### View Dashboard### 1. View Dashboard (No Setup Required)



```bash```bash

# Navigate to dashboard directory# Start simple HTTP server

cd cortex-lenscd cortex-lens

python3 -m http.server 8080

# Open in browser (macOS)

open index.html# Open in browser

open http://localhost:8080/lens-dashboard.html

# Or use Python server```

python3 -m http.server 8000

# Then visit: http://localhost:8000### 2. Generate Dashboard Data

```

```bash

### Regenerate Data# Generate for CORTEX (8 tabs)

python3 cortex-lens/cli.py generate . --cortex

```bash

# Generate latest dashboard data# Generate for external repo (5 tabs)

python3 -m cortex.scripts.generate_dashboard_datapython3 cortex-lens/cli.py generate /path/to/repo

```

# Open dashboard

open cortex-lens/index.html### 3. CLI Commands

```

```bash

---# All commands

python3 cortex-lens/cli.py --help

## 📦 Requirements

# Generate dashboard data

### Runtimepython3 cortex-lens/cli.py generate <repo> [--cortex] [--open]

- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+)

- JavaScript enabled# Serve dashboard

python3 cortex-lens/cli.py serve [--port 8080] [--open]

### Development

- Python 3.8+# Open in browser (auto-starts server)

- Git (for git history analysis)python3 cortex-lens/cli.py open

- PyYAML >= 6.0

# List generated data

---python3 cortex-lens/cli.py cache list



## 📥 Installation# Clear cache

python3 cortex-lens/cli.py cache clear --all

```bash```

# 1. Clone repository

git clone https://github.com/yourusername/CORTEX.git---

cd CORTEX

## 📊 Architecture

# 2. Install dependencies

pip3 install -r requirements.txt### Entry Points



# 3. Generate data| URL | File | Purpose |

python3 -m cortex.scripts.generate_dashboard_data|-----|------|---------|

| `/lens-dashboard.html` | Main entry | Logo hero + repository tiles |

# 4. Open dashboard| `/cortex-dashboard.html?repo=cortex` | 8-tab | CORTEX analysis |

open cortex-lens/index.html| `/cortex-dashboard.html?repo=<slug>` | 5-tab | External repo analysis |

```

### Tabs

---

| # | Tab | CORTEX | External | Data Source |

## 🎯 Usage|---|-----|--------|----------|-------------|

| 1 | Overview | ✅ | ✅ | overview.json |

### Basic Usage| 2 | Dependencies | ✅ | ✅ | dependencies.json |

| 3 | Classes | ✅ | ✅ | classes.json |

1. **Open:** `open cortex-lens/index.html`| 4 | Timeline | ✅ | ✅ | timeline.json |

2. **Navigate:** Click tab buttons or use Tab key| 5 | Impact | ✅ | ✅ | impact.json |

3. **Interact:** Hover for tooltips, drag nodes in graphs| 6 | Brain | ✅ | ❌ | brain.json |

| 7 | Governance | ✅ | ❌ | governance.json |

### Advanced Usage| 8 | Orchestrators | ✅ | ❌ | orchestrators.json |



**Filter Orchestrators:**### Tech Stack

```python

# Edit generate_dashboard_data.py line 181| Component | Library | Purpose |

for category in ["core"]:  # Only core orchestrators|-----------|---------|---------|

```| SPA Framework | Alpine.js 3.13.3 | Reactive UI, tabs |

| Visualizations | D3.js 7.8.5 | Force graph, timeline |

**Increase Commit History:**| Diagrams | Mermaid 10.6.1 | Class diagrams |

```python| Styling | Custom CSS | Dark glassmorphism |

# Edit generate_dashboard_data.py line 256

result = analyzer.get_recent_commits(max_commits=500)---

```

## 🔧 Integration

---

### LENSDashboardOrchestrator

## 📊 Dashboard Tabs

The orchestrator generates all JSON files from LENS analyzers:

| Tab | Data | Features |

|-----|------|----------|```python

| **Overview** | Business context | Statistics, description |from cortex.orchestrators.support.lens_dashboard_orchestrator import (

| **Dependencies** | 1005 modules, 1009 imports | Force-directed graph, circular detection |    get_lens_dashboard_orchestrator

| **Orchestrators** | 27 orchestrators | Network with categories, dependencies |)

| **Timeline** | 200 commits | Scatter plot, author stats |

| **Impact** | 415 files | Hotspots bar chart |orchestrator = get_lens_dashboard_orchestrator()

| **Brain** | 4 tiers | Stacked architecture |result = orchestrator.generate_for_repo(

    repo_path=Path("/path/to/repo"),

---    repo_name="my-project",

    is_cortex=False

## 🔧 Data Generation)



### CLIprint(result["files_generated"])

# ['overview.json', 'dependencies.json', 'classes.json', ...]

```bash```

python3 -m cortex.scripts.generate_dashboard_data

```### LENS Analyzers Used



### Output- **ASTAnalyzer** - Classes, functions, complexity

- **GitHistoryAnalyzer** - Commits, timeline, authors

| File | Size | Purpose |- **CommentExtractor** - TODOs, FIXMEs, docstrings

|------|------|---------|

| `overview.json` | 4KB | Business description |---

| `dependencies.json` | 392KB | Import graph |

| `orchestrators.json` | 12KB | Orchestrator network |## 🎨 Theme Customization

| `timeline.json` | 48KB | Git history |

| `impact.json` | 4KB | File hotspots |Edit `static/css/cortex-lens.css` to customize:

| `brain.json` | 4KB | 4-tier architecture |

```css

---:root {

    --bg-primary: #0a0e27;        /* Main background */

## 🏗️ Architecture    --accent-primary: #00d4ff;    /* Cyan accent */

    --accent-secondary: #7b2cbf;  /* Purple accent */

```    --glass-bg: rgba(26, 31, 60, 0.8);

cortex-lens/}

├── index.html              # Main entry```

├── data/cortex/            # JSON data files

├── static/---

│   ├── css/                # Styles + responsive

│   ├── js/                 # Tab logic + D3 renderers## 📝 Phase 14 Status

│   └── vendor/             # D3.js v7 (local)

```| Task | Status |

|------|--------|

**Stack:** HTML5, CSS3, Vanilla JS, D3.js v7.9.0, Python 3.8+| Dark CSS Theme | ✅ Complete |

| 8-Tab HTML Dashboard | ✅ Complete |

---| JSON Data Files | ✅ Complete |

| D3.js Visualizations | ✅ Complete |

## 🛠️ Development| CLI Commands | ✅ Complete |

| LENSDashboardOrchestrator | ✅ Complete |

### Local Server| Documentation | ✅ Complete |



```bash**Phase 14 Progress:** 100% ✅

cd cortex-lens

python3 -m http.server 8000---

# Visit: http://localhost:8000

```##  Related Documentation



### Edit Visualizations- [Phase 14 Implementation Plan](_workspaces/docker-plan/PHASE-14-LENS-DASHBOARD-IMPLEMENTATION.yaml)

- [LENS Intelligence System](docs/05-lens-protocol/)

```javascript- [LENS Analyzers](cortex/brain/analysis/)

// cortex-lens/static/js/d3-viz.js

// Change node radius:---

.attr('r', 12)  // Default: 8

```**Maintained by:** Asif Hussain  

**Last Updated:** 2026-01-29

### Test Responsive

Chrome DevTools → Toggle device toolbar (Ctrl+Shift+M)
- Mobile: 375x667
- Tablet: 768x1024
- Desktop: 1920x1080

---

## 🐛 Troubleshooting

### "Loading..." Forever

```bash
# Regenerate data
python3 -m cortex.scripts.generate_dashboard_data

# Verify files
ls -la cortex-lens/data/cortex/*.json
```

### Timeline/Impact No Data

```bash
# Check .git exists
ls -la .git

# Test git command
git log -n5 --pretty=format:"%H|%an|%ai|%s" --name-only
```

### Blank Visualizations

```bash
# Check D3.js exists
ls -la cortex-lens/static/vendor/d3.v7.min.js

# Open browser console (F12) for errors
```

---

## ⚡ Performance

### Optimizations

- **Node limiting:** 500 max (internal > external)
- **Lazy rendering:** setTimeout(10ms) for spinner display
- **Force simulation:** Alpha 0.3, 300 iterations
- **Mobile:** 300 nodes, 300px height

### Benchmarks

| Metric | Value | Target |
|--------|-------|--------|
| Initial Load | 1.2s | <2s |
| Tab Switch | 150ms | <200ms |
| Graph Render | 800ms | <1s |
| Mobile Scroll | 60fps | 60fps |

---

**Built with 🧠 by CORTEX Team** | **Version:** 1.0.0 | **Updated:** January 31, 2026
