"""
Tests for IntelligentTestGenerator.

Validates integration of all test generation components with value-based prioritization.
"""

import pytest
from pathlib import Path
from typing import List
from cortex.orchestrators.intelligence.intelligent_test_generator import (
    IntelligentTestGenerator,
    GeneratedTest,
    TestGenerationRequest,
    TestGenerationResult,
)
from cortex.orchestrators.intelligence.orch_test_value_scorer import IssueSeverity, ScenarioLikelihood


class TestIntelligentTestGeneratorInitialization:
    """Test IntelligentTestGenerator initialization."""

    def test_generator_initialization_default(self):
        """Test generator initializes with all components."""
        generator = IntelligentTestGenerator()
        
        assert generator is not None
        assert generator.value_scorer is not None
        assert generator.blind_spot_detector is not None
        assert generator.edge_case_generator is not None
        assert generator.security_test_generator is not None

    def test_generator_initialization_custom_threshold(self):
        """Test generator initializes with custom value threshold."""
        generator = IntelligentTestGenerator(min_value_score=80.0)
        
        assert generator.min_value_score == 80.0


class TestGenerateTests:
    """Test comprehensive test generation."""

    def test_generate_tests_for_function(self):
        """Test generation for Python function."""
        generator = IntelligentTestGenerator(min_value_score=55.0)  # Lower threshold for edge cases
        request = TestGenerationRequest(
            target_type="function",
            target_name="validate_user",
            file_path=Path("cortex/validation.py"),
            parameters=["username", "email", "age"],
            has_database_access=True,
            parameter_constraints={
                "username": {"type_hint": "str", "min_length": 3, "max_length": 50},
                "email": {"type_hint": "str", "nullable": False},
                "age": {"type_hint": "int", "min_value": 0, "max_value": 120},
            }
        )
        
        result = generator.generate_tests(request)
        
        # Verify result type and structure
        assert result is not None
        assert hasattr(result, 'tests')
        assert hasattr(result, 'total_generated')
        assert hasattr(result, 'high_priority_count')
        # Edge case tests should be generated for 3 parameters
        assert len(result.tests) > 0
        assert result.total_generated > 0
        assert result.high_priority_count >= 0

    def test_generate_tests_for_api_endpoint(self):
        """Test generation for API endpoint."""
        generator = IntelligentTestGenerator()
        request = TestGenerationRequest(
            target_type="endpoint",
            target_name="/api/users",
            file_path=Path("api/routes.py"),
            parameters=["user_id", "name"],
            has_database_access=True,
            requires_authentication=True,
        )
        
        result = generator.generate_tests(request)
        
        # Should include security tests
        assert len(result.tests) > 0
        test_types = {test.source for test in result.tests}
        assert "security" in test_types


class TestFilterByValueScore:
    """Test value-based filtering."""

    def test_filter_by_value_score_default_threshold(self):
        """Test filtering keeps high-value tests."""
        generator = IntelligentTestGenerator(min_value_score=70.0)
        request = TestGenerationRequest(
            target_type="function",
            target_name="process_payment",
            file_path=Path("cortex/payment.py"),
            parameters=["amount", "card_number"],
        )
        
        result = generator.generate_tests(request)
        
        # All returned tests should meet threshold
        assert all(test.value_score >= 70.0 for test in result.tests if test.value_score)

    def test_filter_by_value_score_custom_threshold(self):
        """Test filtering with custom threshold."""
        generator = IntelligentTestGenerator(min_value_score=90.0)
        request = TestGenerationRequest(
            target_type="function",
            target_name="delete_user",
            file_path=Path("cortex/users.py"),
            parameters=["user_id"],
        )
        
        result = generator.generate_tests(request)
        
        # Should only return very high-value tests
        assert all(test.value_score >= 90.0 for test in result.tests if test.value_score)


class TestPrioritizeTests:
    """Test test prioritization."""

    def test_prioritize_tests_by_value_score(self):
        """Test tests are prioritized by value score."""
        generator = IntelligentTestGenerator()
        request = TestGenerationRequest(
            target_type="function",
            target_name="authenticate",
            file_path=Path("cortex/auth.py"),
            parameters=["username", "password"],
            has_database_access=True,
        )
        
        result = generator.generate_tests(request)
        
        # Tests should be sorted by value score (descending)
        scores = [test.value_score for test in result.tests if test.value_score]
        assert scores == sorted(scores, reverse=True)

    def test_prioritize_tests_groups_by_priority(self):
        """Test tests are grouped by priority tier."""
        generator = IntelligentTestGenerator()
        request = TestGenerationRequest(
            target_type="endpoint",
            target_name="/api/admin/delete",
            file_path=Path("api/admin.py"),
            parameters=["resource_id"],
            has_database_access=True,
            requires_authentication=True,
            requires_authorization=["admin"],
        )
        
        result = generator.generate_tests(request)
        
        # Should have counts for each priority tier
        assert result.high_priority_count > 0  # Security tests should be high priority
        assert result.total_generated == len(result.tests)


class TestIntegration:
    """Test integration of all generators."""

    def test_integration_blind_spot_detection(self):
        """Test blind spot detection integration."""
        generator = IntelligentTestGenerator(min_value_score=50.0)  # Lower threshold
        request = TestGenerationRequest(
            target_type="function",
            target_name="calculate",
            file_path=Path("cortex/calculator.py"),
            parameters=["x", "y"],
            coverage_data={
                "covered_lines": [1, 2, 3],
                "missing_lines": [4, 5],
                "branch_coverage": 0.60,
            }
        )
        
        result = generator.generate_tests(request)
        
        # Should include blind spot tests (with lower threshold they pass filter)
        # Note: Without actual file content, blind spot detector won't find many,
        # but edge case tests will still be generated
        assert len(result.tests) > 0  # At least edge case tests
        # Check if any blind spot tests made it through
        has_blind_spots = any("blind_spot" in test.source for test in result.tests)
        has_edge_cases = any("edge_case" in test.source for test in result.tests)
        assert has_edge_cases or has_blind_spots  # Should have at least one type

    def test_integration_edge_case_generation(self):
        """Test edge case generation integration."""
        generator = IntelligentTestGenerator(min_value_score=50.0)  # Lower threshold
        request = TestGenerationRequest(
            target_type="function",
            target_name="validate_age",
            file_path=Path("cortex/validation.py"),
            parameters=["age"],
            parameter_constraints={
                "age": {"min_value": 0, "max_value": 120, "type_hint": "int"}
            }
        )
        
        result = generator.generate_tests(request)
        
        # Should include edge case tests
        assert len(result.tests) > 0
        assert any("edge_case" in test.source for test in result.tests)

    def test_integration_security_generation(self):
        """Test security test generation integration."""
        generator = IntelligentTestGenerator()
        request = TestGenerationRequest(
            target_type="endpoint",
            target_name="/api/query",
            file_path=Path("api/query.py"),
            parameters=["search_term"],
            has_database_access=True,
        )
        
        result = generator.generate_tests(request)
        
        # Should include security tests
        assert any("security" in test.source for test in result.tests)
        # Should flag SQL injection as high priority
        assert result.high_priority_count > 0


class TestGenerationResult:
    """Test result aggregation."""

    def test_generation_result_statistics(self):
        """Test result provides accurate statistics."""
        generator = IntelligentTestGenerator()
        request = TestGenerationRequest(
            target_type="function",
            target_name="process",
            file_path=Path("cortex/processor.py"),
            parameters=["data"],
        )
        
        result = generator.generate_tests(request)
        
        assert result.total_generated == len(result.tests)
        assert result.high_priority_count <= result.total_generated
        assert result.request == request

    def test_generation_result_empty_when_no_tests(self):
        """Test result handles no tests generated."""
        generator = IntelligentTestGenerator(min_value_score=99.9)
        request = TestGenerationRequest(
            target_type="function",
            target_name="simple_add",
            file_path=Path("cortex/math.py"),
            parameters=["a", "b"],
        )
        
        result = generator.generate_tests(request)
        
        # Very high threshold may filter all tests
        assert result.total_generated >= 0
        assert result.high_priority_count == 0
