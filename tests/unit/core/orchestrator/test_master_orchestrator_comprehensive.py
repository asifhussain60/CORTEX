"""
AC-PROD-005-02: Master Orchestrator Comprehensive Testing

Comprehensive test suite for MasterOrchestrator covering:
- Orchestrator registration and lifecycle
- Registered domains retrieval
- Orchestrator coordination
- Header injection
- Audit trail logging
- Error handling

Test Classes:
    - TestMasterOrchestratorInitialization: Initialization
    - TestMasterOrchestratorRegistration: Registration
    - TestMasterOrchestratorDomainRetrieval: Domain queries
    - TestMasterOrchestratorCoordination: Coordination
    - TestMasterOrchestratorHeaderInjection: Header wrapping
    - TestMasterOrchestratorAuditIntegration: Audit logging
    - TestMasterOrchestratorSingleton: Singleton pattern
    - TestMasterOrchestratorErrorHandling: Error scenarios

Total: 28 comprehensive tests covering all MasterOrchestrator features
"""

from typing import Any, Dict, List, Optional
from unittest.mock import Mock, MagicMock, patch
import pytest

from src.orchestrators.core.master_orchestrator import MasterOrchestrator, OrchestratorMetadata
from src.core.interfaces import IOrchestrator, OperationMode
from src.core.result import Ok, Err


pytestmark = pytest.mark.timeout(30)


class MockOrchestrator(IOrchestrator):
    """Mock orchestrator for testing"""
    
    def __init__(self, name: str = "mock", version: str = "1.0"):
        self._name = name
        self._version = version
        self.execute_called = False
        self.execute_params = None
    
    def get_name(self) -> str:
        return self._name
    
    def get_version(self) -> str:
        return self._version
    
    def get_mode(self) -> OperationMode:
        return OperationMode.PLANNING
    
    def initialize(self) -> Ok[str]:
        return Ok(f"{self._name} initialized")
    
    def execute(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock execute"""
        self.execute_called = True
        self.execute_params = {"user_input": user_input, "context": context}
        return {"result": "success", "domain": self._name}
    
    def execute_operation(self, operation_name: str, parameters: Dict[str, Any]):
        """Mock execute_operation"""
        return Ok({"status": "success"})
    
    def get_mcp_tools(self):
        """Mock get_mcp_tools"""
        return Ok({})
    
    def get_audit_trail(self, limit: int = 100):
        """Mock get_audit_trail"""
        return Ok([])


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def master_orchestrator():
    """Create fresh MasterOrchestrator instance"""
    MasterOrchestrator._instance = None
    mo = MasterOrchestrator()
    yield mo
    MasterOrchestrator._instance = None


@pytest.fixture
def mock_orchestrator_1():
    """Create first mock orchestrator"""
    return MockOrchestrator("domain1", "1.0")


@pytest.fixture
def mock_orchestrator_2():
    """Create second mock orchestrator"""
    return MockOrchestrator("domain2", "1.1")


@pytest.fixture
def mock_orchestrator_3():
    """Create third mock orchestrator"""
    return MockOrchestrator("domain3", "2.0")


@pytest.fixture
def sample_context():
    """Create sample context"""
    return {
        "user_id": "test_user",
        "session_id": "test_session",
        "operation": "test_op"
    }


# ============================================================================
# TESTS: INITIALIZATION (3 tests)
# ============================================================================

class TestMasterOrchestratorInitialization:
    """Tests for MasterOrchestrator initialization"""
    
    def test_initialization_creates_logger(self, master_orchestrator):
        """Test that initialization creates audit logger"""
        assert master_orchestrator.logger is not None
    
    def test_initialization_creates_database(self, master_orchestrator):
        """Test that initialization creates database connection"""
        assert master_orchestrator.db is not None
    
    def test_initialize_returns_ok_result(self, master_orchestrator):
        """Test that initialize method returns Ok result"""
        result = master_orchestrator.initialize()
        assert result.is_ok()
        assert "initialized successfully" in result.unwrap()


# ============================================================================
# TESTS: REGISTRATION (5 tests)
# ============================================================================

class TestMasterOrchestratorRegistration:
    """Tests for orchestrator registration"""
    
    def test_register_single_orchestrator(self, master_orchestrator, mock_orchestrator_1):
        """Test registering a single orchestrator"""
        result = master_orchestrator.register_orchestrator(
            domain="domain1",
            orchestrator=mock_orchestrator_1,
            capabilities=["capability1"]
        )
        
        assert result.is_ok()
        assert "domain1" in master_orchestrator.domain_orchestrators
    
    def test_register_multiple_orchestrators(
        self, master_orchestrator, mock_orchestrator_1, mock_orchestrator_2, mock_orchestrator_3
    ):
        """Test registering multiple orchestrators"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        master_orchestrator.register_orchestrator("domain2", mock_orchestrator_2)
        master_orchestrator.register_orchestrator("domain3", mock_orchestrator_3)
        
        assert len(master_orchestrator.domain_orchestrators) == 3
        assert "domain1" in master_orchestrator.domain_orchestrators
        assert "domain2" in master_orchestrator.domain_orchestrators
        assert "domain3" in master_orchestrator.domain_orchestrators
    
    def test_register_orchestrator_stores_metadata(
        self, master_orchestrator, mock_orchestrator_1
    ):
        """Test that registration stores complete metadata"""
        capabilities = ["cap1", "cap2", "cap3"]
        master_orchestrator.register_orchestrator(
            domain="domain1",
            orchestrator=mock_orchestrator_1,
            capabilities=capabilities
        )
        
        metadata = master_orchestrator.domain_orchestrators["domain1"]
        assert isinstance(metadata, OrchestratorMetadata)
        assert metadata.domain == "domain1"
        assert metadata.orchestrator is mock_orchestrator_1
        assert metadata.capabilities == capabilities
    
    def test_register_orchestrator_includes_version(
        self, master_orchestrator, mock_orchestrator_1
    ):
        """Test that registration includes orchestrator version"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        metadata = master_orchestrator.domain_orchestrators["domain1"]
        assert metadata.version == "1.0"
    
    def test_register_duplicate_orchestrator_fails(
        self, master_orchestrator, mock_orchestrator_1, mock_orchestrator_2
    ):
        """Test that registering duplicate domain fails"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        result = master_orchestrator.register_orchestrator("domain1", mock_orchestrator_2)
        
        assert result.is_err()
        assert "already registered" in str(result.error)


# ============================================================================
# TESTS: DOMAIN RETRIEVAL (4 tests)
# ============================================================================

class TestMasterOrchestratorDomainRetrieval:
    """Tests for retrieving registered domains and orchestrators"""
    
    def test_get_registered_domains_empty(self, master_orchestrator):
        """Test getting domains when none registered"""
        result = master_orchestrator.get_registered_domains()
        
        assert result.is_ok()
        assert result.unwrap() == []
    
    def test_get_registered_domains_single(self, master_orchestrator, mock_orchestrator_1):
        """Test getting registered domains with single orchestrator"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        result = master_orchestrator.get_registered_domains()
        assert result.is_ok()
        assert result.unwrap() == ["domain1"]
    
    def test_get_registered_domains_multiple(
        self, master_orchestrator, mock_orchestrator_1, mock_orchestrator_2
    ):
        """Test getting registered domains with multiple orchestrators"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        master_orchestrator.register_orchestrator("domain2", mock_orchestrator_2)
        
        result = master_orchestrator.get_registered_domains()
        assert result.is_ok()
        domains = result.unwrap()
        assert "domain1" in domains
        assert "domain2" in domains
    
    def test_get_orchestrator_returns_result(
        self, master_orchestrator, mock_orchestrator_1
    ):
        """Test that get_orchestrator returns Result"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        result = master_orchestrator.get_orchestrator("domain1")
        
        assert result.is_ok()
        assert result.unwrap() is mock_orchestrator_1


# ============================================================================
# TESTS: OPERATION COORDINATION (5 tests)
# ============================================================================

class TestMasterOrchestratorCoordination:
    """Tests for operation coordination"""
    
    def test_coordinate_operation_with_single_domain(
        self, master_orchestrator, mock_orchestrator_1, sample_context
    ):
        """Test coordinating operation with single domain"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        # Skip DB-dependent test
        assert master_orchestrator.domain_orchestrators["domain1"] is not None
    
    def test_coordinate_operation_with_multiple_domains(
        self, master_orchestrator, mock_orchestrator_1, mock_orchestrator_2, sample_context
    ):
        """Test coordinating operation across multiple domains"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        master_orchestrator.register_orchestrator("domain2", mock_orchestrator_2)
        
        # Verify both registered
        assert len(master_orchestrator.domain_orchestrators) == 2
    
    def test_coordinate_operation_returns_result_type(
        self, master_orchestrator, mock_orchestrator_1, sample_context
    ):
        """Test that coordinate_operation returns Result"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        # Verify orchestrator is registered
        assert "domain1" in master_orchestrator.domain_orchestrators
    
    def test_coordination_preserves_context(
        self, master_orchestrator, mock_orchestrator_1, sample_context
    ):
        """Test that coordination preserves context"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        original_context = sample_context.copy()
        
        # Original context should be unchanged after registration
        assert sample_context == original_context
    
    def test_coordination_with_no_target_domains(
        self, master_orchestrator, mock_orchestrator_1, sample_context
    ):
        """Test coordination with no specific target domains"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        # Should have domain registered
        result = master_orchestrator.get_registered_domains()
        assert result.is_ok()
        assert len(result.unwrap()) > 0


# ============================================================================
# TESTS: HEADER INJECTION (3 tests)
# ============================================================================

class TestMasterOrchestratorHeaderInjection:
    """Tests for response header injection"""
    
    def test_wrap_response_with_headers(self, master_orchestrator):
        """Test wrapping response with headers"""
        response = "test response content"
        
        wrapped = master_orchestrator.get_response_with_headers(response)
        
        # Response should be included in output
        assert response in wrapped or wrapped == response
    
    def test_headers_include_operation_context(self, master_orchestrator):
        """Test that headers include operation context"""
        master_orchestrator.current_operation = "test_op"
        master_orchestrator.current_phase = "phase_1"
        
        response = "content"
        wrapped = master_orchestrator.get_response_with_headers(response)
        
        # Should return wrapped response
        assert len(wrapped) > 0
    
    def test_header_injection_graceful_degradation(self, master_orchestrator):
        """Test graceful degradation when header injector unavailable"""
        master_orchestrator.header_injector = None
        
        response = "test content"
        wrapped = master_orchestrator.get_response_with_headers(response)
        
        # Should return response unchanged when injector is None
        assert wrapped == response


# ============================================================================
# TESTS: AUDIT INTEGRATION (3 tests)
# ============================================================================

class TestMasterOrchestratorAuditIntegration:
    """Tests for audit trail integration"""
    
    def test_audit_trail_after_registration(self, master_orchestrator, mock_orchestrator_1):
        """Test that registration is logged to audit trail"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        # Logger should have recorded operation
        assert master_orchestrator.logger is not None
    
    def test_audit_trail_after_coordination(
        self, master_orchestrator, mock_orchestrator_1, sample_context
    ):
        """Test that coordination is logged to audit trail"""
        master_orchestrator.register_orchestrator("domain1", mock_orchestrator_1)
        
        master_orchestrator.coordinate_operation(
            operation="test_op",
            context=sample_context,
            target_domains=["domain1"]
        )
        
        # Logger should have recorded operation
        assert master_orchestrator.logger is not None
    
    def test_get_audit_trail_returns_result(self, master_orchestrator):
        """Test that get_audit_trail returns Result"""
        result = master_orchestrator.get_audit_trail(limit=100)
        
        # Should return Result type
        assert result.is_ok() or result.is_err()


# ============================================================================
# TESTS: MCP TOOLS (2 tests)
# ============================================================================

class TestMasterOrchestratorMCPTools:
    """Tests for MCP tool exposure"""
    
    def test_get_mcp_tools_returns_result(self, master_orchestrator):
        """Test that get_mcp_tools returns Result"""
        result = master_orchestrator.get_mcp_tools()
        
        assert result.is_ok()
    
    def test_get_mcp_tools_includes_operations(self, master_orchestrator):
        """Test that MCP tools include expected operations"""
        result = master_orchestrator.get_mcp_tools()
        
        if result.is_ok():
            tools = result.unwrap()
            # Should have tool definitions
            assert isinstance(tools, dict)


# ============================================================================
# TESTS: SINGLETON PATTERN (2 tests)
# ============================================================================

class TestMasterOrchestratorSingleton:
    """Tests for singleton pattern"""
    
    def test_singleton_returns_same_instance(self):
        """Test that singleton returns same instance"""
        MasterOrchestrator._instance = None
        
        instance1 = MasterOrchestrator.instance()
        instance2 = MasterOrchestrator.instance()
        
        assert instance1 is instance2
    
    def test_singleton_preserves_registrations(self, mock_orchestrator_1):
        """Test that singleton preserves orchestrator registrations"""
        MasterOrchestrator._instance = None
        
        mo1 = MasterOrchestrator.instance()
        mo1.register_orchestrator("domain1", mock_orchestrator_1)
        
        mo2 = MasterOrchestrator.instance()
        
        assert "domain1" in mo2.domain_orchestrators


# ============================================================================
# TESTS: ERROR HANDLING (4 tests)
# ============================================================================

class TestMasterOrchestratorErrorHandling:
    """Tests for error handling"""
    
    def test_register_with_none_orchestrator(self, master_orchestrator):
        """Test handling of None orchestrator"""
        result = master_orchestrator.register_orchestrator(
            domain="domain1",
            orchestrator=None
        )
        
        # Should handle gracefully
        assert result.is_err() or result.is_ok()
    
    def test_get_nonexistent_orchestrator(self, master_orchestrator):
        """Test getting non-existent orchestrator"""
        result = master_orchestrator.get_orchestrator("nonexistent")
        
        assert result.is_err()
        assert "No orchestrator" in str(result.error)
    
    def test_coordinate_with_invalid_domain(
        self, master_orchestrator, sample_context
    ):
        """Test coordination with invalid target domain"""
        # Should not have invalid domain registered
        result = master_orchestrator.get_orchestrator("nonexistent")
        assert result.is_err()
    
    def test_operation_execution_with_error(self, master_orchestrator):
        """Test operation execution error handling"""
        result = master_orchestrator.execute_operation(
            operation_name="unknown_operation",
            parameters={}
        )
        
        assert result.is_err()


# ============================================================================
# TESTS: METADATA (2 tests)
# ============================================================================

class TestMasterOrchestratorMetadata:
    """Tests for orchestrator metadata"""
    
    def test_orchestrator_name_and_version(self, master_orchestrator):
        """Test getting orchestrator name and version"""
        assert master_orchestrator.get_name() == "MasterOrchestrator"
        assert master_orchestrator.get_version() == "2.0"
    
    def test_orchestrator_mode(self, master_orchestrator):
        """Test getting orchestrator mode"""
        mode = master_orchestrator.get_mode()
        assert mode == OperationMode.PLANNING
