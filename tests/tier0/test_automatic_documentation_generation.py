"""
SKULL Test: AUTOMATIC_DOCUMENTATION_GENERATION
Automated enforcement testing for AUTOMATIC_DOCUMENTATION_GENERATION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestAutomaticDocumentationGeneration:
    """Test suite for AUTOMATIC_DOCUMENTATION_GENERATION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_automatic_documentation_generation_detects_violation(self):
        """Test detection of AUTOMATIC_DOCUMENTATION_GENERATION violation."""
        result = self.skull.check_rule('AUTOMATIC_DOCUMENTATION_GENERATION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'AUTOMATIC_DOCUMENTATION_GENERATION'
    
    def test_automatic_documentation_generation_validates_compliance(self):
        """Test validation of AUTOMATIC_DOCUMENTATION_GENERATION compliance."""
        result = self.skull.check_rule('AUTOMATIC_DOCUMENTATION_GENERATION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_automatic_documentation_generation_blocks_on_violation(self):
        """Test that AUTOMATIC_DOCUMENTATION_GENERATION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('AUTOMATIC_DOCUMENTATION_GENERATION', operation, violates=True, severity="blocked")
    
    def test_automatic_documentation_generation_allows_compliant_operation(self):
        """Test that AUTOMATIC_DOCUMENTATION_GENERATION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('AUTOMATIC_DOCUMENTATION_GENERATION', operation, violates=False)
        assert result == "success"
    
    def test_automatic_documentation_generation_logs_violations(self):
        """Test that AUTOMATIC_DOCUMENTATION_GENERATION violations are logged."""
        self.skull.check_rule('AUTOMATIC_DOCUMENTATION_GENERATION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_automatic_documentation_generation_has_metadata(self):
        """Test that AUTOMATIC_DOCUMENTATION_GENERATION has metadata."""
        meta = self.skull.get_rule_metadata('AUTOMATIC_DOCUMENTATION_GENERATION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'AUTOMATIC_DOCUMENTATION_GENERATION'
