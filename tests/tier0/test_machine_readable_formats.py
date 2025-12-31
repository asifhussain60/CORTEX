"""
SKULL Test: MACHINE_READABLE_FORMATS
Automated enforcement testing for MACHINE_READABLE_FORMATS brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestMachineReadableFormats:
    """Test suite for MACHINE_READABLE_FORMATS SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_machine_readable_formats_detects_violation(self):
        """Test detection of MACHINE_READABLE_FORMATS violation."""
        result = self.skull.check_rule('MACHINE_READABLE_FORMATS', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'MACHINE_READABLE_FORMATS'
    
    def test_machine_readable_formats_validates_compliance(self):
        """Test validation of MACHINE_READABLE_FORMATS compliance."""
        result = self.skull.check_rule('MACHINE_READABLE_FORMATS', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_machine_readable_formats_blocks_on_violation(self):
        """Test that MACHINE_READABLE_FORMATS blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('MACHINE_READABLE_FORMATS', operation, violates=True, severity="blocked")
    
    def test_machine_readable_formats_allows_compliant_operation(self):
        """Test that MACHINE_READABLE_FORMATS allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('MACHINE_READABLE_FORMATS', operation, violates=False)
        assert result == "success"
    
    def test_machine_readable_formats_logs_violations(self):
        """Test that MACHINE_READABLE_FORMATS violations are logged."""
        self.skull.check_rule('MACHINE_READABLE_FORMATS', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_machine_readable_formats_has_metadata(self):
        """Test that MACHINE_READABLE_FORMATS has metadata."""
        meta = self.skull.get_rule_metadata('MACHINE_READABLE_FORMATS')
        assert 'severity' in meta
        assert meta['rule_id'] == 'MACHINE_READABLE_FORMATS'
