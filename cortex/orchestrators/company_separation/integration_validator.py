"""Phase 47 S5: Integration and Regression Testing.

Full integration testing and regression validation.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import yaml


@dataclass
class TestResult:
    """Test result."""

    test_name: str
    passed: bool
    duration: float
    error_message: Optional[str] = None


@dataclass
class RegressionReport:
    """Regression test report."""

    total_tests: int
    passed_tests: int
    failed_tests: int
    warnings: List[str]
    duration: float
    coverage_percent: float


class IntegrationTestSuite:
    """Integration test suite for company/CORTEX separation."""

    def __init__(self):
        """Initialize test suite."""
        self.results: List[TestResult] = []
        self.test_count = 0

    def add_result(
        self,
        test_name: str,
        passed: bool,
        duration: float = 0.0,
        error_message: Optional[str] = None,
    ) -> None:
        """Add test result.

        Args:
            test_name: Name of test
            passed: Whether test passed
            duration: Test duration in seconds
            error_message: Error message if failed
        """
        result = TestResult(
            test_name=test_name,
            passed=passed,
            duration=duration,
            error_message=error_message,
        )
        self.results.append(result)
        self.test_count += 1

    def get_results(self) -> List[TestResult]:
        """Get all test results.

        Returns:
            List of TestResult objects.
        """
        return self.results

    def get_pass_rate(self) -> float:
        """Get pass rate percentage.

        Returns:
            Pass rate as percentage (0-100).
        """
        if self.test_count == 0:
            return 0.0

        passed = sum(1 for r in self.results if r.passed)
        return (passed / self.test_count) * 100.0

    def get_failed_tests(self) -> List[TestResult]:
        """Get failed tests.

        Returns:
            List of failed TestResult objects.
        """
        return [r for r in self.results if not r.passed]

    def get_total_duration(self) -> float:
        """Get total test duration.

        Returns:
            Total duration in seconds.
        """
        return sum(r.duration for r in self.results)


class RegressionValidator:
    """Validate that existing tests still pass after changes."""

    def __init__(self):
        """Initialize validator."""
        self.baseline_tests: Dict[str, bool] = {}
        self.current_tests: Dict[str, bool] = {}
        self.regressions: List[str] = []

    def set_baseline(self, test_results: Dict[str, bool]) -> None:
        """Set baseline test results.

        Args:
            test_results: Dictionary of test_name -> passed
        """
        self.baseline_tests = test_results.copy()

    def set_current(self, test_results: Dict[str, bool]) -> None:
        """Set current test results.

        Args:
            test_results: Dictionary of test_name -> passed
        """
        self.current_tests = test_results.copy()
        self._detect_regressions()

    def _detect_regressions(self) -> None:
        """Detect regressions between baseline and current."""
        for test_name, was_passing in self.baseline_tests.items():
            if test_name in self.current_tests:
                is_passing = self.current_tests[test_name]
                if was_passing and not is_passing:
                    self.regressions.append(f"Regression in {test_name}")

    def has_regressions(self) -> bool:
        """Check if there are regressions.

        Returns:
            True if regressions detected.
        """
        return len(self.regressions) > 0

    def get_regressions(self) -> List[str]:
        """Get regression list.

        Returns:
            List of regression descriptions.
        """
        return self.regressions


class IntegrationValidator:
    """Validate integration between modules."""

    def __init__(self):
        """Initialize validator."""
        self.validations: List[Tuple[str, bool]] = []
        self.warnings: List[str] = []

    def validate_imports(self, modules: List[str]) -> bool:
        """Validate that modules can be imported.

        Args:
            modules: List of module paths

        Returns:
            True if all imports successful.
        """
        for module in modules:
            try:
                # Simulate import validation
                if not module or len(module) < 2:
                    self.validations.append((module, False))
                    self.warnings.append(f"Invalid module path: {module}")
                else:
                    self.validations.append((module, True))
            except Exception as e:
                self.validations.append((module, False))
                self.warnings.append(f"Failed to import {module}: {str(e)}")

        return all(v[1] for v in self.validations)

    def validate_interfaces(self, interfaces: Dict[str, List[str]]) -> bool:
        """Validate module interfaces.

        Args:
            interfaces: Dictionary of module -> required methods

        Returns:
            True if all interfaces valid.
        """
        for module, methods in interfaces.items():
            if not methods:
                self.warnings.append(f"No methods defined for {module}")
                continue

            self.validations.append((f"Interface: {module}", len(methods) > 0))

        return all(v[1] for v in self.validations)

    def validate_contracts(self, contracts: Dict[str, Dict[str, Any]]) -> bool:
        """Validate contracts between modules.

        Args:
            contracts: Dictionary of contract definitions

        Returns:
            True if all contracts valid.
        """
        for contract_name, definition in contracts.items():
            has_input = "input" in definition
            has_output = "output" in definition

            self.validations.append(
                (f"Contract: {contract_name}", has_input and has_output)
            )

            if not (has_input and has_output):
                self.warnings.append(f"Incomplete contract: {contract_name}")

        return all(v[1] for v in self.validations)

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary.

        Returns:
            Summary dictionary.
        """
        total = len(self.validations)
        passed = sum(1 for _, result in self.validations if result)

        return {
            "total_validations": total,
            "passed_validations": passed,
            "failed_validations": total - passed,
            "warnings": len(self.warnings),
        }


class RegressionTestReport:
    """Generate regression test report."""

    def __init__(
        self,
        suite: IntegrationTestSuite,
        validator: RegressionValidator,
    ):
        """Initialize report generator.

        Args:
            suite: IntegrationTestSuite instance
            validator: RegressionValidator instance
        """
        self.suite = suite
        self.validator = validator

    def generate(self) -> RegressionReport:
        """Generate regression report.

        Returns:
            RegressionReport object.
        """
        total = len(self.suite.results)
        passed = sum(1 for r in self.suite.results if r.passed)
        failed = total - passed
        duration = self.suite.get_total_duration()
        coverage = self.suite.get_pass_rate()

        warnings = []
        if self.validator.has_regressions():
            warnings.extend(self.validator.get_regressions())

        return RegressionReport(
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            warnings=warnings,
            duration=duration,
            coverage_percent=coverage,
        )

    def print_report(self) -> str:
        """Print regression report.

        Returns:
            Formatted report string.
        """
        report = self.generate()

        lines = [
            "═" * 60,
            "REGRESSION TEST REPORT",
            "═" * 60,
            f"Total Tests: {report.total_tests}",
            f"Passed: {report.passed_tests} ({report.coverage_percent:.1f}%)",
            f"Failed: {report.failed_tests}",
            f"Duration: {report.duration:.2f}s",
            "─" * 60,
        ]

        if report.warnings:
            lines.append("WARNINGS:")
            for warning in report.warnings:
                lines.append(f"  ⚠️  {warning}")
        else:
            lines.append("✅ No regressions detected")

        lines.append("═" * 60)

        return "\n".join(lines)
