"""
SKULL Test: INTERACTIVE_MODE_ENFORCEMENT
Automated enforcement testing for INTERACTIVE_MODE_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestInteractiveModeEnforcement:
    """Test suite for INTERACTIVE_MODE_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_interactive_mode_enforcement_detects_violation(self):
        """Test detection of INTERACTIVE_MODE_ENFORCEMENT violation."""
        result = self.skull.check_rule('INTERACTIVE_MODE_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'INTERACTIVE_MODE_ENFORCEMENT'
    
    def test_interactive_mode_enforcement_validates_compliance(self):
        """Test validation of INTERACTIVE_MODE_ENFORCEMENT compliance."""
        result = self.skull.check_rule('INTERACTIVE_MODE_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_interactive_mode_enforcement_blocks_on_violation(self):
        """Test that INTERACTIVE_MODE_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('INTERACTIVE_MODE_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_interactive_mode_enforcement_allows_compliant_operation(self):
        """Test that INTERACTIVE_MODE_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('INTERACTIVE_MODE_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_interactive_mode_enforcement_logs_violations(self):
        """Test that INTERACTIVE_MODE_ENFORCEMENT violations are logged."""
        self.skull.check_rule('INTERACTIVE_MODE_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_interactive_mode_enforcement_has_metadata(self):
        """Test that INTERACTIVE_MODE_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('INTERACTIVE_MODE_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'INTERACTIVE_MODE_ENFORCEMENT'
