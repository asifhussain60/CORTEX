# CORTEX LENS Dashboard Package

**Extracted:** 2026-01-29 from archive/CORTEX-5.0 and current branch  
**Scope:** Multi-tab dashboard with reverse-engineered text, D3.js visualizations, and mermaid diagrams  
**Purpose:** Comprehensive code intelligence and governance visualization system

---

## 📋 Package Contents

### Frontend Assets
- **`frontend/index.html`** - Main dashboard template with multi-tab interface
- **`frontend/js/app.js`** - Dashboard application controller
- **`frontend/js/components/common/tab-switcher.js`** - Tab navigation with URL state persistence
- **`frontend/js/components/brain/brain-map.js`** - Brain Observatory visualization with D3.js
- **`frontend/js/components/neural/neural-pulse.js`** - Neural activity visualization
- **`frontend/js/components/orchestrator/orchestrator-grid.js`** - Orchestrator constellation display
- **`frontend/js/components/temporal/audit-timeline.js`** - Temporal audit trail with D3.js
- **`frontend/js/utils/api-client.js`** - Backend API communication layer
- **`frontend/css/`** - Styling suite:
  - `colors.css` - Brand color palette (CORTEX cyan, green, purple)
  - `animations.css` - Glassmorphism and transition effects
  - `glassmorphism.css` - Modern frosted glass UI components
  - `header.css` - Header and branding styles
  - `sidebar.css` - Navigation sidebar with collapse toggle
  - `tabs.css` - Tab switcher styling (200ms transitions)
  - `responsive.css` - Mobile-first responsive design
  - `tailwind-custom.css` - Custom Tailwind configuration

### LENS Code Intelligence Modules
- **`lens_context_builder.py`** - Aggregates code intelligence from multiple sources:
  - AST analysis (functions, classes, modules)
  - Git history (change patterns, expertise)
  - Code comments (documentation extraction)
  - Relationship traversal (call graphs, dependencies)
  - Builds unified knowledge graph of codebase

- **`knowledge_graph.py`** - Knowledge graph data structure:
  - `KnowledgeGraph` - Graph representation with nodes and edges
  - `GraphNode` - Code entities (functions, classes, files)
  - `GraphEdge` - Relationships (calls, inherits, imports, depends_on)
  - `KnowledgeGraphBuilder` - Multi-source integration orchestrator
  - Query operations for impact analysis

- **`intent_router.py`** - Routes user intent to appropriate handlers:
  - Language parsing (what, why, why now)
  - AST examination
  - Git navigation
  - Holistic synthesis

### Visualization & Formatting
- **`multi_mode_formatter.py`** - Response formatting for multiple output modes:
  - `VisualizationResponseFormatter` - Format for D3.js/Mermaid rendering
  - Chat, CLI, JSON, Markdown formatters
  - Supports graphs, diagrams, structured data

- **`git_history/`** - Git history analysis:
  - Commit pattern extraction
  - Change frequency analysis
  - Author expertise identification
  - Temporal trend analysis

### Backend API
- **`api/main.py`** - FastAPI dashboard endpoints
- **`api/__init__.py`** - API package configuration
- **`compliance.html`** - Governance compliance report template

### Python Launch Scripts
- **`launch.py`** - Dashboard server launcher
- **`governance_heatmap.py`** - Governance rule compliance visualization
- **`serve-cortex-dashboard.py`** - Standalone dashboard server

### AST Intelligence
- **`ast_intelligence/`** - Abstract Syntax Tree analysis package:
  - Function/class extraction
  - Call graph building
  - Dependency detection
  - Complexity assessment

---

## 🎯 Key Features

### 1. **Multi-Tab Dashboard Interface**
- **Tabs:** Overview, Audit Log, Metrics, Settings (per section)
- **Tab State Persistence:** Stored in URL fragment (#tab-name)
- **Smooth Transitions:** 200ms CSS animations
- **Lazy Loading:** Content loaded on tab activation
- **Responsive:** Mobile hamburger menu, tablet optimization, desktop full sidebar

### 2. **LENS Protocol Integration**
The dashboard implements the CORTEX LENS (Language Examination Navigation Synthesis) protocol:
- **L**anguage: Parse user intent from natural language
- **E**xamination: AST analysis of code structure
- **N**avigation: Git history traversal and pattern extraction
- **S**ynthesis: Unified knowledge graph construction

### 3. **Reverse-Engineered Code Intelligence**
- Extracts function signatures, parameters, return types
- Discovers call graphs and dependency relationships
- Identifies architectural layers and patterns
- Generates impact analysis (what changes break this?)
- Surfaces expertise and ownership patterns

### 4. **D3.js Visualizations**
- **Brain Map:** Codebase structure as neural network
- **Audit Timeline:** Temporal commit history visualization
- **Orchestrator Constellation:** Orchestrator relationships as interactive graph
- **Neural Pulse:** Real-time system activity monitoring

### 5. **Governance Compliance**
- Displays TIER 0 governance rule enforcement
- Real-time rule violation detection
- Compliance heatmap showing impact
- Phase lock status and approval gates

---

## 🔧 Architecture

```
Dashboard System
├── Frontend (Browser)
│   ├── HTML5 Structure (Semantic, Accessible)
│   ├── CSS (Glassmorphism + Tailwind)
│   ├── JavaScript Components (Vanilla JS, no framework)
│   └── D3.js Visualizations
├── Backend API (Python/FastAPI)
│   ├── /api/dashboard - Get dashboard data
│   ├── /api/intelligence - LENS context data
│   ├── /api/governance - Compliance status
│   └── /api/export - PDF/CSV reports
└── Intelligence Engine
    ├── AST Analyzer - Code structure
    ├── Git Historian - Change patterns
    ├── Knowledge Graph - Unified context
    ├── Intent Router - Request routing
    └── Response Formatter - Multi-mode output
```

### Data Flow

```
User Request
    ↓
Intent Router (LENS Protocol)
    ↓
Knowledge Graph Builder
    ├→ AST Intelligence (function/class extraction)
    ├→ Git History Analyzer (change patterns)
    ├→ Comment Analyzer (documentation)
    └→ Relationship Traversal (call graphs)
    ↓
Unified Knowledge Graph
    ↓
Response Formatter (D3/Mermaid/JSON)
    ↓
Dashboard Frontend (Visualization)
```

---

## 🚀 Getting Started

### 1. **Install Dependencies**
```bash
pip install fastapi uvicorn
npm install d3@7.8.5 mermaid@10.x
```

### 2. **Start Backend API**
```bash
python launch.py
# or
python serve-cortex-dashboard.py
```

### 3. **Open Dashboard**
```
http://localhost:8000/dashboard
```

### 4. **Navigate Tabs**
- Click tabs to switch views
- URL updates automatically (#tab-name)
- Refresh page → returns to same tab
- Mobile: hamburger menu replaces sidebar

---

## 📊 Understanding the Data

### Knowledge Graph Nodes
```python
GraphNode(
    id="func_auth_user",
    node_type=NodeType.FUNCTION,
    name="auth_user",
    file="src/auth/endpoints.py",
    metadata={
        "complexity": 0.65,
        "change_frequency": 8,
        "expertise_concentration": 0.3,  # 30% owned by 1 person
        "risk_level": "MEDIUM"
    }
)
```

### Knowledge Graph Edges
```python
GraphEdge(
    source="func_auth_user",
    target="func_validate_token",
    edge_type=EdgeType.CALLS,
    metadata={"call_count": 3, "critical": True}
)
```

---

## 🎨 Styling System

### Color Palette (CSS Variables)
```css
--cortex-primary: #0ea5e9     /* Cyan */
--cortex-primary-hover: #0284c7
--cortex-primary-light: #38bdf8
--cortex-primary-dark: #0369a1

--cortex-secondary: #10b981    /* Green */
--cortex-secondary-hover: #059669
--cortex-accent: #a78bfa      /* Purple */
```

### Glassmorphism Effect
```css
backdrop-filter: blur(10px);
background: rgba(30, 41, 59, 0.7);
border: 1px solid rgba(148, 163, 184, 0.2);
```

### Responsive Breakpoints
- **Mobile:** < 640px (hamburger menu, full-width)
- **Tablet:** 640px - 1024px (sidebar collapsed by default)
- **Desktop:** > 1024px (full sidebar, multi-column)

---

## 📡 API Endpoints

### Dashboard Data
```
GET /api/dashboard/summary
→ {
    "phase_progress": 0.85,
    "active_orchestrators": 12,
    "governance_violations": 2,
    "recent_commits": [...]
  }
```

### LENS Intelligence
```
POST /api/intelligence/analyze
Body: {
    "code": "def func(): ...",
    "context": "user_question",
    "branch": "main"
}
→ {
    "ast_findings": {...},
    "git_history": {...},
    "relationships": {...},
    "recommendations": [...]
  }
```

### Governance Compliance
```
GET /api/governance/status
→ {
    "tier0_rules": 29,
    "compliant_rules": 27,
    "violations": [
        {
            "rule_id": "CORE-005",
            "severity": "BLOCKED",
            "files": ["src/file.py"]
        }
    ]
  }
```

---

## 🧠 CORTEX LENS Protocol

The dashboard implements the CORTEX Master Orchestrator's LENS Protocol:

### Stage 1: Intent Comprehension
- Parse natural language request
- Extract intent (implement, analyze, debug, document)
- Identify scope (file, function, module, system)

### Stage 2: Intent Routing
- Determine execution path
- Identify relevant code locations
- Map to appropriate orchestrators

### Stage 3: Knowledge Integration
- Load TIER 0 governance rules
- Build knowledge graph
- Calculate change impact

### Stage 4: Approval Gate
- Present user with findings
- Show risks and challenges
- Request confirmation

---

## 🔍 Example Workflows

### Scenario 1: Reverse-Engineer a Function
```
User: "How does the auth_user function work?"

1. Intent Router: ANALYZE, function scope
2. AST Analyzer: Extract function signature, parameters, body
3. Git Historian: Find last 10 commits touching this file
4. Relationship Traversal: Find all callers and callees
5. Knowledge Graph: Build function-centric subgraph
6. Response: Display code, call graph, change history
```

### Scenario 2: Assess Change Impact
```
User: "What breaks if I rename process_order?"

1. Intent Router: IMPACT_ANALYSIS, symbol scope
2. AST Analyzer: Find all references to process_order
3. Relationship Traversal: Build call graph
4. Dependency Analysis: Find cascading changes
5. Governance Check: Identify TIER 0 violations
6. Response: List affected code, risk level, recommendations
```

### Scenario 3: Governance Dashboard
```
User: Views admin dashboard

1. Load TIER 0 rules (29 SKULL rules)
2. Scan codebase for violations
3. Identify files with issues
4. Calculate compliance score
5. Display heatmap and enforcement status
6. Highlight blocking violations
```

---

## 🛠️ Integration Guide

### Adding New D3 Visualization
1. Create file in `frontend/js/components/{domain}/`
2. Extend `BaseComponent` class
3. Implement `render()` method with D3.js code
4. Add CSS file in `frontend/css/`
5. Link in `index.html` and `app.js`

### Adding New LENS Intelligence Source
1. Create analyzer in `cortex/brain/core/intelligence/`
2. Extend `IntelligenceEngine` base class
3. Implement `analyze()` method
4. Add to `KnowledgeGraphBuilder._integrate_*` method
5. Regenerate knowledge graph on next run

### Adding Governance Rule
1. Add rule to `cortex/core/governance/core-rules.yaml`
2. Create validator in `governance/validators/`
3. Register in `GovernanceEngine`
4. Add UI to compliance heatmap

---

## 📈 Performance Considerations

- **Dashboard Load:** < 3 seconds on 3G
- **Chart Render:** < 200ms (D3.js with canvas fallback)
- **Search:** < 300ms for 10,000 symbols
- **Knowledge Graph Build:** ~2 minutes for 100k LOC codebase
- **Tab Switch:** 200ms smooth transition
- **Backend API:** Sub-200ms response time

### Optimization Tips
- Use lazy-loading for large datasets
- Canvas rendering for 5000+ nodes
- Memoize graph traversal queries
- Incremental knowledge graph updates
- Service Worker caching for static assets

---

## 🧪 Testing

### Frontend Tests
```bash
# Selenium tests for tab switching
pytest tests/unit/dashboard/components/test_tab_switcher.py

# Dashboard integration tests
pytest tests/unit/dashboard/test_phase_15_all_acs.py
```

### Backend Tests
```bash
# Knowledge graph builder tests
pytest tests/integration/test_cortex_lens_knowledge_graph.py

# LENS protocol tests
pytest tests/unit/core/intent/test_lens_protocol.py
```

---

## 📚 References

### CORTEX System Prompt
See `.github/prompts/CORTEX.prompt.md` for Master Orchestrator guidelines

### Governance Rules
See `cortex/core/governance/core-rules.yaml` for TIER 0 requirements

### Phase Documentation
- **Phase 7.1:** LENS Protocol Formalization
- **Phase 10:** LENS Remote Intelligence
- **Phase 15:** Dashboard Enhancement (16 ACs)

---

## 🤝 Contributing

When extending the dashboard:

1. **Follow CORTEX Governance**
   - CORE-008: TDD (tests before code)
   - CORE-011: Type hints on all functions
   - CORE-012: Google-style docstrings
   - CORE-029: Response headers

2. **Maintain Performance**
   - Keep D3.js operations < 200ms
   - Lazy-load large datasets
   - Memoize expensive calculations

3. **Ensure Accessibility**
   - WCAG 2.1 AA compliance
   - Keyboard navigation support
   - Semantic HTML structure

4. **Document Integration Points**
   - Update this README
   - Add integration tests
   - Document API contracts

---

## 📞 Support

For issues or questions:
1. Check dashboard logs: `python serve-cortex-dashboard.py --debug`
2. Verify TIER 0 governance compliance
3. Review git history for recent changes
4. Consult CORTEX LENS protocol documentation

---

**Status:** ✅ Complete  
**Last Updated:** 2026-01-29  
**Version:** 5.0 → Archive Extract  
**Maintainer:** CORTEX Master Orchestrator
