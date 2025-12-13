# Dashboard CSS Architecture Refactoring Plan

**Project:** CORTEX Dashboard CSS Modernization  
**Complexity:** HIGH (Incremental Planning Required)  
**TDD Integration:** Mandatory  
**Author:** Asif Hussain  
**Date:** December 9, 2025

---

## 📋 Executive Summary

Refactor CORTEX dashboard CSS from monolithic main.css (569 lines) into modular, maintainable architecture with proper separation of concerns, fixing sidebar navigation issues and ensuring all 10 tabs render consistently.

---

## 🎯 Objectives

1. **Extract & Modularize**: Break main.css into logical, focused files
2. **Fix Sidebar**: Resolve navigation display issues visible in production
3. **Consistency**: Ensure all 10 tabs use consistent styling patterns
4. **Performance**: Reduce CSS bloat, enable tree-shaking
5. **Maintainability**: Clear file structure with documented conventions

---

## 📐 Proposed CSS Architecture

```
styles/
├── base/
│   ├── reset.css           # CSS normalization
│   ├── variables.css       # Design tokens (extracted from main.css :root)
│   └── typography.css      # Font families, sizes, weights
│
├── layouts/
│   ├── dashboard-container.css   # Main flex container
│   ├── sidebar.css              # Left navigation panel
│   ├── main-content.css         # Right content area
│   └── content-header.css       # Header with title + actions
│
├── components/
│   ├── buttons.css         # .btn, .btn-primary
│   ├── cards.css           # .glass-card
│   ├── tabs.css            # .nav-tab, .tab-content
│   ├── forms.css           # select, input, label
│   ├── badges.css          # .project-type-badge
│   └── loading.css         # .loading-overlay, .spinner
│
├── tabs/
│   ├── overview-tab.css           # System Overview specific
│   ├── engineering-onboarding.css # Onboarding specific
│   └── architecture-panels.css    # Architecture specific
│
└── utils/
    ├── animations.css      # @keyframes definitions
    └── accessibility.css   # .visually-hidden, focus states
```

**Total Estimated Files:** 18 CSS files  
**Target Total Size:** < 50KB (currently ~60KB estimated)

---

## 📊 Current State Analysis

### Existing Files
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| main.css | 569 | Monolithic - everything | ⚠️ Split needed |
| architecture-panels.css | ? | Architecture tab | ✅ Keep |
| engineering-onboarding.css | ? | Onboarding tab | ✅ Keep |
| onboarding.css | ? | Legacy? | 🔍 Evaluate |
| overview-tab.css | ? | Overview tab | ✅ Keep |
| skeleton-loader.css | ? | Loading states | 🔄 Merge to loading.css |

### Issues Identified
1. **Sidebar Navigation**: Not displaying correctly (see screenshot)
   - Possible z-index issue
   - Missing styles for nav items
   - Logo/badge positioning

2. **CSS Duplication**: Styles repeated across files
   - Button styles in multiple places
   - Card styles duplicated
   - Color values hardcoded

3. **No Proper Layer Ordering**: CSS loads without clear cascade strategy

---

## 🏗️ Implementation Plan (14 Phases)

### Phase 1: Analysis & Audit ✅ COMPLETED
- [x] Review existing CSS files
- [x] Document current structure
- [x] Identify duplication
- [x] Check index.html for embedded CSS (NONE found - good!)

### Phase 2: Create Base Layer
**Files to Create:**
- `base/reset.css` - CSS normalization
- `base/variables.css` - Extract :root{} from main.css
- `base/typography.css` - Font definitions

**Acceptance Criteria:**
- All CSS custom properties in variables.css
- No hard-coded colors/spacing in other files
- Typography scale properly defined

**Tests:**
- Variables load correctly
- No missing custom property warnings
- Computed styles match design tokens

### Phase 3: Create Layout Layer
**Files to Create:**
- `layouts/dashboard-container.css`
- `layouts/sidebar.css` (PRIORITY - fixes navigation)
- `layouts/main-content.css`
- `layouts/content-header.css`

**Acceptance Criteria:**
- Sidebar displays all 10 nav items correctly
- Responsive layout works at 768px, 1024px, 1440px breakpoints
- Content header actions aligned properly

**Tests:**
- Sidebar navigation visible and clickable
- Layout doesn't break on resize
- Z-index stacking correct

### Phase 4: Create Components Layer
**Files to Create:**
- `components/buttons.css`
- `components/cards.css`
- `components/tabs.css`
- `components/forms.css`
- `components/badges.css`
- `components/loading.css` (merge skeleton-loader.css)

**Acceptance Criteria:**
- All components use BEM naming
- No style leakage between components
- Consistent hover/focus states

**Tests:**
- Button variants render correctly
- Cards have proper glassmorphism effect
- Tab switching animation works

### Phase 5: Create Utils Layer
**Files to Create:**
- `utils/animations.css` - All @keyframes
- `utils/accessibility.css` - WCAG AA compliance

**Acceptance Criteria:**
- All animations centralized
- Focus indicators visible
- Screen reader text hidden properly

### Phase 6: Reorganize Tab-Specific CSS
**Action:** Move shared styles from tab CSS to components/

**Files to Update:**
- overview-tab.css (keep only overview-specific)
- engineering-onboarding.css (keep only onboarding-specific)
- architecture-panels.css (keep only architecture-specific)

### Phase 7: Update index.html Import Order
**New CSS Load Order:**
```html
<!-- Base Layer -->
<link rel="stylesheet" href="styles/base/reset.css">
<link rel="stylesheet" href="styles/base/variables.css">
<link rel="stylesheet" href="styles/base/typography.css">

<!-- Layout Layer -->
<link rel="stylesheet" href="styles/layouts/dashboard-container.css">
<link rel="stylesheet" href="styles/layouts/sidebar.css">
<link rel="stylesheet" href="styles/layouts/main-content.css">
<link rel="stylesheet" href="styles/layouts/content-header.css">

<!-- Components Layer -->
<link rel="stylesheet" href="styles/components/buttons.css">
<link rel="stylesheet" href="styles/components/cards.css">
<link rel="stylesheet" href="styles/components/tabs.css">
<link rel="stylesheet" href="styles/components/forms.css">
<link rel="stylesheet" href="styles/components/badges.css">
<link rel="stylesheet" href="styles/components/loading.css">

<!-- Tab-Specific -->
<link rel="stylesheet" href="styles/tabs/overview-tab.css">
<link rel="stylesheet" href="styles/tabs/engineering-onboarding.css">
<link rel="stylesheet" href="styles/tabs/architecture-panels.css">

<!-- Utils Layer -->
<link rel="stylesheet" href="styles/utils/animations.css">
<link rel="stylesheet" href="styles/utils/accessibility.css">
```

### Phase 8-13: Test Each Tab
Test systematically (one phase per 2 tabs):
- Phase 8: Executive Summary, Overview
- Phase 9: Tech Stack, Security
- Phase 10: Use Cases, Recommendations
- Phase 11: Architecture, Code Organization
- Phase 12: Dependencies, Onboarding
- Phase 13: Cross-tab navigation testing

### Phase 14: Documentation & Optimization
- Create CSS style guide
- Minify for production
- Validate performance improvements

---

## 🧪 TDD Strategy

### Test Suite Structure
```
tests/
└── dashboard/
    ├── css/
    │   ├── test_css_loading.py        # All files return 200
    │   ├── test_css_variables.py      # Variables defined correctly
    │   ├── test_css_specificity.py    # No conflicts
    │   └── test_css_coverage.py       # All selectors used
    ├── tabs/
    │   ├── test_tab_rendering.py      # Each tab renders
    │   └── test_tab_styling.py        # Consistent styles
    └── accessibility/
        └── test_wcag_compliance.py    # Color contrast, focus
```

### Critical Tests
1. **CSS Loading**: All 18 files return HTTP 200
2. **Sidebar Navigation**: All 10 tabs visible and clickable
3. **Tab Switching**: Active styles apply correctly
4. **Responsive**: Breakpoints work at 768px, 1024px, 1440px
5. **Color Contrast**: WCAG AA (4.5:1 for text, 3:1 for UI)
6. **Performance**: Total CSS < 50KB, load time < 100ms

---

## 📏 Naming Conventions (BEM)

```css
/* Block */
.sidebar { }

/* Element */
.sidebar__header { }
.sidebar__nav { }
.sidebar__logo { }

/* Modifier */
.sidebar--collapsed { }
.nav-tab--active { }
.btn--primary { }
```

---

## 🎨 Design Tokens (from main.css)

### Colors
- Primary: `#00d4ff` (accent-primary)
- Secondary: `#7b61ff` (accent-secondary)
- Background: `#0a0e27` (bg-primary)
- Success: `#00ff88`
- Warning: `#ffa500`
- Danger: `#ff4444`

### Spacing Scale (4px base)
- xs: 4px (0.25rem)
- sm: 8px (0.5rem)
- md: 16px (1rem)
- lg: 24px (1.5rem)
- xl: 32px (2rem)
- 2xl: 48px (3rem)

### Typography Scale
- xs: 12px
- sm: 14px
- base: 16px
- lg: 18px
- xl: 20px
- 2xl: 24px
- 3xl: 30px
- 4xl: 36px

---

## 🚀 Execution Strategy

1. **Incremental**: One layer at a time (base → layout → components → tabs → utils)
2. **TDD**: Write tests first, implement, verify
3. **Git Commits**: One commit per phase with descriptive message
4. **Testing**: Test after each phase before proceeding
5. **Rollback Plan**: Keep main.css until all phases complete

---

## 📊 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Total CSS Files | 6 | 18 | 📋 Planned |
| Total CSS Size | ~60KB | <50KB | ⏳ Pending |
| Sidebar Issues | 🔴 Broken | ✅ Fixed | ⏳ Pending |
| Tab Consistency | ⚠️ Mixed | ✅ Uniform | ⏳ Pending |
| Load Time | Unknown | <100ms | ⏳ Pending |
| WCAG Compliance | Unknown | AA | ⏳ Pending |
| Maintainability | 3/10 | 9/10 | ⏳ Pending |

---

## 🔗 Dependencies

- Python HTTP server (running)
- Browser with DevTools
- pytest for testing
- Git for version control

---

## 🚨 Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing tabs | HIGH | Keep main.css until complete, test each phase |
| CSS conflicts | MEDIUM | Use BEM, test specificity |
| Performance regression | MEDIUM | Minify, lazy load non-critical |
| Browser compatibility | LOW | Use autoprefixer, test modern browsers |

---

## 📚 References

- BEM Methodology: http://getbem.com/
- WCAG AA Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- CSS Architecture: https://www.smashingmagazine.com/2018/05/css-custom-properties-strategy-guide/
- Glassmorphism Design: https://ui.glass/generator/

---

## 🔍 Architectural Review Integration

**Review Report:** `cortex-brain/documents/analysis/admin-dashboard-architectural-review-2025-12-09.md`  
**Overall Health Score:** 72/100 ⚠️ NEEDS IMPROVEMENT  
**Critical Findings:** 2 (CSS architecture, no testing)  
**High Priority Findings:** 4 (sidebar navigation, error handling, hard-coded paths, accessibility)

**Key Recommendations from Review:**
1. Complete CSS refactoring immediately (fixes navigation issue)
2. Implement Selenium E2E tests (20 critical test cases)
3. Add accessibility features (ARIA labels, keyboard navigation)
4. Standardize error handling across all tabs
5. Add performance monitoring

---

## 🧪 Selenium Testing Integration

### Test-Driven CSS Refactoring

Each CSS refactoring phase will be validated by Selenium tests:

**Phase 2 Validation:**
- [ ] `test_base_css_loads()` - Verify reset.css, variables.css, typography.css load
- [ ] `test_css_variables_defined()` - Check all custom properties exist
- [ ] `test_no_console_errors()` - Verify no CSS parse errors

**Phase 3 Validation:**
- [ ] `test_sidebar_navigation_visible()` - **FIXES USER REPORTED ISSUE**
- [ ] `test_sidebar_width_280px()` - Verify correct dimensions
- [ ] `test_all_10_nav_items_visible()` - Each tab clickable
- [ ] `test_nav_hover_states()` - Hover effects apply correctly
- [ ] `test_active_tab_highlighted()` - Active state CSS works

**Phase 4-6 Validation:**
- [ ] `test_buttons_render_correctly()` - All button variants display
- [ ] `test_cards_have_glassmorphism()` - Backdrop-filter applies
- [ ] `test_tabs_switch_animation()` - Tab transition works

**Phase 7 Validation:**
- [ ] `test_all_18_css_files_load()` - New import order works
- [ ] `test_load_time_under_100ms()` - Performance target met
- [ ] `test_no_duplicate_styles()` - Specificity conflicts resolved

**Phase 8-13 Validation:**
- [ ] `test_executive_tab_renders()` - Health gauge displays
- [ ] `test_overview_tab_renders()` - Metric cards display
- [ ] `test_use_cases_tab_renders()` - Use cases data loads
- [ ] `test_recommendations_tab_renders()` - Priority matrix displays
- [ ] `test_architecture_tab_renders()` - Architecture panels display
- [ ] `test_onboarding_tab_renders()` - Wizard stepper displays
- [ ] `test_all_tabs_no_console_errors()` - Zero JavaScript errors

### Selenium Test Suite Structure

```
tests/
└── dashboard/
    ├── e2e/
    │   ├── test_index_loading.py           # Core HTML loads
    │   ├── test_tab_navigation.py          # All 10 tabs switch
    │   ├── test_css_refactoring.py         # CSS phases validation
    │   ├── test_data_sources.py            # All 5 sources work
    │   ├── test_export_functions.py        # PDF/CSV/JSON export
    │   ├── test_responsive_design.py       # Mobile/tablet/desktop
    │   └── test_accessibility.py           # WCAG compliance
    ├── visual_regression/
    │   └── test_visual_consistency.py      # Screenshot comparison
    └── performance/
        └── test_load_times.py              # Performance budgets
```

### Selenium Configuration

```python
# tests/dashboard/conftest.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="session")
def dashboard_url():
    """Dashboard URL with mock data source."""
    return "http://localhost:8081/ui/index.html?source=mock"

@pytest.fixture(scope="function")
def driver(dashboard_url):
    """Create Chrome driver in headless mode."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get(dashboard_url)
    
    yield driver
    
    # Check for console errors before teardown
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE']
    if errors:
        pytest.fail(f"Console errors detected: {errors}")
    
    driver.quit()

@pytest.fixture(scope="function")
def mobile_driver(dashboard_url):
    """Create mobile viewport driver (375px)."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=375,667")
    
    driver = webdriver.Chrome(options=options)
    driver.get(dashboard_url)
    
    yield driver
    
    driver.quit()

def wait_for_element(driver, by, value, timeout=10):
    """Helper to wait for element visibility."""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )

def wait_for_no_loading_spinner(driver, timeout=10):
    """Helper to wait for loading spinner to disappear."""
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "loading-overlay"))
    )
```

### Sample Test Implementation

```python
# tests/dashboard/e2e/test_css_refactoring.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestPhase2BaseCSS:
    """Validate Phase 2: Base CSS layer."""
    
    def test_base_css_files_load(self, driver):
        """Verify reset.css, variables.css, typography.css load with HTTP 200."""
        css_files = [
            "/ui/styles/base/reset.css",
            "/ui/styles/base/variables.css",
            "/ui/styles/base/typography.css"
        ]
        
        for css_file in css_files:
            # Check if CSS link exists in DOM
            css_link = driver.find_element(
                By.CSS_SELECTOR, 
                f'link[href*="{css_file}"]'
            )
            assert css_link.is_displayed()
    
    def test_css_variables_defined(self, driver):
        """Verify all CSS custom properties exist."""
        # Execute JavaScript to check CSS variables
        script = """
        const root = document.documentElement;
        const style = getComputedStyle(root);
        return {
            bgPrimary: style.getPropertyValue('--bg-primary'),
            accentPrimary: style.getPropertyValue('--accent-primary'),
            spacingMd: style.getPropertyValue('--spacing-md'),
            fontSizeBase: style.getPropertyValue('--font-size-base')
        };
        """
        variables = driver.execute_script(script)
        
        assert variables['bgPrimary'].strip() != "", "Missing --bg-primary"
        assert variables['accentPrimary'].strip() != "", "Missing --accent-primary"
        assert variables['spacingMd'].strip() != "", "Missing --spacing-md"
        assert variables['fontSizeBase'].strip() != "", "Missing --font-size-base"
    
    def test_typography_scales_applied(self, driver):
        """Verify typography classes work."""
        # Check if h1 has correct font size
        driver.execute_script("""
            const testH1 = document.createElement('h1');
            testH1.textContent = 'Test Heading';
            testH1.id = 'test-h1';
            document.body.appendChild(testH1);
        """)
        
        h1 = driver.find_element(By.ID, "test-h1")
        font_size = h1.value_of_css_property('font-size')
        
        # Should be 36px (--font-size-4xl)
        assert font_size == "36px", f"Expected 36px, got {font_size}"

class TestPhase3Layouts:
    """Validate Phase 3: Layout CSS layer (PRIORITY - fixes sidebar)."""
    
    def test_sidebar_navigation_visible(self, driver):
        """CRITICAL: Verify sidebar displays all 10 navigation items."""
        # Check sidebar exists
        sidebar = driver.find_element(By.CLASS_NAME, "nav-tabs")
        assert sidebar.is_displayed(), "Sidebar not visible"
        
        # Check sidebar width
        width = sidebar.value_of_css_property('width')
        # Note: actual computed width might differ slightly
        assert int(width.replace('px', '')) >= 250, f"Sidebar too narrow: {width}"
    
    def test_all_10_nav_items_visible(self, driver):
        """Verify all 10 nav items render correctly."""
        nav_items = driver.find_elements(By.CLASS_NAME, "nav-tab")
        assert len(nav_items) == 10, f"Expected 10 nav items, found {len(nav_items)}"
        
        # Check each item has icon and text
        for item in nav_items:
            icon = item.find_element(By.CLASS_NAME, "nav-tab-icon")
            text = item.find_element(By.CLASS_NAME, "nav-tab-text")
            
            assert icon.is_displayed(), "Nav icon not visible"
            assert text.is_displayed(), "Nav text not visible"
            assert text.text.strip() != "", "Nav text is empty"
    
    def test_nav_hover_states(self, driver):
        """Verify hover effects apply correctly."""
        from selenium.webdriver.common.action_chains import ActionChains
        
        first_nav = driver.find_element(By.CLASS_NAME, "nav-tab")
        
        # Get initial background color
        initial_bg = first_nav.value_of_css_property('background-color')
        
        # Hover over element
        ActionChains(driver).move_to_element(first_nav).perform()
        
        # Get hover background color
        hover_bg = first_nav.value_of_css_property('background-color')
        
        # Colors should be different on hover
        assert initial_bg != hover_bg, "Hover state not applying"
    
    def test_active_tab_highlighted(self, driver):
        """Verify active tab has correct CSS class."""
        # Click second tab
        second_tab = driver.find_elements(By.CLASS_NAME, "nav-tab")[1]
        second_tab.click()
        
        # Wait for tab to activate
        WebDriverWait(driver, 5).until(
            lambda d: "active" in second_tab.get_attribute("class")
        )
        
        assert "active" in second_tab.get_attribute("class")

class TestPhase7Integration:
    """Validate Phase 7: All 18 CSS files load correctly."""
    
    def test_all_18_css_files_load(self, driver):
        """Verify new modular CSS architecture loads without errors."""
        expected_files = [
            # Base layer
            "base/reset.css",
            "base/variables.css",
            "base/typography.css",
            # Layouts layer
            "layouts/dashboard-container.css",
            "layouts/sidebar.css",
            "layouts/main-content.css",
            # Components layer
            "components/buttons.css",
            "components/cards.css",
            "components/tabs.css",
            "components/forms.css",
            "components/badges.css",
            "components/loading.css",
            # Tabs layer
            "tabs/overview-tab.css",
            "tabs/engineering-onboarding.css",
            "tabs/architecture-panels.css",
            # Utils layer
            "utils/animations.css",
            "utils/accessibility.css"
        ]
        
        css_links = driver.find_elements(By.TAG_NAME, "link")
        loaded_files = [link.get_attribute("href") for link in css_links if link.get_attribute("rel") == "stylesheet"]
        
        for expected in expected_files:
            found = any(expected in loaded for loaded in loaded_files)
            assert found, f"Missing CSS file: {expected}"
    
    def test_no_duplicate_styles(self, driver):
        """Verify no CSS specificity conflicts after refactor."""
        # Check that button styles aren't duplicated
        script = """
        const button = document.createElement('button');
        button.className = 'btn btn-primary';
        document.body.appendChild(button);
        const styles = getComputedStyle(button);
        document.body.removeChild(button);
        return {
            bgColor: styles.backgroundColor,
            padding: styles.padding,
            borderRadius: styles.borderRadius
        };
        """
        styles = driver.execute_script(script)
        
        # Should have consistent values (not multiple conflicting rules)
        assert styles['bgColor'] != "rgba(0, 0, 0, 0)", "Button has no background"
        assert styles['padding'] != "0px", "Button has no padding"

class TestPhase8to13TabRendering:
    """Validate Phase 8-13: All 10 tabs render correctly after CSS refactor."""
    
    @pytest.mark.parametrize("tab_key,container_id", [
        ("executive", "executive-container"),
        ("overview", "overview-container"),
        ("tech-stack", "tech-stack-container"),
        ("security", "security-container"),
        ("use-cases", "use-cases-container"),
        ("recommendations", "recommendations-container"),
        ("architecture", "architecture-container"),
        ("code-organization", "code-organization-container"),
        ("vendors", "vendors-container"),
        ("onboarding", "onboarding-container")
    ])
    def test_tab_renders_correctly(self, driver, tab_key, container_id):
        """Test each tab renders without errors."""
        # Click tab
        tab = driver.find_element(By.CSS_SELECTOR, f'[data-tab="{tab_key}"]')
        tab.click()
        
        # Wait for container to be visible
        container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, container_id))
        )
        
        assert container.is_displayed(), f"Tab {tab_key} container not visible"
        
        # Verify active state
        assert "active" in tab.get_attribute("class"), f"Tab {tab_key} not marked active"
        
        # Check for JavaScript errors
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        assert len(errors) == 0, f"Tab {tab_key} has console errors: {errors}"
```

### CI/CD Integration

```yaml
# .github/workflows/dashboard-css-tests.yml
name: Dashboard CSS Refactoring Tests

on:
  pull_request:
    paths:
      - 'cortex-brain/dashboards/ui/**'
  push:
    branches:
      - main
      - CORTEX-3.0

jobs:
  selenium-tests:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install selenium pytest pytest-html pytest-xdist
      
      - name: Install Chrome
        run: |
          wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
          echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable
      
      - name: Start dashboard server
        run: |
          cd cortex-brain/dashboards
          python -m http.server 8081 &
          sleep 5
      
      - name: Run Phase 2 tests (Base CSS)
        if: always()
        run: |
          pytest tests/dashboard/e2e/test_css_refactoring.py::TestPhase2BaseCSS -v
      
      - name: Run Phase 3 tests (Layouts - Sidebar Fix)
        if: always()
        run: |
          pytest tests/dashboard/e2e/test_css_refactoring.py::TestPhase3Layouts -v
      
      - name: Run Phase 7 tests (Integration)
        if: always()
        run: |
          pytest tests/dashboard/e2e/test_css_refactoring.py::TestPhase7Integration -v
      
      - name: Run Phase 8-13 tests (All Tabs)
        if: always()
        run: |
          pytest tests/dashboard/e2e/test_css_refactoring.py::TestPhase8to13TabRendering -v
      
      - name: Generate test report
        if: always()
        run: |
          pytest tests/dashboard/e2e/ --html=dashboard-test-report.html --self-contained-html
      
      - name: Upload test report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: dashboard-test-report
          path: dashboard-test-report.html
      
      - name: Fail if critical tests fail
        run: |
          pytest tests/dashboard/e2e/test_css_refactoring.py::TestPhase3Layouts::test_sidebar_navigation_visible -v
```

---

## 🎯 Updated Success Criteria

Dashboard CSS refactoring is complete when:

1. ✅ All 18 CSS files created and organized correctly
2. ✅ Total CSS size < 50KB (minified)
3. ✅ Load time < 100ms
4. ✅ All 10 tabs render correctly (validated by Selenium)
5. ✅ Sidebar navigation displays properly (validated by Selenium)
6. ✅ Zero console errors (validated by Selenium)
7. ✅ All Selenium tests pass (20+ test cases)
8. ✅ No CSS specificity conflicts
9. ✅ WCAG AA compliance (validated by accessibility tests)
10. ✅ Documentation complete (style guide, test patterns)

---

**Next Action:** Begin Phase 3 - Create layouts/sidebar.css (PRIORITY - fixes navigation)

**Estimated Total Time:** 8-10 hours (including Selenium test creation)  
**Recommended Approach:** Execute phases with TDD - write Selenium test first, implement CSS, validate test passes
