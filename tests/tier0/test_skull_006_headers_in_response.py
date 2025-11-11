"""
SKULL-006: Header/Footer in Copilot Response

Test harness to enforce that operation orchestrators include formatted headers
and footers in the Copilot Chat response, not just terminal output.

Real incident (2025-11-11):
- User: "why is header not being displayed?"
- Headers printing to terminal correctly
- But GitHub Copilot Chat response had NO header
- User wants header "in the copilot response in the chat window"

This test prevents regression by verifying:
1. OperationResult contains formatted_header/footer
2. ResponseFormatter uses stored headers
3. Headers appear in final formatted response
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.operations.base_operation_module import OperationResult, OperationStatus
from src.operations.response_formatter import ResponseFormatter, format_for_copilot
from src.operations.header_utils import format_minimalist_header, format_completion_footer


class TestSKULL006HeadersInResponse:
    """Enforce SKULL-006: Headers must appear in Copilot Chat response."""
    
    def test_operation_result_has_header_footer_fields(self):
        """SKULL-006-A: OperationResult must have formatted_header/footer fields."""
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Test complete",
            formatted_header="Test Header",
            formatted_footer="Test Footer"
        )
        
        assert hasattr(result, 'formatted_header'), \
            "OperationResult missing formatted_header field"
        assert hasattr(result, 'formatted_footer'), \
            "OperationResult missing formatted_footer field"
        assert result.formatted_header == "Test Header"
        assert result.formatted_footer == "Test Footer"
    
    def test_format_minimalist_header_returns_string(self):
        """SKULL-006-B: format_minimalist_header must return formatted string."""
        header = format_minimalist_header(
            operation_name="Test Operation",
            version="1.0.0",
            profile="standard",
            mode="LIVE EXECUTION",
            dry_run=False,
            purpose="Test purpose with specific goal"
        )
        
        assert isinstance(header, str), "Header must be a string"
        assert len(header) > 0, "Header must not be empty"
        assert "CORTEX Test Operation Orchestrator" in header
        assert "Profile: standard" in header
        assert "Mode: LIVE EXECUTION" in header
        assert "📋 Purpose: Test purpose with specific goal" in header
        assert "© 2024-2025 Asif Hussain" in header
    
    def test_format_completion_footer_returns_string(self):
        """SKULL-006-C: format_completion_footer must return formatted string."""
        accomplishments = [
            "Discovered 37 modules (43% implemented)",
            "Analyzed 5 design-implementation gaps",
            "Consolidated 3 status files → 1 source of truth"
        ]
        
        footer = format_completion_footer(
            operation_name="Test Operation",
            success=True,
            duration_seconds=12.5,
            summary="3 improvements applied",
            accomplishments=accomplishments
        )
        
        assert isinstance(footer, str), "Footer must be a string"
        assert len(footer) > 0, "Footer must not be empty"
        assert "✅ COMPLETED" in footer
        assert "12.5s" in footer
        assert "3 improvements applied" in footer
        assert "Accomplishments:" in footer
        assert "• Discovered 37 modules" in footer
    
    def test_response_formatter_uses_stored_header(self):
        """SKULL-006-D: ResponseFormatter must use stored formatted_header."""
        # Create result with formatted header
        formatted_header = format_minimalist_header(
            operation_name="Design Sync",
            version="1.0.0",
            profile="comprehensive",
            mode="LIVE EXECUTION",
            dry_run=False,
            purpose="Full sync: gap analysis + optimization integration"
        )
        
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Design sync complete",
            formatted_header=formatted_header,
            formatted_footer="Test Footer"
        )
        
        # Format for Copilot
        formatted_response = ResponseFormatter.format_operation_result(
            operation_name="Design Sync",
            result=result,
            context={'profile': 'comprehensive'}
        )
        
        # Verify header is in response
        assert formatted_header in formatted_response, \
            "Formatted header must appear in Copilot response"
        assert "CORTEX Design Sync Orchestrator" in formatted_response
        assert "📋 Purpose: Full sync: gap analysis + optimization integration" in formatted_response
    
    def test_response_formatter_uses_stored_footer(self):
        """SKULL-006-E: ResponseFormatter must use stored formatted_footer."""
        accomplishments = [
            "Discovered 37 modules (43% implemented)",
            "Analyzed 5 design-implementation gaps"
        ]
        
        formatted_footer = format_completion_footer(
            operation_name="Design Sync",
            success=True,
            duration_seconds=8.3,
            summary="2 improvements applied",
            accomplishments=accomplishments
        )
        
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Design sync complete",
            formatted_header="Test Header",
            formatted_footer=formatted_footer
        )
        
        # Format for Copilot
        formatted_response = ResponseFormatter.format_operation_result(
            operation_name="Design Sync",
            result=result,
            context={'profile': 'standard'}
        )
        
        # Verify footer is in response
        assert formatted_footer in formatted_response, \
            "Formatted footer must appear in Copilot response"
        assert "✅ COMPLETED" in formatted_response
        assert "8.3s" in formatted_response
        assert "Accomplishments:" in formatted_response
    
    def test_headers_wrapped_in_code_blocks(self):
        """SKULL-006-F: Headers must be wrapped in code blocks for proper display."""
        formatted_header = "TEST HEADER LINE 1\nTEST HEADER LINE 2"
        formatted_footer = "TEST FOOTER LINE 1\nTEST FOOTER LINE 2"
        
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Test complete",
            formatted_header=formatted_header,
            formatted_footer=formatted_footer
        )
        
        formatted_response = ResponseFormatter.format_operation_result(
            operation_name="Test",
            result=result,
            context={}
        )
        
        # Headers should be in code blocks
        assert "```\n" + formatted_header in formatted_response, \
            "Header must be wrapped in code block"
        assert "```\n" + formatted_footer in formatted_response, \
            "Footer must be wrapped in code block"
    
    def test_copyright_attribution_visible(self):
        """SKULL-006-G: Copyright attribution must be visible in response."""
        formatted_header = format_minimalist_header(
            operation_name="Test Operation",
            version="1.0.0",
            profile="standard",
            mode="LIVE EXECUTION",
            dry_run=False
        )
        
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Test complete",
            formatted_header=formatted_header
        )
        
        formatted_response = ResponseFormatter.format_operation_result(
            operation_name="Test",
            result=result,
            context={}
        )
        
        # Copyright must be visible
        assert "© 2024-2025 Asif Hussain" in formatted_response, \
            "Copyright attribution must be visible in Copilot response"
        assert "Proprietary" in formatted_response
        assert "github.com/asifhussain60/CORTEX" in formatted_response
    
    def test_purpose_provides_context(self):
        """SKULL-006-H: Purpose field must provide context about operation goal."""
        purpose = "Synchronize design docs with implementation reality + consolidate status files"
        
        formatted_header = format_minimalist_header(
            operation_name="Design Sync",
            version="1.0.0",
            profile="standard",
            mode="LIVE EXECUTION",
            dry_run=False,
            purpose=purpose
        )
        
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Complete",
            formatted_header=formatted_header
        )
        
        formatted_response = ResponseFormatter.format_operation_result(
            operation_name="Design Sync",
            result=result,
            context={}
        )
        
        # Purpose must be visible
        assert "📋 Purpose:" in formatted_response
        assert purpose in formatted_response
    
    def test_accomplishments_show_value_delivered(self):
        """SKULL-006-I: Accomplishments must show value delivered to user."""
        accomplishments = [
            "Discovered 37 modules (43% implemented)",
            "Analyzed 5 design-implementation gaps",
            "Consolidated 3 status files → 1 source of truth",
            "Committed changes: abc123de"
        ]
        
        formatted_footer = format_completion_footer(
            operation_name="Design Sync",
            success=True,
            duration_seconds=10.2,
            accomplishments=accomplishments
        )
        
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Complete",
            formatted_footer=formatted_footer
        )
        
        formatted_response = ResponseFormatter.format_operation_result(
            operation_name="Design Sync",
            result=result,
            context={}
        )
        
        # All accomplishments must be visible
        assert "Accomplishments:" in formatted_response
        for accomplishment in accomplishments:
            assert accomplishment in formatted_response, \
                f"Accomplishment '{accomplishment}' must be visible"
    
    def test_integration_design_sync_operation(self):
        """SKULL-006-J: Integration test with actual design_sync operation."""
        # This would be run against actual operation
        # For now, we test the pattern
        
        # Simulate design_sync result
        formatted_header = format_minimalist_header(
            operation_name="Design Sync",
            version="1.0.0",
            profile="comprehensive",
            mode="LIVE EXECUTION",
            dry_run=False,
            purpose="Full sync: gap analysis + optimization integration + MD→YAML conversion"
        )
        
        accomplishments = [
            "Discovered 37 modules (43% implemented)",
            "Analyzed 3 design-implementation gaps",
            "Consolidated 2 status files → 1 source of truth"
        ]
        
        formatted_footer = format_completion_footer(
            operation_name="Design Sync",
            success=True,
            duration_seconds=15.7,
            summary="3 improvements applied",
            accomplishments=accomplishments
        )
        
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Design synchronization complete",
            data={
                'metrics': {'gaps_analyzed': 3},
                'implementation_state': {'total_modules': 37}
            },
            formatted_header=formatted_header,
            formatted_footer=formatted_footer
        )
        
        # Format for Copilot Chat
        formatted_response = format_for_copilot(
            operation_name="Design Sync",
            result=result,
            context={'profile': 'comprehensive'}
        )
        
        # Comprehensive verification
        assert "CORTEX Design Sync Orchestrator v1.0.0" in formatted_response
        assert "Profile: comprehensive" in formatted_response
        assert "📋 Purpose: Full sync" in formatted_response
        assert "© 2024-2025 Asif Hussain" in formatted_response
        assert "✅ COMPLETED in 15.7s" in formatted_response
        assert "Accomplishments:" in formatted_response
        assert "Discovered 37 modules" in formatted_response
        assert "3 improvements applied" in formatted_response
    
    def test_missing_header_footer_graceful_fallback(self):
        """SKULL-006-K: Gracefully handle missing headers (backward compatibility)."""
        # Old-style result without formatted headers
        result = OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Complete"
        )
        
        # Should still format without crashing
        formatted_response = ResponseFormatter.format_operation_result(
            operation_name="Test",
            result=result,
            context={}
        )
        
        assert isinstance(formatted_response, str)
        assert len(formatted_response) > 0
        # Should at least have copyright in footer
        assert "© 2024-2025 Asif Hussain" in formatted_response


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
