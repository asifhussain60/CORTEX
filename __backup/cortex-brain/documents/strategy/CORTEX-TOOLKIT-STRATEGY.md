# CORTEX TOOLKIT - Static HTML View Generation & Visualization Infrastructure

**Version:** 1.0.0  
**Created:** 2026-01-12  
**Component of:** Phase 1.5 Enhancement (CORTEX LENS & Onboarding)  
**Purpose:** Expose all CORTEX LENS discovery outputs as interactive static HTML dashboards with glassmorphism design, modern tab systems, and D3.js visualizations

---

## 🎯 Vision

**CORTEX TOOLKIT** is the **visualization and MCP exposure layer** for CORTEX LENS outputs. It transforms raw knowledge graphs, analysis results, and audit logs into:

1. **Static HTML Dashboards** - Glassmorphism-themed, self-contained viewers
2. **Multi-Tab Interfaces** - Progressive disclosure with keyboard navigation
3. **Interactive D3.js Visualizations** - Brain architecture, tier relationships, knowledge graphs
4. **Mermaid Diagrams** - Dependency flows, state transitions, class hierarchies
5. **MCP Tool Exposure** - All generators callable by other orchestrators

**Key Principle:** Light, portable, portable outputs that require zero dependencies. All dashboards are self-contained HTML files with embedded CSS/JS.

---

## 📊 Component Architecture

### Layer 1: View Generators (AC-TOOLKIT-001 to 004)

| AC-ID | Component | Purpose | Input | Output |
|-------|-----------|---------|-------|--------|
| **AC-TOOLKIT-001** | Epic Plan Viewer Generator | Generate interactive epic progress dashboards | plan-viewer-data.json, progress-tracker.json | cortex-plan-viewer.html |
| **AC-TOOLKIT-002** | Knowledge Graph Visualizer | Render knowledge graphs as D3.js force-directed diagrams | knowledge-graph.yaml (tier1) | knowledge-graph-viz.html |
| **AC-TOOLKIT-003** | Architecture Diagram Generator | Multi-tier brain architecture with glassmorphism + D3.js animations | tier0/governance/, tier1/state/, tier2/practices/, tier3/learned | architecture-brain.html |
| **AC-TOOLKIT-004** | Audit Log HTML Exporter | Timeline viewer with filtering, event details, correlation chains | audit-logs/*.jsonl | audit-log-viewer.html |

### Layer 2: Design System (AC-TOOLKIT-005 to 006)

| AC-ID | Component | Purpose |
|-------|-----------|---------|
| **AC-TOOLKIT-005** | Glassmorphism Compliance Engine | Validate all HTML views meet design standard (backdrop-filter, rgba, animations) |
| **AC-TOOLKIT-006** | Modern Tab System (Keyboard + Accessibility) | Reusable tabbed interface with ARIA, keyboard nav (arrows/home/end), state persistence |

### Layer 3: Diagram Integration (AC-TOOLKIT-007)

| AC-ID | Component | Purpose |
|-------|-----------|---------|
| **AC-TOOLKIT-007** | Mermaid Diagram Engine | Embed dependency flows, state machines, class diagrams in all dashboard types |

### Layer 4: MCP Exposure & Automation (AC-TOOLKIT-008)

| AC-ID | Component | Purpose |
|-------|-----------|---------|
| **AC-TOOLKIT-008** | CORTEX TOOLKIT MCP Server | Expose all 7 generators as MCP tools callable by Planning v5, Investigation, Onboarding |

---

## 🔧 AC-ID Specifications

### AC-TOOLKIT-001: Epic Plan Viewer Generator

**What it does:** Generates cortex-plan-viewer.html from master-plan.yaml and progress-tracker.json

**Inputs:**
- `cortex-brain/cx6-plan/master-plan.yaml` - Full plan with phases, ACs, timelines
- `cortex-brain/tier1/tracking/progress-tracker.json` - Real-time completion status
- `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` - AC titles and metadata

**Outputs:**
- `cortex-brain/cx6-plan/viewer/cortex-plan-viewer.html` - Self-contained dashboard (350KB)
  - Glassmorphism gradient backgrounds
  - Real-time progress bars
  - Phase cards with metrics
  - Hero section with overall status
  - Metrics sidebar with health score
  - Responsive grid layout

**Acceptance Criteria:**
- ✅ HTML file <500KB (embedded styles/scripts)
- ✅ Loads JSON data via fetch() every 5 seconds
- ✅ Progress bars animate smoothly (CSS transitions)
- ✅ Mobile responsive (320px-1440px+)
- ✅ WCAG AA compliant (7:1 contrast, keyboard nav)
- ✅ D3.js chart rendering (status distribution, phase trend)
- ✅ Zero runtime errors (graceful degradation if JSON unavailable)

**Data Flow:**
```
master-plan.yaml → MetadataParser
progress-tracker.json → StatusParser
AC-INDEX.yaml → TitleLookup

ParsedData → HTMLViewerGenerator.generate_epic_viewer()
↓
ViewerConfig (plan_id, plan_name, plan_type, tracking_file)
↓
HTMLViewerGenerator outputs HTML string
↓
File: cortex-plan-viewer.html
```

**Test Cases:**
1. `test_toolkit_001_config_validation()` - ViewerConfig requires all fields
2. `test_toolkit_001_html_generation()` - HTML outputs contain expected elements
3. `test_toolkit_001_json_loading()` - Fetch calls correct paths
4. `test_toolkit_001_css_embedding()` - Styles are inline, not external
5. `test_toolkit_001_d3_rendering()` - D3 charts initialized correctly
6. `test_toolkit_001_mobile_responsive()` - Grid columns adjust properly
7. `test_toolkit_001_glassmorphism_compliance()` - Has backdrop-filter, rgba colors
8. `test_toolkit_001_accessibility()` - Tab order correct, ARIA labels present

---

### AC-TOOLKIT-002: Knowledge Graph Visualizer

**What it does:** Converts knowledge-graph.yaml into interactive D3.js force-directed graph

**Inputs:**
- `cortex-brain/tier1/{project}/knowledge-graph.yaml` - Semantic graph structure
  ```yaml
  nodes:
    - id: "auth-pattern"
      label: "Authentication Pattern"
      category: "security"
      frequency: 8
  edges:
    - source: "auth-pattern"
      target: "oauth-impl"
      relationship: "implements"
      strength: 0.9
  ```

**Outputs:**
- `cortex-brain/dashboards/{project}/knowledge-graph-viz.html` - Interactive visualization
  - Force-directed layout (D3.js simulation)
  - Node hover shows metadata
  - Edge labels show relationship strength
  - Color-coded by category (security=red, architecture=blue, etc.)
  - Zoom/pan controls
  - Legend with category counts

**Acceptance Criteria:**
- ✅ D3.js v7+ force simulation with collide/link forces
- ✅ Nodes render with correct colors by category
- ✅ Edges render with stroke-width = relationship strength
- ✅ Hover shows tooltip with node metadata
- ✅ Click node → highlights connected nodes + paths
- ✅ Zoom via mouse wheel, pan via drag
- ✅ Legend shows node counts per category
- ✅ Renders <1s for graphs up to 500 nodes

**Data Flow:**
```
knowledge-graph.yaml → YAML parser
↓
GraphData {nodes: [], edges: []}
↓
KnowledgeGraphVisualizer.render_force_directed()
↓
D3ForceSimulation (300 iterations)
↓
SVG elements (nodes = circles, edges = lines)
↓
Interactive event handlers (hover, click, zoom)
↓
HTML: knowledge-graph-viz.html
```

**Test Cases:**
1. `test_toolkit_002_graph_loading()` - YAML parsed correctly
2. `test_toolkit_002_node_rendering()` - All nodes appear with correct colors
3. `test_toolkit_002_edge_rendering()` - Edge widths match relationship strength
4. `test_toolkit_002_force_simulation()` - Nodes repel each other (don't overlap)
5. `test_toolkit_002_hover_behavior()` - Tooltip shows on mouseenter
6. `test_toolkit_002_click_highlight()` - Related nodes highlight on click
7. `test_toolkit_002_zoom_pan()` - Mouse wheel zoom works, drag pans
8. `test_toolkit_002_legend_accuracy()` - Category counts match actual nodes

---

### AC-TOOLKIT-003: Architecture Diagram Generator

**What it does:** Creates four-tier brain architecture visualization with glassmorphism styling and D3.js animations

**Inputs:**
- Tier 0 file counts: `cortex-brain/tier0/governance/`
- Tier 1 project count + AC metadata: `cortex-brain/tier1/`
- Tier 2 standards: `cortex-brain/tier2/engineering-standards.yaml`
- Tier 3 patterns: `cortex-brain/tier3/domain-patterns.yaml`

**Outputs:**
- `cortex-brain/dashboards/architecture-brain.html` - Animated four-tier visualization
  - 4 circular nodes (tiers 0-3) with radial gradients
  - Curved connection paths with pulsing animation
  - Hover effects (scale 1.05x, gradient glow)
  - Statistics panel per tier (file count, AC count, etc.)
  - Interactive legend

**Acceptance Criteria:**
- ✅ SVG renders 4 circular tier nodes at (150, 150, 150, 150) px radius
- ✅ Connection paths use d3.linkCurve() with smooth Catmull-Rom interpolation
- ✅ Pulsing animation (opacity 0.5-1.0, 2s loop) on connections
- ✅ Hover on node scales to 1.05x, adds glow filter
- ✅ Statistics update from file system (live count, no hardcoding)
- ✅ Colors: Tier0=purple, Tier1=cyan, Tier2=green, Tier3=orange
- ✅ Responsive SVG viewBox maintains aspect ratio on resize
- ✅ Mobile-friendly (stacks vertically on <768px)

**Data Flow:**
```
Tier0: os.listdir(tier0_path) → count governance files
Tier1: os.listdir(tier1_path) → count projects + AC status
Tier2: Load engineering-standards.yaml → parse sections
Tier3: Load domain-patterns.yaml → count pattern categories

Collected Stats → TierMetadata objects
↓
ArchitectureDiagramGenerator.render_four_tier_brain()
↓
SVG Canvas (800x800px)
↓
D3 Selections: circle (nodes), path (connections)
↓
Animations: transition().duration(1500)
↓
HTML: architecture-brain.html
```

**Test Cases:**
1. `test_toolkit_003_tier_counts()` - File counts accurate from filesystem
2. `test_toolkit_003_svg_rendering()` - 4 nodes appear with correct colors
3. `test_toolkit_003_connection_paths()` - All paths render smoothly
4. `test_toolkit_003_pulsing_animation()` - Opacity changes 0.5-1.0 repeatedly
5. `test_toolkit_003_hover_scaling()` - Node scales to 1.05x on hover
6. `test_toolkit_003_glow_filter()` - SVG filter applied on hover
7. `test_toolkit_003_responsive_layout()` - SVG viewBox adjusts on window resize
8. `test_toolkit_003_statistics_panel()` - Shows accurate tier metadata

---

### AC-TOOLKIT-004: Audit Log HTML Exporter

**What it does:** Exports audit-logs/*.jsonl as searchable, filterable HTML timeline

**Inputs:**
- `cortex-brain/audit-logs/default.jsonl` - Newline-delimited JSON events
  ```json
  {"timestamp": "2026-01-12T15:30:00Z", "level": "INFO", "category": "GOVERNANCE", "message": "Rule enforced: CORE-001", "correlation_id": "uuid-123"}
  ```

**Outputs:**
- `cortex-brain/dashboards/audit-log-viewer.html` - Interactive viewer
  - Timeline of events with timestamps
  - Filter pills (by level: INFO/WARNING/ERROR/CRITICAL)
  - Filter pills (by category: GOVERNANCE/ORCHESTRATOR/VALIDATION/etc.)
  - Event cards with: time, level badge, category, message, metadata
  - Click event → detail panel (3-pane layout: filters | timeline | details)
  - Search box (real-time filtering)
  - Export CSV button

**Acceptance Criteria:**
- ✅ Loads and parses JSONL file (10,000+ events)
- ✅ Timeline displays events in reverse chronological order
- ✅ Filter pills work (single or multiple selections)
- ✅ Search box filters events by message text (real-time)
- ✅ Click event → detail pane shows full event + metadata
- ✅ Three-pane layout: filters (top) | timeline (center) | details (bottom)
- ✅ Mobile responsive (timeline stacks full-width on <768px)
- ✅ <2s load time for 10K events (uses pagination or virtual scrolling)
- ✅ Color-coded event levels (INFO=blue, WARNING=orange, ERROR=red, CRITICAL=darkred)

**Data Flow:**
```
default.jsonl → readAsText()
↓
Split by newline → JSON.parse() each line
↓
EventList = [Event{timestamp, level, category, message}, ...]
↓
Sort by timestamp DESC
↓
AuditLogExporter.render_timeline_viewer()
↓
HTML Structure:
  - Filter pills section
  - Timeline list (virtual scroll)
  - Detail panel template
↓
Interactive event handlers: click, filter, search
↓
HTML: audit-log-viewer.html
```

**Test Cases:**
1. `test_toolkit_004_jsonl_parsing()` - Correctly parses JSONL format
2. `test_toolkit_004_event_ordering()` - Events in reverse chronological order
3. `test_toolkit_004_filter_pills()` - Level/category filters work independently
4. `test_toolkit_004_multi_select_filter()` - Multiple pill selections AND together
5. `test_toolkit_004_search_box()` - Real-time search by message
6. `test_toolkit_004_detail_panel()` - Shows all event fields on click
7. `test_toolkit_004_pagination()` - Loads 10K events without performance hit
8. `test_toolkit_004_color_coding()` - Levels have correct badge colors
9. `test_toolkit_004_csv_export()` - Generates valid CSV of filtered events
10. `test_toolkit_004_mobile_responsive()` - Timeline stacks on <768px

---

### AC-TOOLKIT-005: Glassmorphism Compliance Engine

**What it does:** Validates all HTML outputs meet glassmorphism design standard

**Validation Rules:**
- ✅ All panels use `backdrop-filter: blur(10-20px)`
- ✅ Backgrounds use `rgba(x, y, z, 0.1-0.3)` transparency
- ✅ Borders use `1px solid rgba(0, 212, 255, 0.15)`  (cyan with opacity)
- ✅ No inline `style=` attributes (all CSS in `<style>` tags)
- ✅ Colors follow palette (primary=cyan #00d4ff, accent=purple #7b2cbf, success=green #06ffa5)
- ✅ Font stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto
- ✅ No external stylesheets (all CSS embedded)
- ✅ Smooth transitions (200ms-400ms ease-out)

**Test Cases:**
1. `test_toolkit_005_backdrop_filter()` - All panels have backdrop-filter
2. `test_toolkit_005_rgba_compliance()` - Colors use rgba() with opacity
3. `test_toolkit_005_border_colors()` - Borders follow cyan standard
4. `test_toolkit_005_no_inline_styles()` - Zero inline style= attributes
5. `test_toolkit_005_color_palette()` - Only approved colors used
6. `test_toolkit_005_font_stack()` - Correct fallback chain
7. `test_toolkit_005_no_external_css()` - All CSS embedded
8. `test_toolkit_005_transition_timing()` - All animations use approved durations

---

### AC-TOOLKIT-006: Modern Tab System (Reusable Component)

**What it does:** Provides keyboard-accessible tab interface for all dashboards

**Features:**
- Tab navigation with ARIA labels
- Keyboard nav: LEFT/RIGHT arrows, HOME/END, TAB cycle
- State persistence via localStorage
- Smooth fade animations (300ms)
- Mobile-friendly (tabs scroll horizontally on narrow screens)
- Active indicator (left border highlight + color)

**Usage Example:**
```html
<div class="tab-system">
  <div class="tab-nav" role="tablist">
    <button class="tab-button" role="tab" aria-selected="true" aria-controls="tab1">
      Overview
    </button>
    <button class="tab-button" role="tab" aria-selected="false" aria-controls="tab2">
      Details
    </button>
  </div>
  <div class="tab-content">
    <div id="tab1" role="tabpanel" class="tab-panel active">Content 1</div>
    <div id="tab2" role="tabpanel" class="tab-panel">Content 2</div>
  </div>
</div>

<script src="modern-tabs.js"></script>
<script>
  new TabSystem('.tab-system', { persistState: true });
</script>
```

**Test Cases:**
1. `test_toolkit_006_tab_navigation()` - LEFT/RIGHT arrows switch tabs
2. `test_toolkit_006_home_end_keys()` - HOME goes to first, END to last
3. `test_toolkit_006_aria_labels()` - All tabs have proper ARIA attributes
4. `test_toolkit_006_state_persistence()` - Selected tab restored on page reload
5. `test_toolkit_006_fade_animation()` - Tab switch fades smoothly (300ms)
6. `test_toolkit_006_mobile_scrolling()` - Tabs scroll horizontally on narrow viewport
7. `test_toolkit_006_focus_management()` - Focus moves with active tab

---

### AC-TOOLKIT-007: Mermaid Diagram Engine

**What it does:** Embeds Mermaid diagrams in all dashboard types

**Diagram Types:**
- Graph (dependency flows, state transitions)
- Class diagram (object hierarchies)
- Timeline (phase progression)
- Flowchart (orchestrator logic)
- Sequence diagram (component interactions)

**Test Cases:**
1. `test_toolkit_007_mermaid_loading()` - mermaid.js loads correctly
2. `test_toolkit_007_graph_rendering()` - Flowcharts render without errors
3. `test_toolkit_007_responsive_diagrams()` - Diagrams scale on resize
4. `test_toolkit_007_mermaid_theming()` - Color palette applied to diagrams
5. `test_toolkit_007_diagram_exports()` - SVG export works (save as image)

---

### AC-TOOLKIT-008: CORTEX TOOLKIT MCP Server

**What it does:** Expose all 7 generators as MCP tools for other orchestrators

**MCP Tools Exposed:**

```python
@mcp_tool
def generate_epic_viewer(plan_data: dict, tracking_data: dict) -> str:
    """Generate interactive epic plan viewer HTML"""
    return HTMLViewerGenerator().generate_epic_viewer(ViewerConfig(...))

@mcp_tool
def generate_knowledge_graph_viz(kg_yaml_path: str) -> str:
    """Generate interactive knowledge graph visualization"""
    return KnowledgeGraphVisualizer().render_force_directed(...)

@mcp_tool
def generate_architecture_diagram(tier_paths: dict) -> str:
    """Generate four-tier brain architecture diagram"""
    return ArchitectureDiagramGenerator().render_four_tier_brain(...)

@mcp_tool
def generate_audit_log_viewer(audit_jsonl_path: str) -> str:
    """Generate interactive audit log timeline viewer"""
    return AuditLogExporter().render_timeline_viewer(...)

@mcp_tool
def validate_glassmorphism(html_content: str) -> dict:
    """Validate HTML meets glassmorphism design standard"""
    return GlassmorphismEngine().validate(html_content)
```

**Who Uses These Tools:**
- **Planning v5** → Calls `generate_epic_viewer()` to visualize discovered context
- **Investigation** → Calls `generate_knowledge_graph_viz()` to explore learned patterns
- **Onboarding** → Calls `generate_epic_viewer()` to show projected onboarding timeline
- **Dashboard** → Periodically calls all generators to refresh HTML views

**Test Cases:**
1. `test_toolkit_008_mcp_registration()` - All 5 tools registered in MCP registry
2. `test_toolkit_008_tool_parameters()` - Tool signatures match expected inputs
3. `test_toolkit_008_tool_outputs()` - All tools return valid HTML strings
4. `test_toolkit_008_mcp_error_handling()` - Graceful failures with error messages
5. `test_toolkit_008_tool_performance()` - All generators <5s for typical inputs

---

## 🏗️ File Structure

```
cortex-brain/
├── documents/
│   ├── assets/
│   │   ├── modern-tabs.css (399 lines)
│   │   ├── modern-tabs.js (200+ lines)
│   │   ├── four-tier-brain-custom.css (150+ lines)
│   │   └── mermaid-integration.js (NEW)
│   ├── strategy/
│   │   └── CORTEX-TOOLKIT-STRATEGY.md (THIS FILE)
│   └── implementation-guides/
│       └── modern-tab-system-guide.md (from CORTEX-5.5)
├── cx6-plan/viewer/
│   ├── plan-viewer-data.json
│   ├── cortex-plan-viewer.html (AC-TOOLKIT-001 output)
│   └── index.html (redirect to main viewer)
└── dashboards/
    ├── cortex-plan-viewer.html
    ├── audit-log-viewer.html
    ├── knowledge-graph-viz.html
    ├── architecture-brain.html
    └── README.md (how to regenerate views)

scripts/
├── cortex_html_viewer_generator.py (798 lines - HTML generation)
├── page_modernizer.py (from CORTEX-5.5)
└── toolkit_mcp_server.py (NEW - MCP registration)

src/
└── orchestrators/
    └── toolkit/
        ├── __init__.py
        ├── epic_viewer_generator.py
        ├── knowledge_graph_visualizer.py
        ├── architecture_diagram_generator.py
        ├── audit_log_exporter.py
        ├── glassmorphism_engine.py
        ├── modern_tab_system.py
        ├── mermaid_engine.py
        └── toolkit_mcp_server.py
```

---

## 📈 Metrics & Goals

| Metric | Target | Rationale |
|--------|--------|-----------|
| HTML file size | <500KB each | Self-contained, fast load |
| Page load time | <2s (first paint) | User experience |
| Interactive responsiveness | <100ms (click→response) | Smooth interaction |
| D3.js render time | <1s for 500 nodes | Knowledge graph visualization |
| Design compliance | 100% glassmorphism | Visual consistency |
| WCAG compliance | AA (7:1 contrast) | Accessibility |
| Browser support | Chrome, Firefox, Safari, Edge (last 2 versions) | Broad compatibility |
| Mobile responsive | 320px-1440px+ | All device sizes |

---

## 🔗 Integration Points

### Phase 1.5: CORTEX LENS & Onboarding
- CORTEX LENS generates knowledge graphs → **AC-TOOLKIT-002** visualizes
- Onboarding discovers architecture → **AC-TOOLKIT-003** visualizes
- Both write audit logs → **AC-TOOLKIT-004** displays

### Phase 2: Planning v5
- Uses **AC-TOOLKIT-001** to show projected timelines
- Exposes via **AC-TOOLKIT-008** MCP tools to other orchestrators

### Phase 3: Feature Orchestrators
- Investigation queries knowledge graphs → **AC-TOOLKIT-002** renders
- Audit needs visible → **AC-TOOLKIT-004** provides timeline

---

## 📦 Deliverables

**AC-TOOLKIT-001 to 004:** 4 HTML generators (2 weeks)
- `epic_viewer_generator.py` (300 lines)
- `knowledge_graph_visualizer.py` (250 lines)
- `architecture_diagram_generator.py` (300 lines)
- `audit_log_exporter.py` (250 lines)

**AC-TOOLKIT-005 to 006:** Design system (1 week)
- `glassmorphism_engine.py` (150 lines)
- `modern_tab_system.py` (reuse from CORTEX-5.5)

**AC-TOOLKIT-007:** Mermaid integration (3 days)
- `mermaid_engine.py` (150 lines)

**AC-TOOLKIT-008:** MCP exposure (3 days)
- `toolkit_mcp_server.py` (200 lines)
- MCP tool registration

**Total:** 8 ACs, 1.5 weeks implementation, <1800 lines new code

---

## ✅ Success Criteria

1. **All 8 dashboards regenerate automatically** when underlying data changes
2. **Zero external dependencies** (all CSS/JS embedded)
3. **100% glassmorphism compliance** (validated by AC-TOOLKIT-005)
4. **WCAG AA accessible** across all views
5. **Mobile responsive** (320px-1440px+)
6. **<2s page load** even with 10K+ audit events
7. **All tools callable via MCP** from Planning v5, Investigation, others
8. **80%+ test coverage** for all components

---

