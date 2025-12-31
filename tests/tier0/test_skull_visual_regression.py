"""
SKULL Test: SKULL_VISUAL_REGRESSION
Automated enforcement testing for SKULL_VISUAL_REGRESSION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSkullVisualRegression:
    """Test suite for SKULL_VISUAL_REGRESSION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_skull_visual_regression_detects_violation(self):
        """Test detection of SKULL_VISUAL_REGRESSION violation."""
        result = self.skull.check_rule('SKULL_VISUAL_REGRESSION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SKULL_VISUAL_REGRESSION'
    
    def test_skull_visual_regression_validates_compliance(self):
        """Test validation of SKULL_VISUAL_REGRESSION compliance."""
        result = self.skull.check_rule('SKULL_VISUAL_REGRESSION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_skull_visual_regression_blocks_on_violation(self):
        """Test that SKULL_VISUAL_REGRESSION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SKULL_VISUAL_REGRESSION', operation, violates=True, severity="blocked")
    
    def test_skull_visual_regression_allows_compliant_operation(self):
        """Test that SKULL_VISUAL_REGRESSION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SKULL_VISUAL_REGRESSION', operation, violates=False)
        assert result == "success"
    
    def test_skull_visual_regression_logs_violations(self):
        """Test that SKULL_VISUAL_REGRESSION violations are logged."""
        self.skull.check_rule('SKULL_VISUAL_REGRESSION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_skull_visual_regression_has_metadata(self):
        """Test that SKULL_VISUAL_REGRESSION has metadata."""
        meta = self.skull.get_rule_metadata('SKULL_VISUAL_REGRESSION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SKULL_VISUAL_REGRESSION'
