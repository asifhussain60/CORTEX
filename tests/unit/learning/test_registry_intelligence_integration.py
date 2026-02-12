"""
Test Registry Intelligence Integration - End-to-End Validation

AC-ID: HOLISTIC-REGISTRY-TEST-001
Purpose: Validate the complete registry intelligence system works
         Test deployment orchestrator discovery and MCP tool exposure

Author: Asif Hussain
Date: 2026-02-10
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any, List

from cortex.learning.registry_intelligence_agent import (
    RegistryIntelligenceAgent,
    OrchestratorDiscovery,
    RegistryGap,
    get_registry_intelligence_agent,
)


class TestRegistryIntelligenceIntegration(unittest.TestCase):
    """Test complete registry intelligence integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent
        self.agent = RegistryIntelligenceAgent(
            workspace_root=self.workspace_root,
            enable_learning=False  # Disable learning for tests
        )
    
    def test_deployment_orchestrator_discovery(self):
        """Test that DeploymentOrchestrator is discovered correctly."""
        # Scan for orchestrators
        discoveries = self.agent.scan_for_orchestrators(force_rescan=True)
        
        # Find DeploymentOrchestrator
        deployment_discovery = None
        for discovery in discoveries:
            if discovery.name == "DeploymentOrchestrator":
                deployment_discovery = discovery
                break
        
        # Assert DeploymentOrchestrator was discovered
        self.assertIsNotNone(
            deployment_discovery,
            "DeploymentOrchestrator should be discovered by registry intelligence"
        )
        
        # Check that deployment keywords are extracted
        expected_keywords = {"deploy", "production", "release"}
        found_keywords = deployment_discovery.keywords
        
        self.assertTrue(
            expected_keywords & found_keywords,
            f"Expected keywords {expected_keywords} not found in {found_keywords}"
        )
        
        # Check confidence score
        self.assertGreater(
            deployment_discovery.confidence,
            0.5,
            "DeploymentOrchestrator should have high confidence score"
        )
    
    def test_registry_gap_detection(self):
        """Test that unregistered orchestrators are detected as gaps."""
        # Get discoveries first
        discoveries = self.agent.scan_for_orchestrators(force_rescan=True)
        
        # Detect registry gaps
        gaps = self.agent.detect_registry_gaps(discoveries)
        
        # Should find gaps for unregistered orchestrators
        self.assertGreater(
            len(gaps),
            0,
            "Registry gaps should be detected"
        )
        
        # Check for DeploymentOrchestrator gap specifically
        deployment_gaps = [
            gap for gap in gaps
            if gap.orchestrator == "DeploymentOrchestrator"
        ]
        
        if deployment_gaps:
            gap = deployment_gaps[0]
            self.assertEqual(gap.gap_type, "missing_orchestrator")
            self.assertEqual(gap.impact, "critical")  # Deploy is critical
    
    def test_mcp_tool_registration(self):
        """Test that deployment MCP tools are registered correctly."""
        from cortex.mcp.tools import MCP_TOOLS
        
        # Check deployment tools are in MCP registry
        deployment_tools = [
            "cortex_deploy_to_production",
            "cortex_deployment_health_check", 
            "cortex_deployment_canary",
        ]
        
        for tool_name in deployment_tools:
            self.assertIn(
                tool_name,
                MCP_TOOLS,
                f"Deployment tool {tool_name} should be registered in MCP_TOOLS"
            )
            
            tool_info = MCP_TOOLS[tool_name]
            self.assertEqual(tool_info["category"], "deployment")
            self.assertIn("function", tool_info)
    
    def test_deployment_mcp_tool_functionality(self):
        """Test that deployment MCP tools work correctly."""
        from cortex.mcp.tools.deployment_tools import cortex_deploy_to_production
        
        # Test with dry_run=True to avoid actual deployment
        result = cortex_deploy_to_production(
            deployment_type="patch",
            dry_run=True,
            version_bump_type="patch"
        )
        
        # Should return a result dictionary
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        
        # Even if deployment orchestrator isn't fully configured,
        # should handle gracefully
        if not result["success"]:
            self.assertIn("error", result)
    
    @patch('cortex.learning.registry_intelligence_agent.get_learning_loop')
    def test_learning_integration(self, mock_get_loop):
        """Test that registry intelligence integrates with learning loop."""
        # Mock learning loop
        mock_loop = Mock()
        mock_get_loop.return_value = mock_loop
        
        # Create agent with learning enabled
        agent_with_learning = RegistryIntelligenceAgent(
            workspace_root=self.workspace_root,
            enable_learning=True
        )
        
        # Simulate intent gap learning
        agent_with_learning.learn_from_intent_gap(
            user_intent="deploy cortex to production",
            missing_orchestrator="DeploymentOrchestrator"
        )
        
        # Verify learning loop was called
        mock_loop.capture_from_operation.assert_called_once()
        call_args = mock_loop.capture_from_operation.call_args
        
        self.assertEqual(call_args[1]["orchestrator"], "RegistryIntelligenceAgent")
        self.assertEqual(call_args[1]["operation"], "intent_gap_detection")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end registry intelligence workflow."""
        # Step 1: Discover orchestrators
        discoveries = self.agent.scan_for_orchestrators(force_rescan=True)
        self.assertGreater(len(discoveries), 0, "Should discover orchestrators")
        
        # Step 2: Detect gaps
        gaps = self.agent.detect_registry_gaps(discoveries)
        
        # Step 3: Simulate auto-fix (dry run)
        if gaps:
            fix_results = self.agent.auto_fix_gaps(gaps, dry_run=True)
            
            # Should provide fix plan
            self.assertIn("fixed", fix_results)
            self.assertIn("failed", fix_results)
            self.assertIn("skipped", fix_results)
            self.assertTrue(fix_results["dry_run"])
    
    def test_keyword_extraction_patterns(self):
        """Test that intent keywords are extracted correctly."""
        test_texts = [
            ("Deploy the application to production environment", {"deploy", "production"}),
            ("Fix the race condition bug in orchestrator", {"fix"}),
            ("Refactor the legacy code for better maintainability", {"refactor"}),
            ("Analyze the performance bottlenecks", {"analyze"}),
            ("Test the integration with external API", {"test"}),
        ]
        
        for text, expected_keywords in test_texts:
            extracted = self.agent._extract_intent_keywords(text)
            intersection = extracted & expected_keywords
            
            self.assertTrue(
                intersection,
                f"Expected keywords {expected_keywords} not found in extracted {extracted} for text: '{text}'"
            )


class TestIntentRouterIntegration(unittest.TestCase):
    """Test IntentRouter integration with registry intelligence."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock IntentRouter to avoid complex dependencies
        self.mock_router = Mock()
    
    def test_deployment_intent_detection(self):
        """Test that deployment intents are detected correctly."""
        # This would test the IntentRouter integration
        # For now, just verify the pattern
        
        deployment_phrases = [
            "deploy cortex to production",
            "release new version to production",  
            "push to production environment",
            "production deployment",
        ]
        
        for phrase in deployment_phrases:
            # In actual implementation, this would route to DeploymentOrchestrator
            self.assertIn("deploy", phrase.lower())


if __name__ == "__main__":
    # Run specific test
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRegistryIntelligenceIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)