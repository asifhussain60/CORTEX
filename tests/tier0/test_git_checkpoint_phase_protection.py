"""
SKULL Test: GIT_CHECKPOINT_PHASE_PROTECTION
Automated enforcement testing for GIT_CHECKPOINT_PHASE_PROTECTION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestGitCheckpointPhaseProtection:
    """Test suite for GIT_CHECKPOINT_PHASE_PROTECTION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_git_checkpoint_phase_protection_detects_violation(self):
        """Test detection of GIT_CHECKPOINT_PHASE_PROTECTION violation."""
        result = self.skull.check_rule('GIT_CHECKPOINT_PHASE_PROTECTION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'GIT_CHECKPOINT_PHASE_PROTECTION'
    
    def test_git_checkpoint_phase_protection_validates_compliance(self):
        """Test validation of GIT_CHECKPOINT_PHASE_PROTECTION compliance."""
        result = self.skull.check_rule('GIT_CHECKPOINT_PHASE_PROTECTION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_git_checkpoint_phase_protection_blocks_on_violation(self):
        """Test that GIT_CHECKPOINT_PHASE_PROTECTION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('GIT_CHECKPOINT_PHASE_PROTECTION', operation, violates=True, severity="blocked")
    
    def test_git_checkpoint_phase_protection_allows_compliant_operation(self):
        """Test that GIT_CHECKPOINT_PHASE_PROTECTION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('GIT_CHECKPOINT_PHASE_PROTECTION', operation, violates=False)
        assert result == "success"
    
    def test_git_checkpoint_phase_protection_logs_violations(self):
        """Test that GIT_CHECKPOINT_PHASE_PROTECTION violations are logged."""
        self.skull.check_rule('GIT_CHECKPOINT_PHASE_PROTECTION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_git_checkpoint_phase_protection_has_metadata(self):
        """Test that GIT_CHECKPOINT_PHASE_PROTECTION has metadata."""
        meta = self.skull.get_rule_metadata('GIT_CHECKPOINT_PHASE_PROTECTION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'GIT_CHECKPOINT_PHASE_PROTECTION'
