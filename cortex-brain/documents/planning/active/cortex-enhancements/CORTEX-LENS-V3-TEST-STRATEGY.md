# CORTEX Lens v3.0 - Test Strategy Expansion Plan (12 → 60+ Tests)

**Version:** 1.0  
**Date:** December 14, 2025  
**Phase:** Phase 0 - Planning & Preparation  
**Status:** Strategy Defined  
**Target:** 85% test coverage across all CORTEX Lens v3.0 code

---

## 🎯 Objective

Expand Selenium test suite from 12 tests (v2.5) to 60+ tests (v3.0) covering all 8 tabs, 32 components, 6 visualizations, and cross-browser compatibility.

---

## 📊 Current State (v2.5)

**Existing Tests:** 12 Selenium tests in `tests/cortex_lens/`

1. `test_console_app_rendering` - Console app template loads
2. `test_api_service_rendering` - API service template loads
3. `test_tab_switching` - Tab navigation works
4. `test_mermaid_diagram_rendering` - Mermaid diagrams render
5. `test_health_metrics` - Health metrics display
6. `test_dependency_graph` - Basic dependency graph
7. `test_responsive_layout` - Mobile/desktop breakpoints
8. `test_export_html` - Export functionality
9. `test_search_functionality` - Search box works
10. `test_filter_functionality` - Filter dropdowns work
11. `test_code_snippet_syntax_highlighting` - Code blocks render
12. `test_loading_states` - Loading spinners show

**Coverage:** ~40% (focused on happy paths)

---

## 🚀 Target State (v3.0)

**Target Tests:** 60+ tests covering:
- 8-tab navigation (8 tests)
- 32 components (32 tests)
- 6 D3.js visualizations (6 tests)
- Cross-browser compatibility (4 browsers × 5 critical flows = 20 tests)
- Accessibility (WCAG 2.1 AAA) (10 tests)
- Performance benchmarks (6 tests)

**Target Coverage:** 85%+ across all modules

---

## 📋 Test Strategy by Phase

### Phase 1 Tests (Foundation - Design System & Typography)

**Tests to Add:** 5 tests

1. **test_typography_scale_125_percent**
   - Validate all font sizes are 125% of admin dashboard
   - Check `--scale-factor: 1.25` applied correctly
   - Verify responsive typography on mobile/desktop

2. **test_css_variables_loaded**
   - Verify ~200 CSS variables defined
   - Check glassmorphism variables present
   - Validate color, spacing, shadow variables

3. **test_glassmorphism_rendering**
   - Check `backdrop-filter` support in browsers
   - Verify glass-card, glass-sidebar render correctly
   - Test Safari fallback (-webkit-backdrop-filter)

4. **test_loading_animations**
   - Verify spinner, skeleton loader animations
   - Check keyframe animations defined
   - Test animation timing and easing

5. **test_3d_brain_rendering**
   - Check Three.js loads without errors
   - Verify brain mesh renders
   - Test rotation animation

---

### Phase 2 Tests (Navigation & Visualizations)

**Tests to Add:** 14 tests

**Sidebar Navigation (5 tests):**

6. **test_sidebar_navigation_8_sections**
   - Verify 8 navigation items present (📊 📚 ⚙️ 🔒 🎯 💡 🏗️ 📁)
   - Check icons render correctly
   - Test active state highlights

7. **test_sidebar_collapsible**
   - Test expanded/collapsed states
   - Verify transition animations
   - Check localStorage persistence of state

8. **test_sidebar_keyboard_navigation**
   - Tab through navigation items
   - Arrow keys navigate up/down
   - Enter activates item

9. **test_sidebar_responsive**
   - Auto-collapse on mobile (<768px)
   - Expand on desktop (≥768px)
   - Test touch gestures (swipe)

10. **test_sidebar_aria_labels**
    - Verify ARIA roles (navigation, listitem)
    - Check aria-label for each item
    - Test screen reader compatibility

**D3.js Visualizations (6 tests):**

11. **test_d3_architecture_diagram**
    - Verify component nodes render
    - Check layer positioning (UI → BLL → DAL)
    - Test zoom/pan interactions

12. **test_d3_dependency_graph**
    - Verify force-directed layout
    - Check node collision detection
    - Test drag interactions

13. **test_d3_file_hierarchy**
    - Verify tree structure renders
    - Test expand/collapse nodes
    - Check breadcrumb navigation

14. **test_d3_loc_sunburst**
    - Verify sunburst diagram renders
    - Check arc sizes match LOC counts
    - Test click-to-zoom

15. **test_d3_chord_diagram**
    - Verify chord diagram renders
    - Check ribbon thickness matches coupling
    - Test hover interactions

16. **test_d3_export_png_svg**
    - Test export to PNG functionality
    - Test export to SVG functionality
    - Verify downloaded files valid

**Chart.js Presets (3 tests):**

17. **test_chartjs_radar**
    - Verify radar chart renders
    - Check data points correct
    - Test responsiveness

18. **test_chartjs_bar**
    - Verify bar chart renders
    - Check axes labels
    - Test hover tooltips

19. **test_chartjs_pie**
    - Verify pie chart renders
    - Check legend displays
    - Test click interactions

---

### Phase 3 Tests (Core Tabs)

**Tests to Add:** 8 tests (1 per tab × 4 tabs)

20. **test_executive_summary_tab**
    - Verify hero section (health score ring)
    - Check 4 KPI cards render
    - Test business value section displays

21. **test_system_overview_tab**
    - Verify health dashboard (6 sub-scores)
    - Check repository statistics table
    - Test coverage treemap renders

22. **test_tech_stack_tab**
    - Verify dependency overview section
    - Check interactive package table sorting
    - Test vulnerability scanner displays CVEs

23. **test_security_tab**
    - Verify security overview (score gauge)
    - Check vulnerability list renders
    - Test secrets detection display

---

### Phase 4 Tests (Advanced Tabs)

**Tests to Add:** 8 tests (1 per tab × 4 tabs)

24. **test_use_cases_tab**
    - Verify primary use cases list (top 5)
    - Check problem domain synthesis
    - Test workflow diagram renders

25. **test_recommendations_tab**
    - Verify priority recommendations (top 10)
    - Check technical debt analysis section
    - Test priority matrix visualization

26. **test_architecture_tab**
    - Verify component diagram renders
    - Check dependency graph displays
    - Test design patterns list

27. **test_code_organization_tab**
    - Verify file tree renders
    - Check module breakdown table
    - Test code duplication heatmap

---

### Phase 5 Tests (Template Unification)

**Tests to Add:** 12 tests (6 templates × 2 tests each)

28. **test_console_app_8_tabs**
    - Verify all 8 tabs present
    - Check template-specific customizations (command structure)

29. **test_console_app_sidebar**
    - Verify sidebar navigation works
    - Check glassmorphism applied

30-43. **[Similar tests for api_service, fullstack_web, library_package, database_project, microservices]**

---

### Phase 6 Tests (Components & Optimization)

**Tests to Add:** 38 tests (32 components + 6 performance)

**Component Tests (32):**

44-75. **test_{component_name}**
    - Verify component renders
    - Test component variants (primary, secondary, success, error)
    - Check ARIA attributes present
    - Test keyboard interactions
    - Verify component in light/dark theme

**Performance Tests (6):**

76. **test_dashboard_generation_10k_loc**
    - Generate dashboard for 10K LOC repo
    - Assert generation time <2 minutes
    - Check memory usage <500MB

77. **test_dashboard_generation_100k_loc**
    - Generate dashboard for 100K LOC repo
    - Assert generation time <5 minutes
    - Check memory usage <500MB

78. **test_dashboard_load_time**
    - Measure first paint time
    - Assert <3 seconds
    - Measure time to interactive <5 seconds

79. **test_tab_switch_performance**
    - Switch between all 8 tabs
    - Assert switch time <500ms per tab

80. **test_visualization_render_time**
    - Measure D3.js initial render
    - Assert <1 second
    - Measure interaction response <200ms

81. **test_virtual_scrolling_large_table**
    - Render table with 10,000 rows
    - Assert smooth scrolling (60 FPS)
    - Check only visible rows in DOM

---

### Phase 7 Tests (E2E Validation & Cross-Browser)

**Tests to Add:** 25 tests (20 cross-browser + 5 accessibility)

**Cross-Browser Tests (20):**

82-101. **test_{feature}_on_{browser}**
    - Run 5 critical flows on 4 browsers (Chrome, Firefox, Safari, Edge)
    - Critical flows: dashboard generation, tab navigation, D3.js interaction, export, search/filter

**Accessibility Tests (5):**

102. **test_wcag_contrast_ratios**
    - Check all text meets WCAG AAA (7:1 contrast)
    - Verify glassmorphism backgrounds have sufficient contrast

103. **test_screen_reader_navigation**
    - Test NVDA/JAWS compatibility
    - Verify all interactive elements announced
    - Check landmark regions defined

104. **test_keyboard_only_navigation**
    - Navigate entire dashboard with keyboard only
    - Verify all interactive elements reachable
    - Check focus indicators visible

105. **test_skip_links**
    - Verify "Skip to content" link present
    - Test skip link focuses correct element

106. **test_aria_live_regions**
    - Verify dynamic content updates announced
    - Check loading states communicated

---

## 🧪 Test Execution Strategy

### Test Pyramid

```
           E2E (10%)
          /         \
    Integration (20%)
   /                 \
  Unit Tests (70%)
```

**Breakdown:**
- **Unit:** 70 tests × 70% = 49 unit tests (components, utilities)
- **Integration:** 20 tests × 20% = 14 integration tests (tab rendering, visualization integration)
- **E2E:** 10 tests × 10% = 7 E2E tests (full dashboard workflows)

**Total:** 70 Selenium tests (target: 60+ ✅)

### Test Execution Frequency

- **Per Commit:** Unit tests (fast, <2 min)
- **Per PR:** Integration tests (medium, <10 min)
- **Pre-Release:** E2E + cross-browser tests (slow, <60 min)

### CI/CD Integration

```yaml
# .github/workflows/cortex-lens-tests.yml
name: CORTEX Lens Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run unit tests
        run: pytest tests/cortex_lens/unit/ --cov=src/cortex_lens --cov-report=html

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run integration tests
        run: pytest tests/cortex_lens/integration/

  e2e-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chrome, firefox]
    steps:
      - uses: actions/checkout@v2
      - name: Run E2E tests
        run: pytest tests/cortex_lens/e2e/ --browser=${{ matrix.browser }}
```

---

## 📊 Coverage Targets by Module

| Module | Current Coverage | Target Coverage | Gap |
|--------|------------------|-----------------|-----|
| Templates | 30% | 85% | +55% |
| Components | 0% (new) | 90% | +90% |
| Visualizations | 0% (new) | 80% | +80% |
| Utilities | 50% | 85% | +35% |
| Generators | 60% | 85% | +25% |
| **Overall** | **40%** | **85%** | **+45%** |

---

## 🛠️ Testing Tools & Frameworks

**Core:**
- **Selenium WebDriver** - Browser automation
- **pytest** - Test framework
- **pytest-selenium** - Selenium integration
- **pytest-html** - HTML reports

**Coverage:**
- **pytest-cov** - Code coverage
- **coverage.py** - Coverage reports

**Accessibility:**
- **axe-core** - Accessibility testing
- **pa11y** - Accessibility auditing

**Performance:**
- **pytest-benchmark** - Performance benchmarking
- **locust** - Load testing (for dashboard generation)

**Cross-Browser:**
- **Selenium Grid** - Parallel browser testing
- **BrowserStack** - Cloud browser testing (optional)

---

## ✅ Success Criteria

Test strategy complete when:
- [ ] 70+ tests implemented (target: 60+ ✅)
- [ ] Test coverage ≥85%
- [ ] All tests passing (95%+ pass rate)
- [ ] Cross-browser tests passing (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility tests passing (WCAG 2.1 AAA)
- [ ] Performance benchmarks met
- [ ] CI/CD pipeline configured
- [ ] Test documentation complete

---

## 🚀 Implementation Timeline

| Phase | Tests Added | Cumulative | Duration |
|-------|-------------|------------|----------|
| Phase 0 | 0 (planning) | 12 (baseline) | - |
| Phase 1 | 5 | 17 | 1 day |
| Phase 2 | 14 | 31 | 2 days |
| Phase 3 | 8 | 39 | 2 days |
| Phase 4 | 8 | 47 | 2 days |
| Phase 5 | 12 | 59 | 2 days |
| Phase 6 | 38 | 97 | 3 days |
| Phase 7 | 25 | 122 | 3 days |

**Note:** Some tests overlap/consolidate, final count: ~70 tests (exceeds 60+ target ✅)

---

**Next Action:** Begin test implementation in Phase 1 (each phase adds tests incrementally)
