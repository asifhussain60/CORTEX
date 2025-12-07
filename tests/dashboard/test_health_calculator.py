"""
Tests for Health Score Calculator

Test suite for calculating overall health scores and status classification.
TDD Phase: RED - Write failing tests first.
"""

import pytest
from src.dashboard.data.health_calculator import HealthScoreCalculator


class TestHealthScoreCalculator:
    """Test suite for HealthScoreCalculator class."""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance with default weights."""
        return HealthScoreCalculator()
    
    def test_calculate_overall_score_with_all_categories(self, calculator):
        """Test overall score calculation with all categories."""
        scores = {
            "code_quality": 88,
            "security": 96,
            "tests": 82,
            "documentation": 75
        }
        result = calculator.calculate_overall_score(scores)
        # Expected: 88*0.3 + 96*0.3 + 82*0.25 + 75*0.15 = 26.4 + 28.8 + 20.5 + 11.25 = 86.95
        assert result == pytest.approx(86.95, rel=0.01)
    
    def test_calculate_overall_score_with_perfect_scores(self, calculator):
        """Test overall score with all perfect 100s."""
        scores = {
            "code_quality": 100,
            "security": 100,
            "tests": 100,
            "documentation": 100
        }
        result = calculator.calculate_overall_score(scores)
        assert result == 100.0
    
    def test_calculate_overall_score_with_zero_scores(self, calculator):
        """Test overall score with all zeros."""
        scores = {
            "code_quality": 0,
            "security": 0,
            "tests": 0,
            "documentation": 0
        }
        result = calculator.calculate_overall_score(scores)
        assert result == 0.0
    
    def test_determine_status_healthy(self, calculator):
        """Test status determination for healthy score (>=80)."""
        assert calculator.determine_status(92) == "healthy"
        assert calculator.determine_status(80) == "healthy"
        assert calculator.determine_status(100) == "healthy"
    
    def test_determine_status_warning(self, calculator):
        """Test status determination for warning score (50-79)."""
        assert calculator.determine_status(75) == "warning"
        assert calculator.determine_status(50) == "warning"
        assert calculator.determine_status(79) == "warning"
    
    def test_determine_status_critical(self, calculator):
        """Test status determination for critical score (<50)."""
        assert calculator.determine_status(49) == "critical"
        assert calculator.determine_status(25) == "critical"
        assert calculator.determine_status(0) == "critical"
    
    def test_custom_weights_calculation(self):
        """Test calculation with custom category weights."""
        custom_weights = {
            "code_quality": 0.4,
            "security": 0.4,
            "tests": 0.1,
            "documentation": 0.1
        }
        calculator = HealthScoreCalculator(weights=custom_weights)
        scores = {
            "code_quality": 80,
            "security": 90,
            "tests": 70,
            "documentation": 60
        }
        # Expected: 80*0.4 + 90*0.4 + 70*0.1 + 60*0.1 = 32 + 36 + 7 + 6 = 81
        result = calculator.calculate_overall_score(scores)
        assert result == pytest.approx(81.0, rel=0.01)
    
    def test_weights_sum_to_one_validation(self):
        """Test that weights must sum to 1.0."""
        invalid_weights = {
            "code_quality": 0.5,
            "security": 0.5,
            "tests": 0.5,  # Sum > 1.0
            "documentation": 0.5
        }
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            HealthScoreCalculator(weights=invalid_weights)
    
    def test_missing_score_category_raises_error(self, calculator):
        """Test that missing score category raises error."""
        incomplete_scores = {
            "code_quality": 88,
            "security": 96
            # Missing tests and documentation
        }
        with pytest.raises(KeyError):
            calculator.calculate_overall_score(incomplete_scores)
    
    def test_calculate_category_status_for_each_score(self, calculator):
        """Test status determination for multiple categories."""
        category_scores = {
            "code_quality": 88,   # healthy
            "security": 96,       # healthy
            "tests": 75,          # warning
            "documentation": 45   # critical
        }
        
        statuses = {}
        for category, score in category_scores.items():
            statuses[category] = calculator.determine_status(score)
        
        assert statuses["code_quality"] == "healthy"
        assert statuses["security"] == "healthy"
        assert statuses["tests"] == "warning"
        assert statuses["documentation"] == "critical"
