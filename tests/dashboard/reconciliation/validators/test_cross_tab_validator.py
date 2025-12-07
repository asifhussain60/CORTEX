"""
Tests for Cross-Tab Validator

TDD Phase: RED - Writing failing tests for cross-tab validation rules.
Tests rules R8-R10: security-quality correlation, architecture-security alignment, 
maintainability-complexity inverse relationships.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from src.dashboard.reconciliation.validators.cross_tab_validator import CrossTabValidator
from src.dashboard.reconciliation.models import Violation


class TestCrossTabValidator:
    """Test suite for CrossTabValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance for tests."""
        return CrossTabValidator()
    
    # Test: R8 - Security-Quality Correlation
    
    def test_r8_both_low_triggers_violation(self, validator):
        """R8: Security < 50 AND Quality < 50 should cap overall at 50."""
        data = {
            'security': {'score': 35},
            'quality': {'score': 40},
            'overall_score': 75
        }
        
        violations = validator.validate_security_quality_correlation(data)
        
        assert len(violations) == 1
        assert violations[0].rule_id == 'R8'
        assert violations[0].severity == 'high'
        assert violations[0].adjusted_score == 50
    
    def test_r8_only_security_low_no_violation(self, validator):
        """R8: Only security low (quality ok) should not trigger."""
        data = {
            'security': {'score': 35},
            'quality': {'score': 70},
            'overall_score': 75
        }
        
        violations = validator.validate_security_quality_correlation(data)
        
        assert len(violations) == 0
    
    def test_r8_only_quality_low_no_violation(self, validator):
        """R8: Only quality low (security ok) should not trigger."""
        data = {
            'security': {'score': 70},
            'quality': {'score': 35},
            'overall_score': 75
        }
        
        violations = validator.validate_security_quality_correlation(data)
        
        assert len(violations) == 0
    
    def test_r8_both_high_no_violation(self, validator):
        """R8: Both security and quality high should not trigger."""
        data = {
            'security': {'score': 80},
            'quality': {'score': 85},
            'overall_score': 90
        }
        
        violations = validator.validate_security_quality_correlation(data)
        
        assert len(violations) == 0
    
    # Test: R9 - Architecture-Security Alignment
    
    def test_r9_architecture_high_security_low_anomaly(self, validator):
        """R9: High architecture (>80) with low security (<40) is anomalous."""
        data = {
            'architecture': {'score': 85},
            'security': {'score': 30}
        }
        
        anomalies = validator.validate_architecture_security_alignment(data)
        
        assert len(anomalies) == 1
        assert anomalies[0].type == 'score_inconsistency'
        assert anomalies[0].confidence >= 0.8
        assert 'architecture' in anomalies[0].message.lower()
    
    def test_r9_both_aligned_no_anomaly(self, validator):
        """R9: Architecture and security aligned should not trigger."""
        data = {
            'architecture': {'score': 75},
            'security': {'score': 70}
        }
        
        anomalies = validator.validate_architecture_security_alignment(data)
        
        assert len(anomalies) == 0
    
    def test_r9_both_low_no_anomaly(self, validator):
        """R9: Both low is consistent, should not trigger."""
        data = {
            'architecture': {'score': 35},
            'security': {'score': 30}
        }
        
        anomalies = validator.validate_architecture_security_alignment(data)
        
        assert len(anomalies) == 0
    
    # Test: R10 - Maintainability-Complexity Inverse
    
    def test_r10_high_complexity_high_maintainability_violation(self, validator):
        """R10: High complexity (>15) with high maintainability (>80) should adjust."""
        data = {
            'maintainability': {'score': 85},
            'health': {
                'summary': {'average_complexity': 18.5}
            }
        }
        
        violations = validator.validate_maintainability_complexity_inverse(data)
        
        assert len(violations) == 1
        assert violations[0].rule_id == 'R10_MAINTAINABILITY_COMPLEXITY_INVERSE'
        assert violations[0].adjusted_score == 70
        assert violations[0].adjustment < 0  # Score reduced
    
    def test_r10_low_complexity_high_maintainability_ok(self, validator):
        """R10: Low complexity with high maintainability is valid."""
        data = {
            'maintainability': {'score': 85},
            'health': {
                'summary': {'average_complexity': 6.5}
            }
        }
        
        violations = validator.validate_maintainability_complexity_inverse(data)
        
        assert len(violations) == 0
    
    def test_r10_high_complexity_low_maintainability_ok(self, validator):
        """R10: High complexity with already low maintainability is consistent."""
        data = {
            'maintainability': {'score': 55},
            'health': {
                'summary': {'average_complexity': 18.5}
            }
        }
        
        violations = validator.validate_maintainability_complexity_inverse(data)
        
        assert len(violations) == 0
    
    # Test: validate_all (integrated)
    
    def test_validate_all_multiple_violations(self, validator):
        """Test validate_all finds multiple cross-tab issues."""
        data = {
            'security': {'score': 35},
            'quality': {'score': 40},
            'architecture': {'score': 85},
            'maintainability': {'score': 85},
            'overall_score': 75,
            'health': {
                'summary': {'average_complexity': 18.5}
            }
        }
        
        violations, anomalies = validator.validate_all(data)
        
        # Should have R8 violation and R10 violation
        assert len(violations) == 2
        # Should have R9 anomaly
        assert len(anomalies) == 1
    
    def test_validate_all_clean_data(self, validator):
        """Test validate_all with consistent data."""
        data = {
            'security': {'score': 75},
            'quality': {'score': 80},
            'architecture': {'score': 78},
            'maintainability': {'score': 72},
            'overall_score': 75,
            'health': {
                'summary': {'average_complexity': 8.5}
            }
        }
        
        violations, anomalies = validator.validate_all(data)
        
        assert len(violations) == 0
        assert len(anomalies) == 0
