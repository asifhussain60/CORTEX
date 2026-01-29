# Quick Tree Reference: Phase 14 Folder Structure

**Purpose:** Quick-glance visual reference for the three-folder CORTEX system  
**Last Updated:** January 29, 2026

---

## 🌳 Complete Tree: CORTEX Repository Root

```
CORTEX/
│
├── cortex/                                    # ✅ ORCHESTRATION CORE
│   ├── orchestrators/                        # 26 orchestrators
│   │   ├── core/                             # 7 core orchestrators
│   │   ├── domain/                           # 6 domain orchestrators
│   │   ├── support/                          # 13 support orchestrators
│   │   │   ├── lens_orchestrator.py          # Phase 7.1
│   │   │   └── lens_visualization_orchestrator.py  # Phase 14 NEW
│   │   └── registry/
│   │       └── __init__.py                   # Canonical OrchestratorRegistry
│   │
│   ├── brain/                                # ✅ CODE INTELLIGENCE
│   │   ├── analysis/
│   │   │   ├── git_history_analyzer.py       # Phase 7.1 LENS
│   │   │   ├── ast_analyzer.py               # Phase 7.1 LENS
│   │   │   └── comment_extractor.py          # Phase 7.1 LENS
│   │   └── core/
│   │       └── governance_registry.py        # Canonical (608 lines)
│   │
│   ├── visualization/                        # ✅ VISUALIZATION ENGINE
│   │   ├── renderers/
│   │   │   ├── d3_renderer.py
│   │   │   ├── mermaid_renderer.py
│   │   │   ├── governance_heatmap.py
│   │   │   └── dependency_graph.py
│   │   │
│   │   ├── formatters/
│   │   │   ├── graph_formatter.py
│   │   │   ├── diagram_formatter.py
│   │   │   └── response_formatter.py
│   │   │
│   │   ├── business_language_generator.py    # Phase 14 NEW
│   │   ├── repository_detector.py            # Phase 14 NEW
│   │   ├── dashboard_configuration.py        # Phase 14 NEW
│   │   ├── output_manager.py                 # Phase 14 NEW
│   │   │
│   │   ├── dashboards/
│   │   │   └── lens/                         # Temporary location
│   │   │       ├── orchestrator.py
│   │   │       └── __init__.py
│   │   │
│   │   ├── templates/
│   │   │   ├── dashboard_base.html
│   │   │   ├── repository_overview.html      # Phase 14 NEW
│   │   │   ├── dependency_graph.html
│   │   │   ├── class_diagram.html
│   │   │   ├── temporal_analysis.html
│   │   │   ├── impact_analysis.html
│   │   │   ├── brain_architecture.html
│   │   │   ├── governance_heatmap.html
│   │   │   └── orchestrator_constellation.html
│   │   │
│   │   └── static/
│   │       ├── vendor/
│   │       │   ├── alpine-3.13.3.min.js      # Phase 14 NEW
│   │       │   ├── d3-7.8.5.min.js           # Phase 14 NEW
│   │       │   ├── mermaid-10.6.1.min.js     # Phase 14 NEW
│   │       │   └── tailwind-3.4.0.min.css    # Phase 14 NEW
│   │       ├── css/
│   │       │   └── dashboard.css
│   │       ├── js/
│   │       │   ├── app.js
│   │       │   └── overlay-system.js         # Phase 14 NEW
│   │       └── assets/
│   │
│   ├── api/
│   │   └── dashboard_routes.py               # Phase 14 NEW
│   │
│   ├── cli/
│   │   ├── main.py
│   │   └── lens_commands.py
│   │       └── dashboard serve               # Phase 14 NEW
│   │
│   ├── wiring/
│   │   └── specifications/
│   │       └── wiring.yaml
│   │
│   └── ... (other concerns)
│
├── cortex_brain/                             # ✅ GOVERNANCE & KNOWLEDGE
│   ├── tier0/
│   │   └── governance/                       # 28 CORE rules
│   │
│   ├── tier1/
│   │   └── acceptance_criteria/
│   │
│   ├── tier2/
│   │   └── response_templates/
│   │
│   └── tier3/
│       ├── knowledge/                        # 35+ YAML best practices
│       │   ├── refactoring/
│       │   ├── testing/
│       │   ├── architecture/
│       │   └── ...
│       └── ...
│
└── cortex-lens/                              # ⭐ PHASE 14 NEW: LENS DASHBOARD
    ├── README.md
    ├── __init__.py
    ├── app.py
    ├── config.py
    │
    ├── backend/
    │   ├── __init__.py
    │   ├── orchestrator.py                   # Routes to cortex/visualization/
    │   ├── cache_manager.py
    │   ├── repository_loader.py
    │   └── routes.py
    │
    ├── frontend/
    │   ├── index.html                        # Alpine.js SPA
    │   ├── css/
    │   │   └── dashboard-ui.css
    │   ├── js/
    │   │   ├── dashboard-app.js
    │   │   ├── tab-controller.js
    │   │   ├── overlay-ui.js
    │   │   └── visualization-bridge.js
    │   └── views/
    │       ├── tab-1-overview.html           # Universal tabs
    │       ├── tab-2-dependencies.html
    │       ├── tab-3-diagrams.html
    │       ├── tab-4-temporal.html
    │       ├── tab-5-impact.html
    │       ├── tab-6-brain.html              # CORTEX-only
    │       ├── tab-7-governance.html         # CORTEX-only
    │       └── tab-8-orchestrators.html      # CORTEX-only
    │
    ├── static/                               # Symlink to cortex/visualization/static/
    │
    ├── tests/
    │   ├── test_dashboard_api.py
    │   ├── test_cache_manager.py
    │   └── test_tab_rendering.py
    │
    ├── docker/
    │   ├── Dockerfile.dashboard
    │   └── docker-compose.lens.yml
    │
    └── docs/
        └── dashboard-guide.md

# ============================================================================

# 🌳 User Repository: With CORTEX Analysis

```
my-awesome-project/
│
├── src/                                      # Your application code
│   ├── app.py
│   ├── models/
│   └── utils/
│
├── tests/
├── docs/
├── README.md
├── requirements.txt
│
└── .cortex/                                  # ⭐ Generated by CORTEX
    └── lens-dashboard/                       # cortex lens analyze .
        ├── index.html                        # Self-contained SPA
        ├── data.json                         # Repository analysis
        ├── manifest.json                     # Tab configuration
        └── assets/                           # Pre-rendered visualizations (optional)
```

**Usage:**
```bash
cd my-awesome-project/
cortex lens analyze .
cortex lens dashboard serve .
# Opens http://localhost:8888
```

---

## 🌳 Remote Repository Cache: Global Analysis Storage

```
~/.cortex/
│
├── cache/
│   ├── owner-1/
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
│   │   └── repo-3/
│   │       └── lens-dashboard/
│   │           └── ...
│   │
│   ├── owner-2/
│   │   └── ...
│   │
│   └── asifhussain/
│       └── CORTEX/
│           └── lens-dashboard/               # Full 8-tab CORTEX analysis
│               ├── index.html
│               ├── data.json
│               └── manifest.json
│
└── config/
    ├── theme.yml
    └── overlay-defaults.yml
```

**Usage:**
```bash
cortex lens analyze https://github.com/owner/repo
cortex lens dashboard serve owner/repo
# Serves from ~/.cortex/cache/owner/repo/lens-dashboard/
```

---

## 🌳 CI/CD Pipeline: Build Artifact Output

```
my-pipeline/
│
├── .github/workflows/
│   └── cortex-lens.yml
│
└── (After build succeeds)
   Runs: cortex lens analyze .
   Runs: cortex lens dashboard generate
   Output to: $CI_ARTIFACTS_DIR/lens-dashboard/
        ├── index.html
        ├── data.json
        └── manifest.json
```

**Available at:** `https://your-ci-platform.com/build-artifacts/cortex-lens/index.html`

---

## 📊 Tab Visibility Matrix

```
REPOSITORY TYPE          │ TABS 1-5 │ TABS 6-8 │ TOTAL TABS
─────────────────────────┼──────────┼──────────┼──────────
Python/Node/Java/Ruby    │    ✅    │    ❌    │    5
(user repos)             │          │          │
─────────────────────────┼──────────┼──────────┼──────────
CORTEX Repository        │    ✅    │    ✅    │    8
─────────────────────────┼──────────┼──────────┼──────────

UNIVERSAL TABS (5):
  ✅ Tab 1: Repository Overview (NEW - business language)
  ✅ Tab 2: Dependency Graph (D3.js force-directed)
  ✅ Tab 3: Class Diagrams (Mermaid UML/ER)
  ✅ Tab 4: Temporal Analysis (Git timeline)
  ✅ Tab 5: Impact Analysis (Change propagation)

CORTEX-SPECIFIC TABS (3):
  ✅ Tab 6: Brain Architecture (4-tier CORTEX brain)
  ✅ Tab 7: Governance Compliance (CORE rules heatmap)
  ✅ Tab 8: Orchestrator Constellation (26 orchestrators)
```

---

## 📦 Bundle Size & Performance

```
INITIAL LOAD (SPA startup):
├── Alpine.js 3.13.3         15 KB ✓ [loaded]
├── Dashboard app JS        160 KB ✓ [loaded]
├── CSS + assets             50 KB ✓ [loaded]
└── Total                   225 KB 📊 Fast

LAZY-LOADED MODULES (per tab):
├── D3.js (Tabs 2, 4, 5)    250 KB [on-demand]
├── Mermaid (Tab 3)         850 KB [on-demand]
└── Total full bundle      1.5 MB (vs 3MB monolithic)

CACHING:
├── Browser cache           ✓ ETags + expires headers
├── Local cache (.cortex/)  ✓ Persistent across sessions
└── CDN-free               ✓ All assets local (air-gapped compatible)
```

---

## 🔄 Three-Folder Communication

```
User Request (cortex-lens/)
         │
         └──→ backend/orchestrator.py
              │
              └──→ cortex/orchestrators/support/
                   LENSVisualizationOrchestrator
                   │
                   ├──→ cortex/brain/analysis/
                   │    (GitHistoryAnalyzer, ASTAnalyzer, CommentExtractor)
                   │
                   ├──→ cortex/visualization/renderers/
                   │    (D3, Mermaid, Governance Heatmap)
                   │
                   └──→ cortex/visualization/formatters/
                        (Graph, Diagram, Response formatters)
                   │
                   └──→ cortex/visualization/output_manager.py
                        (Cache to .cortex/, reports/, ~/.cortex/)
                   │
                   └──→ Returns JSON to cortex-lens/frontend/
                        (Alpine.js renders D3/Mermaid visualizations)
```

---

## ✅ Key Design Principles

✅ **Separation of Concerns:** Three folders, one system  
✅ **Zero External CDN:** All assets bundled locally  
✅ **Offline-First:** Works in air-gapped environments  
✅ **Context-Aware:** Tabs adapt to repository type  
✅ **Extensible:** Multi-dimensional overlays toggle independently  
✅ **Efficient:** Lazy-loading reduces initial bundle size  
✅ **Protected:** Clear folder boundaries prevent accidental deletion  

---

**Version:** Phase 14 Quick Reference  
**Authority:** CORE-038 (File Placement), CORE-030 (Implementation Truth)  
**Last Updated:** January 29, 2026
