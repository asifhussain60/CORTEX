"""
SKULL Test: DEPLOYMENT_VERSION_TRACKING
Automated enforcement testing for DEPLOYMENT_VERSION_TRACKING brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestDeploymentVersionTracking:
    """Test suite for DEPLOYMENT_VERSION_TRACKING SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_deployment_version_tracking_detects_violation(self):
        """Test detection of DEPLOYMENT_VERSION_TRACKING violation."""
        result = self.skull.check_rule('DEPLOYMENT_VERSION_TRACKING', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'DEPLOYMENT_VERSION_TRACKING'
    
    def test_deployment_version_tracking_validates_compliance(self):
        """Test validation of DEPLOYMENT_VERSION_TRACKING compliance."""
        result = self.skull.check_rule('DEPLOYMENT_VERSION_TRACKING', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_deployment_version_tracking_blocks_on_violation(self):
        """Test that DEPLOYMENT_VERSION_TRACKING blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('DEPLOYMENT_VERSION_TRACKING', operation, violates=True, severity="blocked")
    
    def test_deployment_version_tracking_allows_compliant_operation(self):
        """Test that DEPLOYMENT_VERSION_TRACKING allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('DEPLOYMENT_VERSION_TRACKING', operation, violates=False)
        assert result == "success"
    
    def test_deployment_version_tracking_logs_violations(self):
        """Test that DEPLOYMENT_VERSION_TRACKING violations are logged."""
        self.skull.check_rule('DEPLOYMENT_VERSION_TRACKING', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_deployment_version_tracking_has_metadata(self):
        """Test that DEPLOYMENT_VERSION_TRACKING has metadata."""
        meta = self.skull.get_rule_metadata('DEPLOYMENT_VERSION_TRACKING')
        assert 'severity' in meta
        assert meta['rule_id'] == 'DEPLOYMENT_VERSION_TRACKING'
