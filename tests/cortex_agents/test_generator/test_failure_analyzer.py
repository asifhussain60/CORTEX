"""
Tests for Failure Analyzer - Phase 5.2

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.cortex_agents.test_generator.failure_analyzer import (
    FailureAnalyzer,
    TestFailure,
    FailurePattern,
    FailureAnalysisReport,
    FailureCategory,
    FailureSeverity
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_tier2():
    """Mock Tier 2 Knowledge Graph"""
    tier2 = Mock()
    tier2.store_pattern = Mock(return_value=True)
    tier2.search_patterns = Mock(return_value=[])
    tier2.get_pattern = Mock(return_value=None)
    return tier2


@pytest.fixture
def mock_pattern_store():
    """Mock Pattern Store"""
    store = Mock()
    store.store_pattern = Mock(return_value=True)
    store.search_patterns = Mock(return_value=[])
    store.update_pattern_confidence = Mock(return_value=True)
    return store


@pytest.fixture
def analyzer(mock_tier2, mock_pattern_store):
    """Create analyzer instance with mocked dependencies"""
    return FailureAnalyzer(tier2_kg=mock_tier2, pattern_store=mock_pattern_store)


@pytest.fixture
def sample_pytest_output():
    """Sample pytest output with various failure types"""
    return """
============================= test session starts ==============================
tests/test_auth.py::test_login_success PASSED                            [ 20%]
tests/test_auth.py::test_login_invalid_credentials FAILED                [ 40%]
tests/test_auth.py::test_logout PASSED                                   [ 60%]
tests/test_user.py::test_create_user FAILED                              [ 80%]
tests/test_user.py::test_delete_user PASSED                              [100%]

=================================== FAILURES ===================================
_________________________ test_login_invalid_credentials _______________________

    def test_login_invalid_credentials():
        result = login("user", "wrong_password")
>       assert result.status_code == 401
E       AssertionError: assert 500 == 401
E        +  where 500 = <Response>.status_code

tests/test_auth.py:45: AssertionError

______________________________ test_create_user ________________________________

    def test_create_user():
        with pytest.raises(TimeoutError):
>           create_user_with_validation(timeout=5)
E           TimeoutError: Test exceeded 5 seconds

tests/test_user.py:23: TimeoutError

=========================== 3 passed, 2 failed in 5.23s ========================
"""


@pytest.fixture
def sample_failures():
    """Sample failure objects for testing"""
    return [
        TestFailure(
            test_name="test_login_invalid",
            test_file="tests/test_auth.py",
            category=FailureCategory.ASSERTION_ERROR,
            severity=FailureSeverity.HIGH,
            error_message="AssertionError: assert 500 == 401",
            expected_value="401",
            actual_value="500"
        ),
        TestFailure(
            test_name="test_create_user",
            test_file="tests/test_user.py",
            category=FailureCategory.TIMEOUT,
            severity=FailureSeverity.MEDIUM,
            error_message="TimeoutError: Test exceeded 5 seconds"
        ),
        TestFailure(
            test_name="test_api_call",
            test_file="tests/test_api.py",
            category=FailureCategory.ASSERTION_ERROR,
            severity=FailureSeverity.HIGH,
            error_message="AssertionError: assert 404 == 200",
            expected_value="200",
            actual_value="404"
        )
    ]


# ============================================================================
# TEST PYTEST OUTPUT PARSING
# ============================================================================

class TestPytestOutputParsing:
    """Test pytest output parsing"""
    
    def test_parse_test_counts(self, analyzer, sample_pytest_output):
        """Test extracting test counts from pytest output"""
        counts = analyzer._parse_test_counts(sample_pytest_output)
        
        assert counts['passed'] == 3
        assert counts['failed'] == 2
        assert counts['skipped'] == 0
        assert counts['total'] == 5
    
    def test_parse_test_counts_with_errors(self, analyzer):
        """Test parsing output with errors"""
        output = "5 passed, 2 failed, 1 error in 3.45s"
        counts = analyzer._parse_test_counts(output)
        
        assert counts['passed'] == 5
        assert counts['failed'] == 2
        assert counts['errors'] == 1
    
    def test_parse_test_counts_fallback(self, analyzer):
        """Test fallback parsing when no summary line"""
        output = """
        test_one PASSED
        test_two FAILED
        test_three PASSED
        """
        counts = analyzer._parse_test_counts(output)
        
        assert counts['passed'] == 2
        assert counts['failed'] == 1
    
    def test_extract_failures(self, analyzer, sample_pytest_output):
        """Test extracting individual failures"""
        failures = analyzer._extract_failures(sample_pytest_output)
        
        assert len(failures) == 2
        assert failures[0].test_name == "test_login_invalid_credentials"
        assert failures[0].test_file == "tests/test_auth.py"
        assert failures[1].test_name == "test_create_user"
    
    def test_parse_full_output(self, analyzer, sample_pytest_output):
        """Test complete parsing workflow"""
        report = analyzer.parse_pytest_output(sample_pytest_output, duration=5.23)
        
        assert report.total_tests == 5
        assert report.passed == 3
        assert report.failed == 2
        assert report.duration_seconds == 5.23
        assert len(report.failures) == 2


# ============================================================================
# TEST FAILURE CATEGORIZATION
# ============================================================================

class TestFailureCategorization:
    """Test failure categorization"""
    
    def test_categorize_assertion_error(self, analyzer):
        """Test categorizing assertion errors"""
        error_details = analyzer._extract_error_details(
            """
            tests/test_auth.py::test_login FAILED
            AssertionError: assert 500 == 401
            """,
            "tests/test_auth.py",
            "test_login"
        )
        
        assert error_details['category'] == FailureCategory.ASSERTION_ERROR
        assert error_details['severity'] == FailureSeverity.HIGH
    
    def test_categorize_timeout_error(self, analyzer):
        """Test categorizing timeout errors"""
        error_details = analyzer._extract_error_details(
            """
            tests/test_user.py::test_create FAILED
            TimeoutError: Test exceeded 30 seconds
            """,
            "tests/test_user.py",
            "test_create"
        )
        
        assert error_details['category'] == FailureCategory.TIMEOUT
        assert error_details['severity'] == FailureSeverity.MEDIUM
    
    def test_categorize_import_error(self, analyzer):
        """Test categorizing import errors"""
        error_details = analyzer._extract_error_details(
            """
            tests/test_api.py::test_endpoint FAILED
            ImportError: No module named 'requests'
            """,
            "tests/test_api.py",
            "test_endpoint"
        )
        
        assert error_details['category'] == FailureCategory.IMPORT_ERROR
        assert error_details['severity'] == FailureSeverity.CRITICAL
    
    def test_categorize_fixture_error(self, analyzer):
        """Test categorizing fixture errors"""
        error_details = analyzer._extract_error_details(
            """
            tests/test_db.py::test_query FAILED
            fixture 'database' not found
            """,
            "tests/test_db.py",
            "test_query"
        )
        
        assert error_details['category'] == FailureCategory.FIXTURE_ERROR
        assert error_details['severity'] == FailureSeverity.HIGH
    
    def test_extract_expected_actual_values(self, analyzer):
        """Test extracting expected and actual values"""
        error_details = analyzer._extract_error_details(
            """
            tests/test_calc.py::test_add FAILED
            AssertionError: assert 5 == 4
            Expected: 4
            Actual: 5
            """,
            "tests/test_calc.py",
            "test_add"
        )
        
        assert error_details['expected_value'] is not None
        assert error_details['actual_value'] is not None


# ============================================================================
# TEST PATTERN DETECTION
# ============================================================================

class TestPatternDetection:
    """Test recurring pattern detection"""
    
    def test_detect_patterns_with_duplicates(self, analyzer, sample_failures):
        """Test pattern detection with duplicate failures"""
        patterns = analyzer._detect_patterns(sample_failures)
        
        # Should detect pattern for assertion errors (2 occurrences)
        assert len(patterns) >= 1
        assertion_patterns = [p for p in patterns if p.category == FailureCategory.ASSERTION_ERROR]
        assert len(assertion_patterns) >= 1
    
    def test_pattern_confidence_calculation(self, analyzer):
        """Test confidence calculation based on occurrences"""
        # Create multiple similar failures
        failures = [
            TestFailure(
                test_name=f"test_{i}",
                test_file="tests/test.py",
                category=FailureCategory.ASSERTION_ERROR,
                severity=FailureSeverity.HIGH,
                error_message="AssertionError: assert N == N"
            )
            for i in range(5)
        ]
        
        patterns = analyzer._detect_patterns(failures)
        
        assert len(patterns) >= 1
        pattern = patterns[0]
        assert pattern.confidence >= 0.7  # 5 occurrences should give high confidence
    
    def test_simplify_error_message(self, analyzer):
        """Test error message simplification"""
        error1 = "AssertionError: assert 500 == 401"
        error2 = "AssertionError: assert 404 == 200"
        
        simplified1 = analyzer._simplify_error_message(error1)
        simplified2 = analyzer._simplify_error_message(error2)
        
        # Numbers should be replaced with 'N'
        assert 'N' in simplified1
        assert 'N' in simplified2
        # Simplified messages should be similar
        assert simplified1 == simplified2
    
    def test_pattern_creation(self, analyzer, sample_failures):
        """Test pattern object creation"""
        patterns = analyzer._detect_patterns(sample_failures)
        
        if patterns:
            pattern = patterns[0]
            assert pattern.pattern_id is not None
            assert pattern.category in FailureCategory
            assert pattern.occurrences >= 2
            assert len(pattern.affected_tests) >= 2
            assert 0.0 <= pattern.confidence <= 1.0


# ============================================================================
# TEST RECOMMENDATIONS
# ============================================================================

class TestRecommendations:
    """Test recommendation generation"""
    
    def test_generate_fix_suggestions_assertion(self, analyzer):
        """Test fix suggestions for assertion errors"""
        suggestions = analyzer._generate_fix_suggestions(
            FailureCategory.ASSERTION_ERROR,
            []
        )
        
        assert len(suggestions) > 0
        assert any('validation' in s.lower() for s in suggestions)
    
    def test_generate_fix_suggestions_timeout(self, analyzer):
        """Test fix suggestions for timeout errors"""
        suggestions = analyzer._generate_fix_suggestions(
            FailureCategory.TIMEOUT,
            []
        )
        
        assert len(suggestions) > 0
        assert any('timeout' in s.lower() or 'performance' in s.lower() for s in suggestions)
    
    def test_generate_fix_suggestions_import(self, analyzer):
        """Test fix suggestions for import errors"""
        suggestions = analyzer._generate_fix_suggestions(
            FailureCategory.IMPORT_ERROR,
            []
        )
        
        assert len(suggestions) > 0
        assert any('dependencies' in s.lower() or 'install' in s.lower() for s in suggestions)
    
    def test_generate_recommendations_high_failure_rate(self, analyzer):
        """Test recommendations for high failure rate"""
        failures = [
            TestFailure(
                test_name=f"test_{i}",
                test_file="tests/test.py",
                category=FailureCategory.ASSERTION_ERROR,
                severity=FailureSeverity.HIGH,
                error_message="Error"
            )
            for i in range(5)
        ]
        
        recommendations = analyzer._generate_recommendations(failures, [])
        
        assert len(recommendations) > 0
    
    def test_generate_recommendations_import_errors(self, analyzer):
        """Test critical recommendation for import errors"""
        failures = [
            TestFailure(
                test_name="test_import",
                test_file="tests/test.py",
                category=FailureCategory.IMPORT_ERROR,
                severity=FailureSeverity.CRITICAL,
                error_message="ImportError"
            )
        ]
        
        recommendations = analyzer._generate_recommendations(failures, [])
        
        # Should have critical import error recommendation
        assert any('import' in r.lower() for r in recommendations)
    
    def test_generate_recommendations_no_failures(self, analyzer):
        """Test recommendations when all tests pass"""
        recommendations = analyzer._generate_recommendations([], [])
        
        assert len(recommendations) > 0
        assert any('passing' in r.lower() for r in recommendations)


# ============================================================================
# TEST TEMPLATE IMPROVEMENTS
# ============================================================================

class TestTemplateImprovements:
    """Test template improvement system"""
    
    def test_generate_template_updates_assertion(self, analyzer):
        """Test template updates for assertion errors"""
        updates = analyzer._generate_template_updates(
            FailureCategory.ASSERTION_ERROR,
            []
        )
        
        assert len(updates) > 0
        assert any('assert' in u['update'].lower() for u in updates)
    
    def test_generate_template_updates_timeout(self, analyzer):
        """Test template updates for timeout errors"""
        updates = analyzer._generate_template_updates(
            FailureCategory.TIMEOUT,
            []
        )
        
        assert len(updates) > 0
        assert any('timeout' in u['update'].lower() for u in updates)
    
    def test_improve_templates_with_patterns(self, analyzer):
        """Test template improvement workflow"""
        patterns = [
            FailurePattern(
                pattern_id="pattern_1",
                category=FailureCategory.ASSERTION_ERROR,
                description="Assertion failures",
                occurrences=5,
                confidence=0.8,
                fix_suggestions=["Add validation"],
                template_updates=[
                    {"template": "assertion", "update": "assert x == y, 'message'"}
                ]
            )
        ]
        
        results = analyzer.improve_templates(patterns)
        
        assert results['templates_updated'] >= 1
    
    def test_improve_templates_low_confidence(self, analyzer):
        """Test that low-confidence patterns are skipped"""
        patterns = [
            FailurePattern(
                pattern_id="pattern_1",
                category=FailureCategory.ASSERTION_ERROR,
                description="Low confidence pattern",
                occurrences=2,
                confidence=0.5,  # Below 0.7 threshold
                fix_suggestions=[],
                template_updates=[
                    {"template": "test", "update": "update"}
                ]
            )
        ]
        
        results = analyzer.improve_templates(patterns)
        
        # Should not update templates for low confidence
        assert results['templates_updated'] == 0


# ============================================================================
# TEST PATTERN STORAGE
# ============================================================================

class TestPatternStorage:
    """Test pattern storage in Tier 2 KG"""
    
    def test_store_failure_pattern(self, analyzer, mock_pattern_store):
        """Test storing failure pattern"""
        pattern = FailurePattern(
            pattern_id="pattern_test",
            category=FailureCategory.ASSERTION_ERROR,
            description="Test pattern",
            occurrences=3,
            confidence=0.8,
            fix_suggestions=["Fix 1"],
            template_updates=[]
        )
        
        result = analyzer._store_failure_pattern(pattern)
        
        assert result is True
        mock_pattern_store.store_pattern.assert_called_once()
    
    def test_store_pattern_no_store(self):
        """Test storing when pattern store is None"""
        analyzer = FailureAnalyzer(tier2_kg=None, pattern_store=None)
        
        pattern = FailurePattern(
            pattern_id="pattern_test",
            category=FailureCategory.TIMEOUT,
            description="Test",
            occurrences=1,
            confidence=0.5
        )
        
        result = analyzer._store_failure_pattern(pattern)
        
        assert result is False
    
    def test_boost_related_patterns(self, analyzer, mock_pattern_store):
        """Test boosting confidence of related patterns"""
        # Mock search results
        mock_pattern_store.search_patterns.return_value = [
            {'id': 'pattern_1', 'confidence': 0.7},
            {'id': 'pattern_2', 'confidence': 0.8}
        ]
        
        pattern = FailurePattern(
            pattern_id="pattern_test",
            category=FailureCategory.ASSERTION_ERROR,
            description="Test",
            occurrences=1,
            confidence=0.9
        )
        
        boosted = analyzer._boost_related_patterns(pattern)
        
        assert boosted == 2
        assert mock_pattern_store.update_pattern_confidence.call_count == 2


# ============================================================================
# TEST REPORT GENERATION
# ============================================================================

class TestReportGeneration:
    """Test report generation"""
    
    def test_generate_text_report(self, analyzer, sample_failures):
        """Test text report generation"""
        report = FailureAnalysisReport(
            total_tests=10,
            passed=7,
            failed=3,
            skipped=0,
            errors=0,
            duration_seconds=5.5,
            failures=sample_failures,
            patterns=[],
            category_distribution={'assertion_error': 2, 'timeout': 1},
            severity_distribution={'high': 2, 'medium': 1},
            recommendations=["Fix assertion errors"]
        )
        
        text_report = analyzer.generate_report(report, output_format='text')
        
        assert "FAILURE ANALYSIS REPORT" in text_report
        assert "Total:   10" in text_report
        assert "Passed: 7" in text_report
        assert "Failed: 3" in text_report
        assert "assertion_error" in text_report
        assert "Recommendations:" in text_report
    
    def test_generate_json_report(self, analyzer, sample_failures):
        """Test JSON report generation"""
        report = FailureAnalysisReport(
            total_tests=10,
            passed=7,
            failed=3,
            skipped=0,
            errors=0,
            duration_seconds=5.5,
            failures=sample_failures,
            patterns=[],
            category_distribution={'assertion_error': 2},
            severity_distribution={'high': 2},
            recommendations=["Test recommendation"]
        )
        
        json_report = analyzer.generate_report(report, output_format='json')
        
        # Parse JSON to verify structure
        data = json.loads(json_report)
        
        assert data['total_tests'] == 10
        assert data['passed'] == 7
        assert data['failed'] == 3
        assert 'category_distribution' in data
        assert 'recommendations' in data
    
    def test_generate_report_with_patterns(self, analyzer, sample_failures):
        """Test report with patterns"""
        patterns = [
            FailurePattern(
                pattern_id="pattern_1",
                category=FailureCategory.ASSERTION_ERROR,
                description="Test pattern",
                occurrences=3,
                confidence=0.85,
                affected_tests=["test_1", "test_2", "test_3"],
                fix_suggestions=["Fix suggestion"]
            )
        ]
        
        report = FailureAnalysisReport(
            total_tests=10,
            passed=7,
            failed=3,
            skipped=0,
            errors=0,
            duration_seconds=5.5,
            failures=sample_failures,
            patterns=patterns,
            category_distribution={'assertion_error': 3},
            severity_distribution={'high': 3},
            recommendations=[]
        )
        
        text_report = analyzer.generate_report(report, output_format='text')
        
        assert "Recurring Patterns" in text_report
        assert "pattern_1" not in text_report  # Should show category, not ID
        assert "Occurrences: 3" in text_report
        assert "Confidence: 0.85" in text_report


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_pytest_output(self, analyzer):
        """Test parsing empty pytest output"""
        report = analyzer.parse_pytest_output("", duration=0.0)
        
        assert report.total_tests == 0
        assert report.passed == 0
        assert report.failed == 0
        assert len(report.failures) == 0
    
    def test_malformed_pytest_output(self, analyzer):
        """Test parsing malformed pytest output"""
        output = "Some random text that is not pytest output"
        
        report = analyzer.parse_pytest_output(output, duration=1.0)
        
        # Should not crash, should return default values
        assert report.total_tests >= 0
        assert report.passed >= 0
    
    def test_failure_hash_uniqueness(self):
        """Test that failure hashes are unique"""
        failure1 = TestFailure(
            test_name="test_one",
            test_file="test.py",
            category=FailureCategory.ASSERTION_ERROR,
            severity=FailureSeverity.HIGH,
            error_message="Error 123"
        )
        
        failure2 = TestFailure(
            test_name="test_one",
            test_file="test.py",
            category=FailureCategory.ASSERTION_ERROR,
            severity=FailureSeverity.HIGH,
            error_message="Error 456"
        )
        
        # Same test, category, but different error numbers
        # Hashes should be same (numbers replaced with N)
        assert failure1.failure_hash == failure2.failure_hash
    
    def test_pattern_detection_single_failure(self, analyzer):
        """Test pattern detection with only one failure"""
        failures = [
            TestFailure(
                test_name="test_single",
                test_file="test.py",
                category=FailureCategory.TIMEOUT,
                severity=FailureSeverity.MEDIUM,
                error_message="Timeout"
            )
        ]
        
        patterns = analyzer._detect_patterns(failures)
        
        # Should not create pattern for single occurrence
        assert len(patterns) == 0


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestIntegration:
    """Test end-to-end integration"""
    
    def test_full_analysis_workflow(self, analyzer, sample_pytest_output):
        """Test complete analysis workflow"""
        # Parse output
        report = analyzer.parse_pytest_output(sample_pytest_output, duration=5.23)
        
        # Verify report structure
        assert report.total_tests == 5
        assert report.failed == 2
        assert len(report.failures) == 2
        assert len(report.recommendations) > 0
        
        # Generate text report
        text_report = analyzer.generate_report(report, output_format='text')
        assert "FAILURE ANALYSIS REPORT" in text_report
        
        # Generate JSON report
        json_report = analyzer.generate_report(report, output_format='json')
        data = json.loads(json_report)
        assert data['total_tests'] == 5
    
    def test_improve_templates_workflow(self, analyzer, mock_pattern_store):
        """Test template improvement workflow"""
        # Create high-confidence pattern
        pattern = FailurePattern(
            pattern_id="pattern_improve",
            category=FailureCategory.ASSERTION_ERROR,
            description="Assertion pattern",
            occurrences=5,
            confidence=0.9,
            fix_suggestions=["Add validation"],
            template_updates=[
                {"template": "assertion", "update": "new_template"}
            ]
        )
        
        # Improve templates
        results = analyzer.improve_templates([pattern])
        
        # Verify results
        assert results['templates_updated'] >= 1
        assert results['new_patterns_added'] >= 1
        
        # Verify pattern was stored
        mock_pattern_store.store_pattern.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
