# 📋 GUIDED Orchestrators Assessment & Migration Plan

**Plan ID:** guided-orchestrators-assessment  
**Feature:** Assessment and Potential Migration of TDD, Debug, Sanitization, Refinement Orchestrators  
**Created:** January 2, 2026  
**Complexity:** TIER 4 (STRATEGIC DECISION + POTENTIAL MIGRATIONS)  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.4)  
**Strategy:** Assess each GUIDED orchestrator for autonomous conversion viability  
**Estimated Duration:** 9 days (3d assessment + 6d selective migrations)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Assessment Framework | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 1 | TDD Orchestrator Analysis | `██████████` | 1d | ✅ **APPROVED** |
| 2 | Debug Orchestrator Analysis | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 3 | Sanitization Analysis | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 4 | Refinement Analysis | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 5 | Strategic Recommendations | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 6 | Selective Migrations | `░░░░░░░░░░` | 5d | ⏸️ Not Started |

---

## 🎯 Executive Summary

### Assessment Objectives

**Goal:** Determine which GUIDED orchestrators should convert to AUTONOMOUS and which should remain GUIDED.

**Decision Criteria:**
1. **Complexity of Operations** - Does it require complex AST parsing, multi-phase analysis?
2. **Workflow Simplicity** - Can it be expressed as pure Python logic?
3. **State Management Needs** - Does it require transactional rollback?
4. **User Interaction Requirements** - Does it benefit from approval workflows?
5. **Maintenance Cost** - Is Python easier to maintain than manifest instructions?

### Orchestrators Under Assessment

| Orchestrator | Current Type | Complexity | Preliminary Assessment |
|--------------|--------------|------------|------------------------|
| **TDD Mastery** | 📋 GUIDED | HIGH | ✅ **APPROVED FOR AUTONOMOUS** - Decision: January 2, 2026 |
| **Debug** | 📋 GUIDED | MEDIUM-HIGH | 🟡 **LIKELY AUTONOMOUS** - Marker injection + AST analysis |
| **Sanitization** | 📋 GUIDED | HIGH | 🟢 **AUTONOMOUS** - 5-phase transformation needs transactions |
| **Refinement** | 📋 GUIDED | MEDIUM | 🔵 **REMAIN GUIDED** - Analysis benefits from tool call sequences |

---

## 🏗️ Phase 0: Assessment Framework (1 day)

**Goal:** Establish decision criteria and evaluation methodology

### Task 0.1: Decision Matrix Creation
**Duration:** 4h

**File:** `artifacts/autonomous-vs-guided-decision-matrix.md`

**Matrix:**
```
| Criterion | Weight | AUTONOMOUS Score | GUIDED Score |
|-----------|--------|------------------|--------------|
| Operation Complexity | 30% | High complexity favors autonomous | Low complexity OK for guided |
| State Management | 25% | Multi-phase rollback → autonomous | Simple state → guided |
| User Interaction | 20% | Approval gates work in both | Interactive refinement → guided |
| Maintenance Cost | 15% | Python easier to maintain | Manifests simpler for linear flows |
| Code Reusability | 10% | Libraries/utils favor autonomous | One-off logic OK for guided |

**Scoring:** 0-10 for each criterion, weighted sum → recommendation threshold
```

### Task 0.2: Evaluation Template
**Duration:** 2h

**File:** `artifacts/orchestrator-evaluation-template.md`

Template for each orchestrator:
- Current implementation analysis
- Complexity assessment (operations, state, interactions)
- Autonomous conversion effort estimate
- GUIDED maintenance effort
- Recommendation with confidence level
- Migration roadmap (if autonomous recommended)

### Task 0.3: Stakeholder Communication Plan
**Duration:** 2h

**File:** `artifacts/stakeholder-communication-plan.md`

**Special Focus:** TDD Orchestrator requires design discussion BEFORE enhancement.

**Communication Plan:**
- TDD: Schedule design review (present trade-offs, defer decision)
- Debug: Technical feasibility assessment (present recommendation)
- Sanitization: Implementation plan (high confidence autonomous)
- Refinement: Remain GUIDED justification

---

## 🧪 Phase 1: TDD Orchestrator Analysis (1 day)

**Goal:** Comprehensive analysis of TDD Mastery orchestrator with stakeholder discussion preparation

### Task 1.1: Current TDD Implementation Analysis
**Duration:** 4h

**File:** `context/tdd-orchestrator-analysis.md`

**Analyze:**
- `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`
- Current RED→GREEN→REFACTOR enforcement
- Test execution framework
- Coverage tracking
- Failure reporting

**Document:**
- Workflow complexity (3-phase TDD cycle)
- State tracking requirements
- Test framework integration (pytest, unittest)
- Coverage tool integration (coverage.py)

### Task 1.2: Autonomous Conversion Feasibility
**Duration:** 2h

**File:** `artifacts/tdd-autonomous-feasibility.md`

**Analysis:**
- Can RED phase be enforced algorithmically? (Yes - run tests, verify failures)
- Can GREEN phase be validated? (Yes - run tests, verify passes)
- Can REFACTOR phase be automated? (⚠️ Complex - requires code quality metrics)
- State management: Multi-phase with rollback (favors autonomous)
- User interaction: Approval after GREEN (works in both)

### Task 1.3: Stakeholder Discussion Document
**Duration:** 2h

**File:** `artifacts/tdd-stakeholder-discussion.md`

**Content:**
- **Problem Statement:** Current GUIDED approach vs autonomous benefits
- **Option A:** Convert to AUTONOMOUS
  - Pros: Transactional test execution, better state tracking, Master Orch integration
  - Cons: Higher initial development cost, complex REFACTOR automation
- **Option B:** Remain GUIDED
  - Pros: Simpler manifest updates, tool call sequences work well
  - Cons: No state persistence, manual progress tracking
- **Option C:** Hybrid (AUTONOMOUS test execution, GUIDED refinement)
  - Pros: Best of both worlds
  - Cons: More complex architecture
- **Recommendation:** [To be decided in discussion]
- **Next Steps:** Schedule design review

### ⚠️ CRITICAL DECISION POINT

**TDD Orchestrator Enhancement: ✅ APPROVED FOR AUTONOMOUS CONVERSION**

**Decision Date:** January 2, 2026  
**Decision:** Convert TDD Orchestrator to AUTONOMOUS (v2) with Master Orchestrator integration

**Rationale:**
- ✅ **State Management:** Multi-phase TDD cycle (RED→GREEN→REFACTOR) requires transactional state tracking
- ✅ **Test Execution:** Python-native test framework integration (pytest, unittest) more robust than tool calls
- ✅ **Rollback Capability:** REFACTOR phase failures need atomic rollback to GREEN state
- ✅ **Master Orchestrator Integration:** Pattern-based routing enables deterministic TDD workflow
- ✅ **Coverage Tracking:** Automated coverage.py integration with database persistence
- ✅ **SKULL Enforcement:** Programmatic RED→GREEN→REFACTOR validation

**Next Steps:**
1. Generate TDD v2 migration plan via Planning v5: `/CORTEX Plan TDD Orchestrator v2 Migration`
2. Execute 4-day migration (test runner abstraction + state machine + Master Orch integration)
3. Progressive activation after successful testing

---

## 🐛 Phase 2: Debug Orchestrator Analysis (0.5 days)

**Goal:** Assess Debug orchestrator for autonomous conversion

### Task 2.1: Debug Orchestrator Analysis
**Duration:** 2h

**File:** `context/debug-orchestrator-analysis.md`

**Current Capabilities:**
- Error marker injection (AST manipulation)
- Stack trace analysis
- Failure reproduction
- Fix suggestion generation

**Complexity Assessment:**
- AST parsing: HIGH (complex operations)
- Multi-file analysis: MEDIUM (workspace search)
- State tracking: MEDIUM (error locations, attempted fixes)

### Task 2.2: Autonomous Conversion Recommendation
**Duration:** 2h

**File:** `artifacts/debug-autonomous-recommendation.md`

**Recommendation:** 🟢 **CONVERT TO AUTONOMOUS**

**Rationale:**
- ✅ Complex AST manipulation benefits from Python libraries
- ✅ Multi-phase debugging (detect → analyze → inject → verify) needs state
- ✅ Error handling + rollback important (revert bad marker injections)
- ✅ Reusable utilities (AST parsers, marker injectors)

**Migration Effort:** 3 days
- Day 1: Core DebugOrchestratorV2 + AST engine
- Day 2: Marker injection + fix suggestion
- Day 3: Testing + Master Orch integration

---

## 🧹 Phase 3: Sanitization Orchestrator Analysis (0.5 days)

**Goal:** Assess Sanitization orchestrator for autonomous conversion

### Task 3.1: Sanitization Analysis
**Duration:** 2h

**File:** `context/sanitization-orchestrator-analysis.md`

**Current 5-Phase Workflow:**
1. Discovery: Find sensitive data patterns
2. Classification: Categorize (API keys, emails, credentials)
3. Transformation: Replace with generic placeholders
4. Validation: Ensure no data leakage
5. Reporting: Generate sanitization report

**Complexity:** HIGH (5 phases, needs rollback, regex patterns, validation)

### Task 3.2: Autonomous Conversion Recommendation
**Duration:** 2h

**File:** `artifacts/sanitization-autonomous-recommendation.md`

**Recommendation:** 🟢 **CONVERT TO AUTONOMOUS** (High Confidence)

**Rationale:**
- ✅ 5-phase workflow needs transaction boundaries
- ✅ Rollback critical (revert sanitization if validation fails)
- ✅ Complex regex pattern matching (better in Python)
- ✅ State persistence important (track sanitized files)
- ✅ Reusable pattern libraries

**Migration Effort:** 2 days
- Day 1: Core SanitizationOrchestratorV2 + pattern engine
- Day 2: Testing + Master Orch integration

---

## 🔧 Phase 4: Refinement Orchestrator Analysis (0.5 days)

**Goal:** Assess Refinement orchestrator for potential conversion

### Task 4.1: Refinement Analysis
**Duration:** 2h

**File:** `context/refinement-orchestrator-analysis.md`

**Current 7-Phase Workflow:**
1. Discovery: Find improvement opportunities
2. Analysis: Code quality metrics
3. Prioritization: Rank improvements
4. Planning: Create refinement plan
5. Execution: Apply improvements
6. Validation: Verify improvements
7. Reporting: Generate report

**Complexity:** MEDIUM (analysis-heavy, less transactional)

### Task 4.2: GUIDED Retention Recommendation
**Duration:** 2h

**File:** `artifacts/refinement-remain-guided-recommendation.md`

**Recommendation:** 🔵 **REMAIN GUIDED**

**Rationale:**
- ✅ Analysis phases benefit from tool call sequences (iterative discovery)
- ✅ User interaction important (approve improvements before execution)
- ✅ Linear workflow (no complex state management)
- ❌ Conversion effort (3+ days) not justified by benefits
- ✅ Current GUIDED approach works well

**Enhancement:** Update manifest to reference Master Orchestrator for routing.

---

## 📊 Phase 5: Strategic Recommendations (0.5 days)

**Goal:** Consolidate findings and create migration roadmap

### Task 5.1: Consolidated Recommendation Report
**Duration:** 3h

**File:** `artifacts/consolidated-recommendations.md`

**Summary Table:**

| Orchestrator | Recommendation | Confidence | Effort | Priority |
|--------------|----------------|------------|--------|----------|
| **TDD Mastery** | 🔴 **DISCUSSION REQUIRED** | N/A | TBD | HIGH |
| **Debug** | 🟢 **CONVERT AUTONOMOUS** | HIGH | 3d | MEDIUM |
| **Sanitization** | 🟢 **CONVERT AUTONOMOUS** | HIGH | 2d | HIGH |
| **Refinement** | 🔵 **REMAIN GUIDED** | HIGH | 0d | LOW |

**Total Migration Effort:** 5 days (Debug + Sanitization, excluding TDD pending discussion)

### Task 5.2: Migration Roadmap
**Duration:** 1h

**File:** `artifacts/migration-roadmap.md`

**Recommended Sequence:**
1. **Sanitization v2** (2 days) - Highest confidence, high priority
2. **Debug v2** (3 days) - High confidence, complex implementation
3. **TDD Discussion** (TBD) - Pending stakeholder decision
4. **Refinement Enhancement** (0.5 days) - Update manifest for Master Orch routing

---

## 🔄 Phase 6: Selective Migrations (5 days)

**Goal:** Execute approved migrations

### Task 6.1: Sanitization Orchestrator v2 Migration
**Duration:** 2 days

**Plan:** Create detailed migration plan (similar to ADO v2, Vacuum v2 structure)

**Files to Create:**
- `sanitization-v2-migration/00-master-plan.md`
- `src/orchestrators/sanitization/sanitization_orchestrator_v2.py`
- `cortex-brain/manifests/orchestrators/sanitization-orchestrator-v2.yaml`

**Phases:**
0. Foundation (0.5d)
1. Core Implementation (1d)
2. Testing (0.5d)

### Task 6.2: Debug Orchestrator v2 Migration
**Duration:** 3 days

**Plan:** Create detailed migration plan

**Files to Create:**
- `debug-v2-migration/00-master-plan.md`
- `src/orchestrators/debug/debug_orchestrator_v2.py`
- `src/orchestrators/debug/ast_marker_injector.py`
- `cortex-brain/manifests/orchestrators/debug-orchestrator-v2.yaml`

**Phases:**
0. Foundation (0.5d)
1. Core + AST Engine (1.5d)
2. Testing (1d)

### Task 6.3: Refinement Manifest Enhancement
**Duration:** 0.5 days

**Update:** `cortex-brain/manifests/orchestrators/refinement-orchestrator-v4.yaml`

**Changes:**
- Add Master Orchestrator routing metadata
- Update pattern matching rules
- Preserve GUIDED execution model

---

## 🎉 Assessment Completion Checklist

### Phase 0-5: Assessment Complete
- [ ] Decision matrix established
- [ ] All 4 orchestrators analyzed
- [ ] TDD stakeholder discussion document prepared
- [ ] Debug conversion recommended (HIGH confidence)
- [ ] Sanitization conversion recommended (HIGH confidence)
- [ ] Refinement GUIDED retention recommended (HIGH confidence)
- [ ] Consolidated recommendation report generated
- [ ] Migration roadmap created

### Phase 6: Migrations (Conditional)
- [ ] Sanitization v2 migrated (if approved)
- [ ] Debug v2 migrated (if approved)
- [ ] TDD approach decided (pending stakeholder discussion)
- [ ] Refinement manifest enhanced

### Documentation
- [ ] All analysis documents in `context/`
- [ ] All recommendations in `artifacts/`
- [ ] Migration plans created for approved conversions

---

## ⚠️ Critical Decision Point: TDD Orchestrator

**STATUS:** 🔴 **DISCUSSION REQUIRED**

Before proceeding with TDD enhancement, stakeholder design review required to determine:
- Autonomous vs GUIDED architecture
- REFACTOR phase automation strategy
- Test framework integration approach
- Master Orchestrator routing design

**Deliverable:** `artifacts/tdd-stakeholder-discussion.md` presents trade-offs without making the decision.

---

**Status:** ⏸️ NOT STARTED  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.4)  
**Estimated Start:** After Cleanup v2 complete  
**Duration:** 3 days assessment + 5 days selective migrations (excluding TDD pending discussion)
