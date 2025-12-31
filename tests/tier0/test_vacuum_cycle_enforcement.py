"""
SKULL Test: VACUUM_CYCLE_ENFORCEMENT
Automated enforcement testing for VACUUM_CYCLE_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestVacuumCycleEnforcement:
    """Test suite for VACUUM_CYCLE_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_vacuum_cycle_enforcement_detects_violation(self):
        """Test detection of VACUUM_CYCLE_ENFORCEMENT violation."""
        result = self.skull.check_rule('VACUUM_CYCLE_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'VACUUM_CYCLE_ENFORCEMENT'
    
    def test_vacuum_cycle_enforcement_validates_compliance(self):
        """Test validation of VACUUM_CYCLE_ENFORCEMENT compliance."""
        result = self.skull.check_rule('VACUUM_CYCLE_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_vacuum_cycle_enforcement_blocks_on_violation(self):
        """Test that VACUUM_CYCLE_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('VACUUM_CYCLE_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_vacuum_cycle_enforcement_allows_compliant_operation(self):
        """Test that VACUUM_CYCLE_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('VACUUM_CYCLE_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_vacuum_cycle_enforcement_logs_violations(self):
        """Test that VACUUM_CYCLE_ENFORCEMENT violations are logged."""
        self.skull.check_rule('VACUUM_CYCLE_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_vacuum_cycle_enforcement_has_metadata(self):
        """Test that VACUUM_CYCLE_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('VACUUM_CYCLE_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'VACUUM_CYCLE_ENFORCEMENT'
