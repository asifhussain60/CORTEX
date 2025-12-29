# Test Failure Analyzer User Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 13, 2025  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The **Test Failure Analyzer** is a utility that parses test framework output (pytest, unittest), classifies failures by root cause, and provides actionable mitigation strategies. Designed for **TDD Workflow** integration, it enables strategic test failure deferral while ensuring critical issues block progress.

### Key Features

- **Test Output Parsing:** Extracts structured data from pytest/unittest output
- **Failure Classification:** 6 types (ARCHITECTURAL, TEST_EXPECTATION, LOGIC_BUG, ENVIRONMENT, SYNTAX, UNKNOWN)
- **Severity Determination:** 4 levels (CRITICAL, HIGH, MEDIUM, LOW)
- **Strategic Deferral:** Allow non-critical failures to be deferred, critical failures block
- **Root Cause Analysis:** Pattern-based analysis of error messages and tracebacks
- **Mitigation Strategies:** Actionable fix suggestions per failure type
- **Failure Tracking:** Track deferred failures (must be 0 at 100% completion)

---

## 🚀 Quick Start

### Basic Usage

```python
from src.operations.utilities.test_failure_analyzer import (
    TestFailureAnalyzer,
    analyze_pytest_output
)

# Analyze pytest output
test_output = """
============================= test session starts ==============================
collected 10 items

tests/test_sample.py::test_addition PASSED
tests/test_sample.py::test_subtraction FAILED

======================== 2 failed, 8 passed in 1.20s ==========================
"""

result = analyze_pytest_output(test_output)

print(f"Pass Rate: {result.pass_rate:.1f}%")
print(f"Critical Failures: {len(result.critical_failures)}")
print(f"Deferrable: {len(result.deferrable_failures)}")
```

### Generate Failure Report

```python
analyzer = TestFailureAnalyzer()
result = analyzer.analyze(test_output, "pytest")

# Generate detailed report
report = analyzer.generate_failure_report(result)
print(report)
```

### Strategic Deferral

```python
analyzer = TestFailureAnalyzer()
result = analyzer.analyze(test_output, "pytest")

# Defer non-critical failures
for failure in result.deferrable_failures:
    if analyzer.defer_failure(failure):
        print(f"Deferred: {failure.test_name}")

# Check deferred count (must be 0 at completion)
print(f"Deferred count: {analyzer.get_deferred_count()}")
```

---

## 📋 Failure Classification System

### Failure Types

| Type | Description | Can Defer? | Blocks Progress? |
|------|-------------|------------|------------------|
| **ARCHITECTURAL** | Design issues, circular imports | ❌ No | ✅ Yes |
| **TEST_EXPECTATION** | Wrong assertions, test setup | ✅ Yes | ❌ No |
| **LOGIC_BUG** | TypeError, ValueError, logic errors | ✅ Yes* | ❌ No* |
| **ENVIRONMENT** | Missing deps, connection errors | ❌ No | ✅ Yes |
| **SYNTAX** | SyntaxError, import errors | ❌ No | ✅ Yes |
| **UNKNOWN** | Unclassified errors | ❌ No | ⚠️ Maybe |

*Logic bugs can be deferred if severity is not CRITICAL

### Severity Levels

| Severity | Description | Action |
|----------|-------------|--------|
| **CRITICAL** | Blocks all progress | Must fix immediately |
| **HIGH** | Significant issue | Fix soon |
| **MEDIUM** | Moderate issue | Can defer strategically |
| **LOW** | Minor issue | Can defer |

### Classification Patterns

**ARCHITECTURAL:**
- `circular import`
- `design violation`
- `interface mismatch`
- `dependency cycle`

**TEST_EXPECTATION:**
- `AssertionError`
- `expected.*but got`
- `assert.*==.*failed`

**LOGIC_BUG:**
- `TypeError`
- `AttributeError`
- `ValueError`
- `KeyError`
- `IndexError`

**ENVIRONMENT:**
- `ModuleNotFoundError`
- `ImportError`
- `ConnectionError`
- `PermissionError`
- `FileNotFoundError`

**SYNTAX:**
- `SyntaxError`
- `IndentationError`
- `NameError`

---

## 🔧 Core Components

### 1. TestOutputParser

Parses pytest/unittest output into structured data.

```python
from src.operations.utilities.test_failure_analyzer import TestOutputParser

parser = TestOutputParser(test_output, framework="pytest")
result = parser.parse()

print(f"Total: {result.total_tests}")
print(f"Passed: {result.passed}")
print(f"Failed: {result.failed}")
print(f"Pass Rate: {result.pass_rate}%")

for failure in result.failures:
    print(f"- {failure.test_name}: {failure.failure_type.value}")
```

**Methods:**
- `parse()` → `TestRunResult` - Parse output into structured result
- `_parse_pytest()` - Pytest-specific parsing
- `_parse_unittest()` - Unittest parsing (coming soon)
- `_extract_pytest_failures()` - Extract failure details from FAILURES section
- `_classify_failure()` - Classify individual failure
- `_determine_severity()` - Determine failure severity
- `_generate_mitigation()` - Generate mitigation strategy
- `_analyze_root_cause()` - Perform root cause analysis

### 2. FailureClassifier

Pattern-based failure classification engine.

```python
from src.operations.utilities.test_failure_analyzer import FailureClassifier

classifier = FailureClassifier()

message = "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
traceback = "line 42: result = 5 + 'hello'"

failure_type, confidence = classifier.classify(message, traceback)

print(f"Type: {failure_type.value}")
print(f"Confidence: {confidence:.0%}")
```

**Methods:**
- `classify(message, traceback)` → `(FailureType, float)` - Classify with confidence
- `_pattern_match_score(text, patterns)` → `float` - Score pattern matches

**Pattern Sets:**
- `ARCHITECTURAL_PATTERNS` - Design issues
- `TEST_EXPECTATION_PATTERNS` - Test assertions
- `LOGIC_BUG_PATTERNS` - Implementation errors
- `ENVIRONMENT_PATTERNS` - Setup/dependencies
- `SYNTAX_PATTERNS` - Syntax errors

### 3. TestFailureAnalyzer

Main orchestrator coordinating all analysis operations.

```python
from src.operations.utilities.test_failure_analyzer import TestFailureAnalyzer

analyzer = TestFailureAnalyzer()

# Analyze test run
result = analyzer.analyze(test_output, "pytest")

# Defer non-critical failures
for failure in result.deferrable_failures:
    analyzer.defer_failure(failure)

# Generate report
report = analyzer.generate_failure_report(result)

# Check deferred count
deferred = analyzer.get_deferred_count()
```

**Methods:**
- `analyze(test_output, framework)` → `TestRunResult` - Full analysis workflow
- `defer_failure(failure)` → `bool` - Defer non-critical failure
- `get_deferred_count()` → `int` - Count of deferred failures
- `generate_failure_report(result)` → `str` - Detailed report with all failures

**Attributes:**
- `deferred_failures` - List of deferred failures (must clear before completion)

---

## 📊 Data Models

### TestRunResult

```python
@dataclass
class TestRunResult:
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    failures: List[FailureInfo]
    
    @property
    def pass_rate(self) -> float
    
    @property
    def critical_failures(self) -> List[FailureInfo]
    
    @property
    def deferrable_failures(self) -> List[FailureInfo]
```

### FailureInfo

```python
@dataclass
class FailureInfo:
    test_name: str
    test_file: Path
    line_number: Optional[int]
    failure_message: str
    traceback: str
    failure_type: FailureType
    severity: FailureSeverity
    confidence: float  # 0.0-1.0
    can_defer: bool
    mitigation_strategy: str
    root_cause_analysis: str
```

### FailureType (Enum)

```python
class FailureType(Enum):
    ARCHITECTURAL = "ARCHITECTURAL"
    TEST_EXPECTATION = "TEST_EXPECTATION"
    LOGIC_BUG = "LOGIC_BUG"
    ENVIRONMENT = "ENVIRONMENT"
    SYNTAX = "SYNTAX"
    UNKNOWN = "UNKNOWN"
```

### FailureSeverity (Enum)

```python
class FailureSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
```

---

## 🔄 Integration with TDD Workflow

### TDD Orchestrator Integration

```python
from src.operations.utilities.test_failure_analyzer import TestFailureAnalyzer

class TDDOrchestrator:
    def __init__(self):
        self.failure_analyzer = TestFailureAnalyzer()
    
    def on_test_run_complete(self, test_output: str):
        """Called after each test run"""
        # Analyze failures
        result = self.failure_analyzer.analyze(test_output, "pytest")
        
        if result.critical_failures:
            # Block progress - critical failures must be fixed
            print("🚨 CRITICAL FAILURES - Progress blocked")
            for failure in result.critical_failures:
                print(f"  - {failure.test_name}: {failure.root_cause_analysis}")
                print(f"    Mitigation: {failure.mitigation_strategy}")
            return False
        
        if result.deferrable_failures:
            # Allow deferral with user confirmation
            print(f"⚠️  {len(result.deferrable_failures)} deferrable failures")
            for failure in result.deferrable_failures:
                if self.confirm_defer(failure):
                    self.failure_analyzer.defer_failure(failure)
        
        return True
    
    def on_phase_complete(self):
        """Check deferred failures before marking complete"""
        deferred = self.failure_analyzer.get_deferred_count()
        
        if deferred > 0:
            print(f"❌ Cannot complete: {deferred} deferred failures remain")
            return False
        
        return True
```

### Automated Failure Analysis

```python
def analyze_and_report(test_output: str) -> Dict:
    """Analyze test output and return actionable report"""
    analyzer = TestFailureAnalyzer()
    result = analyzer.analyze(test_output, "pytest")
    
    return {
        'pass_rate': result.pass_rate,
        'can_proceed': len(result.critical_failures) == 0,
        'critical_count': len(result.critical_failures),
        'deferrable_count': len(result.deferrable_failures),
        'recommendations': [
            {
                'test': f.test_name,
                'type': f.failure_type.value,
                'severity': f.severity.value,
                'mitigation': f.mitigation_strategy,
                'can_defer': f.can_defer
            }
            for f in result.failures
        ]
    }
```

---

## 🎯 Use Cases

### 1. RED Phase Validation

Validate that tests fail for the right reasons during TDD RED phase:

```python
def validate_red_phase(test_output: str) -> bool:
    """Ensure tests fail due to missing implementation, not errors"""
    analyzer = TestFailureAnalyzer()
    result = analyzer.analyze(test_output, "pytest")
    
    # RED phase should have only TEST_EXPECTATION or LOGIC_BUG failures
    for failure in result.failures:
        if failure.failure_type in [FailureType.SYNTAX, FailureType.ENVIRONMENT]:
            print(f"❌ Invalid RED phase: {failure.failure_type.value}")
            return False
    
    return True
```

### 2. Strategic Test Deferral

Defer non-critical failures during feature implementation:

```python
def implement_with_strategic_deferral(test_output: str):
    """Allow deferring non-architectural issues"""
    analyzer = TestFailureAnalyzer()
    result = analyzer.analyze(test_output, "pytest")
    
    # Block on architectural issues
    if result.critical_failures:
        print("🚨 Critical failures - must fix now")
        return False
    
    # Defer test expectation mismatches
    for failure in result.deferrable_failures:
        if failure.failure_type == FailureType.TEST_EXPECTATION:
            analyzer.defer_failure(failure)
            print(f"⏸️  Deferred: {failure.test_name}")
    
    return True
```

### 3. Pre-Commit Validation

Ensure no deferred failures before committing:

```python
def pre_commit_check(test_output: str) -> bool:
    """Validate all tests pass before commit"""
    analyzer = TestFailureAnalyzer()
    result = analyzer.analyze(test_output, "pytest")
    
    if result.pass_rate < 100.0:
        print(f"❌ Cannot commit: {result.failed} tests failing")
        
        # Show deferred failures
        if analyzer.get_deferred_count() > 0:
            print(f"⚠️  {analyzer.get_deferred_count()} deferred failures must be resolved")
        
        return False
    
    return True
```

### 4. CI/CD Integration

Integrate with CI/CD pipelines:

```python
import sys

def ci_test_analysis(test_output: str) -> int:
    """Analyze tests for CI/CD pipeline"""
    analyzer = TestFailureAnalyzer()
    result = analyzer.analyze(test_output, "pytest")
    
    # Generate report
    report = analyzer.generate_failure_report(result)
    print(report)
    
    # Exit codes
    if result.critical_failures:
        print("💥 CRITICAL FAILURES - Build blocked")
        return 1  # Fail build
    
    if result.pass_rate < 90.0:
        print("⚠️  Pass rate below threshold")
        return 1  # Fail build
    
    print("✅ All tests passed")
    return 0  # Success
```

---

## 🔍 Advanced Features

### Custom Classification Rules

Extend classifier with custom patterns:

```python
from src.operations.utilities.test_failure_analyzer import FailureClassifier

class CustomClassifier(FailureClassifier):
    # Add custom patterns
    CUSTOM_PATTERNS = [
        r'my_custom_error',
        r'special_case'
    ]
    
    def classify(self, message: str, traceback: str):
        # Check custom patterns first
        if any(re.search(p, f"{message}\n{traceback}") for p in self.CUSTOM_PATTERNS):
            return FailureType.CUSTOM, 1.0
        
        # Fall back to default classification
        return super().classify(message, traceback)
```

### Failure Report Customization

Customize report formatting:

```python
def generate_custom_report(result: TestRunResult) -> str:
    """Generate custom failure report"""
    lines = []
    
    lines.append("=" * 80)
    lines.append(f"TEST ANALYSIS: {result.pass_rate:.1f}% PASSING")
    lines.append("=" * 80)
    
    if result.critical_failures:
        lines.append("\n🚨 BLOCKING ISSUES:")
        for f in result.critical_failures:
            lines.append(f"  [{f.failure_type.value}] {f.test_name}")
            lines.append(f"    → {f.mitigation_strategy}")
    
    if result.deferrable_failures:
        lines.append("\n⚠️  CAN DEFER:")
        for f in result.deferrable_failures:
            lines.append(f"  [{f.severity.value}] {f.test_name}")
    
    return '\n'.join(lines)
```

---

## 🧪 Testing

Comprehensive test coverage with 39 tests:

```bash
# Run all tests
pytest tests/unit/operations/utilities/test_test_failure_analyzer.py -v

# Run specific test class
pytest tests/unit/operations/utilities/test_test_failure_analyzer.py::TestFailureClassifier -v

# With coverage
pytest tests/unit/operations/utilities/test_test_failure_analyzer.py --cov
```

**Test Categories:**
- ✅ Pytest output parsing (4 tests)
- ✅ Failure classification (6 tests)
- ✅ Orchestrator operations (5 tests)
- ✅ Severity determination (5 tests)
- ✅ Mitigation strategies (4 tests)
- ✅ Root cause analysis (4 tests)
- ✅ Deferral logic (4 tests)
- ✅ Convenience functions (2 tests)
- ✅ Edge cases (3 tests)
- ✅ Integration workflows (2 tests)

---

## ⚠️ Best Practices

### 1. Always Check Critical Failures First

```python
# ✅ Correct
result = analyzer.analyze(output)
if result.critical_failures:
    # Handle critical failures - BLOCK progress
    return False

# ❌ Wrong - ignoring critical failures
if result.pass_rate < 100:
    # Generic handling might miss critical issues
    pass
```

### 2. Clear Deferred Failures Before Completion

```python
# ✅ Correct - check deferred count
def complete_phase():
    if analyzer.get_deferred_count() > 0:
        print("Must resolve deferred failures first")
        return False
    return True

# ❌ Wrong - completing with deferred failures
def complete_phase():
    return True  # Ignores deferred failures
```

### 3. Use Strategic Deferral Wisely

```python
# ✅ Good - defer only non-critical
for failure in result.deferrable_failures:
    if failure.severity in [FailureSeverity.MEDIUM, FailureSeverity.LOW]:
        analyzer.defer_failure(failure)

# ❌ Bad - deferring everything
for failure in result.failures:
    analyzer.defer_failure(failure)  # Might try to defer critical!
```

### 4. Generate Reports for Debugging

```python
# ✅ Helpful - generate report for investigation
result = analyzer.analyze(output)
if result.failed > 0:
    report = analyzer.generate_failure_report(result)
    print(report)  # Shows all details

# ❌ Less helpful - just counting failures
print(f"{result.failed} tests failed")  # No context
```

---

## 🐛 Troubleshooting

### Issue: Classification Confidence Low

**Cause:** Error patterns not matching standard patterns

**Solution:** Review patterns and extend if needed

```python
classifier = FailureClassifier()
failure_type, confidence = classifier.classify(message, traceback)

if confidence < 0.5:
    # Manual review recommended
    print(f"Low confidence: {confidence:.0%}")
    print(f"Message: {message}")
    print(f"Consider adding custom patterns")
```

### Issue: Unittest Parsing Not Working

**Cause:** Unittest parser not yet implemented

**Solution:** Use pytest for now, unittest coming in next iteration

```python
# ✅ Works
result = analyzer.analyze(output, "pytest")

# ❌ Not implemented yet
result = analyzer.analyze(output, "unittest")  # Raises NotImplementedError
```

### Issue: Failures Not Extracted

**Cause:** Output format doesn't match expected pytest format

**Solution:** Ensure output includes FAILURES section

```python
# Pytest output must have this structure:
"""
===== FAILURES =====
_____ test_name _____
[traceback here]
"""
```

---

## 📚 References

- **Implementation:** `src/operations/utilities/test_failure_analyzer.py`
- **Tests:** `tests/unit/operations/utilities/test_test_failure_analyzer.py`
- **TDD Workflow:** `src/orchestrators/tdd/tdd_orchestrator.py`
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-13 | Initial release with pytest support |

---

**For questions or issues:** Reference test cases for usage examples.
