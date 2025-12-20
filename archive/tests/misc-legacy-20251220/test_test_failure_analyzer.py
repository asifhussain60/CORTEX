"""
Tests for Test Failure Analyzer

Validates:
- Pytest output parsing (summary, failures, tracebacks)
- Unittest output parsing
- Failure classification (ARCHITECTURAL, TEST_EXPECTATION, LOGIC_BUG, etc.)
- Severity determination (CRITICAL, HIGH, MEDIUM, LOW)
- Mitigation strategy generation
- Root cause analysis
- Deferral logic (can defer vs must fix)
- Failure report generation

Author: Asif Hussain
Date: December 13, 2025
Version: 1.0.0
"""

import pytest
from pathlib import Path

from src.operations.utilities.test_failure_analyzer import (
    TestFailureAnalyzer,
    TestOutputParser,
    FailureClassifier,
    TestRunResult,
    FailureInfo,
    FailureType,
    FailureSeverity,
    analyze_pytest_output,
    analyze_unittest_output
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_pytest_output_success():
    """Sample pytest output with all tests passing"""
    return """
============================= test session starts ==============================
collected 10 items

tests/test_sample.py::test_addition PASSED
tests/test_sample.py::test_subtraction PASSED
tests/test_sample.py::test_multiplication PASSED
tests/test_sample.py::test_division PASSED

============================== 10 passed in 0.50s ===============================
"""


@pytest.fixture
def sample_pytest_output_failures():
    """Sample pytest output with failures"""
    return """
============================= test session starts ==============================
collected 10 items

tests/test_sample.py::test_addition PASSED
tests/test_sample.py::test_subtraction FAILED
tests/test_sample.py::test_multiplication PASSED
tests/test_sample.py::test_division ERROR

============================= FAILURES ========================================
_________________________ test_subtraction _____________________________________

    def test_subtraction():
        result = subtract(5, 3)
>       assert result == 3
E       AssertionError: assert 2 == 3

tests/test_sample.py:15: AssertionError

============================= ERRORS ==========================================
_________________________ test_division ________________________________________

    def test_division():
>       result = divide(10, 0)
E       ZeroDivisionError: division by zero

tests/test_sample.py:20: ZeroDivisionError

======================== 2 failed, 1 error, 7 passed in 1.20s =================
"""


@pytest.fixture
def sample_pytest_architectural_failure():
    """Pytest output with architectural failure"""
    return """
============================= test session starts ==============================
FAILED tests/test_architecture.py::test_import - ImportError: circular import detected

tests/test_architecture.py:5: in <module>
    from module_a import ClassA
module_a.py:3: in <module>
    from module_b import ClassB
module_b.py:3: in <module>
    from module_a import ClassA
E   ImportError: cannot import name 'ClassA' from partially initialized module 'module_a' (most likely due to a circular import)

======================== 1 failed in 0.10s =====================================
"""


@pytest.fixture
def sample_pytest_environment_failure():
    """Pytest output with environment failure"""
    return """
============================= test session starts ==============================
FAILED tests/test_api.py::test_connection - ModuleNotFoundError: No module named 'requests'

tests/test_api.py:1: in <module>
    import requests
E   ModuleNotFoundError: No module named 'requests'

======================== 1 failed in 0.05s =====================================
"""


@pytest.fixture
def test_failure_analyzer():
    """Create TestFailureAnalyzer instance"""
    return TestFailureAnalyzer()


# ============================================================================
# TEST PYTEST OUTPUT PARSER
# ============================================================================

class TestPytestOutputParser:
    """Tests for TestOutputParser with pytest output"""
    
    def test_parse_success(self, sample_pytest_output_success):
        """Should parse successful test run"""
        parser = TestOutputParser(sample_pytest_output_success, "pytest")
        result = parser.parse()
        
        assert result.total_tests == 10
        assert result.passed == 10
        assert result.failed == 0
        assert result.errors == 0
        assert result.duration == 0.50
        assert len(result.failures) == 0
    
    def test_parse_failures(self, sample_pytest_output_failures):
        """Should parse failures and errors"""
        parser = TestOutputParser(sample_pytest_output_failures, "pytest")
        result = parser.parse()
        
        assert result.total_tests == 10
        assert result.passed == 7
        assert result.failed == 2
        assert result.errors == 1
        assert result.duration == 1.20
    
    def test_extract_failure_details(self, sample_pytest_output_failures):
        """Should extract failure details from traceback"""
        parser = TestOutputParser(sample_pytest_output_failures, "pytest")
        result = parser.parse()
        
        # Should have extracted failure info
        assert len(result.failures) > 0
        
        # Check first failure
        failure = result.failures[0]
        assert "test_subtraction" in failure.test_name or "test_division" in failure.test_name
        assert failure.test_file.name.endswith(".py")
    
    def test_parse_pass_rate_calculation(self, sample_pytest_output_failures):
        """Should calculate pass rate correctly"""
        parser = TestOutputParser(sample_pytest_output_failures, "pytest")
        result = parser.parse()
        
        # 7 passed out of 10 = 70%
        assert result.pass_rate == 70.0


# ============================================================================
# TEST FAILURE CLASSIFIER
# ============================================================================

class TestFailureClassifier:
    """Tests for FailureClassifier"""
    
    def test_classify_architectural(self):
        """Should classify architectural failures"""
        classifier = FailureClassifier()
        message = "ImportError: circular import detected"
        traceback = "circular import in module_a and module_b"
        
        failure_type, confidence = classifier.classify(message, traceback)
        
        assert failure_type == FailureType.ARCHITECTURAL
        assert confidence > 0.0
    
    def test_classify_test_expectation(self):
        """Should classify test expectation failures"""
        classifier = FailureClassifier()
        message = "AssertionError: assert 2 == 3"
        traceback = "expected 3 but got 2"
        
        failure_type, confidence = classifier.classify(message, traceback)
        
        assert failure_type == FailureType.TEST_EXPECTATION
        assert confidence > 0.0
    
    def test_classify_logic_bug(self):
        """Should classify logic bug failures"""
        classifier = FailureClassifier()
        message = "TypeError: unsupported operand type(s)"
        traceback = "cannot add 'int' and 'str'"
        
        failure_type, confidence = classifier.classify(message, traceback)
        
        assert failure_type == FailureType.LOGIC_BUG
        assert confidence > 0.0
    
    def test_classify_environment(self):
        """Should classify environment failures"""
        classifier = FailureClassifier()
        message = "ModuleNotFoundError: No module named 'requests'"
        traceback = "import requests failed"
        
        failure_type, confidence = classifier.classify(message, traceback)
        
        assert failure_type == FailureType.ENVIRONMENT
        assert confidence > 0.0
    
    def test_classify_syntax(self):
        """Should classify syntax errors"""
        classifier = FailureClassifier()
        message = "SyntaxError: invalid syntax"
        traceback = "unexpected token at line 5"
        
        failure_type, confidence = classifier.classify(message, traceback)
        
        assert failure_type == FailureType.SYNTAX
        assert confidence > 0.0
    
    def test_classify_unknown(self):
        """Should return UNKNOWN for unrecognized patterns"""
        classifier = FailureClassifier()
        message = "Some random error"
        traceback = "No recognizable patterns"
        
        failure_type, confidence = classifier.classify(message, traceback)
        
        assert failure_type == FailureType.UNKNOWN
        assert confidence == 0.0


# ============================================================================
# TEST FAILURE ANALYZER
# ============================================================================

class TestFailureAnalyzerOrchestrator:
    """Tests for TestFailureAnalyzer main orchestrator"""
    
    def test_analyze_success(self, test_failure_analyzer, sample_pytest_output_success):
        """Should analyze successful test run"""
        result = test_failure_analyzer.analyze(sample_pytest_output_success, "pytest")
        
        assert result.total_tests == 10
        assert result.passed == 10
        assert result.pass_rate == 100.0
        assert len(result.failures) == 0
        assert len(result.critical_failures) == 0
    
    def test_analyze_failures(self, test_failure_analyzer, sample_pytest_output_failures):
        """Should analyze test run with failures"""
        result = test_failure_analyzer.analyze(sample_pytest_output_failures, "pytest")
        
        assert result.failed > 0
        assert result.pass_rate < 100.0
    
    def test_defer_failure_allowed(self, test_failure_analyzer):
        """Should allow deferring non-critical failures"""
        failure = FailureInfo(
            test_name="test_example",
            test_file=Path("test.py"),
            line_number=10,
            failure_message="AssertionError",
            traceback="...",
            failure_type=FailureType.TEST_EXPECTATION,
            severity=FailureSeverity.MEDIUM,
            confidence=0.9,
            can_defer=True,
            mitigation_strategy="Fix test",
            root_cause_analysis="Wrong assertion"
        )
        
        assert test_failure_analyzer.defer_failure(failure) is True
        assert test_failure_analyzer.get_deferred_count() == 1
    
    def test_defer_failure_blocked(self, test_failure_analyzer):
        """Should block deferring critical failures"""
        failure = FailureInfo(
            test_name="test_critical",
            test_file=Path("test.py"),
            line_number=10,
            failure_message="ImportError",
            traceback="...",
            failure_type=FailureType.ARCHITECTURAL,
            severity=FailureSeverity.CRITICAL,
            confidence=0.95,
            can_defer=False,
            mitigation_strategy="Fix architecture",
            root_cause_analysis="Circular import"
        )
        
        assert test_failure_analyzer.defer_failure(failure) is False
        assert test_failure_analyzer.get_deferred_count() == 0
    
    def test_generate_failure_report(self, test_failure_analyzer, sample_pytest_output_failures):
        """Should generate detailed failure report"""
        result = test_failure_analyzer.analyze(sample_pytest_output_failures, "pytest")
        report = test_failure_analyzer.generate_failure_report(result)
        
        assert "TEST FAILURE ANALYSIS REPORT" in report
        assert "Total Tests:" in report
        assert "Passed:" in report
        assert "Failed:" in report


# ============================================================================
# TEST SEVERITY DETERMINATION
# ============================================================================

class TestSeverityDetermination:
    """Tests for severity determination logic"""
    
    def test_architectural_is_critical(self):
        """Architectural failures should be CRITICAL"""
        parser = TestOutputParser("", "pytest")
        severity = parser._determine_severity(FailureType.ARCHITECTURAL, "")
        assert severity == FailureSeverity.CRITICAL
    
    def test_syntax_is_critical(self):
        """Syntax errors should be CRITICAL"""
        parser = TestOutputParser("", "pytest")
        severity = parser._determine_severity(FailureType.SYNTAX, "")
        assert severity == FailureSeverity.CRITICAL
    
    def test_environment_is_critical(self):
        """Environment failures should be CRITICAL"""
        parser = TestOutputParser("", "pytest")
        severity = parser._determine_severity(FailureType.ENVIRONMENT, "")
        assert severity == FailureSeverity.CRITICAL
    
    def test_assertion_is_medium(self):
        """Assertion errors should be MEDIUM"""
        parser = TestOutputParser("", "pytest")
        severity = parser._determine_severity(
            FailureType.TEST_EXPECTATION,
            "AssertionError: assert 2 == 3"
        )
        assert severity == FailureSeverity.MEDIUM
    
    def test_type_error_is_high(self):
        """Type errors should be HIGH"""
        parser = TestOutputParser("", "pytest")
        severity = parser._determine_severity(
            FailureType.LOGIC_BUG,
            "TypeError: unsupported operand"
        )
        assert severity == FailureSeverity.HIGH


# ============================================================================
# TEST MITIGATION STRATEGIES
# ============================================================================

class TestMitigationStrategies:
    """Tests for mitigation strategy generation"""
    
    def test_architectural_mitigation(self):
        """Should generate architectural mitigation"""
        parser = TestOutputParser("", "pytest")
        strategy = parser._generate_mitigation(FailureType.ARCHITECTURAL, "")
        
        assert "design review" in strategy.lower()
        assert "refactor" in strategy.lower()
    
    def test_test_expectation_mitigation(self):
        """Should generate test expectation mitigation"""
        parser = TestOutputParser("", "pytest")
        strategy = parser._generate_mitigation(FailureType.TEST_EXPECTATION, "")
        
        assert "update test" in strategy.lower() or "assertion" in strategy.lower()
    
    def test_logic_bug_mitigation(self):
        """Should generate logic bug mitigation"""
        parser = TestOutputParser("", "pytest")
        strategy = parser._generate_mitigation(FailureType.LOGIC_BUG, "")
        
        assert "fix implementation" in strategy.lower() or "logic" in strategy.lower()
    
    def test_environment_mitigation(self):
        """Should generate environment mitigation"""
        parser = TestOutputParser("", "pytest")
        strategy = parser._generate_mitigation(FailureType.ENVIRONMENT, "")
        
        assert "dependencies" in strategy.lower() or "environment" in strategy.lower()


# ============================================================================
# TEST ROOT CAUSE ANALYSIS
# ============================================================================

class TestRootCauseAnalysis:
    """Tests for root cause analysis"""
    
    def test_assertion_root_cause(self):
        """Should identify assertion failures"""
        parser = TestOutputParser("", "pytest")
        root_cause = parser._analyze_root_cause("AssertionError", "assert 2 == 3")
        
        assert "assertion" in root_cause.lower()
        assert "expected" in root_cause.lower() or "actual" in root_cause.lower()
    
    def test_attribute_error_root_cause(self):
        """Should identify attribute errors"""
        parser = TestOutputParser("", "pytest")
        root_cause = parser._analyze_root_cause("AttributeError", "has no attribute 'foo'")
        
        assert "attribute" in root_cause.lower()
    
    def test_type_error_root_cause(self):
        """Should identify type errors"""
        parser = TestOutputParser("", "pytest")
        root_cause = parser._analyze_root_cause("TypeError", "unsupported operand")
        
        assert "type" in root_cause.lower()
    
    def test_import_error_root_cause(self):
        """Should identify import errors"""
        parser = TestOutputParser("", "pytest")
        root_cause = parser._analyze_root_cause("ImportError", "cannot import")
        
        assert "import" in root_cause.lower() or "dependency" in root_cause.lower()


# ============================================================================
# TEST DEFERRAL LOGIC
# ============================================================================

class TestDeferralLogic:
    """Tests for failure deferral logic"""
    
    def test_test_expectation_can_defer(self):
        """Test expectation failures should be deferrable"""
        parser = TestOutputParser("", "pytest")
        failure = parser._classify_failure(
            test_name="test",
            test_file=Path("test.py"),
            failure_message="AssertionError",
            traceback="assert failed"
        )
        
        assert failure.can_defer is True
    
    def test_logic_bug_can_defer(self):
        """Logic bug failures should be deferrable (if not critical)"""
        parser = TestOutputParser("", "pytest")
        failure = parser._classify_failure(
            test_name="test",
            test_file=Path("test.py"),
            failure_message="ValueError",
            traceback="invalid value"
        )
        
        # Can defer if severity is not critical
        if failure.severity != FailureSeverity.CRITICAL:
            assert failure.can_defer is True
    
    def test_architectural_cannot_defer(self):
        """Architectural failures should NOT be deferrable"""
        parser = TestOutputParser("", "pytest")
        failure = parser._classify_failure(
            test_name="test",
            test_file=Path("test.py"),
            failure_message="circular import",
            traceback="ImportError"
        )
        
        assert failure.can_defer is False
    
    def test_environment_cannot_defer(self):
        """Environment failures should NOT be deferrable"""
        parser = TestOutputParser("", "pytest")
        failure = parser._classify_failure(
            test_name="test",
            test_file=Path("test.py"),
            failure_message="ModuleNotFoundError",
            traceback="No module named 'foo'"
        )
        
        assert failure.can_defer is False


# ============================================================================
# TEST CONVENIENCE FUNCTIONS
# ============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions"""
    
    def test_analyze_pytest_output(self, sample_pytest_output_success):
        """Should analyze pytest output"""
        result = analyze_pytest_output(sample_pytest_output_success)
        
        assert isinstance(result, TestRunResult)
        assert result.total_tests == 10
        assert result.passed == 10
    
    def test_analyze_unittest_output(self):
        """Should raise NotImplementedError for unittest (coming soon)"""
        with pytest.raises(NotImplementedError):
            analyze_unittest_output("unittest output")


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases"""
    
    def test_empty_output(self):
        """Should handle empty output gracefully"""
        parser = TestOutputParser("", "pytest")
        result = parser.parse()
        
        assert result.total_tests == 0
        assert result.passed == 0
    
    def test_malformed_output(self):
        """Should handle malformed output gracefully"""
        parser = TestOutputParser("random text\nno test output", "pytest")
        result = parser.parse()
        
        assert isinstance(result, TestRunResult)
    
    def test_no_failures_section(self, sample_pytest_output_success):
        """Should handle output with no failures section"""
        parser = TestOutputParser(sample_pytest_output_success, "pytest")
        result = parser.parse()
        
        assert len(result.failures) == 0
        assert len(result.critical_failures) == 0


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_complete_analysis_workflow(self, test_failure_analyzer, sample_pytest_output_failures):
        """Should perform complete analysis workflow"""
        # Analyze
        result = test_failure_analyzer.analyze(sample_pytest_output_failures, "pytest")
        
        # Generate report
        report = test_failure_analyzer.generate_failure_report(result)
        
        # Verify workflow completed
        assert result.total_tests > 0
        assert len(report) > 0
        assert "TEST FAILURE ANALYSIS REPORT" in report
    
    def test_defer_and_track(self, test_failure_analyzer):
        """Should defer failures and track count"""
        # Create deferrable failure
        failure = FailureInfo(
            test_name="test_defer",
            test_file=Path("test.py"),
            line_number=10,
            failure_message="AssertionError",
            traceback="...",
            failure_type=FailureType.TEST_EXPECTATION,
            severity=FailureSeverity.MEDIUM,
            confidence=0.9,
            can_defer=True,
            mitigation_strategy="Fix",
            root_cause_analysis="Wrong"
        )
        
        # Defer it
        assert test_failure_analyzer.defer_failure(failure) is True
        
        # Check count
        assert test_failure_analyzer.get_deferred_count() == 1
        
        # Defer another
        test_failure_analyzer.defer_failure(failure)
        assert test_failure_analyzer.get_deferred_count() == 2
