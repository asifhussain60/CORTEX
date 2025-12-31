"""
SKULL Test: SKULL_FACULTY_INTEGRITY
Automated enforcement testing for SKULL_FACULTY_INTEGRITY brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSkullFacultyIntegrity:
    """Test suite for SKULL_FACULTY_INTEGRITY SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_skull_faculty_integrity_detects_violation(self):
        """Test detection of SKULL_FACULTY_INTEGRITY violation."""
        result = self.skull.check_rule('SKULL_FACULTY_INTEGRITY', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SKULL_FACULTY_INTEGRITY'
    
    def test_skull_faculty_integrity_validates_compliance(self):
        """Test validation of SKULL_FACULTY_INTEGRITY compliance."""
        result = self.skull.check_rule('SKULL_FACULTY_INTEGRITY', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_skull_faculty_integrity_blocks_on_violation(self):
        """Test that SKULL_FACULTY_INTEGRITY blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SKULL_FACULTY_INTEGRITY', operation, violates=True, severity="blocked")
    
    def test_skull_faculty_integrity_allows_compliant_operation(self):
        """Test that SKULL_FACULTY_INTEGRITY allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SKULL_FACULTY_INTEGRITY', operation, violates=False)
        assert result == "success"
    
    def test_skull_faculty_integrity_logs_violations(self):
        """Test that SKULL_FACULTY_INTEGRITY violations are logged."""
        self.skull.check_rule('SKULL_FACULTY_INTEGRITY', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_skull_faculty_integrity_has_metadata(self):
        """Test that SKULL_FACULTY_INTEGRITY has metadata."""
        meta = self.skull.get_rule_metadata('SKULL_FACULTY_INTEGRITY')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SKULL_FACULTY_INTEGRITY'
