# Orchestrator Responsibility Matrix

**Document:** AC-PLANNING-RESPONSIBILITIES-001  
**Author:** GitHub Copilot  
**Date:** 2026-01-26  
**Authority:** CORTEX Master Orchestrator

---

## Overview

This document defines the responsibility mapping between user intents and orchestrator handlers in the CORTEX planning system.

**Key Principle:** Each intent type is handled by a single orchestrator (CORE-035: Single Canonical Implementation).

---

## Intent-to-Orchestrator Mapping

### 1. IMPLEMENT → TDDOrchestrator

**When to use:** User wants to create new features, modules, components, or endpoints.

**Orchestrator:** `cortex.orchestrators.core.tdd_orchestrator.TDDOrchestrator`

**Responsibilities:**
- Write RED cycle tests first (failing tests)
- Implement GREEN cycle (minimal code to pass tests)
- REFACTOR cycle (optimize and improve)
- Verify 100% test coverage before completion
- Apply governance rules (CORE-008, 011, 012, 013)

**Governance Rules:**
- **CORE-008:** TDD mandatory - tests BEFORE code
- **CORE-011:** Type hints on all functions
- **CORE-012:** Google-style docstrings
- **CORE-013:** No bare except clauses
- **CORE-026:** Git checkpoint after completion

**Typical Phases:**
1. RED Cycle: Write failing tests
2. GREEN Cycle: Implement minimal code
3. REFACTOR Cycle: Optimize code
4. Git Checkpoint: Save work with AC markers

**Estimated Duration:** 1-4 hours (depends on scope and complexity)

**Example User Requests:**
- "Implement REST API endpoint for user management"
- "Create new authentication module"
- "Build plan validator component"

---

### 2. FIX → IntentRouter (delegates to FixHandler)

**When to use:** User wants to fix bugs, issues, errors, or edge cases.

**Primary Orchestrator:** `cortex.orchestrators.core.intent_router.IntentRouter`  
**Secondary Handler:** `FixHandler`

**Responsibilities:**
- Analyze bug/issue description
- Identify root cause category
- Route to specialized fix handler
- Write tests that reproduce the bug (RED)
- Fix the bug (GREEN)
- Verify fix doesn't break existing tests
- Apply implementation truth (CORE-030)

**Governance Rules:**
- **CORE-008:** TDD for fixes - write reproduction test first
- **CORE-011:** Type hints
- **CORE-013:** No bare except
- **CORE-026:** Git checkpoint per phase
- **CORE-030:** Implementation truth - verify code works

**Typical Phases:**
1. Analyze issue
2. Write reproduction test
3. Identify root cause
4. Apply minimal fix
5. Verify all tests pass
6. Git Checkpoint

**Estimated Duration:** 30 minutes - 2 hours

**Example User Requests:**
- "Fix authentication token expiration bug"
- "Performance is slow when loading large datasets"
- "Null pointer exception in user service"

---

### 3. REFACTOR → RefactoringOrchestrator

**When to use:** User wants to improve code quality, eliminate duplication, or restructure code.

**Orchestrator:** `cortex.orchestrators.domain.refactoring_orchestrator.RefactoringOrchestrator`

**Responsibilities:**
- Identify refactoring target (function, class, module)
- Plan refactoring strategy (extract, inline, move, etc)
- Write tests for existing behavior
- Apply refactoring changes
- Verify all tests still pass
- Improve code organization
- Eliminate duplication (CORE-035)

**Governance Rules:**
- **CORE-008:** TDD discipline - test behavior first
- **CORE-011:** Type hints
- **CORE-035:** Eliminate code duplication (Single Canonical Implementation)
- **CORE-026:** Git checkpoint
- **CORE-030:** Implementation truth

**Typical Phases:**
1. Analyze current code
2. Write behavior tests
3. Plan refactoring strategy
4. Apply changes incrementally
5. Verify tests pass
6. Git Checkpoint

**Estimated Duration:** 1-3 hours

**Example User Requests:**
- "Extract common authentication logic to shared module"
- "Refactor UserService to reduce complexity"
- "Remove duplication in plan validation code"

---

### 4. DOCUMENT → DocumentationOrchestrator

**When to use:** User wants to create or update documentation.

**Orchestrator:** `cortex.orchestrators.documentation.DocumentationOrchestrator`

**Responsibilities:**
- Create or update documentation
- Add code examples
- Create diagrams/visualizations
- Ensure consistency with existing docs
- Apply documentation standards
- Cross-reference related documents
- Apply doc quality standards (CORE-012)

**Governance Rules:**
- **CORE-012:** Documentation quality and accuracy
- **CORE-026:** Git checkpoint
- **CORE-030:** Verify documentation accuracy

**Typical Phases:**
1. Analyze documentation needs
2. Create/update content
3. Add examples
4. Review for accuracy
5. Git Checkpoint

**Estimated Duration:** 30 minutes - 2 hours

**Example User Requests:**
- "Document the new REST API endpoints"
- "Create architecture guide for planning system"
- "Update user guide with new features"

---

### 5. TEST → TDDOrchestrator

**When to use:** User wants to improve test coverage or write new tests.

**Orchestrator:** `cortex.orchestrators.core.tdd_orchestrator.TDDOrchestrator`

**Responsibilities:**
- Analyze test coverage gaps
- Write unit tests
- Write integration tests
- Write end-to-end tests
- Verify test quality (assertions, edge cases)
- Achieve coverage targets
- Apply TDD discipline (CORE-008)

**Governance Rules:**
- **CORE-008:** TDD discipline
- **CORE-011:** Type hints
- **CORE-012:** Docstrings on test functions
- **CORE-026:** Git checkpoint

**Typical Phases:**
1. Identify coverage gaps
2. Write tests
3. Run test suite
4. Verify coverage improved
5. Git Checkpoint

**Estimated Duration:** 1-3 hours

**Example User Requests:**
- "Improve test coverage to 95%"
- "Write integration tests for payment module"
- "Add edge case tests for plan validator"

---

### 6. ANALYZE → MasterOrchestrator

**When to use:** User wants code analysis, reports, or recommendations (read-only).

**Orchestrator:** `cortex.orchestrators.core.master_orchestrator.MasterOrchestrator`

**Responsibilities:**
- Perform code analysis
- Generate reports
- Identify issues/opportunities
- Suggest improvements
- Provide recommendations
- **NO code changes** (read-only operation)

**Governance Rules:**
- **CORE-030:** Implementation truth

**Typical Phases:**
1. Analyze request
2. Run static analysis
3. Generate findings
4. Suggest actions
5. Report results

**Estimated Duration:** 15 minutes - 1 hour

**Example User Requests:**
- "Analyze code complexity in authentication module"
- "Identify potential performance bottlenecks"
- "Report on test coverage gaps"

---

## Execution Gate Matrix

The execution gate determines how automatically a phase executes:

```
Impact \ Confidence    HIGH            MEDIUM              LOW
─────────────────────────────────────────────────────────────
LOW                   AUTO_EXECUTE    NOTIFY_AND_EXECUTE  NOTIFY_USER
MEDIUM               NOTIFY_AND_EXE   CONFIRM_BEFORE      CONFIRM_BEFORE
HIGH                 NOTIFY_USER      CONFIRM_BEFORE      BLOCKED
```

### Gate Types:

- **AUTO_EXECUTE** (Green)
  - Low impact + High confidence
  - Execute immediately, no confirmation needed
  - Example: Fixing a typo in documentation

- **NOTIFY_AND_EXECUTE** (Blue)
  - Low impact + Medium confidence, OR Medium impact + High confidence
  - Execute but notify user immediately
  - Example: Adding a new test file

- **CONFIRM_BEFORE_EXECUTE** (Yellow)
  - Medium impact + Medium confidence, OR High impact + Medium confidence
  - Wait for user confirmation before executing
  - Example: Refactoring a core module

- **NOTIFY_USER** (Orange)
  - High impact + High confidence
  - Notify user and ask for permission
  - Example: Major API endpoint change

- **BLOCKED** (Red)
  - High impact + Low confidence
  - Do NOT execute - requires design review
  - Escalate to human architect for approval
  - Example: Complete system restructuring

---

## Challenge Generation Rules

The challenge engine generates strategic questions based on request analysis:

### Governance Violations (Severity: HIGH)
**Triggers:**
- Bare except clause detected
- Missing type hints
- Missing docstring
- Code duplication detected

**Response:** "Your request violates CORE-XXX. Apply governance rules before proceeding."

### Alternative Path Suggestions (Severity: MEDIUM)
**Triggers:**
- Copy/paste pattern detected
- Similar implementation exists elsewhere
- Duplication in functionality

**Response:** "Consider extracting to shared module instead of duplicating code."

### Scope Creep Detection (Severity: MEDIUM)
**Triggers:**
- Multiple independent tasks (many AND clauses)
- Description longer than expected for scope
- Scope/description mismatch

**Response:** "Break into smaller, focused requests for clarity and efficiency."

### Risk Mismatch (Severity: HIGH)
**Triggers:**
- High impact + Low confidence
- System changes with uncertainty
- Unknown dependencies

**Response:** "Increase confidence through research, design, or incremental approach."

---

## Phase Types to Orchestrator Mapping

Common phase types and their default handlers:

### Implementation Phases
- `feature_implementation` → TDDOrchestrator
- `api_endpoint_creation` → TDDOrchestrator
- `module_creation` → TDDOrchestrator
- `component_implementation` → TDDOrchestrator

### Fix Phases
- `bug_fix` → IntentRouter (FixHandler)
- `performance_optimization` → RefactoringOrchestrator
- `error_handling` → IntentRouter
- `edge_case_fix` → IntentRouter

### Refactoring Phases
- `code_refactoring` → RefactoringOrchestrator
- `duplication_removal` → RefactoringOrchestrator
- `structure_improvement` → RefactoringOrchestrator
- `technical_debt_reduction` → RefactoringOrchestrator

### Testing Phases
- `unit_testing` → TDDOrchestrator
- `integration_testing` → TDDOrchestrator
- `coverage_improvement` → TDDOrchestrator

### Documentation Phases
- `api_documentation` → DocumentationOrchestrator
- `user_guide_creation` → DocumentationOrchestrator
- `code_documentation` → DocumentationOrchestrator
- `architecture_documentation` → DocumentationOrchestrator

---

## Governance Rule Enforcement

### CORE-008: TDD Mandatory
- Applied by: TDDOrchestrator, TDDCycleExecutor
- Applicable to: IMPLEMENT, FIX, REFACTOR, TEST
- Enforcement: Tests written BEFORE code

### CORE-011: Type Hints Mandatory
- Applied by: Pylance, CodeAnalyzer
- Applicable to: IMPLEMENT, FIX, REFACTOR
- Enforcement: All functions must have type hints

### CORE-012: Docstrings Mandatory
- Applied by: DocstringChecker
- Applicable to: IMPLEMENT, FIX, REFACTOR, DOCUMENT
- Enforcement: Google-style docstrings required

### CORE-013: No Bare Except
- Applied by: Pylint, CodeAnalyzer
- Applicable to: IMPLEMENT, FIX, REFACTOR
- Enforcement: Specific exception types required

### CORE-026: Git Checkpoints
- Applied by: PhaseExecutor
- Applicable to: All phases
- Enforcement: Commit after each phase with AC markers

### CORE-030: Implementation Truth
- Applied by: TestExecutor, CodeValidator
- Applicable to: All phases
- Enforcement: Verify code works, don't trust docs

### CORE-035: Single Canonical Implementation
- Applied by: DuplicationDetector, RefactoringOrchestrator
- Applicable to: IMPLEMENT, REFACTOR
- Enforcement: No code duplication, extract to shared module

---

## Usage Examples

### Example 1: User Implements a Feature

```
User Request: "Implement user authentication module"
↓
Intent: IMPLEMENT
↓
Orchestrator: TDDOrchestrator
↓
Phases:
  1. RED Cycle: Write failing tests for auth logic
  2. GREEN Cycle: Implement minimal auth module
  3. REFACTOR Cycle: Optimize code structure
  4. Git Checkpoint: Commit with AC-AUTH-001 markers
↓
Governance Applied:
  - CORE-008: TDD (RED→GREEN→REFACTOR)
  - CORE-011: Type hints required
  - CORE-012: Docstrings required
  - CORE-013: No bare except clauses
  - CORE-026: Git checkpoint
↓
Execution Gate:
  - Impact: HIGH (new authentication system)
  - Confidence: MEDIUM (established patterns)
  - Gate: CONFIRM_BEFORE_EXECUTE
```

### Example 2: User Fixes a Bug

```
User Request: "Fix authentication token expiration bug"
↓
Intent: FIX
↓
Orchestrator: IntentRouter → FixHandler
↓
Phases:
  1. Analyze: Understand token expiration logic
  2. Reproduce: Write failing test that shows bug
  3. Fix: Apply minimal fix
  4. Verify: All tests pass
  5. Git Checkpoint: Commit with AC-AUTH-FIX-001
↓
Governance Applied:
  - CORE-008: TDD (write test first)
  - CORE-030: Implementation truth (verify fix works)
↓
Execution Gate:
  - Impact: MEDIUM (affects auth system)
  - Confidence: HIGH (clear bug description)
  - Gate: NOTIFY_AND_EXECUTE
```

### Example 3: User Refactors Duplicated Code

```
User Request: "Extract common validation logic to shared module"
↓
Intent: REFACTOR
↓
Orchestrator: RefactoringOrchestrator
↓
Phases:
  1. Analyze: Find duplicate validation code
  2. Test: Write tests for validation behavior
  3. Extract: Move code to shared module
  4. Update: Fix imports in existing code
  5. Verify: All tests pass
  6. Git Checkpoint: Commit with AC-VALIDATION-001
↓
Governance Applied:
  - CORE-008: TDD (test first)
  - CORE-035: Single canonical implementation
  - CORE-030: Implementation truth
↓
Execution Gate:
  - Impact: MEDIUM (refactoring affects multiple modules)
  - Confidence: HIGH (clear duplication)
  - Gate: NOTIFY_AND_EXECUTE
```

---

## Implementation Status

✅ **Documented Intent Handlers:**
- TDDOrchestrator (IMPLEMENT, TEST)
- IntentRouter → FixHandler (FIX)
- RefactoringOrchestrator (REFACTOR)
- DocumentationOrchestrator (DOCUMENT)
- MasterOrchestrator (ANALYZE)

✅ **Governance Rules:**
- CORE-008 through CORE-035 (31 rules total)

✅ **Execution Gates:**
- 5-tier gate system (AUTO → BLOCKED)

✅ **Challenge Generation:**
- 4 challenge types (governance, alternative, scope, risk)

---

## Related Documents

- [Autonomous Execution Infrastructure](../AUTONOMOUS-EXECUTION-INFRASTRUCTURE.md)
- [LENS Protocol](../05-lens-protocol/)
- [Governance Rules](../01-cortex-brain/GOVERNANCE_REGISTRY.md)
- [Planner Orchestrator Documentation](./PLANNER_ORCHESTRATOR.md)

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-26  
**Authority:** AC-PLANNING-RESPONSIBILITIES-001
