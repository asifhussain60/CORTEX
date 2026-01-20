"""
Tests for Orchestrator Registry - Domain Query Interface

AC-AR-006-03: Orchestrator registry queryable by domain
- Query by domain (exact match)
- Pattern matching with wildcards
- Filter by capability and version
- Registry statistics and discovery
"""

import pytest
from typing import Any, Dict

from cortex.orchestrators.core.orchestrator_registry import (
    OrchestratorRegistry,
    RegistryQuery,
)
from cortex.core.decorators.orchestrator_decorator import (
    orchestrator,
    clear_orchestrator_registry,
)
from cortex.core.interfaces import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok


class MockOrchestrator(IOrchestrator):
    """Mock orchestrator for testing"""
    
    def __init__(self, domain: str):
        self.domain = domain
    
    def get_name(self) -> str:
        return f"{self.domain}_orchestrator"
    
    def get_version(self) -> str:
        return "1.0"
    
    def initialize(self) -> Result[str]:
        return Ok("Initialized")
    
    def get_mode(self) -> OperationMode:
        return OperationMode.PLANNING
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        return Ok({})
    
    def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
        return Ok({})
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        return Ok([])


class TestOrchestratorRegistrySingleton:
    """Test OrchestratorRegistry singleton pattern"""
    
    def setup_method(self):
        """Setup for each test"""
        OrchestratorRegistry.reset_instance()
        clear_orchestrator_registry()
    
    def test_singleton_instance(self):
        """Test singleton instance creation"""
        registry1 = OrchestratorRegistry.instance()
        registry2 = OrchestratorRegistry.instance()
        
        assert registry1 is registry2
    
    def test_reset_instance(self):
        """Test resetting singleton instance"""
        registry1 = OrchestratorRegistry.instance()
        OrchestratorRegistry.reset_instance()
        registry2 = OrchestratorRegistry.instance()
        
        assert registry1 is not registry2


class TestOrchestratorRegistryQueries:
    """Test orchestrator registry query operations"""
    
    def setup_method(self):
        """Setup for each test"""
        OrchestratorRegistry.reset_instance()
        clear_orchestrator_registry()
        
        # Register test orchestrators
        @orchestrator(domain="governance", version="2.0", capabilities=["validate", "enforce"])
        class GovernanceOrch(IOrchestrator):
            def get_name(self) -> str:
                return "GovernanceOrchestrator"
            
            def get_version(self) -> str:
                return "2.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
        
        @orchestrator(domain="audit", version="1.5", capabilities=["log", "report"])
        class AuditOrch(IOrchestrator):
            def get_name(self) -> str:
                return "AuditOrchestrator"
            
            def get_version(self) -> str:
                return "1.5"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
        
        @orchestrator(domain="evidence", version="1.0", capabilities=["collect", "validate"])
        class EvidenceOrch(IOrchestrator):
            def get_name(self) -> str:
                return "EvidenceOrchestrator"
            
            def get_version(self) -> str:
                return "1.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
        
        self.registry = OrchestratorRegistry.instance()
    
    def test_get_by_domain(self):
        """Test getting orchestrators by domain"""
        governance = self.registry.get_by_domain("governance")
        
        assert len(governance) == 1
        assert governance[0]["domain"] == "governance"
        assert governance[0]["version"] == "2.0"
    
    def test_get_by_domain_not_found(self):
        """Test getting orchestrators for non-existent domain"""
        result = self.registry.get_by_domain("nonexistent")
        
        assert len(result) == 0
    
    def test_get_all(self):
        """Test getting all orchestrators"""
        all_orchestrators = self.registry.get_all()
        
        assert len(all_orchestrators) == 3
    
    def test_query_without_filters(self):
        """Test query without filters returns all"""
        result = self.registry.query()
        
        assert result.total_count == 3
        assert result.matched_count == 3
        assert len(result.results) == 3
    
    def test_query_by_domain_pattern_exact(self):
        """Test query by exact domain pattern"""
        result = self.registry.query(domain_pattern="governance")
        
        assert result.matched_count == 1
        assert result.results[0]["domain"] == "governance"
    
    def test_query_by_domain_pattern_wildcard_prefix(self):
        """Test query by domain pattern with wildcard prefix"""
        result = self.registry.query(domain_pattern="*audit")
        
        assert result.matched_count == 1
        assert result.results[0]["domain"] == "audit"
    
    def test_query_by_domain_pattern_wildcard_suffix(self):
        """Test query by domain pattern with wildcard suffix"""
        result = self.registry.query(domain_pattern="gov*")
        
        assert result.matched_count == 1
        assert result.results[0]["domain"] == "governance"
    
    def test_query_by_domain_pattern_wildcard_both(self):
        """Test query by domain pattern with wildcards on both sides"""
        result = self.registry.query(domain_pattern="*vide*")
        
        assert result.matched_count == 1
        assert result.results[0]["domain"] == "evidence"
    
    def test_query_by_capability(self):
        """Test query by capability"""
        result = self.registry.query(capability="validate")
        
        # governance and evidence have validate
        assert result.matched_count == 2
        domains = {r["domain"] for r in result.results}
        assert domains == {"governance", "evidence"}
    
    def test_query_by_version(self):
        """Test query by version"""
        result = self.registry.query(version="1.0")
        
        assert result.matched_count == 1
        assert result.results[0]["domain"] == "evidence"
    
    def test_query_combined_filters(self):
        """Test query with combined filters"""
        result = self.registry.query(
            domain_pattern="*",
            capability="validate"
        )
        
        assert result.matched_count == 2
        domains = {r["domain"] for r in result.results}
        assert domains == {"governance", "evidence"}


class TestOrchestratorRegistryFinders:
    """Test finder methods"""
    
    def setup_method(self):
        """Setup for each test"""
        OrchestratorRegistry.reset_instance()
        clear_orchestrator_registry()
        
        @orchestrator(domain="governance", capabilities=["validate", "enforce"])
        class GovernanceOrch(IOrchestrator):
            def get_name(self) -> str:
                return "GovernanceOrchestrator"
            
            def get_version(self) -> str:
                return "2.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
        
        @orchestrator(domain="audit", version="1.5")
        class AuditOrch(IOrchestrator):
            def get_name(self) -> str:
                return "AuditOrchestrator"
            
            def get_version(self) -> str:
                return "1.5"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
        
        self.registry = OrchestratorRegistry.instance()
    
    def test_find_by_capability(self):
        """Test finding orchestrators by capability"""
        results = self.registry.find_by_capability("validate")
        
        assert len(results) == 1
        assert results[0]["domain"] == "governance"
    
    def test_find_by_capability_not_found(self):
        """Test finding orchestrators by non-existent capability"""
        results = self.registry.find_by_capability("nonexistent")
        
        assert len(results) == 0
    
    def test_find_by_version(self):
        """Test finding orchestrators by version"""
        results = self.registry.find_by_version("1.5")
        
        assert len(results) == 1
        assert results[0]["domain"] == "audit"


class TestOrchestratorRegistryInfo:
    """Test registry information methods"""
    
    def setup_method(self):
        """Setup for each test"""
        OrchestratorRegistry.reset_instance()
        clear_orchestrator_registry()
        
        @orchestrator(domain="governance", capabilities=["validate"])
        class GovernanceOrch(IOrchestrator):
            def get_name(self) -> str:
                return "GovernanceOrchestrator"
            
            def get_version(self) -> str:
                return "2.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
        
        @orchestrator(domain="audit", capabilities=["log"])
        class AuditOrch(IOrchestrator):
            def get_name(self) -> str:
                return "AuditOrchestrator"
            
            def get_version(self) -> str:
                return "1.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
        
        self.registry = OrchestratorRegistry.instance()
    
    def test_get_domains(self):
        """Test getting all domains"""
        domains = self.registry.get_domains()
        
        assert len(domains) == 2
        assert "governance" in domains
        assert "audit" in domains
    
    def test_get_capabilities(self):
        """Test getting capabilities by domain"""
        capabilities = self.registry.get_capabilities()
        
        assert "governance" in capabilities
        assert "validate" in capabilities["governance"]
        assert "audit" in capabilities
        assert "log" in capabilities["audit"]
    
    def test_get_stats(self):
        """Test getting registry statistics"""
        stats = self.registry.get_stats()
        
        assert stats["total_orchestrators"] == 2
        assert stats["total_domains"] == 2
        assert len(stats["domains"]) == 2
        assert stats["total_capabilities"] == 2
        assert "created_at" in stats
        assert "last_query_time" in stats
    
    def test_is_domain_registered(self):
        """Test checking if domain is registered"""
        assert self.registry.is_domain_registered("governance")
        assert not self.registry.is_domain_registered("nonexistent")
    
    def test_validate_domain(self):
        """Test domain validation"""
        assert self.registry.validate_domain("governance")
        assert not self.registry.validate_domain("nonexistent")
    
    def test_describe_registry(self):
        """Test registry description"""
        description = self.registry.describe_registry()
        
        assert "Orchestrator Registry" in description
        assert "Total Orchestrators: 2" in description
        assert "Total Domains: 2" in description


class TestRegistryQuery:
    """Test RegistryQuery dataclass"""
    
    def test_registry_query_creation(self):
        """Test creating RegistryQuery"""
        query = RegistryQuery(
            domain="test",
            pattern="test*",
            results=[{"domain": "test"}],
            total_count=5,
            matched_count=1,
            query_time="0.001s"
        )
        
        assert query.domain == "test"
        assert query.pattern == "test*"
        assert len(query.results) == 1
        assert query.total_count == 5
        assert query.matched_count == 1
        assert query.query_time == "0.001s"
    
    def test_registry_query_defaults(self):
        """Test RegistryQuery with defaults"""
        query = RegistryQuery()
        
        assert query.domain is None
        assert query.pattern is None
        assert query.results == []
        assert query.total_count == 0
        assert query.matched_count == 0


# =============================================================================
# Tests for AC-AR-012-02: @orchestrator Decorator (Tier-Based Registry)
# =============================================================================

@pytest.mark.ac("AR-012-02")
class TestOrchestratorDecoratorRegistration:
    """
    Test @orchestrator decorator for AC-AR-012-02
    
    Tests auto-registration, tier dependency declaration, context injection,
    and registry queries for the new tier/rule-based decorator.
    """
    
    def setup_method(self):
        """Clear and setup registry before each test"""
        # Import here to avoid import conflicts
        from cortex.core.decorators.orchestrator import get_registry
        registry = get_registry()
        registry.clear()
    
    def test_decorator_imports(self):
        """Test that decorator and registry can be imported"""
        from cortex.core.decorators.orchestrator import (
            orchestrator,
            OrchestratorRegistry,
            get_registry,
        )
        
        assert orchestrator is not None
        assert OrchestratorRegistry is not None
        assert get_registry is not None
    
    def test_tier_based_registry_singleton(self):
        """Test that tier-based registry is a singleton"""
        from cortex.core.decorators.orchestrator import get_registry
        
        reg1 = get_registry()
        reg2 = get_registry()
        
        assert reg1 is reg2
    
    def test_create_simple_decorated_orchestrator(self):
        """Test creating a simple decorated orchestrator"""
        from cortex.core.decorators.orchestrator import orchestrator
        from cortex.core.orchestrator_base import OrchestratorBase
        
        @orchestrator(
            orchestrator_id="test-orch-001",
            description="Test orchestrator"
        )
        class TestOrchestrator(OrchestratorBase):
            def execute(self):
                return {"status": "success"}
        
        assert TestOrchestrator._is_registered is True  # type: ignore
        assert TestOrchestrator._orchestrator_id == "test-orch-001"  # type: ignore
    
    def test_decorated_orchestrator_with_tier_dependencies(self):
        """Test decorated orchestrator with tier dependencies"""
        from cortex.core.decorators.orchestrator import orchestrator, get_registry
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(
            orchestrator_id="tier-test-001",
            tier_dependencies={0, 1},
            description="Tier test"
        )
        class TierTestOrchestrator(OrchestratorBase):
            def execute(self):
                return {"tiers": list(self.get_tier_access())}
        
        entry = reg.get("tier-test-001")
        assert entry is not None
        assert entry["tier_dependencies"] == {0, 1}
    
    def test_decorated_orchestrator_with_required_rules(self):
        """Test decorated orchestrator with required rules"""
        from cortex.core.decorators.orchestrator import orchestrator, get_registry
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(
            orchestrator_id="rules-test-001",
            required_rules=["RULE-A", "RULE-B"],
            description="Rules test"
        )
        class RulesTestOrchestrator(OrchestratorBase):
            def execute(self):
                return {"rules": self.get_required_rules()}
        
        entry = reg.get("rules-test-001")
        assert entry is not None
        assert entry["required_rules"] == ["RULE-A", "RULE-B"]
    
    def test_registry_query_by_tier_new_decorator(self):
        """Test querying registry by tier (new decorator)"""
        from cortex.core.decorators.orchestrator import orchestrator, get_registry
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(
            orchestrator_id="tier-query-1",
            tier_dependencies={0}
        )
        class TierOrch1(OrchestratorBase):
            def execute(self):
                return {}
        
        @orchestrator(
            orchestrator_id="tier-query-2",
            tier_dependencies={0, 1, 2}
        )
        class TierOrch2(OrchestratorBase):
            def execute(self):
                return {}
        
        # Get orchestrators accessing tier 0
        tier_0_orchs = reg.get_by_tier(0)
        tier_0_ids = [o["id"] for o in tier_0_orchs]
        
        assert "tier-query-1" in tier_0_ids
        assert "tier-query-2" in tier_0_ids
        
        # Get orchestrators accessing tier 2
        tier_2_orchs = reg.get_by_tier(2)
        tier_2_ids = [o["id"] for o in tier_2_orchs]
        
        assert "tier-query-1" not in tier_2_ids
        assert "tier-query-2" in tier_2_ids
    
    def test_instantiate_decorated_orchestrator(self):
        """Test instantiating a decorated orchestrator"""
        from cortex.core.decorators.orchestrator import (
            orchestrator,
            instantiate_orchestrator,
            get_registry,
        )
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(
            orchestrator_id="instantiate-test-001",
            tier_dependencies={0},
            description="Instantiation test"
        )
        class InstantiateTestOrch(OrchestratorBase):
            def execute(self):
                return {
                    "id": self.context.orchestrator_id,
                    "tiers": list(self.get_tier_access()),
                }
        
        # Instantiate the orchestrator
        orch = instantiate_orchestrator(
            "instantiate-test-001",
            parameters={"key": "value"}
        )
        
        assert orch is not None
        assert isinstance(orch, InstantiateTestOrch)
        assert orch.context.orchestrator_id == "instantiate-test-001"
        assert orch.context.parameters == {"key": "value"}
    
    def test_instantiated_orchestrator_execution(self):
        """Test executing an instantiated decorated orchestrator"""
        from cortex.core.decorators.orchestrator import (
            orchestrator,
            instantiate_orchestrator,
            get_registry,
        )
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(
            orchestrator_id="exec-test-001",
            tier_dependencies={1},
            required_rules=["RULE-X"]
        )
        class ExecTestOrch(OrchestratorBase):
            def execute(self):
                return {
                    "status": "executed",
                    "tier_accessible": self.can_access_tier(1),
                    "rules": self.get_required_rules(),
                }
        
        orch = instantiate_orchestrator("exec-test-001")
        result = orch.run()
        
        assert result.success is True
        assert result.output["status"] == "executed"
        assert result.output["tier_accessible"] is True
        assert "RULE-X" in result.output["rules"]
    
    def test_tier_access_control_enforcement(self):
        """Test that tier access control is enforced"""
        from cortex.core.decorators.orchestrator import (
            orchestrator,
            instantiate_orchestrator,
            get_registry,
        )
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(
            orchestrator_id="access-control-test",
            tier_dependencies={0, 1},
            description="Access control test"
        )
        class AccessControlOrch(OrchestratorBase):
            def execute(self):
                return {
                    "can_access_0": self.can_access_tier(0),
                    "can_access_1": self.can_access_tier(1),
                    "can_access_2": self.can_access_tier(2),
                    "can_access_3": self.can_access_tier(3),
                }
        
        orch = instantiate_orchestrator("access-control-test")
        result = orch.run()
        
        assert result.success is True
        assert result.output["can_access_0"] is True
        assert result.output["can_access_1"] is True
        assert result.output["can_access_2"] is False
        assert result.output["can_access_3"] is False
    
    def test_mcp_tools_metadata(self):
        """Test MCP tools metadata storage"""
        from cortex.core.decorators.orchestrator import orchestrator, get_registry
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(
            orchestrator_id="mcp-test-001",
            mcp_tools=["tool1", "tool2", "tool3"],
            description="MCP tools test"
        )
        class MCPTestOrch(OrchestratorBase):
            def execute(self):
                return {}
        
        entry = reg.get("mcp-test-001")
        assert entry is not None
        assert entry["mcp_tools"] == ["tool1", "tool2", "tool3"]
    
    def test_decorator_rejects_non_base_class(self):
        """Test that decorator rejects non-OrchestratorBase classes"""
        from cortex.core.decorators.orchestrator import orchestrator
        
        with pytest.raises(TypeError):
            @orchestrator(orchestrator_id="invalid-001")
            class InvalidClass:  # type: ignore
                pass
    
    def test_duplicate_orchestrator_id_raises_error(self):
        """Test that registering duplicate IDs raises error"""
        from cortex.core.decorators.orchestrator import orchestrator, get_registry
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(orchestrator_id="duplicate-test")
        class FirstOrch(OrchestratorBase):
            def execute(self):
                return {}
        
        with pytest.raises(ValueError, match="already registered"):
            @orchestrator(orchestrator_id="duplicate-test")
            class SecondOrch(OrchestratorBase):
                def execute(self):
                    return {}
    
    def test_registry_list_all(self):
        """Test listing all orchestrators"""
        from cortex.core.decorators.orchestrator import orchestrator, get_registry
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(orchestrator_id="list-test-1")
        class ListOrch1(OrchestratorBase):
            def execute(self):
                return {}
        
        @orchestrator(orchestrator_id="list-test-2")
        class ListOrch2(OrchestratorBase):
            def execute(self):
                return {}
        
        all_orchs = reg.list_all()
        
        assert len(all_orchs) == 2
        ids = [o["id"] for o in all_orchs]
        assert "list-test-1" in ids
        assert "list-test-2" in ids
    
    def test_registry_count(self):
        """Test registry count method"""
        from cortex.core.decorators.orchestrator import orchestrator, get_registry
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        assert reg.count() == 0
        
        @orchestrator(orchestrator_id="count-test-1")
        class CountOrch1(OrchestratorBase):
            def execute(self):
                return {}
        
        assert reg.count() == 1
        
        @orchestrator(orchestrator_id="count-test-2")
        class CountOrch2(OrchestratorBase):
            def execute(self):
                return {}
        
        assert reg.count() == 2
    
    def test_get_orchestrator_class_by_id(self):
        """Test getting orchestrator class by ID"""
        from cortex.core.decorators.orchestrator import (
            orchestrator,
            get_orchestrator_class,
            get_registry,
        )
        from cortex.core.orchestrator_base import OrchestratorBase
        
        reg = get_registry()
        reg.clear()
        
        @orchestrator(orchestrator_id="get-class-test")
        class GetClassTestOrch(OrchestratorBase):
            def execute(self):
                return {}
        
        cls = get_orchestrator_class("get-class-test")
        
        assert cls is GetClassTestOrch
    
    def test_get_nonexistent_orchestrator_class(self):
        """Test getting nonexistent orchestrator class returns None"""
        from cortex.core.decorators.orchestrator import get_orchestrator_class
        
        cls = get_orchestrator_class("nonexistent-id")
        
        assert cls is None
