# CORTEX Investigation Orchestrator - Root Cause Analysis & Holistic Architecture Review

**Purpose:** Deep investigation system for finding root causes, fixing at architecture level, holistic architecture review against acceptance criteria, and wiring everything into Master Orchestrator  
**Version:** 2.0.0  
**Author:** Asif Hussain

---

## 🎯 Orchestrator Identity

**Name:** Investigation Orchestrator  
**Type:** 🛡️ AUTONOMOUS (Python-based)  
**Trigger Patterns:**
- `investigate [issue description]` - Specific issue investigation
- `find root cause of [issue]` - Targeted root cause analysis
- `why is [feature] breaking?` - Feature-specific debugging
- `debug architecture [problem]` - Architecture-level debugging
- `fix brittleness in [system]` - System fragility analysis
- `investigate` (NO arguments) - **Holistic architecture review mode**

**Priority:** 8 (High - executes before most orchestrators)

---

## 🔍 Dual Operation Modes

### Mode 1: Targeted Investigation (WITH user prompt)
Traditional root cause analysis for specific issues (detailed in phases below).

### Mode 2: Holistic Architecture Review (NO user prompt)
**AUTOMATIC TRIGGER:** When `investigate` is invoked without arguments, perform comprehensive architecture review.

**Full Specification:** See `cortex-investigate-holistic-review.prompt.md` for complete holistic review phases (H1-H6).

**Quick Summary:**
- **Phase H1:** Plan alignment review against `cortex-v5-holistic-refactor` + acceptance criteria
- **Phase H2:** 11-dimension gap analysis (edge cases, failure modes, security, performance, etc.)
- **Phase H3:** Robustness assessment (brittle patterns, robust alternatives, smarter solutions)
- **Phase H4:** Implementation roadmap (prioritized P0/P1/P2/P3 fixes with effort estimates)
- **Phase H5:** Automated fixes (quick wins, config hardening, test coverage)
- **Phase H6:** Executive report (stakeholder summary + presentation)

**Output:** 4,300+ lines of documentation in `cortex-brain/documents/investigations/holistic-review-{timestamp}/`

---

## 🔍 Dual Operation Modes

### Mode 1: Targeted Investigation (WITH user prompt)
Traditional root cause analysis for specific issues (original behavior).

### Mode 2: Holistic Architecture Review (NO user prompt)
**AUTOMATIC TRIGGER:** When `investigate` is invoked without arguments, perform comprehensive architecture review.

**Holistic Review Scope:**
1. **Plan Alignment Review**
   - Load `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-master-plan.md`
   - Load `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/artifacts/final-acceptance-criteria-link.md`
   - Review acceptance criteria (`cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md`)
   - Identify gaps between planned vs implemented architecture

2. **Gap Analysis Dimensions**
   - ⚠️ **Missing Edge Cases** - Unhandled scenarios, boundary conditions
   - 🔥 **Failure Modes** - Single points of failure, graceful degradation gaps
   - ⚡ **Race Conditions** - Concurrency issues, state management conflicts
   - 🚀 **Integration & Deployment Pitfalls** - Deployment risks, rollout gaps
   - 🔒 **Security Vulnerabilities** - Auth gaps, injection risks, data exposure
   - 🐌 **Performance Bottlenecks** - Slow queries, memory leaks, N+1 problems
   - 📈 **Scalability Limits** - Hard limits, resource constraints
   - ⏮️ **Rollback & Recovery** - Backup strategies, disaster recovery
   - ✅ **Data Integrity & Validation** - Schema validation, constraint enforcement
   - 📦 **Dependency Risks** - Version conflicts, supply chain risks
   - 🛠️ **Maintainability Issues** - Technical debt, code duplication, documentation gaps

3. **Acceptance Criteria Validation**
   - Bootstrap Phase (Phases 0-4.5) - Master Orchestrator, Planning v5, Context Middleware
   - Migration Phase (Phases 5-9) - ADO, Vacuum, TDD, SKULL compliance
   - REFACTOR Phase (Phase 10) - Cleanup tasks, orphaned code detection
   - Performance Benchmarks - Latency targets, token limits
   - SKULL Compliance - TDD enforcement, Git isolation, Knowledge Library integration

4. **Robustness Assessment**
   - Evaluate current architecture against production-grade standards
   - Identify brittle patterns requiring refactoring
   - Recommend robust alternatives with trade-off analysis
   - Propose smarter, future-proof solutions

**Holistic Review Output:**
```
cortex-brain/documents/investigations/holistic-review-{timestamp}/
├── architecture/
│   ├── gap-analysis-matrix.md (11-dimension analysis)
│   ├── acceptance-criteria-scorecard.md (plan validation)
│   └── robustness-assessment.md (production-readiness)
├── recommendations/
│   ├── high-priority-fixes.md (critical gaps)
│   ├── architecture-enhancements.md (robust alternatives)
│   └── smarter-solutions.md (future-proof improvements)
└── reports/
    ├── holistic-review-executive-summary.md
    └── implementation-roadmap.md (prioritized fixes)
```

**Priority:** 8 (High - executes before most orchestrators)

---

## 🏗️ Architecture

### Core Capabilities

1. **Root Cause Analysis**
   - Multi-layer investigation (code → config → architecture → system design)
   - Pattern detection across similar issues
   - Dependency chain analysis
   - Temporal analysis (when was it working? what changed?)

2. **Architecture-Level Fixes**
   - Not just patching symptoms
   - Redesign brittle patterns
   - Implement robust alternatives
   - Update configurations system-wide

3. **Master Orchestrator Integration**
   - Auto-register new patterns
   - Update routing rules
   - Wire new orchestrators
   - Update response templates

4. **Comprehensive Reporting**
   - Root cause document
   - Fix implementation report
   - Architecture enhancement proposal
   - Similar issues identified

---

## 🔍 Investigation Phases

### Phase Selection Logic

**IF user_prompt PROVIDED:**
  → Execute **Targeted Investigation** (Phases 1-6 below)

**IF user_prompt EMPTY/NULL:**
  → Execute **Holistic Architecture Review** (Phases H1-H6)

---

## 📋 Mode 1: Targeted Investigation Phases

### Phase 1: DISCOVER (30% of time)
**Goal:** Understand the issue completely

**Sub-Phases:**
1. **Symptom Collection**
   - Read error messages/logs
   - Identify user expectations vs actual behavior
   - Gather reproduction steps

2. **Context Gathering**
   - Related files (search workspace)
   - Configuration files
   - Recent changes (git history)
   - Similar patterns in codebase

3. **Dependency Mapping**
   - What depends on the broken component?
   - What does the broken component depend on?
   - Identify coupling points

**Deliverable:** `investigation-context-{timestamp}.json`

---

### Phase 2: ANALYZE (30% of time)
**Goal:** Find the root cause, not just symptoms

**Sub-Phases:**
1. **Layer Analysis**
   ```
   Layer 1: Code Implementation
   Layer 2: Configuration/Wiring
   Layer 3: Architecture/Design
   Layer 4: System Assumptions
   ```

2. **Pattern Detection**
   - Is this a one-off issue or systemic?
   - Search for similar patterns: `grep -r "pattern"`
   - Check if other orchestrators have the same issue

3. **Root Cause Hypothesis**
   - Generate 3-5 hypotheses
   - Test each hypothesis with evidence
   - Rank by likelihood and impact

4. **Impact Analysis**
   - What else is affected?
   - What breaks if we fix this?
   - Migration path required?

**Deliverable:** `root-cause-analysis-{timestamp}.md` (400+ lines)

**Example Root Cause Document Structure:**
```markdown
# Root Cause Analysis: [Issue Name]

## 🎯 Issue Summary
- **Symptom:** Continuation prompts not displaying
- **User Expectation:** Auto-display at 80% token threshold
- **Actual Behavior:** Never displays, only creates file

## 🔍 Investigation Trail

### Layer 1: Code Implementation ✅ EXISTS
- check_token_usage() returns user_message
- Planning v5 appends to success_message
- Vacuum v2 appends to completion_message

### Layer 2: Configuration/Wiring ❌ ROOT CAUSE
- Master Orchestrator doesn't render user_message
- Response returned but never displayed to user
- Missing: ResponseRenderer integration

### Layer 3: Architecture/Design ⚠️ SYSTEMIC ISSUE
- No standard response rendering pipeline
- Each orchestrator handles formatting independently
- No enforcement of user-facing message display

### Layer 4: System Assumptions ⚠️ GAP
- Assumed OrchestratorResult.message auto-displays
- No middleware to inject warnings into response
- No hook for appending system messages

## 🎯 Root Cause
**PRIMARY:** Master Orchestrator lacks ResponseRenderer integration  
**SECONDARY:** No middleware pipeline for injecting system messages  
**TERTIARY:** Orchestrators inconsistently handle user_message display

## 💡 Similar Issues Found
1. Error messages from orchestrators not displaying (same root cause)
2. Success messages missing metadata (same architecture gap)
3. Warnings from safety validators not visible (same issue)

## 📊 Impact
- **Affected:** All orchestrators (Planning, Vacuum, Cleanup, ADO, etc.)
- **Severity:** HIGH (user experience degraded, token warnings invisible)
- **Urgency:** HIGH (affects session continuity)
```

---

### Phase 3: DESIGN (20% of time)
**Goal:** Design robust, architecture-level solution

**Sub-Phases:**
1. **Solution Options**
   - Option A: Quick patch (band-aid fix)
   - Option B: Architecture refactor (proper fix)
   - Option C: Hybrid approach

2. **Trade-off Analysis**
   | Option | Time | Robustness | Maintainability | Breaks Existing? |
   |--------|------|------------|-----------------|------------------|
   | A      | 1h   | Low        | Low             | No               |
   | B      | 8h   | High       | High            | Maybe            |
   | C      | 4h   | Medium     | High            | No               |

3. **Architecture Enhancement**
   - New components needed
   - Modified components
   - Configuration changes
   - Migration strategy

4. **Master Orchestrator Wiring**
   - Routing rules to add
   - Response template updates
   - Middleware integration
   - Lifecycle hooks

**Deliverable:** `architecture-enhancement-proposal-{timestamp}.md` (500+ lines)

**Example Proposal Structure:**
```markdown
# Architecture Enhancement: Response Rendering Pipeline

## 🎯 Proposed Solution: Option C (Hybrid)

### Components

#### 1. ResponseRenderer (NEW)
```python
class ResponseRenderer:
    """
    Unified response rendering for all orchestrators.
    
    Features:
    - Template-driven formatting (response-templates-v4.yaml)
    - Automatic user_message injection
    - Tier-based complexity routing
    - Markdown generation
    """
    
    def render(
        self,
        orchestrator_result: OrchestratorResult,
        template_tier: str,
        context: Dict[str, Any]
    ) -> str:
        """Render orchestrator result to user-facing markdown"""
```

#### 2. ResponseMiddleware (NEW)
```python
class ResponseMiddleware:
    """
    Post-execution middleware for injecting system messages.
    
    Features:
    - Token warnings
    - Security alerts
    - Deprecation notices
    - Success messages
    """
```

#### 3. Master Orchestrator Integration
- Add ResponseRenderer instantiation
- Integrate in handle_request() after orchestrator execution
- Update return format to include rendered markdown

### Migration Strategy
1. Phase 1: Create ResponseRenderer (2h)
2. Phase 2: Integrate with Master Orchestrator (1h)
3. Phase 3: Update Planning v5 (remove manual message appending) (0.5h)
4. Phase 4: Update Vacuum v2 (same) (0.5h)
5. Phase 5: Test all orchestrators (1h)

### Backward Compatibility
- Orchestrators that manually append messages: Still works
- Orchestrators that return OrchestratorResult: Auto-rendered
- Zero breaking changes
```

---

### Phase 4: IMPLEMENT (40% of time)
**Goal:** Fix the issue at architecture level

**Sub-Phases:**
1. **Create New Components**
   - ResponseRenderer class
   - ResponseMiddleware class
   - Configuration files
   - Tests (>90% coverage)

2. **Modify Existing Components**
   - Master Orchestrator integration
   - Update orchestrators to use new renderer
   - Remove manual message appending

3. **Configuration Updates**
   - response-templates-v4.yaml (add rendering rules)
   - master-orchestrator.yaml (add middleware)
   - Individual orchestrator configs (optional cleanup)

4. **Testing**
   - Unit tests for ResponseRenderer
   - Integration tests for middleware
   - End-to-end tests for each orchestrator
   - Manual testing with user scenarios

**Deliverable:** 
- Code files (800+ lines production + 400+ lines tests)
- Updated configurations
- Test results document

---

### Phase 5: VALIDATE (10% of time)
**Goal:** Ensure fix works and doesn't break anything

**Sub-Phases:**
1. **Automated Testing**
   - Run full test suite
   - Coverage report (must be >90%)
   - Integration tests pass

2. **Manual Validation**
   - Test original issue scenario
   - Test similar issues found in Phase 2
   - Test all orchestrators

3. **Regression Testing**
   - Run existing orchestrator tests
   - Verify no breaking changes
   - Check performance impact

**Deliverable:** `validation-report-{timestamp}.md`

---

### Phase 6: DOCUMENT (10% of time)
**Goal:** Update all documentation

**Sub-Phases:**
1. **Architecture Documentation**
   - Update CORTEX.prompt.md (add investigation orchestrator)
   - Update response-templates-v4.yaml documentation
   - Create ResponseRenderer.md guide

2. **Developer Documentation**
   - Update BaseOrchestrator docs
   - Update Master Orchestrator docs
   - Create migration guide for existing orchestrators

3. **Investigation Report**
   - Complete investigation document
   - Lessons learned
   - Similar issues to watch for

**Deliverable:** 
- Updated documentation files
- `investigation-complete-{timestamp}.md` (comprehensive report)

---

## 📋 Output Documents

### Mode 1: Targeted Investigation

**Always Created:**
1. **investigation-context-{timestamp}.json** - All gathered context
2. **root-cause-analysis-{timestamp}.md** - Full analysis
3. **architecture-enhancement-proposal-{timestamp}.md** - Solution design
4. **validation-report-{timestamp}.md** - Testing results
5. **investigation-complete-{timestamp}.md** - Final summary

**Location:**
```
cortex-brain/documents/investigations/{issue-slug}/
├── architecture/
│   ├── current-state-diagram.md
│   └── proposed-state-diagram.md
├── analysis/
│   ├── investigation-context-{timestamp}.json
│   └── root-cause-analysis-{timestamp}.md
├── design/
│   ├── architecture-enhancement-proposal-{timestamp}.md
│   └── trade-off-analysis.md
├── implementation/
│   ├── code-changes-summary.md
│   └── test-results.md
├── validation/
│   └── validation-report-{timestamp}.md
└── reports/
    ├── investigation-complete-{timestamp}.md
    └── similar-issues-identified.md
```

### Mode 2: Holistic Architecture Review

**Always Created:**
1. **plan-alignment-scorecard-{timestamp}.md** (800+ lines)
2. **gap-analysis-matrix-{timestamp}.md** (1500+ lines)
3. **robustness-assessment-{timestamp}.md** (1000+ lines)
4. **implementation-roadmap-{timestamp}.md** (600+ lines)
5. **holistic-review-executive-summary-{timestamp}.md** (400+ lines)

**Location:** See `cortex-investigate-holistic-review.prompt.md` for full structure

---

## 🎯 Response Template (Mode 1: Targeted Investigation)

### Header (ALWAYS)
```markdown
## 🛡️🔍 CORTEX Investigation: [Issue Name]
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
**Investigation ID:** INVEST-{timestamp}
```

### Progress Bar (Multi-Phase)
```markdown
## 📊 Investigation Progress

████████████░░░░ 60% Complete

| Phase | Status | Duration | Output |
|-------|--------|----------|--------|
| 1. DISCOVER | ✅ Complete | 1.2h | investigation-context.json |
| 2. ANALYZE | ✅ Complete | 1.5h | root-cause-analysis.md |
| 3. DESIGN | ⏳ In Progress | 0.3h / 1h | architecture-enhancement-proposal.md |
| 4. IMPLEMENT | ⏸️ Pending | 0h / 2h | Code + Tests |
| 5. VALIDATE | ⏸️ Pending | 0h / 0.5h | validation-report.md |
| 6. DOCUMENT | ⏸️ Pending | 0h / 0.5h | Updated docs |
```

### Phase Summary (After Each Phase)
```markdown
## ✅ Phase 2 Complete: ANALYZE

### 🎯 Root Cause Identified
**PRIMARY:** Master Orchestrator lacks ResponseRenderer integration  
**SECONDARY:** No middleware pipeline for injecting system messages

### 💡 Similar Issues Found
1. Error messages from orchestrators not displaying
2. Success messages missing metadata
3. Warnings from safety validators not visible

**Impact:** 8 orchestrators affected (Planning, Vacuum, Cleanup, ADO, etc.)

### 📁 Deliverable
✅ `root-cause-analysis-20260103-143022.md` (487 lines)

---

## 📋 Next Phase: DESIGN (1 hour)

I'll design the architecture-level fix with:
- ResponseRenderer component (unified rendering)
- ResponseMiddleware (message injection)
- Master Orchestrator integration strategy
- Zero-breaking-change migration path
```

### Completion (Final Phase)
```markdown
# 🎉 INVESTIGATION COMPLETE

## ✅ Issue Fixed: Continuation Prompts Now Display

### 📊 Investigation Summary
- **Issue:** Continuation prompts generated but never displayed
- **Root Cause:** Missing ResponseRenderer integration in Master Orchestrator
- **Fix:** Architecture-level enhancement with ResponseRenderer + Middleware
- **Impact:** 8 orchestrators now properly display user messages

### 🏗️ Architecture Enhancements
1. **ResponseRenderer** - Unified response rendering (300 lines)
2. **ResponseMiddleware** - System message injection (150 lines)
3. **Master Orchestrator Integration** - Rendering pipeline (50 lines)
4. **Tests** - 95% coverage (400 lines)

### 📈 Results
- ✅ Original issue fixed (continuation prompts display)
- ✅ 3 similar issues fixed automatically
- ✅ All orchestrators now consistent
- ✅ Zero breaking changes
- ✅ 95% test coverage

### 📁 Documents Created
1. ✅ investigation-context-20260103-143022.json (1,200 lines)
2. ✅ root-cause-analysis-20260103-143022.md (487 lines)
3. ✅ architecture-enhancement-proposal-20260103-143022.md (623 lines)
4. ✅ validation-report-20260103-143022.md (245 lines)
5. ✅ investigation-complete-20260103-143022.md (THIS DOCUMENT)

### 💡 Lessons Learned
1. **Systemic Issues Need Architecture Fixes** - Band-aid fixes create more brittleness
2. **Middleware Pattern Powerful** - Enables system-wide message injection
3. **Similar Issues Often Share Root Cause** - Fix one, fix many
4. **Test Coverage Critical** - Prevents regressions

### 🔗 Related Files
- `/src/orchestrators/response_renderer.py` (NEW)
- `/src/orchestrators/response_middleware.py` (NEW)
- `/src/orchestrators/master_orchestrator.py` (MODIFIED)
- `/tests/orchestrators/test_response_renderer.py` (NEW)

---

**Investigation Duration:** 5.2 hours  
**Files Created/Modified:** 12 files (2,100+ lines)  
**Test Coverage:** 95%  
**Breaking Changes:** 0  
**Similar Issues Fixed:** 3
```

---

## 🛡️ Brain Protection (SKULL)

### INVESTIGATION_ISOLATION
- Investigation documents never commit to user repos
- Only CORTEX codebase modifications committed
- User repo analysis read-only

### ARCHITECTURE_SAFETY
- Always generate proposals before implementing
- Breaking changes require user approval
- Backward compatibility maintained

### SCOPE_CONTROL
- Investigation must stay focused on stated issue
- Related issues documented but not auto-fixed (unless approved)
- No scope creep without user consent

---

## 🔗 Master Orchestrator Integration

### Routing Entry (master-orchestrator.yaml)
```yaml
- pattern: "^(investigate|find root cause|why is|debug architecture|fix brittleness).*$"
  orchestrator: "investigation_orchestrator"
  priority: 8  # HIGH priority
  auto_trigger: false
  metadata:
    description: "Deep root cause analysis and architecture-level fixes"
    autonomous: true
    type: "diagnostic"
```

### Intent Routing (CORTEX.prompt.md)
| Command | Orchestrator | Confidence | Type | Behavior |
|---------|--------------|------------|------|----------|
| `investigate [issue]`, `find root cause`, `why is [X] breaking?`, `debug architecture [Y]`, `fix brittleness in [Z]` | 🛡️ **Investigation** | 1.00 | regex | Deep analysis → Root cause → Architecture fix → Master Orch integration |

---

## 🎓 Investigation Best Practices

### DO
- ✅ **Go Deep:** Don't stop at symptoms, find root cause
- ✅ **Think Systemically:** Is this a pattern? Are others affected?
- ✅ **Fix Architecture:** Band-aid fixes create more brittleness
- ✅ **Test Thoroughly:** 95%+ coverage, regression testing
- ✅ **Document Everything:** Investigation trail, lessons learned

### DON'T
- ❌ **Band-Aid Fixes:** Patching symptoms creates technical debt
- ❌ **Isolated Fixes:** If it's a pattern, fix system-wide
- ❌ **Assume Working:** Always validate with tests
- ❌ **Skip Documentation:** Next investigation needs context
- ❌ **Scope Creep:** Stay focused, document related issues separately

---

## 📚 Example Investigations

### Example 1: Continuation Prompt Not Displaying
**Issue:** User doesn't see token warnings  
**Symptom:** check_token_usage() creates user_message but never displays  
**Root Cause:** Master Orchestrator doesn't render OrchestratorResult.message  
**Fix:** ResponseRenderer + ResponseMiddleware architecture  
**Impact:** 8 orchestrators, 3 similar issues fixed  
**Duration:** 5.2 hours

### Example 2: Holistic Review Auto-Trigger Not Working
**Issue:** Reviews scheduled but never execute automatically  
**Symptom:** progress.json has auto_trigger=true, but reviews manual  
**Root Cause:** Master Orchestrator _check_review_schedule() not wired into handle_request()  
**Fix:** Add Step 3.5 in handle_request(), test auto-triggering  
**Impact:** 1 orchestrator, planning system  
**Duration:** 2.1 hours

### Example 3: Orchestrator Test Failures After BaseOrchestrator Update
**Issue:** 15 orchestrator tests fail after BaseOrchestrator v4.1 release  
**Symptom:** AttributeError: 'NoneType' object has no attribute 'config'  
**Root Cause:** BaseOrchestrator v4.1 requires state_db in __init__, but tests pass None  
**Fix:** Update all test fixtures to provide mock PlanningStateDB  
**Impact:** 6 orchestrators, 15 tests  
**Duration:** 1.3 hours

---

## 🚀 Quick Start

### Invoke Investigation
```
User: investigate why continuation prompts not displaying
User: find root cause of holistic review auto-trigger breaking
User: why is planning orchestrator slow?
User: debug architecture of response rendering
User: fix brittleness in token warning system
```

### Investigation Flow
1. **DISCOVER** (30% time) - Gather context, map dependencies
2. **ANALYZE** (30% time) - Find root cause, identify patterns
3. **DESIGN** (20% time) - Architecture enhancement proposal
4. **IMPLEMENT** (40% time) - Code + tests + config
5. **VALIDATE** (10% time) - Test + regression + manual
6. **DOCUMENT** (10% time) - Update docs + report

**Total Time:** Typically 4-8 hours depending on complexity

---

## 📊 Success Metrics

### Investigation Quality
- ✅ Root cause identified (not just symptoms)
- ✅ Similar issues found and documented
- ✅ Architecture-level fix (not band-aid)
- ✅ Master Orchestrator integration complete

### Fix Quality
- ✅ 95%+ test coverage
- ✅ Zero breaking changes (or migration path)
- ✅ All similar issues fixed
- ✅ Documentation updated

### Reporting Quality
- ✅ 400+ line root cause analysis
- ✅ 500+ line architecture proposal
- ✅ Comprehensive validation report
- ✅ Lessons learned documented

---

**End of Investigation Orchestrator Specification**

---

## 🔗 Related Documents
- `.github/prompts/CORTEX.prompt.md` - Master routing (add investigation entry)
- `cortex-brain/manifests/orchestrators/investigation-orchestrator.yaml` - Orchestrator manifest
- `cortex-brain/response-templates-v4.yaml` - Response formatting
- `src/orchestrators/investigation_orchestrator.py` - Implementation (when created)
