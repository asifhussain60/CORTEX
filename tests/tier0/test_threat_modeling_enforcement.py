"""
SKULL Test: THREAT_MODELING_ENFORCEMENT
Automated enforcement testing for THREAT_MODELING_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestThreatModelingEnforcement:
    """Test suite for THREAT_MODELING_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_threat_modeling_enforcement_detects_violation(self):
        """Test detection of THREAT_MODELING_ENFORCEMENT violation."""
        result = self.skull.check_rule('THREAT_MODELING_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'THREAT_MODELING_ENFORCEMENT'
    
    def test_threat_modeling_enforcement_validates_compliance(self):
        """Test validation of THREAT_MODELING_ENFORCEMENT compliance."""
        result = self.skull.check_rule('THREAT_MODELING_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_threat_modeling_enforcement_blocks_on_violation(self):
        """Test that THREAT_MODELING_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('THREAT_MODELING_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_threat_modeling_enforcement_allows_compliant_operation(self):
        """Test that THREAT_MODELING_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('THREAT_MODELING_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_threat_modeling_enforcement_logs_violations(self):
        """Test that THREAT_MODELING_ENFORCEMENT violations are logged."""
        self.skull.check_rule('THREAT_MODELING_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_threat_modeling_enforcement_has_metadata(self):
        """Test that THREAT_MODELING_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('THREAT_MODELING_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'THREAT_MODELING_ENFORCEMENT'
