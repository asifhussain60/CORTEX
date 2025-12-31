"""
SKULL Test: DEFINITION_OF_READY
Automated enforcement testing for DEFINITION_OF_READY brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestDefinitionOfReady:
    """Test suite for DEFINITION_OF_READY SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_definition_of_ready_detects_violation(self):
        """Test detection of DEFINITION_OF_READY violation."""
        result = self.skull.check_rule('DEFINITION_OF_READY', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'DEFINITION_OF_READY'
    
    def test_definition_of_ready_validates_compliance(self):
        """Test validation of DEFINITION_OF_READY compliance."""
        result = self.skull.check_rule('DEFINITION_OF_READY', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_definition_of_ready_blocks_on_violation(self):
        """Test that DEFINITION_OF_READY blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('DEFINITION_OF_READY', operation, violates=True, severity="blocked")
    
    def test_definition_of_ready_allows_compliant_operation(self):
        """Test that DEFINITION_OF_READY allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('DEFINITION_OF_READY', operation, violates=False)
        assert result == "success"
    
    def test_definition_of_ready_logs_violations(self):
        """Test that DEFINITION_OF_READY violations are logged."""
        self.skull.check_rule('DEFINITION_OF_READY', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_definition_of_ready_has_metadata(self):
        """Test that DEFINITION_OF_READY has metadata."""
        meta = self.skull.get_rule_metadata('DEFINITION_OF_READY')
        assert 'severity' in meta
        assert meta['rule_id'] == 'DEFINITION_OF_READY'
