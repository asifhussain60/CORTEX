"""
SKULL Test: GIT_HISTORY_CONTEXT_REQUIRED
Automated enforcement testing for GIT_HISTORY_CONTEXT_REQUIRED brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestGitHistoryContextRequired:
    """Test suite for GIT_HISTORY_CONTEXT_REQUIRED SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_git_history_context_required_detects_violation(self):
        """Test detection of GIT_HISTORY_CONTEXT_REQUIRED violation."""
        result = self.skull.check_rule('GIT_HISTORY_CONTEXT_REQUIRED', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'GIT_HISTORY_CONTEXT_REQUIRED'
    
    def test_git_history_context_required_validates_compliance(self):
        """Test validation of GIT_HISTORY_CONTEXT_REQUIRED compliance."""
        result = self.skull.check_rule('GIT_HISTORY_CONTEXT_REQUIRED', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_git_history_context_required_blocks_on_violation(self):
        """Test that GIT_HISTORY_CONTEXT_REQUIRED blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('GIT_HISTORY_CONTEXT_REQUIRED', operation, violates=True, severity="blocked")
    
    def test_git_history_context_required_allows_compliant_operation(self):
        """Test that GIT_HISTORY_CONTEXT_REQUIRED allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('GIT_HISTORY_CONTEXT_REQUIRED', operation, violates=False)
        assert result == "success"
    
    def test_git_history_context_required_logs_violations(self):
        """Test that GIT_HISTORY_CONTEXT_REQUIRED violations are logged."""
        self.skull.check_rule('GIT_HISTORY_CONTEXT_REQUIRED', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_git_history_context_required_has_metadata(self):
        """Test that GIT_HISTORY_CONTEXT_REQUIRED has metadata."""
        meta = self.skull.get_rule_metadata('GIT_HISTORY_CONTEXT_REQUIRED')
        assert 'severity' in meta
        assert meta['rule_id'] == 'GIT_HISTORY_CONTEXT_REQUIRED'
