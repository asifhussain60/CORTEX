"""
SKULL Test: INCREMENTAL_PLAN_GENERATION
Automated enforcement testing for INCREMENTAL_PLAN_GENERATION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestIncrementalPlanGeneration:
    """Test suite for INCREMENTAL_PLAN_GENERATION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_incremental_plan_generation_detects_violation(self):
        """Test detection of INCREMENTAL_PLAN_GENERATION violation."""
        result = self.skull.check_rule('INCREMENTAL_PLAN_GENERATION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'INCREMENTAL_PLAN_GENERATION'
    
    def test_incremental_plan_generation_validates_compliance(self):
        """Test validation of INCREMENTAL_PLAN_GENERATION compliance."""
        result = self.skull.check_rule('INCREMENTAL_PLAN_GENERATION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_incremental_plan_generation_blocks_on_violation(self):
        """Test that INCREMENTAL_PLAN_GENERATION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('INCREMENTAL_PLAN_GENERATION', operation, violates=True, severity="blocked")
    
    def test_incremental_plan_generation_allows_compliant_operation(self):
        """Test that INCREMENTAL_PLAN_GENERATION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('INCREMENTAL_PLAN_GENERATION', operation, violates=False)
        assert result == "success"
    
    def test_incremental_plan_generation_logs_violations(self):
        """Test that INCREMENTAL_PLAN_GENERATION violations are logged."""
        self.skull.check_rule('INCREMENTAL_PLAN_GENERATION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_incremental_plan_generation_has_metadata(self):
        """Test that INCREMENTAL_PLAN_GENERATION has metadata."""
        meta = self.skull.get_rule_metadata('INCREMENTAL_PLAN_GENERATION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'INCREMENTAL_PLAN_GENERATION'
