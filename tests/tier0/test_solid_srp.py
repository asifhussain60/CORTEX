"""
SKULL Test: SOLID_SRP
Automated enforcement testing for SOLID_SRP brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSolidSrp:
    """Test suite for SOLID_SRP SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_solid_srp_detects_violation(self):
        """Test detection of SOLID_SRP violation."""
        result = self.skull.check_rule('SOLID_SRP', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SOLID_SRP'
    
    def test_solid_srp_validates_compliance(self):
        """Test validation of SOLID_SRP compliance."""
        result = self.skull.check_rule('SOLID_SRP', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_solid_srp_blocks_on_violation(self):
        """Test that SOLID_SRP blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SOLID_SRP', operation, violates=True, severity="blocked")
    
    def test_solid_srp_allows_compliant_operation(self):
        """Test that SOLID_SRP allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SOLID_SRP', operation, violates=False)
        assert result == "success"
    
    def test_solid_srp_logs_violations(self):
        """Test that SOLID_SRP violations are logged."""
        self.skull.check_rule('SOLID_SRP', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_solid_srp_has_metadata(self):
        """Test that SOLID_SRP has metadata."""
        meta = self.skull.get_rule_metadata('SOLID_SRP')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SOLID_SRP'
