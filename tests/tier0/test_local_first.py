"""
SKULL Test: LOCAL_FIRST
Automated enforcement testing for LOCAL_FIRST brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestLocalFirst:
    """Test suite for LOCAL_FIRST SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_local_first_detects_violation(self):
        """Test detection of LOCAL_FIRST violation."""
        result = self.skull.check_rule('LOCAL_FIRST', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'LOCAL_FIRST'
    
    def test_local_first_validates_compliance(self):
        """Test validation of LOCAL_FIRST compliance."""
        result = self.skull.check_rule('LOCAL_FIRST', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_local_first_blocks_on_violation(self):
        """Test that LOCAL_FIRST blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('LOCAL_FIRST', operation, violates=True, severity="blocked")
    
    def test_local_first_allows_compliant_operation(self):
        """Test that LOCAL_FIRST allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('LOCAL_FIRST', operation, violates=False)
        assert result == "success"
    
    def test_local_first_logs_violations(self):
        """Test that LOCAL_FIRST violations are logged."""
        self.skull.check_rule('LOCAL_FIRST', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_local_first_has_metadata(self):
        """Test that LOCAL_FIRST has metadata."""
        meta = self.skull.get_rule_metadata('LOCAL_FIRST')
        assert 'severity' in meta
        assert meta['rule_id'] == 'LOCAL_FIRST'
