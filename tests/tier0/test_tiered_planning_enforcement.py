"""
SKULL Test: TIERED_PLANNING_ENFORCEMENT
Automated enforcement testing for TIERED_PLANNING_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestTieredPlanningEnforcement:
    """Test suite for TIERED_PLANNING_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_tiered_planning_enforcement_detects_violation(self):
        """Test detection of TIERED_PLANNING_ENFORCEMENT violation."""
        result = self.skull.check_rule('TIERED_PLANNING_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'TIERED_PLANNING_ENFORCEMENT'
    
    def test_tiered_planning_enforcement_validates_compliance(self):
        """Test validation of TIERED_PLANNING_ENFORCEMENT compliance."""
        result = self.skull.check_rule('TIERED_PLANNING_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_tiered_planning_enforcement_blocks_on_violation(self):
        """Test that TIERED_PLANNING_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('TIERED_PLANNING_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_tiered_planning_enforcement_allows_compliant_operation(self):
        """Test that TIERED_PLANNING_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('TIERED_PLANNING_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_tiered_planning_enforcement_logs_violations(self):
        """Test that TIERED_PLANNING_ENFORCEMENT violations are logged."""
        self.skull.check_rule('TIERED_PLANNING_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_tiered_planning_enforcement_has_metadata(self):
        """Test that TIERED_PLANNING_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('TIERED_PLANNING_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'TIERED_PLANNING_ENFORCEMENT'
