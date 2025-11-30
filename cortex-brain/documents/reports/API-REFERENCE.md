# TDD Workflow Orchestrator - API Reference

**Purpose:** Complete API documentation for TDDWorkflowOrchestrator  
**Version:** 1.0  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Configuration](#configuration)
3. [Core Methods](#core-methods)
4. [Session Management](#session-management)
5. [Workflow Phases](#workflow-phases)
6. [Return Types](#return-types)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

---

## Overview

The `TDDWorkflowOrchestrator` provides unified API for complete Test-Driven Development workflows, integrating:
- **Phase 1:** Test generation (edge cases, domain knowledge, error conditions, parametrized)
- **Phase 2:** Workflow management (TDD state machine, refactoring intelligence, session tracking)
- **Phase 3:** End-to-end orchestration

**Import:**
```python
from workflows.tdd_workflow_orchestrator import (
    TDDWorkflowOrchestrator,
    TDDWorkflowConfig
)
```

---

## Configuration

### TDDWorkflowConfig

Configuration dataclass for orchestrator initialization.

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `project_root` | `str` | `"."` | Project root directory path |
| `test_output_dir` | `str` | `"tests"` | Directory for generated test files |
| `session_storage` | `str` | `"cortex-brain/tier2/sessions.db"` | SQLite database path for session persistence |
| `enable_refactoring` | `bool` | `True` | Enable refactoring suggestions |
| `enable_session_tracking` | `bool` | `True` | Enable session save/resume |
| `auto_save_progress` | `bool` | `True` | Auto-save after each phase |
| `refactoring_confidence_threshold` | `float` | `0.75` | Minimum confidence for refactoring suggestions (0.0-1.0) |

**Example:**
```python
config = TDDWorkflowConfig(
    project_root="/path/to/project",
    test_output_dir="tests",
    enable_refactoring=True,
    refactoring_confidence_threshold=0.80
)
```

---

## Core Methods

### `__init__(config: TDDWorkflowConfig)`

Initialize orchestrator with configuration.

**Parameters:**
- `config` (TDDWorkflowConfig): Configuration object

**Initializes:**
- Phase 1 test generators (FunctionTestGenerator, EdgeCaseAnalyzer, DomainKnowledgeIntegrator, ErrorConditionGenerator, ParametrizedTestGenerator)
- Phase 2 workflow components (TDDStateMachine, CodeSmellDetector, RefactoringEngine, PageTracker)

**Example:**
```python
orchestrator = TDDWorkflowOrchestrator(config)
```

---

## Session Management

### `start_session(feature_name: str) -> str`

Start new TDD session.

**Parameters:**
- `feature_name` (str): Name of feature being developed

**Returns:**
- `str`: Session ID (format: `tdd_<uuid>`)

**Side Effects:**
- Creates TDDStateMachine instance
- Creates TDDContext instance
- Saves initial session to PageTracker database

**Example:**
```python
session_id = orchestrator.start_session("user_authentication")
print(f"Started session: {session_id}")
```

---

### `save_progress(location: PageLocation = None, notes: str = "") -> bool`

Save current session progress.

**Parameters:**
- `location` (PageLocation, optional): Current code location
  - `filepath` (str): Absolute file path
  - `line_number` (int): Line number in file
  - `column_offset` (int): Column offset
  - `function_name` (str): Current function name
  - `class_name` (str, optional): Current class name
- `notes` (str, optional): Progress notes

**Returns:**
- `bool`: True if save successful, False otherwise

**Example:**
```python
from workflows.page_tracking import PageLocation

location = PageLocation(
    filepath="src/auth/login.py",
    line_number=45,
    column_offset=4,
    function_name="authenticate_user",
    class_name="AuthService"
)

success = orchestrator.save_progress(
    location=location,
    notes="Completed authentication logic with JWT tokens"
)
```

---

### `resume_session(session_id: str) -> Dict[str, Any]`

Resume existing TDD session.

**Parameters:**
- `session_id` (str): Session ID to resume

**Returns:**
- `Dict[str, Any]`: Session context including:
  - `session_id` (str): Session identifier
  - `feature_name` (str): Feature name
  - `state` (str): Current TDD state (IDLE, RED, GREEN, REFACTOR, DONE, ERROR)
  - `cycle_metrics` (dict): Cycle statistics
  - `last_location` (dict): Last saved code location
    - `file` (str): File path
    - `line` (int): Line number
    - `function` (str): Function name
  - `notes` (str): Last progress notes

**Example:**
```python
resumed = orchestrator.resume_session("tdd_abc123...")

print(f"Resumed: {resumed['feature_name']}")
print(f"State: {resumed['state']}")
print(f"Location: {resumed['last_location']['file']}:{resumed['last_location']['line']}")
print(f"Function: {resumed['last_location']['function']}")
```

---

### `list_active_sessions() -> List[Dict[str, Any]]`

List all active TDD sessions.

**Returns:**
- `List[Dict[str, Any]]`: List of session summaries, each containing:
  - `session_id` (str): Session identifier
  - `feature_name` (str): Feature name
  - `last_updated` (str): Last update timestamp (ISO format)
  - `state` (str): Current state

**Example:**
```python
sessions = orchestrator.list_active_sessions()

for session in sessions:
    print(f"{session['session_id']}: {session['feature_name']} ({session['state']})")
```

---

### `get_session_summary() -> Dict[str, Any]`

Get current session summary with aggregate metrics.

**Returns:**
- `Dict[str, Any]`: Session summary including:
  - `session_id` (str): Session identifier
  - `feature_name` (str): Feature name
  - `total_cycles` (int): Number of RED→GREEN→REFACTOR cycles completed
  - `total_tests_written` (int): Total tests generated across all cycles
  - `total_tests_passing` (int): Total tests passing
  - `test_pass_rate` (float): Percentage of tests passing (0.0-100.0)
  - `total_code_lines_added` (int): Total code lines implemented
  - `total_code_lines_refactored` (int): Total code lines refactored
  - `total_duration_seconds` (float): Total session duration in seconds
  - `current_state` (str): Current TDD state

**Example:**
```python
summary = orchestrator.get_session_summary()

print(f"Feature: {summary['feature_name']}")
print(f"Cycles: {summary['total_cycles']}")
print(f"Tests: {summary['total_tests_passing']}/{summary['total_tests_written']} ({summary['test_pass_rate']:.1f}%)")
print(f"Code lines: {summary['total_code_lines_added']} (+ {summary['total_code_lines_refactored']} refactored)")
```

---

## Workflow Phases

### RED Phase: `generate_tests(source_file: str, function_name: str = None, scenarios: List[str] = None) -> Dict[str, Any]`

Generate comprehensive tests (RED phase of TDD).

**Parameters:**
- `source_file` (str): Absolute path to source file
- `function_name` (str, optional): Specific function to test (if None, generates for all functions)
- `scenarios` (List[str], optional): Test scenarios to generate. Default: all scenarios
  - `"edge_cases"`: Empty strings, None, zero, negative, boundary values
  - `"domain_knowledge"`: Domain-specific patterns (auth, payments, APIs)
  - `"error_conditions"`: ValueError, TypeError, network errors, timeouts
  - `"parametrized"`: Multiple input combinations with pytest.mark.parametrize
  - `"property_based"`: Property-based tests with Hypothesis (if available)

**Returns:**
- `Dict[str, Any]`: Generation results including:
  - `phase` (str): "RED"
  - `test_count` (int): Number of tests generated
  - `test_file` (str): Path to generated test file
  - `tests` (List[dict]): List of generated tests, each with:
    - `test_name` (str): Test function name
    - `scenario_type` (str): Scenario type (edge_cases, domain_knowledge, etc.)
    - `test_code` (str): Generated test code
    - `description` (str): Test description

**Side Effects:**
- Transitions state machine to RED phase
- Writes test file to `test_output_dir`
- Updates cycle metrics (tests_written count)

**Example:**
```python
# Generate all scenarios for specific function
result = orchestrator.generate_tests(
    source_file="src/auth/login.py",
    function_name="authenticate_user",
    scenarios=["edge_cases", "domain_knowledge", "error_conditions"]
)

print(f"Generated {result['test_count']} tests")
print(f"Test file: {result['test_file']}")

for test in result['tests']:
    print(f"  - {test['test_name']} ({test['scenario_type']})")
```

---

### GREEN Phase: `verify_tests_pass(test_results: Dict[str, Any]) -> bool`

Verify tests pass (GREEN phase transition).

**Parameters:**
- `test_results` (Dict[str, Any]): Test execution results
  - `passed` (int): Number of tests passing
  - `failed` (int, optional): Number of tests failing (default: 0)
  - `code_lines` (int): Number of code lines added to make tests pass

**Returns:**
- `bool`: True if all tests pass, False otherwise

**Side Effects:**
- Transitions state machine from RED to GREEN phase
- Records metrics (tests_passing, code_lines_added)
- Updates cycle metrics

**Raises:**
- `ValueError`: If called before RED phase or if tests not all passing

**Example:**
```python
# After implementing code to make tests pass
test_results = {
    "passed": 24,
    "failed": 0,
    "code_lines": 85
}

if orchestrator.verify_tests_pass(test_results):
    print("✅ GREEN phase complete - all tests passing!")
else:
    print("❌ Tests still failing - continue implementation")
```

---

### REFACTOR Phase: `suggest_refactorings(source_file: str) -> List[Dict[str, Any]]`

Get refactoring suggestions (REFACTOR phase).

**Parameters:**
- `source_file` (str): Absolute path to source file

**Returns:**
- `List[Dict[str, Any]]`: Refactoring suggestions, each containing:
  - `type` (str): Refactoring type
    - `"extract_method"`: Extract long method into smaller methods
    - `"simplify_conditional"`: Simplify complex conditional logic
    - `"remove_duplication"`: Remove duplicate code
    - `"rename"`: Rename for clarity
    - `"extract_class"`: Extract responsibility into new class
  - `description` (str): Human-readable description
  - `confidence` (float): Confidence score (0.0-1.0)
  - `effort` (str): Estimated effort ("low", "medium", "high")
  - `code_before` (str): Original code snippet
  - `code_after` (str): Refactored code snippet
  - `line_number` (int): Starting line number
  - `smell_type` (str): Code smell detected (if applicable)
    - `"long_method"`: Method exceeds line threshold
    - `"complex_conditional"`: Nested conditionals >3 levels
    - `"duplicate_code"`: Similar code blocks detected
    - `"long_parameter_list"`: >5 parameters
    - `"god_class"`: Class with >20 methods

**Side Effects:**
- Transitions state machine to REFACTOR phase
- Runs CodeSmellDetector on source file
- Generates refactoring suggestions via RefactoringEngine
- Filters suggestions by confidence threshold

**Example:**
```python
suggestions = orchestrator.suggest_refactorings("src/auth/login.py")

for suggestion in suggestions:
    print(f"\n{suggestion['type'].upper()}: {suggestion['description']}")
    print(f"Confidence: {suggestion['confidence']:.2f} | Effort: {suggestion['effort']}")
    print(f"\nBefore (line {suggestion['line_number']}):")
    print(suggestion['code_before'])
    print(f"\nAfter:")
    print(suggestion['code_after'])
```

---

### `complete_refactor_phase(lines_refactored: int, iterations: int = 1) -> None`

Complete refactoring phase and record metrics.

**Parameters:**
- `lines_refactored` (int): Number of code lines refactored
- `iterations` (int, optional): Number of refactoring iterations (default: 1)

**Side Effects:**
- Records refactoring metrics in state machine
- Updates cycle metrics (code_lines_refactored)

**Example:**
```python
# After applying refactorings
orchestrator.complete_refactor_phase(
    lines_refactored=25,
    iterations=2
)
```

---

### `complete_cycle() -> Dict[str, Any]`

Complete current TDD cycle and get metrics.

**Returns:**
- `Dict[str, Any]`: Cycle metrics including:
  - `cycle_number` (int): Cycle number
  - `tests_written` (int): Tests generated in this cycle
  - `tests_passing` (int): Tests passing in this cycle
  - `code_lines_added` (int): Code lines added
  - `code_lines_refactored` (int): Code lines refactored
  - `duration_seconds` (float): Cycle duration in seconds

**Side Effects:**
- Transitions state machine to DONE state
- Records cycle completion timestamp
- Increments cycle counter

**Example:**
```python
metrics = orchestrator.complete_cycle()

print(f"✅ Cycle {metrics['cycle_number']} complete!")
print(f"Tests: {metrics['tests_passing']}/{metrics['tests_written']} passing")
print(f"Code: +{metrics['code_lines_added']} lines, ~{metrics['code_lines_refactored']} refactored")
print(f"Duration: {metrics['duration_seconds']:.1f}s")
```

---

## Return Types

### PageLocation

Code location dataclass for session tracking.

**Fields:**
- `filepath` (str): Absolute file path
- `line_number` (int): Line number in file
- `column_offset` (int): Column offset
- `function_name` (str): Function name at location
- `class_name` (str, optional): Class name at location

**Example:**
```python
from workflows.page_tracking import PageLocation

location = PageLocation(
    filepath="/path/to/src/auth/login.py",
    line_number=45,
    column_offset=4,
    function_name="authenticate_user",
    class_name="AuthService"
)
```

---

## Error Handling

### Common Exceptions

**ValueError:**
- `verify_tests_pass()` called before `generate_tests()` (not in RED phase)
- `verify_tests_pass()` called with failing tests
- Invalid session ID in `resume_session()`

**FileNotFoundError:**
- Source file not found in `generate_tests()` or `suggest_refactorings()`

**SQLite Errors:**
- Database connection failures (session storage)
- Handled gracefully with fallback to in-memory storage

**Example Error Handling:**
```python
try:
    orchestrator.verify_tests_pass({"passed": 10, "failed": 2})
except ValueError as e:
    print(f"Cannot verify: {e}")
    print("Fix failing tests and try again")

try:
    orchestrator.resume_session("invalid_id")
except ValueError as e:
    print(f"Session not found: {e}")
    sessions = orchestrator.list_active_sessions()
    print(f"Active sessions: {len(sessions)}")
```

---

## Examples

### Complete TDD Workflow

```python
from workflows.tdd_workflow_orchestrator import (
    TDDWorkflowOrchestrator,
    TDDWorkflowConfig
)
from workflows.page_tracking import PageLocation

# 1. Initialize
config = TDDWorkflowConfig(
    project_root="/path/to/project",
    enable_refactoring=True
)
orchestrator = TDDWorkflowOrchestrator(config)

# 2. Start session
session_id = orchestrator.start_session("user_authentication")

# 3. RED: Generate tests
tests = orchestrator.generate_tests(
    source_file="src/auth/login.py",
    function_name="authenticate_user",
    scenarios=["edge_cases", "domain_knowledge", "error_conditions"]
)
print(f"Generated {tests['test_count']} tests")

# 4. Implement code (manual)
# ... write code to make tests pass ...

# 5. GREEN: Verify tests pass
orchestrator.verify_tests_pass({
    "passed": 24,
    "failed": 0,
    "code_lines": 85
})

# 6. REFACTOR: Get suggestions
suggestions = orchestrator.suggest_refactorings("src/auth/login.py")
for s in suggestions:
    print(f"{s['type']}: {s['description']}")

# 7. Apply refactorings (manual)
# ... refactor code ...

orchestrator.complete_refactor_phase(lines_refactored=25)

# 8. Complete cycle
metrics = orchestrator.complete_cycle()
print(f"Cycle {metrics['cycle_number']} complete!")

# 9. Save progress
location = PageLocation(
    filepath="src/auth/login.py",
    line_number=45,
    function_name="authenticate_user"
)
orchestrator.save_progress(location, "Completed authentication with JWT")

# 10. Get summary
summary = orchestrator.get_session_summary()
print(f"Total cycles: {summary['total_cycles']}")
print(f"Test pass rate: {summary['test_pass_rate']:.1f}%")
```

---

### Resume Existing Session

```python
# List active sessions
sessions = orchestrator.list_active_sessions()
print(f"Found {len(sessions)} active sessions")

for session in sessions:
    print(f"- {session['session_id']}: {session['feature_name']}")

# Resume specific session
resumed = orchestrator.resume_session(sessions[0]['session_id'])

print(f"Resumed: {resumed['feature_name']}")
print(f"State: {resumed['state']}")
print(f"Last location: {resumed['last_location']['file']}:{resumed['last_location']['line']}")

# Continue TDD workflow from last state
if resumed['state'] == 'RED':
    # Tests generated, need implementation
    pass
elif resumed['state'] == 'GREEN':
    # Tests passing, need refactoring
    suggestions = orchestrator.suggest_refactorings(resumed['last_location']['file'])
```

---

## See Also

- **Quick Start Guide:** `cortex-brain/documents/implementation-guides/QUICK-START.md`
- **User Authentication Example:** `EXAMPLE-1-USER-AUTHENTICATION.md`
- **Payment Processing Example:** `EXAMPLE-2-PAYMENT-PROCESSING.md`
- **REST API Example:** `EXAMPLE-3-REST-API.md`
- **Phase 3 Validation Report:** `TDD-MASTERY-PHASE-3-FINAL-VALIDATION.md`

---

**Author:** Asif Hussain  
**Date:** 2025-11-23  
**Version:** 1.0
