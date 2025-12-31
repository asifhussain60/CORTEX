"""
SKULL Test: SOLID_PRINCIPLES
Automated enforcement testing for SOLID_PRINCIPLES brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSolidPrinciples:
    """Test suite for SOLID_PRINCIPLES SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_solid_principles_detects_violation(self):
        """Test detection of SOLID_PRINCIPLES violation."""
        result = self.skull.check_rule('SOLID_PRINCIPLES', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SOLID_PRINCIPLES'
    
    def test_solid_principles_validates_compliance(self):
        """Test validation of SOLID_PRINCIPLES compliance."""
        result = self.skull.check_rule('SOLID_PRINCIPLES', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_solid_principles_blocks_on_violation(self):
        """Test that SOLID_PRINCIPLES blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SOLID_PRINCIPLES', operation, violates=True, severity="blocked")
    
    def test_solid_principles_allows_compliant_operation(self):
        """Test that SOLID_PRINCIPLES allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SOLID_PRINCIPLES', operation, violates=False)
        assert result == "success"
    
    def test_solid_principles_logs_violations(self):
        """Test that SOLID_PRINCIPLES violations are logged."""
        self.skull.check_rule('SOLID_PRINCIPLES', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_solid_principles_has_metadata(self):
        """Test that SOLID_PRINCIPLES has metadata."""
        meta = self.skull.get_rule_metadata('SOLID_PRINCIPLES')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SOLID_PRINCIPLES'
