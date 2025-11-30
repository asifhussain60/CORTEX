# CORTEX Onboarding App Dashboard - Comprehensive Enhancement Plan

**Feature Name:** Onboarding App Dashboard 2.0 (Enhanced Visualization)  
**Plan ID:** PLAN-2025-11-30-ONBOARDING-APP-DASHBOARD  
**Created:** 2025-11-30  
**Author:** Asif Hussain  
**Status:** ✅ APPROVED (Ready for Implementation)  
**Approved:** 2025-11-30  
**Priority:** HIGH  
**Type:** Enhancement  
**Target Version:** CORTEX 3.3.0

---

## 📋 Executive Summary

**Current State:** Application Health Dashboard is 70% complete with strong foundations in progressive crawling, multi-language analysis, and D3.js visualization. However, **critical gaps exist** in backend architecture visualization (30%), interactive features (40%), and clean architecture organization (40%).

**Target State:** Production-ready dashboard that impresses audiences with:
- ✅ Backend architecture visualization (dependency graphs, component diagrams)
- ✅ Interactive drill-down navigation with real-time updates
- ✅ 5-tab organized structure (Overview, Architecture, Quality, Security, Recommendations)
- ✅ Clean architecture following CORTEX rulebook principles
- ✅ Modern UI with D3.js, Chart.js, and WebSocket integration

**Key Metric:** From 70% → 95% feature completeness in 3 sprint cycles (6 weeks)

**Business Value:** This is the "wow factor" feature for CORTEX demonstrations, showcasing holistic understanding of codebases with visual insights that exceed traditional static analysis tools.

---

## 🎯 Definition of Ready (DoR) Validation

### Requirements Clarity

**What EXACTLY does this feature do?**

This enhancement transforms the existing Application Health Dashboard into a comprehensive visualization platform that:

1. **Generates Backend Architecture Views** - After scanning an application, automatically creates:
   - Force-directed dependency graphs showing module relationships
   - Component hierarchy diagrams (namespace/package structure)
   - Data flow visualizations (API → Service → Database layers)
   - Call graph analysis (function invocation chains)

2. **Provides Interactive Navigation** - Users can:
   - Click on any component to drill down into details
   - Filter by language, framework, or quality score
   - Toggle between architecture, quality, and security views
   - Export filtered views to PDF/PNG/PPTX

3. **Organizes Data into 5 Tabs** - Structured navigation:
   - **Overview Tab** - Health scores, file counts, language breakdown (EXISTS)
   - **Architecture Tab** - Dependency graphs, component diagrams (NEW)
   - **Quality Tab** - Code smells, complexity metrics, test coverage (ENHANCE)
   - **Security Tab** - Vulnerability reports, OWASP compliance (ENHANCE)
   - **Recommendations Tab** - Prioritized action items with fix templates (NEW)

4. **Follows Clean Architecture** - Dashboard site itself demonstrates best practices:
   - Presentation layer (HTML/CSS/JS) separate from business logic
   - Data layer (JSON adapters) separate from visualization logic
   - Use cases (tab controllers) coordinate between layers
   - Dependency injection for testability

5. **Integrates WebSocket Real-Time Updates** - Live monitoring:
   - Health score changes as code evolves
   - New issues appear in real-time during development
   - Progress bars show crawling status without page refresh

**Who are the SPECIFIC users?**

1. **Development Teams** - Engineers using CORTEX to onboard new applications
   - **Need:** Quick architectural understanding of unfamiliar codebases
   - **Use Case:** "Show me how authentication flows through this app"
   - **Success Metric:** 10 minutes to architectural understanding vs 2+ hours manual

2. **Tech Leads** - Architects reviewing code quality and structure
   - **Need:** High-level component relationships and dependency health
   - **Use Case:** "Identify circular dependencies and tightly coupled modules"
   - **Success Metric:** Immediate visualization vs days of manual analysis

3. **Product Managers** - Non-technical stakeholders needing status visibility
   - **Need:** Health scores, quality trends, security posture
   - **Use Case:** "Is this codebase ready for production deployment?"
   - **Success Metric:** 5-minute executive summary vs technical deep dives

4. **Security Auditors** - Reviewers assessing vulnerability landscape
   - **Need:** OWASP Top 10 mapping, vulnerable dependency identification
   - **Use Case:** "Show all injection vulnerabilities and affected components"
   - **Success Metric:** Instant filtered view vs manual code review

5. **CORTEX Demonstrators** - Asif and team showcasing capabilities to clients/conferences
   - **Need:** Visually impressive, modern, interactive dashboards
   - **Use Case:** Live demonstration of codebase analysis in 30 seconds
   - **Success Metric:** Audience engagement and "wow" reactions

**What are the EXACT systems/APIs/databases required?**

### Internal CORTEX Systems (All Existing)

1. **CrawlerOrchestrator** (`src/crawlers/crawler_orchestrator.py`)
   - Already implemented with 3 scan levels (overview, standard, deep)
   - Provides file discovery, language detection, LOC counting
   - **Enhancement:** Add dependency edge extraction to crawl results

2. **ApplicationHealthOrchestrator** (`src/orchestrators/application_health_orchestrator.py`)
   - Coordinates analyzer execution and result aggregation
   - **Enhancement:** Call DependencyGraph builder after analysis phase

3. **DependencyGraph** (`src/crawlers/dependency_crawler.py`)
   - Exists but NOT integrated into dashboard workflow
   - **Integration Required:** Wire into ApplicationHealthOrchestrator
   - **Output:** Node/edge JSON for D3.js force-directed graph

4. **IntegrationScorer** (`src/validation/integration_scorer.py`)
   - 7-layer validation with health scoring
   - **Integration Required:** Pass scores to dashboard for per-component coloring

5. **RefactoringIntelligence** (`src/agents/refactoring_intelligence.py`)
   - 11 code smell types with confidence scoring
   - **Integration Required:** Generate recommendations tab content

6. **Tier 3 Databases** (All in `cortex-brain/tier3-development-context.db`)
   - `code_metrics` table - Complexity, LOC, function counts
   - `file_changes` table - Git activity heatmap data
   - `dev_insights` table - Pattern learning for recommendations
   - **Enhancement:** Add `architecture_snapshots` table for temporal comparison

### External Libraries (Need Verification)

7. **D3.js v7** - For force-directed graphs
   - Already used in existing dashboard (confirmed in dashboard-20251129-164200.html)
   - **Version:** Verify v7 for latest features (zoom, pan, force simulation)

8. **Chart.js v4** - For real-time metrics
   - Already used in RealLiveDataGenerator dashboards
   - **Enhancement:** Add WebSocket data source adapter

9. **Socket.IO** - For WebSocket real-time updates
   - **Status:** NOT IMPLEMENTED
   - **Requirement:** Python Socket.IO server + JS client integration

10. **python-pptx** - For PowerPoint export
    - **Status:** NOT IMPLEMENTED (PDF/PNG exist via weasyprint, selenium)
    - **Requirement:** Install `python-pptx` package

### APIs/Services

11. **No External APIs Required** - All processing is local
    - CORTEX operates air-gapped by design
    - Dashboard generation is fully offline

**What are the MEASURABLE limits/constraints?**

1. **Performance Targets**
   - Overview scan: <30 seconds for 50K files
   - Standard scan: <2 minutes for 50K files
   - Deep scan: <5 minutes for 50K files
   - Dashboard generation: <10 seconds after scan complete
   - Architecture graph rendering: <2 seconds for 500 nodes
   - Tab switching: <500ms transition animation
   - WebSocket latency: <100ms from event to UI update

2. **Scalability Limits**
   - Maximum nodes in dependency graph: 1,000 (above this, use clustered view)
   - Maximum files analyzed: 100,000 (progressive crawling with sampling)
   - Dashboard file size: <5MB (compressed assets)
   - Memory usage during scan: <500MB per 10K files
   - Concurrent WebSocket connections: 50 maximum

3. **Browser Compatibility**
   - Modern browsers only (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
   - No IE11 support (D3.js v7 requires ES6)
   - Mobile responsive design for tablets (iPad Air+)
   - No phone support (architecture graphs too complex)

4. **Data Freshness**
   - Real-time updates during active scan only
   - Post-scan: Dashboard static until next scan triggered
   - Incremental updates: Only changed files re-analyzed (SHA256 caching)

5. **Export Limitations**
   - PDF: Single page, paginated if content exceeds A4 height
   - PNG: 1920×1080 resolution maximum (higher causes memory issues)
   - PPTX: 10 slides maximum (Overview + 4 tabs + 5 detail slides)

**How do we MEASURE success?**

### Quantitative Metrics

1. **Feature Completeness**
   - **Baseline:** 70% complete (as of Nov 29, 2025)
   - **Target:** 95% complete (5% reserved for polish/edge cases)
   - **Measurement:** Count implemented features vs planned features in this document

2. **Performance Benchmarks**
   - **Baseline:** Overview scan ~45 seconds (unoptimized)
   - **Target:** <30 seconds (33% improvement via multi-threading)
   - **Measurement:** Median scan time across 10 test repositories (5K-50K files)

3. **User Engagement (Demo Audience)**
   - **Baseline:** No existing metric (new feature demonstration)
   - **Target:** 80% of audience asks follow-up questions (engagement indicator)
   - **Measurement:** Post-demo surveys and Q&A participation

4. **Dashboard Generation Speed**
   - **Baseline:** Unknown (not benchmarked)
   - **Target:** <10 seconds from scan complete to dashboard URL returned
   - **Measurement:** Median generation time across 10 test repositories

5. **Code Quality (Clean Architecture Compliance)**
   - **Target:** 90% compliance with CORTEX rulebook principles
   - **Measurement:** System alignment validation score for dashboard site code

### Qualitative Metrics

6. **Visual Appeal**
   - **Target:** "Modern, professional, exceeds expectations"
   - **Measurement:** External reviewer ratings (1-5 scale) on:
     - Color scheme consistency
     - Chart readability
     - Animation smoothness
     - Overall aesthetic

7. **Usability**
   - **Target:** "Intuitive, no training required"
   - **Measurement:** First-time user can navigate to Architecture tab and drill down into component within 60 seconds

8. **Accuracy**
   - **Target:** "Dependency graphs match manual code review"
   - **Measurement:** Spot-check 10 randomly selected edges in dependency graph against actual import statements

**What files/services MUST exist before starting?**

### Prerequisites (All Exist)

✅ **Scanners/Crawlers**
- `src/crawlers/crawler_orchestrator.py` - File system crawler
- `src/crawlers/dependency_crawler.py` - Dependency graph builder
- `src/analyzers/python_analyzer.py` - Python AST analysis
- `src/analyzers/csharp_analyzer.py` - C# code analysis
- `src/analyzers/javascript_analyzer.py` - JS/TS analysis

✅ **Orchestrators**
- `src/orchestrators/application_health_orchestrator.py` - Main coordinator
- `src/operations/onboarding_orchestrator.py` - User-facing entry point

✅ **Data Transformation**
- `src/operations/dashboard_data_adapter.py` - Analyzer output → Dashboard JSON

✅ **Dashboard Generation**
- `src/orchestrators/dashboard_generator.py` - HTML generation
- `templates/dashboard_template.html` - Jinja2 template base

✅ **Tier 3 Database**
- `cortex-brain/tier3-development-context.db` - Metrics storage

✅ **Configuration**
- `cortex-brain/operations-config.yaml` - Dashboard configuration

### New Files Required

❌ **Architecture Components** (To Be Created)
- `src/visualization/dependency_graph_builder.py` - D3.js JSON generator
- `src/visualization/component_diagram_builder.py` - Hierarchy visualization
- `static/js/architecture_tab.js` - Interactive graph controller
- `static/js/websocket_client.js` - Real-time update handler

❌ **Tab Controllers** (To Be Created)
- `static/js/tab_controller.js` - Tab navigation and routing
- `static/js/quality_tab.js` - Code quality visualization
- `static/js/security_tab.js` - Vulnerability dashboard
- `static/js/recommendations_tab.js` - Action item prioritization

❌ **Clean Architecture Layers** (To Be Created)
- `src/dashboard/presentation/` - UI components (read-only)
- `src/dashboard/use_cases/` - Tab controllers, navigation logic
- `src/dashboard/domain/` - Business entities (health score, component, issue)
- `src/dashboard/data/` - JSON adapters, database access

❌ **Export Modules** (To Be Created)
- `src/exporters/pptx_exporter.py` - PowerPoint generation

❌ **WebSocket Server** (To Be Created)
- `src/services/websocket_server.py` - Real-time event broadcaster
- `src/services/scan_progress_emitter.py` - Progress updates during crawl

**What security risks exist?**

### OWASP Top 10 Relevance Assessment

Given this is a **local, offline dashboard generation tool** (not a web service), most OWASP risks are LOW. However:

#### A01 - Broken Access Control ⚠️ MEDIUM RISK

**Risk:** If dashboard HTML files are generated in world-readable locations, sensitive code insights (file paths, function names, internal architecture) could leak.

**Mitigation:**
- Generate dashboards in `cortex-brain/documents/analysis/dashboards/` (excluded from git via .gitignore)
- Set file permissions to user-only (chmod 600 on Unix)
- Add warning banner in dashboard HTML: "Contains sensitive codebase information - do not share publicly"

#### A02 - Cryptographic Failures ✅ LOW RISK

**Risk:** Dashboard contains no encrypted data, no passwords, no API keys.

**Mitigation:** N/A (no sensitive data encrypted)

#### A03 - Injection ⚠️ MEDIUM RISK

**Risk:** User-provided application paths, file names, or code snippets rendered in HTML could contain XSS payloads.

**Example Attack:** Application path contains `<script>alert('XSS')</script>`, rendered in dashboard without escaping.

**Mitigation:**
- Use Jinja2 autoescaping (enabled by default) for all template variables
- Sanitize file paths before rendering (strip `<`, `>`, `"`, `'` characters)
- Use `textContent` instead of `innerHTML` in JavaScript
- **Validation Test:** Attempt to onboard application with malicious path name

#### A04 - Insecure Design ⚠️ MEDIUM RISK

**Risk:** WebSocket server (if implemented) accepts connections without authentication, allowing unauthorized users to receive live scan updates.

**Mitigation:**
- WebSocket server binds to `localhost:8080` only (no external access)
- Require secret token in WebSocket handshake (generated per scan session)
- Token expires after scan completes

#### A05 - Security Misconfiguration ✅ LOW RISK

**Risk:** Default configuration exposes sensitive settings.

**Mitigation:**
- No default credentials (no authentication required for local tool)
- Dashboard paths configurable via `cortex.config.json`
- Default to secure settings (no public access)

#### A06 - Vulnerable and Outdated Components ⚠️ HIGH RISK

**Risk:** Using outdated D3.js, Chart.js, or Socket.IO with known vulnerabilities.

**Mitigation:**
- Pin dependencies to specific versions in `requirements.txt` and `package.json`
- Run `npm audit` and `pip check` in CI/CD pipeline
- Auto-update checker warns if dependencies >6 months old
- **Action:** Document current versions in requirements

#### A07 - Identification and Authentication Failures ✅ LOW RISK

**Risk:** No authentication system (local tool)

**Mitigation:** N/A (no login required)

#### A08 - Software and Data Integrity Failures ⚠️ MEDIUM RISK

**Risk:** Dashboard generation scripts modified by attacker, injecting malicious code into generated HTML.

**Mitigation:**
- Code signing for dashboard_generator.py (SHA256 hash validation)
- Immutable templates (read-only file permissions)
- Validation: Compare generated HTML against trusted template baseline

#### A09 - Security Logging and Monitoring Failures ✅ LOW RISK

**Risk:** No logging of dashboard access (local tool, single user)

**Mitigation:**
- Log dashboard generation events to `logs/dashboard_generation.log`
- Include timestamp, application scanned, dashboard path
- No PII logged (file paths anonymized in logs)

#### A10 - Server-Side Request Forgery (SSRF) ✅ LOW RISK

**Risk:** No external requests (offline tool)

**Mitigation:** N/A (no HTTP requests to external services)

### Summary Table

| OWASP Category | Risk Level | Mitigation Priority | Estimated Effort |
|----------------|------------|-------------------|------------------|
| A01 - Access Control | ⚠️ MEDIUM | HIGH | 1 hour (permissions) |
| A03 - Injection (XSS) | ⚠️ MEDIUM | HIGH | 2 hours (escaping) |
| A04 - Insecure Design | ⚠️ MEDIUM | MEDIUM | 3 hours (auth) |
| A06 - Vulnerable Deps | ⚠️ HIGH | HIGH | 1 hour (audit) |
| A08 - Data Integrity | ⚠️ MEDIUM | LOW | 2 hours (hashing) |
| Others | ✅ LOW | N/A | - |

**Total Security Effort:** 9 hours across 3 sprints

---

## 🔒 Definition of Done (DoD) Checklist

### Code Complete

- [ ] All 5 tabs implemented (Overview, Architecture, Quality, Security, Recommendations)
- [ ] Dependency graph integration wired into ApplicationHealthOrchestrator
- [ ] Clean architecture layers created (presentation, use_cases, domain, data)
- [ ] WebSocket server functional with real-time progress updates
- [ ] PPTX export module implemented
- [ ] Multi-threading crawler orchestrator (100-worker pool)

### Testing

- [ ] Unit tests for all new modules (≥80% coverage)
- [ ] Integration test: Full onboarding workflow → dashboard generation
- [ ] Performance test: 50K file repository completes in <2 minutes (standard scan)
- [ ] Security test: XSS payload in file path does NOT execute in dashboard
- [ ] Browser compatibility test: Chrome, Firefox, Safari, Edge (latest versions)
- [ ] Export test: PDF/PNG/PPTX generation completes without errors

### Documentation

- [ ] User guide created: `cortex-brain/documents/implementation-guides/onboarding-dashboard-guide.md`
- [ ] Architecture diagram added to guide (clean architecture layers)
- [ ] API documentation for new classes (docstrings + examples)
- [ ] Update CORTEX.prompt.md with new dashboard commands
- [ ] Response template added to `cortex-brain/response-templates.yaml`

### Security

- [ ] OWASP checklist validated (all MEDIUM+ risks mitigated)
- [ ] Dependency audit passed (`npm audit`, `pip check`)
- [ ] Code signing implemented for dashboard generator
- [ ] File permissions set to user-only for generated dashboards

### Deployment Ready

- [ ] Feature flag added to `cortex.config.json` (enable/disable new dashboard)
- [ ] Rollback procedure documented (how to revert to old dashboard)
- [ ] Migration script for existing dashboard users
- [ ] Performance benchmarks documented in implementation guide

### User Acceptance

- [ ] Demo completed with external reviewers (visual appeal rating ≥4/5)
- [ ] First-time user test: Navigate to Architecture tab within 60 seconds
- [ ] Accuracy validation: 10 random dependency edges match code review

---

## 🚀 Phase Breakdown (3 Sprints, 12 Tasks)

### Overview

**Total Duration:** 6 weeks (3 × 2-week sprints)  
**Effort Distribution:** 40% Phase 1, 35% Phase 2, 25% Phase 3  
**Risk Mitigation:** Deliver high-value features first (architecture tab) for early demo capability

---

### Phase 1: Foundation & Quick Wins (Sprint 1 - 2 weeks)

**Goal:** Deliver demonstrable architecture visualization and complete tab structure  
**Demo Readiness:** 85% (can show impressive architecture graphs to audience)

#### Task 1.1: Integrate DependencyGraph into Dashboard Workflow ⭐ HIGH PRIORITY

**Description:** Wire existing DependencyGraph class into ApplicationHealthOrchestrator so architecture data flows to dashboard generation.

**Current State:** DependencyGraph exists in `src/crawlers/dependency_crawler.py` but only used in code review workflow. NOT connected to onboarding dashboard.

**Implementation Steps:**
1. Modify `ApplicationHealthOrchestrator.execute()` to call `DependencyGraph.build()` after crawler finishes
2. Extract node/edge JSON format from DependencyGraph output
3. Pass architecture data to `DashboardDataAdapter.transform()`
4. Update adapter to include `architecture_graph` key in dashboard JSON

**Acceptance Criteria:**
- DependencyGraph builds successfully for Python, JavaScript, C# projects
- Dashboard JSON includes `nodes` array (components) and `edges` array (imports)
- At least 90% of actual imports appear in graph (validated via spot-check)

**Estimated Effort:** 4 hours (2 hours coding, 1 hour testing, 1 hour validation)

**Dependencies:** None (self-contained)

**Risk:** Low (existing code integration, no new algorithms)

---

#### Task 1.2: Create Architecture Tab with D3.js Force-Directed Graph ⭐ HIGH PRIORITY

**Description:** Add new "Architecture" tab to dashboard with interactive dependency graph visualization using D3.js force simulation.

**Current State:** Only "Overview" tab exists. No architecture visualization.

**Implementation Steps:**
1. Create `static/js/architecture_tab.js` with D3.js v7 force simulation
2. Implement node coloring by health score (green = healthy, yellow = warning, red = critical)
3. Add zoom/pan controls with mouse wheel and drag
4. Add tooltips showing component name, LOC, dependency count on hover
5. Update `templates/dashboard_template.html` to include Architecture tab container

**Acceptance Criteria:**
- Graph renders 500 nodes in <2 seconds (performance target)
- Clicking node shows details panel (name, file path, metrics)
- Zoom from 0.5x to 3x magnification without lag
- Tooltip appears within 100ms of hover

**Estimated Effort:** 6 hours (4 hours D3.js coding, 2 hours interactivity)

**Dependencies:** Task 1.1 (needs architecture data)

**Risk:** Medium (D3.js complexity, performance optimization)

---

#### Task 1.3: Complete 5-Tab Structure (Overview, Architecture, Quality, Security, Recommendations)

**Description:** Build remaining 3 tabs with placeholder content and tab navigation system.

**Current State:** Only Overview tab exists (100% complete).

**Implementation Steps:**
1. Create `static/js/tab_controller.js` for tab switching logic
2. Build Quality tab structure (code smells, complexity charts)
3. Build Security tab structure (vulnerability list, OWASP mapping)
4. Build Recommendations tab structure (prioritized action items)
5. Add tab state persistence (URL hash: `#/architecture`, `#/quality`)

**Tab Specifications:**

**Quality Tab:**
- Code smell breakdown pie chart (D3.js)
- Complexity distribution histogram (Chart.js)
- Test coverage gauge (Chart.js radial gauge)
- Top 10 most complex files table

**Security Tab:**
- OWASP Top 10 mapping table
- Vulnerability severity breakdown (Critical, High, Medium, Low)
- Affected files list with line numbers
- CWE reference links

**Recommendations Tab:**
- Priority matrix (impact vs. effort quadrant chart)
- Action items with fix templates (copy-paste code snippets)
- Estimated time to fix per item
- "Quick wins" filter (show items < 1 hour effort)

**Acceptance Criteria:**
- All 5 tabs render without errors
- Tab switching completes in <500ms (animation included)
- Browser back/forward navigation works with tabs (URL hash routing)
- Tab state persists on page refresh

**Estimated Effort:** 8 hours (2 hours per new tab + 2 hours controller)

**Dependencies:** None (can work in parallel with Tasks 1.1-1.2)

**Risk:** Low (basic HTML/CSS/JS, no complex algorithms)

---

#### Task 1.4: Multi-Threading Crawler Orchestrator

**Description:** Replace single-threaded file crawler with multi-threaded implementation using ThreadPoolExecutor (100 workers).

**Current State:** CrawlerOrchestrator processes files sequentially (SLOW for large repos).

**Implementation Steps:**
1. Create `ThreadPoolExecutor` with 100 worker threads in `CrawlerOrchestrator.__init__()`
2. Submit file analysis tasks to executor in batches of 1000 files
3. Implement progress callback for live status updates
4. Add thread-safe result aggregation (use `threading.Lock` for shared state)
5. Benchmark performance improvement (expect 10-20x speedup)

**Acceptance Criteria:**
- 50K file repository completes standard scan in <2 minutes (baseline: ~45 seconds)
- No race conditions in result aggregation (validated via 10 test runs)
- Progress updates show accurate percentage completion
- Memory usage stays <500MB during scan

**Estimated Effort:** 6 hours (3 hours coding, 2 hours testing, 1 hour optimization)

**Dependencies:** None (internal crawler improvement)

**Risk:** Medium (threading complexity, race condition debugging)

---

**Phase 1 Summary:**
- **Total Effort:** 24 hours (3 developer-days)
- **Demo Impact:** HIGH (architecture visualization is the "wow" factor)
- **Deliverables:** Architecture tab, 5-tab structure, 10-20x performance improvement
- **Sprint Review Demo:** Show live architecture graph generation in 30 seconds

---

### Phase 2: Clean Architecture & Real-Time Updates (Sprint 2 - 2 weeks)

**Goal:** Refactor dashboard codebase to follow CORTEX rulebook principles and add WebSocket live updates  
**Code Quality:** 90% clean architecture compliance (measured via System Alignment)

#### Task 2.1: Refactor Dashboard into Clean Architecture Layers

**Description:** Reorganize dashboard code into presentation/use_cases/domain/data layers following SOLID principles.

**Current State:** Dashboard code mixed in single directory (violates separation of concerns).

**New Directory Structure:**
```
src/dashboard/
├── presentation/           # UI components (read-only HTML/CSS/JS)
│   ├── templates/
│   │   ├── overview_tab.html
│   │   ├── architecture_tab.html
│   │   ├── quality_tab.html
│   │   ├── security_tab.html
│   │   └── recommendations_tab.html
│   └── static/
│       ├── css/dashboard.css
│       └── js/
│           ├── tab_controller.js
│           ├── architecture_tab.js
│           ├── quality_tab.js
│           ├── security_tab.js
│           └── recommendations_tab.js
├── use_cases/              # Tab controllers (business logic)
│   ├── load_overview.py
│   ├── render_architecture_graph.py
│   ├── analyze_quality_metrics.py
│   ├── scan_security_vulnerabilities.py
│   └── generate_recommendations.py
├── domain/                 # Business entities (pure Python)
│   ├── health_score.py     # Health calculation logic
│   ├── component.py        # Component model (name, path, metrics)
│   ├── dependency.py       # Dependency edge model
│   ├── issue.py            # Code smell/vulnerability model
│   └── recommendation.py   # Action item model
└── data/                   # Data access (JSON adapters, DB queries)
    ├── dashboard_data_adapter.py  # Existing adapter
    ├── architecture_repository.py
    ├── metrics_repository.py
    └── tier3_query_service.py
```

**SOLID Principles Applied:**

1. **Single Responsibility:** Each use case handles ONE tab's logic
2. **Open/Closed:** New tabs added without modifying existing code
3. **Liskov Substitution:** All repositories implement `RepositoryInterface`
4. **Interface Segregation:** Separate interfaces for read/write operations
5. **Dependency Inversion:** Use cases depend on interfaces, not concrete adapters

**Implementation Steps:**
1. Create directory structure above
2. Extract business logic from `dashboard_generator.py` into use cases
3. Define domain entities (HealthScore, Component, Dependency, Issue)
4. Implement repositories with interface-based design
5. Update orchestrator to call use cases instead of generator directly
6. Validate with System Alignment tool (target: 90% score)

**Acceptance Criteria:**
- System Alignment score ≥90% for dashboard code
- All imports follow dependency inversion (use_cases → domain ← data)
- Unit tests pass with mocked repositories (proves testability)
- No circular dependencies detected by `DependencyGraph`

**Estimated Effort:** 12 hours (6 hours refactoring, 4 hours testing, 2 hours validation)

**Dependencies:** None (refactoring can happen independently)

**Risk:** High (large refactor, risk of breaking existing functionality)

**Mitigation:** Create git checkpoint before refactoring, run full test suite after each layer extracted

---

#### Task 2.2: Implement WebSocket Real-Time Updates

**Description:** Add WebSocket server and client for live progress updates during scans (no page refresh needed).

**Current State:** Static dashboard, user must manually refresh to see updated health scores.

**Implementation Steps:**
1. Create `src/services/websocket_server.py` using Socket.IO
2. Implement event emitter in CrawlerOrchestrator: `emit('scan_progress', {percentage: 45})`
3. Create `static/js/websocket_client.js` for browser connection
4. Add progress bar overlay to dashboard UI (Chart.js animated bar)
5. Implement reconnection logic if WebSocket drops

**WebSocket Events:**
- `scan_started` - Emitted when crawler begins
- `scan_progress` - Emitted every 1000 files (payload: `{files_processed: 10000, total_files: 50000}`)
- `analysis_complete` - Emitted when analyzer finishes (payload: `{issues_found: 150}`)
- `dashboard_ready` - Emitted when HTML generation completes (payload: `{url: '/dashboards/dashboard-latest.html'}`)

**Acceptance Criteria:**
- WebSocket connects within 500ms of dashboard load
- Progress bar updates every second during scan (smooth animation)
- Dashboard auto-refreshes when `dashboard_ready` event received
- WebSocket reconnects automatically if connection lost

**Estimated Effort:** 8 hours (4 hours server, 3 hours client, 1 hour testing)

**Dependencies:** None (WebSocket layer separate from existing code)

**Risk:** Medium (async programming complexity, connection handling)

---

#### Task 2.3: Enhance IntegrationScorer for Per-Component Health

**Description:** Extend IntegrationScorer to calculate health scores at component level (not just system-wide) for color-coded architecture graphs.

**Current State:** IntegrationScorer provides system-level health (0-100%). No per-component granularity.

**Implementation Steps:**
1. Modify IntegrationScorer to accept component name parameter
2. Calculate 7-layer score per component (discovery, import, instantiation, docs, tests, wiring, optimization)
3. Output component-health mapping: `{"auth_service.py": 85, "payment_api.py": 72}`
4. Pass component health to D3.js graph for node coloring

**Health Score to Color Mapping:**
- 90-100: `#28a745` (green - healthy)
- 70-89: `#ffc107` (yellow - warning)
- 0-69: `#dc3545` (red - critical)

**Acceptance Criteria:**
- Each component in dependency graph has health score
- Node color matches health category (green/yellow/red)
- Tooltip shows health breakdown (7 layers)
- System alignment validation passes

**Estimated Effort:** 4 hours (2 hours scorer modification, 2 hours graph integration)

**Dependencies:** Task 1.2 (needs architecture graph rendering)

**Risk:** Low (extending existing scorer)

---

**Phase 2 Summary:**
- **Total Effort:** 24 hours (3 developer-days)
- **Code Quality Impact:** HIGH (90% clean architecture compliance)
- **Deliverables:** Clean architecture refactor, WebSocket real-time updates, per-component health
- **Sprint Review Demo:** Show live scan progress bar updating in real-time

---

### Phase 3: Export & Polish (Sprint 3 - 2 weeks)

**Goal:** Complete export functionality, performance optimization, and visual polish  
**Production Readiness:** 95% (ready for public demonstrations)

#### Task 3.1: Implement PPTX Export

**Description:** Add PowerPoint export functionality with 10-slide deck (overview + 4 tabs + 5 detail slides).

**Current State:** PDF and PNG export exist. PPTX missing (requested by users for presentations).

**Implementation Steps:**
1. Install `python-pptx` library
2. Create `src/exporters/pptx_exporter.py` module
3. Define slide templates:
   - Slide 1: Title (application name, scan date)
   - Slide 2: Overview (health score, file counts, language breakdown)
   - Slide 3: Architecture (dependency graph screenshot)
   - Slide 4: Quality (code smell chart, complexity histogram)
   - Slide 5: Security (vulnerability table, OWASP mapping)
   - Slide 6: Recommendations (top 5 action items)
   - Slides 7-10: Deep dive detail slides (most complex files, critical vulnerabilities, etc.)
4. Add export button to dashboard UI (PowerPoint icon)

**Acceptance Criteria:**
- PPTX file generates in <15 seconds
- All charts render as high-resolution images (300 DPI)
- Slides follow professional template (consistent fonts, colors)
- File size <10MB (compressed images)

**Estimated Effort:** 6 hours (4 hours PPTX generation, 2 hours UI integration)

**Dependencies:** All tabs complete (needs content for all slides)

**Risk:** Low (library handles complexity)

---

#### Task 3.2: Performance Optimization Pass

**Description:** Profile and optimize slow operations (graph rendering, large file scans, export generation).

**Current State:** Some operations slower than target (architecture graph >2s for 500 nodes).

**Optimization Targets:**
1. **D3.js Graph Rendering** - Target: <2s for 500 nodes
   - Implement node clustering for graphs >500 nodes
   - Use Web Workers for force simulation calculations
   - Lazy load node details on demand

2. **Crawler Performance** - Target: <2 minutes for 50K files
   - Optimize file I/O with memory-mapped files
   - Cache SHA256 hashes to skip unchanged files
   - Batch database inserts (1000 rows at a time)

3. **Export Generation** - Target: <10s for PDF/PNG/PPTX
   - Parallelize chart rendering with ThreadPoolExecutor
   - Cache rendered chart images (SHA256-based)
   - Compress images before embedding in exports

**Acceptance Criteria:**
- All performance targets met (validated via benchmark suite)
- Memory usage <500MB for 50K file scan
- No performance regressions in existing features

**Estimated Effort:** 8 hours (4 hours profiling, 4 hours optimization)

**Dependencies:** All features complete (can't optimize incomplete code)

**Risk:** Medium (optimization can introduce bugs)

---

#### Task 3.3: Visual Polish & UX Improvements

**Description:** Final design pass for professional appearance (colors, animations, responsive layout).

**Current State:** Functional but basic styling. Needs polish for "wow factor" demonstrations.

**Polish Checklist:**
1. **Color Scheme** - Consistent brand colors throughout
   - Primary: `#007bff` (blue)
   - Success: `#28a745` (green)
   - Warning: `#ffc107` (yellow)
   - Danger: `#dc3545` (red)

2. **Animations** - Smooth transitions
   - Tab switching: 300ms ease-in-out
   - Graph node hover: 150ms scale transform
   - Progress bar: Animated gradient fill

3. **Responsive Layout** - Tablet support
   - Architecture graph scales to viewport
   - Tables stack vertically on narrow screens
   - Charts resize dynamically

4. **Accessibility** - WCAG 2.1 Level AA
   - All charts have alt text
   - Color contrast ratio ≥4.5:1
   - Keyboard navigation for all interactive elements

5. **Loading States** - Clear feedback
   - Skeleton screens while loading data
   - Spinners for long operations
   - Empty state messages ("No vulnerabilities found")

**Acceptance Criteria:**
- External reviewer rating ≥4/5 for visual appeal
- Passes WAVE accessibility checker
- Works on iPad Air (768px width)

**Estimated Effort:** 6 hours (CSS refinements, animation tweaks)

**Dependencies:** All features complete

**Risk:** Low (cosmetic changes)

---

#### Task 3.4: Documentation & User Guide

**Description:** Create comprehensive user guide and update CORTEX entry point documentation.

**Deliverables:**
1. **User Guide:** `cortex-brain/documents/implementation-guides/onboarding-dashboard-guide.md`
   - Getting started (onboard application in 3 commands)
   - Tab explanations (what each tab shows)
   - Export instructions (PDF, PNG, PPTX)
   - Troubleshooting common issues

2. **Architecture Documentation**
   - Clean architecture diagram (Mermaid)
   - Component interaction flowchart
   - Data flow from crawler → dashboard

3. **API Documentation**
   - Docstrings for all public classes
   - Usage examples for each use case
   - Integration guide for custom analyzers

4. **Update CORTEX.prompt.md**
   - Add dashboard commands to help table
   - Link to onboarding-dashboard-guide.md
   - Add demo scenario examples

5. **Response Template**
   - Add `onboarding_dashboard` template to `response-templates.yaml`

**Acceptance Criteria:**
- All new classes have docstrings with examples
- User guide tested by external reviewer (completeness validation)
- CORTEX.prompt.md updated with dashboard section
- Response template renders correctly

**Estimated Effort:** 4 hours (documentation writing)

**Dependencies:** All features complete

**Risk:** None (documentation)

---

**Phase 3 Summary:**
- **Total Effort:** 24 hours (3 developer-days)
- **Production Impact:** HIGH (ready for public demonstrations)
- **Deliverables:** PPTX export, performance optimization, visual polish, complete documentation
- **Sprint Review Demo:** Full demonstration with all 5 tabs, real-time updates, professional polish

---

### Implementation Timeline

```
Week 1-2 (Sprint 1): Foundation & Quick Wins
├─ Task 1.1: DependencyGraph integration [4h]
├─ Task 1.2: Architecture tab D3.js [6h]
├─ Task 1.3: 5-tab structure [8h]
└─ Task 1.4: Multi-threading crawler [6h]
   Total: 24 hours

Week 3-4 (Sprint 2): Clean Architecture & Real-Time
├─ Task 2.1: Clean architecture refactor [12h]
├─ Task 2.2: WebSocket real-time updates [8h]
└─ Task 2.3: Per-component health scoring [4h]
   Total: 24 hours

Week 5-6 (Sprint 3): Export & Polish
├─ Task 3.1: PPTX export [6h]
├─ Task 3.2: Performance optimization [8h]
├─ Task 3.3: Visual polish [6h]
└─ Task 3.4: Documentation [4h]
   Total: 24 hours

Grand Total: 72 hours (9 developer-days)
```

**Risk Buffer:** 8 hours (10% contingency) for unexpected issues  
**Total Project:** 80 hours = 2 full-time weeks OR 4 part-time weeks

---

## 🏗️ Technical Architecture (Clean Architecture + SOLID Principles)

### Architecture Philosophy

**CORTEX Rulebook Compliance:** "The site that you build for data visualization should itself follow the clean architecture and best practice principles."

**Key Principles:**
- **Separation of Concerns:** UI/Business Logic/Data Access isolated
- **Dependency Inversion:** High-level modules don't depend on low-level modules
- **Testability:** Each layer testable independently with mocks
- **SOLID Enforcement:** Validated via System Alignment (target: 90% score)

---

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  (UI Components - Read-Only HTML/CSS/JS)                        │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Overview Tab │  │Architecture  │  │ Quality Tab  │  ...    │
│  │ (HTML/CSS/JS)│  │Tab (D3.js)   │  │(Chart.js)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         ▲                 ▲                  ▲                   │
└─────────┼─────────────────┼──────────────────┼──────────────────┘
          │                 │                  │
          │    Use Case     │     Interface    │
          │                 │                  │
┌─────────┼─────────────────┼──────────────────┼──────────────────┐
│         ▼        USE CASES LAYER             ▼                   │
│  (Business Logic - Tab Controllers)                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │LoadOverview  │  │RenderArch    │  │AnalyzeQuality│  ...    │
│  │UseCase       │  │GraphUseCase  │  │UseCase       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         ▲                 ▲                  ▲                   │
└─────────┼─────────────────┼──────────────────┼──────────────────┘
          │                 │                  │
          │    Domain       │     Entities     │
          │                 │                  │
┌─────────┼─────────────────┼──────────────────┼──────────────────┐
│         ▼          DOMAIN LAYER              ▼                   │
│  (Business Entities - Pure Python)                              │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │HealthScore   │  │ Component    │  │ Dependency   │  ...    │
│  │(calculation) │  │(name,path)   │  │(edge model)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         ▲                 ▲                  ▲                   │
└─────────┼─────────────────┼──────────────────┼──────────────────┘
          │                 │                  │
          │   Repository    │    Interfaces    │
          │                 │                  │
┌─────────┼─────────────────┼──────────────────┼──────────────────┐
│         ▼           DATA LAYER               ▼                   │
│  (Data Access - JSON Adapters, DB Queries)                      │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Architecture  │  │Metrics       │  │Tier3Query    │  ...    │
│  │Repository    │  │Repository    │  │Service       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         ▲                 ▲                  ▲                   │
└─────────┼─────────────────┼──────────────────┼──────────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
     ┌────────┐      ┌────────┐        ┌────────┐
     │  JSON  │      │Tier 3  │        │ Files  │
     │  Data  │      │   DB   │        │ (LOC)  │
     └────────┘      └────────┘        └────────┘
```

**Dependency Flow:** Presentation → Use Cases → Domain ← Data (repositories implement domain interfaces)

---

### Directory Structure (Target State - Phase 2)

```
src/dashboard/
├── presentation/                    # Layer 1: UI Components
│   ├── templates/
│   │   ├── dashboard_base.html      # Base template with header/footer
│   │   ├── overview_tab.html        # Overview metrics and charts
│   │   ├── architecture_tab.html    # D3.js force-directed graph
│   │   ├── quality_tab.html         # Code smell charts
│   │   ├── security_tab.html        # Vulnerability table
│   │   └── recommendations_tab.html # Action items
│   └── static/
│       ├── css/
│       │   ├── dashboard.css        # Global dashboard styles
│       │   ├── architecture.css     # D3.js graph styling
│       │   └── charts.css           # Chart.js styling
│       └── js/
│           ├── tab_controller.js    # Tab navigation logic
│           ├── websocket_client.js  # Real-time updates
│           ├── architecture_tab.js  # D3.js force simulation
│           ├── quality_tab.js       # Chart.js quality metrics
│           ├── security_tab.js      # Vulnerability filtering
│           └── recommendations_tab.js # Priority matrix
│
├── use_cases/                       # Layer 2: Business Logic
│   ├── __init__.py
│   ├── load_overview.py             # LoadOverviewUseCase
│   ├── render_architecture_graph.py # RenderArchGraphUseCase
│   ├── analyze_quality_metrics.py   # AnalyzeQualityUseCase
│   ├── scan_security_vulnerabilities.py # ScanSecurityUseCase
│   └── generate_recommendations.py  # GenerateRecommendationsUseCase
│
├── domain/                          # Layer 3: Business Entities
│   ├── __init__.py
│   ├── entities/
│   │   ├── health_score.py          # HealthScore value object
│   │   ├── component.py             # Component entity (name, path, metrics)
│   │   ├── dependency.py            # Dependency edge (source, target, type)
│   │   ├── issue.py                 # Issue entity (type, severity, location)
│   │   └── recommendation.py        # Recommendation (action, priority, effort)
│   └── interfaces/
│       ├── repository_interface.py  # Base repository contract
│       ├── architecture_repository.py # Architecture data contract
│       ├── metrics_repository.py    # Metrics data contract
│       └── tier3_service.py         # Tier 3 query contract
│
└── data/                            # Layer 4: Data Access
    ├── __init__.py
    ├── adapters/
    │   ├── dashboard_data_adapter.py # JSON adapter (existing)
    │   ├── architecture_repository_impl.py # Architecture repo implementation
    │   ├── metrics_repository_impl.py # Metrics repo implementation
    │   └── tier3_query_service_impl.py # Tier 3 service implementation
    └── models/
        ├── dashboard_json_model.py  # JSON schema models
        └── tier3_query_model.py     # SQL query models
```

**File Count:**
- **Current:** ~10 files in mixed structure
- **Target:** ~35 files in clean architecture (3.5x increase, but each file < 200 lines)

---

### SOLID Principles Applied

#### 1. Single Responsibility Principle (SRP)

**Before (Violates SRP):**
```python
# dashboard_generator.py - Does EVERYTHING (600+ lines)
class DashboardGenerator:
    def generate(self, data):
        # Load data from JSON ❌
        # Calculate health scores ❌
        # Query Tier 3 database ❌
        # Render HTML ❌
        # Generate charts ❌
        # Export to PDF/PNG ❌
```

**After (Follows SRP):**
```python
# use_cases/load_overview.py - ONE responsibility
class LoadOverviewUseCase:
    def __init__(self, metrics_repo: MetricsRepository):
        self._metrics_repo = metrics_repo  # Dependency injection
    
    def execute(self) -> OverviewData:
        """Load overview metrics for dashboard."""
        raw_data = self._metrics_repo.get_latest_scan()
        health = HealthScore.calculate(raw_data)  # Domain logic
        return OverviewData(health=health, metrics=raw_data)
```

**Benefits:**
- Each class has ONE reason to change
- 200-line files instead of 600-line monoliths
- Easy to test (mock repository)

---

#### 2. Open/Closed Principle (OCP)

**Extension Point:** New tabs added without modifying existing code

```python
# domain/interfaces/tab_use_case.py
class TabUseCase(ABC):
    """Base interface for all tab use cases."""
    
    @abstractmethod
    def execute(self) -> TabData:
        """Execute use case and return tab data."""
        pass

# use_cases/new_custom_tab.py - Add new tab WITHOUT modifying existing code
class CustomTabUseCase(TabUseCase):
    def execute(self) -> TabData:
        # Custom tab logic here
        return TabData(...)
```

**Benefits:**
- Add new tabs without touching existing use cases
- Plugin architecture for custom analyzers
- No regression risk to existing tabs

---

#### 3. Liskov Substitution Principle (LSP)

**Repository Contracts:** All repositories implement same interface

```python
# domain/interfaces/repository_interface.py
class Repository(ABC):
    """Base repository contract."""
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Entity:
        pass
    
    @abstractmethod
    def save(self, entity: Entity) -> None:
        pass

# data/adapters/architecture_repository_impl.py
class ArchitectureRepositoryImpl(Repository):
    """JSON-based architecture repository."""
    
    def get_by_id(self, entity_id: str) -> Component:
        # Load from dashboard JSON
        pass

# data/adapters/tier3_architecture_repository.py
class Tier3ArchitectureRepository(Repository):
    """Tier 3 database-based repository."""
    
    def get_by_id(self, entity_id: str) -> Component:
        # Load from Tier 3 DB
        pass
```

**Benefits:**
- Use cases work with ANY repository implementation (JSON, DB, API)
- Swap data source without changing business logic
- Easy to add new data sources (e.g., cloud storage)

---

#### 4. Interface Segregation Principle (ISP)

**Fine-Grained Interfaces:** Clients only depend on methods they use

```python
# domain/interfaces/metrics_repository.py
class ReadOnlyMetricsRepository(ABC):
    """Read-only metrics access."""
    @abstractmethod
    def get_latest_scan(self) -> ScanData:
        pass

class WritableMetricsRepository(ReadOnlyMetricsRepository):
    """Read-write metrics access."""
    @abstractmethod
    def save_scan(self, scan: ScanData) -> None:
        pass

# use_cases/load_overview.py - Only needs read access
class LoadOverviewUseCase:
    def __init__(self, metrics_repo: ReadOnlyMetricsRepository):
        self._metrics_repo = metrics_repo  # Can't accidentally write
```

**Benefits:**
- Use cases can't accidentally modify data when only reading
- Interface documents intent (read vs write)
- Easier to implement (don't need unused methods)

---

#### 5. Dependency Inversion Principle (DIP)

**High-Level → Interfaces ← Low-Level**

```python
# ❌ BEFORE: Use case depends on concrete adapter (tight coupling)
from data.adapters.dashboard_data_adapter import DashboardDataAdapter

class LoadOverviewUseCase:
    def __init__(self):
        self._adapter = DashboardDataAdapter()  # Tight coupling

# ✅ AFTER: Use case depends on interface (loose coupling)
from domain.interfaces.metrics_repository import MetricsRepository

class LoadOverviewUseCase:
    def __init__(self, metrics_repo: MetricsRepository):
        self._metrics_repo = metrics_repo  # Loose coupling
    
    def execute(self) -> OverviewData:
        data = self._metrics_repo.get_latest_scan()  # Interface method
        return OverviewData(data)

# Orchestrator wires dependencies (dependency injection)
from data.adapters.metrics_repository_impl import MetricsRepositoryImpl

def create_overview_use_case() -> LoadOverviewUseCase:
    repo = MetricsRepositoryImpl()  # Concrete implementation
    return LoadOverviewUseCase(repo)  # Inject dependency
```

**Benefits:**
- Use cases testable with mock repositories
- Swap implementations without changing use cases
- Clear dependency graph (no circular dependencies)

---

### D3.js Force-Directed Graph Specification

**Library:** D3.js v7 (force simulation API)  
**Target Performance:** <2 seconds for 500 nodes  
**File:** `src/dashboard/presentation/static/js/architecture_tab.js`

#### Force Simulation Configuration

```javascript
// architecture_tab.js
class ArchitectureGraph {
    constructor(containerId, data) {
        this.container = d3.select(containerId);
        this.nodes = data.nodes;  // {id, name, health, loc}
        this.edges = data.edges;  // {source, target, type}
        this.width = container.node().offsetWidth;
        this.height = container.node().offsetHeight;
    }
    
    render() {
        // Force simulation with collision detection
        this.simulation = d3.forceSimulation(this.nodes)
            .force("link", d3.forceLink(this.edges)
                .id(d => d.id)
                .distance(100)  // Edge length
                .strength(0.3)) // Link stiffness
            .force("charge", d3.forceManyBody()
                .strength(-300)) // Node repulsion
            .force("center", d3.forceCenter(
                this.width / 2, 
                this.height / 2))
            .force("collision", d3.forceCollide()
                .radius(30));  // Prevent node overlap
        
        // Performance: Stop simulation after 300 ticks
        this.simulation.tick(300);
        this.simulation.stop();  // Pre-compute positions
        
        this.renderNodes();
        this.renderEdges();
        this.setupInteractivity();
    }
    
    renderNodes() {
        const nodes = this.svg.selectAll(".node")
            .data(this.nodes)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.x}, ${d.y})`);
        
        // Circle with health-based color
        nodes.append("circle")
            .attr("r", d => Math.sqrt(d.loc) / 10)  // Size by LOC
            .attr("fill", d => this.getHealthColor(d.health))
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);
        
        // Label (show for large components only)
        nodes.filter(d => d.loc > 1000)
            .append("text")
            .attr("dy", 25)
            .attr("text-anchor", "middle")
            .text(d => d.name)
            .style("font-size", "10px")
            .style("fill", "#333");
    }
    
    renderEdges() {
        this.svg.selectAll(".edge")
            .data(this.edges)
            .enter().append("line")
            .attr("class", "edge")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y)
            .attr("stroke", d => this.getEdgeColor(d.type))
            .attr("stroke-width", 1)
            .attr("stroke-opacity", 0.3);
    }
    
    setupInteractivity() {
        // Zoom & Pan
        const zoom = d3.zoom()
            .scaleExtent([0.5, 3])  // 0.5x to 3x magnification
            .on("zoom", (event) => {
                this.svg.attr("transform", event.transform);
            });
        this.container.call(zoom);
        
        // Tooltips
        this.svg.selectAll(".node")
            .on("mouseenter", (event, d) => {
                this.showTooltip(event, d);
            })
            .on("mouseleave", () => {
                this.hideTooltip();
            })
            .on("click", (event, d) => {
                this.showDetailsPanel(d);
            });
    }
    
    getHealthColor(health) {
        if (health >= 90) return "#28a745";  // Green
        if (health >= 70) return "#ffc107";  // Yellow
        return "#dc3545";  // Red
    }
    
    getEdgeColor(type) {
        return {
            "import": "#007bff",      // Blue (standard import)
            "circular": "#dc3545",    // Red (circular dependency)
            "external": "#6c757d"     // Gray (external library)
        }[type] || "#007bff";
    }
}
```

**Performance Optimizations:**

1. **Pre-compute Layout:** Run simulation to completion before rendering (300 ticks)
2. **Node Clustering:** For graphs >500 nodes, cluster small components
3. **Web Workers:** Offload force calculations to background thread
4. **Lazy Loading:** Load node details on click, not on page load
5. **Canvas Fallback:** Use Canvas API instead of SVG for >1000 nodes

**Acceptance Criteria:**
- 500 nodes render in <2 seconds (measured via `performance.now()`)
- Zoom/pan at 60 FPS (no janky animations)
- Tooltips appear within 100ms of hover

---

### Chart.js Real-Time Metrics Specification

**Library:** Chart.js v4 (responsive charts)  
**WebSocket Integration:** Socket.IO client for live updates  
**Files:** 
- `src/dashboard/presentation/static/js/quality_tab.js`
- `src/dashboard/presentation/static/js/websocket_client.js`

#### Quality Metrics Dashboard

```javascript
// quality_tab.js
class QualityMetricsChart {
    constructor(containerId, websocketClient) {
        this.container = document.getElementById(containerId);
        this.wsClient = websocketClient;
        this.chart = null;
    }
    
    initialize(data) {
        // Code smell breakdown pie chart
        this.chart = new Chart(this.container, {
            type: 'pie',
            data: {
                labels: data.smell_types,  // ["Long Method", "Large Class", ...]
                datasets: [{
                    data: data.smell_counts,  // [45, 32, 28, ...]
                    backgroundColor: [
                        '#dc3545',  // Red
                        '#ffc107',  // Yellow
                        '#28a745',  // Green
                        '#007bff',  // Blue
                        '#6c757d'   // Gray
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        // WebSocket listener for real-time updates
        this.wsClient.on('quality_updated', (newData) => {
            this.updateChart(newData);
        });
    }
    
    updateChart(newData) {
        this.chart.data.datasets[0].data = newData.smell_counts;
        this.chart.update('active');  // Smooth animation
    }
}

// websocket_client.js
class WebSocketClient {
    constructor(serverUrl) {
        this.socket = io(serverUrl);
        this.connectionStatus = 'disconnected';
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        this.socket.on('connect', () => {
            this.connectionStatus = 'connected';
            console.log('✅ WebSocket connected');
        });
        
        this.socket.on('disconnect', () => {
            this.connectionStatus = 'disconnected';
            console.log('⚠️ WebSocket disconnected');
            this.reconnect();
        });
        
        // Progress updates
        this.socket.on('scan_progress', (data) => {
            this.updateProgressBar(data.percentage);
        });
        
        // Dashboard ready
        this.socket.on('dashboard_ready', (data) => {
            this.reloadDashboard(data.url);
        });
    }
    
    reconnect() {
        setTimeout(() => {
            console.log('🔄 Reconnecting WebSocket...');
            this.socket.connect();
        }, 3000);  // Retry after 3 seconds
    }
    
    updateProgressBar(percentage) {
        const progressBar = document.getElementById('scan-progress');
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = `${percentage}%`;
    }
    
    reloadDashboard(url) {
        window.location.href = url;  // Auto-refresh
    }
    
    on(event, callback) {
        this.socket.on(event, callback);
    }
    
    emit(event, data) {
        this.socket.emit(event, data);
    }
}
```

**WebSocket Events:**

| Event | Direction | Payload | Purpose |
|-------|-----------|---------|---------|
| `scan_started` | Server → Client | `{files: 50000}` | Show progress overlay |
| `scan_progress` | Server → Client | `{percentage: 45}` | Update progress bar |
| `analysis_complete` | Server → Client | `{issues: 150}` | Hide progress overlay |
| `quality_updated` | Server → Client | `{smell_counts: [...]}` | Update quality chart |
| `dashboard_ready` | Server → Client | `{url: '/path'}` | Auto-refresh dashboard |

**Performance Targets:**
- WebSocket connection: <500ms
- Progress update frequency: Every 1 second
- Chart update animation: 300ms ease-in-out
- Memory: <50MB for WebSocket client

---

### Component Interaction Flow

**Scenario:** User opens dashboard and sees real-time scan progress

```
┌──────────────┐
│   Browser    │
│  (Client)    │
└──────┬───────┘
       │ 1. HTTP GET /dashboard
       ▼
┌──────────────────────┐
│  Flask Server        │
│  (Presentation)      │
└──────┬───────────────┘
       │ 2. Call use case
       ▼
┌──────────────────────┐
│ LoadOverviewUseCase  │
│ (Business Logic)     │
└──────┬───────────────┘
       │ 3. Query repository
       ▼
┌──────────────────────┐
│ MetricsRepository    │
│ (Data Access)        │
└──────┬───────────────┘
       │ 4. Load JSON
       ▼
┌──────────────────────┐
│  dashboard.json      │
│  (Data Source)       │
└──────────────────────┘

   (Dashboard loads in browser)

┌──────────────┐
│   Browser    │
│ (WebSocket)  │
└──────┬───────┘
       │ 5. Connect WebSocket
       ▼
┌──────────────────────┐
│ WebSocket Server     │
│ (Socket.IO)          │
└──────┬───────────────┘
       │ 6. Subscribe to events
       │
       │ (Scan starts)
       │
       │ 7. emit('scan_progress', {percentage: 25})
       ▼
┌──────────────┐
│   Browser    │
│ (Progress)   │ ← Updates progress bar in real-time
└──────────────┘
```

**Data Flow (Detailed):**

1. **HTTP Request** - Browser → Flask `/dashboard` endpoint
2. **Use Case Invocation** - Flask → `LoadOverviewUseCase.execute()`
3. **Repository Query** - Use Case → `MetricsRepository.get_latest_scan()`
4. **JSON Load** - Repository → Read `dashboard.json` from disk
5. **Domain Transformation** - Repository → Convert JSON to `OverviewData` entity
6. **Response Rendering** - Use Case → Return `OverviewData` to Flask
7. **HTML Generation** - Flask → Render `overview_tab.html` template
8. **Browser Display** - Flask → Send HTML to browser
9. **WebSocket Connection** - Browser JS → Connect to Socket.IO server
10. **Event Subscription** - Browser → Listen for `scan_progress` events
11. **Real-Time Updates** - Server → Emit progress events during scan
12. **Chart Updates** - Browser → Update Chart.js with new data

---

### Validation & Testing Strategy

**System Alignment Validation:**
```bash
# Run after Phase 2 refactor complete
python -m src.orchestrators.system_alignment_orchestrator --target dashboard

# Expected output:
# ✅ Single Responsibility: 100% (each use case has ONE job)
# ✅ Open/Closed: 100% (new tabs via inheritance)
# ✅ Liskov Substitution: 100% (repositories interchangeable)
# ✅ Interface Segregation: 100% (read/write interfaces separated)
# ✅ Dependency Inversion: 100% (use cases depend on interfaces)
# Overall Score: 100% (CORTEX Rulebook Compliant)
```

**Unit Testing (Mocked Repositories):**
```python
# tests/dashboard/use_cases/test_load_overview.py
import pytest
from src.dashboard.use_cases.load_overview import LoadOverviewUseCase
from tests.mocks.metrics_repository_mock import MetricsRepositoryMock

def test_load_overview_calculates_health():
    # Arrange
    mock_repo = MetricsRepositoryMock()
    mock_repo.set_scan_data({"issues": 10, "loc": 10000})
    use_case = LoadOverviewUseCase(mock_repo)
    
    # Act
    result = use_case.execute()
    
    # Assert
    assert result.health_score >= 90  # 10 issues / 10K LOC = 99% health
    assert result.total_issues == 10
    assert result.total_loc == 10000
```

**Integration Testing (Real Repositories):**
```python
# tests/dashboard/integration/test_dashboard_workflow.py
def test_end_to_end_dashboard_generation():
    # 1. Run crawler
    crawler = CrawlerOrchestrator()
    crawler.execute(repo_path="/test/repo")
    
    # 2. Generate dashboard
    orchestrator = ApplicationHealthOrchestrator()
    orchestrator.execute()
    
    # 3. Validate dashboard JSON exists
    assert os.path.exists("dashboards/dashboard-latest.json")
    
    # 4. Load dashboard in browser (Selenium)
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000/dashboard")
    
    # 5. Validate tabs render
    assert driver.find_element(By.ID, "overview-tab")
    assert driver.find_element(By.ID, "architecture-tab")
```

---

## 📦 CORTEX Integration Strategy

### Capability Mappings

**Philosophy:** Maximize reuse of existing CORTEX systems. Dashboard is an **orchestrator/aggregator**, not a reimplementation.

---

#### Integration 1: DependencyGraph → Architecture Tab

**Existing System:** `src/discovery/dependency_graph.py` (System Alignment component)

**Current Capabilities:**
- Discovers Python imports via AST parsing
- Builds directed graph (nodes = modules, edges = imports)
- Detects circular dependencies
- Calculates coupling metrics (fan-in/fan-out)

**Integration Point:** Architecture Tab rendering

**API Contract:**
```python
# src/discovery/dependency_graph.py
class DependencyGraph:
    def build_graph(self, repo_path: Path) -> Dict[str, Any]:
        """
        Build dependency graph for repository.
        
        Returns:
            {
                "nodes": [
                    {"id": "src.auth", "label": "auth", "type": "module", "loc": 500},
                    {"id": "src.user", "label": "user", "type": "module", "loc": 300}
                ],
                "edges": [
                    {"source": "src.auth", "target": "src.user", "weight": 5}
                ]
            }
        """
```

**Dashboard Use Case:**
```python
# src/dashboard/use_cases/render_architecture_graph.py
class RenderArchitectureGraphUseCase:
    def __init__(self, dependency_graph: DependencyGraph):
        self.dependency_graph = dependency_graph
    
    def execute(self, repo_path: Path) -> Dict[str, Any]:
        # 1. Get graph data from CORTEX system
        graph_data = self.dependency_graph.build_graph(repo_path)
        
        # 2. Enhance with health scoring
        for node in graph_data["nodes"]:
            score = self._calculate_node_health(node)
            node["health"] = score
            node["color"] = self._score_to_color(score)
        
        # 3. Return D3.js-ready format
        return graph_data
```

**Data Flow:**
```
Repository Scan → DependencyGraph.build_graph() → JSON (nodes/edges)
    ↓
RenderArchitectureGraphUseCase.execute() → Add health colors
    ↓
JSON Response → Browser D3.js → Force-directed graph rendering
```

**Acceptance Criteria:**
- ✅ Graph renders with <2s latency for 500-node repositories
- ✅ Nodes colored by health: green (90+), yellow (70-89), red (<70)
- ✅ Clicking node shows tooltip with LOC, dependencies, health score
- ✅ Circular dependencies highlighted with dashed red edges

---

#### Integration 2: IntegrationScorer → Health Color Coding

**Existing System:** `src/validation/integration_scorer.py` (System Alignment component)

**Current Capabilities:**
- 7-layer validation (Discovery → Import → Instantiation → Documentation → Testing → Wiring → Optimization)
- Per-component scoring (0-100%)
- Status categorization: Healthy (90+), Warning (70-89), Critical (<70)

**Integration Point:** Node color calculation in Architecture Tab

**API Contract:**
```python
# src/validation/integration_scorer.py
class IntegrationScorer:
    def score_component(self, component_path: Path) -> Dict[str, Any]:
        """
        Score component integration depth.
        
        Returns:
            {
                "overall_score": 85,  # 0-100
                "status": "warning",  # healthy/warning/critical
                "layers": {
                    "discovery": True,
                    "import": True,
                    "instantiation": True,
                    "documentation": False,  # Missing docs
                    "testing": True,
                    "wiring": False,  # Not wired to entry point
                    "optimization": False
                },
                "issues": ["Missing documentation", "Not wired to entry point"]
            }
        """
```

**Dashboard Use Case:**
```python
# src/dashboard/use_cases/render_architecture_graph.py (continued)
class RenderArchitectureGraphUseCase:
    def _calculate_node_health(self, node: Dict) -> int:
        """Calculate health score for graph node."""
        component_path = Path(node["id"].replace(".", "/") + ".py")
        
        # Delegate to CORTEX IntegrationScorer
        score_result = self.integration_scorer.score_component(component_path)
        
        return score_result["overall_score"]
    
    def _score_to_color(self, score: int) -> str:
        """Convert health score to D3.js color."""
        if score >= 90:
            return "#28a745"  # Green (healthy)
        elif score >= 70:
            return "#ffc107"  # Yellow (warning)
        else:
            return "#dc3545"  # Red (critical)
```

**Data Flow:**
```
Component Path → IntegrationScorer.score_component() → Score (0-100)
    ↓
_score_to_color() → Hex color (#28a745 / #ffc107 / #dc3545)
    ↓
D3.js node rendering → Visual feedback (green/yellow/red nodes)
```

**Acceptance Criteria:**
- ✅ Node colors reflect actual 7-layer integration scores
- ✅ Tooltip shows score breakdown (which layers pass/fail)
- ✅ Status updates in real-time via WebSocket (if component changes)
- ✅ Legend explains color coding (90+ green, 70-89 yellow, <70 red)

---

#### Integration 3: RefactoringIntelligence → Recommendations Tab

**Existing System:** `src.agents.refactoring_intelligence` (TDD Mastery component)

**Current Capabilities:**
- 11 code smell types (long method, complex method, duplicate code, etc.)
- AST-based analysis for Python, JavaScript, TypeScript, C#
- Performance smell detection (slow functions, hot paths, bottlenecks)
- Confidence scoring per smell (0.70-0.95)

**Integration Point:** Recommendations Tab with prioritized action items

**API Contract:**
```python
# src/agents/refactoring_intelligence.py
class RefactoringIntelligence:
    def detect_smells(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Detect code smells in file.
        
        Returns:
            [
                {
                    "type": "LONG_METHOD",
                    "function": "process_payment",
                    "location": {"file": "payment.py", "line": 45},
                    "severity": "high",
                    "confidence": 0.95,
                    "metrics": {"loc": 78, "threshold": 50},
                    "suggestion": "Split into smaller functions",
                    "estimated_effort": "30 minutes"
                }
            ]
        """
```

**Dashboard Use Case:**
```python
# src/dashboard/use_cases/generate_recommendations.py
class GenerateRecommendationsUseCase:
    def __init__(self, refactoring_intelligence: RefactoringIntelligence):
        self.refactoring_intelligence = refactoring_intelligence
    
    def execute(self, repo_path: Path) -> List[Dict[str, Any]]:
        recommendations = []
        
        # 1. Scan all Python files
        for py_file in repo_path.rglob("*.py"):
            smells = self.refactoring_intelligence.detect_smells(py_file)
            recommendations.extend(smells)
        
        # 2. Prioritize by severity + confidence
        recommendations.sort(
            key=lambda r: (r["severity"], r["confidence"]),
            reverse=True
        )
        
        # 3. Group by type for UI rendering
        grouped = self._group_by_type(recommendations)
        
        return grouped
```

**Data Flow:**
```
Repository Scan → RefactoringIntelligence.detect_smells() → Smell list
    ↓
GenerateRecommendationsUseCase.execute() → Prioritize + group
    ↓
JSON Response → Browser → Recommendations Tab with priority matrix
```

**Acceptance Criteria:**
- ✅ Recommendations sorted by impact (high → medium → low)
- ✅ Each recommendation has: location, description, effort estimate, suggested fix
- ✅ Clicking recommendation navigates to code location (if IDE integration)
- ✅ "Apply fix" button generates fix template (future enhancement)

---

#### Integration 4: Tier 3 Databases → Historical Trend Charts

**Existing Systems:**
- `cortex-brain/tier3/code_metrics.db` - LOC, complexity, file counts over time
- `cortex-brain/tier3/file_changes.db` - Git activity, churn rate
- `cortex-brain/tier3/dev_insights.db` - Development patterns, hotspots

**Current Capabilities:**
- Time-series data storage (daily snapshots)
- Metric aggregation (averages, trends, velocities)
- Historical comparison (current vs 7/30/90 days ago)

**Integration Point:** Quality Tab and Overview Tab with trend charts

**API Contract:**
```python
# src/tier3/code_metrics_query.py
class CodeMetricsQuery:
    def get_trend(self, metric: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical trend for metric.
        
        Returns:
            [
                {"date": "2025-11-01", "value": 10500},
                {"date": "2025-11-02", "value": 10520},
                ...
            ]
        """
    
    def get_velocity(self, metric: str) -> float:
        """Calculate rate of change per day."""
```

**Dashboard Use Case:**
```python
# src/dashboard/use_cases/load_overview.py (enhanced)
class LoadOverviewUseCase:
    def _add_historical_trends(self, overview: OverviewData) -> None:
        # 1. Get LOC trend (last 30 days)
        loc_trend = self.metrics_query.get_trend("total_loc", days=30)
        overview.loc_trend = loc_trend
        
        # 2. Get complexity trend
        complexity_trend = self.metrics_query.get_trend("avg_complexity", days=30)
        overview.complexity_trend = complexity_trend
        
        # 3. Get test coverage trend
        coverage_trend = self.metrics_query.get_trend("test_coverage", days=30)
        overview.coverage_trend = coverage_trend
        
        # 4. Calculate velocities
        overview.loc_velocity = self.metrics_query.get_velocity("total_loc")
```

**Data Flow:**
```
Dashboard Load → CodeMetricsQuery.get_trend() → Time-series data
    ↓
LoadOverviewUseCase._add_historical_trends() → Add to OverviewData
    ↓
JSON Response → Browser Chart.js → Line charts with 30-day history
```

**Acceptance Criteria:**
- ✅ Trend charts show last 30 days by default (configurable to 7/90)
- ✅ Chart.js animations smooth (300ms)
- ✅ Velocity indicators show +/- change per day
- ✅ Tooltips show exact values on hover

---

### API Contracts Summary

**DependencyGraph Integration:**
```python
# Input: Path to repository
# Output: {"nodes": [...], "edges": [...]}
# Performance: <5s for 500-node repos
```

**IntegrationScorer Integration:**
```python
# Input: Path to component file
# Output: {"overall_score": 85, "status": "warning", "layers": {...}}
# Performance: <100ms per component
```

**RefactoringIntelligence Integration:**
```python
# Input: Path to source file
# Output: [{"type": "LONG_METHOD", "severity": "high", ...}]
# Performance: <500ms per file (AST parsing + smell detection)
```

**Tier 3 Databases Integration:**
```python
# Input: Metric name, time range (days)
# Output: [{"date": "YYYY-MM-DD", "value": 123}]
# Performance: <50ms (indexed queries)
```

---

### Data Flow Patterns

**Pattern 1: Crawler → CORTEX Systems → Dashboard**
```
1. CrawlerOrchestrator scans repository
2. Writes raw metrics to JSON files
3. Dashboard Use Cases read JSON via Repositories
4. Apply transformations (health scoring, grouping)
5. Return formatted data to Flask
6. Flask renders HTML with Chart.js/D3.js
7. Browser displays interactive dashboard
```

**Pattern 2: Real-Time Updates (WebSocket)**
```
1. Browser connects to Socket.IO server
2. Server listens for crawler events
3. Crawler emits progress events during scan
4. Server broadcasts to all connected clients
5. Browser updates progress bar/charts in real-time
```

**Pattern 3: Historical Trends (Tier 3)**
```
1. Dashboard queries Tier 3 databases
2. SQLite returns time-series data (indexed)
3. Use Case calculates velocities/trends
4. Chart.js renders line charts with 30-day history
```

---

## 🛡️ Risk Mitigation & Timeline Summary

### OWASP Security Tasks Sprint Mapping

**Philosophy:** Security is NOT a Phase 3 afterthought. OWASP tasks are distributed across all phases.

---

#### Phase 1 Security Tasks (Sprint 1, Week 1-2)

**Task 1.5: Input Validation Framework** [4h]
- **OWASP Category:** A03:2021 – Injection
- **What:** Validate all user inputs (repository paths, filter parameters, export options)
- **Implementation:**
  - Python: `pathlib.Path.resolve()` + `is_relative_to()` to prevent path traversal
  - JavaScript: Regex validation for tab IDs, node IDs (alphanumeric + underscore only)
  - Whitelist allowed file extensions for export (.pdf, .png, .pptx)
- **Acceptance Criteria:**
  - ❌ Reject: `../../../../etc/passwd`, `<script>alert(1)</script>`, `'; DROP TABLE--`
  - ✅ Accept: `./myproject`, `node_42`, `report.pptx`
- **Dependencies:** None (foundational)

**Task 1.6: Output Encoding for XSS Prevention** [3h]
- **OWASP Category:** A03:2021 – Injection (XSS)
- **What:** Escape all dynamic content in HTML templates
- **Implementation:**
  - Jinja2 autoescape enabled (default in Flask)
  - D3.js: Use `.text()` instead of `.html()` for user-controlled strings
  - Chart.js: Sanitize tooltip labels with DOMPurify.js
- **Acceptance Criteria:**
  - ❌ Raw HTML injection: `<img src=x onerror=alert(1)>`
  - ✅ Escaped output: `&lt;img src=x onerror=alert(1)&gt;`
- **Dependencies:** None

---

#### Phase 2 Security Tasks (Sprint 2, Week 3-4)

**Task 2.4: CSRF Protection for WebSocket** [2h]
- **OWASP Category:** A01:2021 – Broken Access Control (CSRF)
- **What:** Verify WebSocket connections originate from legitimate dashboard sessions
- **Implementation:**
  - Generate CSRF token on dashboard load (Flask-WTF)
  - Include token in Socket.IO connection auth: `io.connect('/ws', {auth: {token: csrf_token}})`
  - Server validates token before accepting connection
- **Acceptance Criteria:**
  - ❌ Reject: Cross-origin WebSocket connections without valid token
  - ✅ Accept: Same-origin connections with matching session token
- **Dependencies:** Task 2.2 (WebSocket server must be implemented first)

**Task 2.5: Secure Session Management** [3h]
- **OWASP Category:** A07:2021 – Identification and Authentication Failures
- **What:** Protect dashboard sessions from hijacking
- **Implementation:**
  - Flask: `SESSION_COOKIE_SECURE=True` (HTTPS only)
  - `SESSION_COOKIE_HTTPONLY=True` (prevent XSS cookie theft)
  - `SESSION_COOKIE_SAMESITE='Lax'` (CSRF mitigation)
  - Session timeout: 30 minutes idle, 8 hours absolute
- **Acceptance Criteria:**
  - ❌ Session cookies accessible via JavaScript (`document.cookie`)
  - ✅ Cookies HTTP-only, secure flag set, auto-expire after timeout
- **Dependencies:** None

---

#### Phase 3 Security Tasks (Sprint 3, Week 5-6)

**Task 3.5: Dependency Scanning** [2h]
- **OWASP Category:** A06:2021 – Vulnerable and Outdated Components
- **What:** Scan dashboard dependencies for known CVEs
- **Implementation:**
  - Python: `pip-audit` in CI/CD pipeline
  - JavaScript: `npm audit` before each build
  - Fail build if HIGH/CRITICAL vulnerabilities found
- **Acceptance Criteria:**
  - ✅ Zero HIGH/CRITICAL CVEs in production build
  - ✅ Automated scan runs on every PR
- **Dependencies:** Task 3.4 (documentation must include dependency update procedure)

**Task 3.6: Security Headers** [1h]
- **OWASP Category:** A05:2021 – Security Misconfiguration
- **What:** Add HTTP security headers to Flask responses
- **Implementation:**
  ```python
  @app.after_request
  def add_security_headers(response):
      response.headers['X-Content-Type-Options'] = 'nosniff'
      response.headers['X-Frame-Options'] = 'DENY'
      response.headers['X-XSS-Protection'] = '1; mode=block'
      response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net"
      return response
  ```
- **Acceptance Criteria:**
  - ✅ All 4 headers present in HTTP responses
  - ✅ SecurityHeaders.com scan scores A+ rating
- **Dependencies:** None

**Task 3.7: Penetration Testing** [4h]
- **OWASP Category:** All (comprehensive validation)
- **What:** Manual security testing against OWASP Top 10
- **Test Cases:**
  - SQL Injection: Test repository path inputs with SQL payloads
  - XSS: Test component names, file paths with HTML/JS payloads
  - CSRF: Attempt cross-origin WebSocket connections
  - Path Traversal: Test export functionality with `../../../` paths
  - Authentication Bypass: Test session hijacking, cookie manipulation
- **Acceptance Criteria:**
  - ❌ Zero exploitable vulnerabilities found
  - ✅ Penetration test report documents all tested attack vectors
- **Dependencies:** All prior security tasks complete

---

### Critical Path Analysis

**Definition:** Tasks that MUST complete sequentially (no parallelization possible).

**Critical Path Sequence:**
```
Task 1.1 (Integrate DependencyGraph) [4h]
   ↓
Task 1.2 (Architecture Tab with D3.js) [6h]  ← BLOCKS Phase 2
   ↓
Task 2.1 (Clean Architecture Refactor) [12h]  ← BLOCKS Tasks 2.2, 2.3
   ↓
Task 2.2 (WebSocket Real-Time) [8h]  ← BLOCKS Task 2.4 (CSRF)
   ↓
Task 3.1 (PPTX Export) [6h]
   ↓
Task 3.2 (Performance Optimization) [8h]  ← BLOCKS Task 3.3 (animations depend on performance baseline)
   ↓
Task 3.7 (Penetration Testing) [4h]  ← BLOCKS deployment
```

**Total Critical Path Duration:** 48 hours (2 full-time weeks OR 4 part-time weeks)

**Parallelizable Work:**
- Task 1.3 (5-tab structure) can run in parallel with Task 1.2
- Task 1.4 (multi-threading) can run in parallel with Task 1.3
- Task 1.5 (input validation) can run anytime in Phase 1
- Task 1.6 (output encoding) can run anytime in Phase 1
- Task 2.3 (health scoring) can run in parallel with Task 2.2
- Task 2.5 (session management) can run anytime in Phase 2
- Task 3.4 (documentation) can run in parallel with Task 3.3
- Task 3.5 (dependency scanning) can run anytime in Phase 3
- Task 3.6 (security headers) can run anytime in Phase 3

**Optimization Strategy:**
- **Phase 1:** Run 2 tracks in parallel (Track A: 1.1→1.2, Track B: 1.3→1.4→1.5→1.6)
- **Phase 2:** Wait for Task 2.1 to complete, then run 2.2 and 2.3 in parallel, add 2.4 and 2.5 anytime
- **Phase 3:** After 3.2 completes, run 3.3 and 3.4 in parallel, add 3.5 and 3.6 anytime, finish with 3.7

**Realistic Timeline with Parallel Work:**
- Phase 1: 24h → 14h (parallel tracks)
- Phase 2: 24h → 16h (parallel after refactor)
- Phase 3: 24h → 14h (parallel optimization + docs)
- **Total: 44 hours** (vs 72h sequential) = **39% faster**

---

### Success Metrics & Validation Checkpoints

**Phase 1 Success Criteria (Week 2 Demo):**
- ✅ Architecture tab renders force-directed graph in <2s for 500-node repos
- ✅ Graph nodes colored by health (green/yellow/red based on IntegrationScorer)
- ✅ Clicking node shows tooltip with LOC, dependencies, health score breakdown
- ✅ All 5 tabs visible and accessible (even if 3-5 have placeholder content)
- ✅ Multi-threaded crawler completes 500-file repo scan in <30s (vs 5+ minutes single-threaded)
- ✅ Zero SQL injection or path traversal vulnerabilities (input validation passes penetration test)

**Demo Script Phase 1:**
```
1. Open dashboard, show 5-tab structure
2. Click "Scan Repository" → Show progress bar updating in real-time
3. Navigate to Architecture tab → Graph renders with colored nodes
4. Hover over red node → Tooltip shows "Health: 62%, Issues: Missing tests, High complexity"
5. Click node → Details panel shows file path, LOC, dependencies list
6. Attempt SQL injection in repository path input → Show error message (rejected)
```

**Phase 2 Success Criteria (Week 4 Demo):**
- ✅ System Alignment validation scores 100% (all SOLID principles pass)
- ✅ Codebase organized into 4 clean architecture layers (Presentation/Use Cases/Domain/Data)
- ✅ WebSocket connection establishes in <500ms
- ✅ Real-time progress updates during scan (every 1 second)
- ✅ Health scores update in real-time when analysis completes
- ✅ CSRF protection blocks unauthorized WebSocket connections

**Demo Script Phase 2:**
```
1. Show project structure → Point out 4 clean architecture folders
2. Run System Alignment validation → Show 100% SOLID compliance report
3. Start repository scan → Watch progress bar update in real-time (WebSocket)
4. Graph nodes update colors as IntegrationScorer finishes per-component analysis
5. Show browser developer console → WebSocket messages streaming
6. Attempt cross-origin WebSocket connection → Show 403 Forbidden error
```

**Phase 3 Success Criteria (Week 6 Demo):**
- ✅ PPTX export generates 10-slide deck in <10s
- ✅ Graph rendering optimized: 1000-node repos render in <3s (with clustering)
- ✅ Animations smooth (60 FPS, no jank)
- ✅ WCAG 2.1 Level AA compliance (color contrast, keyboard navigation)
- ✅ SecurityHeaders.com scan scores A+ rating
- ✅ Zero HIGH/CRITICAL CVEs in `pip-audit` and `npm audit`
- ✅ Penetration test report documents 0 exploitable vulnerabilities

**Demo Script Phase 3:**
```
1. Scan large 1000-file repository → Graph renders in <3s with node clustering
2. Click "Export to PPTX" → 10-slide PowerPoint deck downloads
3. Open deck → Show Executive Summary, Architecture Diagram, Top 10 Issues slides
4. Show SecurityHeaders.com scan → A+ rating
5. Show dependency scan reports → Zero vulnerabilities
6. Navigate dashboard using only keyboard (Tab, Enter) → All features accessible
7. Run penetration test → Show report with 0 exploitable issues
```

---

### Sprint Review Demo Scripts

**Sprint 1 Review (End of Week 2) - "Foundation in Place"**

**Audience:** Development team, tech leads  
**Duration:** 15 minutes  
**Objectives:** Prove backend visualization works, show performance gains from multi-threading

**Script:**
1. **Opening (2 min):** "We've completed Phase 1 of the Onboarding Dashboard enhancement. Today I'll show you backend architecture visualization and 10-20x faster scanning."

2. **Live Demo (10 min):**
   - Open CORTEX dashboard on localhost
   - Click "Scan Repository" button, select 500-file Python project
   - **Highlight:** Progress bar updates every second (multi-threaded crawler)
   - **Callout:** "This used to take 5+ minutes, now completes in 30 seconds"
   - Navigate to Architecture tab → D3.js graph renders
   - **Highlight:** Nodes colored by health (green/yellow/red)
   - Hover over red node → Tooltip: "Health: 58%, Issues: No tests, Complexity 42"
   - Click node → Details panel: File path, 450 LOC, imports list
   - Zoom in/out, pan around graph → Smooth interactions
   - Show all 5 tabs (Overview, Architecture, Quality, Security, Recommendations)

3. **Security Demo (2 min):**
   - Attempt SQL injection in repository path: `'; DROP TABLE--`
   - **Highlight:** Error message: "Invalid repository path"
   - Attempt path traversal: `../../../../etc/passwd`
   - **Highlight:** Rejected, logged security violation

4. **Q&A (1 min):** "Questions about the architecture visualization or security?"

**Sprint 2 Review (End of Week 4) - "Clean Architecture & Real-Time"**

**Audience:** Development team, tech leads, product managers  
**Duration:** 20 minutes  
**Objectives:** Prove clean architecture refactor succeeded, show real-time WebSocket updates

**Script:**
1. **Opening (3 min):** "Sprint 2 focused on internal quality and real-time updates. We refactored 600 lines into 35 clean architecture files and added WebSocket streaming."

2. **Clean Architecture Walkthrough (7 min):**
   - Open VS Code, show project structure
   - **Highlight:** 4 folders (presentation, use_cases, domain, data)
   - Open `use_cases/render_architecture_graph.py` → Show SOLID principles
   - Run System Alignment validation → **Show 100% compliance report**
   - **Callout:** "Before refactor: 40% SOLID compliance. After: 100%"
   - Open `tests/` folder → Show unit tests with mocked repositories
   - Run pytest → **Show 95% test coverage**

3. **Real-Time Demo (8 min):**
   - Open dashboard, open browser DevTools → Network tab
   - Click "Scan Repository" → Show WebSocket connection established (<500ms)
   - **Highlight:** Console logs "scan_started", "scan_progress: 25%", "scan_progress: 50%", etc.
   - Watch progress bar update in real-time
   - **Callout:** "Updates every 1 second via WebSocket, not polling"
   - Analysis completes → Graph nodes change color in real-time
   - **Highlight:** Red node → Yellow node (health improved from 65% → 78%)

4. **Security Demo (1 min):**
   - Open Postman, attempt cross-origin WebSocket connection without CSRF token
   - **Highlight:** 403 Forbidden error
   - Show Flask logs → Security violation logged

5. **Q&A (1 min):** "Questions about the refactor or real-time features?"

**Sprint 3 Review (End of Week 6) - "Production Ready"**

**Audience:** Full team, stakeholders, potential customers (if public demo)  
**Duration:** 30 minutes  
**Objectives:** Prove production readiness, impress with polish and export features

**Script:**
1. **Opening (3 min):** "Final sprint focused on export, performance, and security hardening. This dashboard is now production-ready and demo-worthy."

2. **Performance Demo (7 min):**
   - Scan 1000-file repository → Graph renders in <3s
   - **Highlight:** Node clustering (500+ nodes grouped)
   - Zoom into cluster → Nodes expand, smooth animation (60 FPS)
   - Open Performance tab in DevTools → Show frame rate, memory usage
   - **Callout:** "Memory usage <50MB, no memory leaks after 10 scans"
   - Switch between tabs → Instant transitions (<100ms)

3. **Export Demo (5 min):**
   - Click "Export to PPTX" button → Download starts
   - Open PowerPoint deck → 10 slides:
     - Slide 1: Executive Summary (total LOC, health score, language breakdown)
     - Slide 2: Architecture Diagram (force-directed graph screenshot)
     - Slide 3-5: Quality Metrics (complexity chart, test coverage, code smells)
     - Slide 6-7: Security Analysis (vulnerability count, OWASP categories)
     - Slide 8-9: Top 10 Recommendations (prioritized by impact)
     - Slide 10: Next Steps (action items for development team)
   - **Callout:** "Auto-generated in 8 seconds, ready for executive presentation"

4. **Polish Demo (5 min):**
   - Show responsive layout → Resize browser, graph adapts
   - Test keyboard navigation → Tab through all controls, Enter to activate
   - Show color contrast → WCAG 2.1 AA compliant (use browser inspector)
   - Hover animations → Smooth transitions, tooltip timing perfect

5. **Security Validation (7 min):**
   - Open SecurityHeaders.com → Enter dashboard URL → **Show A+ rating**
   - Show `pip-audit` output → Zero vulnerabilities
   - Show `npm audit` output → Zero vulnerabilities
   - Show penetration test report → **0 exploitable vulnerabilities found**
   - List tested attack vectors: SQL injection, XSS, CSRF, path traversal, session hijacking
   - **Callout:** "Passed OWASP Top 10 security validation"

6. **Business Value Closing (2 min):**
   - **Restate goals:** "70% → 95% feature completeness achieved"
   - **Key wins:** "10-20x faster scanning, real-time updates, production-ready security, impressive export feature"
   - **Next steps:** "Ready for beta testing with early adopters, marketing can use demo in sales pitches"

7. **Q&A (1 min):** "Questions or feedback?"

---

### Risk Register

| Risk | Impact | Probability | Mitigation | Owner |
|------|--------|------------|------------|-------|
| D3.js performance degrades with >1000 nodes | HIGH | MEDIUM | Node clustering (Task 3.2), Web Workers for calculations, Canvas fallback | Dev Team |
| WebSocket connection fails in corporate firewalls | MEDIUM | HIGH | Fallback to HTTP polling if WebSocket blocked (graceful degradation) | Dev Team |
| PPTX export library (python-pptx) lacks features | MEDIUM | LOW | Prototype export in Task 3.1 Sprint 3 Week 1, switch to ReportLab if needed | Dev Team |
| Clean architecture refactor introduces regressions | HIGH | MEDIUM | 95% test coverage (Task 2.1), System Alignment validation, integration tests | QA + Dev |
| Security vulnerability discovered post-deployment | HIGH | LOW | Penetration testing (Task 3.7), automated dependency scanning in CI/CD | Security Team |
| Timeline slips due to underestimated complexity | MEDIUM | MEDIUM | 8-hour risk buffer in Phase 3, daily standups to catch blockers early | Project Manager |

---

### Timeline Summary

**Total Effort:** 72 hours (planned tasks) + 8 hours (risk buffer) = **80 hours**

**With Parallelization:** 44 hours critical path + 8 hours buffer = **52 hours**

**Calendar Timeline (2 developers, part-time allocation):**
- **Sprint 1 (Weeks 1-2):** Phase 1 tasks (14 hours per developer)
- **Sprint 2 (Weeks 3-4):** Phase 2 tasks (16 hours per developer)
- **Sprint 3 (Weeks 5-6):** Phase 3 tasks (14 hours per developer)

**Key Milestones:**
- **2025-12-13 (Week 2):** Sprint 1 Review - Architecture visualization demo
- **2025-12-27 (Week 4):** Sprint 2 Review - Clean architecture + real-time demo
- **2026-01-10 (Week 6):** Sprint 3 Review - Production-ready demo
- **2026-01-17 (Week 7):** Beta deployment, early adopter feedback collection
- **2026-01-31 (Week 9):** CORTEX 3.3.0 release with dashboard feature

---

**Document Status:** ✅ COMPLETE (5/5 sections finished)  
**Ready for Approval:** Yes  
**Next Action:** User review and approval before implementation begins  
**Completion Date:** 2025-11-30
