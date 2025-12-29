# CORTEX Lens V3 - Master Sub-Plan Structure

**Version:** 1.0  
**Date:** December 14, 2025  
**Author:** Asif Hussain  
**Status:** 🎯 ACTIVE EXECUTION  
**Parent Plan:** CORTEX-LENS-V3.md

---

## 🎯 Purpose

This master plan breaks down CORTEX Lens V3 implementation into **view-by-view interactive sub-plans**. Each sub-plan focuses on a single view/tab with iterative development and user approval before proceeding.

**Key Principle:** 🔄 **Build → Review → Refine → Approve → Next**

---

## 📋 Sub-Plan Hierarchy

### Phase 1: Console App Template (5 Sub-Plans)

#### **Sub-Plan 1: Landing Page/Home View** 🚀 CURRENT
- **File:** `CORTEX-LENS-V3-SUBPLAN-1-LANDING-PAGE.md`
- **Scope:** Initial dashboard load, navigation, KPI overview
- **Components:** Header, sidebar, theme toggle, KPI cards, health radar
- **Mock Review:** Test with sample data, validate glassmorphism
- **Exit Criteria:** ✅ User approves landing experience

#### **Sub-Plan 2: Executive Brief Tab**
- **File:** `CORTEX-LENS-V3-SUBPLAN-2-EXECUTIVE-BRIEF.md`
- **Scope:** Business narratives display (7 narrative engines)
- **Components:** Narrative panels, problem domain, use cases, competitive positioning
- **Mock Review:** Test narrative rendering with real CORTEX data
- **Exit Criteria:** ✅ Non-technical stakeholders understand narrative

#### **Sub-Plan 3: Architecture Tab**
- **File:** `CORTEX-LENS-V3-SUBPLAN-3-ARCHITECTURE.md`
- **Scope:** Code structure visualization
- **Components:** Module graph (D3 force-directed), layer detection, entry points
- **Mock Review:** Test with CORTEX multi-layer structure
- **Exit Criteria:** ✅ Architecture accurately represented

#### **Sub-Plan 4: Code Quality Tab**
- **File:** `CORTEX-LENS-V3-SUBPLAN-4-CODE-QUALITY.md`
- **Scope:** Complexity metrics, documentation coverage
- **Components:** Cyclomatic complexity charts, docstring coverage, hotspot identification
- **Mock Review:** Test with high/low complexity modules
- **Exit Criteria:** ✅ Quality metrics actionable

#### **Sub-Plan 5: Dependencies & Testing Tabs**
- **File:** `CORTEX-LENS-V3-SUBPLAN-5-DEPS-TESTING.md`
- **Scope:** Remaining console app tabs
- **Components:** Dependency graphs, test coverage, CLI command catalog
- **Mock Review:** Complete console app template validation
- **Exit Criteria:** ✅ Console app template production-ready

### Phase 2: API Service Template (4 Sub-Plans)

#### **Sub-Plan 6: API Overview & Endpoints**
- **File:** `CORTEX-LENS-V3-SUBPLAN-6-API-OVERVIEW.md`
- **Scope:** API service landing, endpoint catalog with filtering
- **Components:** Endpoint list, HTTP method badges, route hierarchy tree
- **Mock Review:** Test with REST API sample data
- **Exit Criteria:** ✅ API endpoints discoverable and filterable

#### **Sub-Plan 7: Security & Auth**
- **File:** `CORTEX-LENS-V3-SUBPLAN-7-API-SECURITY.md`
- **Scope:** Security scan, authentication patterns
- **Components:** Vulnerability list, auth flow diagrams, CORS config
- **Mock Review:** Test with OWASP Top 10 scenarios
- **Exit Criteria:** ✅ Security issues clearly communicated

#### **Sub-Plan 8: Data Models & Testing**
- **File:** `CORTEX-LENS-V3-SUBPLAN-8-API-MODELS.md`
- **Scope:** Data model catalog, contract testing
- **Components:** Model cards, field types, validation rules, test results
- **Mock Review:** Test with complex DTOs
- **Exit Criteria:** ✅ Data contracts documented

#### **Sub-Plan 9: API Performance & Dependencies**
- **File:** `CORTEX-LENS-V3-SUBPLAN-9-API-PERF.md`
- **Scope:** Load test results, dependency analysis
- **Components:** Performance charts, response time metrics, package inventory
- **Mock Review:** Complete API service template validation
- **Exit Criteria:** ✅ API service template production-ready

### Phase 3: Remaining Templates (6 Sub-Plans)

Templates to break down: Full-Stack Web, Database Project, Microservices, Library Package

---

## 🔄 Workflow Per Sub-Plan

### 🚨 **MANDATORY TDD ENFORCEMENT**

**ALL sub-plans MUST follow RED→GREEN→REFACTOR cycle. NO EXCEPTIONS.**

**Brain Protection:** `TDD_ENFORCEMENT` and `RED_PHASE_VALIDATION` active.

### 1. **Implementation Phase** (TDD Cycle)
```
RED → GREEN → REFACTOR (MANDATORY)
├── RED: Write failing tests for view components
│   ├── Structure tests (HTML elements exist)
│   ├── Layout tests (CSS properties correct)
│   ├── Behavior tests (JavaScript functions work)
│   └── Regression tests (prevent known issues)
├── GREEN: Implement minimal working view
│   ├── HTML structure
│   ├── CSS styling (glassmorphism, responsiveness)
│   ├── JavaScript interactivity
│   └── Mock data integration
└── REFACTOR: Optimize and clean up
    ├── Remove code duplication
    ├── Improve performance
    ├── Enhance accessibility
    └── Document complex logic
```

**Test Coverage Requirements:**
- ✅ **Structure:** 100% of DOM elements validated
- ✅ **Layout:** Fixed sidebar, responsive breakpoints tested
- ✅ **Styling:** Glassmorphism, theme switching, animations
- ✅ **Behavior:** Tab switching, data loading, chart rendering
- ✅ **Regression:** All previous bugs have tests

**Test File Location:**
- Tests: `cortex-lens-output/mock-{view}/tests/{view}.test.js`
- Runner: `cortex-lens-output/mock-{view}/tests/test-runner.html`

**Test Execution:**
- Run tests before commit: Open `test-runner.html` in browser
- All tests must pass: 100% pass rate required
- Document failures: Add regression tests for any bugs found

### 2. **Mock Review Phase**
├── Refactor with design system standards
└── Validate test coverage (>80%)
```

### 2. **Mock Review Phase** (Interactive)
```
GENERATE → REVIEW → ITERATE
├── Generate dashboard with mock data
├── User reviews in browser (localhost or file://)
├── Capture feedback (styling, UX, data presentation)
├── Iterate until user approves
└── Document approval checkpoint
```

### 3. **Integration Phase**
```
INTEGRATE → VALIDATE → CHECKPOINT
├── Merge view into template
├── Run integration tests (21/22 Selenium suite)
├── Performance check (load time <5s)
├── Git checkpoint with descriptive commit
└── Update progress tracker
```

### 4. **Transition to Next**
```
DOCUMENT → PLAN → START
├── Document lessons learned
├── Update master sub-plan progress
├── Create next sub-plan file
└── Begin next view (repeat workflow)
```

---

## 📊 Progress Tracking

### Overall Progress
```
Console App Template:    [████░░░░░░░░░░░░░░░░]  20% (1/5 sub-plans - TDD harness complete)
API Service Template:    [░░░░░░░░░░░░░░░░░░░░]   0% (0/4 sub-plans)
Remaining Templates:     [░░░░░░░░░░░░░░░░░░░░]   0% (0/6 sub-plans)
```

### Sub-Plan Status

| ID | Sub-Plan | Status | TDD Tests | User Approval | Completion Date |
|----|----------|--------|-----------|---------------|-----------------|
| 1 | Landing Page/Home View | ✅ Implemented + Tested | ✅ 30+ tests (100%) | ⏳ Review | - |
| 2 | Executive Brief Tab | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |
| 3 | Architecture Tab | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |
| 4 | Code Quality Tab | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |
| 5 | Dependencies & Testing | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |
| 6 | API Overview & Endpoints | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |
| 7 | Security & Auth | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |
| 8 | Data Models & Testing | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |
| 9 | API Performance & Deps | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |
| ... | Additional templates | ⏳ Not Started | ⏳ Pending | ⏳ Pending | - |

**TDD Compliance:** ✅ Test harness created for Sub-Plan 1  
**Template:** `CORTEX-LENS-V3-TDD-TEST-TEMPLATE.md` available for all future sub-plans

---

## 🎨 Design System Compliance

All sub-plans MUST adhere to CORTEX Universal Design System:

**Glassmorphism Standards:**
- Background: `rgba(255, 255, 255, 0.05)`
- Border: `1px solid rgba(255, 255, 255, 0.1)`
- Backdrop filter: `blur(10px)`
- Box shadow: `0 8px 32px rgba(0, 0, 0, 0.2)`

**Typography:**
- Headings: 32-48px (large impact)
- Body: 18px (readable)
- Labels: 16px (clear)
- Monospace: 14px (code)

**Color Palette:**
- Primary: `#00d4ff` (cyan)
- Success: `#00ff88` (green)
- Warning: `#ffaa00` (orange)
- Danger: `#ff4444` (red)
- Neutral: `#888888` (gray)

**Icons:**
- Size: 64px (extra-large emoji for visual impact)
- Usage: Consistent emoji selection per concept

---

## 🚨 Critical Success Factors

### Per Sub-Plan
- ✅ **TDD Compliance:** RED→GREEN→REFACTOR cycle followed
- ✅ **Test Coverage:** >80% for view components
- ✅ **User Approval:** Explicit checkpoint before next sub-plan
- ✅ **Performance:** <5s load time for view
- ✅ **Design System:** No inline styles, glassmorphism enforced

### Overall Project
- ✅ **No View Left Behind:** Each view fully functional before moving on
- ✅ **Mock-First Development:** Test with real data before integration
- ✅ **Iterative Refinement:** User feedback incorporated immediately
- ✅ **Git Checkpoints:** Commit after each sub-plan approval
- ✅ **Progress Transparency:** Master tracker updated after each sub-plan

---

## 📝 Documentation Per Sub-Plan

Each sub-plan file MUST contain:

1. **Scope Definition**
   - View/tab name
   - Components to build
   - Data requirements
   - Dependencies

2. **TDD Implementation Plan**
   - Test cases (RED phase)
   - Implementation steps (GREEN phase)
   - Refactoring opportunities (REFACTOR phase)

3. **Mock Review Checklist**
   - Mock data generation
   - Browser testing steps
   - User feedback capture form
   - Approval criteria

4. **Integration Steps**
   - Template file modifications
   - CSS/JS updates
   - Test suite execution
   - Git commit message

5. **Lessons Learned**
   - What worked well
   - What could improve
   - Insights for next sub-plan

---

## 🔗 Related Files

- **Parent Plan:** `CORTEX-LENS-V3.md` (2665 lines, phases 0-7)
- **Design System:** `cortex-brain/design-system/` (glassmorphism specs)
- **Template Base:** `src/cortex_lens/templates/base/` (shared components)
- **Console Template:** `src/cortex_lens/templates/console_app/` (520 LOC)
- **API Template:** `src/cortex_lens/templates/api_service/` (735 LOC)
- **Test Suite:** `tests/test_dashboard_rendering.py` (21/22 passing)

---

## 🎯 Next Action

**START:** Sub-Plan 1 - Landing Page/Home View  
**File:** `CORTEX-LENS-V3-SUBPLAN-1-LANDING-PAGE.md`  
**Goal:** Build initial dashboard experience with KPI overview and navigation

---

**Last Updated:** December 14, 2025  
**Master Plan Status:** 🚀 EXECUTION PHASE
