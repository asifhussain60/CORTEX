"""
SKULL Test: SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT
Automated enforcement testing for SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSeniorDeveloperEstimateEnforcement:
    """Test suite for SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_senior_developer_estimate_enforcement_detects_violation(self):
        """Test detection of SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT violation."""
        result = self.skull.check_rule('SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT'
    
    def test_senior_developer_estimate_enforcement_validates_compliance(self):
        """Test validation of SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT compliance."""
        result = self.skull.check_rule('SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_senior_developer_estimate_enforcement_blocks_on_violation(self):
        """Test that SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_senior_developer_estimate_enforcement_allows_compliant_operation(self):
        """Test that SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_senior_developer_estimate_enforcement_logs_violations(self):
        """Test that SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT violations are logged."""
        self.skull.check_rule('SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_senior_developer_estimate_enforcement_has_metadata(self):
        """Test that SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT'
