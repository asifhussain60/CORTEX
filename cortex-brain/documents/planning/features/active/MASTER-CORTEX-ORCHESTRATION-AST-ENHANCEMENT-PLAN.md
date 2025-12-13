# MASTER CORTEX Orchestration + AST Enhancement Plan

**Plan ID:** CORTEX-ORCHESTRATION-AST-v1.0  
**Created:** December 13, 2025  
**Author:** Asif Hussain  
**Status:** 🚀 READY FOR EXECUTION

---

## 📊 Master Progress Tracker

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    CORTEX ORCHESTRATION + AST ENHANCEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 0: Foundation & Intent Routing     [██████████] 100%  ✅ Complete
PHASE 1: Pre-Flight Orchestrator         [██████████] 100%  ✅ Complete
PHASE 2: Progress Synchronizer           [██████████] 100%  ✅ Complete
PHASE 3: Test Failure Analyzer           [██████████] 100%  ✅ Complete
PHASE 4: Autonomous Plan Executor        [          ]   0%  ⏳ Not Started
PHASE 5: Living Documentation Generator  [          ]   0%  ⏳ Not Started
PHASE 6: Completion Reporter             [          ]   0%  ⏳ Not Started
PHASE 7: AST-Orchestrator Integration    [          ]   0%  ⏳ Not Started
PHASE 8: REFACTOR Orchestrator           [          ]   0%  ⏳ Not Started
PHASE 9: Visual Progress & Quick Links   [          ]   0%  ⏳ Not Started
PHASE 10: Orchestration Logging          [          ]   0%  ⏳ Not Started

OVERALL PROGRESS: ████████████░░░░░░░░░░░░░░░░░░ 4/10 Phases (40%)
                  
ESTIMATED DURATION: 8-10 weeks
START DATE: December 13, 2025
TARGET COMPLETION: February 21, 2026 (Week 10)
TOTAL ELAPSED TIME: 0d 15h 0m
```

**Legend:** ⏳ Not Started | 🚧 In Progress | ✅ Complete | ⚠️ Blocked

---

## 🎯 Executive Summary

### Vision
Transform CORTEX from a template-based AI assistant into an **intelligent autonomous orchestration platform** that combines AST-powered code analysis with strategic planning execution. Achieve the PrevalidationWS migration success pattern (91% completion, 159/159 tests, zero rework) as the baseline for all future work.

### Key Objectives
1. **Intelligent Intent Routing:** LLM-based routing replacing regex (95%+ accuracy vs current ~70%)
2. **Pre-Flight Validation:** Detect environment blockers BEFORE code generation (save 2-week delays)
3. **Autonomous Execution:** Multi-phase execution without user input (4-hour migrations)
4. **AST Integration:** CORTEX Lens capabilities embedded in all orchestrators
5. **Strategic Intelligence:** Test deferral, refactor automation, living documentation
6. **Visual Excellence:** Progress bars, quick links, orchestrator engagement hints

### Success Metrics
- **Intent Routing Accuracy:** 70% → 95% (LLM-based)
- **Pre-Flight Coverage:** 0% → 100% (all plans validate environment)
- **Autonomous Phases:** 1 → 11 (full plan execution)
- **Test Rework Rate:** 50% → 5% (strategic deferral)
- **Documentation Lag:** Post-project → Real-time (living docs)
- **User Experience:** "Felt anticipatory" - CORTEX predicts needs

---

## 📋 Requirements Distillation

### Source 1: Saved Prompts Analysis

**Extracted Requirements:**

1. **Intelligent Debugger Activation** (saved-prompts.md line 1)
   - **Requirement:** Auto-trigger debugger when bugs reported
   - **Requirement:** Create specialized orchestrators based on user intent (e.g., modernizer for legacy systems)
   - **Challenge:** Balance accuracy vs efficiency with current architecture
   - **Push to 4.0:** Foundational changes requiring new architecture

2. **AST-Orchestrator Integration** (saved-prompts.md line 4)
   - **Requirement:** Incorporate CORTEX Lens AST features into orchestrators
   - **Requirement:** Complete context building using AST during analysis phase
   - **Requirement:** Centralize AST capabilities in an engine
   - **Gap:** Cross-reference orchestration vs CORTEX Lens capabilities

3. **Intent Routing Enhancement** (saved-prompts.md line 12)
   - **Requirement:** Switch from text regex to LLM for accuracy
   - **Current Problem:** Planner not detecting intent correctly (e.g., "plan to implement" incorrectly routed to PLAN instead of FEATURE)
   - **Alternative:** Explore LLM vs other ML approaches

4. **Master Plan Visual Tracker** (saved-prompts.md line 18)
   - **Requirement:** Record start/completion times accurate to minutes
   - **Requirement:** Total elapsed time counter at top (sum of phase totals)
   - **Requirement:** Real-time updates based on phase progress

5. **Planner Response Templates** (saved-prompts.md line 20)
   - **Requirement:** Visual progress bars in GitHub Copilot Chat (not terminal)
   - **Requirement:** Echo orchestrator triggers in Copilot Chat
   - **Integration:** Use response templates from `cortex-brain/response-templates.yaml`

6. **REFACTOR Orchestrator** (saved-prompts.md line 24)
   - **Requirement:** Auto-include REFACTOR phase in master plans
   - **Requirement:** Build entire context using AST
   - **Requirement:** Thorough clean code + best practices review
   - **Requirement:** Identify gaps, align, fix until no issues (max 3 iterations)
   - **Intelligence:** Mandatory for coding work, optional for simple tasks (intelligent detection)
   - **Mode:** Auto-fix (not just report)

7. **ADO Orchestrator Refactoring** (saved-prompts.md line 32)
   - **Requirement:** ADO orchestrator should leverage Planning Orchestrator
   - **Requirement:** Eliminate code duplication
   - **Pattern:** Make future orchestrators part of planning rather than repeating code

8. **Orchestration Logging** (saved-prompts.md line 35)
   - **Requirement:** Turn on logging by default (efficient mechanism)
   - **Requirement:** After every plan (final refactor cycle), review logs and fix orchestration
   - **Self-Healing:** CORTEX reviews own orchestration logs

9. **Quick Links in Progress** (saved-prompts.md line 39)
   - **Requirement:** Visual progress bar + quick links section
   - **Links:** Master plan MD file, current phase executed, next phase
   - **UX:** One-click navigation to plan artifacts

10. **Progress Tracker Positioning** (saved-prompts.md line 43)
    - **Requirement:** Add `## 📊 Master Progress Tracker` to TOP of master plan
    - **Fix:** Update all orchestrators to do this correctly moving forward

### Source 2: PrevalidationWS Migration Patterns

**Extracted Requirements:**

11. **Pre-Flight Validation Pattern** (chat01, lines 1-200)
    - **Evidence:** Detected missing .NET SDK in 15 min → saved 2-week delay
    - **Pattern:** Create validation orchestrator BEFORE Phase 1
    - **Checks:** SDKs, tools, permissions, disk space, internet connectivity
    - **Output:** Executable script (PowerShell/bash) + HealthReport
    - **Gate:** BLOCK if CRITICAL failures

12. **Incremental Progress Synchronization** (chat02, lines 200-500)
    - **Evidence:** Master plan stayed synchronized across 11 sub-plans
    - **Pattern:** Auto-update progress after EVERY phase
    - **Components:** Visual tracker (ASCII art), sub-plan next steps, phase summaries
    - **Benefit:** User always knows status (91% complete vs "in progress")

13. **Strategic Test Deferral** (chat03, lines 1-100)
    - **Evidence:** 133/136 tests passing (97.8%) → proceed to Phase 5
    - **Pattern:** Classify failures as BLOCK vs DEFER
    - **Types:** ARCHITECTURAL (block), TEST_EXPECTATION (fix test), LOGIC_BUG (defer)
    - **Result:** Zero architectural rework

14. **Autonomous Phase Progression** (chat04, lines 1-100)
    - **Evidence:** No user input for 4 hours (Phase 5 → 5A → 6)
    - **Pattern:** Multi-phase executor with gate checks
    - **Gates:** Tests passing, healthcheck, no blockers
    - **Completion:** Auto-generate PROJECT-COMPLETION-SUMMARY.md

15. **Living Documentation** (chat05, lines 1-100)
    - **Evidence:** 7 guides generated DURING execution (not after)
    - **Pattern:** Documentation orchestrator runs parallel to code generation
    - **Outputs:** Engineer guides, API consumer guides, README index
    - **Link:** Phase N: 📋 MANUAL, see guide

16. **Evidence-Based Completion** (PROJECT-COMPLETION-SUMMARY.md)
    - **Evidence:** Metrics tables, deliverables, business value
    - **Pattern:** Stakeholder-ready report (no interpretation needed)
    - **Format:** # 🎉 CONGRATULATIONS template
    - **Metrics:** Test coverage, performance, cost savings

17. **Holistic Discovery Prevention** (implicit in all chats)
    - **Evidence:** NO duplicate files, NO orphaned tests, NO namespace conflicts
    - **Pattern:** Semantic search BEFORE file creation (70% similarity threshold)
    - **Enforcement:** SKULL rule validation

### Source 3: RA Domain Analysis Insights

**Extracted Requirements:**

18. **Domain Intelligence from AST** (executive-narrative.md, lines 1-246)
    - **Evidence:** 14 functional areas detected from 1,113 operations
    - **Pattern:** Business capability mapping from code structure
    - **Capabilities:** AST extracts domain services, entities, workflows
    - **Integration:** Feed orchestrators with domain context

19. **Regulatory Compliance Detection** (executive-narrative.md, regulatory section)
    - **Evidence:** 9 P0 compliance gaps identified via code analysis
    - **Pattern:** AST validates regulatory requirements in code
    - **Examples:** IRS contribution limits, HIPAA audit trails, PCI-DSS encryption
    - **Application:** Planning System should check compliance requirements

20. **Comment Mining for Context** (executive-narrative.md, developer insights)
    - **Evidence:** 1,494 comments across 256 files reveal tribal knowledge
    - **Pattern:** AST extracts business rules, design decisions from comments
    - **Value:** "Why" explanations beyond code structure
    - **Use Case:** Feed context to planning/refactor orchestrators

21. **Workflow Discovery** (executive-narrative.md, workflows section)
    - **Evidence:** 5 mission-critical workflows reverse-engineered from code
    - **Pattern:** AST traces execution paths, identifies batch processing
    - **Examples:** Year-end carryover (50K accounts/20 min), claims processing
    - **Application:** Modernization orchestrator uses workflow maps

### Source 4: CORTEX Lens Capabilities Inventory

**Available AST Capabilities:**

22. **Analyzers** (10 language-specific)
    - Python: ast.parse(), classes, functions, imports, type hints, decorators
    - C#: Regex-based class/method/namespace extraction
    - TypeScript/JS: esprima fallback, React components, hooks
    - Java: Annotation detection, interfaces, inheritance
    - SQL: DDL/DML parsing, table relationships
    - **Gap:** No Tree-sitter integration yet (multi-language unified AST)

23. **Collectors** (10 domain-specific)
    - Health: LOC, files, languages, health score
    - Architecture: MVC, Layered, Clean, Microservices patterns
    - API Endpoints: REST, GraphQL, WebSocket detection
    - Security: OWASP Top 10 scanning, vulnerability patterns
    - Complexity: Cyclomatic, cognitive, maintainability index
    - Tech Stack: Frameworks, databases, build tools
    - Dependencies: Direct/transitive packages, version analysis
    - Test Coverage: pytest/xUnit integration
    - Comments: Documentation coverage, business rule extraction
    - **Gap:** No integration with orchestrators yet

24. **Intelligence Features**
    - Repo classification (API, Console, Library, etc.)
    - Narrative generation (executive summaries)
    - Dashboard builder (adaptive HTML/JSON)
    - Comparison engine (multi-repo analysis)
    - Export manager (markdown, JSON, PDF)
    - **Gap:** Not accessible from planning/execution orchestrators

---

## 🏗️ Architecture Enhancement Design

### Current State (CORTEX 3.8.1)

```
User Request
    ↓
Intent Router (regex-based, ~70% accuracy)
    ↓
Orchestrator (planning, tdd, maintenance, etc.)
    ↓
Response Templates (62 templates)
    ↓
GitHub Copilot Chat Output
```

**Limitations:**
- ❌ No environment validation before execution
- ❌ Manual progress tracking (user must update plans)
- ❌ Test failures always block (no strategic intelligence)
- ❌ One-phase-at-a-time execution (requires user input)
- ❌ Documentation generated after project completion
- ❌ No access to AST intelligence during planning
- ❌ Regex intent routing misses nuanced requests

### Target State (CORTEX 3.9.0 - This Plan)

```
User Request
    ↓
LLM Intent Router (95%+ accuracy) ← NEW
    ↓
Pre-Flight Orchestrator (environment validation) ← NEW
    ↓
Planning Orchestrator + AST Engine (context building) ← ENHANCED
    ↓
Autonomous Executor (multi-phase, gate-checked) ← NEW
    ├→ TDD Orchestrator + Test Failure Analyzer ← ENHANCED
    ├→ Implementation Orchestrator + AST Intelligence ← ENHANCED
    ├→ REFACTOR Orchestrator (clean code + best practices) ← NEW
    └→ Living Doc Generator (parallel execution) ← NEW
    ↓
Progress Synchronizer (auto-update all plans) ← NEW
    ↓
Completion Reporter (stakeholder summary) ← NEW
    ↓
Visual Response (progress bars, quick links) ← ENHANCED
```

**New Capabilities:**
- ✅ LLM-based intent understanding (95%+ accuracy)
- ✅ Pre-flight validation (detect blockers early)
- ✅ AST-powered context building (domain intelligence)
- ✅ Autonomous multi-phase execution (11 phases)
- ✅ Strategic test management (BLOCK vs DEFER)
- ✅ Auto-refactor orchestrator (clean code enforcement)
- ✅ Living documentation (real-time guide generation)
- ✅ Progress synchronization (all plans stay current)
- ✅ Visual excellence (progress bars, quick links, hints)
- ✅ Orchestration logging (self-healing)

---

## 📐 Phase Breakdown

### PHASE 0: Foundation & Intent Routing Enhancement
**Duration:** Week 1 (5 days)  
**Owner:** CORTEX Core Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Implement LLM-based intent router (replace regex)
2. Achieve 95%+ accuracy on 100-request test set
3. Add fallback to regex if LLM unavailable
4. Integrate with existing routing infrastructure

**Deliverables:**
- `src/cortex_agents/llm_intent_router.py` (400 lines)
- Intent classification test suite (100 requests)
- Performance benchmarks (< 500ms routing time)
- Migration guide for regex → LLM

**Acceptance Criteria:**
- [ ] 95%+ accuracy on test set
- [ ] < 500ms average routing time
- [ ] Graceful fallback to regex
- [ ] No breaking changes to existing orchestrators
- [ ] Documentation updated

**Dependencies:** None

**Sub-Plan:** `phase-0-intent-routing-enhancement.md`

---

### PHASE 1: Pre-Flight Orchestrator
**Duration:** Week 1-2 (5 days)  
**Owner:** Planning System Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Create pre-flight validation orchestrator
2. Detect environment requirements from domain patterns
3. Generate executable validation scripts
4. BLOCK execution if CRITICAL failures

**Deliverables:**
- `src/orchestrators/planning/pre_flight_orchestrator.py` (400 lines)
- Validation script templates (PowerShell, bash)
- HealthReport data model
- Integration with Planning System 2.0

**Acceptance Criteria:**
- [ ] Detects 12+ environment checks (SDK, tools, permissions, disk, network)
- [ ] Pattern-specific checks (FastAPI → Python 3.8+, JWT → SSL certs)
- [ ] Generates executable scripts
- [ ] BLOCKS on CRITICAL, WARNS on optional
- [ ] < 15 seconds execution time

**Dependencies:** Phase 0 (intent routing)

**Sub-Plan:** `phase-1-pre-flight-orchestrator.md`

---

### PHASE 2: Progress Synchronizer Utility
**Duration:** Week 2 (3 days)  
**Owner:** Orchestration Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Auto-update master plans after phase completion
2. Synchronize visual progress trackers
3. Update sub-plan next steps
4. Generate phase completion summaries

**Deliverables:**
- `src/utils/progress_synchronizer.py` (300 lines)
- ASCII progress bar generator
- Phase completion template
- Integration with BaseOrchestrator

**Acceptance Criteria:**
- [ ] Updates master plan markdown (Phase N: ✅ Complete)
- [ ] Recalculates progress percentages
- [ ] Updates visual tracker (ASCII art)
- [ ] Generates phase summary with metrics
- [ ] < 1 second update time

**Dependencies:** None (standalone utility)

**Sub-Plan:** `phase-2-progress-synchronizer.md`

---

### PHASE 3: Test Failure Analyzer
**Duration:** Week 2-3 (5 days)  
**Owner:** TDD Mastery Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Classify test failures (ARCHITECTURAL, TEST_EXPECTATION, LOGIC_BUG)
2. Generate mitigation strategies per type
3. Enable strategic deferral (BLOCK vs DEFER)
4. Track deferred failures (must resolve before 100%)

**Deliverables:**
- `src/orchestrators/tdd/test_failure_analyzer.py` (350 lines)
- Failure classification model
- Mitigation strategy generator
- Deferred failure tracker

**Acceptance Criteria:**
- [ ] Classifies failures with 90%+ accuracy
- [ ] Generates actionable mitigation strategies
- [ ] Allows DEFER for non-architectural issues
- [ ] Tracks deferred count (must be 0 at completion)
- [ ] Integration with TDD Orchestrator

**Dependencies:** None (enhances existing TDD)

**Sub-Plan:** `phase-3-test-failure-analyzer.md`

---

### PHASE 4: Autonomous Plan Executor
**Duration:** Week 3-4 (7 days)  
**Owner:** Planning System Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Multi-phase execution without user input
2. Gate checks (pre-flight, tests, healthcheck, blockers)
3. Auto-advance to next phase if gates pass
4. Generate completion report at 100%

**Deliverables:**
- `src/orchestrators/planning/autonomous_executor.py` (500 lines)
- Gate check framework
- Phase transition logic
- Completion report generator

**Acceptance Criteria:**
- [ ] Executes 5+ phases autonomously
- [ ] All gate checks pass before advancement
- [ ] Generates blocker report if any gate fails
- [ ] Completion report uses success template
- [ ] User can interrupt/override at any phase

**Dependencies:** Phase 1 (pre-flight), Phase 2 (progress sync), Phase 3 (test analyzer)

**Sub-Plan:** `phase-4-autonomous-executor.md`

---

### PHASE 5: Living Documentation Generator
**Duration:** Week 4-5 (5 days)  
**Owner:** Documentation Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Generate engineer guides DURING execution (not after)
2. Capture architecture decisions in real-time
3. Create API consumer guides (migration, quick-start)
4. Generate README index of all guides

**Deliverables:**
- `src/orchestrators/documentation/living_doc_generator.py` (400 lines)
- Engineer guide templates
- API consumer guide templates
- README index generator

**Acceptance Criteria:**
- [ ] Generates guides during phase execution (parallel)
- [ ] Links guides in master plan (Phase N: 📋 MANUAL, see guide)
- [ ] Captures architecture decisions with timestamp
- [ ] Creates README.md index
- [ ] No execution slowdown (async generation)

**Dependencies:** Phase 2 (progress sync for linking)

**Sub-Plan:** `phase-5-living-documentation.md`

---

### PHASE 6: Completion Reporter
**Duration:** Week 5 (3 days)  
**Owner:** Orchestration Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Generate PROJECT-COMPLETION-SUMMARY.md at 100%
2. Include metrics tables (test coverage, performance)
3. Calculate business value (cost savings, velocity)
4. Use success template format (# 🎉 CONGRATULATIONS)

**Deliverables:**
- `src/orchestrators/planning/completion_reporter.py` (450 lines)
- Metrics aggregation logic
- Business value calculator
- Success template renderer

**Acceptance Criteria:**
- [ ] Auto-generates at 100% completion
- [ ] Includes test metrics (unit, integration, contract)
- [ ] Calculates performance improvements
- [ ] Estimates cost savings
- [ ] Uses H1 success template

**Dependencies:** Phase 2 (progress tracker for metrics)

**Sub-Plan:** `phase-6-completion-reporter.md`

---

### PHASE 7: AST-Orchestrator Integration
**Duration:** Week 5-7 (10 days)  
**Owner:** CORTEX Lens + Orchestration Teams  
**Status:** ⏳ Not Started

**Objectives:**
1. Create AST Engine accessible from all orchestrators
2. Integrate 10 collectors into planning phase
3. Use domain intelligence for context building
4. Enable pattern detection during pre-planning

**Deliverables:**
- `src/orchestrators/ast_engine.py` (600 lines)
- Orchestrator-Lens integration layer
- Domain pattern detector
- Planning phase AST analysis

**Acceptance Criteria:**
- [ ] All orchestrators can access AST capabilities
- [ ] Planning phase includes AST analysis (< 30 seconds)
- [ ] Domain patterns feed context to plans
- [ ] Architecture patterns detected (MVC, Clean, etc.)
- [ ] Security/compliance patterns flagged

**Dependencies:** CORTEX Lens v1.0 complete

**Sub-Plan:** `phase-7-ast-orchestrator-integration.md`

---

### PHASE 8: REFACTOR Orchestrator
**Duration:** Week 7-8 (7 days)  
**Owner:** Code Quality Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Auto-include REFACTOR phase in plans (intelligent detection)
2. Build context using AST
3. Run clean code + best practices review
4. Identify gaps, align, auto-fix (max 3 iterations)

**Deliverables:**
- `src/orchestrators/refactor_orchestrator.py` (500 lines)
- Clean code analyzer (uses AST)
- Best practices validator
- Auto-fix engine

**Acceptance Criteria:**
- [ ] Intelligent detection (mandatory for code, optional for simple tasks)
- [ ] Max 3 iterations (no infinite loops)
- [ ] Auto-fix mode (not just report)
- [ ] Integrates with Planning System 3.0
- [ ] Reviews orchestration logs and self-heals

**Dependencies:** Phase 7 (AST integration)

**Sub-Plan:** `phase-8-refactor-orchestrator.md`

---

### PHASE 9: Visual Progress & Quick Links
**Duration:** Week 8-9 (5 days)  
**Owner:** UX Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Visual progress bars in Copilot Chat (not terminal)
2. Quick links (master plan, current phase, next phase)
3. Orchestrator engagement hints (🎭 pattern)
4. Progress tracker at TOP of master plans

**Deliverables:**
- Progress bar renderer for Copilot Chat
- Quick links template
- Orchestrator hint system
- Master plan formatter

**Acceptance Criteria:**
- [ ] Progress bars render in Copilot Chat
- [ ] Quick links include MD file paths
- [ ] Orchestrators echo engagement hints
- [ ] Progress tracker always at top of master plan
- [ ] Visual updates in real-time

**Dependencies:** Phase 2 (progress sync)

**Sub-Plan:** `phase-9-visual-progress-quick-links.md`

---

### PHASE 10: Orchestration Logging & Self-Healing
**Duration:** Week 9-10 (5 days)  
**Owner:** Observability Team  
**Status:** ⏳ Not Started

**Objectives:**
1. Enable orchestration logging by default (efficient)
2. Review logs after every plan (final refactor cycle)
3. Auto-fix orchestration issues
4. Generate orchestration health report

**Deliverables:**
- `src/utils/orchestration_logger.py` (300 lines)
- Log review analyzer
- Self-healing engine
- Orchestration health report

**Acceptance Criteria:**
- [ ] Logging enabled by default (< 5% overhead)
- [ ] Logs reviewed at end of every plan
- [ ] Auto-fixes detected orchestration issues
- [ ] Generates health report (pass/fail per orchestrator)
- [ ] Alerts on critical orchestration failures

**Dependencies:** Phase 8 (REFACTOR orchestrator for self-healing)

**Sub-Plan:** `phase-10-orchestration-logging.md`

---

## 📊 Integration Points

### 1. Planning System 3.0 Integration
**Phases Affected:** 1, 4, 7, 8, 9

**Changes:**
- Pre-flight runs BEFORE Phase 1
- AST analysis runs during Phase 0 (pre-planning)
- REFACTOR phase auto-added intelligently
- Progress tracker updates after each phase
- Quick links embedded in response templates

**Manifest Updates:**
- `cortex-brain/orchestrator-manifests/planning-system-3.0-manifest.yaml`
- Add pre_flight_required: true
- Add ast_analysis_required: true
- Add refactor_phase: "intelligent" (vs "always"/"never")

### 2. ADO Operations Integration
**Phases Affected:** 4, 5, 8

**Changes:**
- ADO leverages Planning Orchestrator (no duplication)
- Living docs generate ADO-specific guides
- REFACTOR checks ADO work item formatting

**Manifest Updates:**
- `cortex-brain/orchestrator-manifests/ado-planning-manifest.yaml`
- Inherit from planning-system-3.0-manifest.yaml
- Add ado_formatting: true
- Add work_item_templates: [story, feature, task]

### 3. TDD Mastery Integration
**Phases Affected:** 3, 8

**Changes:**
- Test Failure Analyzer integrated into TDD workflow
- REFACTOR runs after GREEN phase
- Strategic deferral enabled

**Manifest Updates:**
- `cortex-brain/brain-protection-rules.yaml`
- Update TDD_ENFORCEMENT: allow strategic deferral
- Add TEST_FAILURE_CLASSIFICATION rule
- Add REFACTOR_AFTER_GREEN rule

### 4. System Maintenance Integration
**Phases Affected:** 2, 8, 10

**Changes:**
- Progress sync updates maintenance status
- REFACTOR reviews maintenance orchestration
- Logging captures maintenance metrics

**Manifest Updates:**
- `src/operations/modules/orchestration/system_maintenance_orchestrator.py`
- Add progress sync calls
- Add orchestration log review
- Add self-healing check

---

## 🎯 Success Criteria (Overall)

### Quantitative Metrics

| Metric | Current | Target | Measurement Method |
|--------|---------|--------|-------------------|
| Intent Routing Accuracy | 70% | 95% | Test set (100 requests) |
| Pre-Flight Coverage | 0% | 100% | % of plans with pre-flight |
| Autonomous Phases | 1 | 11 | Max consecutive phases |
| Test Rework Rate | 50% | 5% | % tests requiring rework |
| Documentation Lag | Post-project | Real-time | Time between code→doc |
| Blocker Detection Time | 2 weeks | 15 min | Time to detect BLOCKER-001 |
| Plan Sync Accuracy | Manual | 100% | % plans auto-synced |
| Completion Report Gen | Manual | Automatic | % plans with auto-report |

### Qualitative Metrics

- ✅ User reports: "CORTEX felt anticipatory"
- ✅ Stakeholders understand reports without interpretation
- ✅ Engineers execute manual phases without Copilot
- ✅ Zero blocker surprises after Week 1
- ✅ Visual progress enhances UX (not clutters)

### Project Completion Criteria

- [ ] All 10 phases complete (100%)
- [ ] 250+ tests passing (all new components)
- [ ] Documentation complete (10 sub-plans)
- [ ] Performance benchmarks met (< 30s AST analysis)
- [ ] Integration tests pass (end-to-end workflows)
- [ ] User acceptance testing complete
- [ ] Production deployment plan ready

---

## 🚨 Risks & Mitigation

### Risk 1: LLM Intent Routing Cost
**Probability:** Medium | **Impact:** Medium  
**Description:** LLM API calls may be expensive at scale  
**Mitigation:**
- Use GPT-3.5-turbo (lower cost) vs GPT-4
- Cache frequent intent patterns (70% hit rate)
- Fallback to regex if budget exceeded
- Monitor cost per request (< $0.001 target)

### Risk 2: AST Analysis Performance
**Probability:** Medium | **Impact:** High  
**Description:** AST parsing may slow down planning phase  
**Mitigation:**
- Targeted file scanning (entry points, base classes)
- Skip test files, migrations, generated code
- Parallel parsing (4 workers)
- Cache AST trees (file hash-based)
- Performance target: < 30 seconds for 500-file repo

### Risk 3: Breaking Changes to Existing Orchestrators
**Probability:** Low | **Impact:** High  
**Description:** Integration may break existing workflows  
**Mitigation:**
- Feature flags for new capabilities (gradual rollout)
- Comprehensive regression testing (250+ tests)
- Backward compatibility for 3.8.1 APIs
- Rollback plan (git revert + feature flag off)

### Risk 4: User Confusion with Autonomous Execution
**Probability:** Medium | **Impact:** Medium  
**Description:** Users may not understand when to intervene  
**Mitigation:**
- Clear engagement hints (🎭 pattern)
- Interrupt mechanism (user can stop any phase)
- Progress visibility (quick links, visual bars)
- Documentation (when to use autonomous vs manual)

### Risk 5: Orchestration Log Overhead
**Probability:** Low | **Impact:** Medium  
**Description:** Logging may slow down execution  
**Mitigation:**
- Async logging (non-blocking)
- Sampling (log 10% of operations at INFO)
- Target: < 5% performance overhead
- Disable in production if needed (feature flag)

---

## 📚 References

### Source Documents
1. `saved-prompts.md` - User requirements (10 directives)
2. `.github/copilot/copilot-chats/chat01-05.md` - PrevalidationWS patterns (7 patterns)
3. `.github/copilot/RA-Domain-Analysis/executive-narrative.md` - AST insights (246 lines)
4. `CORTEX-ORCHESTRATION-ENHANCEMENTS-FROM-REAL-WORLD-USAGE.md` - Analysis document
5. `cortex-brain/orchestrator-manifests/planning-system-2.0-manifest.yaml` - Current manifest
6. `cortex-brain/brain-protection-rules.yaml` - SKULL rules
7. `src/cortex_lens/` - AST capabilities (10 analyzers, 10 collectors)

### Related Plans
- `copilot-ast-enhancement/MASTER-PLAN.md` - Original AST plan (v1.0)
- `cortex-brain/documents/planning/prevalidation-ws-migration-lessons-learned-plan.md` - 38 lessons
- `cortex-sample-apps/PrevalidationWS/plan/MODERNIZATION-PLAN.md` - 11-phase execution

### Implementation Guides
- Will be created during Phase 5 (Living Documentation)
- Engineer guides for each phase
- API documentation for new components
- Migration guide from 3.8.1 → 3.9.0

---

## 🔍 Next Steps

1. **Review & Approve Plan** - Stakeholder sign-off on 10-phase approach
2. **Create Sub-Plans** - Detailed plans for each phase (10 documents)
3. **Setup Project Structure** - Create phase directories, test scaffolds
4. **Phase 0 Kickoff** - Start LLM intent routing implementation
5. **Weekly Checkpoints** - Review progress, adjust timeline as needed

---

**Plan Status:** 🚀 READY FOR EXECUTION  
**Estimated Duration:** 8-10 weeks  
**Total LOC to Create:** ~4,000 lines (new components)  
**Total LOC to Modify:** ~1,500 lines (integrations)  
**Total Tests to Create:** 250+ tests

**Author:** Asif Hussain  
**Created:** December 13, 2025  
**Last Updated:** December 13, 2025
