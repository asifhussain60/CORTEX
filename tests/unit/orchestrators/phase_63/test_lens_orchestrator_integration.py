"""
Phase 63: LENS Tiered MCP API - REFACTOR Phase Tests

Tests for orchestrator integration, MCP tool definitions, and tier selection.
"""

import pytest
from pathlib import Path
import tempfile
import json

from cortex.orchestrators.lens_orchestrator_integration import (
    LensMCPTools,
    LensOrchestratorWiring,
    LensOrchestratorTierSelection,
    LensIntegrationOrchestrator,
)


class TestLensMCPTools:
    """Tests for MCP tool definitions"""
    
    def test_cortex_lens_quick_tool_definition(self):
        """cortex_lens_quick tool definition is valid"""
        tools = LensMCPTools()
        tool = tools.cortex_lens_quick_tool_definition()
        
        assert tool["name"] == "cortex_lens_quick"
        assert tool["tier"] == "tier_2_quick"
        assert tool["latency_sla_ms"] == 200
        assert "parameters" in tool
        assert "output_schema" in tool
    
    def test_cortex_lens_targeted_tool_definition(self):
        """cortex_lens_targeted tool definition is valid"""
        tools = LensMCPTools()
        tool = tools.cortex_lens_targeted_tool_definition()
        
        assert tool["name"] == "cortex_lens_targeted"
        assert tool["tier"] == "tier_3_targeted"
        assert tool["latency_sla_ms"] == 2000
    
    def test_cortex_lens_stream_tool_definition(self):
        """cortex_lens_stream tool definition is valid"""
        tools = LensMCPTools()
        tool = tools.cortex_lens_stream_tool_definition()
        
        assert tool["name"] == "cortex_lens_stream"
        assert tool["tier"] == "tier_3_stream"
        assert tool["streaming"] is True
    
    def test_cortex_lens_analyze_tool_definition(self):
        """cortex_lens_analyze tool definition is valid and backward compatible"""
        tools = LensMCPTools()
        tool = tools.cortex_lens_analyze_tool_definition()
        
        assert tool["name"] == "cortex_lens_analyze"
        assert tool["tier"] == "tier_4_full"
        assert tool["backward_compatible"] is True
    
    def test_tool_definitions_have_parameters(self):
        """All tool definitions have required parameters"""
        tools = LensMCPTools()
        
        for tool_func in [
            tools.cortex_lens_quick_tool_definition,
            tools.cortex_lens_targeted_tool_definition,
            tools.cortex_lens_stream_tool_definition,
            tools.cortex_lens_analyze_tool_definition,
        ]:
            tool = tool_func()
            assert "parameters" in tool or tool["name"] == "cortex_lens_analyze"


class TestLensOrchestratorWiring:
    """Tests for orchestrator wiring"""
    
    def test_wiring_configuration_complete(self):
        """Wiring configuration includes all orchestrators"""
        wiring = LensOrchestratorWiring()
        config = wiring.get_wiring_configuration()
        
        assert "interaction_orchestrator" in config
        assert "tdd_orchestrator" in config
        assert "plan_orchestrator" in config
        assert "repository_onboarding_orchestrator" in config
    
    def test_interaction_orchestrator_wiring(self):
        """InteractionOrchestrator wired to Tier 2"""
        wiring = LensOrchestratorWiring()
        config = wiring.get_wiring_configuration()
        
        io_wiring = config["interaction_orchestrator"]
        assert io_wiring["tier"] == "tier_2_quick"
        assert io_wiring["mcp_tool"] == "cortex_lens_quick"
        assert io_wiring["latency_requirement"] == "< 200ms"
    
    def test_tdd_orchestrator_wiring(self):
        """TDDOrchestrator wired to Tier 2"""
        wiring = LensOrchestratorWiring()
        config = wiring.get_wiring_configuration()
        
        tdd_wiring = config["tdd_orchestrator"]
        assert tdd_wiring["tier"] == "tier_2_quick"
        assert tdd_wiring["mcp_tool"] == "cortex_lens_quick"
    
    def test_plan_orchestrator_wiring(self):
        """PlanOrchestrator wired to Tier 3 targeted"""
        wiring = LensOrchestratorWiring()
        config = wiring.get_wiring_configuration()
        
        plan_wiring = config["plan_orchestrator"]
        assert plan_wiring["tier"] == "tier_3_targeted"
        assert plan_wiring["mcp_tool"] == "cortex_lens_targeted"
    
    def test_onboarding_orchestrator_wiring(self):
        """RepositoryOnboardingOrchestrator wired to Tier 4"""
        wiring = LensOrchestratorWiring()
        config = wiring.get_wiring_configuration()
        
        onboard_wiring = config["repository_onboarding_orchestrator"]
        assert onboard_wiring["tier"] == "tier_4_full"
        assert onboard_wiring["backward_compatible"] is True


class TestLensOrchestratorTierSelection:
    """Tests for tier selection logic"""
    
    def test_select_tier_for_interact(self):
        """Select Tier 2 for interaction intent"""
        selection = LensOrchestratorTierSelection()
        
        tier = selection.select_tier_for_intent("interact")
        
        assert tier == "tier_2_quick"
    
    def test_select_tier_for_tdd(self):
        """Select Tier 2 for TDD intent"""
        selection = LensOrchestratorTierSelection()
        
        tier = selection.select_tier_for_intent("tdd")
        
        assert tier == "tier_2_quick"
    
    def test_select_tier_for_plan(self):
        """Select Tier 3 targeted for plan intent"""
        selection = LensOrchestratorTierSelection()
        
        tier = selection.select_tier_for_intent("plan")
        
        assert tier == "tier_3_targeted"
    
    def test_select_tier_for_onboard(self):
        """Select Tier 4 for onboard intent"""
        selection = LensOrchestratorTierSelection()
        
        tier = selection.select_tier_for_intent("onboard")
        
        assert tier == "tier_4_full"
    
    def test_select_tier_for_large_repo(self):
        """Select streaming for large repositories"""
        selection = LensOrchestratorTierSelection()
        
        # Large repo should get streaming tier
        tier = selection.select_tier_for_intent("plan", repo_size=1000)
        
        assert tier == "tier_3_stream"
    
    def test_get_tier_characteristics_tier2(self):
        """Get characteristics for Tier 2"""
        selection = LensOrchestratorTierSelection()
        
        chars = selection.get_tier_characteristics("tier_2_quick")
        
        assert chars["latency_ms"] == 200
        assert chars["throughput_rps"] == 100
        assert chars["caching"] is True
    
    def test_get_tier_characteristics_tier4(self):
        """Get characteristics for Tier 4"""
        selection = LensOrchestratorTierSelection()
        
        chars = selection.get_tier_characteristics("tier_4_full")
        
        assert chars["latency_ms"] == 10000
        assert chars["comprehensive"] is True


class TestLensIntegrationOrchestrator:
    """Tests for LENS integration orchestrator"""
    
    def test_orchestrator_initialization(self):
        """Integration orchestrator initializes all components"""
        orchestrator = LensIntegrationOrchestrator()
        
        assert orchestrator.integration is not None
        assert orchestrator.tools is not None
        assert orchestrator.wiring is not None
        assert orchestrator.selection is not None
    
    def test_get_mcp_tools_manifest(self):
        """Get MCP tools manifest"""
        orchestrator = LensIntegrationOrchestrator()
        
        manifest = orchestrator.get_mcp_tools_manifest()
        
        assert "cortex_lens_quick" in manifest
        assert "cortex_lens_targeted" in manifest
        assert "cortex_lens_stream" in manifest
        assert "cortex_lens_analyze" in manifest
    
    def test_get_orchestrator_wiring(self):
        """Get orchestrator wiring configuration"""
        orchestrator = LensIntegrationOrchestrator()
        
        wiring = orchestrator.get_orchestrator_wiring()
        
        assert "interaction_orchestrator" in wiring
        assert "tdd_orchestrator" in wiring
        assert "plan_orchestrator" in wiring
    
    @pytest.mark.asyncio
    async def test_execute_interaction_analysis(self):
        """Execute interaction analysis through orchestrator"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            temp_file = Path(f.name)
        
        try:
            orchestrator = LensIntegrationOrchestrator()
            result = await orchestrator.execute_interaction_analysis(temp_file)
            
            assert isinstance(result, dict)
            assert result["tier"] == "tier_2_quick"
        finally:
            temp_file.unlink()
    
    @pytest.mark.asyncio
    async def test_execute_tdd_enrichment(self):
        """Execute TDD enrichment through orchestrator"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            temp_file = Path(f.name)
        
        try:
            orchestrator = LensIntegrationOrchestrator()
            result = await orchestrator.execute_tdd_enrichment(temp_file)
            
            assert isinstance(result, dict)
            assert result["tier"] == "tier_2_quick"
        finally:
            temp_file.unlink()
    
    @pytest.mark.asyncio
    async def test_execute_plan_validation(self):
        """Execute plan validation through orchestrator"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            temp_file = Path(f.name)
        
        try:
            orchestrator = LensIntegrationOrchestrator()
            result = await orchestrator.execute_plan_validation(temp_file)
            
            assert isinstance(result, dict)
            assert result["tier"] == "tier_3_targeted"
        finally:
            temp_file.unlink()
    
    @pytest.mark.asyncio
    async def test_execute_onboarding_analysis(self):
        """Execute onboarding analysis through orchestrator"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            temp_file = Path(f.name)
        
        try:
            orchestrator = LensIntegrationOrchestrator()
            result = await orchestrator.execute_onboarding_analysis(temp_file)
            
            assert isinstance(result, dict)
            assert result["tier"] == "tier_4_full"
        finally:
            temp_file.unlink()


class TestMCPToolIntegration:
    """Tests for MCP tool integration"""
    
    def test_all_tools_discoverable(self):
        """All MCP tools are discoverable"""
        orchestrator = LensIntegrationOrchestrator()
        manifest = orchestrator.get_mcp_tools_manifest()
        
        tool_names = list(manifest.keys())
        
        assert len(tool_names) == 4
        assert all("cortex_lens" in name for name in tool_names)
    
    def test_tools_have_descriptions(self):
        """All tools have descriptions"""
        orchestrator = LensIntegrationOrchestrator()
        manifest = orchestrator.get_mcp_tools_manifest()
        
        for tool in manifest.values():
            assert "description" in tool
            assert len(tool["description"]) > 0
    
    def test_tools_have_output_schemas(self):
        """All tools have output schemas"""
        orchestrator = LensIntegrationOrchestrator()
        manifest = orchestrator.get_mcp_tools_manifest()
        
        for tool in manifest.values():
            # Streaming tool may not have schema
            if not tool.get("streaming"):
                assert "output_schema" in tool


class TestTierPerformanceSLAs:
    """Tests for tier performance SLAs"""
    
    def test_tier2_sla_definition(self):
        """Tier 2 SLA is <200ms"""
        tools = LensMCPTools()
        tool = tools.cortex_lens_quick_tool_definition()
        
        assert tool["latency_sla_ms"] == 200
    
    def test_tier3_targeted_sla_definition(self):
        """Tier 3 targeted SLA is <2s"""
        tools = LensMCPTools()
        tool = tools.cortex_lens_targeted_tool_definition()
        
        assert tool["latency_sla_ms"] == 2000
    
    def test_tier4_sla_definition(self):
        """Tier 4 SLA is <10s"""
        tools = LensMCPTools()
        tool = tools.cortex_lens_analyze_tool_definition()
        
        assert tool["latency_sla_ms"] == 10000


class TestOrchestratorUtilities:
    """Tests for orchestrator utility methods"""
    
    def test_default_tier_for_unknown_intent(self):
        """Unknown intent defaults to Tier 2"""
        selection = LensOrchestratorTierSelection()
        
        tier = selection.select_tier_for_intent("unknown_intent")
        
        assert tier == "tier_2_quick"
    
    def test_tier_characteristics_all_tiers(self):
        """Can get characteristics for all tiers"""
        selection = LensOrchestratorTierSelection()
        tiers = ["tier_2_quick", "tier_3_targeted", "tier_3_stream", "tier_4_full"]
        
        for tier in tiers:
            chars = selection.get_tier_characteristics(tier)
            assert len(chars) > 0
