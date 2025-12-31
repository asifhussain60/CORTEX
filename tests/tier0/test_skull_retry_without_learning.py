"""
SKULL Test: SKULL_RETRY_WITHOUT_LEARNING
Automated enforcement testing for SKULL_RETRY_WITHOUT_LEARNING brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestSkullRetryWithoutLearning:
    """Test suite for SKULL_RETRY_WITHOUT_LEARNING SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_skull_retry_without_learning_detects_violation(self):
        """Test detection of SKULL_RETRY_WITHOUT_LEARNING violation."""
        result = self.skull.check_rule('SKULL_RETRY_WITHOUT_LEARNING', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'SKULL_RETRY_WITHOUT_LEARNING'
    
    def test_skull_retry_without_learning_validates_compliance(self):
        """Test validation of SKULL_RETRY_WITHOUT_LEARNING compliance."""
        result = self.skull.check_rule('SKULL_RETRY_WITHOUT_LEARNING', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_skull_retry_without_learning_blocks_on_violation(self):
        """Test that SKULL_RETRY_WITHOUT_LEARNING blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('SKULL_RETRY_WITHOUT_LEARNING', operation, violates=True, severity="blocked")
    
    def test_skull_retry_without_learning_allows_compliant_operation(self):
        """Test that SKULL_RETRY_WITHOUT_LEARNING allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('SKULL_RETRY_WITHOUT_LEARNING', operation, violates=False)
        assert result == "success"
    
    def test_skull_retry_without_learning_logs_violations(self):
        """Test that SKULL_RETRY_WITHOUT_LEARNING violations are logged."""
        self.skull.check_rule('SKULL_RETRY_WITHOUT_LEARNING', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_skull_retry_without_learning_has_metadata(self):
        """Test that SKULL_RETRY_WITHOUT_LEARNING has metadata."""
        meta = self.skull.get_rule_metadata('SKULL_RETRY_WITHOUT_LEARNING')
        assert 'severity' in meta
        assert meta['rule_id'] == 'SKULL_RETRY_WITHOUT_LEARNING'
