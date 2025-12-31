"""
SKULL Test: BIDIRECTIONAL_LINKING_ENFORCEMENT
Automated enforcement testing for BIDIRECTIONAL_LINKING_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestBidirectionalLinkingEnforcement:
    """Test suite for BIDIRECTIONAL_LINKING_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_bidirectional_linking_enforcement_detects_violation(self):
        """Test detection of BIDIRECTIONAL_LINKING_ENFORCEMENT violation."""
        result = self.skull.check_rule('BIDIRECTIONAL_LINKING_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'BIDIRECTIONAL_LINKING_ENFORCEMENT'
    
    def test_bidirectional_linking_enforcement_validates_compliance(self):
        """Test validation of BIDIRECTIONAL_LINKING_ENFORCEMENT compliance."""
        result = self.skull.check_rule('BIDIRECTIONAL_LINKING_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_bidirectional_linking_enforcement_blocks_on_violation(self):
        """Test that BIDIRECTIONAL_LINKING_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('BIDIRECTIONAL_LINKING_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_bidirectional_linking_enforcement_allows_compliant_operation(self):
        """Test that BIDIRECTIONAL_LINKING_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('BIDIRECTIONAL_LINKING_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_bidirectional_linking_enforcement_logs_violations(self):
        """Test that BIDIRECTIONAL_LINKING_ENFORCEMENT violations are logged."""
        self.skull.check_rule('BIDIRECTIONAL_LINKING_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_bidirectional_linking_enforcement_has_metadata(self):
        """Test that BIDIRECTIONAL_LINKING_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('BIDIRECTIONAL_LINKING_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'BIDIRECTIONAL_LINKING_ENFORCEMENT'
