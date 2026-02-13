# PHASE 14: LENS Dashboard - Quick Reference
**Status:** ⚠️ SUPERSEDED | **See:** [PHASE-14-V2-QUICK-REFERENCE.md](PHASE-14-V2-QUICK-REFERENCE.md)

---

> **⚠️ THIS DOCUMENT IS SUPERSEDED**
> 
> Phase 14 has been revised to address implementation issues.
> Please use the new plan documents:
> - **Plan:** `PHASE-14-LENS-DASHBOARD-V2.yaml`
> - **Quick Ref:** `PHASE-14-V2-QUICK-REFERENCE.md`
>
> Key changes in v2.0:
> - Static HTML + JSON instead of FastAPI API
> - Dark glassmorphism theme from `_workspaces/dashboard`
> - CORTEX logo hero section (300x300)
> - All 8 tabs properly configured
> - Simplified architecture

---

## ~~🎯 What We're Building~~ (SUPERSEDED)

A **comprehensive visual intelligence dashboard** for code repositories with:

1. **NEW Tab 1: Repository Overview** (Business Language)
   - Auto-generated "What does this repo do?" description
   - Technology stack detection
   - Architecture pattern recognition
   - Key features in plain English

2. **Adaptive Multi-Tab Interface** (Context-Aware)
   
   **UNIVERSAL Dashboard (5 tabs - ANY repository):**
   - Tab 1: Repository Overview (business language)
   - Tab 2: Dependency Graph (D3.js force-directed)
   - Tab 3: Class Diagrams (Mermaid UML + ERD)
   - Tab 4: Temporal Analysis (Git timeline)
   - Tab 5: Impact Analysis (change propagation)
   
   **CORTEX Extended Dashboard (8 tabs - CORTEX only):**
   - Universal tabs 1-5 PLUS:
   - Tab 6: Brain Architecture (CORTEX-specific)
   - Tab 7: Governance Compliance (CORTEX-specific)
   - Tab 8: Orchestrator Constellation (CORTEX-specific)

3. **New D3.js Visualizations**
   - Function call graphs
   - Module import dependencies
   - Change frequency heatmaps
   - Developer collaboration networks
   - Complexity scatter plots

4. **New Mermaid Diagrams**
   - Entity-Relationship Diagrams (database models)
   - State Machine Diagrams (workflows)
   - Sequence Diagrams (API interactions)
   - Architecture Diagrams (system components)

---

## 📁 Where Dashboards Live

| Context | Output Location | Git Tracked? |
|---------|----------------|--------------|
| **Any Repository** | `<repo>/.cortex/lens-dashboard/` | ❌ No (gitignored) |
| **CORTEX Self-Analysis** | `reports/lens-dashboard/` | ✅ Yes |
| **Remote Repo Analysis** | `~/.cortex/cache/<owner>/<repo>/` | ❌ No |
| **CI/CD Artifacts** | `$CI_ARTIFACTS_DIR/lens-dashboard/` | ❌ No |

---

## 🏗️ New Components Created

### Python Backend
```
cortex/
├── orchestrators/support/
│   └── lens_visualization_orchestrator.py  ← NEW (extends LENSOrchestrator)
├── visualization/                          ← NEW PACKAGE
│   ├── __init__.py
│   ├── business_language_generator.py      ← AST → Business Language
│   ├── output_manager.py                   ← Dashboard location routing
│   ├── repository_detector.py              ← Detect CORTEX vs external ⭐ NEW
│   ├── dashboard_configuration.py          ← Context-aware tabs ⭐ NEW
│   ├── renderers/
│   │   ├── d3_renderer.py
│   │   ├── mermaid_renderer.py
│   │   ├── dependency_graph.py             ← Call graph + import graph
│   │   ├── timeline_renderer.py
│   │   ├── complexity_renderer.py          ← Scatter plots
│   │   ├── author_network.py               ← Collaboration network
│   │   └── governance_heatmap.py
│   ├── formatters/
│   │   ├── graph_formatter.py              ← D3 data format
│   │   ├── diagram_formatter.py            ← Mermaid syntax
│   │   └── response_formatter.py
│   ├── templates/                          ← Jinja2 HTML
│   │   ├── dashboard_base.html
│   │   ├── repository_overview.html        ← Tab 1 (UNIVERSAL)
│   │   ├── dependency_graph.html           ← Tab 2 (UNIVERSAL)
│   │   ├── class_diagrams.html             ← Tab 3 (UNIVERSAL)
│   │   ├── temporal_analysis.html          ← Tab 4 (UNIVERSAL)
│   │   ├── impact_analysis.html            ← Tab 5 (UNIVERSAL)
│   │   ├── brain_architecture.html         ← Tab 6 (CORTEX ONLY) ⭐
│   │   ├── governance_heatmap.html         ← Tab 7 (CORTEX ONLY) ⭐
│   │   └── orchestrator_constellation.html ← Tab 8 (CORTEX ONLY) ⭐
│   └── static/
│       ├── css/
│       │   └── cortex-design-system.css    ← Glassmorphism extracted
│       └── js/
│           ├── dependency-graph.js         ← D3.js
│           ├── temporal-timeline.js
│           ├── complexity-scatter.js
│           └── author-network.js
└── api/
    └── dashboard_routes.py                 ← NEW FastAPI routes
```

---

## 🔬 Business Language Generator Algorithm

**Input:** LENS Context (AST + Git + Comments)  
**Output:** Human-readable repository description

### Steps:

1. **AST Extraction**
   - Functions, classes, modules
   - API endpoints, database models
   - Function purposes from docstrings

2. **Git Analysis**
   - Commit patterns → Project maturity
   - Change frequency → Active areas
   - Authors → Key contributors

3. **Technology Detection**
   - Imports → Frameworks used
   - Config files → Database, deployment tools

4. **Pattern Recognition**
   - Directory structure → Architecture style
   - Class inheritance → Design patterns

5. **Business Language Mapping**
   ```python
   class User → "User Management System"
   def authenticate → "User Authentication"
   @app.post("/orders") → "Order Processing API"
   ```

6. **Confidence Scoring**
   - High: Direct evidence (docstrings, explicit patterns)
   - Medium: Inferred patterns
   - Low: Guessed based on structure

### Example Output:

```markdown
## What This Repository Does
This is a microservices-based orchestration system that provides 
AI-powered development workflow automation. It uses Python FastAPI 
for backend services and follows Domain-Driven Design (DDD) with 
23 orchestrators coordinating development tasks.

## Key Features
- Intent Classification via NLP-powered router
- Test-Driven Development enforcement
- Code Intelligence via LENS analyzers
- Governance rule validation (38 CORE rules)
```

---

## 🎨 Enhanced Tab Structure

### Tab 1: Repository Overview (NEW - UNIVERSAL)
- **Content:** Business-language description
- **Visualizations:** Technology badges, architecture diagram
- **Data Sources:** AST, Git, Comments

### Tab 2: Dependency Graph (NEW - UNIVERSAL)
- **Content:** Function and module relationships
- **Visualizations:** D3.js force-directed network
- **Interactions:** Click nodes, zoom, filter

### Tab 3: Class Diagrams (UNIVERSAL)
- **Content:** UML class diagrams + ERD + interfaces
- **Visualizations:** Mermaid diagrams
- **Data Sources:** AST analysis

### Tab 4: Temporal Analysis (UNIVERSAL)
- **Content:** Git history timeline + change heatmap
- **Visualizations:** D3.js timeline, heatmap
- **Data Sources:** Git history analyzer

### Tab 5: Impact Analysis (NEW - UNIVERSAL)
- **Content:** Change impact prediction
- **Visualizations:** Blast radius, dependency impact
- **Data Sources:** AST + Git analysis

### Tab 6: Brain Architecture (CORTEX ONLY)
- **Content:** 4-tier brain system
- **Visualizations:** Tier status cards
- **Data Sources:** Governance registry
- **Shown When:** `cortex_brain/` directory exists

### Tab 7: Governance Compliance (CORTEX ONLY)
- **Content:** CORE rule compliance status
- **Visualizations:** Heatmap showing violations
- **Data Sources:** Governance registry
- **Shown When:** CORTEX repository detected

### Tab 8: Orchestrator Constellation (CORTEX ONLY)
- **Content:** Orchestrator relationships
- **Visualizations:** Network graph
- **Data Sources:** Orchestrator wiring
- **Shown When:** `cortex/wiring/specifications/wiring.yaml` exists

---

## 🚀 CLI Commands

```bash
# Generate dashboard for current repository (auto-detects type)
cortex lens dashboard generate

# Generate for external repository (5 tabs)
cortex lens dashboard generate --repo=/path/to/flask-app
# Output: 🔍 Repository type: External (5 tabs)

# Generate for CORTEX repository (8 tabs)
cortex lens dashboard generate --repo=/path/to/CORTEX
# Output: 🔍 Repository type: CORTEX (8 tabs: 5 universal + 3 CORTEX-specific)

# Generate for remote GitHub repository (auto-detects)
cortex lens dashboard generate --remote=owner/repo

# Manual tab selection (override auto-detection)
cortex lens dashboard generate --tabs=overview,dependency,temporal

# Serve dashboard locally (with hot reload)
cortex lens dashboard serve --port=8080

# Clean old dashboards (older than 30 days)
cortex lens dashboard clean --older-than=30d
```

**Auto-Detection Example:**

```bash
$ cortex lens dashboard generate --repo=/path/to/external-project
🔍 Analyzing repository...
📊 Repository type: External (5 tabs)
✅ Tab 1: Repository Overview
✅ Tab 2: Dependency Graph
✅ Tab 3: Class Diagrams
✅ Tab 4: Temporal Analysis
✅ Tab 5: Impact Analysis
✅ Generated: /path/to/external-project/.cortex/lens-dashboard/index.html

$ cortex lens dashboard generate
🔍 Analyzing repository...
📊 Repository type: CORTEX (8 tabs: 5 universal + 3 CORTEX-specific)
✅ Tab 1: Repository Overview
✅ Tab 2: Dependency Graph
✅ Tab 3: Class Diagrams
✅ Tab 4: Temporal Analysis
✅ Tab 5: Impact Analysis
✅ Tab 6: Brain Architecture (CORTEX)
✅ Tab 7: Governance Compliance (CORTEX)
✅ Tab 8: Orchestrator Constellation (CORTEX)
✅ Generated: reports/lens-dashboard/index.html
```

---

## 📊 API Endpoints

```bash
# Get repository overview (Tab 1)
GET /api/lens/dashboard/overview?repo=/path/to/repo

# Get dependency graph data (Tab 3)
GET /api/lens/dashboard/dependency-graph?type=call_graph

# Get class diagram (Tab 4)
GET /api/lens/dashboard/class-diagram/{module}

# Get temporal analysis (Tab 5)
GET /api/lens/dashboard/temporal-analysis?days=90

# Get governance heatmap (Tab 6)
GET /api/lens/dashboard/governance-heatmap

# Get impact analysis (Tab 8)
GET /api/lens/dashboard/impact-analysis/{file_path}

# Generate full dashboard (async)
POST /api/lens/dashboard/generate
{
  "repo_path": "/path/to/repo",
  "tabs": ["all"]  # or specific tabs
}

# Check generation status
GET /api/lens/dashboard/status/{job_id}
```

---

## 🔧 Integration with Existing CORTEX

### Extends LENSOrchestrator (Phase 7.1)

```python
from cortex.orchestrators.support.lens_visualization_orchestrator import (
    LENSVisualizationOrchestrator
)

# Create orchestrator (inherits all LENSOrchestrator methods)
visualizer = LENSVisualizationOrchestrator(repo_path=Path("/project"))

# Generate complete dashboard
visualizer.generate_dashboard(output_path=Path("reports/lens-dashboard"))

# Generate specific tabs
overview = visualizer.generate_repository_overview()
dep_graph = visualizer.generate_dependency_graph(visualization_type="call_graph")
class_diagram = visualizer.generate_class_diagram(modules=["cortex.brain"])
```

### Uses Existing LENS Analyzers

- **GitHistoryAnalyzer** → Temporal analysis, author networks
- **ASTAnalyzer** → Dependency graphs, class diagrams, business language
- **CommentExtractor** → Repository overview, feature detection

---

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| **Dashboard Generation Time** | < 30 seconds (500-file repo) |
| **Test Coverage** | 100% |
| **D3.js Graph Performance** | Handle 1000+ nodes |
| **User Adoption** | 50+ dashboards in first month |
| **User Satisfaction** | 95%+ |
| **Bug Rate** | < 5 bugs per 100 dashboards |

---

## 🗓️ Implementation Timeline

| Phase | Tasks | Duration |
|-------|-------|----------|
| **Phase 1: Core Infrastructure** | Output manager, business language generator, orchestrator | 4 days |
| **Phase 2: D3.js Visualizations** | Dependency graph, timeline, complexity, author network | 4 days |
| **Phase 3: Mermaid Diagrams** | ERD, state machines, sequence diagrams | 3 days |
| **Phase 4: Frontend Integration** | Templates, CSS, API routes, CLI | 3 days |
| **Phase 5: Testing & Docs** | Integration tests, documentation | 2 days |
| **Total** | | **16 days** |

---

## ✅ Acceptance Criteria

### Functional
- [ ] All tabs render correctly (5 universal + 3 CORTEX-specific)
- [ ] Tab 1 generates business-language descriptions
- [ ] Repository detection works (CORTEX vs external)
- [ ] External repos show 5 tabs only (no CORTEX-specific)
- [ ] CORTEX repo shows 8 tabs
- [ ] D3.js visualizations are interactive (click, zoom, filter)
- [ ] Mermaid diagrams have valid syntax
- [ ] Dashboard generation completes in < 30 seconds
- [ ] Output locations follow specification (.cortex/lens-dashboard/)

### Quality
- [ ] 100% test coverage for Python code
- [ ] CORE-008: Tests exist for all modules
- [ ] CORE-011: All functions have type hints
- [ ] CORE-012: All functions have docstrings
- [ ] CORE-038: All files in subfolders (no root-level files)
- [ ] CORE-040: Documentation follows lifecycle

### Performance
- [ ] Dashboard generation < 30s for 500-file repo
- [ ] D3.js graphs handle 1000+ nodes smoothly
- [ ] Memory usage < 500MB during generation

### User Experience
- [ ] CLI commands are intuitive
- [ ] Error messages are helpful
- [ ] Documentation is comprehensive
- [ ] Dashboard is mobile-responsive

---

## 🔗 Related Documents

- **Full Implementation Plan:** `PHASE-14-LENS-DASHBOARD-IMPLEMENTATION.yaml`
- **Legacy Dashboard Extraction:** `_workspaces/dashboard/`
- **LENS Intelligence (Phase 7.1):** `docs/phases/phase-7.1-lens-intelligence.md`
- **CORTEX Prompt:** `.github/prompts/CORTEX.prompt.md`

---

## 🚨 Key Decisions

1. **Tab 1 is NEW** - Business language generation is a core innovation
2. **Adaptive Dashboard** - 5 universal tabs, +3 CORTEX-specific tabs ⭐ NEW
3. **Repository Detection** - Auto-detect CORTEX vs external repos ⭐ NEW
4. **Output Location** - `.cortex/lens-dashboard/` for per-repo dashboards
5. **Tab Renumbering** - Universal tabs 1-5, CORTEX tabs 6-8
6. **Extends LENSOrchestrator** - Reuses existing LENS analyzers
7. **Glassmorphism CSS** - Extracted as CORTEX design system
8. **Mermaid Only** - Remove graphviz dependency from legacy code
9. **FastAPI + Jinja2** - Server-side rendering for initial load, JavaScript for interactions

---

**Status:** READY FOR APPROVAL  
**Next Step:** Review plan → Get user approval → Begin Task 001
