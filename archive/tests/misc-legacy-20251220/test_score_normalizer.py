"""
Tests for Score Normalizer

TDD Phase: RED - Writing failing tests first

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from src.dashboard.reconciliation.normalizers.score_normalizer import ScoreNormalizer


class TestScoreNormalizer:
    """Test suite for ScoreNormalizer class."""
    
    @pytest.fixture
    def normalizer(self):
        """Create normalizer instance for tests."""
        return ScoreNormalizer()
    
    # Test: normalize_to_100 with different scales
    
    def test_normalize_to_100_from_10_scale(self, normalizer):
        """Test normalizing from 0-10 scale to 0-100."""
        assert normalizer.normalize_to_100(5.0, scale=10) == 50.0
        assert normalizer.normalize_to_100(7.5, scale=10) == 75.0
        assert normalizer.normalize_to_100(10.0, scale=10) == 100.0
        assert normalizer.normalize_to_100(0.0, scale=10) == 0.0
    
    def test_normalize_to_100_from_5_scale(self, normalizer):
        """Test normalizing from 0-5 scale to 0-100."""
        assert normalizer.normalize_to_100(2.5, scale=5) == 50.0
        assert normalizer.normalize_to_100(5.0, scale=5) == 100.0
        assert normalizer.normalize_to_100(0.0, scale=5) == 0.0
    
    def test_normalize_to_100_already_100(self, normalizer):
        """Test normalizing values already in 0-100 scale."""
        assert normalizer.normalize_to_100(50.0, scale=100) == 50.0
        assert normalizer.normalize_to_100(100.0, scale=100) == 100.0
        assert normalizer.normalize_to_100(0.0, scale=100) == 0.0
    
    def test_normalize_to_100_edge_cases(self, normalizer):
        """Test edge cases for normalization."""
        # Negative values should raise ValueError
        with pytest.raises(ValueError):
            normalizer.normalize_to_100(-5.0, scale=10)
        
        # Value exceeding scale should raise ValueError
        with pytest.raises(ValueError):
            normalizer.normalize_to_100(11.0, scale=10)
        
        # Invalid scale should raise ValueError
        with pytest.raises(ValueError):
            normalizer.normalize_to_100(5.0, scale=0)
        
        with pytest.raises(ValueError):
            normalizer.normalize_to_100(5.0, scale=-10)
    
    # Test: normalize_percentage
    
    def test_normalize_percentage_decimal(self, normalizer):
        """Test normalizing decimal percentage (0.0-1.0) to 0-100."""
        assert normalizer.normalize_percentage(0.5) == 50.0
        assert normalizer.normalize_percentage(0.85) == 85.0
        assert normalizer.normalize_percentage(1.0) == 100.0
        assert normalizer.normalize_percentage(0.0) == 0.0
    
    def test_normalize_percentage_already_100(self, normalizer):
        """Test normalizing percentage already in 0-100 range."""
        assert normalizer.normalize_percentage(50.0) == 50.0
        assert normalizer.normalize_percentage(85.0) == 85.0
        assert normalizer.normalize_percentage(100.0) == 100.0
    
    def test_normalize_percentage_edge_cases(self, normalizer):
        """Test edge cases for percentage normalization."""
        # Negative should raise ValueError
        with pytest.raises(ValueError):
            normalizer.normalize_percentage(-0.5)
        
        # Greater than 100 should raise ValueError
        with pytest.raises(ValueError):
            normalizer.normalize_percentage(105.0)
    
    # Test: normalize_severity
    
    def test_normalize_severity_valid_strings(self, normalizer):
        """Test normalizing severity strings to numeric scores."""
        assert normalizer.normalize_severity('critical') == 100.0
        assert normalizer.normalize_severity('high') == 75.0
        assert normalizer.normalize_severity('medium') == 50.0
        assert normalizer.normalize_severity('low') == 25.0
        assert normalizer.normalize_severity('none') == 0.0
    
    def test_normalize_severity_case_insensitive(self, normalizer):
        """Test severity normalization is case-insensitive."""
        assert normalizer.normalize_severity('CRITICAL') == 100.0
        assert normalizer.normalize_severity('High') == 75.0
        assert normalizer.normalize_severity('MeDiUm') == 50.0
    
    def test_normalize_severity_invalid(self, normalizer):
        """Test invalid severity strings raise ValueError."""
        with pytest.raises(ValueError):
            normalizer.normalize_severity('invalid')
        
        with pytest.raises(ValueError):
            normalizer.normalize_severity('')
        
        with pytest.raises(ValueError):
            normalizer.normalize_severity('moderate')  # Not a standard severity
    
    # Test: denormalize_to_severity
    
    def test_denormalize_to_severity(self, normalizer):
        """Test converting numeric scores back to severity strings."""
        assert normalizer.denormalize_to_severity(95) == 'critical'
        assert normalizer.denormalize_to_severity(100) == 'critical'
        assert normalizer.denormalize_to_severity(80) == 'high'
        assert normalizer.denormalize_to_severity(70) == 'high'
        assert normalizer.denormalize_to_severity(60) == 'medium'
        assert normalizer.denormalize_to_severity(40) == 'medium'
        assert normalizer.denormalize_to_severity(30) == 'low'
        assert normalizer.denormalize_to_severity(10) == 'low'
        assert normalizer.denormalize_to_severity(0) == 'none'
    
    def test_denormalize_to_severity_edge_cases(self, normalizer):
        """Test edge cases for denormalization."""
        # Boundary values
        assert normalizer.denormalize_to_severity(90) == 'critical'  # >= 90
        assert normalizer.denormalize_to_severity(89) == 'high'      # < 90
        assert normalizer.denormalize_to_severity(70) == 'high'      # >= 70
        assert normalizer.denormalize_to_severity(69) == 'medium'    # < 70
        
        # Invalid range
        with pytest.raises(ValueError):
            normalizer.denormalize_to_severity(-10)
        
        with pytest.raises(ValueError):
            normalizer.denormalize_to_severity(105)
    
    # Test: clamp_score
    
    def test_clamp_score_within_range(self, normalizer):
        """Test clamping scores within valid range."""
        assert normalizer.clamp_score(50.0) == 50.0
        assert normalizer.clamp_score(0.0) == 0.0
        assert normalizer.clamp_score(100.0) == 100.0
    
    def test_clamp_score_outside_range(self, normalizer):
        """Test clamping scores outside valid range."""
        assert normalizer.clamp_score(-10.0) == 0.0
        assert normalizer.clamp_score(150.0) == 100.0
        assert normalizer.clamp_score(-50.0) == 0.0
        assert normalizer.clamp_score(999.0) == 100.0
    
    # Test: round_score
    
    def test_round_score_precision(self, normalizer):
        """Test score rounding to specified precision."""
        assert normalizer.round_score(75.4567, precision=1) == 75.5
        assert normalizer.round_score(75.4567, precision=2) == 75.46
        assert normalizer.round_score(75.4567, precision=0) == 75.0
        assert normalizer.round_score(75.0, precision=1) == 75.0
