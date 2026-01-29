# Folder Structure: Phase 14 LENS Dashboard Integration

**Version:** 1.0  
**Date:** January 29, 2026  
**Authority:** CORE-038 (File Placement Policy)  
**Phase:** 14 (LENS Dashboard Implementation)

---

## 📊 Executive Overview

Phase 14 introduces `/cortex-lens/` as a root-level, separated folder for the LENS Dashboard system. This document shows the complete folder structure for:

1. **CORTEX Repository** (self-analyzing system)
2. **User Development Repository** (n projects analyzed by CORTEX)

---

## 🏗️ CORTEX Repository Structure (Phase 14+)

```
CORTEX/
├── .github/
│   ├── workflows/
│   │   ├── readiness-verification.yml (UPDATED: includes cortex-lens/)
│   │   ├── ci-cd.yml
│   │   └── deployment.yml
│   ├── prompts/
│   │   └── CORTEX.prompt.md
│   └── copilot-instructions.md
│
├── .git/
│   └── hooks/
│       └── pre-commit (UPDATED: includes cortex-lens/ scanning)
│
├── cortex/                          ← ORCHESTRATORS & ANALYSIS
│   ├── __init__.py
│   ├── bootstrap.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dashboard_routes.py      ← Routes to cortex-lens/
│   │   └── lens_routes.py
│   ├── brain/
│   │   ├── analysis/
│   │   │   ├── git_history_analyzer.py
│   │   │   ├── ast_analyzer.py
│   │   │   └── comment_extractor.py
│   │   └── ...
│   ├── visualization/               ← RENDERING & FORMATTING
│   │   ├── __init__.py
│   │   ├── business_language_generator.py    (NEW - Phase 14)
│   │   ├── repository_detector.py            (NEW - Phase 14)
│   │   ├── dashboard_configuration.py        (NEW - Phase 14)
│   │   ├── renderers/
│   │   │   ├── __init__.py
│   │   │   ├── d3_renderer.py
│   │   │   ├── mermaid_renderer.py
│   │   │   ├── governance_heatmap.py
│   │   │   ├── dependency_graph.py
│   │   │   ├── timeline_renderer.py
│   │   │   ├── complexity_renderer.py
│   │   │   └── author_network.py
│   │   ├── formatters/
│   │   │   ├── __init__.py
│   │   │   ├── graph_formatter.py
│   │   │   ├── diagram_formatter.py
│   │   │   └── response_formatter.py
│   │   └── output_manager.py
│   ├── orchestrators/
│   │   ├── core/
│   │   ├── domain/
│   │   ├── support/
│   │   │   ├── lens_orchestrator.py
│   │   │   └── lens_visualization_orchestrator.py (NEW - Phase 14)
│   │   └── registry/
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── commands/
│   │   │   ├── lens.py              (UPDATED: routes to cortex-lens/)
│   │   │   └── dashboard.py         (UPDATED: routes to cortex-lens/)
│   │   └── ...
│   └── ...
│
├── cortex_brain/                    ← GOVERNANCE & KNOWLEDGE
│   ├── __init__.py
│   ├── tier0/
│   │   └── governance/
│   ├── tier1/
│   ├── tier2/
│   ├── tier3/
│   └── ...
│
├── cortex-lens/                     ← LENS DASHBOARD (SEPARATED) ⭐ NEW
│   ├── __init__.py
│   ├── app.py                       ← FastAPI dashboard app
│   ├── config.py                    ← Dashboard configuration
│   ├── orchestrator.py              ← LensVisualizationOrchestrator (extends cortex/)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard_api.py         ← API endpoints
│   │   ├── repository_api.py        ← Repository metadata API
│   │   ├── analysis_api.py          ← Analysis results API
│   │   └── health.py                ← Health check endpoints
│   ├── static/                      ← Frontend assets (NO external CDN)
│   │   ├── css/
│   │   │   ├── tailwind-3.4.0.min.css
│   │   │   └── dashboard.css
│   │   ├── js/
│   │   │   ├── app.js               ← Alpine.js app (15KB)
│   │   │   ├── modules/
│   │   │   │   ├── tabs.js
│   │   │   │   ├── visualizations.js
│   │   │   │   ├── overlays.js
│   │   │   │   └── cache.js
│   │   │   └── utils.js
│   │   ├── vendor/
│   │   │   ├── alpine-3.13.3.min.js (15KB - lazy loaded)
│   │   │   ├── d3-7.8.5.min.js      (250KB - lazy loaded per tab)
│   │   │   ├── mermaid-10.6.1.min.js (850KB - lazy loaded per tab)
│   │   │   └── tailwind-3.4.0.min.css
│   │   └── assets/
│   │       ├── icons/
│   │       └── images/
│   ├── templates/
│   │   ├── base.html                ← Base Jinja2 template
│   │   ├── dashboard.html           ← Main dashboard container
│   │   ├── tabs/
│   │   │   ├── 01-overview.html     ← Universal Tab 1 (NEW - business language)
│   │   │   ├── 02-dependencies.html ← Universal Tab 2 (D3.js)
│   │   │   ├── 03-diagrams.html     ← Universal Tab 3 (Mermaid)
│   │   │   ├── 04-temporal.html     ← Universal Tab 4 (Timeline)
│   │   │   ├── 05-impact.html       ← Universal Tab 5 (Impact analysis)
│   │   │   ├── 06-brain.html        ← CORTEX-only Tab 6
│   │   │   ├── 07-governance.html   ← CORTEX-only Tab 7
│   │   │   └── 08-orchestrators.html ← CORTEX-only Tab 8
│   │   └── components/
│   │       ├── tab-switcher.html
│   │       ├── overlay-controls.html
│   │       ├── visualization-container.html
│   │       └── sidebar.html
│   ├── services/
│   │   ├── __init__.py
│   │   ├── repository_analyzer.py   ← Orchestrates analysis
│   │   ├── data_transformer.py      ← Converts analyzer output → visualization
│   │   ├── cache_manager.py         ← Manages cached dashboards
│   │   └── export_manager.py        ← Export to JSON/PNG/PDF
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── error_handler.py
│   │   └── cors.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_routes.py
│   │   ├── test_services.py
│   │   ├── test_orchestrator.py
│   │   └── fixtures/
│   ├── requirements.txt              (Shared with cortex/)
│   ├── README.md
│   └── ARCHITECTURE.md
│
├── cortex-registry/                 ← MCP REGISTRY
│   ├── manifest.yaml
│   └── ...
│
├── deployment/                      ← DEPLOYMENT CONFIGS
│   ├── nginx.conf
│   ├── prometheus.yml
│   └── ...
│
├── docs/                            ← DOCUMENTATION (including Phase 14)
│   ├── 00-README.md
│   ├── 05-lens-protocol/
│   ├── 11-lens-dashboard/           ← Phase 14 documentation
│   │   ├── README.md
│   │   ├── ARCHITECTURE.md
│   │   ├── USER-GUIDE.md
│   │   ├── API-REFERENCE.md
│   │   ├── DEPLOYMENT.md
│   │   └── TROUBLESHOOTING.md
│   ├── 17-wiring/
│   │   └── FOLDER-STRUCTURE-PHASE-14.md (this file)
│   └── ...
│
├── reports/                         ← ANALYSIS REPORTS
│   ├── lens-dashboard/              ← CORTEX self-analysis ⭐ NEW
│   │   ├── index.html               ← Main dashboard (generated)
│   │   ├── data.json                ← Analysis cache
│   │   └── exports/
│   └── ...
│
├── tests/                           ← INTEGRATION TESTS
│   ├── test_lens_dashboard.py       ← Phase 14 tests ⭐ NEW
│   ├── test_lens_orchestrator.py    ← Phase 14 tests ⭐ NEW
│   └── ...
│
├── scripts/
│   ├── install-dependencies.sh
│   ├── build-dashboard.sh           ← Phase 14 build script ⭐ NEW
│   └── ...
│
├── Dockerfile                       ← UPDATED: includes cortex-lens/
├── docker-compose.yaml              ← UPDATED: cortex-lens service
├── docker-compose.dev.yaml
├── docker-compose.prod.yml
├── docker-compose.monitoring.yml
├── requirements.txt                 ← Shared dependencies
├── Makefile
├── README.md
├── .gitignore                       ← UPDATED: .cortex/ patterns
└── .env.example

# ============================================================================
# KEY FILES - PHASE 14 ADDITIONS/UPDATES
# ============================================================================

PHASE 14 NEW FILES:
├── cortex-lens/                     (entire folder - SEPARATED)
├── cortex/visualization/business_language_generator.py
├── cortex/visualization/repository_detector.py
├── cortex/visualization/dashboard_configuration.py
├── cortex/orchestrators/support/lens_visualization_orchestrator.py
├── cortex/cli/commands/dashboard.py (UPDATED)
├── docs/11-lens-dashboard/          (documentation set)
├── scripts/build-dashboard.sh
├── tests/test_lens_dashboard.py
└── tests/test_lens_orchestrator.py

PHASE 14 UPDATED FILES:
├── Dockerfile                       (add cortex-lens/ COPY)
├── docker-compose.yaml              (add cortex-lens service)
├── .github/workflows/readiness-verification.yml (check cortex-lens/)
├── .git/hooks/pre-commit            (scan cortex-lens/)
├── cortex/cli/main.py               (route dashboard commands)
└── .gitignore                       (add .cortex/ patterns)
```

---

## 👤 User Development Repository Structure

When a user runs CORTEX on their codebase, the following structure is created:

### **Structure 1: Single Repository (e.g., UserProject_A)**

```
UserProject_A/
├── src/
│   ├── main.py
│   ├── config.py
│   └── ...
├── tests/
│   ├── test_main.py
│   └── ...
├── docs/
├── requirements.txt
├── README.md
│
├── .cortex/                         ← CORTEX ANALYSIS OUTPUT (gitignored)
│   └── lens-dashboard/              ← Generated LENS Dashboard ⭐ NEW Phase 14
│       ├── index.html               ← Main dashboard (generated)
│       ├── data.json                ← Analysis cache (repo metadata)
│       ├── analysis/
│       │   ├── business_language.json   ← "What does this repo do?"
│       │   ├── dependency_graph.json    ← All imports analyzed
│       │   ├── classes.json             ← Class hierarchy
│       │   ├── functions.json           ← All functions
│       │   ├── git_history.json         ← Commit analysis
│       │   ├── metrics.json             ← Code health metrics
│       │   └── overlays/
│       │       ├── security.json        ← Vulnerabilities
│       │       ├── performance.json     ← Bottlenecks
│       │       └── compliance.json      ← Standards violations
│       ├── visualizations/
│       │   ├── dependency-graph.js      ← D3.js force-directed data
│       │   ├── call-graph.js
│       │   ├── timeline-data.js
│       │   ├── author-network.js
│       │   └── ...
│       ├── diagrams/
│       │   ├── class-diagram.mmd        ← Mermaid source
│       │   ├── entity-diagram.mmd
│       │   ├── sequence-diagram.mmd
│       │   └── ...
│       ├── exports/
│       │   ├── dashboard-2026-01-29.png
│       │   ├── dependency-graph-2026-01-29.svg
│       │   └── report-2026-01-29.pdf
│       └── manifest.json               ← Analysis metadata
│
├── .gitignore                       ← INCLUDES .cortex/
└── ...
```

### **Generated Dashboard Files Breakdown:**

#### **index.html (Main Dashboard)**
- Single-page application (SPA)
- Alpine.js reactive framework
- All 5 universal tabs available
- Self-contained (no external CDN)
- ~200KB initial load

**Available Tabs:**
1. **Repository Overview** — Business-language description + tech stack
2. **Dependency Graph** — D3.js interactive network (functions, modules)
3. **Class Diagrams** — Mermaid UML + ER diagrams
4. **Temporal Analysis** — Git timeline + change frequency heatmap
5. **Impact Analysis** — Change propagation + blast radius

**Multi-Dimensional Overlays:**
- 🔴 Security overlay (vulnerabilities, insecure patterns)
- ⚡ Performance overlay (bottlenecks, hotspots)
- ✅ Compliance overlay (if applicable standards detected)

---

## 📦 Multi-Repository Analysis Setup

When analyzing **n repositories**, CORTEX creates:

### **Scenario: Analyzing 3 User Repositories**

```
~/.cortex/                          ← User's CORTEX cache (home directory)
├── cache/
│   ├── github.com/user/project-a/
│   │   ├── lens-dashboard/
│   │   │   ├── index.html
│   │   │   ├── data.json
│   │   │   └── manifest.json
│   │   └── .cortex-meta.yaml
│   │
│   ├── github.com/user/project-b/
│   │   ├── lens-dashboard/
│   │   │   ├── index.html
│   │   │   ├── data.json
│   │   │   └── manifest.json
│   │   └── .cortex-meta.yaml
│   │
│   └── github.com/company/internal-lib/
│       ├── lens-dashboard/
│       │   ├── index.html
│       │   ├── data.json
│       │   └── manifest.json
│       └── .cortex-meta.yaml
│
├── config/
│   ├── cortex-config.yaml           ← User preferences
│   └── themes/
│       └── default.yaml
│
└── logs/
    ├── analysis-2026-01-29.log
    └── errors.log
```

### **CLI Commands for Multi-Repo Analysis:**

```bash
# Analyze local repository (generates in .cortex/lens-dashboard/)
cortex lens analyze /path/to/UserProject_A

# View dashboard locally
cortex lens dashboard serve /path/to/UserProject_A
# Opens: http://localhost:8000

# Analyze remote repository (caches in ~/.cortex/cache/)
cortex lens analyze github.com/user/project-a
cortex lens dashboard serve github.com/user/project-a

# Batch analyze multiple repos
cortex lens batch-analyze \
  /path/to/project-1 \
  /path/to/project-2 \
  github.com/org/project-3

# Export dashboard as artifact
cortex lens dashboard export /path/to/UserProject_A --format pdf
# Output: UserProject_A-dashboard-2026-01-29.pdf
```

---

## 🔄 CORTEX Self-Analysis Structure

CORTEX analyzing itself (meta-analysis):

```
CORTEX/
├── reports/
│   └── lens-dashboard/              ← CORTEX's own dashboard
│       ├── index.html
│       ├── data.json
│       ├── analysis/
│       │   ├── business_language.json    ← "CORTEX is a microservices..."
│       │   ├── dependency_graph.json     ← 26+ orchestrators mapped
│       │   ├── classes.json              ← 140+ orchestrator files
│       │   ├── git_history.json          ← Full commit history
│       │   └── metrics.json              ← System health
│       ├── visualizations/
│       │   └── orchestrator-constellation.js ← CORTEX-specific
│       └── diagrams/
│           ├── brain-architecture.mmd    ← 4-tier brain
│           ├── governance-heatmap.mmd    ← CORE rules status
│           └── call-graph.mmd            ← Orchestrator relationships
│
├── .cortex/                         ← CORTEX can also use local .cortex/
│   └── lens-dashboard/              ← Alternate analysis output
│       └── ...
└── ...
```

**CORTEX-Specific Tabs (8 total instead of 5):**

Tabs 1-5: Universal (same as user repos)

Tabs 6-8: CORTEX Only
- **Tab 6:** Brain Architecture (4-tier visualization)
- **Tab 7:** Governance Compliance (CORE rule heatmap)
- **Tab 8:** Orchestrator Constellation (relationship map)

---

## 📊 Comparison Matrix

| Aspect | CORTEX Repo | User Repo A | User Repo B | User Repo N |
|--------|-------------|------------|------------|-----------|
| **Dashboard Location** | `reports/lens-dashboard/` | `.cortex/lens-dashboard/` | `.cortex/lens-dashboard/` | `.cortex/lens-dashboard/` |
| **Cache Location** | N/A (on-disk in reports/) | `~/.cortex/cache/` | `~/.cortex/cache/` | `~/.cortex/cache/` |
| **Available Tabs** | 8 (universal + CORTEX-specific) | 5 (universal only) | 5 (universal only) | 5 (universal only) |
| **Orchestrator Tab** | ✅ Yes (Tab 8) | ❌ N/A | ❌ N/A | ❌ N/A |
| **Governance Tab** | ✅ Yes (Tab 7) | ❌ N/A | ❌ N/A | ❌ N/A |
| **Brain Architecture Tab** | ✅ Yes (Tab 6) | ❌ N/A | ❌ N/A | ❌ N/A |
| **Analysis Time** | 15-30 sec | 2-10 sec | 2-10 sec | 2-10 sec |
| **Bundle Size** | 1.5MB (full) | 1.5MB (full) | 1.5MB (full) | 1.5MB (full) |
| **Offline Ready** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

---

## 📂 .gitignore Patterns (Updated Phase 14)

```bash
# CORTEX analysis output (never commit)
.cortex/
.cortex-meta.yaml

# User's local CORTEX cache (never commit)
~/.cortex/

# Dashboard exports (optionally committed)
# Leave commented if you want to version exports
# reports/lens-dashboard/*.png
# reports/lens-dashboard/*.pdf

# Build artifacts
__pycache__/
*.pyc
.eggs/
*.egg-info/
```

---

## 🚀 Deployment Implications

### **Docker Image (Phase 14+)**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy entire CORTEX system
COPY cortex/ /app/cortex/
COPY cortex_brain/ /app/cortex_brain/
COPY cortex-lens/ /app/cortex-lens/       ← NEW line for Phase 14

# Copy configuration
COPY requirements.txt docker-compose.yaml ./

# Install dependencies (shared)
RUN pip install -r requirements.txt

# Expose dashboard service
EXPOSE 8000

# Start CORTEX with dashboard
CMD ["python", "-m", "cortex.bootstrap"]
```

### **docker-compose.yaml (Phase 14+)**

```yaml
version: '3.9'

services:
  cortex:
    build: .
    container_name: cortex-main
    ports:
      - "8000:8000"      # Main API
      - "8001:8001"      # Dashboard (cortex-lens)
    volumes:
      - ./cortex:/app/cortex
      - ./cortex_brain:/app/cortex_brain
      - ./cortex-lens:/app/cortex-lens    ← NEW mounting
      - ./reports:/app/reports
      - ./.cortex:/app/.cortex
    environment:
      - CORTEX_ENV=production
      - DASHBOARD_PORT=8001
    depends_on:
      - postgres
      - redis

  # Optional: Separate dashboard container
  lens-dashboard:
    build:
      context: .
      dockerfile: cortex-lens/Dockerfile  ← Optional microservice
    container_name: cortex-lens-dashboard
    ports:
      - "8001:8001"
    volumes:
      - ./cortex:/app/cortex              ← Imports renderers
      - ./cortex-lens:/app/cortex-lens
      - ./reports:/app/reports
    depends_on:
      - cortex                            ← Depends on main API

  postgres:
    image: postgres:15
    # ... config

  redis:
    image: redis:7
    # ... config
```

---

## 🎯 Summary: Folder Logic

```
CORTEX (System)
├── cortex/                  ← Orchestrators, analyzers, renderers
├── cortex_brain/            ← Governance, knowledge, tiers
└── cortex-lens/             ← Dashboard SPA, isolated, user-safe ⭐

User Repository (Project A)
├── src/
├── tests/
├── .cortex/                 ← Generated dashboard (gitignored)
└── reports/                 ← Optional exports

Cache (Home)
└── ~/.cortex/cache/         ← Cached dashboards for multiple repos
    ├── github.com/org/project-a/lens-dashboard/
    ├── github.com/org/project-b/lens-dashboard/
    └── ...
```

This structure ensures:
✅ **Isolation:** Dashboard separate from core system  
✅ **Safety:** Users can't accidentally delete CORTEX logic  
✅ **Scalability:** Works for 1 repo or 1000 repos  
✅ **Clarity:** Clear separation of concerns across 3 folders  

---

**Authority:** CORTEX Development Team  
**Phase:** 14 (LENS Dashboard Implementation)  
**Status:** ✅ Architecture Approved
