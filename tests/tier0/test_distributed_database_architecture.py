"""
SKULL Test: DISTRIBUTED_DATABASE_ARCHITECTURE
Automated enforcement testing for DISTRIBUTED_DATABASE_ARCHITECTURE brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestDistributedDatabaseArchitecture:
    """Test suite for DISTRIBUTED_DATABASE_ARCHITECTURE SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_distributed_database_architecture_detects_violation(self):
        """Test detection of DISTRIBUTED_DATABASE_ARCHITECTURE violation."""
        result = self.skull.check_rule('DISTRIBUTED_DATABASE_ARCHITECTURE', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'DISTRIBUTED_DATABASE_ARCHITECTURE'
    
    def test_distributed_database_architecture_validates_compliance(self):
        """Test validation of DISTRIBUTED_DATABASE_ARCHITECTURE compliance."""
        result = self.skull.check_rule('DISTRIBUTED_DATABASE_ARCHITECTURE', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_distributed_database_architecture_blocks_on_violation(self):
        """Test that DISTRIBUTED_DATABASE_ARCHITECTURE blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('DISTRIBUTED_DATABASE_ARCHITECTURE', operation, violates=True, severity="blocked")
    
    def test_distributed_database_architecture_allows_compliant_operation(self):
        """Test that DISTRIBUTED_DATABASE_ARCHITECTURE allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('DISTRIBUTED_DATABASE_ARCHITECTURE', operation, violates=False)
        assert result == "success"
    
    def test_distributed_database_architecture_logs_violations(self):
        """Test that DISTRIBUTED_DATABASE_ARCHITECTURE violations are logged."""
        self.skull.check_rule('DISTRIBUTED_DATABASE_ARCHITECTURE', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_distributed_database_architecture_has_metadata(self):
        """Test that DISTRIBUTED_DATABASE_ARCHITECTURE has metadata."""
        meta = self.skull.get_rule_metadata('DISTRIBUTED_DATABASE_ARCHITECTURE')
        assert 'severity' in meta
        assert meta['rule_id'] == 'DISTRIBUTED_DATABASE_ARCHITECTURE'
