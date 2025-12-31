"""
SKULL Test: DEBUG_MARKER_REMOVAL_ENFORCEMENT
Automated enforcement testing for DEBUG_MARKER_REMOVAL_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestDebugMarkerRemovalEnforcement:
    """Test suite for DEBUG_MARKER_REMOVAL_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_debug_marker_removal_enforcement_detects_violation(self):
        """Test detection of DEBUG_MARKER_REMOVAL_ENFORCEMENT violation."""
        result = self.skull.check_rule('DEBUG_MARKER_REMOVAL_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'DEBUG_MARKER_REMOVAL_ENFORCEMENT'
    
    def test_debug_marker_removal_enforcement_validates_compliance(self):
        """Test validation of DEBUG_MARKER_REMOVAL_ENFORCEMENT compliance."""
        result = self.skull.check_rule('DEBUG_MARKER_REMOVAL_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_debug_marker_removal_enforcement_blocks_on_violation(self):
        """Test that DEBUG_MARKER_REMOVAL_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('DEBUG_MARKER_REMOVAL_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_debug_marker_removal_enforcement_allows_compliant_operation(self):
        """Test that DEBUG_MARKER_REMOVAL_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('DEBUG_MARKER_REMOVAL_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_debug_marker_removal_enforcement_logs_violations(self):
        """Test that DEBUG_MARKER_REMOVAL_ENFORCEMENT violations are logged."""
        self.skull.check_rule('DEBUG_MARKER_REMOVAL_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_debug_marker_removal_enforcement_has_metadata(self):
        """Test that DEBUG_MARKER_REMOVAL_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('DEBUG_MARKER_REMOVAL_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'DEBUG_MARKER_REMOVAL_ENFORCEMENT'
