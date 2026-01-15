"""
Integration tests for ResponseHeaderInjector in PlanningOrchestrator.

AC-ENH-001-01: Reference implementation verification
AC-ENH-001-02: Response header appearance verification
"""

import pytest
from src.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
from src.core.response_header_config import HeaderConfigurationManager


@pytest.fixture
def planning_orchestrator():
    """Create PlanningOrchestrator instance."""
    orch = PlanningOrchestrator()
    orch.reset_instance()
    orch = PlanningOrchestrator.instance()
    yield orch
    orch.reset_instance()


@pytest.fixture
def header_config():
    """Get header configuration manager."""
    return HeaderConfigurationManager.get_instance()


class TestPlanningOrchestratorHeaders:
    """AC-ENH-001-01: Reference orchestrator header integration."""
    
    def test_orchestrator_initializes_with_headers(self, planning_orchestrator):
        """Verify orchestrator initializes header system."""
        # AC-ENH-001-01: PlanningOrchestrator integrated with headers
        assert planning_orchestrator._header_config is not None
        assert planning_orchestrator.get_name() == "PlanningOrchestrator"
    
    def test_orchestrator_has_get_response_with_headers_method(self, planning_orchestrator):
        """Verify method exists for header-wrapped responses."""
        assert hasattr(planning_orchestrator, 'get_response_with_headers')
        assert callable(planning_orchestrator.get_response_with_headers)
    
    def test_response_wrapping_with_headers(self, planning_orchestrator):
        """AC-ENH-001-02: Verify headers wrap responses correctly."""
        response = "Phase planning status retrieved successfully"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Should contain header
        assert "## 🧠 CORTEX" in wrapped
        assert "GetPlanStatus" in wrapped
        
        # Should contain original response
        assert response in wrapped
        
        # Should contain copyright
        assert "Copyright ©" in wrapped
        assert "Asif Hussain" in wrapped
    
    def test_header_contains_author_info(self, planning_orchestrator):
        """AC-ENH-001-02: Verify header includes author information."""
        response = "Test response"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Should contain author (with bold formatting)
        assert "**Author:** Asif Hussain" in wrapped
        
        # Should contain orchestrator name
        assert "PlanningOrchestrator" in wrapped
        
        # Should contain phase
        assert "PHASE-PLANNING" in wrapped
    
    def test_header_footer_structure(self, planning_orchestrator):
        """AC-ENH-001-02: Verify header and footer structure."""
        response = "Status: OK"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        lines = wrapped.split('\n')
        
        # First line should be header start
        assert "## 🧠 CORTEX" in lines[0]
        
        # Should have proper spacing (blank line between sections)
        assert "" in lines
        
        # Last non-empty line should be copyright
        non_empty_lines = [l for l in lines if l.strip()]
        assert "Copyright ©" in non_empty_lines[-1]
    
    def test_header_variable_substitution(self, planning_orchestrator):
        """AC-ENH-001-02: Verify variable substitution in headers."""
        response = "Response content"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # No braces should remain (all variables substituted)
        assert "{" not in wrapped
        assert "}" not in wrapped
        
        # Author should be substituted
        assert "Asif Hussain" in wrapped
    
    def test_response_without_headers_on_error(self, planning_orchestrator):
        """Verify graceful fallback if header system fails."""
        # Simulate header system failure by disabling config
        planning_orchestrator._header_config = None
        
        response = "Test response"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Should return original response
        assert wrapped == response
    
    def test_multiple_responses_have_headers(self, planning_orchestrator):
        """Verify multiple responses all get headers."""
        responses = [
            "Response 1",
            "Response 2",
            "Response 3",
        ]
        
        for resp in responses:
            wrapped = planning_orchestrator.get_response_with_headers(resp)
            
            # Each should have headers
            assert "## 🧠 CORTEX" in wrapped
            assert "Copyright ©" in wrapped
    
    def test_header_format_matches_spec(self, planning_orchestrator, header_config):
        """Verify header format matches specification."""
        response = "Test"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Should match: ## 🧠 CORTEX {operation}\n**Author:** ...
        assert "## 🧠 CORTEX" in wrapped
        assert "**Author:**" in wrapped
        assert "**" in wrapped  # Bold formatting
        assert "✅" in wrapped  # Checkmark emoji


class TestPlanningOrchestratorHeadersEdgeCases:
    """Edge cases for header integration."""
    
    def test_empty_response_with_headers(self, planning_orchestrator):
        """Verify empty response still gets headers."""
        wrapped = planning_orchestrator.get_response_with_headers("")
        
        assert "## 🧠 CORTEX" in wrapped
        assert "Copyright ©" in wrapped
    
    def test_multiline_response_with_headers(self, planning_orchestrator):
        """Verify multiline response formatted correctly."""
        response = "Line 1\nLine 2\nLine 3"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Original lines should be preserved
        assert "Line 1" in wrapped
        assert "Line 2" in wrapped
        assert "Line 3" in wrapped
        
        # Should have headers and footer
        assert "## 🧠 CORTEX" in wrapped
        assert "Copyright ©" in wrapped
    
    def test_response_with_special_chars(self, planning_orchestrator):
        """Verify response with special characters handled."""
        response = "Status: OK | Details: {key: value} & info"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Special chars should be preserved
        assert "OK" in wrapped
        assert "&" in wrapped
        assert "key: value" in wrapped


class TestPlanningOrchestratorIntegration:
    """Integration tests with other orchestrator methods."""
    
    def test_plan_status_could_be_wrapped(self, planning_orchestrator):
        """Verify plan_status response could be wrapped."""
        result = planning_orchestrator.plan_status("PHASE-01")
        
        assert result.is_ok()
        status_dict = result.value
        
        # Status could be serialized and wrapped
        status_str = str(status_dict)
        wrapped = planning_orchestrator.get_response_with_headers(status_str)
        
        # Should have headers
        assert "## 🧠 CORTEX" in wrapped
    
    def test_next_ac_could_be_wrapped(self, planning_orchestrator):
        """Verify next_ac response could be wrapped."""
        result = planning_orchestrator.next_ac("PHASE-01")
        
        assert result.is_ok()
        ac_dict = result.value
        
        # AC data could be serialized and wrapped
        ac_str = str(ac_dict)
        wrapped = planning_orchestrator.get_response_with_headers(ac_str)
        
        # Should have headers
        assert "## 🧠 CORTEX" in wrapped
    
    def test_audit_trail_integrity_with_headers(self, planning_orchestrator):
        """Verify audit trail unaffected by header system."""
        # Generate some operations
        planning_orchestrator.plan_status("PHASE-01")
        planning_orchestrator.next_ac("PHASE-01")
        
        # Get audit trail
        result = planning_orchestrator.get_audit_trail()
        assert result.is_ok()
        
        trail = result.value
        assert len(trail) > 0
        
        # Audit entries should be unchanged
        for entry in trail:
            assert "audit_id" in entry
            assert "current_hash" in entry


class TestBackwardCompatibility:
    """AC-ENH-001-04: Verify no regressions."""
    
    def test_orchestrator_still_works_without_headers(self):
        """Verify orchestrator functions if header system unavailable."""
        orch = PlanningOrchestrator()
        orch.reset_instance()
        orch = PlanningOrchestrator.instance()
        
        # Disable header system
        orch._header_config = None
        
        # All methods should still work
        assert orch.initialize().is_ok()
        assert orch.plan_status("PHASE-01").is_ok()
        assert orch.next_ac("PHASE-01").is_ok()
        assert orch.get_audit_trail().is_ok()
    
    def test_audit_logging_unchanged(self):
        """Verify audit logging unaffected by headers."""
        orch = PlanningOrchestrator()
        orch.reset_instance()
        orch = PlanningOrchestrator.instance()
        
        # Perform operations
        orch.plan_status("PHASE-01")
        orch.next_ac("PHASE-02")
        
        # Get audit trail
        result = orch.get_audit_trail()
        assert result.is_ok()
        
        trail = result.value
        assert len(trail) > 0
        
        # All standard fields should be present
        for entry in trail:
            assert entry["audit_id"]
            assert entry["timestamp"]
            assert entry["operation"]
            assert entry["current_hash"]
    
    def test_mcp_tools_unchanged(self):
        """Verify MCP tools exposed unchanged."""
        orch = PlanningOrchestrator()
        orch.reset_instance()
        orch = PlanningOrchestrator.instance()
        
        result = orch.get_mcp_tools()
        assert result.is_ok()
        
        tools = result.value
        assert "plan_status" in tools
        assert "next_ac" in tools
        assert "enforce_phase_lock" in tools


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
