"""
SKULL Test: NO_EMOJIS_IN_SCRIPTS
Automated enforcement testing for NO_EMOJIS_IN_SCRIPTS brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestNoEmojisInScripts:
    """Test suite for NO_EMOJIS_IN_SCRIPTS SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_no_emojis_in_scripts_detects_violation(self):
        """Test detection of NO_EMOJIS_IN_SCRIPTS violation."""
        result = self.skull.check_rule('NO_EMOJIS_IN_SCRIPTS', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'NO_EMOJIS_IN_SCRIPTS'
    
    def test_no_emojis_in_scripts_validates_compliance(self):
        """Test validation of NO_EMOJIS_IN_SCRIPTS compliance."""
        result = self.skull.check_rule('NO_EMOJIS_IN_SCRIPTS', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_no_emojis_in_scripts_blocks_on_violation(self):
        """Test that NO_EMOJIS_IN_SCRIPTS blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('NO_EMOJIS_IN_SCRIPTS', operation, violates=True, severity="blocked")
    
    def test_no_emojis_in_scripts_allows_compliant_operation(self):
        """Test that NO_EMOJIS_IN_SCRIPTS allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('NO_EMOJIS_IN_SCRIPTS', operation, violates=False)
        assert result == "success"
    
    def test_no_emojis_in_scripts_logs_violations(self):
        """Test that NO_EMOJIS_IN_SCRIPTS violations are logged."""
        self.skull.check_rule('NO_EMOJIS_IN_SCRIPTS', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_no_emojis_in_scripts_has_metadata(self):
        """Test that NO_EMOJIS_IN_SCRIPTS has metadata."""
        meta = self.skull.get_rule_metadata('NO_EMOJIS_IN_SCRIPTS')
        assert 'severity' in meta
        assert meta['rule_id'] == 'NO_EMOJIS_IN_SCRIPTS'
