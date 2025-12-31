"""
SKULL Test: AUTONOMOUS_EXECUTION_PROTECTION
Automated enforcement testing for AUTONOMOUS_EXECUTION_PROTECTION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestAutonomousExecutionProtection:
    """Test suite for AUTONOMOUS_EXECUTION_PROTECTION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_autonomous_execution_protection_detects_violation(self):
        """Test detection of AUTONOMOUS_EXECUTION_PROTECTION violation."""
        result = self.skull.check_rule('AUTONOMOUS_EXECUTION_PROTECTION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'AUTONOMOUS_EXECUTION_PROTECTION'
    
    def test_autonomous_execution_protection_validates_compliance(self):
        """Test validation of AUTONOMOUS_EXECUTION_PROTECTION compliance."""
        result = self.skull.check_rule('AUTONOMOUS_EXECUTION_PROTECTION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_autonomous_execution_protection_blocks_on_violation(self):
        """Test that AUTONOMOUS_EXECUTION_PROTECTION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('AUTONOMOUS_EXECUTION_PROTECTION', operation, violates=True, severity="blocked")
    
    def test_autonomous_execution_protection_allows_compliant_operation(self):
        """Test that AUTONOMOUS_EXECUTION_PROTECTION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('AUTONOMOUS_EXECUTION_PROTECTION', operation, violates=False)
        assert result == "success"
    
    def test_autonomous_execution_protection_logs_violations(self):
        """Test that AUTONOMOUS_EXECUTION_PROTECTION violations are logged."""
        self.skull.check_rule('AUTONOMOUS_EXECUTION_PROTECTION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_autonomous_execution_protection_has_metadata(self):
        """Test that AUTONOMOUS_EXECUTION_PROTECTION has metadata."""
        meta = self.skull.get_rule_metadata('AUTONOMOUS_EXECUTION_PROTECTION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'AUTONOMOUS_EXECUTION_PROTECTION'
