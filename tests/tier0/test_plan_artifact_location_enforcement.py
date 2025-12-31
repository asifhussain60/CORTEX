"""
SKULL Test: PLAN_ARTIFACT_LOCATION_ENFORCEMENT
Automated enforcement testing for PLAN_ARTIFACT_LOCATION_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestPlanArtifactLocationEnforcement:
    """Test suite for PLAN_ARTIFACT_LOCATION_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_plan_artifact_location_enforcement_detects_violation(self):
        """Test detection of PLAN_ARTIFACT_LOCATION_ENFORCEMENT violation."""
        result = self.skull.check_rule('PLAN_ARTIFACT_LOCATION_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'PLAN_ARTIFACT_LOCATION_ENFORCEMENT'
    
    def test_plan_artifact_location_enforcement_validates_compliance(self):
        """Test validation of PLAN_ARTIFACT_LOCATION_ENFORCEMENT compliance."""
        result = self.skull.check_rule('PLAN_ARTIFACT_LOCATION_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_plan_artifact_location_enforcement_blocks_on_violation(self):
        """Test that PLAN_ARTIFACT_LOCATION_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('PLAN_ARTIFACT_LOCATION_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_plan_artifact_location_enforcement_allows_compliant_operation(self):
        """Test that PLAN_ARTIFACT_LOCATION_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('PLAN_ARTIFACT_LOCATION_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_plan_artifact_location_enforcement_logs_violations(self):
        """Test that PLAN_ARTIFACT_LOCATION_ENFORCEMENT violations are logged."""
        self.skull.check_rule('PLAN_ARTIFACT_LOCATION_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_plan_artifact_location_enforcement_has_metadata(self):
        """Test that PLAN_ARTIFACT_LOCATION_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('PLAN_ARTIFACT_LOCATION_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'PLAN_ARTIFACT_LOCATION_ENFORCEMENT'
