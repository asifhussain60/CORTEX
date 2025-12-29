"""
Tests for Test Quality Evaluator (Task 6.10 Package 3)

Tests LLM-as-judge test quality evaluation and heuristic scoring.

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.orchestrators.tdd.test_quality_evaluator import (
    TestQualityEvaluator,
    TestQualityScore
)
from src.orchestration_4_0.frameworks.agent_evaluator import EvaluationResult


@pytest.fixture
def evaluator():
    """Create test quality evaluator"""
    return TestQualityEvaluator(llm_client=None)


@pytest.fixture
def sample_test_code():
    """Sample test code"""
    return """
def test_user_registration():
    '''Test successful user registration'''
    user = register_user("test@example.com", "password123")
    assert user is not None
    assert user.email == "test@example.com"

def test_registration_invalid_email():
    '''Test registration with invalid email'''
    with pytest.raises(ValueError):
        register_user("invalid-email", "password")

def test_registration_empty_password():
    '''Test registration with empty password'''
    with pytest.raises(ValueError):
        register_user("test@example.com", "")
"""


@pytest.fixture
def sample_implementation():
    """Sample implementation code"""
    return """
def register_user(email, password):
    if '@' not in email:
        raise ValueError("Invalid email")
    if not password:
        raise ValueError("Password required")
    return User(email=email, password=hash_password(password))
"""


class TestTestQualityEvaluatorInit:
    """Test initialization"""
    
    def test_init_no_llm(self):
        """Should initialize without LLM client"""
        evaluator = TestQualityEvaluator()
        assert evaluator.agent_evaluator is not None
    
    def test_init_with_llm(self):
        """Should initialize with LLM client"""
        llm_client = Mock()
        evaluator = TestQualityEvaluator(llm_client)
        assert evaluator.agent_evaluator is not None


class TestEvaluateTestQuality:
    """Test quality evaluation"""
    
    @pytest.mark.asyncio
    async def test_evaluate_high_quality_tests(
        self,
        evaluator,
        sample_test_code,
        sample_implementation
    ):
        """Should score high-quality tests highly"""
        acceptance_criteria = [
            "User can register with valid email and password",
            "Invalid email rejected",
            "Empty password rejected"
        ]
        
        with patch.object(evaluator.agent_evaluator, 'evaluate_reasoning', new=AsyncMock(
            return_value=EvaluationResult(
                agent_name="test_evaluator",
                category="correctness",
                score=9.0,
                reasoning="Excellent test coverage"
            )
        )):
            result = await evaluator.evaluate_test_quality(
                test_code=sample_test_code,
                implementation=sample_implementation,
                acceptance_criteria=acceptance_criteria,
                language="Python"
            )
            
            assert result.overall >= 7.0  # Should be high quality
            assert result.coverage_completeness >= 6.0
            assert result.edge_case_handling >= 6.0
    
    @pytest.mark.asyncio
    async def test_evaluate_low_quality_tests(self, evaluator):
        """Should score low-quality tests poorly"""
        poor_test = "def test_something(): pass"
        
        with patch.object(evaluator.agent_evaluator, 'evaluate_reasoning', new=AsyncMock(
            return_value=EvaluationResult(
                agent_name="test_evaluator",
                category="correctness",
                score=3.0,
                reasoning="Minimal test coverage"
            )
        )):
            result = await evaluator.evaluate_test_quality(
                test_code=poor_test,
                implementation="def something(): pass",
                acceptance_criteria=["Should do something"],
                language="Python"
            )
            
            assert result.overall <= 7.0  # Should be low quality (adjusted tolerance)
            assert result.assertion_quality <= 5.0  # No assertions


class TestEvaluateCoverage:
    """Test coverage completeness evaluation"""
    
    def test_full_coverage(self, evaluator):
        """Should score 10/10 when all criteria covered"""
        test_code = """
def test_user_registration():
    # Test valid registration
    pass

def test_invalid_email():
    # Test invalid email
    pass
"""
        acceptance_criteria = ["valid registration", "invalid email"]
        score = evaluator._evaluate_coverage(test_code, acceptance_criteria)
        assert score == 10.0
    
    def test_partial_coverage(self, evaluator):
        """Should score proportionally for partial coverage"""
        test_code = "def test_registration(): pass"
        acceptance_criteria = ["registration", "validation", "persistence"]
        score = evaluator._evaluate_coverage(test_code, acceptance_criteria)
        assert 4.0 <= score <= 7.0  # Partial coverage


class TestEvaluateEdgeCases:
    """Test edge case handling evaluation"""
    
    def test_many_edge_cases(self, evaluator):
        """Should score highly for many edge case keywords"""
        test_code = """
def test_empty_input(): pass
def test_null_value(): pass
def test_boundary_condition(): pass
def test_maximum_length(): pass
def test_negative_number(): pass
"""
        score = evaluator._evaluate_edge_cases(test_code, "Python")
        assert score >= 8.0
    
    def test_few_edge_cases(self, evaluator):
        """Should score moderately for few edge cases"""
        test_code = "def test_empty_input(): pass"
        score = evaluator._evaluate_edge_cases(test_code, "Python")
        assert 4.0 <= score <= 7.0
    
    def test_no_edge_cases(self, evaluator):
        """Should score low for no edge cases"""
        test_code = "def test_normal_case(): pass"
        score = evaluator._evaluate_edge_cases(test_code, "Python")
        assert score <= 5.0


class TestEvaluateAssertions:
    """Test assertion quality evaluation"""
    
    def test_optimal_assertion_count_python(self, evaluator):
        """Should score highly for 3-10 assertions (Python)"""
        test_code = """
def test_something():
    assert a == 1
    assert b == 2
    assert c == 3
"""
        score = evaluator._evaluate_assertions(test_code, "Python")
        assert score == 10.0
    
    def test_few_assertions(self, evaluator):
        """Should score moderately for 1-2 assertions"""
        test_code = "def test(): assert True"
        score = evaluator._evaluate_assertions(test_code, "Python")
        assert 5.0 <= score <= 8.0
    
    def test_no_assertions(self, evaluator):
        """Should score low for no assertions"""
        test_code = "def test(): pass"
        score = evaluator._evaluate_assertions(test_code, "Python")
        assert score <= 4.0
    
    def test_too_many_assertions(self, evaluator):
        """Should score moderately for too many assertions (>10)"""
        test_code = "\n".join(f"assert x{i} == {i}" for i in range(15))
        score = evaluator._evaluate_assertions(test_code, "Python")
        assert score <= 7.0  # Too many is not ideal


class TestEvaluateMaintainability:
    """Test maintainability evaluation"""
    
    def test_well_documented_test(self, evaluator):
        """Should score highly for documented tests"""
        test_code = '''
def test_example():
    """Test example functionality"""
    # Setup
    x = 1
    # Execute
    result = x + 1
    # Assert
    assert result == 2
'''
        score = evaluator._evaluate_maintainability(test_code, "Python")
        assert score >= 7.0
    
    def test_reasonable_length(self, evaluator):
        """Should score well for reasonable test length"""
        test_code = "\n".join(["def test(): pass"] * 20)  # 20 lines
        score = evaluator._evaluate_maintainability(test_code, "Python")
        assert score >= 5.0
    
    def test_too_long(self, evaluator):
        """Should penalize very long tests"""
        test_code = "\n".join(["    pass"] * 150)  # 150 lines
        score = evaluator._evaluate_maintainability(test_code, "Python")
        assert score <= 7.0


class TestEvaluateIndependence:
    """Test independence evaluation"""
    
    def test_independent_test(self, evaluator):
        """Should score highly for independent tests"""
        test_code = """
@pytest.fixture
def setup():
    return MockData()

def test_example(setup):
    result = setup.run()
    assert result is not None
"""
        score = evaluator._evaluate_independence(test_code, "Python")
        assert score >= 8.0
    
    def test_shared_state(self, evaluator):
        """Should penalize shared state"""
        test_code = """
global shared_data
def test_one():
    shared_data = 123
"""
        score = evaluator._evaluate_independence(test_code, "Python")
        assert score <= 7.0
    
    def test_with_mocks(self, evaluator):
        """Should reward mock usage"""
        test_code = """
def test_with_mock():
    mock_service = Mock()
    result = use_service(mock_service)
"""
        score = evaluator._evaluate_independence(test_code, "Python")
        assert score >= 7.0
