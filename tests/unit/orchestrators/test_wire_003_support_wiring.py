"""
WIRE-003 Test Suite - Support Orchestrator Wiring Tests

AC-TRANSFORM-001-WIRE-003: Tests for support orchestrator registration

Author: GitHub Copilot
Date: 2026-01-24
"""

import pytest

from cortex.orchestrators.core.orchestrator_wiring import (
    OrchestratorCategory,
    get_wiring_registry,
    reset_wiring_registry
)
from cortex.orchestrators.core.wire_003_support_wiring import (
    SupportOrchestratorWiring,
    execute_wire_003
)


class TestSupportOrchestratorWiring:
    """Test suite for support orchestrator registration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.wiring = SupportOrchestratorWiring(registry=self.registry)
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_wire_support_orchestrators_success(self):
        """Test successful wiring of all support orchestrators"""
        result = self.wiring.wire_support_orchestrators()
        assert result is True
    
    def test_onboarding_orchestrator_registered(self):
        """Test OnboardingOrchestrator specific registration"""
        self.wiring.wire_support_orchestrators()
        
        metadata = self.registry.get_orchestrator("support_onboarding")
        assert metadata is not None
        assert metadata.category == OrchestratorCategory.SUPPORT
        assert "user_onboarding" in metadata.capabilities
        assert "onboard" in metadata.routing_keywords
    
    def test_discovery_orchestrator_registered(self):
        """Test ToolDiscoveryOrchestrator specific registration"""
        self.wiring.wire_support_orchestrators()
        
        metadata = self.registry.get_orchestrator("support_discovery")
        assert metadata is not None
        assert "capability_discovery" in metadata.capabilities
        assert "discover" in metadata.routing_keywords
    
    def test_upgrade_orchestrator_registered(self):
        """Test UpgradeOrchestrator specific registration"""
        self.wiring.wire_support_orchestrators()
        
        metadata = self.registry.get_orchestrator("support_upgrade")
        assert metadata is not None
        assert "version_upgrade" in metadata.capabilities
        assert "upgrade" in metadata.routing_keywords
    
    def test_rollback_orchestrator_registered(self):
        """Test RollbackOrchestrator specific registration"""
        self.wiring.wire_support_orchestrators()
        
        metadata = self.registry.get_orchestrator("support_rollback")
        assert metadata is not None
        assert "rollback" in metadata.capabilities
        assert "rollback" in metadata.routing_keywords
    
    def test_setup_orchestrator_registered(self):
        """Test SetupOrchestrator specific registration"""
        self.wiring.wire_support_orchestrators()
        
        metadata = self.registry.get_orchestrator("support_setup")
        assert metadata is not None
        assert "environment_setup" in metadata.capabilities
        assert "setup" in metadata.routing_keywords
    
    def test_composed_orchestrator_registered(self):
        """Test ComposedOrchestrator specific registration"""
        self.wiring.wire_support_orchestrators()
        
        metadata = self.registry.get_orchestrator("support_composed")
        assert metadata is not None
        assert "composition" in metadata.capabilities
        assert "compose" in metadata.routing_keywords


class TestWire003Integration:
    """Integration tests for WIRE-003 execution"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.wiring = SupportOrchestratorWiring(registry=self.registry)
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_execute_all_wiring(self):
        """Test full WIRE-003 execution"""
        result = self.wiring.execute_all_wiring()
        
        assert "results" in result
        assert "summary" in result
        assert result["results"]["support_orchestrators"] is True
        assert result["summary"]["status"] == "SUCCESS"
    
    def test_total_orchestrators_registered(self):
        """Test that all 6 support orchestrators are registered"""
        self.wiring.execute_all_wiring()
        
        support_orchs = self.registry.get_by_category(OrchestratorCategory.SUPPORT)
        assert len(support_orchs) == 6
    
    def test_execute_wire_003_function(self):
        """Test execute_wire_003 standalone function"""
        result = execute_wire_003()
        
        assert "results" in result
        assert "summary" in result
        assert result["summary"]["status"] == "SUCCESS"


class TestWire003CapabilityQueries:
    """Test capability discovery for WIRE-003 orchestrators"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.wiring = SupportOrchestratorWiring(registry=self.registry)
        self.wiring.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_find_by_capability_onboarding(self):
        """Test finding OnboardingOrchestrator by capability"""
        orchestrators = self.registry.get_by_capability("user_onboarding")
        assert len(orchestrators) > 0
        assert any(o.domain == "support_onboarding" for o in orchestrators)
    
    def test_find_by_capability_discovery(self):
        """Test finding ToolDiscoveryOrchestrator by capability"""
        orchestrators = self.registry.get_by_capability("capability_discovery")
        assert len(orchestrators) > 0
        assert any(o.domain == "support_discovery" for o in orchestrators)
    
    def test_find_by_capability_upgrade(self):
        """Test finding UpgradeOrchestrator by capability"""
        orchestrators = self.registry.get_by_capability("version_upgrade")
        assert len(orchestrators) > 0
        assert any(o.domain == "support_upgrade" for o in orchestrators)
    
    def test_find_by_keyword_onboard(self):
        """Test finding OnboardingOrchestrator by keyword"""
        orchestrators = self.registry.get_by_keyword("onboard")
        assert len(orchestrators) > 0
        assert any(o.domain == "support_onboarding" for o in orchestrators)
    
    def test_find_by_keyword_setup(self):
        """Test finding SetupOrchestrator by keyword"""
        orchestrators = self.registry.get_by_keyword("setup")
        assert len(orchestrators) > 0
        assert any(o.domain == "support_setup" for o in orchestrators)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
