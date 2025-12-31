"""
SKULL Test: TOKEN_OPTIMIZATION_ENFORCEMENT
Automated enforcement testing for TOKEN_OPTIMIZATION_ENFORCEMENT brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestTokenOptimizationEnforcement:
    """Test suite for TOKEN_OPTIMIZATION_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_token_optimization_enforcement_detects_violation(self):
        """Test detection of TOKEN_OPTIMIZATION_ENFORCEMENT violation."""
        result = self.skull.check_rule('TOKEN_OPTIMIZATION_ENFORCEMENT', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'TOKEN_OPTIMIZATION_ENFORCEMENT'
    
    def test_token_optimization_enforcement_validates_compliance(self):
        """Test validation of TOKEN_OPTIMIZATION_ENFORCEMENT compliance."""
        result = self.skull.check_rule('TOKEN_OPTIMIZATION_ENFORCEMENT', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_token_optimization_enforcement_blocks_on_violation(self):
        """Test that TOKEN_OPTIMIZATION_ENFORCEMENT blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('TOKEN_OPTIMIZATION_ENFORCEMENT', operation, violates=True, severity="blocked")
    
    def test_token_optimization_enforcement_allows_compliant_operation(self):
        """Test that TOKEN_OPTIMIZATION_ENFORCEMENT allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('TOKEN_OPTIMIZATION_ENFORCEMENT', operation, violates=False)
        assert result == "success"
    
    def test_token_optimization_enforcement_logs_violations(self):
        """Test that TOKEN_OPTIMIZATION_ENFORCEMENT violations are logged."""
        self.skull.check_rule('TOKEN_OPTIMIZATION_ENFORCEMENT', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_token_optimization_enforcement_has_metadata(self):
        """Test that TOKEN_OPTIMIZATION_ENFORCEMENT has metadata."""
        meta = self.skull.get_rule_metadata('TOKEN_OPTIMIZATION_ENFORCEMENT')
        assert 'severity' in meta
        assert meta['rule_id'] == 'TOKEN_OPTIMIZATION_ENFORCEMENT'
