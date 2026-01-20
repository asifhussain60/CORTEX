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


@pytest.mark.ac("ENH-001-01")
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


@pytest.mark.ac("ENH-001-04")
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


@pytest.mark.ac("ENH-001-02")
class TestOperationResponsesWithHeaders:
    """AC-ENH-001-02: Verify headers appear in orchestrator operation responses."""
    
    def test_plan_status_response_with_headers(self, planning_orchestrator):
        """AC-ENH-001-02: Headers should wrap plan_status operation response."""
        response_text = "Status retrieved successfully"
        wrapped = planning_orchestrator.get_response_with_headers(response_text)
        
        # Header should be present
        assert "## 🧠 CORTEX" in wrapped
        assert "GetPlanStatus" in wrapped
        
        # Original response should be present
        assert response_text in wrapped
        
        # Copyright should be present
        assert "Copyright ©" in wrapped
    
    def test_plan_status_operation_output(self, planning_orchestrator):
        """AC-ENH-001-02: plan_status operation should include headers."""
        # Execute operation
        result = planning_orchestrator.plan_status("PHASE-02")
        assert result.is_ok()
        
        # Get status dict
        status = result.value
        assert status["phase_id"] == "PHASE-02"
        assert status["mode"] == "PLANNING"
        
        # Convert to response and wrap with headers
        response_text = f"Phase: {status['phase_id']}, Progress: {status['completion_percentage']:.1f}%"
        wrapped = planning_orchestrator.get_response_with_headers(response_text)
        
        # Verify headers present
        assert "## 🧠 CORTEX" in wrapped
        assert response_text in wrapped
        assert "Copyright ©" in wrapped
    
    def test_next_ac_response_with_headers(self, planning_orchestrator):
        """AC-ENH-001-02: Headers should wrap next_ac operation response."""
        response_text = "Next AC: AC-AR-011-01"
        wrapped = planning_orchestrator.get_response_with_headers(response_text)
        
        # Header should be present
        assert "## 🧠 CORTEX" in wrapped
        
        # Original response should be present
        assert response_text in wrapped
        
        # Copyright should be present
        assert "Copyright ©" in wrapped
    
    def test_next_ac_operation_output(self, planning_orchestrator):
        """AC-ENH-001-02: next_ac operation should include headers."""
        # Execute operation
        result = planning_orchestrator.next_ac("PHASE-02")
        assert result.is_ok()
        
        # Get AC data
        ac_data = result.value
        assert ac_data["ac_id"] == "AC-AR-011-01"
        assert ac_data["phase_id"] == "PHASE-02"
        
        # Convert to response and wrap with headers
        response_text = f"Next: {ac_data['ac_id']} ({ac_data['title']})"
        wrapped = planning_orchestrator.get_response_with_headers(response_text)
        
        # Verify headers present
        assert "## 🧠 CORTEX" in wrapped
        assert ac_data['ac_id'] in wrapped
        assert "Copyright ©" in wrapped
    
    def test_enforce_phase_lock_response_with_headers(self, planning_orchestrator):
        """AC-ENH-001-02: Headers should wrap enforce_phase_lock operation response."""
        response_text = "Phase lock enforced successfully"
        wrapped = planning_orchestrator.get_response_with_headers(response_text)
        
        # Header should be present
        assert "## 🧠 CORTEX" in wrapped
        
        # Original response should be present
        assert response_text in wrapped
        
        # Copyright should be present
        assert "Copyright ©" in wrapped
    
    def test_enforce_phase_lock_operation_output(self, planning_orchestrator):
        """AC-ENH-001-02: enforce_phase_lock operation should include headers."""
        # Execute operation
        result = planning_orchestrator.enforce_phase_lock("PHASE-02", "Testing")
        assert result.is_ok()
        
        # Get lock data
        lock_data = result.value
        assert lock_data["phase_id"] == "PHASE-02"
        assert lock_data["reason"] == "Testing"
        
        # Convert to response and wrap with headers
        response_text = f"Locked: {lock_data['phase_id']} ({lock_data['reason']})"
        wrapped = planning_orchestrator.get_response_with_headers(response_text)
        
        # Verify headers present
        assert "## 🧠 CORTEX" in wrapped
        assert "PHASE-02" in wrapped
        assert "Copyright ©" in wrapped


@pytest.mark.ac("ENH-001-02")
class TestHeaderVariableSubstitution:
    """AC-ENH-001-02: Verify header variables are correctly substituted."""
    
    def test_operation_variable_substitution(self, planning_orchestrator):
        """AC-ENH-001-02: Operation variable should be substituted in header."""
        response = "test"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # "GetPlanStatus" should appear (the operation variable)
        assert "GetPlanStatus" in wrapped
        
        # No braces should remain
        assert "{operation}" not in wrapped
    
    def test_orchestrator_variable_substitution(self, planning_orchestrator):
        """AC-ENH-001-02: Orchestrator name should be substituted in header."""
        response = "test"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Orchestrator name should appear
        assert "PlanningOrchestrator" in wrapped
        
        # No braces should remain
        assert "{orchestrator}" not in wrapped
    
    def test_phase_variable_substitution(self, planning_orchestrator):
        """AC-ENH-001-02: Phase variable should be substituted in header."""
        response = "test"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Phase should appear
        assert "PHASE-PLANNING" in wrapped
        
        # No braces should remain
        assert "{phase}" not in wrapped
    
    def test_author_variable_substitution(self, planning_orchestrator):
        """AC-ENH-001-02: Author should be substituted in header."""
        response = "test"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Author should appear
        assert "Asif Hussain" in wrapped
        
        # No braces should remain
        assert "{author}" not in wrapped
    
    def test_copyright_variable_substitution(self, planning_orchestrator):
        """AC-ENH-001-02: Copyright notice should be substituted."""
        response = "test"
        wrapped = planning_orchestrator.get_response_with_headers(response)
        
        # Copyright notice should appear
        assert "2025-2026" in wrapped
        assert "Asif Hussain" in wrapped
        
        # No braces should remain in copyright
        assert "{notice}" not in wrapped


@pytest.mark.ac("ENH-001-02")
class TestCustomTemplateIndependence:
    """AC-ENH-001-02: Verify custom templates work independently of headers."""
    
    def test_template_renders_unchanged_with_headers(self, planning_orchestrator):
        """AC-ENH-001-02: Template rendering should be unchanged by header wrapping."""
        # Simulate template output
        template_output = """**Operation Status Report**
        
        Status: COMPLETED
        Duration: 2.5 seconds
        Result: SUCCESS"""
        
        # Wrap with headers
        wrapped = planning_orchestrator.get_response_with_headers(template_output)
        
        # Original template content should be completely intact
        assert "**Operation Status Report**" in wrapped
        assert "Status: COMPLETED" in wrapped
        assert "Duration: 2.5 seconds" in wrapped
        assert "Result: SUCCESS" in wrapped
        
        # Headers should wrap, not modify
        assert "## 🧠 CORTEX" in wrapped
        assert "Copyright ©" in wrapped
    
    def test_json_response_with_headers(self, planning_orchestrator):
        """AC-ENH-001-02: JSON responses should render unchanged with headers."""
        import json
        
        # Create JSON response
        json_data = {
            "phase_id": "PHASE-02",
            "status": "IN_PROGRESS",
            "progress": 75
        }
        json_response = json.dumps(json_data, indent=2)
        
        # Wrap with headers
        wrapped = planning_orchestrator.get_response_with_headers(json_response)
        
        # JSON should be intact
        assert '"phase_id": "PHASE-02"' in wrapped
        assert '"status": "IN_PROGRESS"' in wrapped
        assert '"progress": 75' in wrapped
        
        # Extract JSON from wrapped response (between separators)
        lines = wrapped.split('\n')
        # Find the JSON portion (after first blank line, before last separator)
        json_lines = []
        in_json = False
        for line in lines:
            if line.startswith('{'):
                in_json = True
            if in_json:
                json_lines.append(line)
                if line.startswith('}'):
                    break
        
        # Verify JSON is still parseable
        json_text = '\n'.join(json_lines)
        parsed = json.loads(json_text)
        assert parsed["phase_id"] == "PHASE-02"
        assert parsed["status"] == "IN_PROGRESS"
    
    def test_multiline_template_with_headers(self, planning_orchestrator):
        """AC-ENH-001-02: Multiline template should render unchanged."""
        template = """# Phase Planning Report

## Phase: PHASE-02
- Total ACs: 27
- Completed: 20
- In Progress: 5
- Blocked: 2

## Summary
All systems operational. No blockers identified."""
        
        # Wrap with headers
        wrapped = planning_orchestrator.get_response_with_headers(template)
        
        # Template content should be intact
        assert "# Phase Planning Report" in wrapped
        assert "## Phase: PHASE-02" in wrapped
        assert "Total ACs: 27" in wrapped
        assert "All systems operational" in wrapped
        
        # Headers should wrap
        assert "## 🧠 CORTEX" in wrapped
        assert "Copyright ©" in wrapped


@pytest.mark.ac("ENH-001-02")
class TestHeaderStructureWithOperations:
    """AC-ENH-001-02: Verify complete header structure with real operations."""
    
    def test_complete_flow_with_headers(self, planning_orchestrator):
        """AC-ENH-001-02: Complete orchestrator flow should maintain header structure."""
        # Execute multiple operations
        orch = planning_orchestrator
        
        # Initialize
        init_result = orch.initialize()
        assert init_result.is_ok()
        
        # Get plan status
        status_result = orch.plan_status("PHASE-02")
        assert status_result.is_ok()
        status = status_result.value
        
        # Get next AC
        next_ac_result = orch.next_ac("PHASE-02")
        assert next_ac_result.is_ok()
        next_ac_data = next_ac_result.value
        
        # Create responses for each
        status_response = f"Phase {status['phase_id']}: {status['completion_percentage']:.0f}% complete"
        next_ac_response = f"Next: {next_ac_data['ac_id']}"
        lock_response = "Phase lock enforced"
        
        # Wrap all with headers
        status_wrapped = orch.get_response_with_headers(status_response)
        next_wrapped = orch.get_response_with_headers(next_ac_response)
        lock_wrapped = orch.get_response_with_headers(lock_response)
        
        # All should have consistent header structure
        for wrapped in [status_wrapped, next_wrapped, lock_wrapped]:
            assert "## 🧠 CORTEX" in wrapped
            assert "GetPlanStatus" in wrapped
            assert "PlanningOrchestrator" in wrapped
            assert "PHASE-PLANNING" in wrapped
            assert "Asif Hussain" in wrapped
            assert "Copyright ©" in wrapped
            assert "2025-2026" in wrapped
    
    def test_header_structure_consistency(self, planning_orchestrator):
        """AC-ENH-001-02: Header structure should be consistent across multiple calls."""
        orch = planning_orchestrator
        
        # Call multiple times with different content
        responses = [
            "Status OK",
            "AC retrieved",
            "Lock enforced",
            "Planning complete"
        ]
        
        wrapped_responses = [orch.get_response_with_headers(r) for r in responses]
        
        # All should have identical header structure
        for wrapped in wrapped_responses:
            lines = wrapped.split('\n')
            
            # First line should have header
            assert "## 🧠 CORTEX" in lines[0]
            
            # Should have separator after header
            assert "---" in lines
            
            # Should have copyright section
            assert any("Copyright ©" in line for line in lines)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


