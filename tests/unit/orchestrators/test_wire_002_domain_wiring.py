"""
WIRE-002 Test Suite - Domain Orchestrator Wiring Tests

AC-TRANSFORM-001-WIRE-002: Tests for domain orchestrator registration

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
from cortex.orchestrators.core.wire_002_domain_wiring import (
    DomainOrchestratorWiring,
    execute_wire_002
)
from cortex.core.interfaces import IOrchestrator


class TestDomainHandlerWiring:
    """Test suite for domain handler registration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.wiring = DomainOrchestratorWiring(registry=self.registry)
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_wire_domain_handlers_success(self):
        """Test successful wiring of all domain handlers"""
        result = self.wiring.wire_domain_handlers()
        assert result is True
        
        # Verify all 6 handlers registered
        domain_orchs = self.registry.get_by_category(OrchestratorCategory.DOMAIN)
        assert len(domain_orchs) >= 6
    
    def test_create_handler_registered(self):
        """Test CreateHandler specific registration"""
        self.wiring.wire_domain_handlers()
        
        metadata = self.registry.get_orchestrator("domain_create")
        assert metadata is not None
        assert metadata.category == OrchestratorCategory.DOMAIN
        assert "creation" in metadata.capabilities
        assert "create" in metadata.routing_keywords
    
    def test_modify_handler_registered(self):
        """Test ModifyHandler specific registration"""
        self.wiring.wire_domain_handlers()
        
        metadata = self.registry.get_orchestrator("domain_modify")
        assert metadata is not None
        assert "modification" in metadata.capabilities
        assert "modify" in metadata.routing_keywords
    
    def test_fix_handler_registered(self):
        """Test FixHandler specific registration"""
        self.wiring.wire_domain_handlers()
        
        metadata = self.registry.get_orchestrator("domain_fix")
        assert metadata is not None
        assert "error_recovery" in metadata.capabilities
        assert "fix" in metadata.routing_keywords
    
    def test_analyze_handler_registered(self):
        """Test AnalysisHandler specific registration"""
        self.wiring.wire_domain_handlers()
        
        metadata = self.registry.get_orchestrator("domain_analyze")
        assert metadata is not None
        assert "analysis" in metadata.capabilities
        assert "analyze" in metadata.routing_keywords
    
    def test_optimize_handler_registered(self):
        """Test OptimizationHandler specific registration"""
        self.wiring.wire_domain_handlers()
        
        metadata = self.registry.get_orchestrator("domain_optimize")
        assert metadata is not None
        assert "optimization" in metadata.capabilities
        assert "optimize" in metadata.routing_keywords
    
    def test_integrate_handler_registered(self):
        """Test IntegrationHandler specific registration"""
        self.wiring.wire_domain_handlers()
        
        metadata = self.registry.get_orchestrator("domain_integrate")
        assert metadata is not None
        assert "integration" in metadata.capabilities
        assert "integrate" in metadata.routing_keywords


class TestBusinessDomainOrchestratorWiring:
    """Test suite for business domain orchestrator registration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.wiring = DomainOrchestratorWiring(registry=self.registry)
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_wire_business_orchestrators_success(self):
        """Test successful wiring of business domain orchestrators"""
        result = self.wiring.wire_business_domain_orchestrators()
        assert result is True
    
    def test_financial_orchestrator_registered(self):
        """Test FinancialOrchestrator specific registration"""
        self.wiring.wire_business_domain_orchestrators()
        
        metadata = self.registry.get_orchestrator("business_financial")
        assert metadata is not None
        assert "financial_processing" in metadata.capabilities
        assert "financial" in metadata.routing_keywords
    
    def test_ecommerce_orchestrator_registered(self):
        """Test EcommerceOrchestrator specific registration"""
        self.wiring.wire_business_domain_orchestrators()
        
        metadata = self.registry.get_orchestrator("business_ecommerce")
        assert metadata is not None
        assert "product_management" in metadata.capabilities
        assert "ecommerce" in metadata.routing_keywords
    
    def test_healthcare_orchestrator_registered(self):
        """Test HealthcareOrchestrator specific registration"""
        self.wiring.wire_business_domain_orchestrators()
        
        metadata = self.registry.get_orchestrator("business_healthcare")
        assert metadata is not None
        assert "patient_management" in metadata.capabilities
        assert "healthcare" in metadata.routing_keywords


class TestInfrastructureOrchestratorWiring:
    """Test suite for infrastructure orchestrator registration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.wiring = DomainOrchestratorWiring(registry=self.registry)
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_wire_infrastructure_orchestrators_success(self):
        """Test successful wiring of infrastructure orchestrators"""
        result = self.wiring.wire_infrastructure_orchestrators()
        assert result is True
    
    def test_defense_orchestrator_registered(self):
        """Test DefenseOrchestrator specific registration"""
        self.wiring.wire_infrastructure_orchestrators()
        
        metadata = self.registry.get_orchestrator("security_defense")
        assert metadata is not None
        assert "threat_detection" in metadata.capabilities
        assert "defense" in metadata.routing_keywords
    
    def test_hot_reload_orchestrator_registered(self):
        """Test HotReloadOrchestrator specific registration"""
        self.wiring.wire_infrastructure_orchestrators()
        
        metadata = self.registry.get_orchestrator("devx_hot_reload")
        assert metadata is not None
        assert "live_reload" in metadata.capabilities
        assert "reload" in metadata.routing_keywords
    
    def test_vacuum_orchestrator_registered(self):
        """Test VacuumOrchestrator specific registration"""
        self.wiring.wire_infrastructure_orchestrators()
        
        metadata = self.registry.get_orchestrator("resource_vacuum")
        assert metadata is not None
        assert "cleanup" in metadata.capabilities
        assert "vacuum" in metadata.routing_keywords


class TestWire002Integration:
    """Integration tests for complete WIRE-002 execution"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.wiring = DomainOrchestratorWiring(registry=self.registry)
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_execute_all_wiring(self):
        """Test full WIRE-002 execution"""
        result = self.wiring.execute_all_wiring()
        
        assert "results" in result
        assert "summary" in result
        
        # Verify all 3 categories were executed
        results = result["results"]
        assert results["domain_handlers"] is True
        assert results["business_orchestrators"] is True
        assert results["infrastructure_orchestrators"] is True
    
    def test_total_orchestrators_registered(self):
        """Test that total 12 domain orchestrators are registered"""
        self.wiring.execute_all_wiring()
        
        domain_orchs = self.registry.get_by_category(OrchestratorCategory.DOMAIN)
        assert len(domain_orchs) == 12
    
    def test_execute_wire_002_function(self):
        """Test execute_wire_002 standalone function"""
        result = execute_wire_002()
        
        assert "results" in result
        assert "summary" in result
        
        # Verify success
        results = result["results"]
        assert results["domain_handlers"] is True
        assert results["business_orchestrators"] is True
        assert results["infrastructure_orchestrators"] is True


class TestWire002CapabilityQueries:
    """Test capability discovery for WIRE-002 orchestrators"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.wiring = DomainOrchestratorWiring(registry=self.registry)
        self.wiring.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_find_by_capability_creation(self):
        """Test finding CreateHandler by capability"""
        orchestrators = self.registry.get_by_capability("creation")
        assert len(orchestrators) > 0
        assert any(o.domain == "domain_create" for o in orchestrators)
    
    def test_find_by_capability_financial(self):
        """Test finding FinancialOrchestrator by capability"""
        orchestrators = self.registry.get_by_capability("financial_processing")
        assert len(orchestrators) > 0
        assert any(o.domain == "business_financial" for o in orchestrators)
    
    def test_find_by_capability_security(self):
        """Test finding DefenseOrchestrator by capability"""
        orchestrators = self.registry.get_by_capability("threat_detection")
        assert len(orchestrators) > 0
        assert any(o.domain == "security_defense" for o in orchestrators)
    
    def test_find_by_keyword_create(self):
        """Test finding CreateHandler by keyword"""
        orchestrators = self.registry.get_by_keyword("create")
        assert len(orchestrators) > 0
        assert any(o.domain == "domain_create" for o in orchestrators)
    
    def test_find_by_keyword_financial(self):
        """Test finding FinancialOrchestrator by keyword"""
        orchestrators = self.registry.get_by_keyword("financial")
        assert len(orchestrators) > 0
        assert any(o.domain == "business_financial" for o in orchestrators)
    
    def test_find_by_keyword_security(self):
        """Test finding DefenseOrchestrator by keyword"""
        orchestrators = self.registry.get_by_keyword("defense")
        assert len(orchestrators) > 0
        assert any(o.domain == "security_defense" for o in orchestrators)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
