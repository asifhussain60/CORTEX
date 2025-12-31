"""
SKULL Test: GIT_COMMIT_PRIVACY_VALIDATION
Automated enforcement testing for GIT_COMMIT_PRIVACY_VALIDATION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestGitCommitPrivacyValidation:
    """Test suite for GIT_COMMIT_PRIVACY_VALIDATION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_git_commit_privacy_validation_detects_violation(self):
        """Test detection of GIT_COMMIT_PRIVACY_VALIDATION violation."""
        result = self.skull.check_rule('GIT_COMMIT_PRIVACY_VALIDATION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'GIT_COMMIT_PRIVACY_VALIDATION'
    
    def test_git_commit_privacy_validation_validates_compliance(self):
        """Test validation of GIT_COMMIT_PRIVACY_VALIDATION compliance."""
        result = self.skull.check_rule('GIT_COMMIT_PRIVACY_VALIDATION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_git_commit_privacy_validation_blocks_on_violation(self):
        """Test that GIT_COMMIT_PRIVACY_VALIDATION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('GIT_COMMIT_PRIVACY_VALIDATION', operation, violates=True, severity="blocked")
    
    def test_git_commit_privacy_validation_allows_compliant_operation(self):
        """Test that GIT_COMMIT_PRIVACY_VALIDATION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('GIT_COMMIT_PRIVACY_VALIDATION', operation, violates=False)
        assert result == "success"
    
    def test_git_commit_privacy_validation_logs_violations(self):
        """Test that GIT_COMMIT_PRIVACY_VALIDATION violations are logged."""
        self.skull.check_rule('GIT_COMMIT_PRIVACY_VALIDATION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_git_commit_privacy_validation_has_metadata(self):
        """Test that GIT_COMMIT_PRIVACY_VALIDATION has metadata."""
        meta = self.skull.get_rule_metadata('GIT_COMMIT_PRIVACY_VALIDATION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'GIT_COMMIT_PRIVACY_VALIDATION'
