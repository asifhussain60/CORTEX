# 🗺️ Repository Dashboard Redesign: Implementation Roadmap
**Phase:** PLANNING | **Authority:** CORTEX Architecture | **Date:** 2026-02-08

---

## 📋 Project Overview

**Project:** CORTEX Repository Dashboard SPA Redesign  
**Current Status:** ✅ Design Complete  
**Next Phase:** IMPLEMENT (S1: Foundation)  
**Total Effort:** ~17 days (6 weeks part-time, or 2-3 weeks full-time)  
**Team Size:** 1-2 engineers  
**Success Metric:** 9-tab dashboard rendering correctly with full data binding + 150+ tests passing  

---

## 🎯 Phase Breakdown

### Phase S1: Foundation & Schema (2 days)
**Objective:** Establish data model and design system

**Deliverables:**
- [ ] `repo-dashboard-schema.json` — Complete JSON schema for all 9 tabs
- [ ] `pydantic_schema.py` — Validation models (DashboardSchema, Metadata, etc.)
- [ ] `design-tokens.css` — CSS custom properties matching approved-orchestrator-view
- [ ] `component-library.css` — 8+ reusable components
- [ ] `responsive-layout.css` — Mobile-first grid system
- [ ] Unit tests for schema validation (15 tests)

**Key Tasks:**
1. Define JSON schema structure (nested objects for each tab)
2. Create Pydantic models with validation rules
3. CSS variables: colors, spacing, typography, shadows
4. Component styles: glass-card, metric-card, badges, buttons, tables
5. Responsive breakpoints: 320px, 480px, 768px, 1024px, 1600px
6. Write schema validation tests

**Files to Create:**
```
cortex-registry/_cortex-master/dashboard/
├── schema/
│   ├── repo-dashboard-schema.json
│   └── pydantic_schema.py
└── css/
    ├── design-tokens.css
    ├── component-library.css
    └── responsive-layout.css
```

**Success Criteria:**
- ✅ All 9 tabs defined in schema
- ✅ 15 validation tests passing
- ✅ Pydantic models reject invalid data
- ✅ CSS variables used throughout (no hardcoded colors)

---

### Phase S2: Core Tabs (3 days)
**Objective:** Implement first 3 tabs with data binding

**Deliverables:**
- [ ] `repo-dashboard-core.html` — Main SPA (Overview, Architecture, Quality tabs)
- [ ] `tab-data-binder.js` — Framework to map JSON to templates
- [ ] `metrics-renderer.js` — Render metric cards from JSON
- [ ] Tab navigation with smooth transitions
- [ ] 25 unit tests + 5 integration tests

**Key Tasks:**
1. Build HTML structure (header, tab nav, content areas)
2. Implement data binding (JSON → DOM)
3. Create template functions (metric-card, audience-card, etc.)
4. Style with design-tokens.css
5. Implement tab switching with fade transitions
6. Test with sample data

**Tabs to Implement:**
- **Overview (📊):** Metrics grid, audience cards, health badges
- **Architecture (🏗️):** Layer descriptions, module list (D3 placeholder)
- **Quality (✅):** Code quality score, coverage progress bar, complexity table

**Files to Create:**
```
_workspaces/dashboard/
├── repo-dashboard-core.html
├── js/
│   ├── tab-data-binder.js
│   ├── metrics-renderer.js
│   └── component-renderer.js
└── data/
    └── sample-data.json
```

**Sample Data Structure (JSON):**
```json
{
  "metadata": {
    "name": "KSESSIONS",
    "primary_language": "C#",
    "total_files": 26434,
    "total_lines": 3658465,
    "contributors": 30
  },
  "overview": {
    "health_score": 85,
    "code_quality": 8.5,
    "test_coverage": 83.0,
    "maintainability_index": 66.1,
    "languages": {
      "C#": 75880,
      "TypeScript": 29043,
      "JavaScript": 12808
    }
  }
}
```

**Success Criteria:**
- ✅ Overview tab renders all metrics from JSON
- ✅ Tab switching smooth (<500ms)
- ✅ Data binding tests passing (25 tests)
- ✅ Glassmorphism styling applied consistently

---

### Phase S3: Analysis Tabs (3 days)
**Objective:** Implement 4 analysis tabs with tables and visualizations

**Deliverables:**
- [ ] `security-tabs.html` — Security, Vulnerabilities, Dependencies, Testing tabs
- [ ] `data-table-renderer.js` — Flexible table generation from JSON
- [ ] Vulnerability matrix (OWASP table)
- [ ] Dependency list with status badges
- [ ] Test coverage visualization (progress bars)
- [ ] 30 unit tests

**Key Tasks:**
1. Extend HTML with 4 new tab sections
2. Create data-table-renderer for flexible tables
3. Implement vulnerability severity coloring
4. Build progress bars with percentages
5. Create badge system (success, warning, danger, info)
6. Test with security scan data

**Tabs to Implement:**
- **Vulnerabilities (🛡️):** Vulnerability counts, OWASP table, CVE list
- **Security (🔒):** Security score, compliance status, authentication info
- **Dependencies (📦):** Package table, license matrix, outdated counts
- **Testing (🧪):** Coverage progress, test counts, coverage by module table

**Files to Create:**
```
_workspaces/dashboard/js/
├── data-table-renderer.js
├── badge-system.js
├── vulnerability-renderer.js
└── progress-bar.js
```

**Success Criteria:**
- ✅ All 4 tabs render data from JSON
- ✅ Tables sort/filter (basic implementation)
- ✅ Badge colors correct for severity levels
- ✅ 30 integration tests passing

---

### Phase S4: Patterns & Use Cases (3 days)
**Objective:** Implement final 2 tabs + LLM framework

**Deliverables:**
- [ ] `patterns-usecases.html` — Patterns, Use Cases tabs complete
- [ ] `code-to-business-transformer.py` — LLM orchestration for capability detection
- [ ] `business-capability-detector.py` — Pattern matching engine
- [ ] `llm-prompt-templates.yaml` — Capability generation prompts
- [ ] Use case cards with business language
- [ ] SOLID principles radar chart (D3 placeholder)
- [ ] 20 unit tests

**Key Tasks:**
1. Implement Patterns tab (design patterns, anti-patterns, SOLID gauge)
2. Implement Use Cases tab (capability cards, actor mapping)
3. Build LLM integration framework (async capability detection)
4. Create pattern detection rules (YAML)
5. Build business language transformer
6. Test with real code analysis data

**Tabs to Implement:**
- **Patterns (🎨):** Design patterns, anti-patterns, refactoring opportunities, SOLID score
- **Use Cases (📋):** Business capabilities, stakeholder mapping, business flows, integrations

**Files to Create:**
```
cortex/orchestrators/onboarding/
├── code-to-business-transformer.py
├── business-capability-detector.py
├── prompts/
│   ├── capability-generation.yaml
│   ├── impact-analysis.yaml
│   └── persona-summaries.yaml
└── patterns/
    ├── authentication-patterns.yaml
    ├── reporting-patterns.yaml
    └── integration-patterns.yaml
```

**Sample LLM Prompt:**
```yaml
capability_detection:
  template: |
    Analyze this technical capability cluster and describe it in business language:
    
    Technical Signals:
    - API Endpoints: {endpoints}
    - Database Operations: {db_ops}
    - Integrations: {integrations}
    - Domain Objects: {entities}
    
    Generate:
    1. Business capability name
    2. 1-2 sentence description for executives
    3. Business value proposition
    4. Primary actors/beneficiaries
    5. Associated processes
    
    Format: JSON
  temperature: 0.7
  model: gpt-4
```

**Success Criteria:**
- ✅ Patterns tab renders all design patterns from JSON
- ✅ Use Cases tab shows LLM-generated capabilities
- ✅ SOLID principles displayed (placeholder for D3 radar)
- ✅ 20 tests passing

---

### Phase S5: D3.js Visualizations (5 days)
**Objective:** Implement 7 interactive D3.js charts

**Deliverables:**
- [ ] `d3-visualizations.js` — All 7 chart implementations
- [ ] Chart-specific configs (colors, sizes, transitions)
- [ ] Interactive tooltips for all charts
- [ ] Legends with series toggling
- [ ] Responsive scaling (resize → redraw)
- [ ] 35 integration tests

**Key Tasks:**
1. Implement Sunburst chart (language distribution)
2. Implement Force-directed graph (dependencies)
3. Implement Treemap (module complexity)
4. Implement Heatmap (test coverage by module)
5. Implement Sankey diagram (data flow)
6. Implement Timeline (commit history)
7. Implement Radar chart (SOLID principles)
8. Add interactive features (hover, click, legend)
9. Ensure responsive sizing

**Chart Integration:**
- **Overview tab:** Sunburst (language distribution)
- **Architecture tab:** Force-directed (dependency graph) + Treemap (modules)
- **Quality tab:** Heatmap (coverage), Timeline (trends)
- **Security tab:** Radar (compliance frameworks)
- **Dependencies tab:** Force-directed (package graph)
- **Testing tab:** Heatmap (coverage by module)
- **Patterns tab:** Radar (SOLID principles)

**Files to Create:**
```
_workspaces/dashboard/js/
├── d3-visualizations.js
├── charts/
│   ├── sunburst.js
│   ├── force-directed.js
│   ├── treemap.js
│   ├── heatmap.js
│   ├── sankey.js
│   ├── timeline.js
│   └── radar.js
├── chart-configs.json
└── interactive-legends.js
```

**Sample D3 Chart (Sunburst):**
```javascript
function createSunburst(containerId, data) {
  const width = document.getElementById(containerId).clientWidth;
  const height = 500;
  const radius = Math.min(width, height) / 2;
  
  const svg = d3.select(`#${containerId}`).append('svg')
    .attr('width', width)
    .attr('height', height);
  
  const g = svg.append('g')
    .attr('transform', `translate(${width/2},${height/2})`);
  
  const partition = d3.partition()
    .size([2 * Math.PI, radius]);
  
  const root = d3.hierarchy(data)
    .sum(d => d.value)
    .sort((a, b) => b.value - a.value);
  
  partition(root);
  
  // Render arcs
  g.selectAll('path')
    .data(root.descendants())
    .enter()
    .append('path')
    .attr('d', d3.arc()
      .startAngle(d => d.x0)
      .endAngle(d => d.x1)
      .innerRadius(d => d.y0)
      .outerRadius(d => d.y1))
    .attr('fill', (d, i) => d3.schemeCategory10[i % 10])
    .on('mouseover', function() { d3.select(this).attr('opacity', 0.8); })
    .on('mouseout', function() { d3.select(this).attr('opacity', 1); });
}
```

**Success Criteria:**
- ✅ All 7 charts render correctly
- ✅ Charts responsive to container resize
- ✅ Tooltips show contextual data
- ✅ Legend toggles work
- ✅ 35 tests passing

---

### Phase S6: Polish & Integration (4 days)
**Objective:** Production readiness, orchestrator integration, documentation

**Deliverables:**
- [ ] `repo-dashboard-final.html` — Production-ready SPA (all 9 tabs complete)
- [ ] `orchestrator-integration.py` — RepoOnboardingOrchestrator hooks
- [ ] `performance-guide.md` — Optimization strategies
- [ ] `accessibility-audit.md` — WCAG 2.1 AA compliance checklist
- [ ] `deployment-guide.md` — How to generate/host dashboards
- [ ] `component-api.md` — Developer documentation
- [ ] `data-schema-spec.md` — JSON schema reference
- [ ] E2E test suite (Playwright/Cypress)
- [ ] 25+ tests

**Key Tasks:**
1. RepoOnboardingOrchestrator integration
   - Hook into onboarding pipeline
   - Generate dashboard JSON after LENS analysis
   - Store dashboard data in cortex-registry
2. Performance optimization
   - Lazy load D3.js visualizations (Intersection Observer)
   - Virtual scroll for large tables
   - Debounce resize handlers
   - Cache JSON data locally
3. Accessibility audit
   - Color contrast verification (4.5:1 for text)
   - Keyboard navigation (Tab, Arrow keys)
   - ARIA labels + roles
   - Screen reader testing
4. Mobile testing
   - iOS Safari, Chrome
   - Android Chrome
   - Touch interactions verified
5. Documentation
   - Component library API
   - Data schema specification
   - Deployment instructions
   - LLM integration guide
6. E2E testing
   - Tab switching
   - Data rendering
   - D3 chart interactions
   - Responsive layout

**Orchestrator Integration Code:**
```python
# cortex/orchestrators/onboarding/repo_onboarding_orchestrator.py

@orchestrator_hook('onboarding:post_analysis')
async def generate_dashboard(lens_results: Dict, repo_metadata: Dict) -> str:
    """Generate dashboard JSON after LENS analysis"""
    
    # Transform LENS results into dashboard schema
    dashboard_data = transform_to_dashboard_schema(
        metadata=repo_metadata,
        analysis=lens_results
    )
    
    # Store in registry
    dashboard_path = save_dashboard_data(
        repo_name=repo_metadata['name'],
        data=dashboard_data
    )
    
    # Infer business capabilities (async)
    asyncio.create_task(
        infer_business_capabilities(dashboard_data, llm_client)
    )
    
    return dashboard_path

async def infer_business_capabilities(dashboard_data: Dict, llm_client):
    """Async task: Use LLM to detect business capabilities"""
    
    transformer = CodeToBusinessTransformer(llm_client)
    
    capabilities = await transformer.detect_capabilities(
        code_analysis={
            'patterns': dashboard_data['patterns']['design_patterns'],
            'modules': dashboard_data['architecture']['modules'],
            'integrations': dashboard_data['use_cases']['integrations']
        }
    )
    
    # Update dashboard with capabilities
    dashboard_data['use_cases']['detected_capabilities'] = capabilities
    save_dashboard_data(repo_name, dashboard_data)
```

**Files to Create:**
```
deployment/
├── dashboard-deployment.yaml
├── docker/
│   └── dashboard-server.Dockerfile
└── scripts/
    └── generate-dashboard.sh

docs/
├── api/
│   └── dashboard-schema-spec.md
├── guides/
│   ├── deployment-guide.md
│   ├── customization-guide.md
│   └── llm-integration-guide.md
└── troubleshooting/
    └── faq.md

tests/
├── e2e/
│   ├── dashboard.spec.js
│   ├── tab-navigation.spec.js
│   └── d3-interactions.spec.js
└── integration/
    └── orchestrator-integration.test.py
```

**Success Criteria:**
- ✅ Dashboard works in RepoOnboardingOrchestrator pipeline
- ✅ Performance: <3s initial load, <500ms tab switch
- ✅ Accessibility audit: WCAG 2.1 AA passing
- ✅ E2E tests: 25+ tests passing
- ✅ Mobile responsive on 320px - 1920px
- ✅ Documentation complete

---

## 📊 Test Strategy

### Unit Tests (80 tests total)
- **Schema validation:** 15 tests (valid/invalid data)
- **Component rendering:** 20 tests (metric-card, badge, progress-bar)
- **Data binding:** 15 tests (JSON → DOM mapping)
- **Business capability detection:** 20 tests (pattern matching, LLM prompts)
- **D3 chart configuration:** 10 tests (data transformation)

### Integration Tests (50 tests total)
- **Tab navigation:** 10 tests (switching, state preservation)
- **Data loading:** 10 tests (async loading, error handling)
- **Chart rendering:** 15 tests (D3 initialization, responsiveness)
- **Orchestrator integration:** 15 tests (hooks, data flow)

### E2E Tests (20 tests total)
- **User workflows:** 8 tests (dashboard navigation, interaction)
- **Performance:** 5 tests (load time, render speed)
- **Accessibility:** 4 tests (keyboard nav, screen reader)
- **Mobile:** 3 tests (touch, responsiveness)

**Total Coverage Target:** 90%+ (150+ tests passing)

---

## 🎯 Success Metrics

### Functionality
- ✅ All 9 tabs render correctly
- ✅ All metrics display from JSON schema
- ✅ All D3 charts interactive
- ✅ Tab switching <500ms
- ✅ Business capabilities auto-detected

### Quality
- ✅ 150+ tests passing
- ✅ 90%+ code coverage
- ✅ Zero 404 errors
- ✅ Zero console errors/warnings

### User Experience
- ✅ Glassmorphism theme consistent
- ✅ Animations smooth (60fps)
- ✅ Responsive 320px - 1920px
- ✅ Mobile touch-friendly
- ✅ WCAG 2.1 AA accessible

### Performance
- ✅ Initial load <3s
- ✅ Tab switch <500ms
- ✅ Lighthouse score >90
- ✅ Core Web Vitals green

### Integration
- ✅ RepoOnboardingOrchestrator hook working
- ✅ Dashboard auto-generated on onboarding
- ✅ LLM capability detection async
- ✅ MCP tools callable

---

## 📅 Timeline (Detailed)

### Week 1 (S1: Foundation)
- **Day 1:** JSON schema + Pydantic models
- **Day 2:** CSS tokens + component library, unit tests

### Week 2 (S2: Core Tabs)
- **Day 3:** HTML structure + tab navigation
- **Day 4:** Data binding framework + metrics renderer
- **Day 5:** Overview, Architecture, Quality tabs complete

### Week 3 (S3: Analysis Tabs)
- **Day 6:** Security, Vulnerabilities tabs
- **Day 7:** Dependencies, Testing tabs
- **Day 8:** Table renderer + badge system, integration tests

### Week 4 (S4: Patterns & Use Cases)
- **Day 9:** Patterns tab + SOLID gauge
- **Day 10:** Use Cases tab + LLM framework
- **Day 11:** Code-to-business transformer, prompt engineering

### Week 5-6 (S5: Visualizations)
- **Day 12-13:** Sunburst + Force-directed
- **Day 14-15:** Treemap + Heatmap
- **Day 16:** Sankey + Timeline + Radar
- **Day 17:** Interactive legends, responsive sizing

### Week 7 (S6: Polish)
- **Day 18:** Orchestrator integration
- **Day 19:** Performance optimization + accessibility audit
- **Day 20:** E2E tests + documentation
- **Day 21:** Buffer/polish/final testing

**Effort Summary:**
- Design: ✅ Complete (2 days)
- Implementation: 17 days
- Testing: Included in each phase
- **Total:** 19 days (6 weeks part-time, 2-3 weeks full-time)

---

## 🔄 Dependencies & Blockers

### External Dependencies
- [ ] D3.js v7+ (already in project)
- [ ] RepoOnboardingOrchestrator stable
- [ ] LENS multi-analyzer results consistent
- [ ] LLM client available (GPT-4 or equivalent)

### Internal Dependencies
- [ ] S1 → S2 (schema before rendering)
- [ ] S2 → S3 (data binding framework before complex tabs)
- [ ] S3 → S4 (core functionality before advanced features)
- [ ] S4 → S5 (LLM framework before D3 visualization)
- [ ] S5 → S6 (features complete before optimization)

### Potential Blockers
- ❌ **Missing LENS analyzer outputs** → Use mock data for testing
- ❌ **LLM API rate limits** → Implement caching + background jobs
- ❌ **Large repositories** → Use virtual scrolling for tables
- ❌ **Browser compatibility** → Test on Chrome, Firefox, Safari, Edge

---

## 💰 Resource Estimation

| Role | Effort | Rate | Total |
|------|--------|------|-------|
| Lead Architect (design) | 2 days | - | ✅ Complete |
| Senior Engineer (S1-S3) | 8 days | $150/hr | $9,600 |
| Senior Engineer (S4-S5) | 7 days | $150/hr | $8,400 |
| QA/Test Automation (S6) | 4 days | $120/hr | $3,840 |
| Technical Writer (docs) | 2 days | $100/hr | $1,600 |
| **Total** | **19 days** | - | **$23,440** |

*Assumes: 8-hour days, no overhead*

---

## 📞 Communication Plan

### Daily Standup (15 min)
- What's complete
- What's in progress
- Blockers

### Weekly Review (1 hour)
- Phase progress review
- Test results
- Performance metrics
- Adjustments to timeline

### Stakeholder Updates (Bi-weekly)
- Executive summary (1 page)
- Demo of completed features
- Updated timeline
- Risk assessment

---

## 🚀 Go-Live Readiness

**Pre-Launch Checklist:**
- [ ] All 9 tabs rendering correctly
- [ ] 150+ tests passing (90%+ coverage)
- [ ] Performance audit: <3s load, <500ms tab switch
- [ ] Accessibility audit: WCAG 2.1 AA passing
- [ ] Mobile testing: responsive 320px - 1920px
- [ ] Security scan: no vulnerabilities
- [ ] Documentation complete
- [ ] RepoOnboardingOrchestrator integration tested
- [ ] LLM capability detection working
- [ ] Stakeholder approval obtained

**Production Deployment:**
1. Deploy to cortex-registry/dashboards/
2. Update RepoOnboardingOrchestrator to generate dashboards
3. Enable automatic dashboard generation on repo onboarding
4. Monitor usage metrics and performance
5. Gather user feedback for future enhancements

---

## 📖 Next Documents to Review

1. **HOLISTIC_REDESIGN_2026-02-08.md** — Complete specification (1,726 lines)
2. **EXECUTIVE_SUMMARY_2026-02-08.md** — High-level overview
3. **This file (IMPLEMENTATION_ROADMAP_2026-02-08.md)** — Detailed breakdown

---

**Status:** ✅ Planning Complete | Ready for Implementation  
**Owner:** CORTEX Architect + Engineering Team  
**Approval:** Awaiting stakeholder sign-off  
**Start Date:** Recommended 2026-02-15  

---

*All planning artifacts are stored in:*  
`cortex-registry/_cortex-master/`
