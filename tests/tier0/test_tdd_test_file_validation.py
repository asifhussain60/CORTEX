"""
SKULL Test: TDD_TEST_FILE_VALIDATION
Automated enforcement testing for TDD_TEST_FILE_VALIDATION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestTddTestFileValidation:
    """Test suite for TDD_TEST_FILE_VALIDATION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_tdd_test_file_validation_detects_violation(self):
        """Test detection of TDD_TEST_FILE_VALIDATION violation."""
        result = self.skull.check_rule('TDD_TEST_FILE_VALIDATION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'TDD_TEST_FILE_VALIDATION'
    
    def test_tdd_test_file_validation_validates_compliance(self):
        """Test validation of TDD_TEST_FILE_VALIDATION compliance."""
        result = self.skull.check_rule('TDD_TEST_FILE_VALIDATION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_tdd_test_file_validation_blocks_on_violation(self):
        """Test that TDD_TEST_FILE_VALIDATION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('TDD_TEST_FILE_VALIDATION', operation, violates=True, severity="blocked")
    
    def test_tdd_test_file_validation_allows_compliant_operation(self):
        """Test that TDD_TEST_FILE_VALIDATION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('TDD_TEST_FILE_VALIDATION', operation, violates=False)
        assert result == "success"
    
    def test_tdd_test_file_validation_logs_violations(self):
        """Test that TDD_TEST_FILE_VALIDATION violations are logged."""
        self.skull.check_rule('TDD_TEST_FILE_VALIDATION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_tdd_test_file_validation_has_metadata(self):
        """Test that TDD_TEST_FILE_VALIDATION has metadata."""
        meta = self.skull.get_rule_metadata('TDD_TEST_FILE_VALIDATION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'TDD_TEST_FILE_VALIDATION'
