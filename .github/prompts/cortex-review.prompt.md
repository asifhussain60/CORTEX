# CORTEX Epic Review & Verification Prompt

**Purpose:** Comprehensive verification that epic plans align with implementation and CORTEX design goals.  
**Version:** 1.0.0  
**Author:** Asif Hussain  
**Usage:** Run against any epic or feature plan, multiple times throughout development lifecycle.

---

## 🎯 Review Objectives

This prompt performs holistic verification of CORTEX epic plans and implementations against:

1. **Strategic Alignment** - Does the design achieve stated goals?
2. **Architectural Integrity** - Are there conflicts, brittleness, or technical debt risks?
3. **Autonomous Execution** - Will it be an efficient RAG/DAG executor post-completion?
4. **Best Practices** - Does it follow knowledge library and company domain boundaries?
5. **Implementation Fidelity** - Does implementation match the plan?

---

## 📋 Review Scope

### Core Review Areas

**1. Strategic Goals Verification**
- Autonomous RAG/DAG execution capability
- Python-script-based orchestration (post-LLM handoff)
- Best practices adherence from knowledge library
- Company domain boundary enforcement
- Token optimization and efficiency

**2. Architecture Analysis**
- Master orchestrator → child orchestrator coordination
- LLM intent classification → Python execution handoff
- Script organization, categorization, and cataloging
- Development best practices enforcement
- Modular, maintainable code structure

**3. Snowball Effect Prioritization**
- Phase dependencies and sequencing
- Parallel execution opportunities
- Foundation-first approach validation
- Incremental value delivery

**4. Edge Cases & Failure Modes**
- Race conditions (concurrent execution, state conflicts)
- Integration failures (orchestrator coordination, registry conflicts)
- Deployment pitfalls (migration paths, rollback scenarios)
- Security vulnerabilities (privilege escalation, injection attacks)
- Performance bottlenecks (memory leaks, CPU spikes, database locks)

**5. Implementation Verification**
- Plan vs. actual code alignment
- Missing components or partial implementations
- Technical debt accumulation
- Testing coverage and quality

---

## 🔍 Review Process

### Phase 1: Epic Structure Analysis

**Target Files:**
- `00-{epic-name}.md` - Main epic document
- `phases/master-plan.md` - Phase breakdown
- `phases/phase-{N}-*.md` - Individual phase plans
- `tracking/progress.json` - Execution status

**Verification Points:**
1. ✅ All phases have clear deliverables
2. ✅ Dependencies correctly identified
3. ✅ Success criteria measurable
4. ✅ Snowball effect optimized
5. ✅ Phase 0 migration complete (if applicable)

**Output:** Structure integrity score (0-100)

---

### Phase 2: Architecture Coherence Review

**Target Files:**
- `cortex-brain/config/master-orchestrator.yaml`
- `cortex-brain/registry/orchestrators.json`
- `src/orchestrators/master_orchestrator.py`
- `src/orchestrators/pattern_router.py`
- `src/orchestrators/execution_engine.py`

**Verification Points:**
1. ✅ Master orchestrator routes to all registered orchestrators
2. ✅ Pattern matching deterministic (no regex ambiguity)
3. ✅ LLM fallback only for ambiguous cases
4. ✅ State management isolated per orchestrator
5. ✅ No circular dependencies
6. ✅ Autonomous orchestrators invoke Python scripts (not inline LLM)

**Output:** Architecture coherence score (0-100)

---

### Phase 3: Knowledge Integration Analysis

**Target Files:**
- `src/knowledge/company_knowledge_provider.py`
- `src/knowledge/knowledge_merger.py`
- `cortex-brain/tier2/company-knowledge/`
- Knowledge query implementations

**Verification Points:**
1. ✅ Company knowledge overrides CORTEX intelligently
2. ✅ Merge logic preserves best practices
3. ✅ Domain boundaries enforced
4. ✅ Query performance <50ms
5. ✅ No knowledge pollution (core vs. company isolation)

**Output:** Knowledge integrity score (0-100)

---

### Phase 4: Orchestrator Registry Audit

**Target Files:**
- `cortex-brain/registry/orchestrators.json`
- `cortex-brain/manifests/orchestrators/*.yaml`
- Custom orchestrator implementations

**Verification Points:**
1. ✅ All orchestrators registered with unique IDs
2. ✅ Manifests complete (patterns, capabilities, dependencies)
3. ✅ No pattern collisions between orchestrators
4. ✅ Custom orchestrators isolated from core
5. ✅ Inheritance relationships valid

**Output:** Registry health score (0-100)

---

### Phase 5: Edge Case & Failure Mode Analysis

**Critical Scenarios to Test:**

**A. Race Conditions**
- [ ] Concurrent plan creation (same epic, different users)
- [ ] State file conflicts (multiple orchestrators writing)
- [ ] Registry updates during routing
- [ ] Cache invalidation during knowledge merge

**B. Integration Failures**
- [ ] Orchestrator fails to load (missing dependency)
- [ ] Pattern match returns multiple orchestrators
- [ ] LLM fallback unavailable
- [ ] State database locked/corrupted
- [ ] Knowledge file missing/malformed

**C. Deployment & Migration**
- [ ] CORTEX-5.0 → CORTEX-5.5 migration incomplete
- [ ] Database schema version mismatch
- [ ] Manifest format version incompatibility
- [ ] Pull-from-CORTEX-5.0 budget exceeded
- [ ] Rollback to previous version

**D. Security Vulnerabilities**
- [ ] Company knowledge path traversal
- [ ] Orchestrator manifest injection
- [ ] State file tampering
- [ ] Privilege escalation via custom orchestrators
- [ ] Secrets leakage in logs/reports

**E. Performance Bottlenecks**
- [ ] Knowledge merge >50ms threshold
- [ ] Pattern matching >20ms threshold
- [ ] State persistence blocking execution
- [ ] Memory leaks in long-running orchestrators
- [ ] Database query N+1 problems

**Output:** Risk matrix with severity, likelihood, mitigation

---

### Phase 6: Implementation Fidelity Check

**Comparison Process:**

1. **Plan Analysis:**
   - Extract all deliverables from phase plans
   - Identify file creation/modification commitments
   - Map dependencies between components

2. **Implementation Analysis:**
   - Scan codebase for planned components
   - Verify file existence and completeness
   - Check test coverage for new code
   - Identify stub/placeholder implementations

3. **Gap Analysis:**
   - Missing implementations
   - Partial implementations
   - Over-implemented (scope creep)
   - Technical debt introduced

**Output:** Implementation completeness matrix

---

### Phase 7: Best Practices Enforcement & Governance Validation

**Target Files:**
- `cortex-brain/knowledge-library/standards/python-style-guide.md`
- `cortex-brain/knowledge-library/design-patterns/solid-principles.md`
- `cortex-brain/brain-protection-rules.yaml` (governance rules)
- `tracking/governance-audit.jsonl` (audit logs)
- All Python source files in `src/`
- Test files in `tests/`

**NEW: Audit Log Validation (MANDATORY FIRST STEP)**

Before checking code compliance, compare audit logs against completed implementation to identify gaps:

**Step 7.0: Audit Log Analysis**
- [ ] **Load Audit Logs:** Read `tracking/governance-audit.jsonl` (if exists)
- [ ] **Parse Violations:** Extract all violations by rule_id and file path
- [ ] **Compare Against Current Code:** Check if violations still exist
- [ ] **Identify Gaps:**
  - Violations marked "fixed" but still present in code
  - New violations introduced since last review
  - Violations in new files not yet audited
- [ ] **Block Phase Progression:** If critical violations unfixed, BLOCK next phase
- [ ] **Generate Gap Report:** `reports/governance-gaps-{timestamp}.yaml`

**Audit Log Schema:**
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "rule_id": "PYTHON_TYPE_HINTS_MANDATORY",
  "severity": "blocked",
  "file": "src/orchestrators/planning/planning_orchestrator_v5.py",
  "line": 245,
  "violation": "Missing return type hint for method execute_phase",
  "status": "active",  // active, fixed, ignored
  "fix_commit": null,
  "reviewer": "PythonBestPracticesValidator"
}
```

**Gap Detection Rules:**
1. If `status: "active"` → Verify violation still exists in current code
2. If `status: "fixed"` + `fix_commit` → Verify commit actually fixed it
3. If violation no longer exists but not marked "fixed" → Update audit log
4. If new violations found → Add to audit log with `status: "active"`

**Output:** Governance gaps matrix + recommendations

---

**Verification Points:**

**A. Python Style Guide Compliance (PEP 8)**
- [ ] **Indentation:** 4 spaces (no tabs)
- [ ] **Line Length:** ≤100 characters
- [ ] **Naming Conventions:**
  - Classes: PascalCase (`OrchestratorRegistry`)
  - Functions/methods: snake_case (`match_pattern`)
  - Constants: SCREAMING_SNAKE_CASE (`DEFAULT_TIMEOUT`)
  - Private attributes: _leading_underscore (`_cache`)
- [ ] **Import Organization:** stdlib → third-party → local (with blank line separation)
- [ ] **Whitespace:** Consistent spacing around operators, commas

**B. Type Hints (PEP 484 - MANDATORY)**
- [ ] **Function signatures:** Return type + parameter types for ALL public functions
- [ ] **Class attributes:** Type annotations for instance and class variables
- [ ] **Complex types:** Proper use of `Dict`, `List`, `Optional`, `Union`, `TypedDict`
- [ ] **Generic types:** `Type[T]`, `Callable[[Args], Return]` where applicable
- [ ] **No `Any`:** Avoid `Any` except for truly dynamic types (justify in comments)

**C. Docstrings (PEP 257 + Google Style - MANDATORY)**
- [ ] **Module docstrings:** Purpose, classes, author, version
- [ ] **Class docstrings:** Description, attributes, thread safety, example usage
- [ ] **Function/method docstrings:** Description, Args, Returns, Raises, Example
  - Include performance characteristics (e.g., "O(n) complexity")
  - Document side effects (e.g., "Modifies database")
  - Specify thread safety (e.g., "NOT thread-safe")

**D. SOLID Principles**
- [ ] **Single Responsibility:** Each class has ONE reason to change
  - ✅ GOOD: `OrchestratorRegistry` (registration only), `OrchestratorExecutor` (execution only)
  - ❌ BAD: `OrchestratorManager` (registration + execution + logging)
- [ ] **Open/Closed:** Extend via inheritance, don't modify existing classes
  - ✅ GOOD: `BaseOrchestrator` ABC with child orchestrators
  - ❌ BAD: Adding `if orchestrator_type == "new_type"` to existing code
- [ ] **Liskov Substitution:** Subclass can replace parent without breaking behavior
  - ✅ GOOD: All orchestrators return `Dict[str, Any]` with 'status' key
  - ❌ BAD: One orchestrator returns `str`, breaking caller expectations
- [ ] **Interface Segregation:** Small, focused interfaces
  - ✅ GOOD: `Executable`, `Cancellable`, `Monitorable` as separate protocols
  - ❌ BAD: `OrchestratorInterface` with 10+ methods (not all needed)
- [ ] **Dependency Inversion:** Depend on abstractions, not concretions
  - ✅ GOOD: `def __init__(self, state_store: StateStore)` (protocol)
  - ❌ BAD: `def __init__(self, db_path: str)` then hardcode `sqlite3.connect()`

**E. Code Quality Standards**
- [ ] **DRY (Don't Repeat Yourself):** No code duplication >5 lines
  - Extract to helper functions or base classes
- [ ] **KISS (Keep It Simple):** Prefer simple solutions over clever ones
  - ✅ GOOD: `orchestrator_id.isidentifier()`
  - ❌ BAD: Complex regex when simple method exists
- [ ] **YAGNI (You Aren't Gonna Need It):** No premature optimization/features
  - Don't add caching, metrics, backups until actually needed
- [ ] **Cyclomatic Complexity:** ≤10 per function
  - If >10, extract helper functions
- [ ] **Nesting Depth:** ≤4 levels
  - Use early returns, guard clauses

**F. Architecture Patterns (CORTEX-Specific)**
- [ ] **Master-Child Orchestrator:** Single entry point (MasterOrchestrator) routes to children
- [ ] **Plugin Architecture:** Dynamic orchestrator loading via registry
- [ ] **Strategy Pattern:** Execution modes (autonomous, guided, interactive)
- [ ] **Repository Pattern:** Abstract state persistence (SQLite, PostgreSQL swappable)
- [ ] **Chain of Responsibility:** Middleware for logging, validation, caching
- [ ] **LLM → Python Handoff:** Copilot transforms request → invokes Python via terminal
- [ ] **Snowball Optimization:** Dependency graph analysis for parallel execution

**G. Testing Best Practices**
- [ ] **Test Structure:** AAA pattern (Arrange-Act-Assert)
- [ ] **Test Naming:** Descriptive (e.g., `test_router_matches_planning_request`)
- [ ] **Test Coverage:**
  - Unit tests: 80%+ for all modules
  - Integration tests: 60%+ for orchestrator coordination
  - All error paths tested
  - Race condition tests for state management
- [ ] **Test Isolation:** Tests don't depend on each other
- [ ] **Test Performance:** Unit tests <100ms, integration tests <5s

**H. Error Handling**
- [ ] **Custom Exceptions:** Specific exception hierarchy (e.g., `OrchestratorNotFoundError`)
- [ ] **Context Managers:** Use `with` for resources (files, DB connections)
- [ ] **Retry Logic:** Exponential backoff for transient failures
- [ ] **Graceful Degradation:** Fallback behavior when non-critical components fail

**I. Security & Safety**
- [ ] **No Secrets in Code:** Environment variables or secure vaults only
- [ ] **Path Validation:** Prevent path traversal attacks
- [ ] **Input Sanitization:** Validate all external inputs
- [ ] **SQL Injection Prevention:** Parameterized queries only
- [ ] **Resource Limits:** Timeout, memory limits for orchestrators

**J. Performance & Scalability**
- [ ] **Complexity Limits:**
  - Lines per function: ≤50
  - Lines per class: ≤300
  - Parameters per function: ≤5
  - Module lines: ≤500
- [ ] **Lazy Loading:** Load orchestrators on-demand, not upfront
- [ ] **Database Optimization:**
  - WAL mode for SQLite concurrency
  - Connection pooling
  - Index on frequently queried columns
- [ ] **Caching:** Cache expensive operations (knowledge queries, pattern matching)

**K. Static Analysis Tools**
- [ ] **mypy:** Type checking with `--strict` flag (MANDATORY - Rule: PYTHON_TYPE_HINTS_MANDATORY)
  - Zero type errors allowed
  - All functions have type hints
  - Run: `mypy src/ --strict --show-error-codes`
- [ ] **pylint:** Code quality score ≥8.0
  - No bare-except warnings (Rule: PYTHON_ERROR_HANDLING_REQUIRED)
  - No broad-except without justification
  - Run: `pylint src/ --rcfile=.pylintrc`
- [ ] **pydocstyle:** Docstring coverage 100% for public APIs (MANDATORY - Rule: PYTHON_DOCSTRINGS_MANDATORY)
  - Google-style docstrings enforced
  - Args, Returns, Raises documented
  - Run: `pydocstyle src/ --convention=google`
- [ ] **black:** Consistent formatting (line length 100) (Rule: PYTHON_CODE_FORMATTING_REQUIRED)
  - Auto-fixable, should show zero diffs
  - Run: `black src/ --check --line-length=100`
- [ ] **isort:** Import sorting with `--profile=black` (Rule: PYTHON_IMPORT_ORGANIZATION_REQUIRED)
  - 3-group import structure enforced
  - Run: `isort src/ --check-only --profile=black`
- [ ] **pytest:** Test suite passes 100%
  - All tests pass without warnings
  - Run: `pytest tests/ -v`
- [ ] **coverage.py:** Coverage reports generated
  - Unit tests: ≥80% coverage
  - Integration tests: ≥60% coverage
  - Run: `coverage run -m pytest && coverage report`

**ENFORCEMENT:** All checks MUST pass before phase progression. CI/CD pipeline MUST block on failures.

**L. Documentation Completeness**
- [ ] **Architecture diagrams:** Up-to-date with implementation
- [ ] **README.md:** New capabilities documented
- [ ] **CHANGELOG.md:** All changes logged
- [ ] **API documentation:** Generated from docstrings (Sphinx)
- [ ] **Examples:** Custom orchestrator creation guide

**Output:** Best practices compliance score (0-100) with detailed breakdown per category

**NEW: Governance Rule Validation (Cross-Check with brain-protection-rules.yaml)**

After checking code compliance, validate against governance rules:

**Step 7.Z: Governance Cross-Check**
- [ ] **Load Governance Rules:** Read `cortex-brain/brain-protection-rules.yaml`
- [ ] **Validate Each Rule:**
  - **PYTHON_TYPE_HINTS_MANDATORY** → mypy --strict passes
  - **PYTHON_DOCSTRINGS_MANDATORY** → pydocstyle passes
  - **PYTHON_ERROR_HANDLING_REQUIRED** → pylint bare-except check passes
  - **PYTHON_SOLID_PRINCIPLES_REQUIRED** → SOLIDAnalyzer passes
  - **PYTHON_IMPORT_ORGANIZATION_REQUIRED** → isort check passes
  - **PYTHON_CODE_FORMATTING_REQUIRED** → black check passes
- [ ] **Check Middleware Implementation:**
  - `PythonBestPracticesValidator` exists in `src/orchestrators/middleware/`
  - Validator invoked on `pre_file_save` hook
  - Validator references knowledge library files
- [ ] **Verify Enforcement:**
  - Pre-commit hooks configured (.pre-commit-config.yaml)
  - CI/CD pipeline runs all checks
  - Failed checks block PR merges
- [ ] **Update Audit Log:** Log all violations found during this review

**Output:** Governance enforcement validation report

---

### Phase 8: Python AI Application Best Practices (NEW)

**Purpose:** Verify CORTEX-specific best practices for Python-based AI applications.

**Target Files:**
- `src/orchestrators/master_orchestrator.py`
- `src/orchestrators/pattern_router.py`
- `src/orchestrators/execution_engine.py`
- All child orchestrator implementations

**Verification Points:**

**A. LLM Integration Patterns**
- [ ] **LLM → Python Handoff:**
  - GitHub Copilot transforms requests (pattern matching + transformation)
  - Python executes via terminal invocation
  - NO inline LLM code generation during execution
- [ ] **Intent Classification:**
  - Pattern matching handles 90%+ of requests
  - LLM fallback ONLY for ambiguous cases
  - Classification confidence threshold ≥0.7
- [ ] **Context Window Management:**
  - Summarize long conversations (keep <8K tokens)
  - Use knowledge library references instead of full text
  - Prune irrelevant context before LLM calls

**B. Autonomous Orchestration**
- [ ] **Script-Based Execution:**
  - All autonomous orchestrators execute Python scripts (not LLM prompts)
  - Scripts cataloged and versioned
  - No duplicate script creation (SKULL enforcement)
- [ ] **State Machine Pattern:**
  - Clear state transitions (PENDING → RUNNING → COMPLETED → FAILED)
  - State persistence across executions
  - Rollback capability for failed states
- [ ] **Orchestrator Interface Contract:**
  - All orchestrators implement `OrchestratorInterface` protocol
  - Mandatory methods: `execute()`, `validate()`, `get_status()`
  - Consistent `__init__` signature (prevents INT-001 type issues)

**C. Knowledge Management**
- [ ] **Three-Layer Knowledge System:**
  - CORTEX knowledge (tier 0 - immutable best practices)
  - Company knowledge (tier 2 - overrides CORTEX intelligently)
  - Domain knowledge (tier 3 - project-specific)
- [ ] **Knowledge Merge Logic:**
  - Company knowledge overrides CORTEX only where relevant
  - Core best practices preserved
  - Merge conflicts logged for review
- [ ] **Knowledge Query Performance:**
  - <50ms for knowledge queries
  - Caching for frequently accessed knowledge
  - Lazy loading of domain-specific knowledge

**D. Registry & Plugin System**
- [ ] **Orchestrator Registry:**
  - JSON-based registry with validation schema
  - Lazy orchestrator instantiation (performance)
  - Dependency injection via registry metadata
- [ ] **Pattern Collision Detection:**
  - NO overlapping regex patterns
  - Priority-based routing when patterns similar
  - Test suite verifies pattern uniqueness
- [ ] **Orchestrator Validation:**
  - Validation before registration
  - Health checks before execution
  - Graceful degradation if orchestrator unavailable

**E. Concurrency & State Management**
- [ ] **Thread Safety:**
  - StateManager handles concurrent writes (SQLite WAL mode)
  - No JSON file-based state (prevents INT-001)
  - Transaction-based updates with retry logic
- [ ] **Race Condition Prevention:**
  - Database-level locking for critical sections
  - Optimistic concurrency control (version numbers)
  - Integration tests for concurrent orchestrator execution
- [ ] **State Isolation:**
  - Each orchestrator has isolated state namespace
  - No shared mutable state between orchestrators
  - State cleanup on orchestrator completion

**F. Observability & Debugging**
- [ ] **Audit Logging:**
  - All orchestrator executions logged
  - State transitions logged
  - Pattern matching decisions logged
- [ ] **Metrics Collection:**
  - Execution time per orchestrator
  - Pattern matching accuracy
  - State persistence latency
- [ ] **Debugging Tools:**
  - Execution trace for failed orchestrators
  - State snapshots at key transitions
  - Dry-run mode for testing

**G. Resilience & Reliability**
- [ ] **Retry Strategies:**
  - Exponential backoff for transient failures
  - Circuit breaker for persistent failures
  - Dead letter queue for unrecoverable errors
- [ ] **Rollback Mechanisms:**
  - Rollback scripts for migrations
  - State rollback on orchestrator failure
  - Validation that rollback successful
- [ ] **Health Checks:**
  - Orchestrator health endpoint
  - Dependency health checks (database, filesystem)
  - Automated recovery on health check failure

**Output:** Python AI application compliance score (0-100)

---

### Phase 9: Implementation Validation Against Plan (NEW)

**Purpose:** Verify completed implementation matches epic plan requirements.

**Target Files:**
- Epic plan files (00-*.md, phases/*.md)
- Implemented code (src/)
- Test files (tests/)
- Tracking data (tracking/progress-tracker.json)
- Audit logs (tracking/governance-audit.jsonl)

**Verification Points:**

**A. Phase Completion Validation**
- [ ] **Load Progress Tracker:** Read `tracking/progress-tracker.json`
- [ ] **Verify Phase Status:**
  - All phases marked "completed" have corresponding artifacts
  - Completion criteria from phase plans actually met
  - Success metrics measured and documented
- [ ] **Check Deliverables:**
  - Each phase lists required deliverables in plan
  - Verify each deliverable exists and functions correctly
  - Cross-reference with git commits (deliverable creation dates)
- [ ] **Validate Dependencies:**
  - Phase dependencies honored (no phase started before prerequisites)
  - Dependency artifacts available when needed
  - No circular dependencies introduced

**B. Gap Analysis (Plan vs. Implementation)**
- [ ] **Missing Features:**
  - Features planned but not implemented
  - Partial implementations (80% complete but marked done)
  - Features implemented differently than planned (document why)
- [ ] **Scope Creep Detection:**
  - Features implemented but not in plan (are they necessary?)
  - Extra complexity added without justification
  - Technical debt introduced that wasn't anticipated
- [ ] **Deviations from Design:**
  - Architecture changes not reflected in plan updates
  - API signatures different from specifications
  - Data models diverged from schema definitions

**C. Governance Compliance Verification**
- [ ] **Audit Log Reconciliation:**
  - All active violations in audit log fixed before phase marked complete
  - No new violations introduced in phase
  - Violation trends tracked (improving or degrading?)
- [ ] **SKULL Rule Enforcement:**
  - TDD_ENFORCEMENT: Tests written before implementation
  - SETUP_VERIFICATION: Phase -2 verification passed
  - TEARDOWN_REFACTOR: Phase N+1 refactor completed
  - PLAN_FILE_ORGANIZATION: All files in correct subfolders
- [ ] **Knowledge Library Usage:**
  - Best practices from knowledge library followed
  - Company domain boundaries respected
  - Architecture patterns applied correctly

**D. Quality Gate Validation**
- [ ] **All Static Analysis Passes:**
  - mypy --strict (zero errors)
  - pylint ≥8.0 score
  - pydocstyle (100% docstring coverage)
  - black --check (zero diffs)
  - isort --check (zero diffs)
  - pytest (100% pass)
  - coverage ≥80% unit, ≥60% integration
- [ ] **Manual Testing Completed:**
  - Integration tests run successfully
  - End-to-end workflows validated
  - Edge cases tested (from Phase 5 edge case analysis)
- [ ] **Performance Benchmarks Met:**
  - Orchestrator execution time within SLA
  - Memory usage within limits
  - Database query performance acceptable

**E. Pre-Phase-Progression Checklist**

Before allowing progression to next phase, ALL must be checked:

- [ ] ✅ **Audit Logs Clean:** No active critical violations
- [ ] ✅ **Plan-Code Alignment:** Implementation matches plan ≥95%
- [ ] ✅ **Governance Rules Pass:** All BLOCKED severity rules satisfied
- [ ] ✅ **Static Analysis Pass:** All tools pass with zero errors
- [ ] ✅ **Tests Pass:** 100% test pass rate
- [ ] ✅ **Documentation Updated:** All new code documented
- [ ] ✅ **Deliverables Verified:** All phase deliverables exist and function
- [ ] ✅ **No Regressions:** Previous phases still work correctly

**BLOCKING:** If ANY checklist item fails, BLOCK progression to next phase. Generate remediation plan.

**Output:** Implementation validation report with GO/NO-GO decision

---

## 📊 Review Report Format

### Report Structure

**File:** `cortex-brain/documents/planning/active/{epic-name}/reports/cortex-review/{YYYYMMDD_HHMMSS}_review.yaml`

```yaml
metadata:
  epic_id: "cortex5-enhancement-epic"
  review_date: "2026-01-07T10:30:00Z"
  reviewer: "CORTEX Review System"
  review_iteration: 1
  previous_review: null  # Path to previous review for delta analysis

summary:
  overall_score: 85  # 0-100
  status: "ON_TRACK"  # ON_TRACK, AT_RISK, CRITICAL
  critical_issues: 2
  high_priority_issues: 5
  medium_priority_issues: 12
  low_priority_issues: 8
  
  executive_summary: |
    CORTEX-5 epic shows strong strategic alignment (92/100) and architectural coherence (88/100).
    Two critical issues identified: race condition in state management and missing rollback strategy.
    Overall implementation on track with 87% phase completion fidelity.

phase_scores:
  structure_integrity: 95
  architecture_coherence: 88
  knowledge_integration: 82
  registry_health: 91
  edge_case_coverage: 65  # LOW - Requires attention
  implementation_fidelity: 87
  best_practices: 79
  python_ai_application: 84
  implementation_validation: 90
  governance_compliance: 88

governance_audit_analysis:
  audit_log_path: "tracking/governance-audit.jsonl"
  total_violations_logged: 42
  active_violations: 3
  fixed_violations: 38
  ignored_violations: 1
  
  violations_by_rule:
    PYTHON_TYPE_HINTS_MANDATORY:
      total: 15
      active: 2
      files:
        - "src/orchestrators/planning/planning_orchestrator_v5.py:245"
        - "src/orchestrators/state_manager.py:89"
    PYTHON_DOCSTRINGS_MANDATORY:
      total: 12
      active: 1
      files:
        - "src/orchestrators/execution_engine.py:156"
    PYTHON_ERROR_HANDLING_REQUIRED:
      total: 8
      active: 0
      files: []
    PYTHON_SOLID_PRINCIPLES_REQUIRED:
      total: 7
      active: 0
      files: []
  
  gap_analysis:
    violations_fixed_but_regressed: 0
    violations_marked_fixed_but_still_present: 0
    new_violations_since_last_review: 3
    violations_blocking_phase_progression: 3
  
  remediation_required: true
  blocking_issues:
    - rule_id: "PYTHON_TYPE_HINTS_MANDATORY"
      file: "src/orchestrators/planning/planning_orchestrator_v5.py"
      line: 245
      impact: "HIGH"
      recommendation: "Add return type hint: -> Dict[str, Any]"
    - rule_id: "PYTHON_TYPE_HINTS_MANDATORY"
      file: "src/orchestrators/state_manager.py"
      line: 89
      impact: "CRITICAL"
      recommendation: "Add type hints for all parameters and return value"
    - rule_id: "PYTHON_DOCSTRINGS_MANDATORY"
      file: "src/orchestrators/execution_engine.py"
      line: 156
      impact: "HIGH"
      recommendation: "Add Google-style docstring with Args, Returns, Raises"

pre_phase_progression_checklist:
  phase_1_to_phase_2:
    audit_logs_clean: false  # 3 active critical violations
    plan_code_alignment: true  # 96% alignment
    governance_rules_pass: false  # Type hints missing
    static_analysis_pass: false  # mypy errors
    tests_pass: true  # 100% pass rate
    documentation_updated: true
    deliverables_verified: true
    no_regressions: true
    
    decision: "NO-GO"
    blocking_reason: "3 active governance violations must be fixed before Phase 2"
    remediation_plan_path: "reports/phase-1-remediation-{timestamp}.yaml"

strategic_alignment:
  autonomous_rag_dag_execution:
    status: "EXCELLENT"
    score: 92
    evidence:
      - "Master orchestrator correctly routes to Python-based child orchestrators"
      - "LLM only used for intent classification, not execution"
      - "State machine pattern enables DAG execution"
    gaps:
      - "Continuation system lacks retry logic for failed phases"
  
  python_script_based:
    status: "GOOD"
    score: 85
    evidence:
      - "All autonomous orchestrators invoke Python via terminal"
      - "No inline LLM code generation during execution"
    gaps:
      - "Some orchestrators still have LLM-dependent validation"
  
  best_practices_adherence:
    status: "GOOD"
    score: 81
    evidence:
      - "Company knowledge provider queries CORTEX library first"
      - "Merge logic preserves CORTEX best practices"
    gaps:
      - "Override logic not fully tested for all knowledge types"
  
  token_optimization:
    status: "EXCELLENT"
    score: 94
    evidence:
      - "Pattern matching eliminates 90% of LLM calls"
      - "Context middleware reuses cross-session data"
    gaps: []

architecture_analysis:
  master_orchestrator_coordination:
    status: "EXCELLENT"
    score: 91
    findings:
      - "Routing deterministic via PatternRouter"
      - "ExecutionEngine manages lifecycle correctly"
      - "State isolation per orchestrator"
    issues:
      - severity: "HIGH"
        title: "Race condition in StateManager"
        description: "Concurrent orchestrator execution can corrupt state.db"
        file: "src/orchestrators/state_manager.py"
        line: 145
        recommendation: "Implement file locking or SQLite WAL mode"
  
  script_organization:
    status: "GOOD"
    score: 78
    findings:
      - "Planning orchestrator well-structured"
      - "Vacuum orchestrator follows module pattern"
    issues:
      - severity: "MEDIUM"
        title: "Inconsistent module organization"
        description: "Some orchestrators in src/orchestrators/, others in src/operations/modules/"
        recommendation: "Consolidate to single location or document convention"

edge_cases:
  race_conditions:
    - id: "RACE-001"
      severity: "CRITICAL"
      title: "State database concurrent write corruption"
      scenario: "Two orchestrators write to planning_state.db simultaneously"
      likelihood: "HIGH"
      impact: "HIGH"
      current_mitigation: "None"
      recommended_mitigation: "Enable SQLite WAL mode + row-level locking"
      test_exists: false
  
  integration_failures:
    - id: "INT-001"
      severity: "HIGH"
      title: "Pattern collision detection missing"
      scenario: "Custom orchestrator registered with pattern matching core orchestrator"
      likelihood: "MEDIUM"
      impact: "HIGH"
      current_mitigation: "Manual review during registration"
      recommended_mitigation: "Automated collision detection in registry"
      test_exists: false
  
  deployment_pitfalls:
    - id: "DEPLOY-001"
      severity: "CRITICAL"
      title: "No rollback strategy for failed migration"
      scenario: "CORTEX-5.5 migration fails midway, leaving broken state"
      likelihood: "MEDIUM"
      impact: "CRITICAL"
      current_mitigation: "None documented"
      recommended_mitigation: "Add rollback script + backup/restore procedure"
      test_exists: false
  
  security_vulnerabilities:
    - id: "SEC-001"
      severity: "MEDIUM"
      title: "Company knowledge path traversal risk"
      scenario: "Malicious company_id '../../../etc' escapes tier2 directory"
      likelihood: "LOW"
      impact: "HIGH"
      current_mitigation: "None"
      recommended_mitigation: "Validate company_id format (alphanumeric only)"
      test_exists: false
  
  performance_bottlenecks:
    - id: "PERF-001"
      severity: "LOW"
      title: "Knowledge merge not cached across requests"
      scenario: "Same company knowledge merged on every request"
      likelihood: "HIGH"
      impact: "MEDIUM"
      current_mitigation: "None"
      recommended_mitigation: "Add in-memory cache with TTL"
      test_exists: false

implementation_gaps:
  missing_components:
    - component: "Rollback script for CORTEX-5.5 migration"
      planned_phase: "Phase 0"
      status: "NOT_IMPLEMENTED"
      blocker: false
    
    - component: "Pattern collision detection in orchestrator registry"
      planned_phase: "Phase 2"
      status: "NOT_IMPLEMENTED"
      blocker: true
  
  partial_implementations:
    - component: "Knowledge merge caching"
      planned_phase: "Phase 1"
      status: "PARTIAL"
      completion: "60%"
      missing: "Cache invalidation logic"
      blocker: false
  
  technical_debt:
    - component: "StateManager concurrency handling"
      description: "Uses basic file I/O without locking"
      severity: "HIGH"
      recommendation: "Refactor to use SQLite transactions"
    
    - component: "Orchestrator module location inconsistency"
      description: "Mixed src/orchestrators/ and src/operations/modules/"
      severity: "MEDIUM"
      recommendation: "Consolidate or document convention clearly"

recommendations:
  immediate_actions:
    - priority: "CRITICAL"
      action: "Implement StateManager file locking to prevent race conditions"
      effort: "4 hours"
      impact: "Prevents data corruption in concurrent usage"
    
    - priority: "CRITICAL"
      action: "Create rollback script for CORTEX-5.5 migration"
      effort: "2 hours"
      impact: "Enables safe recovery from failed migrations"
    
    - priority: "HIGH"
      action: "Add pattern collision detection to registry"
      effort: "6 hours"
      impact: "Prevents runtime routing conflicts"
  
  short_term_improvements:
    - priority: "HIGH"
      action: "Implement knowledge merge caching with TTL"
      effort: "3 hours"
      impact: "Reduces latency by 30-50% for repeat queries"
    
    - priority: "MEDIUM"
      action: "Standardize orchestrator module organization"
      effort: "1 hour"
      impact: "Improves developer experience and maintainability"
  
  long_term_enhancements:
    - priority: "LOW"
      action: "Create comprehensive edge case test suite"
      effort: "20 hours"
      impact: "Prevents regression and improves system robustness"

next_review:
  recommended_date: "2026-01-14T10:00:00Z"
  focus_areas:
    - "Verify StateManager race condition fix"
    - "Confirm rollback script operational"
    - "Validate pattern collision detection"
  triggers:
    - "Before Phase 2 completion"
    - "After any critical architecture change"
    - "Weekly during active development"
```

---

## 🚀 Usage Instructions

### Initial Review

```bash
# Run against active epic
cortex review cortex-brain/documents/planning/active/cortex5-enhancement-epic

# Or invoke via CORTEX prompt
"Review the CORTEX-5 enhancement epic using cortex-review.prompt.md"
```

### Incremental Review (Reads Previous Reports)

```bash
# Automatic context from previous reviews
cortex review cortex-brain/documents/planning/active/cortex5-enhancement-epic --incremental

# Will read:
# - reports/cortex-review/{latest}_review.yaml
# - Identify changes since last review
# - Focus on previously flagged issues
# - Track resolution progress
```

### Review During Implementation

```bash
# Check specific phase alignment
cortex review cortex-brain/documents/planning/active/cortex5-enhancement-epic --phase 1

# Verify implementation matches phase 1 plan
# Highlight deviations
# Check phase 1 success criteria
```

---

## 🎯 Success Criteria

A review is considered **PASSING** when:

1. ✅ **Overall Score ≥85** - Indicates strong alignment and quality
2. ✅ **No Critical Issues** - All CRITICAL severity items resolved
3. ✅ **Architecture Coherence ≥80** - Core design sound
4. ✅ **Implementation Fidelity ≥80** - Code matches plan
5. ✅ **Edge Case Coverage ≥70** - Major failure modes addressed
6. ✅ **Governance Compliance ≥85** - All BLOCKED rules satisfied (NEW)
7. ✅ **Audit Logs Clean** - Zero active critical violations (NEW)
8. ✅ **Pre-Phase Checklist 100%** - All items checked before phase progression (NEW)

A review is **AT_RISK** when:

- ⚠️ Overall Score 70-84
- ⚠️ 1-2 Critical Issues
- ⚠️ Architecture Coherence 65-79
- ⚠️ Edge Case Coverage <70
- ⚠️ Governance Compliance 70-84 (NEW)
- ⚠️ 1-5 active non-critical violations (NEW)

A review is **CRITICAL** when:

- 🚨 Overall Score <70
- 🚨 3+ Critical Issues
- 🚨 Architecture Coherence <65
- 🚨 Implementation Fidelity <60
- 🚨 Governance Compliance <70 (NEW)
- 🚨 Any active BLOCKED severity violations (NEW)
- 🚨 Phase progression attempted with failing checklist (NEW)

**NEW: Phase Progression Blocking Rules**

Phase progression is **BLOCKED** if ANY of these conditions are true:

1. 🚫 Active violations with severity = "blocked" exist in audit logs
2. 🚫 Static analysis tools (mypy, pylint, pydocstyle) have errors
3. 🚫 Pre-phase progression checklist has any unchecked items
4. 🚫 Implementation gaps >5% (plan-code alignment <95%)
5. 🚫 Test coverage <80% for unit tests or <60% for integration tests
6. 🚫 Previous phase deliverables not verified

**Remediation Process:**

When phase progression is blocked:
1. Generate remediation plan: `reports/phase-{N}-remediation-{timestamp}.yaml`
2. Fix all blocking issues
3. Re-run review
4. Validate fixes in audit logs (status changed to "fixed")
5. Only then allow phase progression

---

## 📚 Reference Documents

**CORTEX Architecture:**
- `.github/prompts/CORTEX.prompt.md` - Main prompt with intent routing
- `cortex-brain/brain-protection-rules.yaml` - SKULL governance rules
- `cortex-brain/response-templates-v4.yaml` - Response format specifications

**Epic Plans:**
- `00-{epic-name}.md` - Epic overview
- `phases/master-plan.md` - Phase coordination
- `phases/phase-{N}-*.md` - Phase-specific plans

**Implementation:**
- `src/orchestrators/` - Orchestrator implementations
- `src/knowledge/` - Knowledge system
- `cortex-brain/registry/` - Orchestrator registry

---

## 🔄 Review Lifecycle

```
Plan Created → Initial Review (Baseline)
     ↓
Implementation Starts → Weekly Reviews (Progress Tracking)
     ↓
Phase Completes → Phase Review (Verification)
     ↓
Epic Completes → Final Review (Acceptance)
     ↓
Post-Deployment → Retrospective Review (Lessons Learned)
```

**Review Frequency:**
- **Planning Phase:** 1 initial review (baseline)
- **Active Development:** Weekly reviews
- **Phase Transitions:** Mandatory phase review
- **Critical Changes:** Ad-hoc review triggered by architecture changes
- **Post-Deployment:** 1 retrospective review (30 days after completion)

---

## 🛡️ CORTEX Integration

This prompt integrates with CORTEX routing:

**Trigger Patterns:**
- `review epic`
- `verify plan`
- `cortex review`
- `check alignment`
- `validate implementation`

**Orchestrator:** Investigation System v2 (adapted for review workflow)

**Output Location:** `cortex-brain/documents/planning/active/{epic-name}/reports/cortex-review/`

---

**Last Updated:** 2026-01-07  
**Maintainer:** Asif Hussain  
**Version:** 1.0.0
