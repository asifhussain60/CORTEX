# CORTEX LENS Dashboard - Integration Guide

**Status:** Complete & Ready for Integration  
**Extracted Components:** 36 files  
**Source Branches:** archive/CORTEX-5.0 + current (archive/CORTEX-4.0)  
**Date:** 2026-01-29

---

## 🎯 Quick Start Integration

### Step 1: Copy Dashboard to Your Project
```bash
# Copy entire dashboard package to your project
cp -r _workspaces/dashboard /path/to/your/project/cortex/brain/

# Or integrate specific components as needed
```

### Step 2: Install Dependencies
```bash
# Python dependencies
pip install fastapi uvicorn
pip install d3py mermaid-py  # Optional visualization libs

# Frontend dependencies
npm install d3@7.8.5 mermaid@10.x chart.js@4.4.0
```

### Step 3: Start Dashboard
```bash
# Option A: Use existing launch script
python launch.py

# Option B: Use standalone server
python serve-cortex-dashboard.py

# Option C: Run with FastAPI
uvicorn api.main:app --reload --port 8000
```

### Step 4: Open in Browser
```
http://localhost:8000
# or
http://localhost:8000/dashboard
```

---

## 📦 Component Breakdown

### Frontend Components

#### 1. **Multi-Tab Dashboard Interface** (`frontend/index.html`)
**Purpose:** Main page shell with sidebar navigation and tab switcher  
**Dependencies:** Tailwind CSS, D3.js, Chart.js  
**Key Features:**
- Responsive sidebar (collapsible on mobile)
- Multi-section navigation (Brain Observatory, Temporal Cortex, Orchestrators, Plan Hub, Admin)
- Tab-based content switching with URL persistence
- Glassmorphism design system

**Integration:**
```html
<!-- Include in your Flask/FastAPI template -->
{% include "dashboard/frontend/index.html" %}

<!-- Or iframe -->
<iframe src="/dashboard" width="100%" height="100%"></iframe>
```

#### 2. **Tab Switcher** (`frontend/js/components/common/tab-switcher.js`)
**Purpose:** Handles tab navigation with URL state management  
**Key Methods:**
```javascript
// Initialize tab switcher
initializeTabSwitcher();

// Listen for tab changes
document.addEventListener('tab-changed', (e) => {
  console.log('Switched to:', e.detail.tab);
});

// Programmatically switch tab
switchTab('metrics');
```

**Features:**
- Hash-based URL navigation (#overview, #audit-log, etc.)
- Smooth 200ms transitions
- Lazy content loading
- Keyboard navigation support (arrow keys)

#### 3. **D3.js Visualizations**

**Brain Map** (`frontend/js/components/brain/brain-map.js`)
- Renders codebase as neural network
- Node: Functions/classes, Edge: Call relationships
- Interactive: Hover for details, click to drill down
- Zoom/pan supported

```javascript
// Initialize brain map
const brainMap = new BrainMap({
  container: '#brain-visualization',
  data: knowledgeGraph,
  onNodeClick: (node) => { /* Show details */ }
});
```

**Audit Timeline** (`frontend/js/components/temporal/audit-timeline.js`)
- Temporal visualization of commits/changes
- Time-series analysis of codebase evolution
- Change frequency heatmap

```javascript
// Initialize timeline
const timeline = new AuditTimeline({
  container: '#timeline-visualization',
  data: gitHistory,
  timeRange: [startDate, endDate]
});
```

**Orchestrator Grid** (`frontend/js/components/orchestrator/orchestrator-grid.js`)
- Displays orchestrator constellation
- Shows orchestrator relationships and status
- Real-time status updates

```javascript
// Initialize orchestrator grid
const grid = new OrchestratorGrid({
  container: '#orchestrators',
  data: orchestratorData,
  onOrchestratorClick: (id) => { /* Show details */ }
});
```

### Backend Components

#### 1. **Knowledge Graph Builder** (`knowledge_graph.py`)
**Purpose:** Central intelligence aggregator  
**Key Classes:**
```python
# Knowledge graph representation
graph = KnowledgeGraph()
graph.add_node(GraphNode(...))
graph.add_edge(GraphEdge(...))

# Build from multiple sources
builder = KnowledgeGraphBuilder(workspace_root="/path/to/code")
graph = builder.build()

# Query the graph
functions = graph.query_nodes_by_type(NodeType.FUNCTION)
impact = graph.get_change_impact("func_id")
```

#### 2. **LENS Context Builder** (`lens_context_builder.py`)
**Purpose:** Reverse-engineer codebase context  
**Features:**
- AST analysis → functions, classes, complexity
- Git history → change patterns, expertise
- Code comments → documentation extraction
- Relationships → call graphs, dependencies

```python
from lens_context_builder import LENSContextBuilder

builder = LENSContextBuilder()
context = builder.build_context(
    code_path="/path/to/file.py",
    git_history=True,
    include_comments=True
)

# Access findings
print(context.functions)
print(context.relationships)
print(context.documentation)
```

#### 3. **Intent Router** (`intent_router.py`)
**Purpose:** Route user requests to appropriate orchestrators  
**Protocol:** LENS (Language, Examination, Navigation, Synthesis)

```python
from intent_router import IntentRouter

router = IntentRouter()
route = router.route_intent(
    user_query="How does auth_user work?",
    context=knowledge_graph
)

# Returns:
# {
#   "operation": "ANALYZE",
#   "target": "function",
#   "scope": "auth_user",
#   "handler": "DocumentationOrchestrator",
#   "confidence": 0.95
# }
```

#### 4. **API Endpoints** (`api/main.py`)
**Purpose:** REST API for dashboard and tools

```python
# Get dashboard summary
GET /api/dashboard/summary
→ { phase_progress, active_orchestrators, violations, ... }

# Analyze code with LENS
POST /api/intelligence/analyze
Body: { code, context, branch }
→ { ast_findings, git_history, relationships, recommendations }

# Get governance status
GET /api/governance/status
→ { tier0_rules, compliant_rules, violations }

# Export reports
GET /api/export/pdf
GET /api/export/csv
```

#### 5. **Response Formatter** (`multi_mode_formatter.py`)
**Purpose:** Format responses for multiple output modes

```python
from multi_mode_formatter import VisualizationResponseFormatter

# Format for D3.js visualization
viz_response = VisualizationResponseFormatter.format(
    content="Call graph analysis",
    data={
        "nodes": [...],
        "links": [...]
    }
)
# Returns: { type, content, data, metadata }
```

---

## 🔌 Integration Points

### 1. FastAPI Backend
```python
# In your main application
from fastapi import FastAPI
from cortex.brain.dashboard.api.main import router as dashboard_router

app = FastAPI()
app.include_router(dashboard_router, prefix="/api")
```

### 2. Flask Backend
```python
# In your Flask app
from cortex.brain.dashboard.api.main import get_dashboard_data

@app.route('/dashboard/api/summary')
def dashboard_summary():
    return get_dashboard_data()
```

### 3. Knowledge Graph Integration
```python
# Integrate with your IDE/tool
from cortex.brain.core.knowledge.knowledge_graph import KnowledgeGraphBuilder

# Build once, reuse everywhere
builder = KnowledgeGraphBuilder()
global_graph = builder.build()

# Access from any component
affected_code = global_graph.get_change_impact("modified_file.py")
```

### 4. CI/CD Pipeline
```yaml
# Add to your GitHub Actions
- name: Generate Dashboard Data
  run: |
    python -m cortex.brain.dashboard.launch \
      --output ./dashboard-data.json \
      --include-governance \
      --include-metrics
      
- name: Deploy Dashboard
  run: cp dashboard-data.json ./build/
```

---

## 🎨 Customization

### Adding New Tabs
```javascript
// In frontend/js/app.js

// Register new tab
registerTab({
  id: 'custom-tab',
  label: 'My Analysis',
  icon: '<svg>...</svg>',
  content: () => customComponentElement,
  lazy: true  // Load only when clicked
});
```

### Adding New Visualizations
1. Create component in `frontend/js/components/{domain}/`
2. Extend BaseComponent class:
```javascript
class MyVisualization extends BaseComponent {
  render() {
    // Your D3.js code here
    return this.container;
  }
  
  update(data) {
    // Handle data updates
  }
}
```
3. Register in `frontend/js/app.js`
4. Add CSS styling

### Customizing LENS Protocol
```python
# Create custom intent handlers
from cortex.brain.core.intent.intent_router import IntentHandler

class CustomIntentHandler(IntentHandler):
    def can_handle(self, intent):
        return intent.operation == "CUSTOM"
    
    def handle(self, intent, context):
        # Your custom logic
        return result

# Register handler
router.register_handler(CustomIntentHandler())
```

---

## 📊 Data Schema Reference

### Knowledge Graph Node
```python
{
  "id": "func_auth_user",
  "node_type": "function",
  "name": "auth_user",
  "file": "src/auth/endpoints.py",
  "metadata": {
    "line_number": 42,
    "complexity": 0.65,
    "change_frequency": 8,
    "expertise_concentration": 0.3,
    "risk_level": "MEDIUM",
    "last_modified": "2026-01-28",
    "author": "asif"
  }
}
```

### Dashboard API Response
```json
{
  "phase": {
    "current": 15,
    "progress": 0.85,
    "status": "IN_PROGRESS"
  },
  "orchestrators": {
    "total": 12,
    "active": 10,
    "failed": 0
  },
  "governance": {
    "violations": 2,
    "tier0_rules": 29,
    "compliance_score": 0.93
  },
  "recent_activity": [
    {
      "timestamp": "2026-01-29T10:30:00Z",
      "type": "commit",
      "description": "feat(AC-LENS): Add remote intelligence"
    }
  ]
}
```

---

## 🧪 Testing Your Integration

### Unit Tests
```bash
# Test dashboard components
pytest tests/unit/dashboard/

# Test LENS protocol
pytest tests/unit/core/intent/test_lens_protocol.py

# Test knowledge graph
pytest tests/integration/test_cortex_lens_knowledge_graph.py
```

### Integration Tests
```bash
# Full end-to-end test
pytest tests/integration/test_dashboard_e2e.py

# API endpoint tests
pytest tests/unit/dashboard/api/test_endpoints.py
```

### Manual Testing
1. Open http://localhost:8000/dashboard
2. Click through tabs (verify URL updates)
3. Check sidebar navigation
4. Click on visualizations (verify interactions)
5. Check mobile view (hamburger menu)

---

## 🔒 Governance Compliance

### TIER 0 Rules Applied
- **CORE-001:** Incremental execution (dashboard lazy-loads content)
- **CORE-005:** No hardcoded paths (uses path_resolver)
- **CORE-008:** TDD (100% test coverage for dashboard ACs)
- **CORE-011:** Type hints (all Python functions annotated)
- **CORE-012:** Docstrings (Google format on all public APIs)
- **CORE-029:** Response headers (mandatory on all API responses)

### Governance Dashboard Features
- Real-time rule violation detection
- Compliance score calculation
- Impact analysis for rule changes
- Approval gate enforcement

---

## 🐛 Troubleshooting

### Dashboard Won't Load
1. **Check server running:** `curl http://localhost:8000/health`
2. **Check ports:** `netstat -an | grep 8000`
3. **Check logs:** `python serve-cortex-dashboard.py --debug`

### D3 Visualizations Not Rendering
1. **Check D3 loaded:** `console.log(d3)` in browser console
2. **Check data:** Verify JSON structure in network tab
3. **Check SVG:** Right-click → Inspect element

### LENS Context Builder Errors
1. **Workspace not found:** Verify `workspace_root` parameter
2. **Git errors:** Ensure `.git` folder exists
3. **AST errors:** Check Python syntax in target files

### Performance Issues
1. **Slow graph building:** Use `--cache` flag for incremental builds
2. **Slow visualization:** Reduce node count or use canvas mode
3. **Slow API:** Check database indexes, enable query caching

---

## 🚀 Advanced Configuration

### Environment Variables
```bash
export CORTEX_DASHBOARD_PORT=8000
export CORTEX_WORKSPACE_ROOT=/path/to/workspace
export CORTEX_CACHE_DIR=/tmp/cortex-cache
export CORTEX_LOG_LEVEL=INFO
export CORTEX_ENABLE_PROFILING=false
```

### Configuration File (`dashboard.yaml`)
```yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: 4

knowledge_graph:
  cache_enabled: true
  cache_ttl: 3600
  incremental_updates: true

visualizations:
  max_nodes: 5000
  use_canvas: true
  animation_duration: 200

governance:
  tier0_enforcement: true
  compliance_check_interval: 60
```

---

## 📚 Further Reading

- [CORTEX.prompt.md](.github/prompts/CORTEX.prompt.md) - Master Orchestrator guidelines
- [LENS Protocol Spec](cortex/brain/tier0/lens_protocol.md) - Full protocol details
- [Governance Rules](cortex/core/governance/core-rules.yaml) - All 29 SKULL rules
- [Phase 15 Dashboard](docs/PHASE-15-DASHBOARD-ENHANCEMENT.md) - Complete implementation

---

## 🤝 Support & Contributions

### Reporting Issues
1. Collect error logs: `python serve-cortex-dashboard.py --debug > logs.txt`
2. Reproduce in isolation: Share minimal example
3. Check git history: `git log --oneline -- _workspaces/dashboard`

### Contributing Changes
1. Create feature branch: `git checkout -b feature/my-feature`
2. Follow TIER 0 governance (TDD, type hints, docstrings)
3. Add tests: `pytest tests/unit/dashboard/`
4. Submit PR with governance checklist

---

## 📄 License & Attribution

© 2025-2026 Asif Hussain. All rights reserved.

**Extracted Components:**
- Dashboard UI from archive/CORTEX-5.0 (2026-01-24)
- LENS Intelligence from archive/CORTEX-4.0 (current branch)
- Knowledge Graph from cortex/brain/core/ (multiple sources)
- Visualization Framework from D3.js ecosystem

---

**Ready to Integrate!** 🎉

This package is production-ready with:
- ✅ 36 integrated files
- ✅ 4 complete orchestrators
- ✅ Multi-source intelligence (AST + Git + Comments + Relationships)
- ✅ D3.js and Mermaid visualizations
- ✅ Full governance compliance
- ✅ Comprehensive documentation

Start with the Quick Start Integration guide above!
