"""
SKULL Test: GREEN_PHASE_VALIDATION
Automated enforcement testing for GREEN_PHASE_VALIDATION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestGreenPhaseValidation:
    """Test suite for GREEN_PHASE_VALIDATION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_green_phase_validation_detects_violation(self):
        """Test detection of GREEN_PHASE_VALIDATION violation."""
        result = self.skull.check_rule('GREEN_PHASE_VALIDATION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'GREEN_PHASE_VALIDATION'
    
    def test_green_phase_validation_validates_compliance(self):
        """Test validation of GREEN_PHASE_VALIDATION compliance."""
        result = self.skull.check_rule('GREEN_PHASE_VALIDATION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_green_phase_validation_blocks_on_violation(self):
        """Test that GREEN_PHASE_VALIDATION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('GREEN_PHASE_VALIDATION', operation, violates=True, severity="blocked")
    
    def test_green_phase_validation_allows_compliant_operation(self):
        """Test that GREEN_PHASE_VALIDATION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('GREEN_PHASE_VALIDATION', operation, violates=False)
        assert result == "success"
    
    def test_green_phase_validation_logs_violations(self):
        """Test that GREEN_PHASE_VALIDATION violations are logged."""
        self.skull.check_rule('GREEN_PHASE_VALIDATION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_green_phase_validation_has_metadata(self):
        """Test that GREEN_PHASE_VALIDATION has metadata."""
        meta = self.skull.get_rule_metadata('GREEN_PHASE_VALIDATION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'GREEN_PHASE_VALIDATION'
