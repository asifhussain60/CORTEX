"""
SKULL Test: SKULL_TRANSFORMATION_VERIFICATION
Automated enforcement testing for SKULL_TRANSFORMATION_VERIFICATION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSkullTransformationVerification:
    """Test suite for SKULL_TRANSFORMATION_VERIFICATION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_skull_transformation_verification_detects_violation(self):
        """Test detection of SKULL_TRANSFORMATION_VERIFICATION violation."""
        result = self.skull.check_rule('SKULL_TRANSFORMATION_VERIFICATION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SKULL_TRANSFORMATION_VERIFICATION'
    
    def test_skull_transformation_verification_validates_compliance(self):
        """Test validation of SKULL_TRANSFORMATION_VERIFICATION compliance."""
        result = self.skull.check_rule('SKULL_TRANSFORMATION_VERIFICATION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_skull_transformation_verification_blocks_on_violation(self):
        """Test that SKULL_TRANSFORMATION_VERIFICATION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SKULL_TRANSFORMATION_VERIFICATION', operation, violates=True, severity="blocked")
    
    def test_skull_transformation_verification_allows_compliant_operation(self):
        """Test that SKULL_TRANSFORMATION_VERIFICATION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SKULL_TRANSFORMATION_VERIFICATION', operation, violates=False)
        assert result == "success"
    
    def test_skull_transformation_verification_logs_violations(self):
        """Test that SKULL_TRANSFORMATION_VERIFICATION violations are logged."""
        self.skull.check_rule('SKULL_TRANSFORMATION_VERIFICATION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_skull_transformation_verification_has_metadata(self):
        """Test that SKULL_TRANSFORMATION_VERIFICATION has metadata."""
        meta = self.skull.get_rule_metadata('SKULL_TRANSFORMATION_VERIFICATION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SKULL_TRANSFORMATION_VERIFICATION'
