"""
SKULL Test: API_DOCUMENTATION_REQUIRED
Automated enforcement testing for API_DOCUMENTATION_REQUIRED brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestApiDocumentationRequired:
    """Test suite for API_DOCUMENTATION_REQUIRED SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_api_documentation_required_detects_violation(self):
        """Test detection of API_DOCUMENTATION_REQUIRED violation."""
        result = self.skull.check_rule('API_DOCUMENTATION_REQUIRED', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'API_DOCUMENTATION_REQUIRED'
    
    def test_api_documentation_required_validates_compliance(self):
        """Test validation of API_DOCUMENTATION_REQUIRED compliance."""
        result = self.skull.check_rule('API_DOCUMENTATION_REQUIRED', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_api_documentation_required_blocks_on_violation(self):
        """Test that API_DOCUMENTATION_REQUIRED blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('API_DOCUMENTATION_REQUIRED', operation, violates=True, severity="blocked")
    
    def test_api_documentation_required_allows_compliant_operation(self):
        """Test that API_DOCUMENTATION_REQUIRED allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('API_DOCUMENTATION_REQUIRED', operation, violates=False)
        assert result == "success"
    
    def test_api_documentation_required_logs_violations(self):
        """Test that API_DOCUMENTATION_REQUIRED violations are logged."""
        self.skull.check_rule('API_DOCUMENTATION_REQUIRED', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_api_documentation_required_has_metadata(self):
        """Test that API_DOCUMENTATION_REQUIRED has metadata."""
        meta = self.skull.get_rule_metadata('API_DOCUMENTATION_REQUIRED')
        assert 'severity' in meta
        assert meta['rule_id'] == 'API_DOCUMENTATION_REQUIRED'
