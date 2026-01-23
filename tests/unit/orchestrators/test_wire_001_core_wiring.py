"""
WIRE-001 Test Suite - Core Orchestrator Registration Tests

AC-TRANSFORM-001-WIRE-001: Tests for core orchestrator registration
- Basic wiring functionality tests
- Registry population tests
- Capability configuration tests

Author: GitHub Copilot
Date: 2026-01-24
"""

import pytest
from unittest.mock import Mock

from cortex.orchestrators.core.orchestrator_wiring import (
    OrchestratorWiringRegistry,
    OrchestratorCategory,
    get_wiring_registry,
    reset_wiring_registry
)
from cortex.core.interfaces import IOrchestrator


class TestCoreOrchestratorWiring:
    """Test suite for WIRE-001 core orchestrator registration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a fresh registry for each test
        reset_wiring_registry()
        self.registry = get_wiring_registry()
    
    def teardown_method(self):
        """Clean up after tests"""
        # Reset singleton
        reset_wiring_registry()
    
    def test_core_orchestrators_registry_basics(self):
        """Test basic core orchestrator registration"""
        # Register 5 mock core orchestrators
        core_orchestrators = [
            ("interaction", ["comprehension", "session_management"]),
            ("intent_routing", ["routing", "classification"]),
            ("tdd", ["test_generation", "coverage"]),
            ("workflow", ["execution", "steps"]),
            ("wrapped_tdd", ["governance", "compliance"]),
        ]
        
        for domain, capabilities in core_orchestrators:
            mock_orch = Mock(spec=IOrchestrator)
            result = self.registry.register_orchestrator(
                domain=domain,
                orchestrator=mock_orch,
                category=OrchestratorCategory.CORE,
                capabilities=capabilities
            )
            assert result.is_ok()
        
        # Verify all registered
        core = self.registry.get_by_category(OrchestratorCategory.CORE)
        assert len(core) == 5
    
    def test_interaction_orchestrator_registration(self):
        """Test InteractionOrchestrator specific registration"""
        mock_orch = Mock(spec=IOrchestrator)
        result = self.registry.register_orchestrator(
            domain="interaction",
            orchestrator=mock_orch,
            category=OrchestratorCategory.CORE,
            capabilities=["comprehension", "session_management", "context_preservation"],
            routing_keywords=["understand", "analyze", "comprehend", "listen"],
            version="1.0"
        )
        
        assert result.is_ok()
        metadata = self.registry.get_orchestrator("interaction")
        assert metadata is not None
        assert metadata.category == OrchestratorCategory.CORE
        assert "comprehension" in metadata.capabilities
        assert "understand" in metadata.routing_keywords
    
    def test_intent_router_registration(self):
        """Test IntentRouter specific registration"""
        mock_orch = Mock(spec=IOrchestrator)
        result = self.registry.register_orchestrator(
            domain="intent_routing",
            orchestrator=mock_orch,
            category=OrchestratorCategory.CORE,
            capabilities=["intent_classification", "domain_selection", "routing"],
            routing_keywords=["route", "select", "classify"],
            version="1.0"
        )
        
        assert result.is_ok()
        metadata = self.registry.get_orchestrator("intent_routing")
        assert metadata is not None
        assert "routing" in metadata.capabilities
    
    def test_tdd_orchestrator_registration(self):
        """Test TDDOrchestrator specific registration"""
        mock_orch = Mock(spec=IOrchestrator)
        result = self.registry.register_orchestrator(
            domain="tdd",
            orchestrator=mock_orch,
            category=OrchestratorCategory.CORE,
            capabilities=["test_generation", "test_execution", "coverage_analysis"],
            routing_keywords=["test", "tdd", "coverage", "unit_test"],
            version="1.0"
        )
        
        assert result.is_ok()
        metadata = self.registry.get_orchestrator("tdd")
        assert metadata is not None
        assert "test_generation" in metadata.capabilities
    
    def test_workflow_orchestrator_registration(self):
        """Test WorkflowOrchestrator specific registration"""
        mock_orch = Mock(spec=IOrchestrator)
        result = self.registry.register_orchestrator(
            domain="workflow",
            orchestrator=mock_orch,
            category=OrchestratorCategory.CORE,
            capabilities=["workflow_execution", "step_management", "state_transitions"],
            routing_keywords=["workflow", "step", "execute", "chain"],
            version="1.0"
        )
        
        assert result.is_ok()
        metadata = self.registry.get_orchestrator("workflow")
        assert metadata is not None
        assert "workflow_execution" in metadata.capabilities
    
    def test_wrapped_tdd_orchestrator_registration(self):
        """Test WrappedTDDOrchestrator specific registration"""
        mock_orch = Mock(spec=IOrchestrator)
        result = self.registry.register_orchestrator(
            domain="wrapped_tdd",
            orchestrator=mock_orch,
            category=OrchestratorCategory.CORE,
            capabilities=["tdd_with_governance", "compliance_checking", "governance_enforcement"],
            routing_keywords=["governed_test", "compliant_test"],
            version="1.0"
        )
        
        assert result.is_ok()
        metadata = self.registry.get_orchestrator("wrapped_tdd")
        assert metadata is not None
        assert "governance_enforcement" in metadata.capabilities


class TestWire001CapabilityQueries:
    """Test capability queries for WIRE-001"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        
        # Register core orchestrators with keywords
        self.core_domains = [
            ("interaction", ["comprehension", "session_management"], ["understand", "analyze"]),
            ("intent_routing", ["routing", "classification"], ["route", "select"]),
            ("tdd", ["test_generation", "coverage"], ["test", "tdd"]),
            ("workflow", ["execution", "steps"], ["workflow", "step"]),
            ("wrapped_tdd", ["governance", "compliance"], ["governed_test", "compliant"]),
        ]
        
        for domain, capabilities, keywords in self.core_domains:
            mock_orch = Mock(spec=IOrchestrator)
            self.registry.register_orchestrator(
                domain=domain,
                orchestrator=mock_orch,
                category=OrchestratorCategory.CORE,
                capabilities=capabilities,
                routing_keywords=keywords
            )
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_find_by_capability_test_generation(self):
        """Test finding TDDOrchestrator by test_generation capability"""
        orchestrators = self.registry.get_by_capability("test_generation")
        assert len(orchestrators) > 0
        assert any(o.domain == "tdd" for o in orchestrators)
    
    def test_find_by_capability_routing(self):
        """Test finding IntentRouter by routing capability"""
        orchestrators = self.registry.get_by_capability("routing")
        assert len(orchestrators) > 0
        assert any(o.domain == "intent_routing" for o in orchestrators)
    
    def test_find_by_capability_governance(self):
        """Test finding WrappedTDDOrchestrator by governance capability"""
        orchestrators = self.registry.get_by_capability("governance")
        assert len(orchestrators) > 0
        assert any(o.domain == "wrapped_tdd" for o in orchestrators)
    
    def test_find_by_keyword_test(self):
        """Test finding TDDOrchestrator by 'test' keyword"""
        orchestrators = self.registry.get_by_keyword("test")
        assert len(orchestrators) > 0
        assert any(o.domain == "tdd" for o in orchestrators)
    
    def test_find_by_keyword_workflow(self):
        """Test finding WorkflowOrchestrator by 'workflow' keyword"""
        orchestrators = self.registry.get_by_keyword("workflow")
        assert len(orchestrators) > 0
        assert any(o.domain == "workflow" for o in orchestrators)


class TestWire001Status:
    """Test WIRE-001 status reporting"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_wiring_status_empty(self):
        """Test wiring status when no orchestrators registered"""
        status = self.registry.get_wiring_status()
        assert status["total_wired"] == 0
        assert status["coverage_percentage"] == 0.0
    
    def test_wiring_status_partial(self):
        """Test wiring status with 3 core orchestrators (60%)"""
        for domain in ["interaction", "intent_routing", "tdd"]:
            mock_orch = Mock(spec=IOrchestrator)
            self.registry.register_orchestrator(
                domain=domain,
                orchestrator=mock_orch,
                category=OrchestratorCategory.CORE,
                capabilities=["feature"]
            )
        
        status = self.registry.get_wiring_status()
        assert status["total_wired"] == 3
        assert status["by_category"]["core"] == 3
    
    def test_wiring_status_full_core(self):
        """Test wiring status with all 5 core orchestrators"""
        for domain in ["interaction", "intent_routing", "tdd", "workflow", "wrapped_tdd"]:
            mock_orch = Mock(spec=IOrchestrator)
            self.registry.register_orchestrator(
                domain=domain,
                orchestrator=mock_orch,
                category=OrchestratorCategory.CORE,
                capabilities=["feature"]
            )
        
        status = self.registry.get_wiring_status()
        assert status["total_wired"] == 5
        assert status["by_category"]["core"] == 5
        assert len(status["orchestrators"]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
