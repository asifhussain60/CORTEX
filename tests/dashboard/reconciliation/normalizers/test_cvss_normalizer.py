"""
Tests for CVSS Normalizer

TDD Phase: RED - Writing failing tests first
Tests CVSS v3.1/v4.0 score normalization per NIST standards.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from src.dashboard.reconciliation.normalizers.cvss_normalizer import CVSSNormalizer


class TestCVSSNormalizer:
    """Test suite for CVSSNormalizer class."""
    
    @pytest.fixture
    def normalizer(self):
        """Create normalizer instance for tests."""
        return CVSSNormalizer()
    
    # Test: cvss_to_100 conversion
    
    def test_cvss_to_100_critical_range(self, normalizer):
        """Test CVSS Critical range (9.0-10.0) maps to 90-100."""
        assert normalizer.cvss_to_100(10.0) == 100.0
        assert normalizer.cvss_to_100(9.5) == 95.0
        assert normalizer.cvss_to_100(9.0) == 90.0
    
    def test_cvss_to_100_high_range(self, normalizer):
        """Test CVSS High range (7.0-8.9) maps to 70-89."""
        assert normalizer.cvss_to_100(8.9) == 89.0
        assert normalizer.cvss_to_100(8.0) == 80.0
        assert normalizer.cvss_to_100(7.0) == 70.0
    
    def test_cvss_to_100_medium_range(self, normalizer):
        """Test CVSS Medium range (4.0-6.9) maps to 40-69."""
        assert normalizer.cvss_to_100(6.9) == 69.0
        assert normalizer.cvss_to_100(5.0) == 50.0
        assert normalizer.cvss_to_100(4.0) == 40.0
    
    def test_cvss_to_100_low_range(self, normalizer):
        """Test CVSS Low range (0.1-3.9) maps to 1-39."""
        assert normalizer.cvss_to_100(3.9) == 39.0
        assert normalizer.cvss_to_100(2.0) == 20.0
        assert normalizer.cvss_to_100(0.1) == 1.0
    
    def test_cvss_to_100_none(self, normalizer):
        """Test CVSS None (0.0) maps to 0."""
        assert normalizer.cvss_to_100(0.0) == 0.0
    
    def test_cvss_to_100_edge_cases(self, normalizer):
        """Test edge cases for CVSS conversion."""
        # Negative should raise ValueError
        with pytest.raises(ValueError):
            normalizer.cvss_to_100(-1.0)
        
        # Above 10.0 should raise ValueError
        with pytest.raises(ValueError):
            normalizer.cvss_to_100(10.5)
    
    # Test: severity_to_cvss
    
    def test_severity_to_cvss_midpoints(self, normalizer):
        """Test severity strings map to CVSS midpoints."""
        assert normalizer.severity_to_cvss('critical') == 9.5
        assert normalizer.severity_to_cvss('high') == 7.95
        assert normalizer.severity_to_cvss('medium') == 5.45
        assert normalizer.severity_to_cvss('low') == 2.0
        assert normalizer.severity_to_cvss('none') == 0.0
    
    def test_severity_to_cvss_case_insensitive(self, normalizer):
        """Test severity to CVSS is case-insensitive."""
        assert normalizer.severity_to_cvss('CRITICAL') == 9.5
        assert normalizer.severity_to_cvss('High') == 7.95
    
    def test_severity_to_cvss_invalid(self, normalizer):
        """Test invalid severity raises ValueError."""
        with pytest.raises(ValueError):
            normalizer.severity_to_cvss('invalid')
    
    # Test: get_severity_from_cvss
    
    def test_get_severity_from_cvss(self, normalizer):
        """Test getting severity category from CVSS score."""
        assert normalizer.get_severity_from_cvss(10.0) == 'critical'
        assert normalizer.get_severity_from_cvss(9.5) == 'critical'
        assert normalizer.get_severity_from_cvss(9.0) == 'critical'
        assert normalizer.get_severity_from_cvss(8.9) == 'high'
        assert normalizer.get_severity_from_cvss(7.0) == 'high'
        assert normalizer.get_severity_from_cvss(6.9) == 'medium'
        assert normalizer.get_severity_from_cvss(4.0) == 'medium'
        assert normalizer.get_severity_from_cvss(3.9) == 'low'
        assert normalizer.get_severity_from_cvss(0.1) == 'low'
        assert normalizer.get_severity_from_cvss(0.0) == 'none'
    
    # Test: get_severity_range
    
    def test_get_severity_range(self, normalizer):
        """Test getting CVSS score ranges for severities."""
        assert normalizer.get_severity_range('critical') == (9.0, 10.0)
        assert normalizer.get_severity_range('high') == (7.0, 8.9)
        assert normalizer.get_severity_range('medium') == (4.0, 6.9)
        assert normalizer.get_severity_range('low') == (0.1, 3.9)
        assert normalizer.get_severity_range('none') == (0.0, 0.0)
    
    def test_get_severity_range_invalid(self, normalizer):
        """Test invalid severity raises ValueError."""
        with pytest.raises(ValueError):
            normalizer.get_severity_range('invalid')
    
    # Test: normalize_vulnerability_impact
    
    def test_normalize_vulnerability_impact(self, normalizer):
        """Test vulnerability impact weight calculation."""
        assert normalizer.normalize_vulnerability_impact('critical') == 1.0
        assert normalizer.normalize_vulnerability_impact('high') == 0.7
        assert normalizer.normalize_vulnerability_impact('medium') == 0.4
        assert normalizer.normalize_vulnerability_impact('low') == 0.1
        assert normalizer.normalize_vulnerability_impact('none') == 0.0
    
    def test_normalize_vulnerability_impact_invalid(self, normalizer):
        """Test invalid severity raises ValueError."""
        with pytest.raises(ValueError):
            normalizer.normalize_vulnerability_impact('invalid')
