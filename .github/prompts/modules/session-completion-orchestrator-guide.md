# Session Completion Orchestrator Guide

**Purpose:** Comprehensive TDD session validation with metrics comparison and SKULL rule enforcement

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

---

## Overview

The Session Completion Orchestrator provides end-to-end validation when completing a TDD session, including full test suite execution, metrics comparison, git diff analysis, and SKULL rule validation.

**Key Features:**
- **Full Test Suite Execution:** Runs all tests (unit, integration, end-to-end)
- **Metrics Comparison:** Before/after comparison (test count, pass rate, coverage)
- **SKULL Rule Validation:** Enforces 22 brain protection rules
- **Git Diff Summary:** Shows changes made during session
- **Multi-Language Support:** .NET, Python, JavaScript test frameworks
- **Completion Report:** Comprehensive session summary with recommendations

---

## Usage

### Basic Usage

```python
from src.orchestrators.session_completion_orchestrator import SessionCompletionOrchestrator

# Initialize with session context
orchestrator = SessionCompletionOrchestrator(
    session_id="auth-feature-123",
    project_root="/path/to/project"
)

# Complete session with full validation
result = orchestrator.complete_session(
    start_metrics={'tests': 45, 'passed': 42, 'coverage': 78.5},
    end_metrics={'tests': 52, 'passed': 52, 'coverage': 85.2}
)

# Generate completion report
report = orchestrator.generate_completion_report(result)
print(report)
```

### Natural Language Commands

**Commands:**
- `complete session` or `finish session` - Complete TDD session with validation
- `session report` - Generate session completion report
- `end session` - Alias for complete session

**Examples:**
```
User: "complete session with full validation"
CORTEX: Running session completion validation...
        ✅ Full test suite: 52/52 tests passed
        ✅ SKULL rules: 22/22 validated
        ✅ Coverage increased: 78.5% → 85.2% (+6.7%)
        ✅ Git changes: 8 files modified, 247 insertions, 53 deletions
        
        Session completed successfully. Report saved to:
        cortex-brain/documents/reports/SESSION-auth-feature-123.md
```

---

## API Reference

### Class: `SessionCompletionOrchestrator`

Orchestrates comprehensive validation at TDD session completion.

#### Methods

**`__init__(session_id: str, project_root: str = None)`**

Initialize session completion orchestrator.

**Parameters:**
- `session_id` (str): Unique identifier for TDD session
- `project_root` (str, optional): Path to project root. Auto-detected if not provided.

**Returns:**
- `SessionCompletionOrchestrator`: Initialized orchestrator instance

---

**`complete_session(start_metrics: dict, end_metrics: dict) -> dict`**

Complete TDD session with full validation suite.

**Parameters:**
- `start_metrics` (dict): Session start metrics `{'tests': int, 'passed': int, 'coverage': float}`
- `end_metrics` (dict): Session end metrics (same structure)

**Returns:**
- `dict`: Completion result with structure:
  ```python
  {
      'session_id': 'auth-feature-123',
      'test_results': {...},
      'metrics_comparison': {...},
      'skull_validation': {...},
      'git_diff': {...},
      'success': bool,
      'report_path': 'cortex-brain/documents/reports/SESSION-*.md'
  }
  ```

---

**`run_full_test_suite() -> dict`**

Execute complete test suite across all project types.

**Parameters:**
- None

**Returns:**
- `dict`: Test results `{'total': int, 'passed': int, 'failed': int, 'skipped': int, 'duration': float}`

---

**`calculate_metrics_comparison(start: dict, end: dict) -> dict`**

Compare before/after session metrics.

**Parameters:**
- `start` (dict): Start metrics
- `end` (dict): End metrics

**Returns:**
- `dict`: Comparison with deltas and percentages

---

**`validate_skull_rules() -> dict`**

Validate all 22 SKULL brain protection rules.

**Parameters:**
- None

**Returns:**
- `dict`: Validation results `{'passed': int, 'failed': int, 'violations': [...]}`

---

**`generate_diff_summary() -> dict`**

Generate git diff summary for session changes.

**Parameters:**
- None

**Returns:**
- `dict`: Diff summary `{'files_changed': int, 'insertions': int, 'deletions': int, 'files': [...]}`

---

**`generate_completion_report(result: dict) -> str`**

Generate human-readable session completion report.

**Parameters:**
- `result` (dict): Result from complete_session()

**Returns:**
- `str`: Formatted markdown report

---

### Language-Specific Test Execution

**`_is_dotnet_project() -> bool`**

Detect if project uses .NET (.csproj, .sln files).

**`_is_python_project() -> bool`**

Detect if project uses Python (requirements.txt, setup.py).

**`_is_javascript_project() -> bool`**

Detect if project uses JavaScript (package.json, jest.config.js).

**`_run_dotnet_tests() -> dict`**

Run `dotnet test` with coverage collection.

**`_run_python_tests() -> dict`**

Run `pytest` with coverage (pytest-cov).

**`_run_javascript_tests() -> dict`**

Run `npm test` (Jest/Mocha/Jasmine)

---

## Configuration

**cortex.config.json:**

```json
{
  "session_completion": {
    "run_full_test_suite": true,
    "validate_skull_rules": true,
    "generate_git_diff": true,
    "require_coverage_increase": false,
    "min_coverage_delta": 0.0,
    "fail_on_test_failures": true,
    "report_location": "cortex-brain/documents/reports/"
  }
}
```

**Required Tools:**
- Git (for diff generation)
- Test frameworks (.NET: xunit/nunit, Python: pytest, JavaScript: jest/mocha)
- Coverage tools (.NET: coverlet, Python: pytest-cov, JavaScript: nyc/istanbul)

---

## Examples

### Example 1: Complete TDD Session

```python
from src.orchestrators.session_completion_orchestrator import SessionCompletionOrchestrator

# Initialize session
orchestrator = SessionCompletionOrchestrator(
    session_id="user-auth-session",
    project_root="/home/user/myapp"
)

# Capture start metrics
start_metrics = {
    'tests': 45,
    'passed': 42,
    'coverage': 78.5
}

# ... TDD work happens here ...

# Capture end metrics
end_metrics = {
    'tests': 52,
    'passed': 52,
    'coverage': 85.2
}

# Complete session
result = orchestrator.complete_session(start_metrics, end_metrics)

if result['success']:
    print(f"✅ Session completed. Report: {result['report_path']}")
else:
    print(f"❌ Session validation failed: {result.get('errors', [])}")
```

**Output:**
```
🎯 Session Completion Validation

Test Suite Execution:
  ✅ Total Tests: 52 (was 45, +7 new tests)
  ✅ Pass Rate: 100% (was 93.3%, +6.7%)
  ✅ Duration: 12.4s

Metrics Comparison:
  ✅ Coverage: 85.2% (was 78.5%, +6.7%)
  ✅ Tests Added: 7
  ✅ Tests Fixed: 3

SKULL Rule Validation:
  ✅ 22/22 rules passed

Git Changes:
  📝 Files Modified: 8
  ➕ Insertions: 247 lines
  ➖ Deletions: 53 lines

✅ Session completed successfully
   Report saved to: cortex-brain/documents/reports/SESSION-user-auth-session.md
```

### Example 2: Integrated with TDD Workflow

```python
from src.workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator
from src.orchestrators.session_completion_orchestrator import SessionCompletionOrchestrator

# Start TDD session
tdd = TDDWorkflowOrchestrator()
session_id = tdd.start_session("payment-integration")

# Capture start metrics
start = tdd.get_current_metrics()

# RED → GREEN → REFACTOR cycles
tdd.write_failing_test("test_payment_processing")
tdd.implement_feature()
tdd.refactor()

# Complete session
completion = SessionCompletionOrchestrator(session_id)
result = completion.complete_session(
    start_metrics=start,
    end_metrics=tdd.get_current_metrics()
)
```

---

## Integration

**Entry Points:**
- `complete session` - Natural language command
- `finish session` - Alias for session completion
- `end session` - Another alias
- TDD Workflow (automatic after REFACTOR phase)

**Dependencies:**
- Git (for diff generation)
- Test frameworks (language-specific)
- Coverage tools (for metrics)
- Brain Protector (for SKULL rule validation)

**Response Template:**
- Template ID: `session_completion`
- Triggers: `complete session`, `finish session`, `session report`

**See Also:**
- TDD Workflow Orchestrator Guide
- Lint Validation Orchestrator Guide (runs during session)
- Brain Protector Rules (SKULL validation)

---

## Troubleshooting

**Issue:** "Test suite failed to execute"  
**Solution:** Verify test framework installed and project structure correct. Check logs in `cortex-brain/logs/session-completion.log`.

**Issue:** "SKULL rule validation failed"  
**Solution:** Review failed rules in report. Common violations:
- Brain database modified directly (use Brain API)
- Documents created in repository root (use cortex-brain/documents/)
- Missing copyright headers (add to new files)

**Issue:** "Git diff generation failed"  
**Solution:** Ensure git repository initialized and commits exist. Run `git status` to verify working directory state.

**Issue:** "Coverage metrics unavailable"  
**Solution:** Install coverage tool for your language:
- .NET: `dotnet add package coverlet.collector`
- Python: `pip install pytest-cov`
- JavaScript: `npm install --save-dev nyc`

**Issue:** "Session metrics comparison shows negative delta"  
**Solution:** This indicates tests were removed or coverage decreased. Review git diff to understand changes. Configure `require_coverage_increase: false` to allow this.

---

**Last Updated:** November 25, 2025  
**Version:** 1.0
