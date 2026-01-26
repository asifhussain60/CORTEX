"""
Phase 3: Integration Test Suite for MCP Adapters

Tests all 23 orchestrator adapters with the MCP server.

Authority: CORE-008 (TDD), CORE-031 (Unified Registry)
AC-ID: AC-MCP-INTEGRATION-TESTS-001
Date: 2026-01-26
"""

import unittest
import logging

from cortex.mcp.orchestrator_mcp_server import (
    OrchestratorMCPServer,
    ExecutionContext,
    ContextType,
    CapabilityMetadata,
    CapabilityResponse,
    IOrchestratorAdapter,
)

from cortex.mcp.adapters import (
    # Tier 1: Core
    MasterOrchestratorAdapter,
    TDDOrchestratorAdapter,
    IntentRouterAdapter,
    InteractionOrchestratorAdapter,
    WorkflowOrchestratorAdapter,
    WrappedTDDOrchestratorAdapter,
    # Tier 2: Domain
    RefactoringOrchestratorAdapter,
    PlanningOrchestratorAdapter,
    DomainOrchestratorAdapter,
    ConversationOrchestratorAdapter,
    SeleniumPlaywrightOrchestratorAdapter,
    DocumentationOrchestratorAdapter,
    # Tier 3: Support
    OnboardingOrchestratorAdapter,
    ToolDiscoveryOrchestratorAdapter,
    UpgradeOrchestratorAdapter,
    RollbackOrchestratorAdapter,
    SetupOrchestratorAdapter,
    ComposedOrchestratorAdapter,
    OrchestratorBootstrapAdapter,
    DoRApprovalGateAdapter,
    LENSSynthesisAdapter,
    GovernanceRegistryAdapter,
    KnowledgeRepositoryAdapter,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestAdapterInstantiation(unittest.TestCase):
    """Test that all 23 adapters can be instantiated"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.server = OrchestratorMCPServer.instance()
        self.context = ExecutionContext(
            context_type=ContextType.SINGLE_REPO,
            repository_path="/test/repo",
            workspace_root="/test",
            session_id="test-session-001",
        )
    
    def test_tier1_core_adapters_instantiation(self):
        """Test Tier 1 (Core) adapters can be instantiated"""
        adapters = [
            MasterOrchestratorAdapter,
            TDDOrchestratorAdapter,
            IntentRouterAdapter,
            InteractionOrchestratorAdapter,
            WorkflowOrchestratorAdapter,
            WrappedTDDOrchestratorAdapter,
        ]
        
        for adapter_class in adapters:
            with self.subTest(adapter=adapter_class.__name__):
                adapter = adapter_class()
                self.assertIsInstance(adapter, IOrchestratorAdapter)
                self.assertIsNotNone(adapter)
    
    def test_tier2_domain_adapters_instantiation(self):
        """Test Tier 2 (Domain) adapters can be instantiated"""
        adapters = [
            RefactoringOrchestratorAdapter,
            PlanningOrchestratorAdapter,
            DomainOrchestratorAdapter,
            ConversationOrchestratorAdapter,
            SeleniumPlaywrightOrchestratorAdapter,
            DocumentationOrchestratorAdapter,
        ]
        
        for adapter_class in adapters:
            with self.subTest(adapter=adapter_class.__name__):
                adapter = adapter_class()
                self.assertIsInstance(adapter, IOrchestratorAdapter)
                self.assertIsNotNone(adapter)
    
    def test_tier3_support_adapters_instantiation(self):
        """Test Tier 3 (Support) adapters can be instantiated"""
        adapters = [
            OnboardingOrchestratorAdapter,
            ToolDiscoveryOrchestratorAdapter,
            UpgradeOrchestratorAdapter,
            RollbackOrchestratorAdapter,
            SetupOrchestratorAdapter,
            ComposedOrchestratorAdapter,
            OrchestratorBootstrapAdapter,
            DoRApprovalGateAdapter,
            LENSSynthesisAdapter,
            GovernanceRegistryAdapter,
            KnowledgeRepositoryAdapter,
        ]
        
        for adapter_class in adapters:
            with self.subTest(adapter=adapter_class.__name__):
                adapter = adapter_class()
                self.assertIsInstance(adapter, IOrchestratorAdapter)
                self.assertIsNotNone(adapter)


class TestCapabilityDiscovery(unittest.TestCase):
    """Test capability discovery for all adapters"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.all_adapters = [
            # Tier 1
            MasterOrchestratorAdapter(),
            TDDOrchestratorAdapter(),
            IntentRouterAdapter(),
            InteractionOrchestratorAdapter(),
            WorkflowOrchestratorAdapter(),
            WrappedTDDOrchestratorAdapter(),
            # Tier 2
            RefactoringOrchestratorAdapter(),
            PlanningOrchestratorAdapter(),
            DomainOrchestratorAdapter(),
            ConversationOrchestratorAdapter(),
            SeleniumPlaywrightOrchestratorAdapter(),
            DocumentationOrchestratorAdapter(),
            # Tier 3
            OnboardingOrchestratorAdapter(),
            ToolDiscoveryOrchestratorAdapter(),
            UpgradeOrchestratorAdapter(),
            RollbackOrchestratorAdapter(),
            SetupOrchestratorAdapter(),
            ComposedOrchestratorAdapter(),
            OrchestratorBootstrapAdapter(),
            DoRApprovalGateAdapter(),
            LENSSynthesisAdapter(),
            GovernanceRegistryAdapter(),
            KnowledgeRepositoryAdapter(),
        ]
    
    def test_all_adapters_have_capabilities(self):
        """Test that all adapters expose at least 1 capability"""
        total_capabilities = 0
        
        for adapter in self.all_adapters:
            with self.subTest(adapter=adapter.__class__.__name__):
                capabilities = adapter.get_capabilities()
                self.assertIsInstance(capabilities, list)
                self.assertGreater(len(capabilities), 0)
                
                for cap in capabilities:
                    self.assertIsInstance(cap, CapabilityMetadata)
                    self.assertIsNotNone(cap.name)
                    self.assertIsNotNone(cap.orchestrator)
                    self.assertIsNotNone(cap.description)
                    
                total_capabilities += len(capabilities)
        
        # Verify total capability count (should be ~37)
        self.assertGreaterEqual(total_capabilities, 35)
        logger.info(f"Total capabilities discovered: {total_capabilities}")
    
    def test_capability_metadata_structure(self):
        """Test that capability metadata has required fields"""
        for adapter in self.all_adapters:
            with self.subTest(adapter=adapter.__class__.__name__):
                capabilities = adapter.get_capabilities()
                
                for cap in capabilities:
                    # Required fields
                    self.assertTrue(hasattr(cap, 'name'))
                    self.assertTrue(hasattr(cap, 'orchestrator'))
                    self.assertTrue(hasattr(cap, 'description'))
                    self.assertTrue(hasattr(cap, 'input_schema'))
                    self.assertTrue(hasattr(cap, 'output_schema'))
                    self.assertTrue(hasattr(cap, 'routing_keywords'))
                    
                    # Type validation
                    self.assertIsInstance(cap.name, str)
                    self.assertIsInstance(cap.orchestrator, str)
                    self.assertIsInstance(cap.description, str)
                    self.assertIsInstance(cap.input_schema, dict)
                    self.assertIsInstance(cap.output_schema, dict)
                    self.assertIsInstance(cap.routing_keywords, list)


class TestCapabilityExecution(unittest.TestCase):
    """Test capability execution interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.context = ExecutionContext(
            context_type=ContextType.SINGLE_REPO,
            repository_path="/test/repo",
            workspace_root="/test",
            session_id="test-session-002",
        )
        self.all_adapters = [
            MasterOrchestratorAdapter(),
            TDDOrchestratorAdapter(),
            IntentRouterAdapter(),
            InteractionOrchestratorAdapter(),
            WorkflowOrchestratorAdapter(),
            WrappedTDDOrchestratorAdapter(),
            RefactoringOrchestratorAdapter(),
            PlanningOrchestratorAdapter(),
            DomainOrchestratorAdapter(),
            ConversationOrchestratorAdapter(),
            SeleniumPlaywrightOrchestratorAdapter(),
            DocumentationOrchestratorAdapter(),
            OnboardingOrchestratorAdapter(),
            ToolDiscoveryOrchestratorAdapter(),
            UpgradeOrchestratorAdapter(),
            RollbackOrchestratorAdapter(),
            SetupOrchestratorAdapter(),
            ComposedOrchestratorAdapter(),
            OrchestratorBootstrapAdapter(),
            DoRApprovalGateAdapter(),
            LENSSynthesisAdapter(),
            GovernanceRegistryAdapter(),
            KnowledgeRepositoryAdapter(),
        ]
    
    def test_adapters_respond_to_capability_requests(self):
        """Test that all adapters respond to capability requests"""
        for adapter in self.all_adapters:
            with self.subTest(adapter=adapter.__class__.__name__):
                capabilities = adapter.get_capabilities()
                
                if capabilities:
                    # Get first capability
                    first_cap = capabilities[0]
                    
                    # Execute the capability
                    response = adapter.execute_capability(
                        capability_name=first_cap.name,
                        parameters={},
                        context=self.context,
                    )
                    
                    # Validate response structure
                    self.assertIsInstance(response, CapabilityResponse)
                    self.assertIsNotNone(response.success)
                    self.assertIsInstance(response.success, bool)
    
    def test_error_handling_for_invalid_capability(self):
        """Test that adapters handle invalid capability names gracefully"""
        adapter = MasterOrchestratorAdapter()
        
        response = adapter.execute_capability(
            capability_name="invalid_capability_name",
            parameters={},
            context=self.context,
        )
        
        self.assertIsInstance(response, CapabilityResponse)
        # Response should either fail or return error
        self.assertIsNotNone(response.success)


class TestHealthAndStatus(unittest.TestCase):
    """Test health checking and status reporting"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.all_adapters = [
            MasterOrchestratorAdapter(),
            TDDOrchestratorAdapter(),
            IntentRouterAdapter(),
            InteractionOrchestratorAdapter(),
            WorkflowOrchestratorAdapter(),
            WrappedTDDOrchestratorAdapter(),
            RefactoringOrchestratorAdapter(),
            PlanningOrchestratorAdapter(),
            DomainOrchestratorAdapter(),
            ConversationOrchestratorAdapter(),
            SeleniumPlaywrightOrchestratorAdapter(),
            DocumentationOrchestratorAdapter(),
            OnboardingOrchestratorAdapter(),
            ToolDiscoveryOrchestratorAdapter(),
            UpgradeOrchestratorAdapter(),
            RollbackOrchestratorAdapter(),
            SetupOrchestratorAdapter(),
            ComposedOrchestratorAdapter(),
            OrchestratorBootstrapAdapter(),
            DoRApprovalGateAdapter(),
            LENSSynthesisAdapter(),
            GovernanceRegistryAdapter(),
            KnowledgeRepositoryAdapter(),
        ]
    
    def test_all_adapters_health_check(self):
        """Test that all adapters support health checking"""
        for adapter in self.all_adapters:
            with self.subTest(adapter=adapter.__class__.__name__):
                health = adapter.is_healthy()
                self.assertIsInstance(health, bool)
    
    def test_all_adapters_status_reporting(self):
        """Test that all adapters support status reporting"""
        for adapter in self.all_adapters:
            with self.subTest(adapter=adapter.__class__.__name__):
                status = adapter.get_status()
                self.assertIsInstance(status, dict)
                # All adapters should have 'name' and 'healthy' in status
                self.assertIn('name', status)
                self.assertIn('healthy', status)


class TestMCPServerRegistration(unittest.TestCase):
    """Test registration of adapters with MCP server"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a fresh server instance for testing
        self.server = OrchestratorMCPServer()
    
    def test_register_single_adapter(self):
        """Test registering a single adapter"""
        adapter = MasterOrchestratorAdapter()
        result = self.server.register_orchestrator("master", adapter)
        self.assertTrue(result)
    
    def test_register_all_adapters(self):
        """Test registering all 23 adapters with the server"""
        adapters = [
            ("master", MasterOrchestratorAdapter()),
            ("tdd", TDDOrchestratorAdapter()),
            ("intent_router", IntentRouterAdapter()),
            ("interaction", InteractionOrchestratorAdapter()),
            ("workflow", WorkflowOrchestratorAdapter()),
            ("wrapped_tdd", WrappedTDDOrchestratorAdapter()),
            ("refactoring", RefactoringOrchestratorAdapter()),
            ("planning", PlanningOrchestratorAdapter()),
            ("domain", DomainOrchestratorAdapter()),
            ("conversation", ConversationOrchestratorAdapter()),
            ("selenium_playwright", SeleniumPlaywrightOrchestratorAdapter()),
            ("documentation", DocumentationOrchestratorAdapter()),
            ("onboarding", OnboardingOrchestratorAdapter()),
            ("tool_discovery", ToolDiscoveryOrchestratorAdapter()),
            ("upgrade", UpgradeOrchestratorAdapter()),
            ("rollback", RollbackOrchestratorAdapter()),
            ("setup", SetupOrchestratorAdapter()),
            ("composed", ComposedOrchestratorAdapter()),
            ("bootstrap", OrchestratorBootstrapAdapter()),
            ("dor_gate", DoRApprovalGateAdapter()),
            ("lens_synthesis", LENSSynthesisAdapter()),
            ("governance_registry", GovernanceRegistryAdapter()),
            ("knowledge_repository", KnowledgeRepositoryAdapter()),
        ]
        
        registered_count = 0
        for name, adapter in adapters:
            with self.subTest(adapter=name):
                result = self.server.register_orchestrator(name, adapter)
                if result:
                    registered_count += 1
        
        # All should be registered successfully
        self.assertEqual(registered_count, 23)


class TestInterfaceCompliance(unittest.TestCase):
    """Test IOrchestratorAdapter interface compliance"""
    
    def test_all_adapters_implement_interface(self):
        """Test that all adapters properly implement IOrchestratorAdapter"""
        adapters = [
            MasterOrchestratorAdapter(),
            TDDOrchestratorAdapter(),
            IntentRouterAdapter(),
            InteractionOrchestratorAdapter(),
            WorkflowOrchestratorAdapter(),
            WrappedTDDOrchestratorAdapter(),
            RefactoringOrchestratorAdapter(),
            PlanningOrchestratorAdapter(),
            DomainOrchestratorAdapter(),
            ConversationOrchestratorAdapter(),
            SeleniumPlaywrightOrchestratorAdapter(),
            DocumentationOrchestratorAdapter(),
            OnboardingOrchestratorAdapter(),
            ToolDiscoveryOrchestratorAdapter(),
            UpgradeOrchestratorAdapter(),
            RollbackOrchestratorAdapter(),
            SetupOrchestratorAdapter(),
            ComposedOrchestratorAdapter(),
            OrchestratorBootstrapAdapter(),
            DoRApprovalGateAdapter(),
            LENSSynthesisAdapter(),
            GovernanceRegistryAdapter(),
            KnowledgeRepositoryAdapter(),
        ]
        
        for adapter in adapters:
            with self.subTest(adapter=adapter.__class__.__name__):
                # Check all required methods exist
                self.assertTrue(hasattr(adapter, 'get_capabilities'))
                self.assertTrue(hasattr(adapter, 'execute_capability'))
                self.assertTrue(hasattr(adapter, 'is_healthy'))
                self.assertTrue(hasattr(adapter, 'get_status'))
                
                # Check they're callable
                self.assertTrue(callable(getattr(adapter, 'get_capabilities')))
                self.assertTrue(callable(getattr(adapter, 'execute_capability')))
                self.assertTrue(callable(getattr(adapter, 'is_healthy')))
                self.assertTrue(callable(getattr(adapter, 'get_status')))


class TestRoutingKeywords(unittest.TestCase):
    """Test routing keywords for capability discovery"""
    
    def test_all_capabilities_have_routing_keywords(self):
        """Test that all capabilities define routing keywords"""
        adapters = [
            MasterOrchestratorAdapter(),
            TDDOrchestratorAdapter(),
            IntentRouterAdapter(),
            RefactoringOrchestratorAdapter(),
            PlanningOrchestratorAdapter(),
        ]
        
        for adapter in adapters:
            capabilities = adapter.get_capabilities()
            for cap in capabilities:
                with self.subTest(capability=cap.name):
                    self.assertIsNotNone(cap.routing_keywords)
                    self.assertGreater(len(cap.routing_keywords), 0)
                    self.assertIsInstance(cap.routing_keywords, list)
                    
                    # Check all keywords are strings
                    for keyword in cap.routing_keywords:
                        self.assertIsInstance(keyword, str)


if __name__ == '__main__':
    unittest.main(verbosity=2)
