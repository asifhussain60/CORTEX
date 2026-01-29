# LENS Dashboard - Overview

**Phase:** 14 - Visual Intelligence  
**Status:** IN_PROGRESS (75% Complete)  
**Author:** Asif Hussain (asifhussain60@gmail.com)

---

## 🎯 What is LENS Dashboard?

LENS Dashboard is a **self-contained, interactive Single Page Application (SPA)** that visualizes repository intelligence through multiple dimensions. It integrates Phase 7.1 LENS analyzers (GitHistoryAnalyzer, ASTAnalyzer, CommentExtractor) with rich D3.js and Mermaid.js visualizations.

### Key Features

- **🌐 Universal Tabs (5)** - Work with any repository
- **🧠 CORTEX-Specific Tabs (3)** - Deep CORTEX integration
- **📊 Multi-Dimensional Overlays** - Security, Performance, Compliance
- **🔌 Self-Contained** - Zero external CDN dependencies
- **⚡ Reactive UI** - Alpine.js for state management
- **🎨 Modern Design** - Tailwind CSS styling

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LENS Dashboard SPA                        │
│  (Alpine.js + D3.js + Mermaid.js + Tailwind CSS)            │
└───────────────────────┬─────────────────────────────────────┘
                        │
            ┌───────────▼───────────┐
            │  LENSVisualization    │
            │    Orchestrator       │
            └───────────┬───────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │   Git   │    │   AST   │    │ Comment │
   │ History │    │Analyzer │    │Extractor│
   │Analyzer │    │         │    │         │
   └─────────┘    └─────────┘    └─────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
            ┌───────────▼───────────┐
            │    Repository Code    │
            └───────────────────────┘
```

---

## 📁 Components

### Core Modules

| Module | Purpose | Lines | Tests |
|--------|---------|-------|-------|
| `repository_detector.py` | Detects CORTEX vs external repos | 150 | 12 |
| `dashboard_configuration.py` | Tab management | 120 | 12 |
| `output_manager.py` | Output routing | 180 | 12 |
| `business_language_generator.py` | Natural language descriptions | 230 | 15 |

### Renderers

| Renderer | Visualization Type | Lines | Tests |
|----------|-------------------|-------|-------|
| `d3_call_graph_renderer.py` | Function call graphs | 250 | 12 |
| `d3_import_graph_renderer.py` | Module dependency graphs | 185 | 6 |
| `d3_git_timeline_renderer.py` | Temporal commit visualization | 318 | 11 |
| `d3_author_network_renderer.py` | Collaboration networks | 295 | 17 |
| `mermaid_class_diagram_generator.py` | UML class diagrams | 295 | 20 |
| `mermaid_sequence_diagram_generator.py` | UML sequence diagrams | 230 | 22 |

### Integration

| Component | Purpose | Lines | Tests |
|-----------|---------|-------|-------|
| `lens_visualization_orchestrator.py` | Main coordinator | 384 | - |
| `dashboard_routes.py` | FastAPI REST API | 300+ | 12 |
| `lens_dashboard.py` | CLI commands | 250 | 13 |
| HTML Templates | Dashboard UI | - | 20 |

---

## 🎨 Dashboard Tabs

### Universal Tabs (All Repositories)

1. **📋 Repository Overview**
   - Business language description
   - Key features and capabilities
   - Technology stack detection
   - Architecture patterns

2. **🔗 Dependency Graph**
   - D3.js call graph visualization
   - Import/module dependency analysis
   - Circular dependency detection
   - External vs internal modules

3. **📐 Class Diagram**
   - Mermaid UML class diagrams
   - Inheritance relationships
   - Method and attribute visibility
   - Interface implementations

4. **⏱️ Git Timeline**
   - D3.js temporal commit visualization
   - Commit categorization (feat/fix/docs/refactor)
   - Impact assessment (insertions/deletions)
   - Author activity patterns

5. **👥 Author Network**
   - D3.js collaboration graph
   - Shared file detection
   - Node sizing by contribution
   - Collaboration strength

### CORTEX-Specific Tabs (CORTEX Only)

6. **🧠 Brain Architecture**
   - Tier 0-3 structure visualization
   - Governance registry heatmap
   - Knowledge repository explorer

7. **📊 Governance Heatmap**
   - CORE rule compliance matrix
   - File-level policy adherence
   - Violation hotspots

8. **🎼 Orchestrator Constellation**
   - Wiring.yaml visualization
   - Orchestrator dependencies
   - Intent routing paths

---

## 🔧 Multi-Dimensional Overlays

### Security Overlay
- **High Risk:** Red badges on vulnerable patterns
- **Medium Risk:** Orange badges on warning conditions
- **Low Risk:** Yellow badges on informational items
- **Indicators:** SQL injection, XSS, hardcoded secrets

### Performance Overlay
- **Purple badges** on performance-critical code
- **Indicators:** N+1 queries, inefficient loops, large data structures
- **Metrics:** Time complexity, space complexity

### Compliance Overlay
- **Green badges** on policy-compliant code
- **Indicators:** License compliance, data privacy, accessibility
- **Metrics:** GDPR compliance, security standards

---

## 🚀 Quick Start

### Generate Dashboard (CLI)

```bash
# Generate for current repository
cortex dashboard generate .

# Generate for specific repository
cortex dashboard generate /path/to/repo

# Generate with custom output
cortex dashboard generate /path/to/repo --output /custom/path

# Serve dashboard locally
cortex dashboard serve /path/to/repo --port 8080
```

### Generate Dashboard (API)

```bash
# Start FastAPI server
uvicorn cortex.visualization.api.dashboard_routes:app --reload

# Generate dashboard via REST API
curl -X POST http://localhost:8000/api/lens/dashboard/generate \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/repo"}'

# List generated dashboards
curl http://localhost:8000/api/lens/dashboard/list

# Get dashboard metadata
curl http://localhost:8000/api/lens/dashboard/my-repo/metadata
```

### Generate Dashboard (Python)

```python
from pathlib import Path
from cortex.orchestrators.support.lens_visualization_orchestrator import (
    LENSVisualizationOrchestrator,
)

# Initialize orchestrator
orchestrator = LENSVisualizationOrchestrator(
    repo_path=Path("/path/to/repo")
)

# Generate dashboard
result = orchestrator.generate_dashboard()

print(f"Dashboard generated at: {result.output_path}")
print(f"Tabs available: {len(result.tabs)}")
```

---

## 📦 Output Structure

### External Repositories
```
/path/to/external-repo/
├── .cortex-lens/              # Auto-created
│   └── dashboard/
│       ├── index.html         # Main dashboard
│       ├── static/
│       │   ├── vendor/        # Bundled dependencies
│       │   └── data/          # JSON data files
│       └── tabs/              # Tab-specific assets
└── .gitignore                 # Auto-updated
```

### CORTEX Repository
```
/path/to/CORTEX/
├── reports/
│   └── lens-dashboard/        # CORTEX dashboards
│       ├── index.html
│       ├── static/
│       └── tabs/
```

---

## 🎯 Use Cases

### For External Repositories
- **Onboarding:** Quick project understanding
- **Code Review:** Architectural overview
- **Refactoring:** Identify dependencies
- **Documentation:** Visual architecture docs
- **Team Collaboration:** Visualize contributions

### For CORTEX Repository
- **Brain Visualization:** Explore tier structure
- **Governance Audit:** CORE rule compliance
- **Orchestrator Discovery:** Understand wiring
- **Development:** Feature impact analysis
- **Documentation:** Living architecture docs

---

## 📊 Technology Stack

| Technology | Version | Size | Purpose |
|------------|---------|------|---------|
| **Alpine.js** | 3.13.3 | 15KB | Reactive UI |
| **D3.js** | v7.8.5 | 250KB | Visualizations |
| **Mermaid.js** | v10.6.1 | 850KB | Diagrams |
| **Tailwind CSS** | 3.4.0 | ~100KB | Styling |
| **FastAPI** | Latest | - | REST API |
| **Click** | Latest | - | CLI |
| **Jinja2** | Latest | - | Templates |

**Total SPA Size:** ~1.2MB (gzipped: ~400KB)

---

## 🔐 Security & Privacy

### Data Handling
- ✅ **Local Processing:** All analysis done locally
- ✅ **No Telemetry:** Zero data transmission
- ✅ **Self-Contained:** No external CDN calls
- ✅ **Git-Ignored:** Dashboard output excluded from commits

### File Permissions
- Dashboard output: `755` (user read/write/execute)
- Static assets: `644` (user read/write)
- `.gitignore` entry: Auto-created for external repos

---

## 🎓 Learn More

- **[Getting Started](./01-getting-started.md)** - Installation and first dashboard
- **[API Reference](./02-api-reference.md)** - REST API endpoints
- **[CLI Reference](./03-cli-reference.md)** - Command-line usage
- **[Renderer Guide](./04-renderer-guide.md)** - Custom visualizations
- **[Template Customization](./05-template-customization.md)** - UI modifications
- **[Architecture Deep Dive](./06-architecture.md)** - Technical details

---

## 📈 Roadmap

### Phase 14.1 (Current - 75% Complete)
- ✅ Foundation components (Tasks 001-006)
- ✅ Visualization renderers (Tasks 007-010)
- ✅ UI & Integration (Tasks 011-014)
- 🚧 Documentation (Task 015)
- 🚧 SPA bundling & optimization (Tasks 016-018)

### Phase 14.2 (Future)
- CORTEX-specific tabs implementation
- Advanced overlay logic
- Real-time dashboard updates
- Dashboard theming system
- Export to PDF/PNG

---

## 🤝 Contributing

See **[10-contributing](../10-contributing/)** for development guidelines.

### Adding Custom Renderers
```python
from cortex.visualization.renderers.base_renderer import BaseRenderer

class MyCustomRenderer(BaseRenderer):
    def render(self, data: dict) -> dict:
        # Your visualization logic
        pass
```

### Adding Custom Tabs
```yaml
# dashboard_configuration.py
tabs:
  - id: my_custom_tab
    name: "My Custom Tab"
    template: "my_custom_tab.html"
    applicability: "universal"  # or "cortex_only"
```

---

**Generated by CORTEX LENS Dashboard v1.0.0**
