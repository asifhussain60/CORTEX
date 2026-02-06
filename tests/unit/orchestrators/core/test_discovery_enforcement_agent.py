"""
Tests for DiscoveryEnforcementAgent.

Authority: ENH-047 Pre-Execution Discovery Protocol
Author: Asif Hussain
"""

import pytest
from cortex.orchestrators.core.enforcement_orchestrator import (
    DiscoveryEnforcementAgent,
    EnforcementLevel,
)


class TestDiscoveryEnforcementAgent:
    """Test DiscoveryEnforcementAgent governance enforcement."""
    
    @pytest.fixture
    def agent(self):
        """Create discovery enforcement agent fixture."""
        return DiscoveryEnforcementAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct rules."""
        assert agent.name == "DiscoveryEnforcementAgent"
        assert "CORE-030" in agent.rules
        assert "CORE-035" in agent.rules
    
    def test_blocks_when_no_discovery_performed(self, agent):
        """Test agent blocks IMPLEMENT without discovery (CORE-030)."""
        operation = {
            "intent": "IMPLEMENT",
            "feature_name": "dashboard",
            "scope": "module",
            # No discovery_result
        }
        
        result = agent.validate(operation)
        
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0
        assert "CORE-030" in result.violations[0]
        assert "discovery not performed" in result.violations[0].lower()
    
    def test_blocks_when_duplicates_detected(self, agent):
        """Test agent blocks when duplicates found (CORE-035)."""
        operation = {
            "intent": "IMPLEMENT",
            "feature_name": "dashboard",
            "scope": "module",
            "discovery_result": {
                "recommendation": "BLOCKED",
                "duplicates": [
                    {"file_path": "dashboard_v2.py"}
                ],
                "existing_features": [],
            }
        }
        
        result = agent.validate(operation)
        
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0
        assert "CORE-035" in result.violations[0]
        assert "duplicate" in result.violations[0].lower()
    
    def test_warns_when_existing_features_found(self, agent):
        """Test agent warns when existing features found without extend mode."""
        operation = {
            "intent": "IMPLEMENT",
            "feature_name": "dashboard",
            "scope": "module",
            "extend_mode": False,
            "discovery_result": {
                "recommendation": "EXTEND",
                "duplicates": [],
                "existing_features": [
                    {"file_path": "dashboard.py"}
                ],
            }
        }
        
        result = agent.validate(operation)
        
        assert result.level == EnforcementLevel.WARNING
        assert len(result.warnings) > 0
        assert "CORE-030" in result.warnings[0]
        assert "similar implementation" in result.warnings[0].lower()
    
    def test_passes_when_discovery_safe(self, agent):
        """Test agent passes when discovery shows safe to proceed."""
        operation = {
            "intent": "IMPLEMENT",
            "feature_name": "new_feature",
            "scope": "file",
            "discovery_result": {
                "recommendation": "CREATE_NEW",
                "duplicates": [],
                "existing_features": [],
            }
        }
        
        result = agent.validate(operation)
        
        assert result.level == EnforcementLevel.PASS
        assert len(result.violations) == 0
        assert len(result.warnings) == 0
    
    def test_skips_for_non_implementation_intents(self, agent):
        """Test agent skips discovery check for ANALYZE/AUDIT intents."""
        operation = {
            "intent": "ANALYZE",
            "feature_name": "test",
        }
        
        result = agent.validate(operation)
        
        assert result.level == EnforcementLevel.PASS
        assert "skipped" in result.metadata
    
    def test_passes_with_extend_mode(self, agent):
        """Test agent passes when extend_mode is true."""
        operation = {
            "intent": "IMPLEMENT",
            "feature_name": "dashboard",
            "scope": "module",
            "extend_mode": True,
            "discovery_result": {
                "recommendation": "EXTEND",
                "duplicates": [],
                "existing_features": [
                    {"file_path": "dashboard.py"}
                ],
            }
        }
        
        result = agent.validate(operation)
        
        # Should pass or have no warnings about extend
        assert result.level in [EnforcementLevel.PASS, EnforcementLevel.WARNING]
        if result.level == EnforcementLevel.WARNING:
            # If warnings exist, they shouldn't be about extending
            for warning in result.warnings:
                assert "--extend flag" not in warning.lower()
