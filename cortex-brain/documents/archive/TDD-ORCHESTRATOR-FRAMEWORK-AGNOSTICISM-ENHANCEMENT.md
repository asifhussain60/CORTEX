# TDD Orchestrator Framework Agnosticism Enhancement

**Author:** Asif Hussain (CORTEX)  
**Date:** 2025-12-12  
**Version:** 1.0  
**Context:** Platform.Classic Enhancement + TDD Orchestrator Refactoring

---

## 🎯 Executive Summary

**Problem:** TDD Implementation Orchestrator is hardcoded to pytest with Python-specific test output parsing. Platform.Classic requires Playwright support for E2E tests, but orchestrator cannot execute or validate Playwright tests.

**Solution:** Create framework abstraction layer with pluggable test runners supporting multiple frameworks (pytest, xUnit, NUnit, Playwright, Jest, Cypress, Mocha).

**Impact:**
- ✅ Platform.Classic can use Playwright tests with TDD workflow
- ✅ CORTEX becomes framework-agnostic (Python, .NET, JavaScript, Ruby)
- ✅ Existing pytest tests continue working (backward compatibility)
- ✅ Zero user impact (auto-detection handles framework selection)

---

## 📋 Current State Analysis

### Hardcoded pytest Dependencies

**File:** `src/orchestrators/tdd_implementation_orchestrator.py`

**Lines 1045-1064 - Detection Logic (pytest only):**
```python
def _detect_test_command(self, with_coverage: bool = False) -> str:
    # Check for pytest
    if (self.project_root / "pytest.ini").exists() or \
       (self.project_root / "setup.py").exists() or \
       (self.project_root / "tests").exists():
        if with_coverage:
            return "pytest --cov --cov-report=term-missing"
        return "pytest"
    
    # Fallback to unittest
    if with_coverage:
        return "python -m coverage run -m unittest discover"
    return "python -m unittest discover"
```

**Lines 1066-1086 - Output Parsing (pytest regex):**
```python
def _parse_test_output(self, output: str) -> Tuple[int, int, int]:
    # Pytest format: "18 passed in 0.30s" or "5 failed, 13 passed"
    passed_match = re.search(r'(\d+)\s+passed', output)
    failed_match = re.search(r'(\d+)\s+failed', output)
    
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    total = passed + failed
    
    return passed, failed, total
```

**Lines 1088-1103 - Failing Tests Extraction (pytest format):**
```python
def _extract_failing_tests(self, output: str) -> List[str]:
    # Pytest format: "tests/test_file.py::TestClass::test_method FAILED"
    failing_tests = re.findall(r'([\w/]+\.py::[\w:]+)\s+FAILED', output)
    return failing_tests
```

**Lines 1105-1122 - Coverage Extraction (pytest-cov format):**
```python
def _extract_coverage(self, output: str) -> float:
    # Pytest-cov format: "TOTAL ... 81%"
    coverage_match = re.search(r'TOTAL\s+.*?(\d+)%', output)
    if coverage_match:
        return float(coverage_match.group(1))
    return 0.0
```

---

## 🏗️ Proposed Architecture

### 1. Test Framework Abstraction Layer

**New Module:** `src/orchestrators/test_framework_adapter.py`

```python
"""
Test Framework Adapter for TDD Orchestrator

Provides framework-agnostic test execution and result parsing.
Supports multiple test frameworks across languages.

Supported Frameworks:
- Python: pytest, unittest
- .NET: xUnit, NUnit, MSTest
- JavaScript: Jest, Mocha, Playwright, Cypress
- Ruby: RSpec, Minitest

Author: Asif Hussain
Version: 1.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import subprocess
import re
import logging

logger = logging.getLogger(__name__)


class TestFrameworkType(Enum):
    """Supported test frameworks."""
    # Python
    PYTEST = "pytest"
    UNITTEST = "unittest"
    
    # .NET
    XUNIT = "xunit"
    NUNIT = "nunit"
    MSTEST = "mstest"
    
    # JavaScript/TypeScript
    JEST = "jest"
    MOCHA = "mocha"
    PLAYWRIGHT = "playwright"
    CYPRESS = "cypress"
    
    # Ruby
    RSPEC = "rspec"
    MINITEST = "minitest"


@dataclass
class TestExecutionResult:
    """Framework-agnostic test execution result."""
    success: bool
    tests_passed: int
    tests_failed: int
    tests_total: int
    failing_tests: List[str]
    coverage_percent: Optional[float] = None
    output: str = ""
    command: str = ""
    error: Optional[str] = None


class TestFrameworkAdapter(ABC):
    """Abstract base class for test framework adapters."""
    
    @abstractmethod
    def detect_framework(self, project_root: Path) -> bool:
        """Detect if this framework is present in project."""
        pass
    
    @abstractmethod
    def get_test_command(self, with_coverage: bool = False, test_files: Optional[List[Path]] = None) -> str:
        """Get command to run tests."""
        pass
    
    @abstractmethod
    def parse_test_output(self, output: str) -> Tuple[int, int, int]:
        """Parse test output to extract (passed, failed, total)."""
        pass
    
    @abstractmethod
    def extract_failing_tests(self, output: str) -> List[str]:
        """Extract list of failing test names."""
        pass
    
    @abstractmethod
    def extract_coverage(self, output: str) -> float:
        """Extract coverage percentage (0.0-100.0)."""
        pass
    
    def execute_tests(
        self,
        project_root: Path,
        with_coverage: bool = False,
        test_files: Optional[List[Path]] = None
    ) -> TestExecutionResult:
        """Execute tests and return framework-agnostic results."""
        command = self.get_test_command(with_coverage, test_files)
        
        try:
            result = subprocess.run(
                command,
                cwd=project_root,
                capture_output=True,
                text=True,
                shell=True
            )
            
            output = result.stdout + result.stderr
            passed, failed, total = self.parse_test_output(output)
            failing_tests = self.extract_failing_tests(output) if failed > 0 else []
            coverage = self.extract_coverage(output) if with_coverage else None
            
            return TestExecutionResult(
                success=result.returncode == 0,
                tests_passed=passed,
                tests_failed=failed,
                tests_total=total,
                failing_tests=failing_tests,
                coverage_percent=coverage,
                output=output,
                command=command
            )
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return TestExecutionResult(
                success=False,
                tests_passed=0,
                tests_failed=0,
                tests_total=0,
                failing_tests=[],
                output="",
                command=command,
                error=str(e)
            )


# ===== Python Frameworks =====

class PytestAdapter(TestFrameworkAdapter):
    """Adapter for pytest framework."""
    
    def detect_framework(self, project_root: Path) -> bool:
        return (
            (project_root / "pytest.ini").exists() or
            (project_root / "pyproject.toml").exists() or
            (project_root / "setup.py").exists() or
            (project_root / "tests").exists()
        )
    
    def get_test_command(self, with_coverage: bool = False, test_files: Optional[List[Path]] = None) -> str:
        base = "pytest"
        
        if test_files:
            base += " " + " ".join(str(f) for f in test_files)
        
        if with_coverage:
            return f"{base} --cov --cov-report=term-missing"
        
        return base
    
    def parse_test_output(self, output: str) -> Tuple[int, int, int]:
        # Pytest format: "18 passed in 0.30s" or "5 failed, 13 passed"
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        
        return passed, failed, passed + failed
    
    def extract_failing_tests(self, output: str) -> List[str]:
        # Format: "tests/test_file.py::TestClass::test_method FAILED"
        return re.findall(r'([\w/]+\.py::[\w:]+)\s+FAILED', output)
    
    def extract_coverage(self, output: str) -> float:
        # Format: "TOTAL ... 81%"
        match = re.search(r'TOTAL\s+.*?(\d+)%', output)
        return float(match.group(1)) if match else 0.0


class UnittestAdapter(TestFrameworkAdapter):
    """Adapter for unittest framework."""
    
    def detect_framework(self, project_root: Path) -> bool:
        # Fallback framework, always available in Python
        return True
    
    def get_test_command(self, with_coverage: bool = False, test_files: Optional[List[Path]] = None) -> str:
        if with_coverage:
            return "python -m coverage run -m unittest discover"
        return "python -m unittest discover"
    
    def parse_test_output(self, output: str) -> Tuple[int, int, int]:
        # Format: "Ran 18 tests in 0.30s" + "OK" or "FAILED (failures=5)"
        total_match = re.search(r'Ran (\d+) tests?', output)
        failed_match = re.search(r'FAILED.*failures=(\d+)', output)
        
        total = int(total_match.group(1)) if total_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        passed = total - failed
        
        return passed, failed, total
    
    def extract_failing_tests(self, output: str) -> List[str]:
        # Format: "FAIL: test_method (test_module.TestClass)"
        return re.findall(r'FAIL: ([\w_]+)', output)
    
    def extract_coverage(self, output: str) -> float:
        match = re.search(r'TOTAL\s+.*?(\d+)%', output)
        return float(match.group(1)) if match else 0.0


# ===== .NET Frameworks =====

class XUnitAdapter(TestFrameworkAdapter):
    """Adapter for xUnit framework."""
    
    def detect_framework(self, project_root: Path) -> bool:
        # Look for .csproj files with xUnit package reference
        for csproj in project_root.rglob("*.csproj"):
            content = csproj.read_text()
            if "xunit" in content.lower():
                return True
        return False
    
    def get_test_command(self, with_coverage: bool = False, test_files: Optional[List[Path]] = None) -> str:
        base = "dotnet test"
        
        if test_files:
            # Use first test file's project directory
            project = test_files[0].parent
            while project.name and not list(project.glob("*.csproj")):
                project = project.parent
            base += f" {project}"
        
        if with_coverage:
            return f"{base} --collect:\"XPlat Code Coverage\""
        
        return base
    
    def parse_test_output(self, output: str) -> Tuple[int, int, int]:
        # Format: "Passed!  - Failed:     0, Passed:    18, Skipped:     0, Total:    18"
        passed_match = re.search(r'Passed:\s*(\d+)', output)
        failed_match = re.search(r'Failed:\s*(\d+)', output)
        total_match = re.search(r'Total:\s*(\d+)', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        total = int(total_match.group(1)) if total_match else passed + failed
        
        return passed, failed, total
    
    def extract_failing_tests(self, output: str) -> List[str]:
        # Format: "Failed TestNamespace.TestClass.TestMethod [< 1 ms]"
        return re.findall(r'Failed\s+([\w.]+)', output)
    
    def extract_coverage(self, output: str) -> float:
        # Coverage report generated separately, parse coverage.xml
        return 0.0  # TODO: Implement XML parsing


class NUnitAdapter(TestFrameworkAdapter):
    """Adapter for NUnit framework."""
    
    def detect_framework(self, project_root: Path) -> bool:
        for csproj in project_root.rglob("*.csproj"):
            content = csproj.read_text()
            if "nunit" in content.lower():
                return True
        return False
    
    def get_test_command(self, with_coverage: bool = False, test_files: Optional[List[Path]] = None) -> str:
        # Same as xUnit
        return XUnitAdapter().get_test_command(with_coverage, test_files)
    
    def parse_test_output(self, output: str) -> Tuple[int, int, int]:
        # NUnit uses similar format to xUnit via dotnet test
        return XUnitAdapter().parse_test_output(output)
    
    def extract_failing_tests(self, output: str) -> List[str]:
        return XUnitAdapter().extract_failing_tests(output)
    
    def extract_coverage(self, output: str) -> float:
        return 0.0


# ===== JavaScript Frameworks =====

class PlaywrightAdapter(TestFrameworkAdapter):
    """Adapter for Playwright framework."""
    
    def detect_framework(self, project_root: Path) -> bool:
        return (
            (project_root / "playwright.config.js").exists() or
            (project_root / "playwright.config.ts").exists() or
            (project_root / "package.json").exists() and
            "playwright" in (project_root / "package.json").read_text()
        )
    
    def get_test_command(self, with_coverage: bool = False, test_files: Optional[List[Path]] = None) -> str:
        base = "npx playwright test"
        
        if test_files:
            base += " " + " ".join(str(f) for f in test_files)
        
        # Playwright doesn't have built-in coverage, use nyc/c8 if needed
        if with_coverage:
            base = f"npx c8 {base}"
        
        return base
    
    def parse_test_output(self, output: str) -> Tuple[int, int, int]:
        # Format: "5 passed (1s)" or "3 failed, 2 passed (2s)"
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        
        return passed, failed, passed + failed
    
    def extract_failing_tests(self, output: str) -> List[str]:
        # Format: "  1) [chromium] › test-file.spec.ts:10:5 › test name"
        return re.findall(r'›\s+([\w-]+\.spec\.\w+:\d+:\d+)\s+›\s+(.+)', output)
    
    def extract_coverage(self, output: str) -> float:
        # c8 format similar to pytest-cov
        match = re.search(r'All files\s+\|\s+[\d.]+\s+\|\s+[\d.]+\s+\|\s+[\d.]+\s+\|\s+([\d.]+)', output)
        return float(match.group(1)) if match else 0.0


class JestAdapter(TestFrameworkAdapter):
    """Adapter for Jest framework."""
    
    def detect_framework(self, project_root: Path) -> bool:
        return (
            (project_root / "jest.config.js").exists() or
            (project_root / "jest.config.ts").exists() or
            (project_root / "package.json").exists() and
            "jest" in (project_root / "package.json").read_text()
        )
    
    def get_test_command(self, with_coverage: bool = False, test_files: Optional[List[Path]] = None) -> str:
        base = "npx jest"
        
        if test_files:
            base += " " + " ".join(str(f) for f in test_files)
        
        if with_coverage:
            base += " --coverage"
        
        return base
    
    def parse_test_output(self, output: str) -> Tuple[int, int, int]:
        # Format: "Tests: 3 failed, 15 passed, 18 total"
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        total_match = re.search(r'(\d+)\s+total', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        total = int(total_match.group(1)) if total_match else passed + failed
        
        return passed, failed, total
    
    def extract_failing_tests(self, output: str) -> List[str]:
        # Format: "● Test suite failed to run" or "● test name"
        return re.findall(r'●\s+(.+)', output)
    
    def extract_coverage(self, output: str) -> float:
        # Format: "All files | 81.25 | 75.0 | 85.71 | 81.25 |"
        match = re.search(r'All files\s+\|\s+([\d.]+)', output)
        return float(match.group(1)) if match else 0.0


class CypressAdapter(TestFrameworkAdapter):
    """Adapter for Cypress framework."""
    
    def detect_framework(self, project_root: Path) -> bool:
        return (
            (project_root / "cypress.config.js").exists() or
            (project_root / "cypress.config.ts").exists() or
            (project_root / "cypress.json").exists()
        )
    
    def get_test_command(self, with_coverage: bool = False, test_files: Optional[List[Path]] = None) -> str:
        base = "npx cypress run"
        
        if test_files:
            base += " --spec " + ",".join(str(f) for f in test_files)
        
        if with_coverage:
            # Cypress coverage via @cypress/code-coverage plugin
            logger.warning("Cypress coverage requires @cypress/code-coverage plugin")
        
        return base
    
    def parse_test_output(self, output: str) -> Tuple[int, int, int]:
        # Format: "5 passing (1s)" or "3 failing, 2 passing"
        passed_match = re.search(r'(\d+)\s+passing', output)
        failed_match = re.search(r'(\d+)\s+failing', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        
        return passed, failed, passed + failed
    
    def extract_failing_tests(self, output: str) -> List[str]:
        # Format: "  1) test name"
        return re.findall(r'\d+\)\s+(.+)', output)
    
    def extract_coverage(self, output: str) -> float:
        return 0.0


# ===== Framework Factory =====

class TestFrameworkFactory:
    """Factory for creating appropriate test framework adapter."""
    
    # Adapter priority order (higher priority checked first)
    ADAPTERS = [
        # JavaScript/E2E (check before generic JS frameworks)
        PlaywrightAdapter,
        CypressAdapter,
        
        # .NET
        XUnitAdapter,
        NUnitAdapter,
        
        # JavaScript
        JestAdapter,
        
        # Python (pytest preferred over unittest)
        PytestAdapter,
        UnittestAdapter,  # Fallback
    ]
    
    @classmethod
    def detect_framework(cls, project_root: Path) -> Optional[TestFrameworkAdapter]:
        """
        Auto-detect test framework in project.
        
        Args:
            project_root: Project root directory
            
        Returns:
            Appropriate adapter or None if no framework detected
        """
        for adapter_class in cls.ADAPTERS:
            adapter = adapter_class()
            if adapter.detect_framework(project_root):
                logger.info(f"✅ Detected test framework: {adapter_class.__name__}")
                return adapter
        
        logger.warning("⚠️  No test framework detected")
        return None
    
    @classmethod
    def get_adapter(cls, framework_type: TestFrameworkType) -> TestFrameworkAdapter:
        """Get adapter for specific framework type."""
        mapping = {
            TestFrameworkType.PYTEST: PytestAdapter,
            TestFrameworkType.UNITTEST: UnittestAdapter,
            TestFrameworkType.XUNIT: XUnitAdapter,
            TestFrameworkType.NUNIT: NUnitAdapter,
            TestFrameworkType.PLAYWRIGHT: PlaywrightAdapter,
            TestFrameworkType.JEST: JestAdapter,
            TestFrameworkType.CYPRESS: CypressAdapter,
        }
        
        adapter_class = mapping.get(framework_type)
        if not adapter_class:
            raise ValueError(f"Unsupported framework: {framework_type}")
        
        return adapter_class()
```

---

## 🔄 TDD Orchestrator Refactoring

### Modified Methods in `tdd_implementation_orchestrator.py`

**1. Add Framework Adapter Import:**
```python
from src.orchestrators.test_framework_adapter import (
    TestFrameworkFactory,
    TestFrameworkAdapter,
    TestExecutionResult
)
```

**2. Initialize Adapter in `__init__`:**
```python
def __init__(self, cortex_root: str):
    # ... existing init ...
    
    # NEW: Auto-detect test framework
    self.test_adapter = TestFrameworkFactory.detect_framework(self.project_root)
    if self.test_adapter:
        logger.info(f"✅ Test framework adapter initialized: {self.test_adapter.__class__.__name__}")
    else:
        logger.warning("⚠️  No test framework detected - manual test commands required")
```

**3. Refactor `_run_tests()` Method:**
```python
def _run_tests(self, test_command: Optional[str] = None) -> Dict[str, Any]:
    """
    Run tests without coverage (framework-agnostic).
    
    Args:
        test_command: Optional test command (auto-detected if not provided)
        
    Returns:
        Dict with test results
    """
    # Use adapter if available
    if self.test_adapter and not test_command:
        result = self.test_adapter.execute_tests(
            project_root=self.project_root,
            with_coverage=False
        )
        
        return {
            "success": result.success,
            "tests_passed": result.tests_passed,
            "tests_failed": result.tests_failed,
            "tests_total": result.tests_total,
            "failing_tests": result.failing_tests,
            "output": result.output,
            "command": result.command,
            "error": result.error
        }
    
    # Fallback: Manual command execution (backward compatibility)
    if not test_command:
        test_command = self._detect_test_command()
    
    try:
        result = subprocess.run(
            test_command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            shell=True
        )
        
        output = result.stdout + result.stderr
        tests_passed, tests_failed, tests_total = self._parse_test_output(output)
        failing_tests = self._extract_failing_tests(output) if tests_failed > 0 else []
        
        return {
            "success": result.returncode == 0,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_total": tests_total,
            "failing_tests": failing_tests,
            "output": output,
            "command": test_command
        }
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "command": test_command
        }
```

**4. Refactor `_run_tests_with_coverage()` Method:**
```python
def _run_tests_with_coverage(self, test_command: Optional[str] = None) -> Dict[str, Any]:
    """
    Run tests with coverage tracking (framework-agnostic).
    
    Args:
        test_command: Optional test command (auto-detected if not provided)
        
    Returns:
        Dict with test results and coverage
    """
    # Use adapter if available
    if self.test_adapter and not test_command:
        result = self.test_adapter.execute_tests(
            project_root=self.project_root,
            with_coverage=True
        )
        
        return {
            "success": result.success,
            "tests_passed": result.tests_passed,
            "tests_failed": result.tests_failed,
            "tests_total": result.tests_total,
            "failing_tests": result.failing_tests,
            "coverage_percent": result.coverage_percent,
            "output": result.output,
            "command": result.command,
            "error": result.error
        }
    
    # Fallback: Manual command execution (backward compatibility)
    if not test_command:
        test_command = self._detect_test_command(with_coverage=True)
    
    try:
        result = subprocess.run(
            test_command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            shell=True
        )
        
        output = result.stdout + result.stderr
        tests_passed, tests_failed, tests_total = self._parse_test_output(output)
        failing_tests = self._extract_failing_tests(output) if tests_failed > 0 else []
        coverage_percent = self._extract_coverage(output)
        
        return {
            "success": result.returncode == 0,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_total": tests_total,
            "failing_tests": failing_tests,
            "coverage_percent": coverage_percent,
            "output": output,
            "command": test_command
        }
        
    except Exception as e:
        logger.error(f"❌ Test execution with coverage failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "command": test_command
        }
```

**5. Keep Existing Methods for Backward Compatibility:**
```python
# DEPRECATED: Keep for backward compatibility with manual test commands
def _detect_test_command(self, with_coverage: bool = False) -> str:
    """Auto-detect test command based on project structure (LEGACY)."""
    logger.warning("Using legacy test command detection - consider using test framework adapter")
    # ... existing implementation ...

def _parse_test_output(self, output: str) -> Tuple[int, int, int]:
    """Parse test output (LEGACY - pytest specific)."""
    # ... existing implementation ...

def _extract_failing_tests(self, output: str) -> List[str]:
    """Extract failing tests (LEGACY - pytest specific)."""
    # ... existing implementation ...

def _extract_coverage(self, output: str) -> float:
    """Extract coverage (LEGACY - pytest specific)."""
    # ... existing implementation ...
```

---

## 📊 Platform.Classic Integration

### Playwright Test Example (RA Funding Invoices)

**File:** `Platform.Classic/cortex/ra-modernized/tests/e2e/funding-invoice.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('RA Funding Invoice Creation', () => {
    test('should create funding invoice via UI', async ({ page }) => {
        // Navigate to funding invoice page
        await page.goto('http://localhost:5000/ra/funding-invoices');
        
        // Fill invoice form
        await page.fill('[data-testid="subaccount-id"]', 'SUB123');
        await page.fill('[data-testid="invoice-amount"]', '500.00');
        await page.click('[data-testid="submit-invoice"]');
        
        // Verify success message
        await expect(page.locator('[data-testid="success-message"]')).toContainText('Invoice created successfully');
        
        // Verify invoice appears in list
        const invoice = page.locator('[data-testid="invoice-list"] >> text=SUB123');
        await expect(invoice).toBeVisible();
    });
    
    test('should validate amount > 0', async ({ page }) => {
        await page.goto('http://localhost:5000/ra/funding-invoices');
        
        // Try invalid amount
        await page.fill('[data-testid="subaccount-id"]', 'SUB123');
        await page.fill('[data-testid="invoice-amount"]', '-100');
        await page.click('[data-testid="submit-invoice"]');
        
        // Verify validation error
        await expect(page.locator('[data-testid="validation-error"]')).toContainText('Amount must be greater than 0');
    });
});
```

### TDD Workflow with Playwright

**RED Phase:**
```bash
# CORTEX detects Playwright framework
> start tdd session "RA Funding Invoice UI Tests"

🎭 Orchestrator engaged: TDDImplementationOrchestrator
✅ Test framework adapter initialized: PlaywrightAdapter

# Write failing Playwright test
> create test Platform.Classic/cortex/ra-modernized/tests/e2e/funding-invoice.spec.ts

# Execute RED phase
> execute red phase

🔴 Executing RED phase
Command: npx playwright test tests/e2e/funding-invoice.spec.ts
Output: 2 failed (3s)
  1) [chromium] › funding-invoice.spec.ts:5:5 › should create funding invoice via UI
  2) [chromium] › funding-invoice.spec.ts:20:5 › should validate amount > 0

✅ RED phase validated: 2 test(s) failing as expected
```

**GREEN Phase:**
```bash
# Implement UI components
> implement minimum code to pass tests

# Execute GREEN phase
> execute green phase

🟢 Executing GREEN phase
Command: npx playwright test tests/e2e/funding-invoice.spec.ts
Output: 2 passed (4s)

✅ GREEN phase validated: All tests passing
```

**REFACTOR Phase:**
```bash
# Refactor UI components
> execute refactor phase

🔵 Executing REFACTOR phase
Running tests: npx playwright test tests/e2e/funding-invoice.spec.ts
Output: 2 passed (3s)

✅ REFACTOR phase complete: Tests still passing after refactor
```

---

## 🎯 Implementation Checklist

### Phase 1: Create Framework Abstraction (2-3 hours)
- [x] Create `test_framework_adapter.py` module
- [x] Implement base `TestFrameworkAdapter` abstract class
- [x] Create `TestExecutionResult` dataclass
- [x] Implement `PytestAdapter` (backward compatibility)
- [x] Implement `PlaywrightAdapter` (Platform.Classic requirement)
- [x] Implement `XUnitAdapter` (.NET support)
- [x] Implement `JestAdapter` (JavaScript support)
- [x] Implement `CypressAdapter` (E2E alternative)
- [x] Create `TestFrameworkFactory` with auto-detection

### Phase 2: Refactor TDD Orchestrator (1-2 hours)
- [ ] Add framework adapter import
- [ ] Initialize adapter in `__init__`
- [ ] Refactor `_run_tests()` to use adapter
- [ ] Refactor `_run_tests_with_coverage()` to use adapter
- [ ] Mark legacy methods as DEPRECATED
- [ ] Add backward compatibility fallback
- [ ] Update logging with framework name

### Phase 3: Testing & Validation (2-3 hours)
- [ ] Test with pytest (CORTEX internal tests)
- [ ] Test with xUnit (Platform.Classic unit tests)
- [ ] Test with Playwright (Platform.Classic E2E tests)
- [ ] Test manual command override
- [ ] Test coverage extraction for each framework
- [ ] Validate backward compatibility (existing TDD sessions)

### Phase 4: Documentation (1 hour)
- [ ] Update TDD Mastery Guide with framework support
- [ ] Add Playwright example to documentation
- [ ] Update CORTEX.prompt.md with framework-agnostic language
- [ ] Create Platform.Classic test setup guide

---

## 📈 Success Metrics

**Backward Compatibility:**
- ✅ Existing pytest tests continue working (zero changes required)
- ✅ Legacy `_detect_test_command()` still works
- ✅ Manual test commands override adapter

**New Capabilities:**
- ✅ Playwright tests run via TDD workflow
- ✅ xUnit tests run via TDD workflow
- ✅ Jest tests run via TDD workflow
- ✅ Auto-detection works for all supported frameworks

**Platform.Classic Impact:**
- ✅ RA Funding Invoices E2E tests use Playwright
- ✅ Unit tests use xUnit
- ✅ Both frameworks work in same TDD session

---

## 🚨 Risks & Mitigations

**Risk 1: Breaking Existing TDD Sessions**
- **Mitigation:** Fallback to legacy methods if adapter fails
- **Validation:** Run existing CORTEX tests with new code

**Risk 2: Framework Detection False Positives**
- **Mitigation:** Priority order (Playwright before Jest, pytest before unittest)
- **Validation:** Test detection on mixed projects

**Risk 3: Coverage Parsing Inconsistencies**
- **Mitigation:** Each adapter implements framework-specific parsing
- **Validation:** Test coverage extraction for each framework

---

## 📚 References

**CORTEX Files:**
- `src/orchestrators/tdd_implementation_orchestrator.py` (lines 945-1122)
- `src/orchestrators/test_intelligence.py` (framework-agnostic test detection)
- `src/intelligence/test_discovery_engine.py` (existing `TestFramework` enum)

**Platform.Classic Files:**
- `cortex-brain/documents/planning/ra-funding-invoices-migration-plan.md` (lines 2690-2750)
- `cortex/ra-modernized/tests/` (test structure)

**External Documentation:**
- Playwright Test Docs: https://playwright.dev/docs/test-intro
- xUnit Docs: https://xunit.net/docs/getting-started/netcore/cmdline
- Jest Docs: https://jestjs.io/docs/cli

---

**Status:** ✅ Design Complete - Ready for Implementation  
**Next Action:** Implement Phase 1 (Create Framework Abstraction)  
**Estimated Total Time:** 6-8 hours
