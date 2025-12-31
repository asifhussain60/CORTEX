"""
SKULL Test: SKULL_TEST_BEFORE_CLAIM
Automated enforcement testing for SKULL_TEST_BEFORE_CLAIM brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSkullTestBeforeClaim:
    """Test suite for SKULL_TEST_BEFORE_CLAIM SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_skull_test_before_claim_detects_violation(self):
        """Test detection of SKULL_TEST_BEFORE_CLAIM violation."""
        result = self.skull.check_rule('SKULL_TEST_BEFORE_CLAIM', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SKULL_TEST_BEFORE_CLAIM'
    
    def test_skull_test_before_claim_validates_compliance(self):
        """Test validation of SKULL_TEST_BEFORE_CLAIM compliance."""
        result = self.skull.check_rule('SKULL_TEST_BEFORE_CLAIM', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_skull_test_before_claim_blocks_on_violation(self):
        """Test that SKULL_TEST_BEFORE_CLAIM blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SKULL_TEST_BEFORE_CLAIM', operation, violates=True, severity="blocked")
    
    def test_skull_test_before_claim_allows_compliant_operation(self):
        """Test that SKULL_TEST_BEFORE_CLAIM allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SKULL_TEST_BEFORE_CLAIM', operation, violates=False)
        assert result == "success"
    
    def test_skull_test_before_claim_logs_violations(self):
        """Test that SKULL_TEST_BEFORE_CLAIM violations are logged."""
        self.skull.check_rule('SKULL_TEST_BEFORE_CLAIM', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_skull_test_before_claim_has_metadata(self):
        """Test that SKULL_TEST_BEFORE_CLAIM has metadata."""
        meta = self.skull.get_rule_metadata('SKULL_TEST_BEFORE_CLAIM')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SKULL_TEST_BEFORE_CLAIM'
