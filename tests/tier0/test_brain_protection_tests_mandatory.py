"""
SKULL Test: BRAIN_PROTECTION_TESTS_MANDATORY
Automated enforcement testing for BRAIN_PROTECTION_TESTS_MANDATORY brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestBrainProtectionTestsMandatory:
    """Test suite for BRAIN_PROTECTION_TESTS_MANDATORY SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_brain_protection_tests_mandatory_detects_violation(self):
        """Test detection of BRAIN_PROTECTION_TESTS_MANDATORY violation."""
        result = self.skull.check_rule('BRAIN_PROTECTION_TESTS_MANDATORY', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'BRAIN_PROTECTION_TESTS_MANDATORY'
    
    def test_brain_protection_tests_mandatory_validates_compliance(self):
        """Test validation of BRAIN_PROTECTION_TESTS_MANDATORY compliance."""
        result = self.skull.check_rule('BRAIN_PROTECTION_TESTS_MANDATORY', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_brain_protection_tests_mandatory_blocks_on_violation(self):
        """Test that BRAIN_PROTECTION_TESTS_MANDATORY blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('BRAIN_PROTECTION_TESTS_MANDATORY', operation, violates=True, severity="blocked")
    
    def test_brain_protection_tests_mandatory_allows_compliant_operation(self):
        """Test that BRAIN_PROTECTION_TESTS_MANDATORY allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('BRAIN_PROTECTION_TESTS_MANDATORY', operation, violates=False)
        assert result == "success"
    
    def test_brain_protection_tests_mandatory_logs_violations(self):
        """Test that BRAIN_PROTECTION_TESTS_MANDATORY violations are logged."""
        self.skull.check_rule('BRAIN_PROTECTION_TESTS_MANDATORY', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_brain_protection_tests_mandatory_has_metadata(self):
        """Test that BRAIN_PROTECTION_TESTS_MANDATORY has metadata."""
        meta = self.skull.get_rule_metadata('BRAIN_PROTECTION_TESTS_MANDATORY')
        assert 'severity' in meta
        assert meta['rule_id'] == 'BRAIN_PROTECTION_TESTS_MANDATORY'
