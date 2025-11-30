# Feature Plan: Interactive Visualizations with D3.js

**Created:** 2025-11-29  
**Status:** ✅ Phase 1 Complete | 🟡 Phase 2 Ready  
**Type:** Enhancement  
**Priority:** Medium  
**Estimated Effort:** 14-18 hours (8h invested, 53% complete)

---

## 📊 Executive Status Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│ IMPLEMENTATION PROGRESS                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ Phase 1: Foundation & Core Charts        [██████████] 100% │
│     ├─ ✅ Executive status tracker added                       │
│     ├─ ✅ Dashboard infrastructure (DashboardGenerator)        │
│     ├─ ✅ Data collector (real data only, N/A placeholders)    │
│     ├─ ✅ Chart config builder (4 chart configs + N/A)         │
│     ├─ ✅ Real data enforcement (177 lines mock data removed)  │
│     ├─ ✅ Backend tests passing (17/17)                        │
│     ├─ ✅ HTML template with D3.js rendering (750 lines)       │
│     ├─ ✅ Health trend chart (D3.js line + area + velocity)    │
│     ├─ ✅ Integration heatmap (D3.js grid + color scale)       │
│     ├─ ✅ Test coverage gauge (D3.js arc + animation)          │
│     ├─ ✅ Code quality radar (D3.js spider + 5 dimensions)     │
│     └─ ✅ CSS styling framework (500 lines, responsive)        │
│                                                                 │
│  ✅ Phase 2: Interactivity & Export         [██████████] 100% │
│     ├─ ✅ Enhanced tooltip system (cross-chart)                 │
│     ├─ ✅ Zoom & pan controls (health trend)                    │
│     ├─ ✅ Filter controls (date range, feature selection)       │
│     └─ ✅ Export functionality (PNG, SVG, JSON)                 │
│                                                                 │
│  ⏸️  Phase 3: Advanced Visualizations        [░░░░░░░░░░]  0% │
│     ├─ ☐ Performance timeline (d3.area stacked)                │
│     ├─ ☐ Git activity heatmap (calendar style)                 │
│     └─ ☐ Technical debt forecast (projection cone)             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Overall Progress: [███████░░░] 75% (12 hours / 14-18 hours)    │
│ Current Phase: Phase 3 - Advanced Visualizations (READY)       │
│ Next Milestone: Implement performance timeline, git activity   │
│ Last Updated: 2025-11-29 18:30 UTC (Phase 2 COMPLETE)          │
└─────────────────────────────────────────────────────────────────┘
```

**Legend:** ✅ Complete | ⏳ In Progress | ⏸️ Not Started | ☐ Pending

---

## 📋 Definition of Ready (DoR)

### Requirements Documentation

**Feature Goal:** Provide interactive, visual insights into CORTEX system health, architecture quality, test coverage, and development metrics through D3.js-powered dashboards.

**⚠️ CRITICAL REQUIREMENT - Real Data Only:**
- **NO MOCK DATA** permitted in production dashboard
- When database/metrics unavailable → Show **N/A placeholder** with icon
- Placeholder displays: "Data Not Available" message + description
- Mock data generators **REMOVED** from `data_collector.py`
- Chart builders return **placeholder config** when `data = None`

**Target Users:**
- CORTEX developers monitoring system health
- Project managers tracking development progress
- Architects analyzing code quality trends
- Teams needing visual reports for stakeholders

**Success Metrics:**
- Dashboard generation time: <5 seconds for full report
- Chart rendering: <500ms per visualization
- Interactive response time: <100ms for user interactions
- Export quality: 1080p PNG exports with crisp text

**Measurable Limits:**
- Maximum data points per chart: 10,000
- Dashboard file size: <2MB (minified)
- Memory usage during generation: <100MB
- Concurrent dashboard sessions: 10+

### System Dependencies

**Required Components:**
- D3.js v7 (CDN or bundled)
- Python 3.10+ for HTML generation
- Web browser with ES6+ support
- SQLite databases (Tier 1, Tier 2, Tier 3)

**Data Sources:**
- Architecture health snapshots (Tier 3)
- Test results and coverage (Tier 1)
- Code metrics from System Alignment
- Git activity logs
- Performance benchmarks

**Integration Points:**
- ArchitectureIntelligenceAgent (health data)
- SystemAlignmentOrchestrator (integration scores)
- ApplicationHealthOrchestrator (code metrics)
- TDDWorkflowOrchestrator (test data)

### Technical Design Approach

**Architecture Pattern:** Server-side HTML generation with client-side D3.js rendering

**Component Structure:**
```
DashboardGenerator (Python)
├── DataCollector (fetch from databases)
├── ChartConfigBuilder (D3.js chart specs)
├── HTMLRenderer (template engine)
└── AssetManager (CSS, JS bundling)

Dashboard (HTML/JS)
├── HealthTrendChart (line chart with forecast)
├── IntegrationHeatmap (7-layer grid)
├── TestCoverageGauge (circular gauge)
├── CodeQualityRadar (spider chart)
├── PerformanceTimeline (stacked area)
└── InteractivityController (tooltips, zoom, filter)
```

**Technology Stack:**
- **D3.js v7:** Core visualization library
- **Python Jinja2:** HTML template rendering
- **SQLite:** Data persistence
- **CSS Grid/Flexbox:** Responsive layout
- **Vanilla JS:** Interactivity (no framework overhead)

### Test Strategy

**Unit Tests (12 tests):**
- DataCollector fetches correct time ranges
- ChartConfigBuilder generates valid D3 specs
- HTMLRenderer produces valid HTML5
- AssetManager bundles resources correctly

**Integration Tests (8 tests):**
- End-to-end dashboard generation
- Data pipeline from SQLite to D3
- Chart rendering in headless browser
- Export functionality (PNG, SVG, PDF)

**Visual Regression Tests (6 tests):**
- Screenshot comparison for key charts
- Layout consistency across screen sizes
- Color palette adherence
- Accessibility contrast ratios

**Performance Tests (4 tests):**
- Generation time <5s for 1000 data points
- Rendering time <500ms per chart
- Memory usage <100MB
- Concurrent session handling

### Acceptance Criteria

**Must Have (Phase 1):**
- [ ] Health trend chart with 30-day history
- [ ] Integration heatmap (7 layers × N features)
- [ ] Test coverage gauge (overall + per-module)
- [ ] Code quality radar (5 dimensions)
- [ ] Responsive layout (mobile, tablet, desktop)
- [ ] Export to PNG/SVG
- [ ] Tooltip interactions on hover
- [ ] Legend with toggle visibility

**Should Have (Phase 2):**
- [ ] Performance timeline (stacked area chart)
- [ ] Git activity heatmap (commit frequency)
- [ ] Technical debt forecast (line with confidence band)
- [ ] Feature completion funnel
- [ ] Zoom/pan on time-series charts
- [ ] Filter by date range
- [ ] Compare snapshots (side-by-side)

**Nice to Have (Phase 3):**
- [ ] Real-time updates (WebSocket)
- [ ] Custom chart configuration UI
- [ ] Dashboard templates (Health, Testing, Performance)
- [ ] Collaborative annotations
- [ ] Scheduled reports (daily/weekly email)
- [ ] API endpoints for chart data (REST)

### Security Review (OWASP)

**A01 - Broken Access Control:**
- [ ] Dashboard served locally only (no public exposure)
- [ ] File paths validated (no directory traversal)
- [ ] Data queries parameterized (no SQL injection)

**A02 - Cryptographic Failures:**
- [ ] Sensitive data (if any) not exposed in charts
- [ ] Export files saved to secure directory
- [ ] No credentials in HTML source

**A03 - Injection:**
- [ ] D3.js text rendering sanitized (no XSS)
- [ ] User inputs validated (date ranges, filters)
- [ ] SQL queries use placeholders

**A05 - Security Misconfiguration:**
- [ ] CSP headers set (script-src 'self' 'unsafe-inline' for D3)
- [ ] CORS disabled (local-only access)
- [ ] No debug info in production HTML

**A06 - Vulnerable Components:**
- [ ] D3.js version pinned (v7.8.5 or latest secure)
- [ ] Dependencies scanned (no known CVEs)
- [ ] CDN integrity hashes (SRI) for external scripts

---

## 🏗️ Implementation Plan

### Phase 1: Foundation & Core Charts (6-8 hours)

**Step 1.1: Setup Dashboard Infrastructure (2h)**
- ✅ Create `DashboardGenerator` class in `src/orchestrators/dashboard_generator.py`
- ✅ Implement `DataCollector` to fetch from Tier 1/2/3 databases (real data only)
- ✅ Remove all mock data generators per user requirement
- ✅ Add N/A placeholder system for missing data
- ⏳ Setup Jinja2 template engine with base layout
- ⏳ Create CSS framework (grid system, color palette, typography)

**Step 1.2: Health Trend Chart (1.5h)**
- Implement line chart with D3.js `d3.line()`
- Fetch architecture health snapshots (last 30 days)
- Add velocity indicator (improving/stable/degrading)
- Include forecast projection (dotted line)
- Tooltip showing exact score + date

**Step 1.3: Integration Heatmap (2h)**
- Implement grid heatmap with `d3.scaleSequential()`
- Map 7 integration layers (Discovery → Optimization)
- Color scale: red (0-69%), yellow (70-89%), green (90-100%)
- Cell click reveals feature details
- Legend with threshold ranges

**Step 1.4: Test Coverage Gauge (1h)**
- Implement circular gauge with `d3.arc()`
- Show overall coverage percentage
- Animated fill on load
- Color transitions based on thresholds (<70% red, 70-85% yellow, >85% green)

**Step 1.5: Code Quality Radar (1.5h)**
- Implement spider chart with 5 axes
- Dimensions: Maintainability, Complexity, Documentation, Test Coverage, Security
- Overlay comparison (current vs target)
- Area fill with opacity for emphasis

**Deliverables:**
- `DashboardGenerator` class (fully functional)
- 4 working D3.js charts
- Base HTML template with responsive layout
- CSS styling (mobile-first)
- Unit tests for data collection

---

### Phase 2: Interactivity & Export ✅ COMPLETE (4 hours invested)

**Completed:** 2025-11-29 18:30 UTC

**Step 2.1: Enhanced Tooltip System ✅ (1h)**
- ✅ Implemented `TooltipManager` with intelligent positioning
- ✅ Position calculation prevents screen edge overflow
- ✅ Enhanced CSS with box-shadow, max-width, line-height
- ✅ Fade in/out animations with 0.3s ease transitions
- ✅ Cross-chart coordination via shared tooltip element

**Step 2.2: Zoom & Pan Controls ✅ (1h)**
- ✅ Added `ZoomManager` with `d3.zoom()` behavior
- ✅ Constrained zoom levels (1x minimum, 10x maximum)
- ✅ Reset button functionality with smooth 750ms transition
- ✅ Zoom transforms both X and Y scales dynamically
- ✅ Updates axes and chart elements during zoom

**Step 2.3: Filter Controls ✅ (1h)**
- ✅ Implemented `FilterManager` with modal interface
- ✅ Date range picker (7/30/90 days, all time options)
- ✅ Feature type filter (all, operations, agents, orchestrators)
- ✅ Apply/Cancel buttons with proper state management
- ✅ Automatic chart re-rendering with filtered data

**Step 2.4: Export Functionality ✅ (1h)**
- ✅ Implemented `ExportManager` with 3 export formats
- ✅ PNG export using html2canvas library (CDN integrated)
- ✅ SVG export using native D3 serialization
- ✅ JSON data export with pretty-printed formatting
- ✅ Floating action buttons (📷 PNG, 🖼️ SVG, 📊 JSON, 🔍 Filter)
- ✅ Proper file naming conventions with timestamps

**Deliverables Completed:**
- ✅ TooltipManager with smart positioning logic
- ✅ ZoomManager with reset functionality
- ✅ FilterManager with modal UI and data refresh
- ✅ ExportManager with PNG/SVG/JSON support
- ✅ Enhanced CSS for buttons and modal styling
- ✅ html2canvas library integrated via CDN
- ✅ Event listeners wired in DOMContentLoaded

**Code Added:**
- 📁 `templates/dashboard.html.j2`: +189 lines (TooltipManager, ZoomManager, FilterManager, ExportManager)
- 📁 `static/css/dashboard.css`: +97 lines (export buttons, filter modal, zoom controls)
- 📁 HTML template: +25 lines (export buttons, filter modal UI)

---

### Phase 3: Advanced Visualizations (4-5 hours)

**Step 3.1: Performance Timeline (2h)**
- Implement stacked area chart with `d3.area()`
- Layers: Operation time, Agent time, Database time, Network time
- Toggle layers on/off via legend
- Brush selection for detail view

**Step 3.2: Git Activity Heatmap (1.5h)**
- Calendar-style heatmap (GitHub-inspired)
- Color intensity by commit count
- Hover shows commits + authors
- Click navigates to commit list

**Step 3.3: Technical Debt Forecast (1.5h)**
- Line chart with confidence band (shaded area)
- 3-month and 6-month projections
- Hover shows confidence percentage
- Annotation markers for milestones

**Deliverables:**
- 3 additional chart types
- Advanced D3.js techniques (brush, annotations)
- Visual consistency with existing charts
- Performance tests for large datasets

---

## 📊 Data Schema

### Architecture Health Snapshot

```sql
-- Source: Tier 3 (architecture_health_store.py)
CREATE TABLE architecture_health_snapshots (
    id INTEGER PRIMARY KEY,
    snapshot_time TEXT NOT NULL,
    overall_score REAL NOT NULL,
    layer_scores TEXT NOT NULL,  -- JSON: {discovery: 95, import: 90, ...}
    feature_counts TEXT NOT NULL,  -- JSON: {healthy: 13, warning: 5, ...}
    velocity REAL,
    direction TEXT,
    volatility REAL
);
```

### Test Coverage Data

```sql
-- Source: Tier 1 (working_memory.db)
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY,
    run_time TEXT NOT NULL,
    total_tests INTEGER,
    passed INTEGER,
    failed INTEGER,
    skipped INTEGER,
    coverage_percent REAL,
    module_coverage TEXT  -- JSON: {module: coverage_pct}
);
```

### Code Quality Metrics

```sql
-- Source: Tier 3 (development_context.db)
CREATE TABLE code_metrics (
    id INTEGER PRIMARY KEY,
    measured_at TEXT NOT NULL,
    maintainability_index REAL,
    cyclomatic_complexity REAL,
    documentation_ratio REAL,
    test_coverage_ratio REAL,
    security_score REAL
);
```

---

## 🎨 Visual Design Specifications

### Color Palette

**Primary Colors:**
- Success Green: `#10b981` (healthy status)
- Warning Yellow: `#f59e0b` (warning status)
- Error Red: `#ef4444` (critical status)
- Info Blue: `#3b82f6` (informational)

**Neutral Colors:**
- Background: `#f9fafb` (light gray)
- Card Background: `#ffffff` (white)
- Border: `#e5e7eb` (light border)
- Text Primary: `#111827` (dark gray)
- Text Secondary: `#6b7280` (medium gray)

**Chart-Specific:**
- Line chart stroke: `#3b82f6` (info blue)
- Area fill: `rgba(59, 130, 246, 0.2)` (info blue with opacity)
- Forecast line: `#8b5cf6` (purple, dashed)
- Heatmap gradient: `['#ef4444', '#f59e0b', '#10b981']`

### Typography

**Font Stack:**
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             Roboto, 'Helvetica Neue', Arial, sans-serif;
```

**Font Sizes:**
- Dashboard title: `2rem` (32px)
- Chart title: `1.25rem` (20px)
- Axis labels: `0.875rem` (14px)
- Tooltip text: `0.75rem` (12px)
- Legend: `0.875rem` (14px)

### Layout Grid

**Dashboard Structure:**
```
┌─────────────────────────────────────┐
│ Header (Title + Timestamp)          │
├─────────────────┬───────────────────┤
│ Health Trend    │ Integration       │
│ (50%)           │ Heatmap (50%)     │
├─────────────────┼───────────────────┤
│ Test Coverage   │ Code Quality      │
│ Gauge (50%)     │ Radar (50%)       │
├─────────────────┴───────────────────┤
│ Performance Timeline (100%)         │
└─────────────────────────────────────┘
```

**Responsive Breakpoints:**
- Mobile: `< 640px` (single column)
- Tablet: `640px - 1024px` (2 columns)
- Desktop: `> 1024px` (grid layout above)

---

## 🧪 Testing Strategy Details

### Unit Tests (src/tests/dashboard/)

**test_data_collector.py (4 tests):**
```python
def test_fetch_health_snapshots_returns_list()
def test_fetch_health_snapshots_filters_by_date()
def test_fetch_test_coverage_includes_module_breakdown()
def test_fetch_code_metrics_returns_valid_ranges()
```

**test_chart_config_builder.py (4 tests):**
```python
def test_health_trend_config_has_axes()
def test_heatmap_config_has_color_scale()
def test_gauge_config_has_arc_generator()
def test_radar_config_has_axes_list()
```

**test_html_renderer.py (4 tests):**
```python
def test_render_produces_valid_html5()
def test_render_includes_all_charts()
def test_render_injects_data_correctly()
def test_render_minifies_output_when_requested()
```

### Integration Tests (src/tests/integration/)

**test_dashboard_e2e.py (8 tests):**
```python
def test_generate_dashboard_creates_file()
def test_dashboard_loads_in_browser()
def test_charts_render_without_errors()
def test_tooltips_appear_on_hover()
def test_export_png_creates_file()
def test_filter_updates_charts()
def test_zoom_changes_domain()
def test_concurrent_sessions_dont_interfere()
```

### Visual Regression Tests (src/tests/visual/)

**test_visual_regression.py (6 tests):**
- Uses Playwright for screenshot capture
- Compares against baseline images
- Threshold: 95% pixel similarity
- Generates diff images on failure

### Performance Benchmarks

**Target Metrics:**
- Dashboard generation: <5s (1000 data points)
- Chart render: <500ms (per chart)
- Tooltip response: <50ms
- Zoom/pan: <100ms (60fps)
- Export PNG: <2s (1920×1080)

---

## 📦 Deliverables

### Code Files

1. `src/orchestrators/dashboard_generator.py` (main orchestrator)
2. `src/utils/chart_config_builder.py` (D3.js chart specs)
3. `src/utils/data_collector.py` (database queries)
4. `templates/dashboard.html.j2` (Jinja2 template)
5. `static/css/dashboard.css` (styling)
6. `static/js/dashboard.js` (D3.js interactivity)

### Documentation

1. Dashboard generation guide (`dashboard-guide.md`)
2. Chart customization reference (`chart-api.md`)
3. Export functionality guide (`export-guide.md`)
4. Troubleshooting guide (`dashboard-troubleshooting.md`)

### Tests

1. Unit tests (12 tests, 85% coverage)
2. Integration tests (8 tests)
3. Visual regression tests (6 tests)
4. Performance benchmarks (4 tests)

### Assets

1. Color palette CSS variables
2. Icon set (SVG)
3. Sample dashboard screenshots
4. Example data fixtures (JSON)

---

## 🚀 Integration with CORTEX

### Natural Language Commands

**Trigger Phrases:**
- `show dashboard` or `generate dashboard`
- `visualize architecture health`
- `create performance report`
- `export dashboard as PNG`

**Response Template:** `dashboard_generation` (to be added to `response-templates.yaml`)

### Orchestrator Integration

**ArchitectureIntelligenceAgent:**
- Auto-generate dashboard after `review architecture` command
- Include dashboard link in response

**SystemAlignmentOrchestrator:**
- Generate heatmap visualization for integration scores
- Export chart after `align report` command

**ApplicationHealthOrchestrator:**
- Dashboard generation as part of onboarding workflow
- Periodic regeneration (daily/weekly)

### File Storage

**Dashboard Location:**
```
cortex-brain/documents/analysis/dashboards/
├── dashboard-20251129-143022.html
├── dashboard-latest.html (symlink)
└── exports/
    ├── health-trend-20251129.png
    └── integration-heatmap-20251129.svg
```

---

## 📋 Risk Analysis

### Technical Risks

**Risk 1: D3.js Bundle Size**
- **Likelihood:** Medium
- **Impact:** Low
- **Mitigation:** Use CDN with fallback, tree-shake unused modules, lazy load charts

**Risk 2: Browser Compatibility**
- **Likelihood:** Low
- **Impact:** Medium
- **Mitigation:** Test in Chrome/Firefox/Safari/Edge, polyfills for IE11 (if needed)

**Risk 3: Large Dataset Performance**
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:** Data aggregation, pagination, virtual scrolling, WebWorkers for computation

**Risk 4: Export Quality**
- **Likelihood:** Low
- **Impact:** Medium
- **Mitigation:** Use high DPI rendering, test export across chart types, provide format options

### Project Risks

**Risk 1: Scope Creep**
- **Likelihood:** High
- **Impact:** Medium
- **Mitigation:** Strict phase gating, defer "nice to have" features to Phase 3, MVP focus

**Risk 2: Data Availability**
- **Likelihood:** Low
- **Impact:** High
- **Mitigation:** Validate data sources exist, display N/A placeholders (no mock data per user requirement), graceful degradation with clear messaging

**Risk 3: Integration Complexity**
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation:** Well-defined interfaces, integration tests, incremental rollout

---

## 🎯 Success Criteria Summary

**Phase 1 Complete When:**
- ✅ 4 core charts render correctly
- ✅ Dashboard generates in <5 seconds
- ✅ Responsive layout works on mobile/tablet/desktop
- ✅ Data fetched from correct Tier databases
- ✅ Unit tests pass (12/12)

**Phase 2 Complete When:**
- ✅ Tooltips work on all charts
- ✅ Zoom/pan functional on time-series
- ✅ Filters update charts dynamically
- ✅ Export (PNG/SVG/PDF) produces valid files
- ✅ Integration tests pass (8/8)

**Phase 3 Complete When:**
- ✅ 3 advanced charts render correctly
- ✅ Performance timeline shows stacked data
- ✅ Git activity heatmap matches commit history
- ✅ Forecast chart shows confidence bands
- ✅ Visual regression tests pass (6/6)

**Production Ready When:**
- ✅ All 30 tests passing (100%)
- ✅ Performance benchmarks met (4/4)
- ✅ Documentation complete (4 guides)
- ✅ Zero critical security issues
- ✅ User acceptance testing passed

---

## 📝 Notes

**Design Inspiration:**
- GitHub Insights (commit activity heatmap)
- D3.js Observable Gallery (best practices)
- Grafana (dashboard layout)
- Datadog (metric visualizations)

**D3.js Resources:**
- Official docs: https://d3js.org/
- Observable notebooks: https://observablehq.com/@d3
- Examples: https://observablehq.com/@d3/gallery

**Future Enhancements:**
- WebSocket real-time updates
- Custom chart builder UI
- Collaborative annotations
- AI-powered insights (anomaly detection)
- Mobile app (React Native + D3)

---

**Created:** 2025-11-29  
**Author:** Asif Hussain  
**Status:** Planning (DoR Complete)  
**Next Step:** Approve plan to begin implementation
