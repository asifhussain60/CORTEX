"""Phase S5: Testing Tab (🧪) - TDD Test Suite
Tests for test coverage, code quality, and testing metrics
"""

import pytest
from pydantic import ValidationError
from cortex.orchestrators.onboarding.dashboard_schema_models import TestingTab


@pytest.fixture
def valid_testing():
    """Valid testing metrics"""
    return {
        "coverage_percentage": 85.5,
        "coverage_trend": [
            {"date": "2026-02-01", "value": 80.0},
            {"date": "2026-02-08", "value": 85.5}
        ],
        "test_counts": {
            "total": 450,
            "passing": 445,
            "failing": 2,
            "skipped": 3
        },
        "test_types": {
            "unit": 300,
            "integration": 120,
            "e2e": 30
        },
        "failing_tests": [
            {
                "name": "test_critical_workflow",
                "file": "tests/test_workflow.py",
                "error": "Timeout after 30s",
                "priority": "high"
            }
        ],
        "coverage_by_module": {
            "core": 92.0,
            "api": 85.0,
            "utils": 78.0
        }
    }


class TestCoveragePercentage:
    """Test coverage percentage validation"""
    
    def test_valid_coverage(self, valid_testing):
        """Test valid coverage percentage"""
        testing = TestingTab(**valid_testing)
        assert testing.coverage_percentage == 85.5
        assert 0 <= testing.coverage_percentage <= 100
    
    def test_zero_coverage(self):
        """Test zero coverage"""
        data = {
            "coverage_percentage": 0.0,
            "coverage_trend": [],
            "test_counts": {"total": 0, "passing": 0, "failing": 0, "skipped": 0},
            "test_types": {"unit": 0, "integration": 0, "e2e": 0},
            "failing_tests": [],
            "coverage_by_module": {}
        }
        testing = TestingTab(**data)
        assert testing.coverage_percentage == 0.0
    
    def test_perfect_coverage(self):
        """Test 100% coverage"""
        data = {
            "coverage_percentage": 100.0,
            "coverage_trend": [],
            "test_counts": {"total": 100, "passing": 100, "failing": 0, "skipped": 0},
            "test_types": {"unit": 60, "integration": 30, "e2e": 10},
            "failing_tests": [],
            "coverage_by_module": {}
        }
        testing = TestingTab(**data)
        assert testing.coverage_percentage == 100.0
    
    def test_coverage_exceeds_100(self):
        """Test coverage exceeding 100% (invalid)"""
        data = {
            "coverage_percentage": 105.0,
            "coverage_trend": [],
            "test_counts": {"total": 0, "passing": 0, "failing": 0, "skipped": 0},
            "test_types": {"unit": 0, "integration": 0, "e2e": 0},
            "failing_tests": [],
            "coverage_by_module": {}
        }
        with pytest.raises(ValidationError):
            TestingTab(**data)


class TestCoverageTrend:
    """Test coverage trend tracking"""
    
    def test_coverage_trend_list(self, valid_testing):
        """Test coverage trend is list"""
        testing = TestingTab(**valid_testing)
        assert isinstance(testing.coverage_trend, list)
    
    def test_trend_with_dates(self, valid_testing):
        """Test trend points have dates"""
        testing = TestingTab(**valid_testing)
        if testing.coverage_trend:
            for point in testing.coverage_trend:
                assert hasattr(point, 'date')
                assert hasattr(point, 'value')


class TestCounts:
    """Test execution count validation"""
    
    def test_test_counts(self, valid_testing):
        """Test count structure"""
        testing = TestingTab(**valid_testing)
        counts = testing.test_counts
        assert counts.total == 450
        assert counts.passing == 445
        assert counts.failing == 2
        assert counts.skipped == 3
    
    def test_passing_less_than_total(self, valid_testing):
        """Test passing <= total"""
        testing = TestingTab(**valid_testing)
        total = testing.test_counts.total
        passing = testing.test_counts.passing
        assert passing <= total
    
    def test_sum_matches_total(self, valid_testing):
        """Test sum of test states equals total"""
        testing = TestingTab(**valid_testing)
        counts = testing.test_counts
        calculated = counts.passing + counts.failing + counts.skipped
        assert calculated == counts.total


class TestTypes:
    """Test type breakdown"""
    
    def test_test_types(self, valid_testing):
        """Test type breakdown"""
        testing = TestingTab(**valid_testing)
        types = testing.test_types
        assert types.unit == 300
        assert types.integration == 120
        assert types.e2e == 30
    
    def test_types_non_negative(self, valid_testing):
        """Test all test types non-negative"""
        testing = TestingTab(**valid_testing)
        types = testing.test_types
        assert types.unit >= 0
        assert types.integration >= 0
        assert types.e2e >= 0


class TestFailingTests:
    """Test failing test tracking"""
    
    def test_failing_tests_list(self, valid_testing):
        """Test failing tests list"""
        testing = TestingTab(**valid_testing)
        assert isinstance(testing.failing_tests, list)
    
    def test_failing_test_structure(self, valid_testing):
        """Test failing test has required fields"""
        testing = TestingTab(**valid_testing)
        if testing.failing_tests:
            ft = testing.failing_tests[0]
            assert ft.name is not None
            assert ft.file is not None
            assert ft.error is not None
    
    def test_no_failing_tests(self):
        """Test no failing tests"""
        data = {
            "coverage_percentage": 95.0,
            "coverage_trend": [],
            "test_counts": {"total": 100, "passing": 100, "failing": 0, "skipped": 0},
            "test_types": {"unit": 60, "integration": 30, "e2e": 10},
            "failing_tests": [],
            "coverage_by_module": {}
        }
        testing = TestingTab(**data)
        assert len(testing.failing_tests) == 0


class TestCoverageByModule:
    """Test module coverage tracking"""
    
    def test_coverage_by_module(self, valid_testing):
        """Test module coverage dict"""
        testing = TestingTab(**valid_testing)
        assert isinstance(testing.coverage_by_module, dict)
    
    def test_module_coverage_range(self, valid_testing):
        """Test module coverage in valid range"""
        testing = TestingTab(**valid_testing)
        for module, coverage in testing.coverage_by_module.items():
            assert 0 <= coverage <= 100


class TestQualityEdgeCases:
    """Test edge cases"""
    
    def test_all_tests_passing(self):
        """Test all tests passing"""
        data = {
            "coverage_percentage": 95.0,
            "coverage_trend": [],
            "test_counts": {"total": 500, "passing": 500, "failing": 0, "skipped": 0},
            "test_types": {"unit": 300, "integration": 150, "e2e": 50},
            "failing_tests": [],
            "coverage_by_module": {"core": 95.0, "api": 95.0, "utils": 95.0}
        }
        testing = TestingTab(**data)
        assert testing.test_counts.failing == 0
    
    def test_many_failing_tests(self):
        """Test many failing tests"""
        failing = [
            {
                "name": f"test_case_{i}",
                "file": f"tests/test_{i}.py",
                "error": f"Error {i}",
                "priority": "high" if i % 2 == 0 else "medium"
            }
            for i in range(50)
        ]
        data = {
            "coverage_percentage": 30.0,
            "coverage_trend": [],
            "test_counts": {"total": 100, "passing": 50, "failing": 50, "skipped": 0},
            "test_types": {"unit": 50, "integration": 30, "e2e": 20},
            "failing_tests": failing,
            "coverage_by_module": {}
        }
        testing = TestingTab(**data)
        assert len(testing.failing_tests) == 50
