"""
SKULL Test: UPGRADE_BRAIN_PRESERVATION
Automated enforcement testing for UPGRADE_BRAIN_PRESERVATION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestUpgradeBrainPreservation:
    """Test suite for UPGRADE_BRAIN_PRESERVATION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_upgrade_brain_preservation_detects_violation(self):
        """Test detection of UPGRADE_BRAIN_PRESERVATION violation."""
        result = self.skull.check_rule('UPGRADE_BRAIN_PRESERVATION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'UPGRADE_BRAIN_PRESERVATION'
    
    def test_upgrade_brain_preservation_validates_compliance(self):
        """Test validation of UPGRADE_BRAIN_PRESERVATION compliance."""
        result = self.skull.check_rule('UPGRADE_BRAIN_PRESERVATION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_upgrade_brain_preservation_blocks_on_violation(self):
        """Test that UPGRADE_BRAIN_PRESERVATION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('UPGRADE_BRAIN_PRESERVATION', operation, violates=True, severity="blocked")
    
    def test_upgrade_brain_preservation_allows_compliant_operation(self):
        """Test that UPGRADE_BRAIN_PRESERVATION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('UPGRADE_BRAIN_PRESERVATION', operation, violates=False)
        assert result == "success"
    
    def test_upgrade_brain_preservation_logs_violations(self):
        """Test that UPGRADE_BRAIN_PRESERVATION violations are logged."""
        self.skull.check_rule('UPGRADE_BRAIN_PRESERVATION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_upgrade_brain_preservation_has_metadata(self):
        """Test that UPGRADE_BRAIN_PRESERVATION has metadata."""
        meta = self.skull.get_rule_metadata('UPGRADE_BRAIN_PRESERVATION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'UPGRADE_BRAIN_PRESERVATION'
