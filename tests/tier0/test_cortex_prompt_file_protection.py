"""
SKULL Test: CORTEX_PROMPT_FILE_PROTECTION
Automated enforcement testing for CORTEX_PROMPT_FILE_PROTECTION brain protection rule.
"""
import pytest
from tests.fixtures.skull_framework import SkullProtector, SkullViolationError, Severity
from unittest.mock import Mock


class TestCortexPromptFileProtection:
    """Test suite for CORTEX_PROMPT_FILE_PROTECTION SKULL rule."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.skull = SkullProtector()
    
    def test_cortex_prompt_file_protection_detects_violation(self):
        """Test detection of CORTEX_PROMPT_FILE_PROTECTION violation."""
        result = self.skull.check_rule('CORTEX_PROMPT_FILE_PROTECTION', {"violates": True, "severity": "blocked"})
        assert result.violated is True
        assert result.rule_id == 'CORTEX_PROMPT_FILE_PROTECTION'
    
    def test_cortex_prompt_file_protection_validates_compliance(self):
        """Test validation of CORTEX_PROMPT_FILE_PROTECTION compliance."""
        result = self.skull.check_rule('CORTEX_PROMPT_FILE_PROTECTION', {"violates": False})
        assert result.violated is False
        assert result.compliant is True
    
    def test_cortex_prompt_file_protection_blocks_on_violation(self):
        """Test that CORTEX_PROMPT_FILE_PROTECTION blocks violating operations."""
        operation = Mock(return_value="blocked")
        with pytest.raises(SkullViolationError):
            self.skull.enforce('CORTEX_PROMPT_FILE_PROTECTION', operation, violates=True, severity="blocked")
    
    def test_cortex_prompt_file_protection_allows_compliant_operation(self):
        """Test that CORTEX_PROMPT_FILE_PROTECTION allows compliant operations."""
        operation = Mock(return_value="success")
        result = self.skull.enforce('CORTEX_PROMPT_FILE_PROTECTION', operation, violates=False)
        assert result == "success"
    
    def test_cortex_prompt_file_protection_logs_violations(self):
        """Test that CORTEX_PROMPT_FILE_PROTECTION violations are logged."""
        self.skull.check_rule('CORTEX_PROMPT_FILE_PROTECTION', {"violates": True})
        assert len(self.skull.violations_logged) > 0
    
    def test_cortex_prompt_file_protection_has_metadata(self):
        """Test that CORTEX_PROMPT_FILE_PROTECTION has metadata."""
        meta = self.skull.get_rule_metadata('CORTEX_PROMPT_FILE_PROTECTION')
        assert 'severity' in meta
        assert meta['rule_id'] == 'CORTEX_PROMPT_FILE_PROTECTION'
