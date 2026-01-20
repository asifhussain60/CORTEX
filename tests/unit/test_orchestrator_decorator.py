"""
Tests for Orchestrator Decorator - Auto-registration

AC-AR-006-02: Orchestrators auto-registered via @orchestrator decorator
- Decorator marks classes as orchestrators
- Auto-registration in global registry
- Metadata tracking (domain, version, capabilities)
- Registry queries and discovery
"""

import pytest
from typing import Any, Dict

from cortex.core.decorators.orchestrator_decorator import (
    orchestrator,
    get_registered_orchestrators,
    get_orchestrator_by_domain,
    get_orchestrators_by_domain,
    is_orchestrator,
    clear_orchestrator_registry,
)
from cortex.core.interfaces import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok, Err


class TestOrchestratorDecoratorBasics:
    """Test basic orchestrator decorator functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        clear_orchestrator_registry()
    
    def test_decorator_marks_class_as_orchestrator(self):
        """Test that decorator marks class as orchestrator"""
        @orchestrator(domain="test_domain")
        class TestOrch:
            pass
        
        assert is_orchestrator(TestOrch)
        assert hasattr(TestOrch, "_orchestrator_registered")
        assert TestOrch._orchestrator_registered == True
    
    def test_decorator_stores_metadata(self):
        """Test that decorator stores orchestrator metadata"""
        @orchestrator(
            domain="governance",
            version="2.0",
            capabilities=["validate", "enforce"]
        )
        class GovernanceOrch:
            pass
        
        assert hasattr(GovernanceOrch, "_orchestrator_metadata")
        metadata = GovernanceOrch._orchestrator_metadata
        assert metadata["domain"] == "governance"
        assert metadata["version"] == "2.0"
        assert metadata["capabilities"] == ["validate", "enforce"]
    
    def test_decorator_with_default_version(self):
        """Test that decorator uses default version if not specified"""
        @orchestrator(domain="test")
        class TestOrch:
            pass
        
        metadata = TestOrch._orchestrator_metadata
        assert metadata["version"] == "1.0"
    
    def test_decorator_with_description(self):
        """Test that decorator stores description"""
        @orchestrator(
            domain="test",
            description="Test orchestrator"
        )
        class TestOrch:
            pass
        
        metadata = TestOrch._orchestrator_metadata
        assert metadata["description"] == "Test orchestrator"
    
    def test_decorator_auto_generates_description(self):
        """Test that decorator auto-generates description if not provided"""
        @orchestrator(domain="test")
        class TestOrch:
            pass
        
        metadata = TestOrch._orchestrator_metadata
        assert "TestOrch" in metadata["description"]
        assert "orchestrator" in metadata["description"].lower()


class TestOrchestratorRegistry:
    """Test orchestrator registry operations"""
    
    def setup_method(self):
        """Setup for each test"""
        clear_orchestrator_registry()
    
    def test_get_registered_orchestrators(self):
        """Test getting all registered orchestrators"""
        @orchestrator(domain="governance")
        class GovernanceOrch:
            pass
        
        @orchestrator(domain="audit")
        class AuditOrch:
            pass
        
        orchestrators = get_registered_orchestrators()
        assert len(orchestrators) == 2
    
    def test_get_orchestrator_by_domain_found(self):
        """Test getting orchestrator by domain when it exists"""
        @orchestrator(domain="governance")
        class GovernanceOrch:
            pass
        
        metadata = get_orchestrator_by_domain("governance")
        assert metadata is not None
        assert metadata["domain"] == "governance"
    
    def test_get_orchestrator_by_domain_not_found(self):
        """Test getting orchestrator by domain when it doesn't exist"""
        @orchestrator(domain="governance")
        class GovernanceOrch:
            pass
        
        metadata = get_orchestrator_by_domain("nonexistent")
        assert metadata is None
    
    def test_get_orchestrators_by_domain_multiple(self):
        """Test getting multiple orchestrators in same domain"""
        @orchestrator(domain="governance", version="1.0")
        class GovernanceOrch1:
            pass
        
        @orchestrator(domain="governance", version="2.0")
        class GovernanceOrch2:
            pass
        
        @orchestrator(domain="audit")
        class AuditOrch:
            pass
        
        governance_orchs = get_orchestrators_by_domain("governance")
        assert len(governance_orchs) == 2
        
        audit_orchs = get_orchestrators_by_domain("audit")
        assert len(audit_orchs) == 1
    
    def test_get_orchestrators_by_domain_empty(self):
        """Test getting orchestrators for non-existent domain"""
        @orchestrator(domain="governance")
        class GovernanceOrch:
            pass
        
        orchestrators = get_orchestrators_by_domain("nonexistent")
        assert len(orchestrators) == 0


class TestOrchestratorDecoratorWithIOrchestrator:
    """Test orchestrator decorator with IOrchestrator implementations"""
    
    def setup_method(self):
        """Setup for each test"""
        clear_orchestrator_registry()
    
    def test_decorator_on_iorchestrator_implementation(self):
        """Test decorator on IOrchestrator implementation"""
        @orchestrator(domain="governance")
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
        
        assert is_orchestrator(GovernanceOrch)
        metadata = GovernanceOrch._orchestrator_metadata
        assert metadata["domain"] == "governance"
        
        # Can still instantiate
        instance = GovernanceOrch()
        assert instance.get_name() == "GovernanceOrchestrator"
    
    def test_multiple_orchestrators_different_domains(self):
        """Test multiple orchestrators with different domains"""
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
        
        @orchestrator(domain="audit", capabilities=["log", "report"])
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
        
        governance = get_orchestrator_by_domain("governance")
        audit = get_orchestrator_by_domain("audit")
        
        assert governance is not None
        assert governance["capabilities"] == ["validate"]
        assert audit is not None
        assert audit["capabilities"] == ["log", "report"]


class TestOrchestratorMetadata:
    """Test orchestrator metadata tracking"""
    
    def setup_method(self):
        """Setup for each test"""
        clear_orchestrator_registry()
    
    def test_metadata_includes_class_name(self):
        """Test that metadata includes class name"""
        @orchestrator(domain="test")
        class TestOrchestrator:
            pass
        
        metadata = TestOrchestrator._orchestrator_metadata
        assert metadata["class_name"] == "TestOrchestrator"
    
    def test_metadata_includes_registered_at(self):
        """Test that metadata includes registration timestamp"""
        @orchestrator(domain="test")
        class TestOrch:
            pass
        
        metadata = TestOrch._orchestrator_metadata
        assert "registered_at" in metadata
        assert isinstance(metadata["registered_at"], str)
    
    def test_metadata_includes_class_reference(self):
        """Test that metadata includes class reference"""
        @orchestrator(domain="test")
        class TestOrch:
            pass
        
        metadata = TestOrch._orchestrator_metadata
        assert metadata["class"] is TestOrch
    
    def test_orchestrator_domain_attribute(self):
        """Test that domain is stored as class attribute"""
        @orchestrator(domain="governance")
        class GovernanceOrch:
            pass
        
        assert GovernanceOrch._orchestrator_domain == "governance"


class TestClearRegistry:
    """Test registry clearing functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        clear_orchestrator_registry()
    
    def test_clear_orchestrator_registry(self):
        """Test clearing the orchestrator registry"""
        @orchestrator(domain="test1")
        class TestOrch1:
            pass
        
        @orchestrator(domain="test2")
        class TestOrch2:
            pass
        
        # Should have 2 orchestrators
        assert len(get_registered_orchestrators()) == 2
        
        # Clear registry
        clear_orchestrator_registry()
        
        # Should be empty
        assert len(get_registered_orchestrators()) == 0
        
        # Should be able to register again
        @orchestrator(domain="test3")
        class TestOrch3:
            pass
        
        assert len(get_registered_orchestrators()) == 1


class TestOrchestratorIntegration:
    """Integration tests for orchestrator decorator"""
    
    def setup_method(self):
        """Setup for each test"""
        clear_orchestrator_registry()
    
    def test_complete_orchestrator_registration_workflow(self):
        """Test complete orchestrator registration workflow"""
        # Define multiple orchestrators
        @orchestrator(
            domain="governance",
            version="2.0",
            capabilities=["validate", "enforce"]
        )
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
        
        @orchestrator(
            domain="audit",
            version="1.5",
            capabilities=["log", "report"]
        )
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
        
        # Verify registration
        all_orchs = get_registered_orchestrators()
        assert len(all_orchs) == 2
        
        # Query by domain
        governance = get_orchestrator_by_domain("governance")
        assert governance is not None
        assert governance["version"] == "2.0"
        assert set(governance["capabilities"]) == {"validate", "enforce"}
        
        audit = get_orchestrator_by_domain("audit")
        assert audit is not None
        assert audit["version"] == "1.5"
        assert set(audit["capabilities"]) == {"log", "report"}
        
        # Verify instances can be created
        gov_instance = GovernanceOrch()
        audit_instance = AuditOrch()
        
        assert gov_instance.get_name() == "GovernanceOrchestrator"
        assert audit_instance.get_name() == "AuditOrchestrator"
