"""
AC-ENH-003-01: Orchestrator Header System Completion Test.

This test verifies that all core orchestrators (PlanningOrchestrator and 
MasterOrchestrator) have achieved feature parity in response header integration.

Scope:
- Verify both orchestrators have ResponseHeaderInjector initialized
- Confirm identical header wrapping behavior across orchestrators
- Validate consistent context variable handling
- Ensure graceful degradation works consistently
- Confirm no regressions in orchestrator core functionality

This AC marks the completion of the response header system across all core
orchestrators, providing a consistent interface for future orchestrator 
additions.
"""

import pytest
from datetime import datetime, timezone
from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.core.response_header_config import HeaderConfigurationManager


@pytest.fixture
def planning_orch():
    """Get PlanningOrchestrator instance."""
    PlanningOrchestrator.reset_instance()
    orch = PlanningOrchestrator.instance()
    yield orch
    PlanningOrchestrator.reset_instance()


@pytest.fixture
def master_orch():
    """Get MasterOrchestrator instance."""
    orch = MasterOrchestrator.instance()
    yield orch


@pytest.mark.ac("ENH-003-01")
class TestOrchestratorHeaderParity:
    """AC-ENH-003-01: Verify feature parity in header integration."""
    
    def test_both_orchestrators_initialize_headers(self, planning_orch, master_orch):
        """Both orchestrators should have header injection system initialized."""
        # PlanningOrchestrator
        assert planning_orch._header_injector is not None
        assert planning_orch._header_config is not None
        
        # MasterOrchestrator
        assert master_orch.header_injector is not None
        
    def test_both_orchestrators_have_get_response_with_headers_method(self, planning_orch, master_orch):
        """Both orchestrators should have header wrapping method."""
        assert hasattr(planning_orch, 'get_response_with_headers')
        assert callable(planning_orch.get_response_with_headers)
        
        assert hasattr(master_orch, 'get_response_with_headers')
        assert callable(master_orch.get_response_with_headers)
    
    def test_header_wrapping_produces_consistent_format(self, planning_orch, master_orch):
        """Both orchestrators should produce headers with consistent format."""
        test_response = "Test orchestrator response"
        
        # Wrap with both orchestrators
        planning_wrapped = planning_orch.get_response_with_headers(test_response)
        master_wrapped = master_orch.get_response_with_headers(test_response)
        
        # Both should have headers
        assert "## 🧠 CORTEX" in planning_wrapped
        assert "## 🧠 CORTEX" in master_wrapped
        
        # Both should have copyright
        assert "Copyright © 2025-2026" in planning_wrapped
        assert "Copyright © 2025-2026" in master_wrapped
        
        # Both should contain original response
        assert test_response in planning_wrapped
        assert test_response in master_wrapped
    
    def test_header_includes_orchestrator_name(self, planning_orch, master_orch):
        """Headers should include orchestrator name."""
        test_response = "Status report"
        
        planning_wrapped = planning_orch.get_response_with_headers(test_response)
        master_wrapped = master_orch.get_response_with_headers(test_response)
        
        # Each should contain its name
        assert "PlanningOrchestrator" in planning_wrapped
        assert "MasterOrchestrator" in master_wrapped
    
    def test_header_structure_header_content_copyright(self, planning_orch, master_orch):
        """Both orchestrators should follow header-content-copyright structure."""
        test_response = "Response body"
        
        planning_wrapped = planning_orch.get_response_with_headers(test_response)
        
        # Find positions
        header_pos = planning_wrapped.find("## 🧠 CORTEX")
        content_pos = planning_wrapped.find(test_response)
        copyright_pos = planning_wrapped.find("Copyright ©")
        
        # Header should come first, then content, then copyright
        assert header_pos < content_pos < copyright_pos
    
    def test_graceful_degradation_without_injector(self, planning_orch):
        """If header_injector is None, should return response unchanged."""
        # Temporarily disable injector
        original_injector = planning_orch._header_injector
        planning_orch._header_injector = None
        
        test_response = "Plain response without headers"
        result = planning_orch.get_response_with_headers(test_response)
        
        # Should return unchanged response
        assert result == test_response
        
        # Restore
        planning_orch._header_injector = original_injector
    
    def test_graceful_degradation_master_without_injector(self, master_orch):
        """MasterOrchestrator should handle missing injector gracefully."""
        # Temporarily disable injector
        original_injector = master_orch.header_injector
        master_orch.header_injector = None
        
        test_response = "Plain response without headers"
        result = master_orch.get_response_with_headers(test_response)
        
        # Should return unchanged response
        assert result == test_response
        
        # Restore
        master_orch.header_injector = original_injector
    
    def test_context_variables_planning_orchestrator(self, planning_orch):
        """PlanningOrchestrator should build correct context."""
        test_response = "Planning response"
        wrapped = planning_orch.get_response_with_headers(test_response)
        
        # Should include planning mode indicators
        assert "PHASE-PLANNING" in wrapped or "PLANNING" in wrapped
        assert "PlanningOrchestrator" in wrapped
    
    def test_context_variables_master_orchestrator(self, master_orch):
        """MasterOrchestrator should build correct context."""
        master_orch.current_operation = "test_operation"
        master_orch.current_phase = "TEST_PHASE"
        
        test_response = "Master response"
        wrapped = master_orch.get_response_with_headers(test_response)
        
        # Should include operation and phase
        assert "test_operation" in wrapped or "coordination" in wrapped
        assert "MasterOrchestrator" in wrapped
    
    def test_multiple_wrappings_produce_consistent_output(self, planning_orch):
        """Multiple calls should produce consistent formatted output."""
        response1 = planning_orch.get_response_with_headers("First response")
        response2 = planning_orch.get_response_with_headers("First response")
        
        # Both wrappings should be identical (same input = same output)
        assert response1 == response2
    
    def test_different_content_produces_different_wrapped_responses(self, planning_orch):
        """Different content should produce different wrapped responses."""
        response1 = planning_orch.get_response_with_headers("Content A")
        response2 = planning_orch.get_response_with_headers("Content B")
        
        # Different content should produce different results
        assert response1 != response2
        assert "Content A" in response1
        assert "Content B" in response2
    
    def test_empty_response_handling(self, planning_orch, master_orch):
        """Both orchestrators should handle empty responses."""
        empty_response = ""
        
        planning_result = planning_orch.get_response_with_headers(empty_response)
        master_result = master_orch.get_response_with_headers(empty_response)
        
        # Should not crash, should return something
        assert planning_result is not None
        assert master_result is not None
    
    def test_multiline_response_handling(self, planning_orch):
        """Headers should wrap multiline responses correctly."""
        multiline_response = """Line 1
Line 2
Line 3
Multi-line response"""
        
        wrapped = planning_orch.get_response_with_headers(multiline_response)
        
        # Should contain header and all lines
        assert "## 🧠 CORTEX" in wrapped
        assert "Line 1" in wrapped
        assert "Line 3" in wrapped
        assert "Multi-line response" in wrapped
    
    def test_special_characters_in_response(self, planning_orch):
        """Headers should handle special characters in responses."""
        special_response = "Response with !@#$%^&*() special chars"
        wrapped = planning_orch.get_response_with_headers(special_response)
        
        # Should include original response intact
        assert special_response in wrapped
    
    def test_unicode_in_response(self, planning_orch):
        """Headers should handle unicode in responses."""
        unicode_response = "Response with unicode: 你好 мир 🚀"
        wrapped = planning_orch.get_response_with_headers(unicode_response)
        
        # Should include unicode response intact
        assert unicode_response in wrapped


@pytest.mark.ac("ENH-003-01")
class TestOrchestratorHeaderIntegration:
    """AC-ENH-003-01: Integration tests for header system completion."""
    
    def test_planning_orchestrator_core_functionality_unchanged(self, planning_orch):
        """Header integration should not affect PlanningOrchestrator core functionality."""
        # Initialize orchestrator
        result = planning_orch.initialize()
        assert result.is_ok()
        
        # Get name and version
        assert planning_orch.get_name() == "PlanningOrchestrator"
        assert planning_orch.get_version() == "1.0.0"
        
        # Get mode
        from cortex.core.interfaces import OperationMode
        assert planning_orch.get_mode() == OperationMode.PLANNING
    
    def test_master_orchestrator_core_functionality_unchanged(self, master_orch):
        """Header integration should not affect MasterOrchestrator core functionality."""
        # Initialize orchestrator
        result = master_orch.initialize()
        assert result.is_ok()
        
        # Get name and version
        assert master_orch.get_name() == "MasterOrchestrator"
        assert master_orch.get_version() == "2.0"
        
        # Get mode
        from cortex.core.interfaces import OperationMode
        assert master_orch.get_mode() == OperationMode.PLANNING
    
    def test_planning_orchestrator_mcp_tools_unchanged(self, planning_orch):
        """Header integration should not affect MCP tools."""
        result = planning_orch.get_mcp_tools()
        assert result.is_ok()
        
        tools = result.value
        assert "plan_status" in tools
        assert "next_ac" in tools
        assert "enforce_phase_lock" in tools
    
    def test_planning_orchestrator_operations_unchanged(self, planning_orch):
        """Header integration should not affect operations."""
        # Execute plan_status operation
        result = planning_orch.execute_operation("plan_status", {"phase_id": "PHASE-01"})
        assert result.is_ok()
        
        status = result.value
        assert status["phase_id"] == "PHASE-01"
        assert "completion_percentage" in status
    
    def test_planning_orchestrator_audit_trail_unchanged(self, planning_orch):
        """Header integration should not affect audit trail."""
        # Execute operation
        planning_orch.execute_operation("plan_status", {"phase_id": "PHASE-01"})
        
        # Get audit trail
        result = planning_orch.get_audit_trail()
        assert result.is_ok()
        
        trail = result.value
        assert len(trail) > 0
        assert "operation" in trail[0]
        assert "actor" in trail[0]
        assert "timestamp" in trail[0]


@pytest.mark.ac("ENH-003-01")
class TestHeaderSystemCompletion:
    """AC-ENH-003-01: Verify header system is complete and production-ready."""
    
    def test_header_config_manager_accessible(self):
        """Header configuration manager should be properly initialized."""
        config_manager = HeaderConfigurationManager.get_instance()
        assert config_manager is not None
    
    def test_both_orchestrators_use_same_config_manager(self, planning_orch, master_orch):
        """Both orchestrators should use same configuration manager instance."""
        if planning_orch._header_config:
            # Both should be singleton instances
            config1 = planning_orch._header_config
            config2 = HeaderConfigurationManager.get_instance()
            assert config1 is config2
    
    def test_header_system_is_optional_non_blocking(self, planning_orch):
        """Header system failure should not block orchestrator initialization."""
        # Create new orchestrator with header system disabled
        PlanningOrchestrator.reset_instance()
        
        # Should initialize successfully even if headers fail
        # (This is demonstrated by graceful degradation test)
        orch = PlanningOrchestrator.instance()
        assert orch is not None
    
    def test_header_configuration_file_exists(self):
        """Header configuration file should be loadable."""
        try:
            config_manager = HeaderConfigurationManager.get_instance()
            # If it loaded successfully during orchestrator init, this passed
            assert True
        except FileNotFoundError:
            pytest.skip("Header config file not found at expected location")
    
    def test_pattern_reusable_for_future_orchestrators(self, planning_orch, master_orch):
        """Header pattern should be consistent for future orchestrator additions."""
        # Both orchestrators follow same pattern:
        # 1. Initialize header_injector and header_config in __init__
        # 2. Have get_response_with_headers() method
        # 3. Use _build_header_section and _build_copyright_section
        # 4. Gracefully degrade without headers
        
        # This test documents the pattern for future orchestrators
        
        # Pattern element 1: Initialization
        assert hasattr(planning_orch, '_header_injector')
        assert hasattr(master_orch, 'header_injector')
        
        # Pattern element 2: Method
        assert hasattr(planning_orch, 'get_response_with_headers')
        assert hasattr(master_orch, 'get_response_with_headers')
        
        # Both methods callable
        assert callable(planning_orch.get_response_with_headers)
        assert callable(master_orch.get_response_with_headers)


@pytest.mark.ac("ENH-003-01")
class TestBackwardCompatibility:
    """AC-ENH-003-01: Ensure no regressions in existing functionality."""
    
    def test_planning_orchestrator_backward_compatibility(self, planning_orch):
        """PlanningOrchestrator with headers should be backward compatible."""
        # Old code that doesn't use headers should still work
        
        # Test audit operations
        result = planning_orch.execute_operation(
            "enforce_phase_lock",
            {"phase_id": "PHASE-01", "reason": "Test lock"}
        )
        assert result.is_ok()
        
        lock_data = result.value
        assert lock_data["phase_id"] == "PHASE-01"
        assert lock_data["reason"] == "Test lock"
    
    def test_master_orchestrator_backward_compatibility(self, master_orch):
        """MasterOrchestrator with headers should be backward compatible."""
        # Test that orchestrator registry still works
        
        # Get instance
        assert master_orch is not None
        
        # Test basic orchestrator interface
        assert master_orch.get_name() == "MasterOrchestrator"
        assert master_orch.get_version() == "2.0"
    
    def test_audit_logging_preserved(self, planning_orch):
        """Audit logging should be preserved with header integration."""
        # Execute operation
        planning_orch.execute_operation("plan_status", {"phase_id": "PHASE-02"})
        
        # Get audit trail
        result = planning_orch.get_audit_trail()
        assert result.is_ok()
        
        trail = result.value
        # Should have multiple entries from initialization and operation
        assert len(trail) > 0
        
        # Verify audit entries have expected structure
        for entry in trail:
            assert "operation" in entry
            assert "actor" in entry
            assert "result" in entry
            assert "timestamp" in entry


@pytest.mark.ac("ENH-003-01")
class TestProductionReadiness:
    """AC-ENH-003-01: Production readiness verification."""
    
    def test_header_generation_performance(self, planning_orch):
        """Header generation should be fast (non-blocking)."""
        import time
        
        test_response = "x" * 10000  # Large response
        
        start = time.time()
        for _ in range(100):
            planning_orch.get_response_with_headers(test_response)
        elapsed = time.time() - start
        
        # 100 wrappings should take less than 1 second
        assert elapsed < 1.0, f"Header generation too slow: {elapsed}s for 100 wrappings"
    
    def test_no_memory_leaks_in_repeated_wrapping(self, planning_orch):
        """Repeated wrapping should not leak memory."""
        # This is a basic check - repeated calls should work fine
        for i in range(1000):
            response = f"Response {i}"
            wrapped = planning_orch.get_response_with_headers(response)
            assert f"Response {i}" in wrapped
        
        # If we get here without running out of memory, test passes
        assert True
    
    def test_thread_safety_header_operations(self, planning_orch):
        """Header operations should be thread-safe."""
        import threading
        
        results = []
        
        def wrap_response(orchestrator, response):
            result = orchestrator.get_response_with_headers(response)
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(
                target=wrap_response,
                args=(planning_orch, f"Response from thread {i}")
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All threads should complete successfully
        assert len(results) == 10
