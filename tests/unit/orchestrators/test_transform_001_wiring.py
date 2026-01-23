"""
TRANSFORM-001 Test Suite - Orchestrator Wiring Implementation Tests

Tests for WIRE-001, WIRE-002, WIRE-003 orchestrator registration.

AC-TRANSFORM-001: Orchestrator Wiring Expansion (40 hours)
- Tests for orchestrator registration
- Tests for routing capabilities
- Tests for discovery API
- Integration tests for 17 orchestrators

Author: GitHub Copilot
Date: 2026-01-24
"""

import pytest
from unittest.mock import Mock

from cortex.orchestrators.core.orchestrator_wiring import (
    OrchestratorWiringRegistry,
    OrchestratorWiringMetadata,
    OrchestratorCategory,
    get_wiring_registry
)
from cortex.core.interfaces import IOrchestrator


class TestOrchestratorWiringRegistry:
    """Test suite for orchestrator wiring registry"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.registry = OrchestratorWiringRegistry()
        self.mock_orchestrator = Mock(spec=IOrchestrator)
    
    def test_register_orchestrator_success(self):
        """Test successful orchestrator registration"""
        # WIRE-001: Register Core Orchestrators
        result = self.registry.register_orchestrator(
            domain="interaction",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.CORE,
            capabilities=["comprehension", "session_management"],
            routing_keywords=["understand", "analyze"],
            version="1.0"
        )
        
        assert result.is_ok()
        assert "interaction" in self.registry.wired_orchestrators
        metadata = self.registry.get_orchestrator("interaction")
        assert metadata is not None
        assert metadata.domain == "interaction"
        assert metadata.category == OrchestratorCategory.CORE
        assert "comprehension" in metadata.capabilities
    
    def test_register_duplicate_domain_fails(self):
        """Test that registering duplicate domain fails"""
        # First registration succeeds
        result1 = self.registry.register_orchestrator(
            domain="test_domain",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.CORE,
            capabilities=["test"]
        )
        assert result1.is_ok()
        
        # Duplicate registration fails
        result2 = self.registry.register_orchestrator(
            domain="test_domain",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.DOMAIN,
            capabilities=["different"]
        )
        assert result2.is_err()
    
    def test_get_orchestrator_by_capability(self):
        """Test finding orchestrators by capability"""
        # Register multiple orchestrators with different capabilities
        self.registry.register_orchestrator(
            domain="tdd",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.CORE,
            capabilities=["test_generation", "coverage_analysis"]
        )
        
        self.registry.register_orchestrator(
            domain="refactoring",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.DOMAIN,
            capabilities=["code_refactoring", "pattern_detection"]
        )
        
        # Find by capability
        test_gen_orchestrators = self.registry.get_by_capability("test_generation")
        assert len(test_gen_orchestrators) == 1
        assert test_gen_orchestrators[0].domain == "tdd"
        
        refactor_orchestrators = self.registry.get_by_capability("code_refactoring")
        assert len(refactor_orchestrators) == 1
        assert refactor_orchestrators[0].domain == "refactoring"
    
    def test_get_orchestrator_by_category(self):
        """Test finding orchestrators by category"""
        # Register core orchestrator
        self.registry.register_orchestrator(
            domain="core1",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.CORE,
            capabilities=["feature1"]
        )
        
        # Register domain orchestrator
        self.registry.register_orchestrator(
            domain="domain1",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.DOMAIN,
            capabilities=["feature2"]
        )
        
        # Query by category
        core_orchestrators = self.registry.get_by_category(OrchestratorCategory.CORE)
        assert len(core_orchestrators) == 1
        assert core_orchestrators[0].domain == "core1"
        
        domain_orchestrators = self.registry.get_by_category(OrchestratorCategory.DOMAIN)
        assert len(domain_orchestrators) == 1
        assert domain_orchestrators[0].domain == "domain1"
    
    def test_get_orchestrator_by_keyword(self):
        """Test finding orchestrators by routing keyword"""
        # Register orchestrators with routing keywords
        self.registry.register_orchestrator(
            domain="tdd",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.CORE,
            capabilities=["test"],
            routing_keywords=["test", "tdd", "unit_test"]
        )
        
        self.registry.register_orchestrator(
            domain="refactoring",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.DOMAIN,
            capabilities=["refactor"],
            routing_keywords=["refactor", "pattern"]
        )
        
        # Find by keyword (case-insensitive)
        test_orchestrators = self.registry.get_by_keyword("test")
        assert len(test_orchestrators) == 1
        assert test_orchestrators[0].domain == "tdd"
        
        refactor_orchestrators = self.registry.get_by_keyword("refactor")
        assert len(refactor_orchestrators) == 1
        assert refactor_orchestrators[0].domain == "refactoring"
    
    def test_wiring_status(self):
        """Test wiring status reporting"""
        # Register some orchestrators
        for i in range(5):
            self.registry.register_orchestrator(
                domain=f"orchestrator_{i}",
                orchestrator=self.mock_orchestrator,
                category=OrchestratorCategory.CORE,
                capabilities=[f"capability_{i}"]
            )
        
        status = self.registry.get_wiring_status()
        
        assert status["total_wired"] == 5
        assert status["target_wired"] == 20
        assert status["by_category"]["core"] == 5
        assert len(status["orchestrators"]) == 5
    
    def test_metadata_to_dict(self):
        """Test OrchestratorWiringMetadata.to_dict()"""
        metadata = OrchestratorWiringMetadata(
            domain="test",
            orchestrator=self.mock_orchestrator,
            category=OrchestratorCategory.CORE,
            version="1.0",
            capabilities=["test"],
            routing_keywords=["keyword"]
        )
        
        data = metadata.to_dict()
        
        assert data["domain"] == "test"
        assert data["category"] == "core"
        assert data["version"] == "1.0"
        assert "test" in data["capabilities"]
        assert "keyword" in data["routing_keywords"]


class TestWiringRegistry:
    """Test suite for wiring registry singleton"""
    
    def test_singleton_instance(self):
        """Test that wiring registry is a singleton"""
        registry1 = get_wiring_registry()
        registry2 = get_wiring_registry()
        
        assert registry1 is registry2
    
    def test_registry_persistence(self):
        """Test that registry persists registrations"""
        registry = get_wiring_registry()
        mock_orch = Mock(spec=IOrchestrator)
        
        registry.register_orchestrator(
            domain="persistent_test",
            orchestrator=mock_orch,
            category=OrchestratorCategory.SUPPORT,
            capabilities=["test"]
        )
        
        # Verify it's still there
        metadata = registry.get_orchestrator("persistent_test")
        assert metadata is not None
        assert metadata.domain == "persistent_test"


class TestOrchestratorWiringMetadata:
    """Test suite for metadata classes"""
    
    def test_orchestrator_category_enum(self):
        """Test OrchestratorCategory enum"""
        assert OrchestratorCategory.CORE.value == "core"
        assert OrchestratorCategory.DOMAIN.value == "domain"
        assert OrchestratorCategory.SUPPORT.value == "support"
        assert OrchestratorCategory.INFRASTRUCTURE.value == "infrastructure"
    
    def test_wiring_metadata_defaults(self):
        """Test default values in OrchestratorWiringMetadata"""
        mock_orch = Mock(spec=IOrchestrator)
        metadata = OrchestratorWiringMetadata(
            domain="test",
            orchestrator=mock_orch,
            category=OrchestratorCategory.CORE
        )
        
        assert metadata.version == "1.0"
        assert metadata.health_status == "healthy"
        assert metadata.confidence_score == 100
        assert metadata.capabilities == []
        assert metadata.routing_keywords == []
        assert metadata.registered_at is not None


# WIRE-001 Tests: Core Orchestrators
class TestWire001CoreOrchestrators:
    """Tests for WIRE-001: Core orchestrator registration"""
    
    def test_core_orchestrator_metadata(self):
        """Test core orchestrator metadata structure"""
        registry = OrchestratorWiringRegistry()
        mock_orch = Mock(spec=IOrchestrator)
        
        # Register core orchestrator (simulates InteractionOrchestrator)
        result = registry.register_orchestrator(
            domain="interaction",
            orchestrator=mock_orch,
            category=OrchestratorCategory.CORE,
            capabilities=["comprehension", "session_management", "context_preservation"],
            routing_keywords=["understand", "analyze", "comprehend"],
            version="1.0"
        )
        
        assert result.is_ok()
        metadata = registry.get_orchestrator("interaction")
        assert metadata is not None
        assert metadata.category == OrchestratorCategory.CORE
        assert len(metadata.capabilities) == 3
        assert len(metadata.routing_keywords) == 3
    
    def test_multiple_core_orchestrators(self):
        """Test registering multiple core orchestrators"""
        registry = OrchestratorWiringRegistry()
        mock_orch = Mock(spec=IOrchestrator)
        
        core_orchestrators = [
            ("interaction", ["comprehension"]),
            ("intent_routing", ["routing", "classification"]),
            ("tdd", ["test_generation", "coverage"]),
            ("workflow", ["execution", "steps"]),
            ("wrapped_tdd", ["governance", "compliance"]),
        ]
        
        for domain, capabilities in core_orchestrators:
            result = registry.register_orchestrator(
                domain=domain,
                orchestrator=mock_orch,
                category=OrchestratorCategory.CORE,
                capabilities=capabilities
            )
            assert result.is_ok()
        
        # Verify all are registered
        core = registry.get_by_category(OrchestratorCategory.CORE)
        assert len(core) == 5


# WIRE-002 Tests: Domain Orchestrators
class TestWire002DomainOrchestrators:
    """Tests for WIRE-002: Domain orchestrator registration"""
    
    def test_domain_orchestrator_metadata(self):
        """Test domain orchestrator metadata structure"""
        registry = OrchestratorWiringRegistry()
        mock_orch = Mock(spec=IOrchestrator)
        
        result = registry.register_orchestrator(
            domain="refactoring",
            orchestrator=mock_orch,
            category=OrchestratorCategory.DOMAIN,
            capabilities=["code_refactoring", "pattern_detection"],
            routing_keywords=["refactor", "pattern"],
            version="1.0"
        )
        
        assert result.is_ok()
        metadata = registry.get_orchestrator("refactoring")
        assert metadata is not None
        assert metadata.category == OrchestratorCategory.DOMAIN


# WIRE-003 Tests: Support Orchestrators
class TestWire003SupportOrchestrators:
    """Tests for WIRE-003: Support orchestrator registration"""
    
    def test_support_orchestrator_metadata(self):
        """Test support orchestrator metadata structure"""
        registry = OrchestratorWiringRegistry()
        mock_orch = Mock(spec=IOrchestrator)
        
        result = registry.register_orchestrator(
            domain="onboarding",
            orchestrator=mock_orch,
            category=OrchestratorCategory.SUPPORT,
            capabilities=["user_onboarding", "setup"],
            routing_keywords=["onboard", "setup"],
            version="1.0"
        )
        
        assert result.is_ok()
        metadata = registry.get_orchestrator("onboarding")
        assert metadata is not None
        assert metadata.category == OrchestratorCategory.SUPPORT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
