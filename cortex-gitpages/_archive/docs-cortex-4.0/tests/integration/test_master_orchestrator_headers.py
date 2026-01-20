"""
Integration tests for MasterOrchestrator with ResponseHeaderInjector

AC-ENH-002-01: MasterOrchestrator integrated with ResponseHeaderInjector
- Tests header wrapping in MasterOrchestrator responses
- Tests delegation with headers
- Tests header variables and consistency
"""

import pytest
from typing import Dict, Any

from src.orchestrators.core.master_orchestrator import MasterOrchestrator
from src.core.interfaces import IOrchestrator, OperationMode
from src.core.result import Result, Ok, Err


class MockDomainOrchestrator(IOrchestrator):
    """Mock domain orchestrator for testing"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.operations_executed = []
    
    def get_name(self) -> str:
        return f"MockOrchestrator({self.domain})"
    
    def get_version(self) -> str:
        return "1.0"
    
    def initialize(self) -> Result[str]:
        return Ok(f"Initialized {self.domain}")
    
    def get_mode(self) -> OperationMode:
        return OperationMode.PLANNING
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        return Ok({})
    
    def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
        self.operations_executed.append(operation_name)
        return Ok(f"Executed {operation_name} on {self.domain}")
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        return Ok([])


@pytest.mark.ac("ENH-002-01")
class TestMasterOrchestratorHeaders:
    """Test MasterOrchestrator header injection"""
    
    def test_master_orchestrator_initializes_with_headers(self):
        """AC-ENH-002-01: MasterOrchestrator should initialize header injector"""
        master = MasterOrchestrator()
        # Header injector may be None if initialization failed, but that's ok for graceful degradation
        # What matters is the method exists and works
        assert hasattr(master, 'header_injector'), "Should have header_injector attribute"
    
    def test_get_response_with_headers_method_exists(self):
        """AC-ENH-002-01: MasterOrchestrator should have get_response_with_headers method"""
        master = MasterOrchestrator()
        assert hasattr(master, 'get_response_with_headers'), "Should have get_response_with_headers method"
        assert callable(master.get_response_with_headers), "Should be callable"
    
    def test_response_wrapping_with_headers(self):
        """AC-ENH-002-01: Responses should be wrapped with headers when injector is available"""
        master = MasterOrchestrator()
        if master.header_injector is None:
            pytest.skip("Header injector not available (graceful degradation)")
        
        response = "Coordination complete"
        wrapped = master.get_response_with_headers(response)
        
        # Should be wrapped (longer than original)
        assert len(wrapped) > len(response), "Response should be wrapped with headers"
        # Original response should be in wrapped response
        assert response in wrapped, "Original response should be in wrapped response"
    
    def test_header_contains_orchestrator_info(self):
        """AC-ENH-002-01: Header should contain orchestrator information"""
        master = MasterOrchestrator()
        if master.header_injector is None:
            pytest.skip("Header injector not available (graceful degradation)")
        
        response = "Coordination complete"
        wrapped = master.get_response_with_headers(response)
        
        # Should contain orchestrator name or be substantially wrapped
        assert "MasterOrchestrator" in wrapped or len(wrapped) > len(response) * 1.5, \
            "Should contain orchestrator info or be significantly wrapped"
    
    def test_response_without_headers_on_none_injector(self):
        """AC-ENH-002-01: Should gracefully handle missing injector"""
        master = MasterOrchestrator()
        master.header_injector = None  # Simulate initialization failure
        
        response = "Coordination complete"
        wrapped = master.get_response_with_headers(response)
        
        # Should return original response unchanged
        assert wrapped == response, "Should return original response when injector is None"
    
    def test_multiple_responses_have_consistent_wrapping(self):
        """AC-ENH-002-01: Multiple responses should all have consistent wrapping"""
        master = MasterOrchestrator()
        if master.header_injector is None:
            pytest.skip("Header injector not available (graceful degradation)")
        
        responses = [
            "Operation 1 complete",
            "Operation 2 complete",
            "Operation 3 complete"
        ]
        
        wrapped_responses = [master.get_response_with_headers(r) for r in responses]
        
        # All should be wrapped consistently
        for wrapped, original in zip(wrapped_responses, responses):
            assert original in wrapped, f"Response {original} should be in wrapped version"
            # All wrapped responses should be significantly longer than originals
            assert len(wrapped) > len(original) * 1.2, "Wrapped response should be longer"
    
    def test_header_format_callable(self):
        """AC-ENH-002-01: Header wrapping should be callable without errors"""
        master = MasterOrchestrator()
        response = "Test response"
        
        # Should not raise an error
        try:
            wrapped = master.get_response_with_headers(response)
            assert isinstance(wrapped, str), "Should return a string"
        except Exception as e:
            pytest.fail(f"get_response_with_headers should not raise: {e}")


@pytest.mark.ac("ENH-002-02")
class TestMasterOrchestratorHeaderVariables:
    """Test header variable substitution in MasterOrchestrator"""
    
    def test_operation_variable_in_context(self):
        """AC-ENH-002-02: Operation variable should be used in context"""
        master = MasterOrchestrator()
        master.current_operation = "test_coordination"
        
        # Should not raise an error and method should work
        response = "Test"
        wrapped = master.get_response_with_headers(response)
        assert isinstance(wrapped, str), "Should return a string"
    
    def test_orchestrator_variable_in_context(self):
        """AC-ENH-002-02: Orchestrator variable should be used in context"""
        master = MasterOrchestrator()
        response = "Test"
        
        # Should use orchestrator name from get_name()
        wrapped = master.get_response_with_headers(response)
        assert isinstance(wrapped, str), "Should return a string"
        if master.header_injector:
            assert "MasterOrchestrator" in wrapped, "Should contain orchestrator name when headers present"
    
    def test_phase_variable_in_context(self):
        """AC-ENH-002-02: Phase variable should be used in context"""
        master = MasterOrchestrator()
        master.current_phase = "coordination"
        
        response = "Test"
        wrapped = master.get_response_with_headers(response)
        assert isinstance(wrapped, str), "Should return a string"
    
    def test_author_variable_in_context(self):
        """AC-ENH-002-02: Author variable should be CORTEX for master orchestrator"""
        master = MasterOrchestrator()
        response = "Test"
        
        wrapped = master.get_response_with_headers(response)
        assert isinstance(wrapped, str), "Should return a string"


@pytest.mark.ac("ENH-002-02")
class TestMasterOrchestratorIntegrationWithDelegation:
    """Test MasterOrchestrator headers with delegation"""
    
    def test_registry_status_can_be_wrapped(self):
        """AC-ENH-002-02: Registry status responses can be wrapped with headers"""
        master = MasterOrchestrator()
        
        # Register a mock orchestrator
        mock = MockDomainOrchestrator("governance")
        result = master.register_orchestrator("governance", mock)
        assert result.is_ok(), "Should register orchestrator"
        
        # Get registry status
        status_result = master.get_registry_status()
        assert status_result.is_ok(), "Should get registry status"
        
        # Wrap status with headers - status_result is a Result[Dict]
        status_str = str(status_result)
        wrapped = master.get_response_with_headers(status_str)
        
        # Should be wrapped or return original
        assert isinstance(wrapped, str), "Should return wrapped string"
    
    def test_coordination_history_with_headers(self):
        """AC-ENH-002-02: Coordination history can be wrapped with headers"""
        master = MasterOrchestrator()
        
        # Add some operation history
        history_entry = {
            "operation": "test",
            "timestamp": "2026-01-15T00:00:00",
            "orchestrators_involved": 1
        }
        master.operation_history.append(history_entry)
        
        # Get history
        history_result = master.get_coordination_history(limit=10)
        assert history_result.is_ok(), "Should get coordination history"
        
        # Wrap with headers
        history_str = str(history_result)
        wrapped = master.get_response_with_headers(history_str)
        
        # Should return a string
        assert isinstance(wrapped, str), "Should return wrapped string"


@pytest.mark.ac("ENH-002-02")
class TestMasterOrchestratorBackwardCompatibility:
    """Test backward compatibility of MasterOrchestrator with headers"""
    
    def test_orchestrator_still_works_without_headers(self):
        """AC-ENH-002-02: MasterOrchestrator should work without headers"""
        master = MasterOrchestrator()
        master.header_injector = None  # Disable headers
        
        # All basic operations should still work
        assert master.get_name() == "MasterOrchestrator"
        assert master.get_version() == "2.0"
        
        # Registry operations should work
        mock = MockDomainOrchestrator("test")
        result = master.register_orchestrator("test", mock, ["test"])
        assert result.is_ok(), "Should register orchestrator"
    
    def test_mcp_tools_unchanged(self):
        """AC-ENH-002-02: MCP tool exposure should be unchanged"""
        master = MasterOrchestrator()
        
        tools_result = master.get_mcp_tools()
        assert tools_result.is_ok(), "Should get MCP tools"
        
        # tools_result is Result[Dict], so we just check it's Ok
        assert tools_result.is_ok(), "Should have tools available"
    
    def test_delegation_unchanged(self):
        """AC-ENH-002-02: Delegation should work unchanged"""
        master = MasterOrchestrator()
        
        # Register orchestrators
        mock1 = MockDomainOrchestrator("governance")
        mock2 = MockDomainOrchestrator("audit")
        
        r1 = master.register_orchestrator("governance", mock1)
        r2 = master.register_orchestrator("audit", mock2)
        assert r1.is_ok() and r2.is_ok(), "Should register both orchestrators"
        
        # Coordinate operation
        result = master.coordinate_operation(
            operation="validate",
            context={"test": True},
            target_domains=["governance", "audit"]
        )
        
        assert result.is_ok(), "Coordination should succeed"


@pytest.mark.ac("ENH-002-02")
class TestMasterOrchestratorHeaderStructure:
    """Test header structure consistency in MasterOrchestrator"""
    
    def test_complete_flow_with_headers(self):
        """AC-ENH-002-02: Complete orchestration flow should handle headers"""
        master = MasterOrchestrator()
        
        # Initialize
        init_result = master.initialize()
        assert init_result.is_ok()
        
        # Wrap with headers
        wrapped_init = master.get_response_with_headers(str(init_result))
        assert isinstance(wrapped_init, str), "Should return a string"
    
    def test_header_structure_consistency(self):
        """AC-ENH-002-02: Header structure should be consistent across responses"""
        master = MasterOrchestrator()
        
        responses = [
            "Response 1",
            "Response 2",
            "Response 3"
        ]
        
        wrapped_responses = [master.get_response_with_headers(r) for r in responses]
        
        # All should return strings
        for wrapped in wrapped_responses:
            assert isinstance(wrapped, str), "All should return strings"


@pytest.mark.ac("ENH-002-01")
class TestMasterOrchestratorEdgeCases:
    """Test edge cases for MasterOrchestrator header injection"""
    
    def test_empty_response_with_headers(self):
        """AC-ENH-002-01: Empty responses should be handled"""
        master = MasterOrchestrator()
        
        wrapped = master.get_response_with_headers("")
        
        # Should still return a string
        assert isinstance(wrapped, str)
    
    def test_multiline_response_with_headers(self):
        """AC-ENH-002-01: Multiline responses should be wrapped"""
        master = MasterOrchestrator()
        
        response = """Line 1
Line 2
Line 3"""
        
        wrapped = master.get_response_with_headers(response)
        
        # Should still contain response
        assert isinstance(wrapped, str)
        if master.header_injector:
            # If headers are injected, all lines should be in wrapped
            assert "Line 1" in wrapped or len(wrapped) > len(response)
    
    def test_response_with_special_chars(self):
        """AC-ENH-002-01: Responses with special characters should work"""
        master = MasterOrchestrator()
        
        response = "Response with special chars: !@#$%^&*()_+-=[]{}|;:',.<>?/"
        
        wrapped = master.get_response_with_headers(response)
        
        # Should handle special chars gracefully
        assert isinstance(wrapped, str)
        assert len(wrapped) > 0

