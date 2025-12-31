"""
SKULL Test: GIT_CHECKPOINT_ENFORCEMENT
Automated enforcement testing for GIT_CHECKPOINT_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestGitCheckpointEnforcement:
    """Test suite for GIT_CHECKPOINT_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_git_checkpoint_enforcement_detects_violation(self):
        """Test detection of GIT_CHECKPOINT_ENFORCEMENT violation."""
        result = self.skull.check_rule('GIT_CHECKPOINT_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'GIT_CHECKPOINT_ENFORCEMENT'
    
    def test_git_checkpoint_enforcement_validates_compliance(self):
        """Test validation of GIT_CHECKPOINT_ENFORCEMENT compliance."""
        result = self.skull.check_rule('GIT_CHECKPOINT_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_git_checkpoint_enforcement_blocks_on_violation(self):
        """Test that GIT_CHECKPOINT_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('GIT_CHECKPOINT_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_git_checkpoint_enforcement_allows_compliant_operation(self):
        """Test that GIT_CHECKPOINT_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('GIT_CHECKPOINT_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_git_checkpoint_enforcement_logs_violations(self):
        """Test that GIT_CHECKPOINT_ENFORCEMENT violations are logged."""
        self.skull.check_rule('GIT_CHECKPOINT_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_git_checkpoint_enforcement_has_metadata(self):
        """Test that GIT_CHECKPOINT_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('GIT_CHECKPOINT_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'GIT_CHECKPOINT_ENFORCEMENT'
