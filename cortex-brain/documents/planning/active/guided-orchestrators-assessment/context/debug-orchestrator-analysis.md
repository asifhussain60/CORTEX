# Debug Orchestrator Evaluation

**Orchestrator Name:** Debug Orchestrator  
**Current Type:** 📋 GUIDED  
**Evaluator:** Asif Hussain (CORTEX AI)  
**Evaluation Date:** January 3, 2026

---

## 🔍 Current Implementation Analysis

### 1. Location & Structure

**Manifest File:** `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml`  
**Prompt File(s):** [Not found - appears to be manifest-only]  
**Supporting Files:** None currently (planned implementation)

**Current Status:** Planned for implementation (Version 2.0.0)

### 2. Current Workflow Description

**Phase Structure:**
```
Phase 0: Bug Report Intake - Parse bug description, extract error details
Phase 1: Review Integration - Contextual architectural review scoped to bug
Phase 2: Debug Injection - Template-based debug code at strategic locations
Phase 3: Log Analysis - Analyze debug logs + stack traces
Phase 4: Root Cause Hypothesis - Generate ranked hypotheses
Phase 5: Fix Application - Apply fix (user-guided or autonomous)
Phase 6: Fix Verification - Run tests to verify fix
Phase 7: Marker Cleanup - Remove all debug markers (one-shot)
Phase 8: Pattern Learning - Store successful strategies to Tier 2
```

**Total Phases:** 9 (complex multi-phase workflow)  
**Linear vs Branching:** Conditional (verification loop: fix → test → re-debug on failure)

### 3. Current Capabilities

**Primary Functions:**
- Parse natural language bug reports
- Inject debug markers (logging, state capture, event tracing)
- Run contextual architectural reviews
- Analyze debug logs + stack traces
- Generate root cause hypotheses
- Verify fixes via automated testing
- One-shot marker cleanup
- Pattern learning to Tier 2

**Key Operations:**
- **AST Manipulation:** Inject debug code at function boundaries
- **Template-Based Code Generation:** Generate logging, event listeners
- **Multi-file Analysis:** Scan workspace for bug-related files
- **Test Execution:** Run tests via TestExecutionManager
- **Git Operations:** Create checkpoints at debug milestones
- **State Tracking:** Track marker locations, fix attempts, session progress

### 4. Integration Points

**Dependencies:**
- Master Orchestrator: ⏸️ Not yet configured (planned)
- BaseOrchestrator: ⏸️ N/A (GUIDED, not yet implemented)
- PlanningStateDB: ⏸️ Not integrated (planned for session persistence)
- Other Orchestrators:
  - **TDD Workflow:** Bidirectional (TDD triggers debug on failures)
  - **Review Orchestrator:** One-way (debug triggers contextual reviews)
  - **Git Checkpoint:** One-way (debug creates checkpoints)
  - **Knowledge Graph:** Bidirectional (query patterns, store learnings)

**Tool Calls Used:**
- File read/write (marker injection/cleanup)
- AST parsing (locate injection points)
- Test execution (verify fixes)
- Git operations (checkpoints)
- Review orchestrator invocation

---

## 📊 Decision Matrix Scoring

### Criterion 1: Operation Complexity (Weight: 30%)

**Assessment:**
- **AST manipulation:** ✅ YES
  - Inject debug code at function entry/exit
  - Parse code structure to find strategic injection points
  - Generate context-aware logging statements
  
- **Multi-phase workflow:** ✅ YES - **9 phases** with conditional branching
  - Linear progression: Intake → Review → Inject → Analyze → Fix
  - Conditional loop: Fix → Verify → (pass: cleanup, fail: re-inject)
  
- **Complex algorithms:** ✅ YES
  - Root cause hypothesis generation (correlate logs, stack traces, review findings)
  - Template-based code generation (Python logging, JavaScript console.log)
  - Event tracing pattern detection
  - One-shot marker cleanup (scan entire workspace)
  
- **Multi-file analysis:** ✅ YES
  - Search workspace for bug-related files
  - Correlate stack traces across modules
  - Inject markers in multiple files simultaneously

**Raw Score:** **10/10** (Very High Complexity)

**Rationale:**
- AST manipulation (+3): Complex Python `ast` module operations
- Multi-phase workflow (+2): 9 phases with conditional loops
- Complex algorithms (+2): Root cause analysis, template generation
- Multi-file analysis (+2): Workspace-wide bug correlation
- **Total:** 9 operational complexity indicators

**Weighted Score:** 10 × 0.30 = **3.00**

---

### Criterion 2: State Management (Weight: 25%)

**Assessment:**
- **Requires rollback:** ✅ YES - **CRITICAL**
  - Bad marker injection → Revert to pre-injection checkpoint
  - Fix breaks more tests → Rollback to pre-fix state
  - Cleanup failure → Rollback to known good state
  
- **Multi-phase state:** ✅ YES - **9 phases** with persistence
  - Track marker injection locations (for cleanup)
  - Store debug logs generated
  - Record fix attempts (for loop detection)
  - Persist session for resumption
  
- **Progress persistence:** ✅ YES
  - Tier 1 Working Memory integration planned
  - Session resumption across chat sessions
  - Debug history for pattern learning
  
- **Transaction boundaries:** ✅ YES
  - Atomic marker injection (all-or-nothing)
  - Atomic marker cleanup (zero markers guaranteed)
  - Atomic fix application (checkpoint before/after)

**Raw Score:** **10/10** (Critical State Management)

**Rationale:**
- Requires rollback (+4): Multiple failure points requiring atomic revert
- Multi-phase state (+3): 9 phases with complex state tracking
- Progress persistence (+2): Tier 1 integration, session resumption
- Transaction boundaries (+1): Multiple atomic operations required
- **Total:** All state management indicators present

**Weighted Score:** 10 × 0.25 = **2.50**

---

### Criterion 3: User Interaction (Weight: 20%)

**Assessment:**
- **Automation level:** Minimal Interaction (1-2 approval gates)
  - Approval gate 1: Fix proposal (user can modify before applying)
  - Approval gate 2: Marker cleanup (confirm before removal)
  - Otherwise autonomous execution
  
- **Approval gates:** 2 gates
  - Fix application approval (safety gate)
  - Cleanup confirmation (prevent accidental marker removal)
  
- **Conversational elements:** ⏸️ NO
  - Not exploratory or iterative
  - Deterministic workflow: inject → analyze → fix → verify → cleanup
  
- **Iterative refinement:** ⏸️ LIMITED
  - Verification loop is automatic (not user-driven)
  - User only approves fix strategy, doesn't refine

**Raw Score:** **8/10** (Minimal Interaction)

**Rationale:**
- Mostly automated workflow
- 2 strategic approval gates (not blocking autonomous execution)
- Not conversational or exploratory
- Fits autonomous model with approval hooks

**Weighted Score:** 8 × 0.20 = **1.60**

---

### Criterion 4: Maintenance Cost (Weight: 15%)

**Assessment:**
- **Logic complexity:** ✅ Complex
  - AST parsing and code injection logic
  - Template rendering engine
  - Root cause hypothesis generation (ML-adjacent)
  - One-shot marker cleanup algorithm
  - Event correlation across logs
  
- **Update frequency:** ✅ Regularly expected
  - New debug templates as patterns emerge
  - Enhanced root cause algorithms
  - Additional marker types (browser DevTools, etc.)
  - Integration with new test frameworks
  
- **Debug difficulty:** ✅ Hard with manifests
  - Current GUIDED approach requires testing via full orchestrator execution
  - Python implementation allows unit tests for each component
  - IDE support for debugging AST logic
  
- **Test coverage:** ⏸️ None currently (planned implementation)
  - AUTONOMOUS enables 100% test coverage requirement
  - Critical for complex AST operations

**Raw Score:** **10/10** (High Maintenance Benefits from Python)

**Rationale:**
- Complex logic benefits from IDE support, debugging, unit tests
- Regular updates expected (new patterns, templates)
- Python significantly easier to maintain than YAML manifests for complex logic
- Test coverage critical for reliability

**Weighted Score:** 10 × 0.15 = **1.50**

---

### Criterion 5: Code Reusability (Weight: 10%)

**Assessment:**
- **Shared utilities:** ✅ High reuse potential
  - **AST Parser:** Reusable by Vacuum (orphan detection), Planning v5 (code analysis)
  - **Template Injector:** Reusable by Sanitization (code transformation), Refinement (code generation)
  - **Marker Manager:** Reusable pattern for temporary code insertion
  - **Test Execution Manager:** Already shared with TDD Orchestrator
  
- **Used by other orchestrators:** ✅ Potential for 3+
  - TDD Workflow: Test execution utilities
  - Vacuum: AST parsing for orphan detection
  - Sanitization: Code transformation patterns
  - Planning v5: Code analysis capabilities
  
- **Potential for reuse:** ✅ Very High
  - Debug marker pattern applicable to any temporary code injection
  - Template-based code generation framework
  - Root cause analysis could be library
  
- **Unique vs generic logic:** ~30% unique (bug-specific), 70% reusable (AST, templates, execution)

**Raw Score:** **9/10** (High Reusability)

**Rationale:**
- AST parsing library benefits multiple orchestrators
- Template injection pattern is generic
- Test execution already shared
- Marker management pattern reusable

**Weighted Score:** 9 × 0.10 = **0.90**

---

## 🎯 Final Score & Recommendation

| Criterion | Weight | Raw Score | Weighted Score |
|-----------|--------|-----------|----------------|
| Operation Complexity | 30% | 10/10 | 3.00 |
| State Management | 25% | 10/10 | 2.50 |
| User Interaction | 20% | 8/10 | 1.60 |
| Maintenance Cost | 15% | 10/10 | 1.50 |
| Code Reusability | 10% | 9/10 | 0.90 |
| **TOTAL** | **100%** | **47/50** | **9.50/10** |

---

### Recommendation: ✅ **AUTONOMOUS** (STRONG)

**Confidence Level:** ✅ **HIGH**

**Primary Rationale:**
Debug Orchestrator scores **9.50/10** - the highest complexity score of all assessed orchestrators. The combination of AST manipulation, multi-phase state management with rollback, complex algorithm requirements, and high reusability potential make this an ideal candidate for AUTONOMOUS conversion. The planned implementation already anticipates BaseOrchestrator v4.1 integration and autonomous execution patterns.

**Key Decision Factors:**
1. **AST Complexity (10/10):** Debug marker injection requires sophisticated AST parsing and code generation - Python's `ast` module provides first-class support
2. **Critical State Management (10/10):** Rollback capabilities for bad injections, fix failures, and cleanup errors require transactional database state
3. **High Reusability (9/10):** AST parsing, template injection, and marker management utilities benefit multiple orchestrators

**Strategic Alignment:**
- Planned manifest already follows BaseOrchestrator v4.1 patterns (DoR/DoD, quality gates, autonomous execution)
- Integration points with TDD, Review, Git Checkpoint orchestrators favor AUTONOMOUS coordination
- Master Orchestrator routing enables deterministic debug workflow invocation

---

## 🏗️ Migration Roadmap

### Effort Estimate

**Total Duration:** 3 days

**Phase Breakdown:**
- **Day 1:** Core DebugOrchestratorV2 + AST Engine (8 hours)
  - BaseOrchestrator v4.1 scaffolding
  - AST parser for injection point detection
  - Template-based code generator
  - Marker manager (track injection locations)
  
- **Day 2:** Debug Workflow Automation (8 hours)
  - Bug report parser (natural language + test failures)
  - Review Orchestrator integration
  - Root cause hypothesis generator
  - Fix verification loop
  - One-shot marker cleanup
  
- **Day 3:** Testing + Master Orchestrator Integration (8 hours)
  - 100% test coverage (unit + integration)
  - Master Orchestrator routing configuration
  - Response template integration
  - Documentation

### Implementation Strategy

**New Files to Create:**
```
src/orchestrators/debug/
├── debug_orchestrator_v2.py          # Main orchestrator (BaseOrchestrator v4.1)
├── ast_engine.py                     # AST parsing + injection point detection
├── template_injector.py              # Code generation from templates
├── marker_manager.py                 # Track + cleanup debug markers
├── root_cause_analyzer.py            # Hypothesis generation
├── bug_report_parser.py              # Parse natural language + test output
└── __init__.py

cortex-brain/manifests/orchestrators/
└── debug-orchestrator-v2.yaml        # Configuration manifest (AUTONOMOUS)

cortex-brain/templates/debug/
├── python_function_logging.jinja2    # Python debug template
├── javascript_console_log.jinja2     # Browser debug template
├── event_tracer.jinja2               # Event listener template
├── bug_report_received.jinja2        # Response template
├── debug_progress.jinja2             # Response template
├── fix_proposal.jinja2               # Response template
└── debug_complete.jinja2             # Response template

tests/orchestrators/debug/
├── test_debug_orchestrator_v2.py     # Main orchestrator tests
├── test_ast_engine.py                # AST parsing tests
├── test_template_injector.py         # Code generation tests
├── test_marker_manager.py            # Marker management tests
├── test_root_cause_analyzer.py       # Hypothesis generation tests
└── test_bug_report_parser.py         # Parser tests
```

### Key Components

1. **Core Orchestrator:** DebugOrchestratorV2
   - 9-phase workflow state machine
   - Verification loop (fix → test → re-debug on failure)
   - Integration with TDD, Review, Git Checkpoint orchestrators
   - DoR/DoD quality gates
   - Autonomous execution with 2 approval gates

2. **AST Engine:**
   - Parse Python/JavaScript code
   - Identify injection points (function entry/exit, exception boundaries)
   - Validate injection safety (syntax preservation)
   - Reusable by Vacuum, Planning v5, Sanitization

3. **Template Injector:**
   - Jinja2-based code generation
   - Context-aware logging statements
   - Browser console.log generation
   - Event listener injection
   - Reusable pattern for code transformation

4. **Marker Manager:**
   - Track all injected markers (file, line, marker ID)
   - One-shot cleanup (scan workspace, remove all CORTEX_DEBUG_ markers)
   - Verification (zero markers remaining)
   - Rollback support (restore pre-injection state)

5. **Root Cause Analyzer:**
   - Correlate debug logs, stack traces, review findings
   - Pattern matching against Tier 2 knowledge
   - Confidence scoring for hypotheses
   - Ranking (present top 3 likely causes)

6. **State Management:**
   - PlanningStateDB integration for session persistence
   - Track: marker locations, debug logs, fix attempts, verification results
   - Transaction boundaries: marker injection, fix application, cleanup
   - Rollback capability at each checkpoint

### Master Orchestrator Integration

**Routing Pattern:**
```yaml
- pattern: "^(debug|fix bug|debug (this|the) (bug|issue|error)).*$"
  orchestrator: debug_orchestrator_v2
  confidence: 1.0
  match_type: regex
  priority: 30
  metadata:
    description: "Debug Mastery v2 (Marker Injection + Root Cause Analysis)"
    autonomous: true
    lifecycle_hooks:
      - pre_execution: validate_bug_report
      - post_execution: cleanup_markers
    dependencies:
      - tdd_workflow_orchestrator  # For test execution
      - review_orchestrator         # For contextual reviews
      - git_checkpoint_orchestrator # For rollback
```

**Integration Points:**
- **Pattern Matching:** Regex captures common debug commands
- **Lifecycle Hooks:** Pre-execution bug report validation, post-execution marker cleanup
- **Dependencies:** Explicit orchestrator dependencies for proper coordination
- **Priority:** 30 (medium-high, after TDD but before generic planning)

### Testing Strategy

**Test Coverage Requirements:**
- Unit tests: **100% coverage** (all components)
- Integration tests: **8 scenarios**
  1. Bug report parsing (natural language)
  2. Bug report parsing (test failure output)
  3. Marker injection + AST validation
  4. Root cause hypothesis generation
  5. Fix verification loop (success path)
  6. Fix verification loop (failure path with re-debug)
  7. One-shot marker cleanup
  8. End-to-end: bug report → inject → analyze → fix → verify → cleanup
  
- End-to-end tests: **3 workflows**
  1. Simple bug fix (linear path)
  2. Complex bug (multiple re-debug iterations)
  3. Verification loop abort (user gives up)

**Critical Test Cases:**
1. **AST Injection Safety:** Ensure injected code doesn't break syntax
2. **Marker Cleanup Completeness:** Verify zero markers remain (scan entire workspace)
3. **Rollback Integrity:** Bad injection → rollback → code unchanged
4. **Verification Loop Termination:** Prevent infinite re-debug loops
5. **Concurrent Debug Sessions:** Multiple bugs debugged simultaneously (state isolation)
6. **Review Integration:** Contextual review triggered with correct scope
7. **Pattern Learning:** Successful fix → pattern stored to Tier 2
8. **Template Rendering:** All response templates render correctly

### SKULL Enforcement

**Applicable Rules:**
- `TDD_ENFORCEMENT`: Debug workflow follows RED→GREEN→REFACTOR
  - Application: Verify bug reproduces (RED), fix applied (GREEN), markers cleaned + checkpoint (REFACTOR)
  
- `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT`: Search before injecting
  - Application: AST scan discovers existing debug markers before injection (prevent duplication)
  
- `GIT_CHECKPOINT_ENFORCEMENT`: Checkpoint at debug milestones
  - Application: Checkpoint before injection, after fix, after cleanup
  
- `REFACTOR_CODE_CLEANUP_ENFORCEMENT`: Remove all temporary code
  - Application: One-shot marker cleanup with verification (zero markers remaining)
  
- `PROGRESS_TRACKER_ENFORCEMENT`: Visual progress tracking
  - Application: Response templates show phase progression (Phase 1/9, Phase 2/9, etc.)
  
- `OPERATIONAL_READINESS_ENFORCEMENT`: DoR/DoD checklists
  - Application: Bug reproducibility check (DoR), tests passing + zero markers (DoD)

---

## 📊 Risk Assessment

### Risks of Converting to AUTONOMOUS

**Technical Risks:**
- **Risk 1:** AST parsing failures on edge cases (malformed code)
  - **Mitigation:** Comprehensive test suite covering edge cases, fallback to manual injection
  
- **Risk 2:** Marker cleanup misses markers (false negatives)
  - **Mitigation:** Multiple cleanup strategies (AST scan + regex scan + grep), verification step
  
- **Risk 3:** Root cause analyzer generates low-confidence hypotheses
  - **Mitigation:** Confidence thresholds, present top 3 hypotheses (not just one), user override

**Resource Risks:**
- Development time: 3 days investment (24 hours engineering time)
- Testing complexity: Requires workspace fixtures with intentional bugs
- **Mitigation:** Phased implementation (core Day 1, features Day 2, testing Day 3)

**Maintenance Risks:**
- **Risk 1:** AST library updates break injection logic
  - **Mitigation:** Pin library versions, comprehensive regression tests

### Risks of Remaining GUIDED

**Technical Risks:**
- **Risk 1:** Manifest-based approach cannot express complex AST logic
  - **Impact:** Manual marker injection, error-prone cleanup, no rollback
  
- **Risk 2:** No state persistence for multi-phase workflow
  - **Impact:** Cannot resume debug sessions, fix attempts lost
  
- **Risk 3:** Difficult to test complex logic in manifests
  - **Impact:** Reliability issues, hard-to-debug failures

**Operational Risks:**
- **Risk 1:** Low code reusability (AST logic not shared with other orchestrators)
  - **Impact:** Duplicate implementation in Vacuum, Planning v5

**Verdict:** Risks of remaining GUIDED **outweigh** risks of converting to AUTONOMOUS.

---

## 📝 Additional Notes

### Alignment with Existing Manifest

The current `debug-orchestrator-manifest.yaml` (v2.0.0, status: planned) **already anticipates autonomous implementation**:

- **REQ-DBG-016:** "Autonomous Debug Workflow" - matches Planning Orchestrator's `execute_all_phases_autonomously()` pattern
- **REQ-DBG-012:** "Phase Completion Event System" - integration with LearningObserver (autonomous pattern)
- **REQ-DBG-014:** "Git Checkpoint Integration" - matches TDD Workflow autonomous checkpointing
- **REQ-DBG-015:** "Debug Session Quality Gates (DoR/DoD)" - matches Planning Orchestrator quality gates

**Conclusion:** Migration to AUTONOMOUS aligns with planned architecture, not a pivot.

### Synergy with Other Migrations

1. **TDD Orchestrator v2 (Approved):** Shares TestExecutionManager, verification loop pattern
2. **Vacuum Orchestrator v2 (Complete):** Can reuse AST scanning for orphan detection
3. **Planning System v5 (Complete):** Can integrate Debug's AST analysis for plan generation

### Future Enhancements (Post-Migration)

**CORTEX 4.0 Enhancements (Deferred):**
- Chrome DevTools Protocol integration (real-time browser debugging)
- Automatic state diffing (before/after action comparison)
- ML-enhanced root cause analysis (pattern recognition from Tier 2)
- WebSocket streaming for live debug logs

**Current Scope:** Template-based approach (CORTEX 3.0) provides 80% value with 20% effort.

---

## ✅ Approval

**Evaluator:** Asif Hussain (CORTEX AI)  
**Date:** January 3, 2026  
**Status:** ✅ **RECOMMENDATION COMPLETE**

**Recommendation:** ✅ **AUTONOMOUS CONVERSION APPROVED**

**Next Steps:**
1. Present evaluation to stakeholders (Engineering, QA, Architecture teams)
2. Generate migration plan via Planning v5: `/CORTEX Plan Debug Orchestrator v2 Migration`
3. Schedule 3-day implementation window
4. Execute migration with 100% test coverage requirement
5. Progressive activation after successful validation

**Comments:**
Debug Orchestrator is the highest-complexity orchestrator assessed (9.50/10 score). The combination of AST manipulation, critical state management, and high reusability potential makes this a textbook case for AUTONOMOUS conversion. The planned manifest already follows autonomous patterns, confirming this recommendation aligns with original design intent.
