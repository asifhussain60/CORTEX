# CORTEX Lens v3.0 - Master Plan (Enhanced Planning System v3.0 Compatible)

**Version:** 3.0.0 🚀 ALIGNED WITH PLANNING SYSTEM V3.0  
**Date:** December 14, 2025  
**Author:** Asif Hussain  
**Status:** 🎯 READY FOR EXECUTION  
**Planning System:** v3.0 (`orchestration_3_0`) - DoR/DoD Enforced  
**Manifest:** `planning-orchestrator-v3-manifest.yaml` (when created)

---

## 🎯 Strategic Goal

Achieve feature parity with CORTEX Admin Dashboard while maintaining zero dependencies. Create self-contained, production-ready universal repository analyzer with modern visualization stack.

**Alignment with CORTEX 4.0:**
- Uses **Planning System v3.0** architecture (`src/orchestration_3_0/orchestrators/planning/`)
- Enforces **DoR/DoD** compliance gates
- Integrates with **TDD Orchestrator** for test-driven development
- Follows **state machine** workflow (INITIALIZED → VALIDATING_DOR → EXECUTING → VALIDATING_DOD → COMPLETED)
- Supports **session persistence** and recovery

---

## 📋 Definition of Ready (DoR)

**Feature Requirements:**
- ✅ Feature name: "CORTEX Lens v3.0 Admin Dashboard Parity"
- ✅ Description: Complete migration of admin dashboard glassmorphism design, 8-tab navigation, D3.js visualization stack, and production components to CORTEX Lens with zero external dependencies
- ✅ Target release: January 2026 (Week 15-17)
- ✅ Acceptance criteria: 16 (see below)

**Technical Prerequisites:**
- ✅ Admin dashboard exists (`cortex-brain/dashboards/ui/`)
- ✅ CORTEX Lens v2.5 baseline exists (`src/cortex_lens/`)
- ✅ D3.js/Three.js/Chart.js can be vendored (zero deps requirement)
- ✅ Template system supports extensions (HTML/CSS/JS injection)
- ✅ Selenium test framework exists (`tests/cortex_lens/`)

**Stakeholder Approvals:**
- ✅ Technical approach approved (glassmorphism + 8-tab + D3.js stack)
- ✅ Zero dependencies constraint accepted
- ✅ 125% typography scale rationale documented

**Dependencies:**
- ⚠️ Admin dashboard must remain stable during migration
- ⚠️ v2.5 templates (console_app, api_service) must continue working

---

## 📊 Complexity Analysis

**Overall Complexity:** HIGH

**Justification:**
- 16 sub-plans spanning 6-7 weeks
- ~23,000 LOC new/modified code
- Complex D3.js force graphs, Three.js 3D rendering
- 6 repository type templates requiring unified redesign
- 26+ production components with accessibility requirements
- Performance optimization for 1M LOC repositories

**Complexity Breakdown:**
- **Foundation (Sub-Plans 1-4):** HIGH - Design extraction, CSS architecture, D3.js stack
- **Core Tabs (Sub-Plans 5-8):** MEDIUM - Template-based development with new visualizations
- **Advanced Tabs (Sub-Plans 9-12):** MEDIUM - Business logic and interactive workflows
- **Integration (Sub-Plans 13-14):** HIGH - Unifying 6 templates, 26 components
- **Optimization (Sub-Plans 15-16):** HIGH - Multi-threading, virtual scrolling, E2E validation

---

## 🏗️ Phase Decomposition

### Phase 0: Planning & Preparation (Week 1, 5 days)
**DoR Gate:** Architectural review, dependency validation, design extraction planning

**Deliverables:**
1. Planning System v3.0 manifest for CORTEX Lens (`planning-orchestrator-v3-manifest.yaml`)
2. Design extraction strategy document
3. Component migration checklist
4. Visualization replacement roadmap (Mermaid → D3.js)
5. Test strategy (expand Selenium suite to 60+ tests)

**DoD:**
- [ ] Manifest validated by Planning Orchestrator
- [ ] All DoR items approved
- [ ] Zero blocking architectural issues
- [ ] Design extraction plan peer-reviewed
- [ ] Test strategy approved (85% coverage target)

**Tasks:**
1. Create Planning System v3.0 manifest inheriting from base orchestrator manifest
2. Document admin dashboard CSS architecture (8 layers)
3. Catalog all glassmorphism patterns (backdrop-filter, transparency, shadows)
4. Map component dependencies (admin → lens)
5. Define D3.js visualization API contracts
6. Expand test plan (current: 12 tests → target: 60+ tests)
7. Git checkpoint: `[CORTEX-LENS][PHASE-0] Planning complete`

---

### Phase 1: Foundation - Design System & Typography (Week 2, 5 days)
**Corresponds to:** Sub-Plans 1-2

**Deliverables:**
1. Admin design extraction document (~1,200 LOC documentation)
2. `src/cortex_lens/templates/base/variables.css` with 125% typography scale (~300 LOC)
3. Glassmorphism pattern library (CSS snippets)
4. 3D brain visualization implementation guide
5. Loading animation library
6. Typography scale documentation

**DoD:**
- [ ] All CSS variables extracted (200+ variables)
- [ ] 125% typography scale validated with Selenium
- [ ] Glassmorphism patterns render correctly (backdrop-filter support tested)
- [ ] 3D brain viz documented with Three.js integration steps
- [ ] Loading animations extracted and tested
- [ ] Zero console errors in browser
- [ ] Git checkpoint created

**Tasks:**
1. **Sub-Plan 1: Admin Design Migration (3-4 days)**
   - Extract CSS architecture (reset, variables, typography, layouts, components, utils, animations, accessibility)
   - Document glassmorphism patterns (~30 components)
   - Extract 3D brain viz (Three.js implementation)
   - Document loading animations and skeleton loaders
   - Create pattern library markdown

2. **Sub-Plan 2: Typography 125% Scale (1 day)**
   - Create `variables.css` with 10-level scale (xs → 5xl)
   - Apply `--scale-factor: 1.25` multiplier
   - Create responsive typography utilities
   - Update existing templates (console_app, api_service)
   - Test with Selenium (font size validation)

3. Git checkpoint: `[CORTEX-LENS][PHASE-1] Design foundation complete`

**TDD Requirements:**
- [ ] RED: Write failing test for typography scale rendering
- [ ] GREEN: Implement variables.css and utilities
- [ ] REFACTOR: Remove hardcoded font sizes from templates
- [ ] Test coverage: 85% for typography utilities

---

### Phase 2: Navigation & Visualizations (Week 3-4, 8 days)
**Corresponds to:** Sub-Plans 3-4

**Deliverables:**
1. Sidebar navigation system (~700 LOC CSS + JS)
2. 6 D3.js visualization components (~1,200 LOC)
3. Three.js 3D brain component (~200 LOC)
4. Chart.js preset library (~300 LOC)
5. Export utilities (PNG/SVG)

**DoD:**
- [ ] Sidebar navigation functional (8 sections, collapsible, keyboard nav)
- [ ] ARIA labels and roles for WCAG 2.1 AAA compliance
- [ ] All 6 D3.js components render with real data
- [ ] Three.js brain rotates and displays health score color
- [ ] Export to PNG/SVG working
- [ ] Selenium tests pass (navigation, visualizations)
- [ ] Git checkpoint created

**Tasks:**
1. **Sub-Plan 3: Sidebar Navigation (2-3 days)**
   - Create `sidebar.css` with glassmorphism (~400 LOC)
   - Implement collapsible behavior (expanded/collapsed states)
   - Add 8 navigation sections with icons (📊 📚 ⚙️ 🔒 🎯 💡 🏗️ 📁)
   - Implement keyboard navigation (Tab, Arrow keys, Enter)
   - Add responsive breakpoints (auto-collapse on mobile)
   - Write Selenium tests for navigation

2. **Sub-Plan 4: D3.js Visualization Stack (4-5 days)**
   - Create `d3-architecture-diagram.js` (component diagrams)
   - Create `d3-dependency-graph.js` (force layout with clustering)
   - Create `d3-hierarchy-tree.js` (file structure)
   - Create `d3-sunburst.js` (LOC distribution)
   - Create `d3-chord-diagram.js` (inter-module dependencies)
   - Implement Three.js 3D brain visualization
   - Create Chart.js preset library (radar, bar, line, doughnut, pie)
   - Add zoom, pan, drag interactions
   - Implement export to PNG/SVG

3. Git checkpoint: `[CORTEX-LENS][PHASE-2] Navigation & visualizations complete`

**TDD Requirements:**
- [ ] RED: Write failing tests for sidebar navigation states
- [ ] GREEN: Implement sidebar.css and sidebar-navigation.js
- [ ] REFACTOR: Extract reusable nav utilities
- [ ] RED: Write failing tests for D3.js rendering
- [ ] GREEN: Implement D3.js components
- [ ] REFACTOR: Remove Mermaid dependencies, consolidate D3 utilities
- [ ] Test coverage: 85% for navigation and visualization modules

---

### Phase 3: Core Tabs Implementation (Week 5-6, 10 days)
**Corresponds to:** Sub-Plans 5-8

**Deliverables:**
1. Executive Summary tab (~800 LOC)
2. System Overview tab (~850 LOC)
3. Tech Stack tab (~1,000 LOC)
4. Security tab (~1,000 LOC)
5. Health scoring algorithms
6. Dependency analysis utilities
7. Vulnerability scanner UI
8. Security best practices checker

**DoD:**
- [ ] All 4 tabs render with real data
- [ ] Health scores calculate correctly (0-100 scale)
- [ ] Dependency graph shows package relationships
- [ ] Vulnerability scanner detects CVEs and secrets
- [ ] All visualizations interactive (hover, click, zoom)
- [ ] Selenium tests cover all tab interactions
- [ ] Git checkpoint created

**Tasks:**
1. **Sub-Plan 5: Executive Summary Tab (2-3 days)**
   - Hero section (repo name, health score ring chart, quick actions)
   - Key metrics grid (4 cards: LOC, coverage, security, maintainability)
   - Business value section (use cases, stakeholders, advantages, risks)
   - Quick insights (architecture type, languages, readiness scores)
   - Narrative panel (executive summary, capabilities, highlights)

2. **Sub-Plan 6: System Overview Tab (3 days)**
   - Health dashboard (6 sub-scores radar chart)
   - Repository statistics (file counts, LOC by language, complexity histogram)
   - Code quality metrics (cyclomatic complexity, code smells, duplication)
   - Test coverage detail (line/branch/function coverage treemap)
   - Documentation metrics (docstring coverage, comment ratio)

3. **Sub-Plan 7: Tech Stack Tab (3-4 days)**
   - Dependency overview (health score, outdated/vulnerable counts)
   - Interactive package table (sortable, filterable)
   - Framework detection (EOL tracking, migration recommendations)
   - Dependency force graph (D3.js with zoom/pan/filter)
   - Vulnerability scanner (CVE list, CVSS scores, fixes)
   - License compliance checker (pie chart, conflict warnings)

4. **Sub-Plan 8: Security Tab (3-4 days)**
   - Security overview (score gauge, issue breakdown)
   - Vulnerability list (CVE links, remediation steps)
   - Secrets detection (API keys, passwords, tokens with file/line locations)
   - Security best practices (auth, authorization, input validation checks)
   - Code security scan (dangerous functions, injection risks)
   - Compliance checks (OWASP Top 10, CWE mapping)

5. Git checkpoint: `[CORTEX-LENS][PHASE-3] Core tabs complete`

**TDD Requirements:**
- [ ] RED: Write failing tests for health score calculations
- [ ] GREEN: Implement health scoring algorithms
- [ ] REFACTOR: Extract scoring utilities to shared module
- [ ] RED: Write failing tests for dependency graph rendering
- [ ] GREEN: Implement dependency analysis and D3.js graph
- [ ] REFACTOR: Consolidate graph utilities
- [ ] Test coverage: 85% for tab components and utilities

---

### Phase 4: Advanced Tabs Implementation (Week 7-8, 9 days)
**Corresponds to:** Sub-Plans 9-12

**Deliverables:**
1. Use Cases tab (~900 LOC)
2. Recommendations tab (~1,000 LOC)
3. Architecture tab (~1,100 LOC)
4. Code Organization tab (~1,050 LOC)
5. Workflow diagram generator
6. Technical debt analyzer
7. Pattern detection display
8. File tree visualizer

**DoD:**
- [ ] All 4 tabs render with real data
- [ ] Use cases synthesized from code analysis
- [ ] Technical debt calculated with payoff roadmap
- [ ] Architecture patterns detected (MVC, Layered, Microservices)
- [ ] Code organization metrics accurate (LOC, complexity, duplication)
- [ ] Selenium tests cover all advanced features
- [ ] Git checkpoint created

**Tasks:**
1. **Sub-Plan 9: Use Cases Tab (2-3 days)**
   - Primary use cases (top 5 with supporting evidence)
   - Problem domain synthesis (industry-specific patterns)
   - Business workflows (D3.js workflow diagram)
   - Stakeholder analysis (identified roles, responsibilities)
   - Competitive positioning (technical advantages)
   - Evolution narrative (maturity assessment, growth trajectory)

2. **Sub-Plan 10: Recommendations Tab (3 days)**
   - Priority recommendations (top 10 sorted by impact, effort estimates, ROI)
   - Technical debt analysis (total debt, debt ratio, hotspots, payoff roadmap)
   - Refactoring opportunities (code smells, duplicates, suggested patterns)
   - Modernization suggestions (deprecated APIs, EOL frameworks, alternatives)
   - Performance improvements (slow paths, N+1 queries, caching opportunities)
   - Security hardening (top recommendations, quick wins)
   - Testing improvements (uncovered paths, missing categories, flaky tests)

3. **Sub-Plan 11: Architecture Tab (4 days)**
   - Architecture overview (detected type, layer breakdown, component count)
   - Component diagram (D3.js with layer positioning)
   - Dependency graph (module-level force layout, circular detection)
   - Design patterns (detected patterns, locations, anti-patterns)
   - Layer analysis (violations, dependency direction validation)
   - API surface catalog (public APIs, versioning, breaking changes)

4. **Sub-Plan 12: Code Organization Tab (3-4 days)**
   - File structure tree (D3.js expandable hierarchy)
   - Module breakdown (LOC by module, complexity, coverage)
   - Naming conventions (consistency score, violations, refactoring suggestions)
   - Code metrics (file size distribution, largest files, thresholds)
   - Directory metrics (depth, nested complexity, reorganization recommendations)
   - Code duplication detection (percentage, blocks, similar code)

5. Git checkpoint: `[CORTEX-LENS][PHASE-4] Advanced tabs complete`

**TDD Requirements:**
- [ ] RED: Write failing tests for use case synthesis
- [ ] GREEN: Implement use case extraction from code patterns
- [ ] REFACTOR: Extract narrative utilities
- [ ] RED: Write failing tests for technical debt calculation
- [ ] GREEN: Implement debt analyzer with payoff roadmap
- [ ] REFACTOR: Consolidate recommendation utilities
- [ ] Test coverage: 85% for advanced tab logic

---

### Phase 5: Template Unification (Week 9-10, 10 days)
**Corresponds to:** Sub-Plan 13

**Deliverables:**
1. Updated `console_app` template with 8 tabs
2. Updated `api_service` template with 8 tabs
3. New `fullstack_web` template (~1,200 LOC)
4. New `library_package` template (~1,000 LOC)
5. New `database_project` template (~1,100 LOC)
6. New `microservices` template (~1,300 LOC)
7. Unified manifest structure
8. Template selection logic updates

**DoD:**
- [ ] All 6 templates have 8-tab structure
- [ ] Sidebar navigation integrated in all templates
- [ ] Glassmorphism 125% scale applied uniformly
- [ ] D3.js visualizations render in all templates
- [ ] Template-specific customizations implemented
- [ ] Selenium tests pass for all 6 templates
- [ ] Git checkpoint created

**Tasks:**
1. **Sub-Plan 13: Template Unification (6-7 days)**
   - Update `console_app`: Add 6 new tabs (Executive, Overview, Tech Stack, Security, Use Cases, Recommendations, Architecture, Code Org)
   - Update `api_service`: Add 6 new tabs + emphasize endpoint catalog
   - Create `fullstack_web`: 8 tabs + frontend/backend split view + route mapping
   - Create `library_package`: 8 tabs + public API reference + usage examples
   - Create `database_project`: 8 tabs + schema ERD + migration history + query performance
   - Create `microservices`: 8 tabs + service topology + inter-service communication + event bus viz
   - Apply sidebar navigation to all templates
   - Apply glassmorphism 125% scale uniformly
   - Integrate all D3.js visualizations
   - Add progressive loading to all
   - Implement keyboard navigation across all

2. Git checkpoint: `[CORTEX-LENS][PHASE-5] Template unification complete`

**TDD Requirements:**
- [ ] RED: Write failing tests for each template's 8-tab structure
- [ ] GREEN: Implement unified tab structure with template-specific customizations
- [ ] REFACTOR: Extract shared tab components to base template
- [ ] Test coverage: 85% for template rendering logic

---

### Phase 6: Component Library & Optimization (Week 11-12, 10 days)
**Corresponds to:** Sub-Plans 14-15

**Deliverables:**
1. 26 production components (~3,500 LOC)
2. Component documentation with examples
3. Performance optimization utilities (~800 LOC)
4. Benchmarking suite
5. Performance dashboard

**DoD:**
- [ ] All 26 components functional and tested
- [ ] Component documentation complete with Storybook-style examples
- [ ] Multi-threading implemented for file parsing
- [ ] Caching strategies applied (FileCache)
- [ ] Progressive loading working (lazy tab loading)
- [ ] Virtual scrolling functional for large tables
- [ ] Performance targets met (see below)
- [ ] Git checkpoint created

**Performance Targets:**
- Dashboard generation: <2min (10K LOC), <5min (100K LOC), <30min (1M LOC)
- Dashboard load: <3s (first paint), <5s (interactive)
- Tab switch: <500ms
- Visualization render: <1s (initial), <200ms (interactions)
- Memory usage: <100MB (dashboard), <500MB (generation)

**Tasks:**
1. **Sub-Plan 14: Component Library v2 (5-6 days)**
   - Core components (20): LoadingSpinner, SkeletonLoader, ProgressBar, Modal, Tooltip, Toast, Dropdown, DatePicker, SearchBox, Pagination, InfiniteScroll, VirtualScroll, Breadcrumbs, Stepper, Accordion, Carousel, Badge, Avatar, FileUpload, CodeBlock
   - Admin components (6): ProgressiveLoader, ExportUtils, AdaptiveVisibility, KeyboardNavigation, ThemeToggle, DataGrid
   - Lens-specific components (6): HealthScoreRing, TrendIndicator, SecurityBadge, DependencyStatus, CoverageBar, ComplexityGauge
   - TypeScript declarations for all components
   - ARIA attributes and keyboard navigation
   - Theme support (dark/light)
   - Unit tests for each component

2. **Sub-Plan 15: Performance Optimization (4-5 days)**
   - Generation optimization: Multi-threaded file parsing, incremental analysis, smart caching, parallel collectors
   - Rendering optimization: Virtual scrolling, progressive loading, lazy tab loading, code splitting, minification
   - Data optimization: JSON chunking, IndexedDB caching, streaming parsing, pagination
   - Visualization optimization: Canvas rendering for large graphs, LOD for zoom, culling offscreen elements
   - Asset optimization: Image compression (WebP), CSS purging, JS tree shaking, font subsetting
   - Memory management: Object pooling, GC optimization, leak detection

3. Git checkpoint: `[CORTEX-LENS][PHASE-6] Components & optimization complete`

**TDD Requirements:**
- [ ] RED: Write failing tests for each component's key interactions
- [ ] GREEN: Implement components with ARIA support
- [ ] REFACTOR: Extract shared component utilities
- [ ] RED: Write performance benchmark tests (fail if targets missed)
- [ ] GREEN: Implement optimizations (multi-threading, caching, virtual scrolling)
- [ ] REFACTOR: Consolidate optimization utilities
- [ ] Test coverage: 90% for component library, 80% for optimization utilities

---

### Phase 7: End-to-End Validation & Release (Week 13-14, 10 days)
**Corresponds to:** Sub-Plan 16

**Deliverables:**
1. Expanded Selenium test suite (~1,500 LOC, 60+ tests)
2. Performance benchmark report
3. Accessibility audit report (WCAG 2.1 AAA compliance)
4. Cross-browser compatibility matrix
5. User acceptance test results
6. v3.0 release validation report

**DoD:**
- [ ] All 6 templates validated with real repositories
- [ ] All visualizations tested with edge cases
- [ ] All 26 components verified in isolation and integration
- [ ] Performance targets met across 10K, 100K, 500K, 1M LOC repos
- [ ] WCAG 2.1 AAA compliance achieved (screen reader tested)
- [ ] Cross-browser compatibility confirmed (Chrome, Firefox, Safari, Edge)
- [ ] Selenium suite: 60+ tests, 95%+ pass rate
- [ ] Zero console errors across all tests
- [ ] Git checkpoint created
- [ ] Release tagged: `v3.0.0`

**Tasks:**
1. **Sub-Plan 16: E2E Validation (5-6 days)**
   - Template validation: Test all 6 templates with real repos (Console App 5-10K, API Service 20-50K, Full-Stack Web 100K+, Library 10-30K, Database 5-15K, Microservices 50-100K)
   - Visualization validation: Test all D3.js components with real data, Chart.js presets, Three.js brain, export functionality
   - Component validation: Test all 26 components in isolation, verify interactions, keyboard nav, ARIA, theme switching
   - Performance validation: Benchmark on 10K, 100K, 500K, 1M LOC repos, memory profiling, load time measurement
   - Accessibility validation: WCAG 2.1 AAA compliance, screen reader testing, keyboard-only navigation, color contrast
   - Cross-browser validation: Chrome, Firefox, Safari, Edge, mobile browsers
   - Selenium test suite expansion: Add tests for all 8 tabs, sidebar, visualizations, export, keyboard nav

2. Git checkpoint: `[CORTEX-LENS][PHASE-7] E2E validation complete`

3. Release: Tag `v3.0.0`, update CHANGELOG.md, publish documentation

**TDD Requirements:**
- [ ] RED: Write comprehensive E2E tests (60+ scenarios)
- [ ] GREEN: Ensure all tests pass (95%+ pass rate)
- [ ] REFACTOR: Consolidate test utilities, remove duplicates
- [ ] Final test coverage: 85%+ across entire CORTEX Lens codebase

---

## ✅ Definition of Done (DoD)

**Feature Acceptance Criteria:**
1. ✅ All 16 sub-plans completed with timestamps
2. ✅ Master progress tracker shows 100%
3. ✅ All 6 templates have 8-tab structure
4. ✅ Glassmorphism 125% scale applied uniformly
5. ✅ Sidebar navigation working across all templates
6. ✅ All D3.js visualizations rendering with real data
7. ✅ 26 components functional and tested
8. ✅ Performance targets met (see Phase 6)
9. ✅ Selenium test suite: 60+ tests, 95%+ pass rate
10. ✅ WCAG 2.1 AAA compliance achieved
11. ✅ Zero dependencies on admin dashboard
12. ✅ Zero console errors in browser
13. ✅ All assets loading correctly
14. ✅ Responsive design validated
15. ✅ Cross-browser compatibility confirmed
16. ✅ Documentation complete

**Code Quality:**
- [ ] Test coverage ≥85% (per-layer validation)
- [ ] Zero critical/high security vulnerabilities
- [ ] Zero code smells (SonarQube clean)
- [ ] All Selenium tests passing (95%+ pass rate)
- [ ] Performance benchmarks met (see Phase 6)

**Documentation:**
- [ ] All 16 sub-plan documents created
- [ ] Master plan (this document) updated after each phase
- [ ] Component documentation with examples
- [ ] Visualization guides
- [ ] Performance optimization guide
- [ ] Accessibility compliance report
- [ ] User acceptance test results

**Release Readiness:**
- [ ] CHANGELOG.md updated
- [ ] Version tagged: `v3.0.0`
- [ ] Release notes published
- [ ] Admin dashboard remains stable (no regressions)
- [ ] v2.5 templates continue working

---

## 📦 Deliverables Summary

**Code:**
- 6 unified templates (~6,800 LOC)
- 26 production components (~3,500 LOC)
- 6 D3.js visualizations (~1,200 LOC)
- 8 tab implementations (~7,000 LOC)
- Performance utilities (~800 LOC)
- Test suites (~1,500 LOC)
- **Total:** ~21,000 LOC

**Documentation:**
- 16 sub-plan documents
- Master plan (this document)
- Component documentation
- Visualization guides
- Performance optimization guide
- Accessibility compliance report
- User acceptance test results

**Tests:**
- 60+ Selenium tests
- Performance benchmarks
- Cross-browser validation
- Accessibility audits

---

## 🚀 Execution Timeline

**Total Duration:** 13-14 weeks (65-70 working days)

| Week | Phase | Sub-Plans | Duration | Deliverables |
|------|-------|-----------|----------|--------------|
| 1 | Phase 0: Planning | Preparation | 5 days | Manifest, strategy, roadmap |
| 2 | Phase 1: Foundation | SP-1, SP-2 | 5 days | Design extraction, typography |
| 3-4 | Phase 2: Navigation & Viz | SP-3, SP-4 | 8 days | Sidebar, D3.js stack |
| 5-6 | Phase 3: Core Tabs | SP-5, SP-6, SP-7, SP-8 | 10 days | 4 tabs implemented |
| 7-8 | Phase 4: Advanced Tabs | SP-9, SP-10, SP-11, SP-12 | 9 days | 4 tabs implemented |
| 9-10 | Phase 5: Template Unification | SP-13 | 10 days | 6 unified templates |
| 11-12 | Phase 6: Components & Perf | SP-14, SP-15 | 10 days | 26 components, optimization |
| 13-14 | Phase 7: E2E Validation | SP-16 | 10 days | 60+ tests, release |

---

## 🔗 Integration Points

**Planning System v3.0 Integration:**
- Orchestrator: `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`
- State machine: INITIALIZED → VALIDATING_DOR → EXECUTING → VALIDATING_DOD → COMPLETED
- Session persistence: SQLite-backed state recovery
- Manifest: `cortex-brain/manifests/orchestrators/cortex-lens-v3-manifest.yaml` (to be created)

**TDD Orchestrator Integration:**
- RED→GREEN→REFACTOR enforced at every phase
- Per-layer coverage validation (85% target)
- Empty test detection
- Test template library usage

**Git Checkpoint Integration:**
- Automatic checkpoint after each phase completion
- Commit format: `[CORTEX-LENS][PHASE-X] Description`
- Recovery from interruption supported

**Quality Assurance Integration:**
- Architectural review before Phase 0
- Code review after each phase
- Security assessment for Security tab (Phase 3)
- Performance benchmarking (Phase 6)

---

### Phase 8: Documentation Distillation Dashboard (Week 15-16, 8 days) 🆕
**NEW ENHANCEMENT - Post-v3.0 Release**

**Strategic Goal:**
Create a second dashboard using the SAME architecture and generator as CORTEX Lens, but specialized for distilling complex documentation (like CORTEX's own brain files, planning documents, and guides) into easily readable visual tabs with smart summarization.

**Use Case:**
- Distill complex technical documentation into visual summaries
- Provide tabbed navigation through large document collections
- Auto-generate visual hierarchies from markdown files
- Create interactive documentation explorers
- Support multi-file documentation projects

**Architecture Reuse:**
- ✅ Same glassmorphism design system (inherited from Phase 1)
- ✅ Same 8-tab navigation pattern (inherited from Phase 2)
- ✅ Same D3.js visualization stack (inherited from Phase 2)
- ✅ Same template generator architecture (inherited from Phase 5)
- ✅ Same component library (inherited from Phase 6)
- ✅ Same zero-dependency philosophy

**Deliverables:**
1. Documentation parser (Markdown → structured data)
2. Smart summarization module (extract key points, TOC, relationships)
3. 8-tab documentation dashboard template:
   - 📚 **Overview** - Document hierarchy tree (D3.js)
   - 📊 **Structure** - Content breakdown (sunburst chart)
   - 🔗 **Relationships** - Cross-reference graph (force layout)
   - 📝 **Summaries** - Auto-generated summaries per document
   - 🔍 **Search** - Full-text search with highlighting
   - 🎯 **Key Points** - Extracted insights (cards)
   - 📈 **Metrics** - Document stats (word count, complexity, readability)
   - 💾 **Export** - Generate static site / PDF

4. New template: `cortex_lens_docs` (~800 LOC)
5. Documentation-specific visualizations (~600 LOC)
6. Integration with existing CORTEX Lens generator

**Implementation Instructions:**

**Step 1: Extend Template System (2 days)**
```python
# src/cortex_lens/templates/cortex_lens_docs/template.py
from src.cortex_lens.templates.base.base_template import BaseTemplate

class DocsDistillationTemplate(BaseTemplate):
    \"\"\"
    Documentation distillation template - inherits from BaseTemplate.
    Reuses glassmorphism, typography, navigation from v3.0.
    \"\"\"
    
    def __init__(self):
        super().__init__(template_name="cortex_lens_docs")
        self.tabs = [
            "overview", "structure", "relationships", "summaries",
            "search", "key-points", "metrics", "export"
        ]
    
    def generate(self, docs_path: str) -> str:
        # Parse markdown files
        docs = self._parse_documentation(docs_path)
        
        # Generate visualizations
        hierarchy = self._generate_hierarchy_viz(docs)
        structure = self._generate_structure_viz(docs)
        relationships = self._generate_relationship_graph(docs)
        
        # Smart summarization
        summaries = self._extract_summaries(docs)
        key_points = self._extract_key_points(docs)
        
        # Generate HTML using base template + docs-specific tabs
        return self._render_template(
            tabs_data={
                "overview": hierarchy,
                "structure": structure,
                "relationships": relationships,
                "summaries": summaries,
                "search": self._generate_search_index(docs),
                "key_points": key_points,
                "metrics": self._calculate_metrics(docs),
                "export": self._generate_export_config()
            }
        )
```

**Step 2: Documentation Parser (1 day)**
```python
# src/cortex_lens/parsers/markdown_parser.py
class MarkdownDocumentationParser:
    \"\"\"Parse markdown files and extract structure, metadata, relationships.\"\"\"
    
    def parse(self, docs_path: str) -> List[Document]:
        # Walk directory tree
        # Parse each .md file (frontmatter, headers, content, links)
        # Extract cross-references
        # Build document graph
        pass
```

**Step 3: Smart Summarization (2 days)**
```python
# src/cortex_lens/analysis/doc_summarizer.py
class DocumentSummarizer:
    \"\"\"Extract key points, summaries, and insights from documentation.\"\"\"
    
    def summarize(self, document: Document) -> Summary:
        # Extract headers → generate TOC
        # Identify key terms (TF-IDF)
        # Extract code blocks, diagrams, tables
        # Calculate readability score (Flesch-Kincaid)
        # Detect document type (guide, reference, API, planning)
        pass
```

**Step 4: Documentation Visualizations (2 days)**
- Reuse D3.js components from Phase 2
- Add document-specific viz:
  - Hierarchy tree (file structure)
  - Relationship graph (cross-references)
  - Content sunburst (section sizes)
  - Readability heatmap

**Step 5: CLI Integration (1 day)**
```bash
# New command
python -m src.cortex_lens generate --template cortex_lens_docs --input ./cortex-brain/documents/

# Output: cortex-lens-output/docs-dashboard.html
```

**DoR (Definition of Ready):**
- [ ] Phase 0-7 completed and v3.0 released
- [ ] Markdown parser API contract defined
- [ ] Summarization algorithm researched (extractive vs. abstractive)
- [ ] Visualization requirements validated with sample docs

**DoD (Definition of Done):**
- [ ] `cortex_lens_docs` template implemented and tested
- [ ] Documentation parser handles 500+ markdown files
- [ ] Smart summarization generates accurate summaries (manual validation on 20 samples)
- [ ] All 8 tabs render correctly with real CORTEX documentation
- [ ] Export to static site / PDF working
- [ ] Selenium tests pass (12+ tests for docs-specific features)
- [ ] Integration with main generator CLI complete
- [ ] Documentation guide written

**Success Metrics:**
- Parse 500+ markdown files in < 10 seconds
- Generate dashboard HTML < 5MB
- Summarization accuracy ≥ 80% (human evaluation)
- Zero dependencies (like CORTEX Lens v3.0)

**Future Extensions (Optional):**
- AI-powered summarization (GPT-4 integration)
- Collaborative annotation (comments on docs)
- Version comparison (diff between doc versions)
- Multi-language support (translate docs)

---

## 📊 Progress Tracking

**Master Progress Tracker:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CORTEX LENS v3.0 - PLANNING SYSTEM V3.0 EXECUTION                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ Phase 0: Planning & Preparation        [░░░░░░░░░░░░░░░░░░░░]   0%    │
│ Phase 1: Foundation                    [░░░░░░░░░░░░░░░░░░░░]   0%    │
│ Phase 2: Navigation & Visualizations   [░░░░░░░░░░░░░░░░░░░░]   0%    │
│ Phase 3: Core Tabs                     [░░░░░░░░░░░░░░░░░░░░]   0%    │
│ Phase 4: Advanced Tabs                 [░░░░░░░░░░░░░░░░░░░░]   0%    │
│ Phase 5: Template Unification          [░░░░░░░░░░░░░░░░░░░░]   0%    │
│ Phase 6: Components & Optimization     [░░░░░░░░░░░░░░░░░░░░]   0%    │
│ Phase 7: E2E Validation & Release      [░░░░░░░░░░░░░░░░░░░░]   0%    │
│ Phase 8: Docs Distillation Dashboard  [░░░░░░░░░░░░░░░░░░░░]   0%    │
│          (NEW ENHANCEMENT)                                               │
│                                                                          │
│ ════════════════════════════════════════════════════════════════════════ │
│ OVERALL PROGRESS:  [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   0%     │
└─────────────────────────────────────────────────────────────────────────┘
```

**Status:** 🎯 READY FOR EXECUTION  
**Overall Completion:** 0% | **Started:** TBD | **Target:** Week 15-17 (Jan 2026)

---

## 🎯 Success Criteria

**v3.0 is considered complete when:**
1. ✅ All 7 phases (0-7) completed with DoD validation
2. ✅ Master progress tracker shows 100% (excluding Phase 8)
3. ✅ All 16 acceptance criteria met (see DoD section)
4. ✅ Planning System v3.0 validates plan as COMPLETED state
5. ✅ Release tagged: `v3.0.0`

**Phase 8 (Documentation Distillation Dashboard) is separate post-release enhancement:**
- Can be executed independently after v3.0 release
- Uses v3.0 architecture as foundation
- Extends CORTEX Lens capabilities to documentation analysis
- Optional feature (not required for v3.0 completion)

---

## 🔄 Update Protocol

**After completing each phase:**

1. **Update this file** (`CORTEX-LENS-V3.0-MASTER-PLAN.md`):
   ```markdown
   **Status:** ✅ COMPLETE  
   **Started:** 2025-12-XX HH:MM EST  
   **Completed:** 2025-12-XX HH:MM EST  
   **Progress:** 100%
   ```

2. **Update progress tracker:**
   ```
   Phase X: Name  [████████████████████]  100%
   ```

3. **Update overall completion:**
   ```
   OVERALL PROGRESS:  [███░░░░░░░...]  12.5%  (1/8)
   ```

4. **Git commit format:**
   ```bash
   git commit -m "[CORTEX-LENS][PHASE-X] Brief description

   DoR Validated: Yes
   DoD Validated: Yes
   Test Coverage: XX%
   LOC Added: XXX
   Tests Added: XX

   Started: YYYY-MM-DD HH:MM EST
   Completed: YYYY-MM-DD HH:MM EST
   Duration: X.X days"
   ```

5. **Update Planning System v3.0 session:**
   ```python
   session_manager.update_phase_status(
       phase_name="Phase X",
       status="completed",
       tokens_used=XXX
   )
   ```

---

## 🔗 References

**Admin Dashboard:**
- `cortex-brain/dashboards/ui/index.html`
- `cortex-brain/dashboards/ui/styles/` (8 CSS layers)
- `cortex-brain/dashboards/ui/components/`

**CORTEX Lens v2.5:**
- `cortex-brain/documents/planning/archived/sessions/cortex-lens-plan-v3.md` (original v3 plan)
- `src/cortex_lens/` (current codebase)
- `src/cortex_lens/templates/` (2 templates complete)

**Planning System v3.0:**
- `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`
- `src/orchestration_3_0/README.md`
- `cortex-brain/manifests/orchestrators/planning-system-manifest.yaml` (to be replaced with v3.0 manifest)

**Design System:**
- Glassmorphism patterns
- 125% typography scale
- CSS variables system
- Component architecture

---

**Master Plan Status:** 🎯 READY FOR EXECUTION  
**Last Updated:** 2025-12-14 EST  
**Next Update:** Upon completion of Phase 0

---

*This is the definitive v3.0 master plan aligned with Planning System v3.0 (`orchestration_3_0`). All work must reference and update this document. DoR/DoD gates will be enforced by Planning Orchestrator.*
