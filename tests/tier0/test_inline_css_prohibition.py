"""
SKULL Test: INLINE_CSS_PROHIBITION
Automated enforcement testing for INLINE_CSS_PROHIBITION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestInlineCssProhibition:
    """Test suite for INLINE_CSS_PROHIBITION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_inline_css_prohibition_detects_violation(self):
        """Test detection of INLINE_CSS_PROHIBITION violation."""
        result = self.skull.check_rule('INLINE_CSS_PROHIBITION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'INLINE_CSS_PROHIBITION'
    
    def test_inline_css_prohibition_validates_compliance(self):
        """Test validation of INLINE_CSS_PROHIBITION compliance."""
        result = self.skull.check_rule('INLINE_CSS_PROHIBITION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_inline_css_prohibition_blocks_on_violation(self):
        """Test that INLINE_CSS_PROHIBITION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('INLINE_CSS_PROHIBITION', operation, violates=True, severity="blocked")
    
    def test_inline_css_prohibition_allows_compliant_operation(self):
        """Test that INLINE_CSS_PROHIBITION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('INLINE_CSS_PROHIBITION', operation, violates=False)
        assert result == "success"
    
    def test_inline_css_prohibition_logs_violations(self):
        """Test that INLINE_CSS_PROHIBITION violations are logged."""
        self.skull.check_rule('INLINE_CSS_PROHIBITION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_inline_css_prohibition_has_metadata(self):
        """Test that INLINE_CSS_PROHIBITION has metadata."""
        meta = self.skull.get_rule_metadata('INLINE_CSS_PROHIBITION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'INLINE_CSS_PROHIBITION'
