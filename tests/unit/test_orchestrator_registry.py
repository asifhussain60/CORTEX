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

from src.orchestrators.core.orchestrator_registry import (
    OrchestratorRegistry,
    RegistryQuery,
)
from src.core.decorators.orchestrator_decorator import (
    orchestrator,
    clear_orchestrator_registry,
)
from src.core.interfaces import IOrchestrator, OperationMode
from src.core.result import Result, Ok


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
