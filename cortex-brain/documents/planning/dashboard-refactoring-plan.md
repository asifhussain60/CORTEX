# Dashboard Refactoring Plan

**Plan ID:** DASH-REFACTOR-2024-001  
**Created:** December 7, 2024  
**Status:** 🟡 Awaiting Approval  
**Author:** Asif Hussain

---

## 📋 Plan Overview

**Objective:** Systematically refactor the CORTEX dashboard system to eliminate architectural inconsistencies, standardize rendering patterns, and improve maintainability while preserving all functionality.

**Scope:** `cortex-brain/dashboards/ui/` (49 JavaScript files, 170 tests)

**Estimated Effort:** 3-5 days (distributed across 4 phases)

---

## 🎯 Problem Statement

**Current State Issues:**

1. **Inconsistent Rendering Patterns** (Terminal evidence shows recent fixes)
   - Progressive loader called inconsistently across tabs
   - Some components return HTML strings, others directly manipulate DOM
   - Mix of `showSkeleton/hideSkeleton` usage and direct rendering

2. **Architecture Drift**
   - `overview-tab.js` AND `overview-tab-v3.js` (redundant components)
   - Removed `architecture-panels.js` but import may remain in places
   - Tab components have different initialization signatures

3. **Performance Concerns**
   - `renderCurrentTab()` called 5+ times on source changes
   - Render cache clearing strategy unclear
   - No consistent lazy loading pattern

4. **Test Coverage Gaps**
   - 170 tests exist but unclear which cover refactored components
   - Tests may be checking old patterns (skeleton loader usage)

5. **Documentation Lag**
   - `README.md` references 7 JSON files, unclear if all still required
   - Component interaction flow not documented
   - No architectural decision records (ADRs)

**Risk Assessment:**
- 🔴 HIGH: Breaking existing functionality across 7 tabs
- 🟡 MEDIUM: Performance regression if caching breaks
- 🟢 LOW: Documentation updates

---

## 📐 Architecture Goals

**Target State:**

1. **Unified Component Pattern**
   ```javascript
   class TabComponent {
       constructor() { /* Setup */ }
       async init(data) { /* Render entry point */ }
       destroy() { /* Cleanup */ }
   }
   ```

2. **Standardized Data Flow**
   ```
   app.js (state) → renderCurrentTab() → TabComponent.init(data) → DOM
   ```

3. **Declarative Loading States**
   - Components declare loading requirements via metadata
   - Progressive loader automatically manages skeletons
   - Single source of truth for loading behavior

4. **Performance Optimization**
   - Lazy load tab code (dynamic imports)
   - Render caching with proper invalidation
   - IntersectionObserver for deferred rendering

---

## 🏗️ Phase Breakdown

### Phase 1: Discovery & Analysis (Day 1)
**Objective:** Map current state, identify all patterns, establish baseline

**Tasks:**
1. [ ] Audit all 7 tab components for rendering patterns
2. [ ] Document component interface variations
3. [ ] Identify all progressive loader usage points
4. [ ] Map data dependencies (what data each tab needs)
5. [ ] Review existing test coverage per component
6. [ ] Create component dependency graph
7. [ ] Document current performance metrics (baseline)

**Deliverables:**
- `dashboard-component-audit.md` (component interface matrix)
- `dashboard-data-flow-diagram.svg` (visual architecture)
- `dashboard-performance-baseline.json` (metrics snapshot)

**Definition of Ready:**
- ✅ All 49 JavaScript files cataloged
- ✅ Test suite passes (170 tests green)
- ✅ Dashboard runs without console errors
- ✅ Access to all 7 tab data files

**Definition of Done:**
- ✅ Audit document complete with all patterns documented
- ✅ Visual diagram shows component relationships
- ✅ Baseline performance metrics captured
- ✅ No regressions from analysis work

---

### Phase 2: Component Standardization (Days 2-3)
**Objective:** Unify component interfaces and rendering patterns

**Tasks:**
1. [ ] Create `BaseTabComponent` abstract class
2. [ ] Refactor `overview-tab-v3.js` to BaseTabComponent
3. [ ] Remove deprecated `overview-tab.js`
4. [ ] Migrate `tech-stack-tab.js` to standard pattern
5. [ ] Migrate `security-tab.js` to standard pattern
6. [ ] Migrate `architecture-tab.js` to standard pattern
7. [ ] Migrate `code-org-tab.js` to standard pattern
8. [ ] Migrate `vendors-tab.js` to standard pattern
9. [ ] Migrate `executive-tab.js` to standard pattern
10. [ ] Migrate `engineering-onboarding-tab.js` to standard pattern
11. [ ] Update `app.js` renderCurrentTab() for standard pattern
12. [ ] Remove unused progressive loader methods

**TDD Requirements (RED → GREEN → REFACTOR):**
- **RED:** Write failing test for BaseTabComponent interface
- **GREEN:** Implement minimal BaseTabComponent
- **REFACTOR:** Extract common patterns from existing components
- **RED:** Write failing test for first tab migration (overview-v3)
- **GREEN:** Migrate component to pass tests
- **REFACTOR:** Clean up and optimize
- **REPEAT:** For each remaining tab component

**Deliverables:**
- `src/components/BaseTabComponent.js` (abstract class)
- 8 refactored tab components following standard pattern
- Updated test suite (maintain 170+ test count)
- Migration guide document

**Definition of Ready:**
- ✅ Phase 1 complete (audit done)
- ✅ BaseTabComponent design approved
- ✅ Test infrastructure supports new pattern

**Definition of Done:**
- ✅ All 8 tab components inherit from BaseTabComponent
- ✅ All tests pass (no regressions)
- ✅ No console errors in browser
- ✅ Performance metrics match or exceed baseline
- ✅ Code review completed
- ✅ Documentation updated

---

### Phase 3: Progressive Loading Refactor (Day 3)
**Objective:** Centralize loading state management

**Tasks:**
1. [ ] Design declarative loading metadata schema
2. [ ] Update `progressive-loader.js` to use metadata
3. [ ] Add component-level loading declarations
4. [ ] Remove manual showSkeleton/hideSkeleton calls
5. [ ] Implement automatic skeleton management
6. [ ] Add loading state tests
7. [ ] Benchmark loading performance

**TDD Requirements:**
- **RED:** Test that metadata drives skeleton display
- **GREEN:** Implement metadata-driven loader
- **REFACTOR:** Simplify component code
- **RED:** Test skeleton auto-hide on render complete
- **GREEN:** Implement completion detection
- **REFACTOR:** Remove redundant timing logic

**Deliverables:**
- Enhanced `progressive-loader.js` with metadata support
- Component loading declarations
- Loading state test suite
- Performance comparison report

**Definition of Ready:**
- ✅ Phase 2 complete (components standardized)
- ✅ Metadata schema designed and approved
- ✅ Test plan for loading states defined

**Definition of Done:**
- ✅ Zero manual showSkeleton/hideSkeleton calls in components
- ✅ Loading states work automatically via metadata
- ✅ All loading tests pass
- ✅ Loading times improved or maintained
- ✅ Documentation updated with new pattern

---

### Phase 4: Performance & Polish (Day 4-5)
**Objective:** Optimize rendering and finalize documentation

**Tasks:**
1. [ ] Implement dynamic imports for tab components
2. [ ] Add IntersectionObserver for lazy rendering
3. [ ] Optimize render cache invalidation strategy
4. [ ] Add performance monitoring instrumentation
5. [ ] Create architectural decision records (ADRs)
6. [ ] Update README with new architecture
7. [ ] Create developer onboarding guide
8. [ ] Final performance audit
9. [ ] Security review (XSS, injection risks)
10. [ ] Accessibility audit (WCAG 2.1)

**TDD Requirements:**
- **RED:** Test lazy loading behavior (tab not rendered until viewed)
- **GREEN:** Implement dynamic imports
- **REFACTOR:** Optimize bundle splitting
- **RED:** Test cache invalidation correctness
- **GREEN:** Implement smart cache strategy
- **REFACTOR:** Simplify cache logic

**Deliverables:**
- Optimized `app.js` with lazy loading
- Performance monitoring dashboard
- Complete ADR set
- Updated documentation suite
- Security & accessibility reports

**Definition of Ready:**
- ✅ Phase 3 complete (loading refactored)
- ✅ Performance tooling set up
- ✅ Documentation templates prepared

**Definition of Done:**
- ✅ All 4 phases complete and tested
- ✅ Performance metrics show improvement:
  - Initial load time < baseline
  - Tab switch time < 100ms
  - Memory usage stable over 10 switches
- ✅ Zero console errors or warnings
- ✅ All 170+ tests pass
- ✅ Documentation complete and accurate
- ✅ Security review passed
- ✅ Accessibility score ≥ 95
- ✅ Code review approved by Architecture team
- ✅ Smoke tests passed on 3 data sources (mock, cortex, noor-canvas)

---

## 🔍 Success Metrics

**Performance:**
- Initial load time: < baseline (currently ~2s for mock data)
- Tab switch: < 100ms (target: 50ms)
- Memory usage: Stable over 10+ tab switches
- Bundle size: < 500KB uncompressed

**Quality:**
- Test coverage: ≥ 90% (maintain or improve from current 170 tests)
- Zero console errors
- Zero ESLint warnings
- Lighthouse score: ≥ 95

**Maintainability:**
- Component interface consistency: 100%
- Documentation completeness: 100%
- Code duplication: < 5% (measured by SonarQube)

---

## 🚨 Risk Mitigation

**Risk 1: Breaking Existing Functionality**
- **Mitigation:** TDD approach (RED → GREEN → REFACTOR mandatory)
- **Mitigation:** Maintain 170+ test count throughout
- **Mitigation:** Smoke test each phase on all 3 data sources

**Risk 2: Performance Regression**
- **Mitigation:** Baseline metrics established in Phase 1
- **Mitigation:** Performance gates in DoD criteria
- **Mitigation:** Benchmark suite run after each phase

**Risk 3: Scope Creep**
- **Mitigation:** Strict phase boundaries (no Phase 2 work in Phase 1)
- **Mitigation:** Approval required before starting each phase
- **Mitigation:** "Not in scope" list maintained

**Risk 4: Time Overrun**
- **Mitigation:** Daily check-ins on progress
- **Mitigation:** Phase 4 tasks can be deferred if needed
- **Mitigation:** Core functionality (Phases 1-3) prioritized

---

## 🎭 Roles & Responsibilities

**Plan Owner:** Asif Hussain (AI Assistant)  
**Reviewer:** User (approval required before execution)  
**Tester:** Automated test suite + manual smoke tests  
**Approver:** User (phase gate approvals)

---

## 📅 Timeline

**Total Duration:** 3-5 days (depends on approval speed)

| Phase | Duration | Start Condition | End Condition |
|-------|----------|----------------|---------------|
| Phase 1 | 1 day | Plan approved | Audit complete |
| Phase 2 | 1.5 days | Phase 1 DoD met | Components standardized |
| Phase 3 | 0.5 day | Phase 2 DoD met | Loading refactored |
| Phase 4 | 1-2 days | Phase 3 DoD met | All DoD criteria met |

---

## 🔄 Approval & Execution Options

**Option 1: Interactive Mode (Default)**
- You review each phase deliverables
- I proceed to next phase after your approval
- Allows for course correction

**Option 2: Autonomous Execution**
- Say "execute all phases autonomously"
- I complete all phases end-to-end
- Daily progress reports provided
- You can pause at any time

**Option 3: Phase-by-Phase**
- Say "start phase 1" to begin
- Each phase requires explicit approval
- Maximum control and oversight

---

## 📝 Next Steps

**To proceed, tell me:**

1. **Do you approve this plan?** (Yes/No/Modify)
2. **Which execution mode?** (Interactive/Autonomous/Phase-by-Phase)
3. **Any changes needed?** (Add tasks, remove tasks, adjust DoD)

**Quick Commands:**
- `approve plan` - Approve and start Phase 1
- `execute all phases autonomously` - Run end-to-end
- `modify plan [changes]` - Request modifications
- `start phase 1` - Begin Phase 1 only

---

## 📚 Related Documents

- `.github/prompts/modules/planning-orchestrator-guide.md` - Planning system details
- `.github/prompts/modules/tdd-mastery-guide.md` - TDD workflow
- `cortex-brain/dashboards/README.md` - Dashboard overview
- `cortex-brain/brain-protection-rules.yaml` - Governance rules (SKULL)

---

**Status:** 🟡 Awaiting Your Approval

**Last Updated:** December 7, 2024
