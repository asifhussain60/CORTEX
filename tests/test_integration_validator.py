"""Tests for Phase 47 S5: Integration and Regression Testing."""

import pytest
from cortex.orchestrators.company_separation.integration_validator import (
    TestResult,
    RegressionReport,
    IntegrationTestSuite,
    RegressionValidator,
    IntegrationValidator,
    RegressionTestReport,
)


class TestTestResult:
    """Test TestResult dataclass."""

    def test_create_passed_result(self):
        """Test creating passed test result."""
        result = TestResult(
            test_name="test_example",
            passed=True,
            duration=0.5,
        )

        assert result.test_name == "test_example"
        assert result.passed is True
        assert result.duration == 0.5
        assert result.error_message is None

    def test_create_failed_result(self):
        """Test creating failed test result."""
        result = TestResult(
            test_name="test_failure",
            passed=False,
            duration=0.1,
            error_message="Assertion failed",
        )

        assert result.passed is False
        assert result.error_message == "Assertion failed"


class TestRegressionReport:
    """Test RegressionReport dataclass."""

    def test_create_report(self):
        """Test creating regression report."""
        report = RegressionReport(
            total_tests=100,
            passed_tests=95,
            failed_tests=5,
            warnings=[],
            duration=10.5,
            coverage_percent=95.0,
        )

        assert report.total_tests == 100
        assert report.passed_tests == 95
        assert report.coverage_percent == 95.0


class TestIntegrationTestSuite:
    """Test IntegrationTestSuite class."""

    def test_initialize_suite(self):
        """Test suite initialization."""
        suite = IntegrationTestSuite()

        assert suite.test_count == 0
        assert len(suite.results) == 0

    def test_add_result(self):
        """Test adding test result."""
        suite = IntegrationTestSuite()
        suite.add_result("test_1", True, 0.5)

        assert suite.test_count == 1
        assert len(suite.results) == 1

    def test_add_multiple_results(self):
        """Test adding multiple results."""
        suite = IntegrationTestSuite()

        suite.add_result("test_1", True, 0.5)
        suite.add_result("test_2", False, 0.3, "Error message")
        suite.add_result("test_3", True, 0.2)

        assert suite.test_count == 3

    def test_get_pass_rate(self):
        """Test getting pass rate."""
        suite = IntegrationTestSuite()

        suite.add_result("test_1", True, 0.5)
        suite.add_result("test_2", False, 0.3)

        assert suite.get_pass_rate() == 50.0

    def test_get_failed_tests(self):
        """Test getting failed tests."""
        suite = IntegrationTestSuite()

        suite.add_result("test_1", True, 0.5)
        suite.add_result("test_2", False, 0.3)
        suite.add_result("test_3", False, 0.2)

        failed = suite.get_failed_tests()
        assert len(failed) == 2
        assert all(not r.passed for r in failed)

    def test_get_total_duration(self):
        """Test getting total duration."""
        suite = IntegrationTestSuite()

        suite.add_result("test_1", True, 0.5)
        suite.add_result("test_2", True, 0.3)
        suite.add_result("test_3", True, 0.2)

        assert suite.get_total_duration() == 1.0

    def test_pass_rate_no_tests(self):
        """Test pass rate with no tests."""
        suite = IntegrationTestSuite()

        assert suite.get_pass_rate() == 0.0


class TestRegressionValidator:
    """Test RegressionValidator class."""

    def test_initialize_validator(self):
        """Test validator initialization."""
        validator = RegressionValidator()

        assert len(validator.baseline_tests) == 0
        assert len(validator.current_tests) == 0
        assert len(validator.regressions) == 0

    def test_set_baseline(self):
        """Test setting baseline tests."""
        validator = RegressionValidator()
        baseline = {"test_1": True, "test_2": True}

        validator.set_baseline(baseline)

        assert len(validator.baseline_tests) == 2

    def test_detect_no_regressions(self):
        """Test detecting no regressions."""
        validator = RegressionValidator()
        baseline = {"test_1": True, "test_2": True}
        current = {"test_1": True, "test_2": True}

        validator.set_baseline(baseline)
        validator.set_current(current)

        assert validator.has_regressions() is False

    def test_detect_regression(self):
        """Test detecting regression."""
        validator = RegressionValidator()
        baseline = {"test_1": True, "test_2": True}
        current = {"test_1": True, "test_2": False}  # test_2 regressed

        validator.set_baseline(baseline)
        validator.set_current(current)

        assert validator.has_regressions() is True
        assert len(validator.get_regressions()) > 0

    def test_get_regressions(self):
        """Test getting regression list."""
        validator = RegressionValidator()
        baseline = {"test_1": True, "test_2": True}
        current = {"test_1": False, "test_2": False}

        validator.set_baseline(baseline)
        validator.set_current(current)

        regressions = validator.get_regressions()
        assert len(regressions) >= 2


class TestIntegrationValidator:
    """Test IntegrationValidator class."""

    def test_initialize_validator(self):
        """Test validator initialization."""
        validator = IntegrationValidator()

        assert len(validator.validations) == 0
        assert len(validator.warnings) == 0

    def test_validate_imports_success(self):
        """Test successful import validation."""
        validator = IntegrationValidator()
        modules = ["cortex.orchestrators", "cortex.wiring"]

        success = validator.validate_imports(modules)

        assert success is True

    def test_validate_imports_with_invalid(self):
        """Test import validation with invalid module."""
        validator = IntegrationValidator()
        modules = ["valid.module", ""]

        success = validator.validate_imports(modules)

        assert success is False
        assert len(validator.warnings) > 0

    def test_validate_interfaces(self):
        """Test interface validation."""
        validator = IntegrationValidator()
        interfaces = {
            "Resolver": ["resolve", "get_stats"],
            "Analyzer": ["analyze", "get_summary"],
        }

        success = validator.validate_interfaces(interfaces)

        assert success is True

    def test_validate_contracts(self):
        """Test contract validation."""
        validator = IntegrationValidator()
        contracts = {
            "contract_1": {"input": {"type": "str"}, "output": {"type": "dict"}},
            "contract_2": {"input": {"type": "list"}},  # missing output
        }

        success = validator.validate_contracts(contracts)

        assert success is False
        assert len(validator.warnings) > 0

    def test_get_validation_summary(self):
        """Test getting validation summary."""
        validator = IntegrationValidator()
        modules = ["module1", "module2"]

        validator.validate_imports(modules)
        summary = validator.get_validation_summary()

        assert "total_validations" in summary
        assert "passed_validations" in summary
        assert summary["total_validations"] > 0


class TestRegressionTestReport:
    """Test RegressionTestReport class."""

    def test_initialize_report(self):
        """Test report initialization."""
        suite = IntegrationTestSuite()
        validator = RegressionValidator()
        report = RegressionTestReport(suite, validator)

        assert report.suite == suite
        assert report.validator == validator

    def test_generate_report(self):
        """Test generating report."""
        suite = IntegrationTestSuite()
        suite.add_result("test_1", True, 0.5)
        suite.add_result("test_2", True, 0.3)

        validator = RegressionValidator()
        validator.set_baseline({"test_1": True, "test_2": True})
        validator.set_current({"test_1": True, "test_2": True})

        report_gen = RegressionTestReport(suite, validator)
        report = report_gen.generate()

        assert report.total_tests == 2
        assert report.passed_tests == 2
        assert report.coverage_percent == 100.0

    def test_print_report(self):
        """Test printing report."""
        suite = IntegrationTestSuite()
        suite.add_result("test_1", True, 0.5)

        validator = RegressionValidator()
        report_gen = RegressionTestReport(suite, validator)
        output = report_gen.print_report()

        assert "REGRESSION TEST REPORT" in output
        assert "Total Tests" in output
        assert "Passed" in output
