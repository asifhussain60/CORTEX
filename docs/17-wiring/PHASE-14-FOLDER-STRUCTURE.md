# Phase 14: Folder Structure with CORTEX LENS Dashboard

**Version:** 1.0  
**Created:** January 29, 2026  
**Authority:** CORE-038 (File Placement Policy)  
**Scope:** CORTEX repository + User development repositories

---

## 📊 Three-Folder CORTEX System

The CORTEX system now spans three root-level folders, each with distinct responsibilities:

```
/Users/asifhussain/PROJECTS/CORTEX/
│
├── cortex/                          # CORE ORCHESTRATION SYSTEM
│   ├── __init__.py
│   ├── bootstrap.py
│   ├── orchestrators/               # 26 orchestrators (7 core, 6 domain, 13 support)
│   │   ├── core/
│   │   │   ├── master_orchestrator.py
│   │   │   ├── intent_router.py
│   │   │   ├── tdd_orchestrator.py
│   │   │   └── ...
│   │   ├── domain/
│   │   ├── support/
│   │   │   ├── lens_orchestrator.py          # LENS Intelligence (Phase 7.1)
│   │   │   ├── lens_visualization_orchestrator.py  # NEW (Phase 14)
│   │   │   └── ...
│   │   └── registry/
│   │       └── __init__.py                    # OrchestratorRegistry (canonical)
│   │
│   ├── brain/                       # CODE INTELLIGENCE & ANALYSIS
│   │   ├── analysis/
│   │   │   ├── git_history_analyzer.py        # LENS: Git history analysis
│   │   │   ├── ast_analyzer.py                # LENS: Code structure analysis
│   │   │   ├── comment_extractor.py           # LENS: Documentation extraction
│   │   │   └── ...
│   │   ├── core/
│   │   │   ├── governance_registry.py         # CORE rules (608 lines, canonical)
│   │   │   ├── knowledge_repository.py
│   │   │   └── ...
│   │   └── ...
│   │
│   ├── visualization/               # DASHBOARD & VISUALIZATION ENGINE
│   │   ├── __init__.py
│   │   ├── renderers/
│   │   │   ├── d3_renderer.py
│   │   │   ├── mermaid_renderer.py
│   │   │   ├── governance_heatmap.py
│   │   │   ├── dependency_graph.py
│   │   │   └── ...
│   │   │
│   │   ├── formatters/
│   │   │   ├── graph_formatter.py
│   │   │   ├── diagram_formatter.py
│   │   │   └── response_formatter.py
│   │   │
│   │   ├── business_language_generator.py     # NEW (Phase 14): Reverse-engineer intent
│   │   ├── repository_detector.py             # NEW (Phase 14): CORTEX vs external repo detection
│   │   ├── dashboard_configuration.py         # NEW (Phase 14): Context-aware tab selection
│   │   ├── output_manager.py                  # NEW (Phase 14): Dashboard file management
│   │   │
│   │   ├── dashboards/
│   │   │   ├── __init__.py
│   │   │   └── lens/                          # LENS DASHBOARD (Phase 14 - Initially here for prototyping)
│   │   │       ├── orchestrator.py            # Routes to cortex-lens after stabilization
│   │   │       └── __init__.py
│   │   │
│   │   ├── templates/
│   │   │   ├── dashboard_base.html
│   │   │   ├── repository_overview.html       # NEW (Phase 14)
│   │   │   ├── dependency_graph.html
│   │   │   ├── class_diagram.html
│   │   │   ├── temporal_analysis.html
│   │   │   ├── impact_analysis.html
│   │   │   ├── brain_architecture.html        # CORTEX-only
│   │   │   ├── governance_heatmap.html        # CORTEX-only
│   │   │   └── orchestrator_constellation.html # CORTEX-only
│   │   │
│   │   └── static/
│   │       ├── vendor/                         # NEW (Phase 14): Bundled JS frameworks
│   │       │   ├── alpine-3.13.3.min.js       # 15KB reactive SPA framework
│   │       │   ├── d3-7.8.5.min.js            # 250KB (lazy-loaded)
│   │       │   ├── mermaid-10.6.1.min.js      # 850KB (lazy-loaded)
│   │       │   └── tailwind-3.4.0.min.css     # Styling framework
│   │       ├── css/
│   │       │   ├── dashboard.css
│   │       │   └── overlays.css                # NEW (Phase 14): Overlay system
│   │       ├── js/
│   │       │   ├── app.js                      # Alpine.js application
│   │       │   ├── tab-manager.js
│   │       │   ├── overlay-system.js           # NEW (Phase 14): Multi-dimensional overlays
│   │       │   ├── data-loader.js
│   │       │   └── interactions.js
│   │       └── assets/
│   │           ├── icons/
│   │           └── images/
│   │
│   ├── api/
│   │   ├── dashboard_routes.py                 # NEW (Phase 14): FastAPI endpoints
│   │   └── ...
│   │
│   ├── cli/
│   │   ├── main.py
│   │   ├── lens_commands.py                    # cortex lens [command]
│   │   │   ├── analyze                         # cortex lens analyze <file>
│   │   │   ├── history                         # cortex lens history <file>
│   │   │   ├── complexity                      # cortex lens complexity <file>
│   │   │   ├── todos                           # cortex lens todos <file>
│   │   │   └── dashboard serve                 # NEW (Phase 14): cortex lens dashboard serve
│   │   └── ...
│   │
│   ├── wiring/
│   │   └── specifications/
│   │       └── wiring.yaml                     # Git-backed orchestrator registry (SSOT)
│   │
│   ├── config/
│   ├── infrastructure/
│   ├── governance/
│   └── ... (other concerns)
│
├── cortex_brain/                    # GOVERNANCE & KNOWLEDGE TIER SYSTEM
│   ├── __init__.py
│   ├── tier0/
│   │   └── governance/              # Immutable rules (28 CORE rules)
│   │       ├── __init__.py
│   │       ├── core_registry.py
│   │       └── ...
│   │
│   ├── tier1/
│   │   └── acceptance_criteria/     # Phase validation specs
│   │
│   ├── tier2/
│   │   └── response_templates/      # Behavioral boundaries
│   │
│   └── tier3/
│       ├── knowledge/               # 35+ YAML best practices
│       │   ├── refactoring/
│       │   ├── testing/
│       │   ├── architecture/
│       │   └── ...
│       └── ...
│
└── cortex-lens/                     # ⭐ NEW: LENS DASHBOARD (PHASE 14)
    ├── README.md                    # Dashboard-specific documentation
    ├── __init__.py
    ├── app.py                       # Flask/FastAPI app server
    ├── config.py                    # Dashboard configuration
    ├── requirements-dashboard.txt   # Dashboard-specific deps (if any)
    │
    ├── backend/
    │   ├── __init__.py
    │   ├── orchestrator.py          # Routes requests to cortex/visualization/
    │   ├── cache_manager.py         # Manages dashboard output caching
    │   ├── repository_loader.py     # Load & analyze repositories
    │   └── routes.py                # API endpoints
    │
    ├── frontend/
    │   ├── index.html               # SPA entry point (Alpine.js)
    │   ├── css/
    │   │   └── dashboard-ui.css
    │   ├── js/
    │   │   ├── dashboard-app.js     # Main Alpine app
    │   │   ├── tab-controller.js
    │   │   ├── overlay-ui.js        # UI for overlays
    │   │   └── visualization-bridge.js
    │   └── views/
    │       ├── tab-1-overview.html
    │       ├── tab-2-dependencies.html
    │       ├── tab-3-diagrams.html
    │       ├── tab-4-temporal.html
    │       ├── tab-5-impact.html
    │       ├── tab-6-brain.html             # CORTEX-only
    │       ├── tab-7-governance.html        # CORTEX-only
    │       └── tab-8-orchestrators.html     # CORTEX-only
    │
    ├── static/
    │   └── (symlink to cortex/visualization/static/)
    │
    ├── tests/
    │   ├── test_dashboard_api.py
    │   ├── test_cache_manager.py
    │   └── test_tab_rendering.py
    │
    ├── docker/
    │   ├── Dockerfile.dashboard     # Optional: separate dashboard container
    │   └── docker-compose.lens.yml
    │
    └── docs/
        └── dashboard-guide.md       # Dashboard-specific documentation

```

---

## 🔄 Interaction Flow: How Three Folders Communicate

```
┌─────────────────────────────────────────────────────────────────┐
│                      cortex-lens/ (User Facing)                  │
│                   [SPA + Dashboard Routes]                        │
│                                                                   │
│  Frontend (Alpine.js)     ──┐                                    │
│  - Tab selection           │                                    │
│  - Overlay toggles         │                                    │
│  - Visualization display   │────→ backend/routes.py             │
│                            │       (orchestrator.py calls)      │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 │ HTTP API Calls
                 │
┌────────────────▼───────────────────────────────────────────────┐
│              cortex/api/ (API Layer)                             │
│        [FastAPI dashboard_routes.py]                             │
│                                                                  │
│  GET /dashboard/analyze?repo=<path>                             │
│  GET /dashboard/tab/<tab-id>?repo=<path>                        │
│  GET /dashboard/overlay/<overlay-type>?repo=<path>              │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 │ Routes calls to orchestrator
                 │
┌────────────────▼────────────────────────────────────────────┐
│    cortex/orchestrators/support/ (Orchestration Layer)       │
│  [LENSVisualizationOrchestrator - NEW Phase 14]              │
│                                                              │
│  1. Receives analysis request                               │
│  2. Calls LENSOrchestrator (Phase 7.1)                      │
│     ├─ GitHistoryAnalyzer                                   │
│     ├─ ASTAnalyzer                                          │
│     └─ CommentExtractor                                     │
│  3. Calls visualization renderers                           │
└────────────────┬────────────────────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
┌─────▼──┐  ┌────▼────┐  ┌──▼──────────┐
│ cortex/│  │ cortex/ │  │  cortex/    │
│ brain/ │  │visualiz-│  │ visualization
│analyzer│  │ ation/  │  │/formatters/ │
│        │  │renderers│  │             │
└────────┘  └─────────┘  └─────────────┘
      │          │              │
      └──────────┼──────────────┘
                 │
         Returns formatted data
                 │
         (D3 nodes/edges, Mermaid syntax,
          governance heatmap, etc.)
                 │
      ┌──────────▼──────────┐
      │  cortex/visualization
      │  /output_manager.py │
      │                     │
      │ Caches to:          │
      │ - .cortex/lens-     │
      │   dashboard/        │
      │ - reports/lens-     │
      │   dashboard/        │
      │ - ~/.cortex/cache/  │
      └──────────┬──────────┘
                 │
         Returns to API
                 │
      ┌──────────▼──────────┐
      │ cortex-lens/        │
      │ frontend/           │
      │                     │
      │ Alpine.js renders   │
      │ D3.js visualizations│
      │ Mermaid diagrams    │
      └─────────────────────┘
```

---

## 📁 User Repository Folder Structure (Any Language/Framework)

When users analyze their repositories with CORTEX LENS, the dashboard generates output in:

### **Option 1: User Repository (WITH .cortex/)**

```
my-awesome-project/
├── src/
│   ├── app.py
│   ├── models/
│   └── utils/
├── tests/
├── docs/
├── README.md
├── requirements.txt
│
└── .cortex/                         # ⭐ NEW: CORTEX analysis cache
    └── lens-dashboard/              # Generated by: cortex lens analyze .
        ├── index.html               # Self-contained SPA
        ├── data.json                # Repository analysis metadata
        ├── manifest.json            # Tab configuration (what's CORTEX vs not)
        └── assets/
            └── (D3/Mermaid generated SVGs if pre-rendered)
```

**How to use:**
```bash
cd my-awesome-project/
cortex lens analyze .
cortex lens dashboard serve .  # Serves .cortex/lens-dashboard/index.html
```

---

### **Option 2: Remote Repository (Cached Locally)**

```
~/.cortex/
├── cache/
│   ├── owner/
│   │   ├── repo-1/
│   │   │   └── lens-dashboard/
│   │   │       ├── index.html
│   │   │       ├── data.json
│   │   │       └── manifest.json
│   │   │
│   │   ├── repo-2/
│   │   │   └── lens-dashboard/
│   │   │       └── ...
│   │   │
│   │   └── cortex/                  # CORTEX self-analysis
│   │       └── lens-dashboard/
│   │           ├── index.html       # Full 8-tab version
│   │           ├── data.json        # Includes orchestrators, brain, etc.
│   │           └── manifest.json    # Shows all CORTEX-specific tabs
│   │
│   └── config/                      # Dashboard preferences
│       ├── theme.yml
│       └── overlay-defaults.yml
│
└── .gitignore                       # ~/.cortex/ is typically gitignored
```

**How to use:**
```bash
cortex lens analyze https://github.com/user/repo
cortex lens dashboard serve user/repo  # Serves from ~/.cortex/cache/
```

---

### **Option 3: CI/CD Pipeline Integration**

```
my-pipeline/
├── .github/workflows/
│   └── cortex-lens.yml
│
└── (runs after build succeeds)
   cortex lens analyze .
   cortex lens dashboard generate
   # Outputs to: $CI_ARTIFACTS_DIR/lens-dashboard/
```

---

## 🎯 Tab Availability: CORTEX vs User Repos

### **User Repository (ANY Language/Framework)**

**Always available (5 tabs):**
```
Tab 1: 📋 Repository Overview     [Business language, tech stack, activity]
Tab 2: 📊 Dependency Graph        [D3.js force-directed network]
Tab 3: 📐 Class Diagrams          [Mermaid UML, ER, interfaces]
Tab 4: ⏱️  Temporal Analysis       [Git timeline, change frequency]
Tab 5: 💥 Impact Analysis         [Blast radius, change propagation]
```

**Tabs hidden:**
```
❌ Tab 6: Brain Architecture
❌ Tab 7: Governance Compliance
❌ Tab 8: Orchestrator Constellation
```

---

### **CORTEX Repository (ONLY)**

**All 8 tabs available:**
```
Tab 1: 📋 Repository Overview       [Reverse-engineered business intent]
Tab 2: 📊 Dependency Graph          [Orchestrator dependencies, call graphs]
Tab 3: 📐 Class Diagrams            [Orchestrator inheritance, interfaces]
Tab 4: ⏱️  Temporal Analysis         [Development velocity, focus areas]
Tab 5: 💥 Impact Analysis           [Orchestrator impact chain]
Tab 6: 🧠 Brain Architecture        [4-tier CORTEX brain (Tier 0-3)]
Tab 7: 🛡️  Governance Compliance    [CORE rule violations, audit trail]
Tab 8: 🌟 Orchestrator Constellation [26 orchestrators, wiring map, data flow]
```

---

## 📦 Multi-Dimensional Overlay System (Phase 14.1)

**Available on ALL tabs for ALL repositories:**

```
┌─ Security Overlay (P0/P1/P2 vulnerabilities)
├─ Performance Overlay (Bottlenecks, complexity hotspots)
└─ Compliance Overlay (CORE rules for CORTEX, linting for others)

Each toggle independently on/off:
  ☑️ Security  ☑️ Performance  ☑️ Compliance  ☐ Custom
```

---

## 🚀 Deployment Topology

### **Development (Single Container)**

```
docker-compose up -d
├── cortex (Python 3.11 + FastAPI)
│   ├── cortex/
│   ├── cortex_brain/
│   ├── cortex-lens/
│   └── Runs on :8000
└── Dashboard accessible at http://localhost:8000/dashboard/
```

### **Production (Optional Separation)**

```
Option 1: Monolithic
└── cortex-main:latest [cortex + cortex-lens together]

Option 2: Microservices (Future)
├── cortex-orchestrator:latest [core system]
├── cortex-lens-dashboard:latest [separate service]
└── cortex-insights-api:latest [analysis APIs]
```

---

## ✅ Summary: Folder Responsibility Matrix

| Folder | Responsibility | Isolation Level | Scalability |
|--------|-----------------|-----------------|-------------|
| **cortex/** | Orchestration, analysis, core APIs | Highest | 🟢 Excellent |
| **cortex_brain/** | Governance rules, knowledge, tiers | Highest | 🟢 Excellent |
| **cortex-lens/** | Dashboard UI, user interaction | Highest | 🟢 Excellent |
| **.cortex/** (user repos) | Per-repo analysis cache | Highest | 🟢 Excellent |
| **~/.cortex/cache/** | Global cache for remote analysis | Highest | 🟢 Excellent |

---

## 🔐 Accidental Deletion Protection

With three separate root folders, deletion protection strategies:

```bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q '^cortex-lens/'; then
  echo "⚠️  Modifying cortex-lens/ - dashboard visualization system"
  echo "Review carefully: dashboard functionality depends on these files"
fi

# CODEOWNERS
cortex-lens/* @asifhussain
cortex/* @asifhussain
cortex_brain/* @asifhussain
```

---

**Authority:** CORE-038 (File Placement Policy), CORE-030 (Implementation Truth)  
**Version:** Phase 14 Architecture  
**Last Updated:** January 29, 2026
