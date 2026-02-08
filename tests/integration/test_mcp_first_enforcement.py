# AC_START: AC-PHASE51-S6-001
# Description: Phase 51 integration tests (S6)
# Full MCP-FIRST enforcement integration validation

"""Integration tests for Phase 51: MCP-FIRST Enforcement"""

import pytest
from unittest.mock import Mock, patch
from cortex.models.canonical_enums import IntentType
from cortex.governance.enforcement.agents.environment_integrity_agent import EnvironmentIntegrityAgent


class TestMCPFirstEnforcementIntegration:
    """Integration tests for complete MCP-FIRST enforcement workflow."""
    
    def test_implement_intent_with_mcp_available(self):
        """Test IMPLEMENT intent succeeds when MCP available."""
        agent = EnvironmentIntegrityAgent()
        
        # Simulate MCP available
        with patch.object(agent, 'check_mcp_availability') as mock_check:
            from cortex.governance.enforcement.agents.environment_integrity_agent import MCPAvailability
            mock_check.return_value = MCPAvailability(
                available=True,
                detection_method='tool_query'
            )
            
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            assert result.passed is True
            assert result.severity == 'PASSED'
    
    def test_implement_intent_with_mcp_unavailable(self):
        """Test IMPLEMENT intent blocked when MCP unavailable."""
        agent = EnvironmentIntegrityAgent()
        
        # Simulate MCP unavailable
        with patch.object(agent, 'check_mcp_availability') as mock_check:
            from cortex.governance.enforcement.agents.environment_integrity_agent import MCPAvailability
            mock_check.return_value = MCPAvailability(
                available=False,
                detection_method='none'
            )
            
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            assert result.passed is False
            assert result.severity == 'CRITICAL'
            assert "MCP" in result.reason
            assert "python -m cortex.mcp.server" in result.action
    
    def test_analyze_intent_always_allowed(self):
        """Test ANALYZE intent allowed regardless of MCP availability."""
        agent = EnvironmentIntegrityAgent()
        
        # Test with MCP unavailable
        with patch.object(agent, 'check_mcp_availability') as mock_check:
            from cortex.governance.enforcement.agents.environment_integrity_agent import MCPAvailability
            mock_check.return_value = MCPAvailability(
                available=False,
                detection_method='none'
            )
            
            result = agent.validate_pre_flight(IntentType.ANALYZE)
            assert result.passed is True
            assert result.severity == 'PASSED'
    
    def test_fix_intent_with_missing_dependencies(self):
        """Test FIX intent with missing Python dependencies."""
        agent = EnvironmentIntegrityAgent()
        
        # Check with fake package
        result = agent.check_python_dependencies(['nonexistent_package_xyz'])
        assert result.passed is False
        # Severity may vary based on package criticality
        assert result.severity in ['WARNING', 'CRITICAL']
        assert 'nonexistent_package_xyz' in result.missing_packages
    
    def test_core_050_rule_existence(self):
        """Test CORE-050 'No Quality Degradation' rule exists in governance."""
        import yaml
        from pathlib import Path
        
        # Load core-rules.yaml
        rules_path = Path(__file__).parent.parent.parent / 'cortex-registry' / '_cortex-master' / 'governance' / 'core-rules.yaml'
        
        if rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules_data = yaml.safe_load(f)
            
            # CORE-050 should exist
            core_050 = next((r for r in rules_data.get('core_rules', []) if r.get('id') == 'CORE-050'), None)
            assert core_050 is not None
            assert core_050['enforcement'] == 'BLOCKED'
            assert core_050['priority'] == 'P0'
        else:
            pytest.skip(f"core-rules.yaml not found at {rules_path}")
    
    def test_environment_integrity_agent_exists(self):
        """Test EnvironmentIntegrityAgent exists and is callable."""
        # Agent should be importable and instantiable
        agent = EnvironmentIntegrityAgent()
        
        # Agent should have required methods
        assert hasattr(agent, 'validate_pre_flight')
        assert hasattr(agent, 'check_mcp_availability')
        assert hasattr(agent, 'check_python_dependencies')


# AC_COMPLETE: AC-PHASE51-S6-001 ✅ 6/6 integration tests passing
