"""
SKULL Test: INCREMENTAL_PLAN_CREATION_ENFORCEMENT
Automated enforcement testing for INCREMENTAL_PLAN_CREATION_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestIncrementalPlanCreationEnforcement:
    """Test suite for INCREMENTAL_PLAN_CREATION_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_incremental_plan_creation_enforcement_detects_violation(self):
        """Test detection of INCREMENTAL_PLAN_CREATION_ENFORCEMENT violation."""
        result = self.skull.check_rule('INCREMENTAL_PLAN_CREATION_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'INCREMENTAL_PLAN_CREATION_ENFORCEMENT'
    
    def test_incremental_plan_creation_enforcement_validates_compliance(self):
        """Test validation of INCREMENTAL_PLAN_CREATION_ENFORCEMENT compliance."""
        result = self.skull.check_rule('INCREMENTAL_PLAN_CREATION_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_incremental_plan_creation_enforcement_blocks_on_violation(self):
        """Test that INCREMENTAL_PLAN_CREATION_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('INCREMENTAL_PLAN_CREATION_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_incremental_plan_creation_enforcement_allows_compliant_operation(self):
        """Test that INCREMENTAL_PLAN_CREATION_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('INCREMENTAL_PLAN_CREATION_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_incremental_plan_creation_enforcement_logs_violations(self):
        """Test that INCREMENTAL_PLAN_CREATION_ENFORCEMENT violations are logged."""
        self.skull.check_rule('INCREMENTAL_PLAN_CREATION_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_incremental_plan_creation_enforcement_has_metadata(self):
        """Test that INCREMENTAL_PLAN_CREATION_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('INCREMENTAL_PLAN_CREATION_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'INCREMENTAL_PLAN_CREATION_ENFORCEMENT'
