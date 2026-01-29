# CORTEX Visualization Package

**Version:** 1.0.0  
**Phase:** 14 - LENS Dashboard Implementation  
**Status:** In Development

---

## Overview

The `cortex.visualization` package provides visual intelligence dashboards for code repositories, converting LENS analysis data into interactive web-based visualizations.

## Key Features

### 1. Adaptive Dashboard Configuration
- **Universal Tabs (5):** Applicable to ANY repository
- **CORTEX-Specific Tabs (3):** Only shown for CORTEX repository
- Auto-detects repository type via markers

### 2. Business Language Generation
- Converts AST/Git/Comments → Human-readable descriptions
- Generates "What does this repo do?" content automatically
- Confidence scoring based on evidence quality

### 3. Interactive Visualizations
- **D3.js:** Dependency graphs, timelines, complexity scatter plots
- **Mermaid:** UML diagrams, ERD, state machines, sequence diagrams

## Package Structure

```
cortex/visualization/
├── __init__.py
├── repository_detector.py          # Detect CORTEX vs external repos
├── dashboard_configuration.py      # Context-aware tab selection
├── business_language_generator.py  # AST → Business language
├── output_manager.py               # Dashboard location routing
├── renderers/
│   ├── d3_renderer.py
│   ├── mermaid_renderer.py
│   ├── dependency_graph.py
│   ├── timeline_renderer.py
│   ├── complexity_renderer.py
│   ├── author_network.py
│   └── governance_heatmap.py
├── formatters/
│   ├── graph_formatter.py
│   ├── diagram_formatter.py
│   └── response_formatter.py
├── templates/                      # Jinja2 HTML
│   ├── dashboard_base.html
│   ├── repository_overview.html
│   └── ...
└── static/
    ├── css/
    └── js/
```

## Usage

```python
from cortex.visualization.repository_detector import is_cortex_repository
from cortex.visualization.dashboard_configuration import DashboardConfiguration

# Detect repository type
if is_cortex_repository(Path("/project")):
    print("CORTEX repository - 8 tabs")
else:
    print("External repository - 5 tabs")

# Get applicable tabs
config = DashboardConfiguration()
tabs = config.get_tabs_for_repo(Path("/project"))
```

## Dashboard Tabs

### Universal (ALL repositories)
1. **Repository Overview** - Business language description
2. **Dependency Graph** - Call graph + import graph
3. **Class Diagrams** - UML, ERD, interfaces
4. **Temporal Analysis** - Git timeline, change heatmap
5. **Impact Analysis** - Change propagation

### CORTEX-Specific (CORTEX repository only)
6. **Brain Architecture** - 4-tier brain system
7. **Governance Compliance** - CORE rule heatmap
8. **Orchestrator Constellation** - Orchestrator wiring

## Output Locations

| Context | Path |
|---------|------|
| **External Repo** | `<repo>/.cortex/lens-dashboard/` |
| **CORTEX Repo** | `reports/lens-dashboard/` |
| **Remote Repo** | `~/.cortex/cache/<owner>/<repo>/` |

## Development

### Running Tests

```bash
pytest tests/visualization/ -v --cov=cortex.visualization
```

### Implementation Status

- [ ] Task 001: Package structure (✅ DONE)
- [ ] Task 002a: Repository detector
- [ ] Task 002b: Dashboard configuration
- [ ] Task 002c: Output manager
- [ ] Task 003: Business language generator
- [ ] Task 004: LENS visualization orchestrator
- [ ] Tasks 005-011: Renderers
- [ ] Tasks 012-015: Templates, API, CLI

## Authority

- **CORE-008:** TDD - Tests before implementation
- **CORE-011:** Type hints mandatory
- **CORE-012:** Google-style docstrings
- **CORE-038:** All files in subfolders

## Documentation

Phase 14 (LENS Dashboard) has been superseded by Phase 10 (LENS Remote Intelligence).
For visualization documentation, see `docs/` folder.
