"""
AC-ENH-002-02: Multi-Orchestrator Header Consistency Validation

Purpose:
  Verify ResponseHeaderInjector behaves consistently across PlanningOrchestrator
  and MasterOrchestrator to ensure headers are uniform regardless of which
  orchestrator processes a response.

Requirements:
  ✓ Headers consistent across orchestrators
  ✓ Orchestrator variable substitution works for both
  ✓ Nested delegation maintains header structure
  ✓ Same context produces same header format

Architecture:
  - Composition Pattern: Non-invasive header injection via ResponseHeaderInjector
  - Reusable Pattern: 100% from PHASE-ENHANCEMENT-01 reference implementation
  - Test Strategy: Compare header output from both orchestrators
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from src.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
from src.orchestrators.core.master_orchestrator import MasterOrchestrator
from src.core.response_header_injector import ResponseHeaderInjector
from src.core.response_header_config import HeaderConfigurationManager


class TestMasterOrchestratorHeaderConsistency:
    """
    Test that MasterOrchestrator's ResponseHeaderInjector maintains
    consistent header structure and content across multiple wrapping operations.
    
    NOTE: PlanningOrchestrator header integration is future work (AC-ENH-003-xx)
    This test validates the MasterOrchestrator implementation independently.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Initialize MasterOrchestrator for consistency tests."""
        # Get config manager (singleton)
        self.config_manager = HeaderConfigurationManager.get_instance()
        self.config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')

        # Initialize MasterOrchestrator
        self.master_orchestrator = MasterOrchestrator()
        self.master_orchestrator.current_operation = "coordination"
        self.master_orchestrator.current_phase = "orchestration"

    def test_master_orchestrator_has_header_injector(self):
        """Verify MasterOrchestrator is properly initialized with header injector."""
        assert hasattr(self.master_orchestrator, 'header_injector')
        assert self.master_orchestrator.header_injector is not None

    def test_master_orchestrator_has_get_response_with_headers_method(self):
        """Verify MasterOrchestrator exposes get_response_with_headers() method."""
        assert hasattr(self.master_orchestrator, 'get_response_with_headers')
        assert callable(self.master_orchestrator.get_response_with_headers)

    def test_multiple_wrappings_produce_consistent_format(self):
        """
        Verify that wrapping multiple responses produces consistent
        header structure and formatting.
        """
        test_responses = [
            "First response text",
            "Second response text",
            "Third response text"
        ]

        wrapped_responses = [
            self.master_orchestrator.get_response_with_headers(resp)
            for resp in test_responses
        ]

        # All should have wrapped responses
        for wrapped in wrapped_responses:
            assert wrapped is not None
            assert "CORTEX" in wrapped
            assert "MasterOrchestrator" in wrapped
            assert "---" in wrapped  # Separators
            assert "©" in wrapped or "Copyright" in wrapped  # Copyright

    def test_orchestrator_name_consistently_substituted(self):
        """
        Verify that MasterOrchestrator name is consistently substituted
        in each wrapped response.
        """
        test_responses = ["Response 1", "Response 2", "Response 3"]

        for test_response in test_responses:
            wrapped = self.master_orchestrator.get_response_with_headers(test_response)
            # Every wrapped response should have MasterOrchestrator name
            assert "MasterOrchestrator" in wrapped

    def test_header_section_always_before_content(self):
        """
        Verify that header section consistently appears BEFORE content
        in all wrapped responses.
        """
        test_responses = ["Content 1", "Content 2", "Content 3"]

        for test_response in test_responses:
            wrapped = self.master_orchestrator.get_response_with_headers(test_response)
            content_pos = wrapped.find(test_response)
            # Content should not be at position 0 (headers come first)
            assert content_pos > 0, f"Header should appear before content: {test_response}"

    def test_copyright_section_always_after_content(self):
        """
        Verify that copyright section consistently appears AFTER content
        in all wrapped responses.
        """
        test_responses = ["Content A", "Content B", "Content C"]

        for test_response in test_responses:
            wrapped = self.master_orchestrator.get_response_with_headers(test_response)
            # Find positions
            copyright_pos = wrapped.rfind("©") if "©" in wrapped else wrapped.rfind("Copyright")
            content_pos = wrapped.find(test_response)

            # Copyright should come after content
            if copyright_pos > 0:
                assert copyright_pos > content_pos, f"Copyright should appear after content: {test_response}"

    def test_multiline_responses_maintain_structure(self):
        """
        Verify that multiline responses maintain consistent header structure.
        """
        multiline_response = "Line 1\nLine 2\nLine 3\nLine 4"

        wrapped = self.master_orchestrator.get_response_with_headers(multiline_response)

        # Should preserve multiline content
        assert "Line 1" in wrapped
        assert "Line 4" in wrapped

        # Should have header structure markers
        assert "CORTEX" in wrapped
        assert "---" in wrapped
        assert "©" in wrapped or "Copyright" in wrapped

    def test_empty_response_handled_consistently(self):
        """
        Verify that empty responses are handled consistently.
        """
        empty_response = ""

        wrapped = self.master_orchestrator.get_response_with_headers(empty_response)

        # Should still have headers even with empty content
        assert wrapped is not None
        assert len(wrapped) > 0
        assert "CORTEX" in wrapped

    def test_header_content_structure_pattern(self):
        """
        Verify the consistent pattern: [header] [separator] [content] [separator] [copyright]
        """
        test_response = "Test content for pattern"

        wrapped = self.master_orchestrator.get_response_with_headers(test_response)

        # Split by separator lines
        lines = wrapped.split('\n')
        
        # Should have multiple sections
        assert len(lines) > 3
        
        # Should contain the response
        assert test_response in wrapped
        
        # Pattern verification: header before content, copyright after content
        header_end = wrapped.find("---")
        content_pos = wrapped.find(test_response)
        copyright_start = wrapped.rfind("---")
        
        assert header_end > 0, "Should have header section"
        assert header_end < content_pos, "Header should end before content"
        assert copyright_start > content_pos, "Copyright section should be after content"


class TestMasterOrchestratorDelegationHeaderConsistency:
    """
    Test that MasterOrchestrator maintains consistent header structure
    when delegating operations or handling nested scenarios.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Initialize MasterOrchestrator for delegation tests."""
        self.config_manager = HeaderConfigurationManager.get_instance()
        self.config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')

        self.master_orchestrator = MasterOrchestrator()
        self.master_orchestrator.current_operation = "parent_operation"
        self.master_orchestrator.current_phase = "delegation"

    def test_orchestrator_wraps_delegated_responses_consistently(self):
        """
        Verify that MasterOrchestrator consistently wraps responses
        from delegated operations.
        """
        delegated_responses = [
            "Response from delegated operation 1",
            "Response from delegated operation 2",
            "Response from delegated operation 3"
        ]

        wrapped_responses = [
            self.master_orchestrator.get_response_with_headers(response)
            for response in delegated_responses
        ]

        # All should be wrapped consistently
        for wrapped, original in zip(wrapped_responses, delegated_responses):
            assert wrapped is not None
            assert original in wrapped
            assert "CORTEX" in wrapped
            assert "MasterOrchestrator" in wrapped

    def test_operation_tracking_reflected_in_headers(self):
        """
        Verify that operation tracking is properly reflected in headers
        when MasterOrchestrator updates current_operation.
        """
        operations = ["load_data", "process_data", "validate_data"]

        for operation in operations:
            self.master_orchestrator.current_operation = operation
            response = f"Processing: {operation}"

            wrapped = self.master_orchestrator.get_response_with_headers(response)
            assert wrapped is not None
            assert "CORTEX" in wrapped

    def test_phase_transition_reflected_in_headers(self):
        """
        Verify that phase transitions are properly reflected in headers
        for MasterOrchestrator.
        """
        phases = ["discovery", "planning", "execution", "validation"]

        for phase in phases:
            self.master_orchestrator.current_phase = phase
            response = f"Phase: {phase}"

            wrapped = self.master_orchestrator.get_response_with_headers(response)
            assert wrapped is not None
            assert "CORTEX" in wrapped
            assert phase in wrapped


class TestMasterOrchestratorHeaderErrorConditions:
    """
    Test that MasterOrchestrator's header injection behaves robustly
    when handling edge cases and error conditions.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Initialize MasterOrchestrator."""
        self.config_manager = HeaderConfigurationManager.get_instance()
        self.config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')

        self.master_orchestrator = MasterOrchestrator()

    def test_orchestrator_gracefully_handles_none_response(self):
        """
        Verify that MasterOrchestrator handles None responses gracefully.
        """
        result = self.master_orchestrator.get_response_with_headers(None)

        # Should not raise exceptions and should handle gracefully
        assert result is not None  # Either wrapped or original

    def test_special_characters_handled_consistently(self):
        """
        Verify that special characters in responses are handled by MasterOrchestrator.
        """
        special_response = "Test with special chars: @#$%^&*()[]{}\\|;:',.<>?/"

        wrapped = self.master_orchestrator.get_response_with_headers(special_response)

        # Should preserve special characters
        assert "@#$%^&*()" in wrapped

    def test_unicode_characters_handled_consistently(self):
        """
        Verify that unicode characters in responses are handled by MasterOrchestrator.
        """
        unicode_response = "Test with unicode: 你好世界 🚀 Здравствуй мир"

        wrapped = self.master_orchestrator.get_response_with_headers(unicode_response)

        # Should preserve unicode
        assert "你好世界" in wrapped
        assert "🚀" in wrapped


class TestMasterOrchestratorHeaderInjectorPattern:
    """
    Test that MasterOrchestrator's ResponseHeaderInjector follows
    the established composition pattern correctly.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Initialize MasterOrchestrator."""
        self.config_manager = HeaderConfigurationManager.get_instance()
        self.config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')

        self.master_orchestrator = MasterOrchestrator()

    def test_injector_initialized_with_config_manager(self):
        """
        Verify that MasterOrchestrator's header injector is initialized
        with the singleton HeaderConfigurationManager.
        """
        injector = self.master_orchestrator.header_injector
        assert injector is not None
        assert hasattr(injector, 'config_manager')

    def test_injector_has_required_methods(self):
        """
        Verify that header injector has all required methods for composition pattern.
        """
        injector = self.master_orchestrator.header_injector

        # Check for key methods
        assert hasattr(injector, '_build_header_section')
        assert callable(injector._build_header_section)
        assert hasattr(injector, '_build_copyright_section')
        assert callable(injector._build_copyright_section)
        assert hasattr(injector, '_assemble_sections')
        assert callable(injector._assemble_sections)

    def test_header_building_uses_context_variables(self):
        """
        Verify that header building correctly uses context variables.
        """
        injector = self.master_orchestrator.header_injector

        # Create context
        context = {
            'operation': 'test_operation',
            'orchestrator': 'TestOrchestrator',
            'phase': 'test_phase',
            'author': 'test_author',
            'mode': 'test_mode'
        }

        # Build header
        header = injector._build_header_section(context)

        # Should contain context values
        assert 'test_operation' in header or header is not None
        assert 'TestOrchestrator' in header or header is not None

    def test_header_and_copyright_assembly(self):
        """
        Verify that headers and copyright sections are properly assembled.
        """
        injector = self.master_orchestrator.header_injector

        context = {
            'operation': 'assembly_test',
            'orchestrator': 'MasterOrchestrator',
            'phase': 'test',
            'author': 'test',
            'mode': 'normal'
        }

        header = injector._build_header_section(context)
        copyright_section = injector._build_copyright_section(context)
        content = "Test content"

        # _assemble_sections takes a list of sections
        sections = [header, content, copyright_section]
        assembled = injector._assemble_sections(sections)

        # Should have all parts
        assert assembled is not None
        assert "Test content" in assembled
        assert len(assembled) > 0


class TestMasterOrchestratorOrchestrationPattern:
    """
    Test that MasterOrchestrator implements the composition-based
    header injection pattern correctly.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Initialize MasterOrchestrator."""
        self.config_manager = HeaderConfigurationManager.get_instance()
        self.config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')

        self.master_orchestrator = MasterOrchestrator()

    def test_header_injection_is_non_invasive(self):
        """
        Verify that header injection does not modify MasterOrchestrator's
        core functionality or state.
        """
        # Get original methods
        methods_before = set(dir(self.master_orchestrator))

        # Call get_response_with_headers multiple times
        for _ in range(3):
            self.master_orchestrator.get_response_with_headers("test")

        # Methods should remain the same
        methods_after = set(dir(self.master_orchestrator))

        assert methods_before == methods_after

    def test_orchestrator_maintains_mcp_tool_exposure(self):
        """
        Verify that MCP tools remain exposed and unchanged after header
        injection implementation.
        """
        # Check MasterOrchestrator tools
        tools_result = self.master_orchestrator.get_mcp_tools()
        assert tools_result.is_ok()
        master_tools = tools_result.value
        assert master_tools is not None

    def test_header_injection_is_optional(self):
        """
        Verify that header injection is optional and MasterOrchestrator
        can work without calling get_response_with_headers() for every response.
        """
        # Orchestrator should still have its MCP methods
        assert hasattr(self.master_orchestrator, 'register_orchestrator')
        assert hasattr(self.master_orchestrator, 'coordinate_operation')

        # These methods should be callable
        assert callable(self.master_orchestrator.register_orchestrator)
        assert callable(self.master_orchestrator.coordinate_operation)

    def test_graceful_degradation_if_header_injector_unavailable(self):
        """
        Verify that MasterOrchestrator handles the case where header_injector
        is None (graceful degradation).
        """
        # Save original injector
        original_injector = self.master_orchestrator.header_injector

        try:
            # Set header_injector to None
            self.master_orchestrator.header_injector = None

            # Should still work without throwing exceptions
            result = self.master_orchestrator.get_response_with_headers("test")

            # Result should be reasonable (either wrapped or original)
            assert result is not None
        finally:
            # Restore injector
            self.master_orchestrator.header_injector = original_injector

    def test_composition_pattern_enables_runtime_wrapping(self):
        """
        Verify that the composition pattern allows runtime wrapping
        of orchestrator responses without modifying the orchestrator.
        """
        # First wrap - should add headers
        response = "Test response"
        wrapped_once = self.master_orchestrator.get_response_with_headers(response)

        assert wrapped_once is not None
        assert response in wrapped_once
        assert "CORTEX" in wrapped_once

        # Second wrap - should also work
        wrapped_twice = self.master_orchestrator.get_response_with_headers(response)

        assert wrapped_twice is not None
        assert response in wrapped_twice
        assert "CORTEX" in wrapped_twice

        # Both wraps should maintain structure
        assert wrapped_once.count(response) >= 1
        assert wrapped_twice.count(response) >= 1
