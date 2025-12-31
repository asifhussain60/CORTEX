"""
SKULL Test: BRAIN_ARCHITECTURE_INTEGRITY
Automated enforcement testing for BRAIN_ARCHITECTURE_INTEGRITY brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestBrainArchitectureIntegrity:
    """Test suite for BRAIN_ARCHITECTURE_INTEGRITY SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_brain_architecture_integrity_detects_violation(self):
        """Test detection of BRAIN_ARCHITECTURE_INTEGRITY violation."""
        result = self.skull.check_rule('BRAIN_ARCHITECTURE_INTEGRITY', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'BRAIN_ARCHITECTURE_INTEGRITY'
    
    def test_brain_architecture_integrity_validates_compliance(self):
        """Test validation of BRAIN_ARCHITECTURE_INTEGRITY compliance."""
        result = self.skull.check_rule('BRAIN_ARCHITECTURE_INTEGRITY', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_brain_architecture_integrity_blocks_on_violation(self):
        """Test that BRAIN_ARCHITECTURE_INTEGRITY blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('BRAIN_ARCHITECTURE_INTEGRITY', operation, violates=True, severity="blocked")
    
    def test_brain_architecture_integrity_allows_compliant_operation(self):
        """Test that BRAIN_ARCHITECTURE_INTEGRITY allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('BRAIN_ARCHITECTURE_INTEGRITY', operation, violates=False)
        assert result == "success"
    
    def test_brain_architecture_integrity_logs_violations(self):
        """Test that BRAIN_ARCHITECTURE_INTEGRITY violations are logged."""
        self.skull.check_rule('BRAIN_ARCHITECTURE_INTEGRITY', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_brain_architecture_integrity_has_metadata(self):
        """Test that BRAIN_ARCHITECTURE_INTEGRITY has metadata."""
        meta = self.skull.get_rule_metadata('BRAIN_ARCHITECTURE_INTEGRITY')
        assert 'severity' in meta
        assert meta['rule_id'] == 'BRAIN_ARCHITECTURE_INTEGRITY'
