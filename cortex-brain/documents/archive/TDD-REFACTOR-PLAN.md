# Dashboard TDD Refactoring Plan

**Plan ID:** DASH-TDD-REFACTOR-2025-001  
**Created:** December 7, 2025  
**Status:** 🟢 Ready for Autonomous Execution  
**Author:** Asif Hussain  
**Execution Mode:** Autonomous with Strategic Checkpoints

---

## 📋 Executive Summary

**Objective:** Comprehensive test-driven refactoring of the CORTEX dashboard system with data architecture restructuring

**Approach:** RED → GREEN → REFACTOR at system scale
1. **GREEN:** Establish comprehensive test baseline (current working state)
2. **RED:** Deliberately break tests via data + code refactoring
3. **GREEN:** Systematically fix all tests
4. **REFACTOR:** Optimize entire application

**Timeline:** 5-7 days (6 phases)  
**Test Target:** 300+ tests (integration + unit + component)  
**Current State:** Dashboard functional, 170 existing tests, mixed patterns

---

## 🎯 Success Criteria

**Must Have (Blockers):**
- ✅ 300+ tests with 100% pass rate
- ✅ All 8 tabs fully functional
- ✅ Data structure consistency (each repo in own subfolder)
- ✅ Component standardization (BaseTabComponent pattern)
- ✅ Zero console errors or warnings
- ✅ Performance maintained or improved

**Should Have (Targets):**
- ✅ Test coverage ≥ 90%
- ✅ Bundle size < 500KB
- ✅ Tab switch time < 100ms
- ✅ Lighthouse score ≥ 95

**Nice to Have (Optimizations):**
- ✅ Dynamic imports for lazy loading
- ✅ Accessibility score ≥ 95
- ✅ Comprehensive ADRs

---

## 📐 Architecture Changes

### Current Data Structure (Problems)
```
cortex-brain/dashboards/data/
├── mock/               # Mock data files (11 JSON)
├── luum-fresh/         # Inconsistent - some repos have subfolders
├── tcbulk/
├── v5-coldfusion/
├── v5-prevalidation-ws/
└── repos/              # Some repos nested here?
    └── ...
```

**Problems:**
- Inconsistent folder structure (mock mixed with real repos)
- No clear pattern for repo data organization
- Path resolution logic complex in data-loader.js

### Target Data Structure (Solution)
```
cortex-brain/dashboards/data/
├── repositories/       # NEW: All repos including mock
│   ├── mock/          # Mock data now in subfolder
│   │   ├── overview.json
│   │   ├── health-data.json
│   │   ├── tech-stack.json
│   │   ├── security.json
│   │   ├── architecture.json
│   │   ├── code-organization.json
│   │   ├── vendors.json
│   │   └── executive-summary.json
│   ├── cortex/        # CORTEX repository data
│   ├── luum-fresh/
│   ├── tcbulk/
│   └── ...
├── schemas/           # JSON schemas for validation
└── registry.json      # Repository registry
```

**Benefits:**
- Consistent structure for all repositories
- Simplified path resolution
- Easy to add new repositories
- Clear separation of concerns

### Current Code Structure (Problems)
```
ui/
├── app.js              # 445 lines - too large
├── progressive-loader.js  # Mixed usage patterns
├── components/
│   ├── overview-tab.js      # Deprecated
│   ├── overview-tab-v3.js   # Current - inconsistent naming
│   ├── tech-stack-tab.js    # Direct DOM manipulation
│   ├── security-tab.js      # Returns HTML strings
│   └── ...                  # 8 tabs with different patterns
```

**Problems:**
- No base component class
- Inconsistent initialization (some use `init()`, others `render()`)
- Mixed rendering patterns (DOM manipulation vs HTML strings)
- Progressive loader usage inconsistent

### Target Code Structure (Solution)
```
ui/
├── app.js              # Simplified orchestrator (~200 lines)
├── core/
│   ├── BaseTabComponent.js   # Abstract base class
│   ├── DataLoader.js         # Refactored data loading
│   ├── ProgressiveLoader.js  # Metadata-driven
│   └── StateManager.js       # Centralized state
├── components/
│   ├── tabs/
│   │   ├── OverviewTab.js     # Standard naming
│   │   ├── TechStackTab.js
│   │   ├── SecurityTab.js
│   │   ├── ArchitectureTab.js
│   │   ├── CodeOrgTab.js
│   │   ├── VendorsTab.js
│   │   ├── ExecutiveTab.js
│   │   └── EngineeringTab.js
│   └── shared/               # Shared UI components
│       ├── HealthScore.js
│       ├── MetricCard.js
│       └── ChartRenderer.js
└── tests/
    ├── integration/          # Integration tests
    ├── unit/                 # Unit tests per component
    └── fixtures/             # Test data fixtures
```

---

## 🚀 Phase Breakdown

### Phase 0: Establish GREEN Test Baseline (Day 1)
**Objective:** Capture current working state with comprehensive tests

**Why This Matters:** Tests protect against regression during refactoring

#### Tasks:
1. [ ] **Integration Tests** - End-to-end tab functionality
   - Load dashboard with each data source
   - Switch between all 8 tabs
   - Verify tab content renders
   - Test data refresh functionality
   - Test export functionality
   - Test source selector
   - Test keyboard navigation
   - Test responsive behavior

2. [ ] **Tab Rendering Tests** (8 tabs × 10 tests = 80 tests)
   - Executive tab: Health score, summary, metrics
   - Overview tab: Charts, metrics, navigation
   - Tech-stack tab: Language breakdown, framework detection
   - Security tab: Vulnerability list, OWASP compliance
   - Architecture tab: Component detection, pattern recognition
   - Code-org tab: Complexity metrics, hotspot detection
   - Vendors tab: Third-party services, risk assessment
   - Engineering tab: Onboarding content

3. [ ] **Component Unit Tests** - Individual component behavior
   - HealthScore component: Score calculation, color coding
   - MetricCard component: Value formatting, icon display
   - ChartRenderer: D3.js charts, Chart.js charts
   - VulnerabilityCard: Severity display, CVE links
   - ArchitectureDiagram: Mermaid.js integration

4. [ ] **Data Structure Tests** - Validate data contracts
   - Schema validation for all 7 JSON files
   - Required field presence
   - Data type validation
   - Nested structure validation
   - Boundary conditions (empty arrays, null values)

#### Deliverables:
- `tests/integration/dashboard-integration.test.js` (30+ tests)
- `tests/integration/tab-rendering.test.js` (80+ tests)
- `tests/unit/components/*.test.js` (50+ tests per component type)
- `tests/unit/data-validation.test.js` (40+ tests)
- **Total: 200+ tests, all passing (GREEN)**

#### Definition of Done:
- ✅ 200+ tests written and passing
- ✅ Test coverage ≥ 80% of current codebase
- ✅ Dashboard works perfectly in browser
- ✅ All data sources load correctly
- ✅ No console errors
- ✅ Test report generated

---

### Phase 1: Component-Level Unit Tests (Day 1-2)
**Objective:** Add granular tests for internal component logic

**Why This Matters:** Component tests catch logic errors before integration

#### Tasks:
1. [ ] **Data Processing Tests**
   - Tech-stack aggregation logic
   - Security vulnerability scoring
   - Architecture pattern detection
   - Code complexity calculations
   - Health score computation

2. [ ] **Event Handler Tests**
   - Click handlers for tab switches
   - Source change handlers
   - Refresh button functionality
   - Export button functionality
   - Keyboard shortcuts

3. [ ] **Error State Tests**
   - Missing data handling
   - Malformed JSON handling
   - Network error handling
   - Timeout scenarios
   - Graceful degradation

4. [ ] **Edge Case Tests**
   - Empty data arrays
   - Null/undefined values
   - Very large datasets
   - Special characters in data
   - Concurrent operations

#### Deliverables:
- `tests/unit/data-processing.test.js` (30 tests)
- `tests/unit/event-handlers.test.js` (25 tests)
- `tests/unit/error-handling.test.js` (20 tests)
- `tests/unit/edge-cases.test.js` (25 tests)
- **Total: 300+ tests cumulative, all passing (GREEN)**

#### Definition of Done:
- ✅ 100+ additional tests added
- ✅ 300+ total tests all passing
- ✅ Test coverage ≥ 85%
- ✅ All edge cases covered
- ✅ Error scenarios documented

---

### Phase 2: Data Architecture Refactor (Day 2-3) [RED PHASE]
**Objective:** Restructure repository data folders - tests WILL fail

**Why This Matters:** Consistent data structure = maintainable system

#### Tasks:
1. [ ] **Create New Data Structure**
   ```bash
   mkdir -p data/repositories
   mv data/mock data/repositories/mock
   mv data/luum-fresh data/repositories/luum-fresh
   # ... move all repos
   ```

2. [ ] **Update Path Constants**
   - Update `DATA_SOURCES` in data-loader.js
   - Change base paths from `../data/` to `../data/repositories/`
   - Update registry.json paths

3. [ ] **Refactor Data Loader**
   - Simplify path resolution logic
   - Add repository discovery
   - Improve error messages
   - Add schema validation

4. [ ] **Update Tests (mark as expected failures)**
   - Add comments: `// EXPECTED TO FAIL - Phase 2 refactoring`
   - Document which tests break and why
   - Track test failure count

#### Expected State:
- 🔴 **100-150 tests failing** (data path changes)
- 🔴 **Console errors:** "Failed to load JSON"
- 🔴 **Dashboard broken:** Tabs won't load
- ✅ **This is INTENTIONAL - controlled RED phase**

#### Deliverables:
- New data folder structure
- Updated data-loader.js
- Test failure report
- Migration guide document

#### Definition of Done:
- ✅ All repositories in `data/repositories/` subfolders
- ✅ data-loader.js refactored
- ✅ Test failures documented (expected ~100-150)
- ✅ No NEW errors beyond expected path issues

---

### Phase 3: Code Architecture Refactor (Day 3-4) [RED PHASE CONTINUES]
**Objective:** Implement BaseTabComponent pattern - more tests WILL fail

**Why This Matters:** Standardized components = predictable behavior

#### Tasks:
1. [ ] **Create BaseTabComponent**
   ```javascript
   class BaseTabComponent {
       constructor(containerId) {
           this.containerId = containerId;
           this.container = null;
           this.data = null;
           this.loading = false;
       }
       
       async init(data) {
           this.data = data;
           this.container = document.getElementById(this.containerId);
           if (!this.container) throw new Error(`Container not found: ${this.containerId}`);
           await this.render();
       }
       
       async render() {
           throw new Error('render() must be implemented by subclass');
       }
       
       destroy() {
           if (this.container) this.container.innerHTML = '';
       }
       
       showLoading() { /* ... */ }
       hideLoading() { /* ... */ }
       showError(message) { /* ... */ }
   }
   ```

2. [ ] **Migrate All Tabs to BaseTabComponent**
   - OverviewTab extends BaseTabComponent
   - TechStackTab extends BaseTabComponent
   - SecurityTab extends BaseTabComponent
   - ArchitectureTab extends BaseTabComponent
   - CodeOrgTab extends BaseTabComponent
   - VendorsTab extends BaseTabComponent
   - ExecutiveTab extends BaseTabComponent
   - EngineeringTab extends BaseTabComponent

3. [ ] **Refactor Progressive Loader**
   - Metadata-driven skeleton display
   - Components declare loading requirements
   - Automatic show/hide based on render state

4. [ ] **Simplify app.js renderCurrentTab()**
   ```javascript
   async function renderCurrentTab() {
       const tabId = getTabContainerId(appState.currentTab);
       showTab(tabId);
       
       const TabClass = getTabClass(appState.currentTab);
       const tab = new TabClass(tabId);
       await tab.init(appState.data);
   }
   ```

#### Expected State:
- 🔴 **200-250 tests failing** (API changes + data paths)
- 🔴 **Dashboard still broken**
- ✅ **This is STILL INTENTIONAL - controlled RED phase**

#### Deliverables:
- BaseTabComponent.js
- 8 refactored tab components
- Updated progressive-loader.js
- Simplified app.js
- Architecture documentation

#### Definition of Done:
- ✅ BaseTabComponent implemented
- ✅ All 8 tabs refactored to new pattern
- ✅ Progressive loader refactored
- ✅ app.js simplified
- ✅ Test failures documented (expected ~200-250)
- ✅ Code review completed

---

### Phase 4: Fix Tests (Day 4-5) [GREEN PHASE]
**Objective:** Make ALL 300+ tests pass - dashboard MUST work

**Why This Matters:** Tests validate refactoring correctness

#### Tasks:
1. [ ] **Fix Data Path Tests** (Priority 1)
   - Update all test fixtures to use new paths
   - Fix data-loader test expectations
   - Verify registry.json loading

2. [ ] **Fix Component API Tests** (Priority 2)
   - Update test assertions for BaseTabComponent API
   - Fix initialization tests
   - Update render method tests

3. [ ] **Fix Integration Tests** (Priority 3)
   - End-to-end tab loading
   - Data source switching
   - Tab switching flows

4. [ ] **Systematic Test Fixing Strategy**
   ```
   For each failing test:
   1. Identify root cause (data path? API change? logic bug?)
   2. Determine if test needs update or code needs fix
   3. Fix code or test (prefer fixing code unless API intentionally changed)
   4. Verify test passes
   5. Check for regressions
   ```

5. [ ] **Verify Dashboard Functionality**
   - Load all data sources (mock, cortex, etc.)
   - Test all tabs render correctly
   - Test all interactions work
   - No console errors

#### Deliverables:
- ✅ **ALL 300+ tests passing (100% GREEN)**
- ✅ **Dashboard fully functional**
- Test fix report
- Regression test suite

#### Definition of Done:
- ✅ 300+ tests all passing (0 failures)
- ✅ Test coverage ≥ 90%
- ✅ Dashboard works in browser (all tabs)
- ✅ All data sources load correctly
- ✅ Zero console errors
- ✅ Zero ESLint warnings
- ✅ Smoke tests passed on 3+ data sources

---

### Phase 5: Optimization & Polish (Day 5-7) [REFACTOR PHASE]
**Objective:** Optimize performance, accessibility, documentation

**Why This Matters:** Production-ready quality

#### Tasks:
1. [ ] **Performance Optimization**
   - Implement dynamic imports for tab components
   - Add code splitting
   - Lazy load Chart.js, D3.js only when needed
   - Optimize render cache strategy
   - Add IntersectionObserver for deferred rendering

2. [ ] **Accessibility Audit**
   - WCAG 2.1 AA compliance
   - Keyboard navigation (already exists, verify)
   - Screen reader compatibility
   - ARIA labels and roles
   - Focus management

3. [ ] **Security Audit**
   - XSS vulnerability scan
   - CSP policy implementation
   - Input sanitization
   - Dependency audit

4. [ ] **Documentation**
   - Architecture Decision Records (ADRs)
   - Component API documentation
   - Data schema documentation
   - Developer onboarding guide
   - User guide

5. [ ] **Final Quality Gates**
   - Lighthouse audit (target ≥ 95)
   - Bundle size analysis
   - Performance profiling
   - Cross-browser testing (Chrome, Firefox, Safari, Edge)

#### Deliverables:
- Dynamic import implementation
- Accessibility report (WCAG 2.1 AA)
- Security audit report
- Complete documentation suite
- Performance benchmark report
- Lighthouse score report

#### Definition of Done:
- ✅ All 300+ tests still passing
- ✅ Performance metrics improved:
  - Initial load < 2s
  - Tab switch < 100ms
  - Bundle size < 500KB
- ✅ Lighthouse score ≥ 95
- ✅ Accessibility score ≥ 95
- ✅ Security vulnerabilities: 0 high, 0 medium
- ✅ Documentation complete (100% coverage)
- ✅ Cross-browser testing passed
- ✅ Code review approved

---

## 🧪 Testing Strategy

### Test Framework: Jest + Puppeteer
```javascript
// Integration test example
describe('Dashboard Integration', () => {
    beforeAll(async () => {
        await page.goto('http://localhost:8080/ui/index.html?source=mock');
    });
    
    test('loads dashboard with mock data', async () => {
        await page.waitForSelector('.dashboard-container');
        const title = await page.title();
        expect(title).toBe('CORTEX Health Dashboard');
    });
    
    test('renders all 8 tabs', async () => {
        const tabs = await page.$$eval('.nav-item', items => items.length);
        expect(tabs).toBe(8);
    });
    
    test('switches to tech-stack tab', async () => {
        await page.click('[data-tab="tech-stack"]');
        await page.waitForSelector('#tech-stack-tab.active');
        const content = await page.$eval('#tech-stack-tab', el => el.textContent);
        expect(content).toContain('Languages');
    });
});
```

### Component Test Example
```javascript
// Component unit test
import { TechStackTab } from '../components/tabs/TechStackTab.js';

describe('TechStackTab', () => {
    let tab;
    let container;
    
    beforeEach(() => {
        container = document.createElement('div');
        container.id = 'tech-stack-tab';
        document.body.appendChild(container);
        tab = new TechStackTab('tech-stack-tab');
    });
    
    afterEach(() => {
        tab.destroy();
        container.remove();
    });
    
    test('renders language breakdown', async () => {
        const mockData = {
            techStack: {
                languages: { 'JavaScript': 45.2, 'Python': 30.5, 'HTML': 24.3 }
            }
        };
        
        await tab.init(mockData);
        
        const languageItems = container.querySelectorAll('.language-item');
        expect(languageItems.length).toBe(3);
        expect(languageItems[0].textContent).toContain('JavaScript');
        expect(languageItems[0].textContent).toContain('45.2%');
    });
});
```

### Test Organization
```
tests/
├── integration/
│   ├── dashboard-loading.test.js
│   ├── tab-navigation.test.js
│   ├── data-sources.test.js
│   └── user-interactions.test.js
├── unit/
│   ├── components/
│   │   ├── OverviewTab.test.js
│   │   ├── TechStackTab.test.js
│   │   └── ...
│   ├── data-loader.test.js
│   ├── progressive-loader.test.js
│   └── state-manager.test.js
├── fixtures/
│   ├── mock-data.json
│   ├── empty-data.json
│   └── malformed-data.json
└── helpers/
    ├── test-utils.js
    └── dom-setup.js
```

---

## 📊 Progress Tracking

### Phase Completion Checklist

#### Phase 0: GREEN Baseline ☐
- [ ] 200+ integration tests written
- [ ] All tests passing
- [ ] Dashboard functional
- [ ] Test report generated

#### Phase 1: Component Tests ☐
- [ ] 100+ unit tests added
- [ ] 300+ total tests passing
- [ ] Coverage ≥ 85%
- [ ] Edge cases covered

#### Phase 2: Data Refactor (RED) ☐
- [ ] New folder structure created
- [ ] data-loader.js refactored
- [ ] 100-150 tests failing (expected)
- [ ] Failure report documented

#### Phase 3: Code Refactor (RED) ☐
- [ ] BaseTabComponent created
- [ ] 8 tabs migrated
- [ ] 200-250 tests failing (expected)
- [ ] Architecture documented

#### Phase 4: Fix Tests (GREEN) ☐
- [ ] ALL 300+ tests passing
- [ ] Dashboard functional
- [ ] Zero console errors
- [ ] Smoke tests passed

#### Phase 5: Optimization ☐
- [ ] Performance optimized
- [ ] Accessibility ≥ 95
- [ ] Security audit passed
- [ ] Documentation complete

---

## 🚨 Risk Management

### Risk 1: Breaking Critical Functionality
**Likelihood:** HIGH | **Impact:** HIGH
- **Mitigation:** Comprehensive test suite before refactoring
- **Mitigation:** Phase 0-1 must be 100% complete before Phase 2
- **Mitigation:** Smoke tests after every phase
- **Rollback:** Git branches per phase for easy rollback

### Risk 2: Test Coverage Gaps
**Likelihood:** MEDIUM | **Impact:** HIGH
- **Mitigation:** Systematic test writing (every component, every function)
- **Mitigation:** Coverage report must show ≥ 90%
- **Mitigation:** Manual testing of critical paths

### Risk 3: Time Overrun
**Likelihood:** MEDIUM | **Impact:** MEDIUM
- **Mitigation:** Clear phase boundaries, no scope creep
- **Mitigation:** Phase 5 tasks can be deferred if needed
- **Mitigation:** Daily progress reports

### Risk 4: Data Migration Issues
**Likelihood:** LOW | **Impact:** MEDIUM
- **Mitigation:** Backup data folder before Phase 2
- **Mitigation:** Validate data integrity after migration
- **Mitigation:** Document any data transformations

---

## 🎯 Autonomous Execution Plan

**Mode:** Autonomous with Strategic Checkpoints

### Execution Flow:
1. **Phase 0-1:** Execute autonomously (Day 1-2)
   - Checkpoint: Report test count and pass rate
   
2. **Phase 2:** Execute autonomously (Day 2-3)
   - Checkpoint: Report expected test failures
   
3. **Phase 3:** Execute autonomously (Day 3-4)
   - Checkpoint: Report refactoring progress
   
4. **Phase 4:** Execute autonomously (Day 4-5)
   - Checkpoint: Report test fixing progress daily
   - **CRITICAL:** Must achieve 100% pass rate before Phase 5
   
5. **Phase 5:** Execute autonomously (Day 5-7)
   - Checkpoint: Report optimization metrics

### Daily Reports Include:
- Tests written / fixed
- Current pass rate
- Blockers encountered
- Time estimate to completion
- Next day's focus areas

### User Intervention Points:
- **Phase Gate:** Approval to proceed to Phase 2 (RED phase)
- **Phase Gate:** Approval to proceed to Phase 5 (optimization)
- **Blockers:** If stuck for >2 hours
- **Critical Decisions:** Architecture trade-offs

### Success Signal:
✅ **ALL 300+ tests passing**  
✅ **Dashboard fully functional**  
✅ **Performance metrics improved**  
✅ **Documentation complete**

---

## 📝 Next Steps

**To begin autonomous execution:**

Say: `execute all phases autonomously`

**To execute phase-by-phase:**

Say: `start phase 0`

**To modify the plan:**

Say: `modify plan [your changes]`

---

## 📚 Related Documents

- `.github/prompts/modules/tdd-mastery-guide.md` - TDD workflow
- `.github/prompts/modules/planning-orchestrator-guide.md` - Planning system
- `cortex-brain/dashboards/README.md` - Dashboard overview
- `cortex-brain/brain-protection-rules.yaml` - SKULL governance rules

---

**Status:** 🟢 Ready for Autonomous Execution  
**Last Updated:** December 7, 2025  
**Plan Owner:** Asif Hussain (AI Assistant)  
**Estimated Completion:** December 12-14, 2025
