"""
SKULL Test: CODE_STYLE_CONSISTENCY
Automated enforcement testing for CODE_STYLE_CONSISTENCY brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestCodeStyleConsistency:
    """Test suite for CODE_STYLE_CONSISTENCY SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_code_style_consistency_detects_violation(self):
        """Test detection of CODE_STYLE_CONSISTENCY violation."""
        result = self.skull.check_rule('CODE_STYLE_CONSISTENCY', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'CODE_STYLE_CONSISTENCY'
    
    def test_code_style_consistency_validates_compliance(self):
        """Test validation of CODE_STYLE_CONSISTENCY compliance."""
        result = self.skull.check_rule('CODE_STYLE_CONSISTENCY', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_code_style_consistency_blocks_on_violation(self):
        """Test that CODE_STYLE_CONSISTENCY blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('CODE_STYLE_CONSISTENCY', operation, violates=True, severity="blocked")
    
    def test_code_style_consistency_allows_compliant_operation(self):
        """Test that CODE_STYLE_CONSISTENCY allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('CODE_STYLE_CONSISTENCY', operation, violates=False)
        assert result == "success"
    
    def test_code_style_consistency_logs_violations(self):
        """Test that CODE_STYLE_CONSISTENCY violations are logged."""
        self.skull.check_rule('CODE_STYLE_CONSISTENCY', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_code_style_consistency_has_metadata(self):
        """Test that CODE_STYLE_CONSISTENCY has metadata."""
        meta = self.skull.get_rule_metadata('CODE_STYLE_CONSISTENCY')
        assert 'severity' in meta
        assert meta['rule_id'] == 'CODE_STYLE_CONSISTENCY'
