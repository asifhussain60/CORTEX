"""
SKULL Test: SECURITY_AUTHENTICATION
Automated enforcement testing for SECURITY_AUTHENTICATION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSecurityAuthentication:
    """Test suite for SECURITY_AUTHENTICATION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_security_authentication_detects_violation(self):
        """Test detection of SECURITY_AUTHENTICATION violation."""
        result = self.skull.check_rule('SECURITY_AUTHENTICATION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SECURITY_AUTHENTICATION'
    
    def test_security_authentication_validates_compliance(self):
        """Test validation of SECURITY_AUTHENTICATION compliance."""
        result = self.skull.check_rule('SECURITY_AUTHENTICATION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_security_authentication_blocks_on_violation(self):
        """Test that SECURITY_AUTHENTICATION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SECURITY_AUTHENTICATION', operation, violates=True, severity="blocked")
    
    def test_security_authentication_allows_compliant_operation(self):
        """Test that SECURITY_AUTHENTICATION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SECURITY_AUTHENTICATION', operation, violates=False)
        assert result == "success"
    
    def test_security_authentication_logs_violations(self):
        """Test that SECURITY_AUTHENTICATION violations are logged."""
        self.skull.check_rule('SECURITY_AUTHENTICATION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_security_authentication_has_metadata(self):
        """Test that SECURITY_AUTHENTICATION has metadata."""
        meta = self.skull.get_rule_metadata('SECURITY_AUTHENTICATION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SECURITY_AUTHENTICATION'
