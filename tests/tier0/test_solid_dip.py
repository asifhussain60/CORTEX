"""
SKULL Test: SOLID_DIP
Automated enforcement testing for SOLID_DIP brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSolidDip:
    """Test suite for SOLID_DIP SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_solid_dip_detects_violation(self):
        """Test detection of SOLID_DIP violation."""
        result = self.skull.check_rule('SOLID_DIP', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SOLID_DIP'
    
    def test_solid_dip_validates_compliance(self):
        """Test validation of SOLID_DIP compliance."""
        result = self.skull.check_rule('SOLID_DIP', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_solid_dip_blocks_on_violation(self):
        """Test that SOLID_DIP blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SOLID_DIP', operation, violates=True, severity="blocked")
    
    def test_solid_dip_allows_compliant_operation(self):
        """Test that SOLID_DIP allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SOLID_DIP', operation, violates=False)
        assert result == "success"
    
    def test_solid_dip_logs_violations(self):
        """Test that SOLID_DIP violations are logged."""
        self.skull.check_rule('SOLID_DIP', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_solid_dip_has_metadata(self):
        """Test that SOLID_DIP has metadata."""
        meta = self.skull.get_rule_metadata('SOLID_DIP')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SOLID_DIP'
