"""
Tests for AC-TEST-002: Test Execution
"""

import pytest
from pathlib import Path
from src.infrastructure.test_executor import TestExecutor, TestResult


@pytest.fixture
def executor():
    """Create test executor instance."""
    return TestExecutor(test_dir=Path("tests"))


def test_test_result_creation():
    """TestResult can be created with data."""
    result = TestResult(
        ac_id="AC-TEST-002",
        passed=5,
        failed=0,
        skipped=1,
        total=6,
        success_rate=83.3
    )
    
    assert result.ac_id == "AC-TEST-002"
    assert result.passed == 5
    assert result.success_rate == 83.3


def test_test_result_to_dict():
    """TestResult converts to dictionary."""
    result = TestResult(
        ac_id="AC-TEST-002",
        passed=3,
        failed=1,
        skipped=0,
        total=4,
        success_rate=75.0
    )
    
    result_dict = result.to_dict()
    assert result_dict["ac_id"] == "AC-TEST-002"
    assert result_dict["passed"] == 3
    assert result_dict["total"] == 4


def test_executor_initialization(executor):
    """TestExecutor initializes with test directory."""
    assert executor.test_dir == Path("tests")


def test_run_all_tests_returns_dict(executor):
    """run_all_tests returns dictionary with statistics."""
    result = executor.run_all_tests()
    
    assert isinstance(result, dict)
    assert "total_tests" in result
    assert "passed" in result
    assert "failed" in result
    assert "success_rate" in result
    assert "exit_code" in result


def test_run_all_tests_counts_tests(executor):
    """run_all_tests counts tests correctly."""
    result = executor.run_all_tests()
    
    # Should find some tests
    assert result["total_tests"] > 0
    assert result["passed"] >= 0
    assert result["failed"] >= 0


def test_run_tests_for_ac(executor):
    """run_tests_for_ac returns TestResult for AC-ID."""
    result = executor.run_tests_for_ac("AC-TEST")
    
    assert isinstance(result, TestResult)
    assert result.ac_id == "AC-TEST"
    assert result.total >= 0
    assert result.success_rate >= 0
