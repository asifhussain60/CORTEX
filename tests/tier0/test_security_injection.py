"""
SKULL Test: SECURITY_INJECTION
Automated enforcement testing for SECURITY_INJECTION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSecurityInjection:
    """Test suite for SECURITY_INJECTION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_security_injection_detects_violation(self):
        """Test detection of SECURITY_INJECTION violation."""
        result = self.skull.check_rule('SECURITY_INJECTION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SECURITY_INJECTION'
    
    def test_security_injection_validates_compliance(self):
        """Test validation of SECURITY_INJECTION compliance."""
        result = self.skull.check_rule('SECURITY_INJECTION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_security_injection_blocks_on_violation(self):
        """Test that SECURITY_INJECTION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SECURITY_INJECTION', operation, violates=True, severity="blocked")
    
    def test_security_injection_allows_compliant_operation(self):
        """Test that SECURITY_INJECTION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SECURITY_INJECTION', operation, violates=False)
        assert result == "success"
    
    def test_security_injection_logs_violations(self):
        """Test that SECURITY_INJECTION violations are logged."""
        self.skull.check_rule('SECURITY_INJECTION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_security_injection_has_metadata(self):
        """Test that SECURITY_INJECTION has metadata."""
        meta = self.skull.get_rule_metadata('SECURITY_INJECTION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SECURITY_INJECTION'
