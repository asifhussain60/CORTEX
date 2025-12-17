# Sprint 4 Migration Plan

**Sprint:** 4  
**Created:** December 2, 2024  
**Status:** READY TO START  
**Estimated Duration:** 4-5 hours

---

## 🎯 Sprint Objectives

Continue orchestrator-to-utility migration with 3 high-value targets:
1. **Analysis Engine** (969 lines) - Code analysis for reviews
2. **Onboarding Orchestrator** (843 lines) - User onboarding workflow
3. **Lint Validation Orchestrator** (461 lines) - Multi-language code quality

**Success Criteria:**
- ✅ All operations complete in <3s
- ✅ System alignment passing
- ✅ ~700-900 lines removed (30-40% reduction)
- ✅ Zero functionality loss

---

## 📊 Orchestrator Analysis

### Current State (27 Orchestrators)

**Top 15 by Size:**
1. swagger_entry_point_orchestrator.py - 1,572 lines (61KB) - **Skip: Critical entry point**
2. setup_epm_orchestrator.py - 1,123 lines (43KB) - **Skip: EPM setup complexity**
3. upgrade_orchestrator.py - 1,115 lines (42KB) - **Skip: Critical upgrade system**
4. **analysis_engine.py - 969 lines (42KB)** ⭐ **TARGET 1**
5. **onboarding_orchestrator.py - 843 lines (28KB)** ⭐ **TARGET 2**
6. master_setup_orchestrator.py - 28KB - **Skip: Setup orchestrator**
7. ux_enhancement_orchestrator.py - 25KB - **Skip: UX complexity**
8. session_completion_orchestrator.py - 22KB - **Skip: Session management**
9. pr_context_builder.py - 20KB - **Skip: PR integration (Phase 2)**
10. brain_init_orchestrator.py - 19KB - **Skip: Critical initialization**
11. unified_entry_point_orchestrator.py - 18KB - **Skip: Entry point**
12. **lint_validation_orchestrator.py - 461 lines (16KB)** ⭐ **TARGET 3**
13. realignment_orchestrator.py - 15KB - **Defer: System alignment**
14. phase8_operation_handler.py - 15KB - **Defer: Phase handler**
15. metrics_tracker.py - 15KB - **Defer: Metrics system**

---

## 🎯 Sprint 4 Task Selection

### Task 9: Analysis Engine Migration ⭐ HIGH VALUE

**File:** `src/orchestrators/analysis_engine.py` (969 lines, 42KB)

**Current Structure:**
- **Enums (2):** IssueSeverity (CRITICAL/WARNING/SUGGESTION), IssueCategory (6 categories)
- **Dataclasses (2):** IssueFinding, AnalysisResult
- **Base Class:** BaseAnalyzer (abstract)
- **Concrete Analyzers (~700 lines):** BreakingChangeAnalyzer, CodeSmellAnalyzer, BestPracticeAnalyzer, SecurityAnalyzer, PerformanceAnalyzer, TDDViolationAnalyzer

**Analysis:**
- **Core Purpose:** Detect code issues for review feature
- **Dependencies:** Used by code review orchestrator (now migrated to utility)
- **Migration Strategy:** Extract base analyzer logic, simplify concrete analyzers
- **Target:** ~600 lines (38% reduction, 369 lines removed)

**Operations to Implement (5-6):**
1. `analyze_file()` - Run all analyzers on single file
2. `analyze_changes()` - Run analyzers on git diff
3. `get_breaking_changes()` - Detect breaking changes
4. `check_security()` - Security vulnerability scan
5. `check_performance()` - Performance issue detection
6. `generate_analysis_report()` - Create analysis report

**Simplifications:**
- Remove heavy pattern matching (use simple regex)
- Consolidate analyzer initialization
- Remove confidence scoring complexity
- Simplify reporting (basic markdown vs. complex formatting)

**Estimated Impact:**
- Code reduction: 369 lines (38%)
- Performance: <2s for file analysis
- Complexity: Medium (multiple analyzers)

---

### Task 10: Onboarding Orchestrator Migration ⭐ MEDIUM VALUE

**File:** `src/orchestrators/onboarding_orchestrator.py` (843 lines, 28KB)

**Current Structure:**
- **Class:** OnboardingOrchestrator
- **Profile System:** 2-question micro-survey (experience level, interaction mode)
- **Tech Stack Presets:** Azure/AWS/GCP/Custom
- **Integration:** Tier 1 Working Memory (profile storage)
- **Features:** Progress notifications, resumable, FIFO exemption

**Analysis:**
- **Core Purpose:** First-time user onboarding (10-second survey)
- **Dependencies:** Tier 1 Working Memory, Progress Decorator
- **Migration Strategy:** Extract profile creation, simplify survey logic
- **Target:** ~550 lines (35% reduction, 293 lines removed)

**Operations to Implement (5):**
1. `create_profile()` - Create user profile from survey responses
2. `load_profile()` - Load existing user profile
3. `update_profile()` - Update profile preferences
4. `run_onboarding()` - Interactive 2-question survey
5. `validate_profile()` - Validate profile completeness

**Simplifications:**
- Remove progress notifications (overkill for 10-second survey)
- Simplify tech stack presets (basic JSON config vs. nested dicts)
- Remove resumable logic (survey is <10s, just rerun)
- Streamline validation (basic checks vs. complex rules)

**Estimated Impact:**
- Code reduction: 293 lines (35%)
- Performance: <1s for profile creation
- Complexity: Low (simple survey logic)

---

### Task 11: Lint Validation Orchestrator Migration ⭐ LOW VALUE

**File:** `src/orchestrators/lint_validation_orchestrator.py` (461 lines, 16KB)

**Current Structure:**
- **Enums (1):** ViolationSeverity (CRITICAL/WARNING/INFO)
- **Class:** Violation (dataclass-like)
- **Class:** LintValidationOrchestrator
- **Language Support:** .NET (Roslynator), Python (Pylint/Black), JavaScript (ESLint/Prettier)
- **Features:** Configurable rules, severity detection, phase blocking, auto-fix suggestions

**Analysis:**
- **Core Purpose:** Multi-language code quality validation for TDD phases
- **Dependencies:** External linters (Roslynator, Pylint, ESLint)
- **Migration Strategy:** Simplify to basic linting without TDD phase integration
- **Target:** ~300 lines (35% reduction, 161 lines removed)

**Operations to Implement (5):**
1. `lint_file()` - Run linter on single file
2. `lint_directory()` - Run linter on directory
3. `check_violations()` - Check for critical violations
4. `generate_lint_report()` - Create lint report
5. `list_violations()` - Query violations by severity

**Simplifications:**
- Remove TDD phase blocking logic (orthogonal concern)
- Remove auto-fix suggestions (just report violations)
- Simplify language detection (file extension only)
- Basic subprocess calls vs. complex wrapper logic

**Estimated Impact:**
- Code reduction: 161 lines (35%)
- Performance: <2s for file linting
- Complexity: Medium (multi-language support)

---

## 📋 Sprint 4 Task Summary

| Task | Orchestrator | Lines | Target | Reduction | Complexity | Priority |
|------|-------------|-------|--------|-----------|------------|----------|
| 9 | Analysis Engine | 969 | 600 | 369 (38%) | Medium | HIGH |
| 10 | Onboarding | 843 | 550 | 293 (35%) | Low | MEDIUM |
| 11 | Lint Validation | 461 | 300 | 161 (35%) | Medium | LOW |
| **Total** | **3 orchestrators** | **2,273** | **1,450** | **823 (36%)** | **Mixed** | - |

---

## 🎯 Sprint Options

### Option A: All 3 Orchestrators (RECOMMENDED) ⭐

**Tasks:** Analysis Engine + Onboarding + Lint Validation  
**Total Lines:** 2,273 → 1,450 (823 lines removed, 36% reduction)  
**Estimated Time:** 4-5 hours  
**Complexity:** Mixed (1 medium-high, 1 low, 1 medium)

**Pros:**
- ✅ Significant code reduction (823 lines)
- ✅ Completes 3 diverse orchestrator types
- ✅ Maintains Sprint 3 momentum (3 per sprint)
- ✅ Balanced complexity mix

**Cons:**
- ⚠️ Analysis Engine has multiple analyzers (more complex)
- ⚠️ Longer session (~5 hours)

**Recommendation:** **RECOMMENDED** - Maintains proven 3-orchestrator sprint pattern with manageable complexity.

---

### Option B: Analysis Engine + Onboarding (CONSERVATIVE)

**Tasks:** Analysis Engine + Onboarding  
**Total Lines:** 1,812 → 1,150 (662 lines removed, 37% reduction)  
**Estimated Time:** 3-4 hours  
**Complexity:** Medium-high + Low

**Pros:**
- ✅ High-value targets (analysis + onboarding)
- ✅ Significant code reduction (662 lines)
- ✅ Manageable time commitment
- ✅ Mixed complexity (easier balance)

**Cons:**
- ⚠️ Only 2 orchestrators (below Sprint 3 cadence)
- ⚠️ Leaves lint validation for later

**Recommendation:** Good fallback if time-constrained.

---

### Option C: All 3 + Metrics Tracker (AGGRESSIVE)

**Tasks:** Analysis Engine + Onboarding + Lint Validation + Metrics Tracker  
**Total Lines:** ~2,750 → ~1,800 (950 lines removed)  
**Estimated Time:** 6-7 hours  
**Complexity:** High

**Pros:**
- ✅ Maximum code reduction (950+ lines)
- ✅ 4 orchestrators migrated
- ✅ Accelerates CORTEX 3.0 timeline

**Cons:**
- ⚠️ Very long session (6-7 hours)
- ⚠️ High fatigue risk
- ⚠️ Complexity accumulation

**Recommendation:** **NOT RECOMMENDED** - Risk of fatigue and errors. Sprint 3's 3-orchestrator pattern is sustainable.

---

## 📊 Success Criteria

### Performance Targets
- All operations: <3s (Sprint 3 achieved 0.064-0.074s, 40-47x faster)
- File analysis: <2s
- Profile creation: <1s
- Linting: <2s per file

### Code Quality
- Zero functionality loss
- All tests passing
- System alignment: 8/8 checks
- Clean git history

### Reduction Targets
- Analysis Engine: 38% reduction (369 lines)
- Onboarding: 35% reduction (293 lines)
- Lint Validation: 35% reduction (161 lines)
- **Total: 36% reduction (823 lines)**

### System Impact
- Orchestrators: 27 → 24 (11% reduction from start of Sprint 4)
- Cumulative: 30 → 24 (20% reduction across Sprints 1-4)
- Code removed: ~6,500 lines (5,700 + 823)

---

## 🚀 Migration Strategy

### Proven Pattern (from Sprint 3)

**Phase 1: Investigation (30-45 min per orchestrator)**
1. Read orchestrator structure (lines 1-100)
2. Grep_search for methods/classes
3. Identify core operations vs. workflow logic
4. Document dependencies and simplifications

**Phase 2: Implementation (45-60 min per orchestrator)**
1. Create utility file with 5-6 core operations
2. Simplify dataclasses/enums
3. Remove heavy dependencies
4. Implement CRUD + core logic

**Phase 3: Testing (15-20 min per orchestrator)**
1. Direct utility test (measure performance)
2. Create CLI wrapper (if beneficial)
3. Real-world testing with actual files
4. Validate all operations

**Phase 4: Completion (10-15 min per orchestrator)**
1. Deprecate orchestrator (.bak)
2. Git commit with comprehensive message
3. Push to origin
4. System alignment validation

**Total per orchestrator:** ~2-2.5 hours  
**Total Sprint 4:** ~4-5 hours (Option A)

---

## ⚠️ Risk Assessment

### Medium Risks

1. **Analysis Engine Complexity**
   - **Risk:** 6 concrete analyzers with pattern matching
   - **Mitigation:** Start with base analyzer + 2-3 core analyzers, defer complex ones
   - **Impact:** Medium - may need simplified analyzer approach

2. **External Linter Dependencies**
   - **Risk:** Lint validation requires Pylint, ESLint, Roslynator installed
   - **Mitigation:** Graceful degradation if linters not found, focus on Python (always available)
   - **Impact:** Low - can test without all linters

### Low Risks

3. **Onboarding Tier 1 Integration**
   - **Risk:** Profile storage in Working Memory (Tier 1)
   - **Mitigation:** Tier 1 API stable, used successfully in past
   - **Impact:** Very Low - well-tested integration point

4. **Time Estimation**
   - **Risk:** 4-5 hour estimate may be optimistic with Analysis Engine complexity
   - **Mitigation:** Option B fallback (2 orchestrators, 3-4 hours)
   - **Impact:** Low - flexible sprint options

---

## 📅 Sprint Schedule

### Recommended Timeline (Option A)

**Hour 1-2: Task 9 - Analysis Engine**
- Investigation: 45 min
- Implementation: 60 min
- Testing: 15 min

**Hour 2.5-3.5: Task 10 - Onboarding**
- Investigation: 30 min
- Implementation: 45 min
- Testing: 15 min

**Hour 3.5-4.5: Task 11 - Lint Validation**
- Investigation: 30 min
- Implementation: 40 min
- Testing: 15 min

**Hour 4.5-5: Sprint Completion**
- System validation: 10 min
- Sprint 4 report: 20 min

**Total: 4-5 hours**

---

## 🎯 Sprint 4 Recommendation

**RECOMMENDED OPTION: A (All 3 Orchestrators)**

**Rationale:**
- Maintains proven 3-orchestrator cadence from Sprint 3
- Balanced complexity mix (1 medium-high, 1 low, 1 medium)
- Significant code reduction (823 lines, 36%)
- Manageable 4-5 hour time commitment
- Clear fallback to Option B if needed

**Next Steps:**
1. Confirm Option A selection
2. Begin Task 9: Analysis Engine investigation
3. Follow proven migration pattern
4. Complete with Sprint 4 report

---

**Plan Created:** December 2, 2024 17:55 PST  
**Author:** Asif Hussain  
**CORTEX Version:** 3.0.0 (Utility Migration Phase)  
**Ready for Execution:** YES
