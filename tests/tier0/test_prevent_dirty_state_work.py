"""
SKULL Test: PREVENT_DIRTY_STATE_WORK
Automated enforcement testing for PREVENT_DIRTY_STATE_WORK brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestPreventDirtyStateWork:
    """Test suite for PREVENT_DIRTY_STATE_WORK SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_prevent_dirty_state_work_detects_violation(self):
        """Test detection of PREVENT_DIRTY_STATE_WORK violation."""
        result = self.skull.check_rule('PREVENT_DIRTY_STATE_WORK', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'PREVENT_DIRTY_STATE_WORK'
    
    def test_prevent_dirty_state_work_validates_compliance(self):
        """Test validation of PREVENT_DIRTY_STATE_WORK compliance."""
        result = self.skull.check_rule('PREVENT_DIRTY_STATE_WORK', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_prevent_dirty_state_work_blocks_on_violation(self):
        """Test that PREVENT_DIRTY_STATE_WORK blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('PREVENT_DIRTY_STATE_WORK', operation, violates=True, severity="blocked")
    
    def test_prevent_dirty_state_work_allows_compliant_operation(self):
        """Test that PREVENT_DIRTY_STATE_WORK allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('PREVENT_DIRTY_STATE_WORK', operation, violates=False)
        assert result == "success"
    
    def test_prevent_dirty_state_work_logs_violations(self):
        """Test that PREVENT_DIRTY_STATE_WORK violations are logged."""
        self.skull.check_rule('PREVENT_DIRTY_STATE_WORK', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_prevent_dirty_state_work_has_metadata(self):
        """Test that PREVENT_DIRTY_STATE_WORK has metadata."""
        meta = self.skull.get_rule_metadata('PREVENT_DIRTY_STATE_WORK')
        assert 'severity' in meta
        assert meta['rule_id'] == 'PREVENT_DIRTY_STATE_WORK'
