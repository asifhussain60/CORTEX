"""
SKULL Test: ALIGNMENT_STATE_PROTECTION
Automated enforcement testing for ALIGNMENT_STATE_PROTECTION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestAlignmentStateProtection:
    """Test suite for ALIGNMENT_STATE_PROTECTION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_alignment_state_protection_detects_violation(self):
        """Test detection of ALIGNMENT_STATE_PROTECTION violation."""
        result = self.skull.check_rule('ALIGNMENT_STATE_PROTECTION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'ALIGNMENT_STATE_PROTECTION'
    
    def test_alignment_state_protection_validates_compliance(self):
        """Test validation of ALIGNMENT_STATE_PROTECTION compliance."""
        result = self.skull.check_rule('ALIGNMENT_STATE_PROTECTION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_alignment_state_protection_blocks_on_violation(self):
        """Test that ALIGNMENT_STATE_PROTECTION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('ALIGNMENT_STATE_PROTECTION', operation, violates=True, severity="blocked")
    
    def test_alignment_state_protection_allows_compliant_operation(self):
        """Test that ALIGNMENT_STATE_PROTECTION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('ALIGNMENT_STATE_PROTECTION', operation, violates=False)
        assert result == "success"
    
    def test_alignment_state_protection_logs_violations(self):
        """Test that ALIGNMENT_STATE_PROTECTION violations are logged."""
        self.skull.check_rule('ALIGNMENT_STATE_PROTECTION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_alignment_state_protection_has_metadata(self):
        """Test that ALIGNMENT_STATE_PROTECTION has metadata."""
        meta = self.skull.get_rule_metadata('ALIGNMENT_STATE_PROTECTION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'ALIGNMENT_STATE_PROTECTION'
