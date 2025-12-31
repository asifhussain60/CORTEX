"""
SKULL Test: FILE_ORGANIZATION_ENFORCEMENT
Automated enforcement testing for FILE_ORGANIZATION_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestFileOrganizationEnforcement:
    """Test suite for FILE_ORGANIZATION_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_file_organization_enforcement_detects_violation(self):
        """Test detection of FILE_ORGANIZATION_ENFORCEMENT violation."""
        result = self.skull.check_rule('FILE_ORGANIZATION_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'FILE_ORGANIZATION_ENFORCEMENT'
    
    def test_file_organization_enforcement_validates_compliance(self):
        """Test validation of FILE_ORGANIZATION_ENFORCEMENT compliance."""
        result = self.skull.check_rule('FILE_ORGANIZATION_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_file_organization_enforcement_blocks_on_violation(self):
        """Test that FILE_ORGANIZATION_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('FILE_ORGANIZATION_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_file_organization_enforcement_allows_compliant_operation(self):
        """Test that FILE_ORGANIZATION_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('FILE_ORGANIZATION_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_file_organization_enforcement_logs_violations(self):
        """Test that FILE_ORGANIZATION_ENFORCEMENT violations are logged."""
        self.skull.check_rule('FILE_ORGANIZATION_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_file_organization_enforcement_has_metadata(self):
        """Test that FILE_ORGANIZATION_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('FILE_ORGANIZATION_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'FILE_ORGANIZATION_ENFORCEMENT'
