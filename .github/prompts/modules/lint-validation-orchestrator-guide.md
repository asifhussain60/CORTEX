# Lint Validation Orchestrator Guide

**Purpose:** Multi-language code quality validation with severity mapping and TDD integration

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

---

## Overview

The Lint Validation Orchestrator provides automated code quality validation across multiple programming languages with intelligent severity mapping and TDD workflow integration.

**Key Features:**
- **Multi-Language Support:** .NET (Roslynator), Python (Pylint), JavaScript (ESLint)
- **Severity Mapping:** Critical, Warning, Info levels with customizable thresholds
- **Phase Blocking:** Prevents TDD phase progression on critical violations
- **Configurable Rules:** Per-project configuration via cortex.config.json
- **Detailed Reports:** Violation summaries with file/line locations

---

## Usage

### Basic Usage

```python
from src.orchestrators.lint_validation_orchestrator import LintValidationOrchestrator

# Initialize with project root
orchestrator = LintValidationOrchestrator(project_root="/path/to/project")

# Validate all supported languages
result = orchestrator.validate()

# Check if critical violations block TDD phase
if orchestrator.should_block_phase(result):
    print("❌ Critical violations detected - fix before continuing")
else:
    print("✅ Code quality checks passed")
```

### Natural Language Commands

**Commands:**
- `validate lint` or `check code quality` - Run lint validation
- `lint validation` - Full validation with detailed report
- `run linter` - Execute linting for detected project types

**Examples:**
```
User: "validate lint before moving to GREEN phase"
CORTEX: Running code quality validation...
        ✅ .NET: 0 critical, 3 warnings
        ✅ Python: 0 critical, 1 warning
        Status: PASS - No blocking violations
```

---

## API Reference

### Class: `LintValidationOrchestrator`

Orchestrates code quality validation across multiple programming languages.

#### Methods

**`__init__(project_root: str = None, config: dict = None)`**

Initialize lint validation orchestrator.

**Parameters:**
- `project_root` (str, optional): Path to project root. Auto-detected if not provided.
- `config` (dict, optional): Configuration overrides. Loaded from cortex.config.json by default.

**Returns:**
- `LintValidationOrchestrator`: Initialized orchestrator instance

---

**`validate() -> dict`**

Run lint validation for all detected project types.

**Parameters:**
- None

**Returns:**
- `dict`: Validation results with structure:
  ```python
  {
      'dotnet': {'critical': 0, 'warning': 3, 'info': 5, 'violations': [...]},
      'python': {'critical': 0, 'warning': 1, 'info': 2, 'violations': [...]},
      'javascript': {'critical': 0, 'warning': 0, 'info': 1, 'violations': [...]},
      'total_critical': 0,
      'total_warnings': 4,
      'total_info': 8
  }
  ```

---

**`should_block_phase(validation_result: dict) -> bool`**

Determine if critical violations should block TDD phase progression.

**Parameters:**
- `validation_result` (dict): Result from validate() method

**Returns:**
- `bool`: True if critical violations detected, False otherwise

---

**`generate_report(validation_result: dict) -> str`**

Generate human-readable lint validation report.

**Parameters:**
- `validation_result` (dict): Result from validate() method

**Returns:**
- `str`: Formatted markdown report with violations by severity

---

### Language-Specific Validation

**`_validate_dotnet() -> dict`**

Run Roslynator analysis on .NET projects (.csproj, .sln files).

**`_validate_python() -> dict`**

Run Pylint analysis on Python projects (requirements.txt, setup.py).

**`_validate_javascript() -> dict`**

Run ESLint analysis on JavaScript projects (package.json, .eslintrc).

---

### Severity Mapping

**`_map_dotnet_severity(diagnostic: dict) -> str`**

Map Roslynator severity (Error, Warning, Info) to CORTEX severity (critical, warning, info).

**`_map_python_severity(message: dict) -> str`**

Map Pylint message types (error, warning, convention) to CORTEX severity.

**`_map_javascript_severity(message: dict) -> str`**

Map ESLint severity (2=error, 1=warning, 0=off) to CORTEX severity

---

## Configuration

**cortex.config.json:**

```json
{
  "lint_validation": {
    "dotnet": {
      "enabled": true,
      "tool": "roslynator",
      "critical_threshold": 0,
      "warning_threshold": 10
    },
    "python": {
      "enabled": true,
      "tool": "pylint",
      "critical_threshold": 0,
      "warning_threshold": 5
    },
    "javascript": {
      "enabled": true,
      "tool": "eslint",
      "critical_threshold": 0,
      "warning_threshold": 10
    },
    "block_on_critical": true
  }
}
```

**Required Tools:**
- .NET SDK (for Roslynator)
- Python 3.10+ with pylint (`pip install pylint`)
- Node.js with eslint (`npm install -g eslint`)

---

## Examples

### Example 1: TDD RED Phase Validation

```python
from src.orchestrators.lint_validation_orchestrator import LintValidationOrchestrator

# After writing failing test (RED phase)
orchestrator = LintValidationOrchestrator()
result = orchestrator.validate()

if orchestrator.should_block_phase(result):
    print("❌ Fix critical lint violations before implementing")
    report = orchestrator.generate_report(result)
    print(report)
else:
    print("✅ Code quality acceptable - proceed to GREEN phase")
```

**Output:**
```
❌ Fix critical lint violations before implementing

🔍 Lint Validation Report

.NET (Roslynator):
  ❌ Critical: 2
     - CS8618: Non-nullable field must contain a non-null value (UserService.cs:15)
     - CA1062: Validate arguments of public methods (AuthController.cs:42)
  ⚠️  Warnings: 3

Python (Pylint):
  ✅ Critical: 0
  ⚠️  Warnings: 1

🚫 Phase Blocked: Fix 2 critical violations before continuing
```

### Example 2: Integrated with TDD Workflow

```python
from src.workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator
from src.orchestrators.lint_validation_orchestrator import LintValidationOrchestrator

# Initialize TDD workflow with lint validation
tdd = TDDWorkflowOrchestrator(enable_lint_validation=True)
lint = LintValidationOrchestrator()

# RED phase
tdd.write_failing_test("test_user_authentication")

# Validate before GREEN phase
if lint.should_block_phase(lint.validate()):
    print("Fix linting issues first")
else:
    # GREEN phase
    tdd.implement_feature()
```

---

## Integration

**Entry Points:**
- `validate lint` - Natural language command
- `lint validation` - Explicit validation request
- TDD Workflow (automatic between RED and GREEN phases)

**Dependencies:**
- Roslynator (.NET code analysis)
- Pylint (Python linting)
- ESLint (JavaScript linting)
- TDD Workflow Orchestrator (for phase blocking)

**Response Template:**
- Template ID: `lint_validation`
- Triggers: `validate lint`, `check code quality`, `run linter`

**See Also:**
- TDD Workflow Orchestrator Guide
- Session Completion Orchestrator Guide (uses lint validation)
- System Alignment Guide (validates lint integration)

---

## Troubleshooting

**Issue:** "Roslynator not found"  
**Solution:** Install .NET SDK and verify `dotnet --version` works. Roslynator runs via `dotnet format --verify-no-changes`.

**Issue:** "Pylint not installed"  
**Solution:** Run `pip install pylint` in your Python environment. Verify with `pylint --version`.

**Issue:** "ESLint config not found"  
**Solution:** Create `.eslintrc.json` in project root or run `npm init @eslint/config` to generate.

**Issue:** "False positives blocking phase"  
**Solution:** Adjust thresholds in cortex.config.json or add suppression comments:
- .NET: `#pragma warning disable CA1062`
- Python: `# pylint: disable=missing-docstring`
- JavaScript: `/* eslint-disable no-console */`

**Issue:** "Performance slow on large codebases"  
**Solution:** Configure file exclusions in lint config files (.pylintrc, .eslintignore) to skip generated/vendor code.

---

**Last Updated:** November 25, 2025  
**Version:** 1.0
