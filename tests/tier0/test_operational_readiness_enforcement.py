"""
SKULL Test: OPERATIONAL_READINESS_ENFORCEMENT
Automated enforcement testing for OPERATIONAL_READINESS_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestOperationalReadinessEnforcement:
    """Test suite for OPERATIONAL_READINESS_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_operational_readiness_enforcement_detects_violation(self):
        """Test detection of OPERATIONAL_READINESS_ENFORCEMENT violation."""
        result = self.skull.check_rule('OPERATIONAL_READINESS_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'OPERATIONAL_READINESS_ENFORCEMENT'
    
    def test_operational_readiness_enforcement_validates_compliance(self):
        """Test validation of OPERATIONAL_READINESS_ENFORCEMENT compliance."""
        result = self.skull.check_rule('OPERATIONAL_READINESS_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_operational_readiness_enforcement_blocks_on_violation(self):
        """Test that OPERATIONAL_READINESS_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('OPERATIONAL_READINESS_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_operational_readiness_enforcement_allows_compliant_operation(self):
        """Test that OPERATIONAL_READINESS_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('OPERATIONAL_READINESS_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_operational_readiness_enforcement_logs_violations(self):
        """Test that OPERATIONAL_READINESS_ENFORCEMENT violations are logged."""
        self.skull.check_rule('OPERATIONAL_READINESS_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_operational_readiness_enforcement_has_metadata(self):
        """Test that OPERATIONAL_READINESS_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('OPERATIONAL_READINESS_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'OPERATIONAL_READINESS_ENFORCEMENT'
