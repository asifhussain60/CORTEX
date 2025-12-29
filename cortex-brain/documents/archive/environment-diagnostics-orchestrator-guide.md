# Environment Diagnostics Orchestrator - User Guide

**Version:** 1.1.0 (REFACTORED)  
**Author:** Asif Hussain  
**Created:** December 12, 2025  
**Status:** ✅ Production Ready

---

## 🎯 Overview

The Environment Diagnostics Orchestrator validates your development environment before technical work begins, preventing the time waste documented in chat04 (30+ minutes troubleshooting .NET SDK configuration).

**Problem Solved:** Automated pre-flight checks catch environment issues immediately instead of discovering them mid-workflow.

---

## 📋 Features

### Validations

1. **.NET SDK**
   - Version detection
   - Minimum version compatibility
   - PATH configuration
   - Upgrade recommendations

2. **Python**
   - Version detection
   - Virtual environment status
   - Best practice warnings

3. **Node.js**
   - Version detection
   - npm availability
   - Optional validation

4. **Git**
   - Installation check
   - Repository detection
   - User configuration validation

5. **Write Permissions**
   - Output directory access
   - Automatic directory creation
   - Platform-specific remediation

### Key Benefits

- ⚡ **Fast**: <2 second execution time
- 🔍 **Comprehensive**: 5 critical environment checks
- 🛠️ **Actionable**: Platform-specific remediation guides
- 🧪 **TDD-Ready**: Validates test infrastructure before TDD workflow
- 🌍 **Cross-Platform**: Windows, Mac, Linux support

---

## 🚀 Quick Start

### Basic Usage

```python
from src.orchestrators.environment_diagnostics_orchestrator import (
    EnvironmentDiagnosticsOrchestrator
)

# Create orchestrator
orchestrator = EnvironmentDiagnosticsOrchestrator()

# Run full diagnostics
result = orchestrator.run_full_diagnostics()

# Check status
if result.status == CheckStatus.BLOCKED:
    print("❌ Critical issues found:")
    print(result.remediation_guide)
elif result.status == CheckStatus.WARNING:
    print("⚠️  Warnings (non-blocking):")
    for warning in result.recommendations:
        print(f"  - {warning}")
else:
    print("✅ Environment ready!")
```

### TDD Workflow Integration

```python
# Validate before starting TDD
result = orchestrator.validate_for_tdd_workflow()

if not result.test_framework_ready:
    print("Cannot start TDD - environment not ready")
    print(result.remediation_guide)
    exit(1)

# Proceed with TDD workflow
print("✅ TDD environment validated - starting RED phase")
```

### Individual Checks

```python
# Check .NET SDK (minimum version 8.0)
dotnet_result = orchestrator.validate_dotnet_sdk(min_version="8.0")
if dotnet_result.status == CheckStatus.WARNING:
    print(f"⚠️  {dotnet_result.message}")
    print(f"Remediation: {dotnet_result.remediation}")

# Check Python with venv awareness
python_result = orchestrator.validate_python()
if not python_result.venv_active:
    print("⚠️  Virtual environment not active")

# Check Node.js (optional)
nodejs_result = orchestrator.validate_nodejs(required=False)
if nodejs_result.status == CheckStatus.SKIPPED:
    print("Node.js not required - skipped")

# Check Git
git_result = orchestrator.validate_git()
if not git_result.is_git_repo:
    print("⚠️  Not in a git repository")

# Check write permissions
perm_result = orchestrator.validate_write_permissions(
    directories=["./output", "./logs"],
    create_if_missing=True
)
```

---

## 📊 Output Format

### DiagnosticsResult Structure

```python
@dataclass
class DiagnosticsResult:
    status: CheckStatus              # PASS | WARNING | BLOCKED
    summary: str                     # Human-readable summary
    details: List[ValidationResult]  # Individual check results
    recommendations: List[str]       # Non-blocking recommendations
    blocking_issues: List[str]       # Critical issues
    failed_checks: List[str]         # Check names that failed
    remediation_guide: Optional[str] # Full remediation guide
    
    # TDD-specific
    test_framework_ready: bool
    test_runner_available: bool
    dependencies_installed: bool
```

### CheckStatus Values

- **PASS**: Check passed, no issues
- **WARNING**: Non-critical issue, work can continue
- **BLOCKED**: Critical issue, work cannot proceed
- **SKIPPED**: Check not required for this project

---

## 🛠️ Configuration

### Minimum Versions

```python
# .NET SDK - adjust based on project requirements
orchestrator.validate_dotnet_sdk(min_version="8.0")  # Default: 6.0

# Python - always uses detected version
orchestrator.validate_python()

# Node.js - make optional if not needed
orchestrator.validate_nodejs(required=False)
```

### Directory Permissions

```python
# Specify directories to validate
orchestrator.validate_write_permissions(
    directories=[
        "./output",
        "./logs",
        "./test-results",
        "./coverage"
    ],
    create_if_missing=True  # Auto-create if missing
)
```

---

## 🏗️ Architecture (SOLID Principles)

### Validator Pattern

The orchestrator uses a **validator pattern** following SOLID principles:

```
EnvironmentDiagnosticsOrchestrator (Coordinator)
    ↓
BaseValidator (Abstract)
    ↓
    ├── DotNetValidator
    ├── PythonValidator
    ├── NodeJsValidator
    └── GitValidator
```

### Adding Custom Validators

1. **Create Validator Class**

```python
from src.orchestrators.validators import BaseValidator, ValidatorResult

class RustValidator(BaseValidator):
    def get_command(self) -> str:
        return "rustc"
    
    def get_version_args(self) -> list:
        return ["--version"]
    
    def parse_version(self, output: str) -> str:
        # Parse "rustc 1.70.0 (abc123 2023-06-01)"
        return output.split()[1]
    
    def get_name(self) -> str:
        return "Rust"
    
    def additional_validation(self, version: str, **kwargs):
        # Optional: check cargo, etc.
        return (True, "", {})
```

2. **Register in Orchestrator**

```python
class EnvironmentDiagnosticsOrchestrator:
    def __init__(self):
        # ... existing validators
        self.rust_validator = RustValidator()
    
    def validate_rust(self) -> ValidationResult:
        validator_result = self.rust_validator.validate()
        # Convert to ValidationResult
        return ValidationResult(...)
```

### Benefits of This Architecture

- ✅ **Single Responsibility**: Each validator handles one runtime
- ✅ **Open/Closed**: Add validators without modifying existing code
- ✅ **Liskov Substitution**: All validators interchangeable
- ✅ **Interface Segregation**: Minimal required methods
- ✅ **Dependency Inversion**: Orchestrator depends on abstraction

---

## 🧪 Testing

### Run Tests

```bash
# All tests (22 tests, 100% passing)
pytest tests/orchestrators/test_environment_diagnostics_orchestrator.py -v

# With coverage
pytest tests/orchestrators/test_environment_diagnostics_orchestrator.py \
    --cov=src/orchestrators/environment_diagnostics_orchestrator \
    --cov-report=term-missing

# Performance test only
pytest tests/orchestrators/test_environment_diagnostics_orchestrator.py::test_environment_diagnostics_execution_time_under_2_seconds -v
```

### Test Coverage

- **22 tests** covering all validation scenarios
- **100% passing** rate
- **<0.5s** execution time
- Platform-specific remediation testing

---

## 🌍 Cross-Platform Support

### Platform Detection

The orchestrator automatically detects the platform and provides appropriate remediation:

```python
import platform

# Automatically detected
orchestrator = EnvironmentDiagnosticsOrchestrator()
print(f"Platform: {orchestrator.platform}")  # "Windows" | "Darwin" | "Linux"
```

### Platform-Specific Remediation

**Windows:**
```
Install .NET SDK:
1. Download from https://dotnet.microsoft.com/download
2. Run installer (.exe)
3. Restart terminal
4. Verify: dotnet --version
5. Add to PATH if needed: Control Panel → System → Environment Variables
```

**Mac/Linux:**
```
Install .NET SDK:
1. Download from https://dotnet.microsoft.com/download
2. For Mac: Use installer or 'brew install dotnet'
3. For Linux: Follow distribution-specific instructions
4. Verify: dotnet --version
5. Add to PATH if needed: export PATH="$PATH:/usr/local/share/dotnet"
```

---

## 📖 API Reference

### EnvironmentDiagnosticsOrchestrator

**Methods:**

- `validate_dotnet_sdk(min_version: str = "6.0") -> ValidationResult`
- `validate_python() -> ValidationResult`
- `validate_nodejs(required: bool = True) -> ValidationResult`
- `validate_git() -> ValidationResult`
- `validate_write_permissions(directories: List[str], create_if_missing: bool = True) -> ValidationResult`
- `run_full_diagnostics() -> DiagnosticsResult`
- `validate_for_tdd_workflow() -> DiagnosticsResult`
- `generate_remediation(check_name: str) -> str`

### BaseValidator (Abstract)

**Abstract Methods:**
- `get_command() -> str`
- `get_version_args() -> list`
- `parse_version(output: str) -> str`
- `get_name() -> str`

**Template Method:**
- `validate(**kwargs) -> ValidatorResult`

**Hooks:**
- `additional_validation(version: str, **kwargs) -> Tuple[bool, str, dict]`

**Helper:**
- `run_command(args: list, timeout: int = 5) -> Tuple[bool, str, str]`

---

## 💡 Best Practices

### 1. Run Before Technical Work

```python
# At start of any technical workflow
result = orchestrator.run_full_diagnostics()
if result.status == CheckStatus.BLOCKED:
    handle_blockers(result)
    exit(1)
```

### 2. Cache Results

```python
# Cache for session (environment rarely changes)
_diagnostics_cache = None

def get_diagnostics():
    global _diagnostics_cache
    if _diagnostics_cache is None:
        orchestrator = EnvironmentDiagnosticsOrchestrator()
        _diagnostics_cache = orchestrator.run_full_diagnostics()
    return _diagnostics_cache
```

### 3. Integrate with CI/CD

```yaml
# GitHub Actions example
- name: Validate Environment
  run: |
    python -c "
    from src.orchestrators.environment_diagnostics_orchestrator import EnvironmentDiagnosticsOrchestrator
    result = EnvironmentDiagnosticsOrchestrator().run_full_diagnostics()
    if result.status == 'blocked':
        print(result.remediation_guide)
        exit(1)
    "
```

### 4. Log Results

```python
import logging

result = orchestrator.run_full_diagnostics()
logging.info(f"Environment diagnostics: {result.summary}")

for detail in result.details:
    logging.debug(f"{detail.check_name}: {detail.status.value} - {detail.message}")
```

---

## 🐛 Troubleshooting

### Issue: "dotnet not found in PATH"

**Solution:**
```bash
# Mac
brew install dotnet

# Or download from https://dotnet.microsoft.com/download
# Verify installation
dotnet --version

# If still not found, add to PATH:
export PATH="$PATH:/usr/local/share/dotnet"
```

### Issue: "Python detected but no virtual environment active"

**Solution:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Verify
python -c "import sys; print(sys.prefix)"
```

### Issue: "Permission denied for ./output"

**Solution:**
```bash
# Mac/Linux
chmod 755 ./output

# Or change ownership
sudo chown -R $USER ./output

# Windows (PowerShell as Admin)
icacls .\output /grant Users:F
```

---

## 📚 Related Documentation

- [Planning System Enhancement Plan](../planning/orchestrator-enhancement-plan-v1.md)
- [Copilot Chat Analysis](../analysis/copilot-chat-analysis-2025-12-12.md)
- [Brain Protection Rules](../../brain-protection-rules.yaml)
- [TDD Mastery Orchestrator](../../operations/tdd-mastery/)

---

## 📝 Changelog

### Version 1.1.0 (2025-12-12) - REFACTORED

- ✅ Extracted validator pattern (SOLID principles)
- ✅ Created BaseValidator abstract class
- ✅ Separated concerns: DotNetValidator, PythonValidator, NodeJsValidator, GitValidator
- ✅ Improved performance: 0.41s → 0.38s (7% faster)
- ✅ Maintained 100% test coverage (22/22 tests passing)
- ✅ Enhanced extensibility (easy to add new validators)

### Version 1.0.0 (2025-12-12) - INITIAL RELEASE

- ✅ RED→GREEN→REFACTOR TDD cycle complete
- ✅ 22 comprehensive tests (100% passing)
- ✅ 5 environment validations (.NET, Python, Node, Git, Permissions)
- ✅ Cross-platform support (Windows, Mac, Linux)
- ✅ Platform-specific remediation guides
- ✅ TDD workflow integration
- ✅ <2 second execution time

---

## 🤝 Contributing

To add a new validator:

1. Create validator class extending `BaseValidator`
2. Implement required abstract methods
3. Add validation method to orchestrator
4. Write tests (RED→GREEN→REFACTOR)
5. Update this documentation
6. Submit PR with git checkpoint

---

**Questions?** Contact Asif Hussain or see [CORTEX Documentation](../../README.md)
