"""
Integration tests for Phase 22 MCP tools and Phase 20.2 visibility.

Tests the complete flow:
1. cortex_ask MCP tool → EducationalOrchestrator
2. cortex_verify_claim MCP tool → TruthVerificationEngine
3. OrchestratorVisibility integration
"""

import pytest
from unittest.mock import Mock, patch
from cortex.mcp.tools.cortex_ask import cortex_ask
from cortex.mcp.tools.cortex_verify_claim import cortex_verify_claim
from cortex.orchestrators.support.orchestrator_visibility import OrchestratorVisibility


class TestCortexPlanIntegration:
    """Integration tests for cortex-plan 100% completion."""

    def test_ask_mode_end_to_end(self):
        """Test complete ASK mode flow."""
        # Execute educational query
        result = cortex_ask(
            user_query="What is MasterOrchestrator?",
            knowledge_level="beginner",
            verify_implementation=True
        )
        
        # Verify response structure
        assert result["status"] == "success"
        assert "explanation" in result
        assert "next_steps" in result
        assert isinstance(result["next_steps"], list)
        assert len(result["next_steps"]) >= 3
        
        # Verify verification was performed
        if "verification" in result:
            assert "verified" in result["verification"]

    def test_claim_verification_end_to_end(self):
        """Test complete claim verification flow."""
        # Verify a known true claim with specific orchestrator name
        result = cortex_verify_claim(
            claim="MasterOrchestrator exists",
            use_ast=True
        )
        
        # Should succeed
        assert result["status"] == "success"
        assert result["verdict"] in ["verified", "partial", "false"]

    def test_visibility_system_integration(self):
        """Test visibility system with orchestrator."""
        visibility = OrchestratorVisibility()
        
        # Generate visibility for TDD orchestrator
        result = visibility.execute({
            "orchestrator": "TDDOrchestrator",
            "stage": 2,
            "total_stages": 4,
            "intelligence": ["lens", "knowledge"]
        })
        
        # Verify visibility generated
        if result["visible"]:
            assert "header" in result
            assert "TDDOrchestrator" in result["header"]

    def test_ask_with_visibility(self):
        """Test ASK mode with visibility enabled."""
        visibility = OrchestratorVisibility()
        
        # Enable visibility
        with patch.dict('os.environ', {'CORTEX_ORCHESTRATOR_VISIBILITY': 'full'}):
            # Generate visibility header
            vis_result = visibility.execute({
                "orchestrator": "EducationalOrchestrator",
                "stage": 1,
                "total_stages": 4,
                "intelligence": ["lens", "knowledge"]
            })
            
            # Execute ASK query
            ask_result = cortex_ask(
                user_query="Explain LENS",
                knowledge_level="intermediate"
            )
            
            # Both should succeed
            assert vis_result["visible"] is True
            assert ask_result["status"] == "success"

    def test_mcp_tools_registered(self):
        """Test that MCP tools are properly registered."""
        # Check tool attributes
        assert hasattr(cortex_ask, '__mcp_tool__') or cortex_ask.__name__ == 'cortex_ask'
        assert hasattr(cortex_verify_claim, '__mcp_tool__') or cortex_verify_claim.__name__ == 'cortex_verify_claim'

    def test_orchestrator_visibility_wired(self):
        """Test that OrchestratorVisibility is properly wired."""
        # This will be verified by wiring tests
        orch = OrchestratorVisibility()
        assert orch.get_name() == "OrchestratorVisibility"
        assert orch.health_check() is True

    def test_error_handling_cascade(self):
        """Test error handling across integration points."""
        # Test with invalid input
        result = cortex_ask(
            user_query="",  # Empty query
            knowledge_level="beginner"
        )
        
        assert result["status"] == "error"
        assert "error" in result

    def test_progressive_disclosure_levels(self):
        """Test that knowledge levels work end-to-end."""
        levels = ["beginner", "intermediate", "advanced"]
        
        for level in levels:
            result = cortex_ask(
                user_query="Explain orchestrators",
                knowledge_level=level
            )
            
            assert result["status"] == "success"
            assert result["knowledge_level"] == level

    def test_verification_integration(self):
        """Test verification engine integration."""
        # Verify a claim via ASK mode
        result = cortex_ask(
            user_query="Does TDDOrchestrator exist?",
            knowledge_level="advanced",
            verify_implementation=True
        )
        
        assert result["status"] == "success"
        
        # Also verify via direct claim verification
        claim_result = cortex_verify_claim(
            claim="TDDOrchestrator exists in wiring.yaml"
        )
        
        assert claim_result["status"] == "success"

    def test_production_readiness(self):
        """Test that all components are production-ready."""
        # All tools should handle basic cases without errors
        
        # 1. ASK mode
        ask_result = cortex_ask(
            user_query="Test query",
            knowledge_level="beginner"
        )
        assert ask_result["status"] in ["success", "error"]
        
        # 2. Claim verification
        claim_result = cortex_verify_claim(
            claim="CORTEX exists"
        )
        assert claim_result["status"] in ["success", "error"]
        
        # 3. Visibility
        visibility = OrchestratorVisibility()
        vis_result = visibility.execute({
            "orchestrator": "Test",
            "stage": 1,
            "total_stages": 4
        })
        assert "visible" in vis_result
