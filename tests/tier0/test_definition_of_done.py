"""
SKULL Test: DEFINITION_OF_DONE
Automated enforcement testing for DEFINITION_OF_DONE brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestDefinitionOfDone:
    """Test suite for DEFINITION_OF_DONE SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_definition_of_done_detects_violation(self):
        """Test detection of DEFINITION_OF_DONE violation."""
        result = self.skull.check_rule('DEFINITION_OF_DONE', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'DEFINITION_OF_DONE'
    
    def test_definition_of_done_validates_compliance(self):
        """Test validation of DEFINITION_OF_DONE compliance."""
        result = self.skull.check_rule('DEFINITION_OF_DONE', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_definition_of_done_blocks_on_violation(self):
        """Test that DEFINITION_OF_DONE blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('DEFINITION_OF_DONE', operation, violates=True, severity="blocked")
    
    def test_definition_of_done_allows_compliant_operation(self):
        """Test that DEFINITION_OF_DONE allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('DEFINITION_OF_DONE', operation, violates=False)
        assert result == "success"
    
    def test_definition_of_done_logs_violations(self):
        """Test that DEFINITION_OF_DONE violations are logged."""
        self.skull.check_rule('DEFINITION_OF_DONE', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_definition_of_done_has_metadata(self):
        """Test that DEFINITION_OF_DONE has metadata."""
        meta = self.skull.get_rule_metadata('DEFINITION_OF_DONE')
        assert 'severity' in meta
        assert meta['rule_id'] == 'DEFINITION_OF_DONE'
