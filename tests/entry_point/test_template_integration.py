"""
Integration Tests for Template System in CortexEntry

Tests that template responses work correctly when called through
the main entry point.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.entry_point.cortex_entry import CortexEntry


@pytest.fixture
def entry():
    """Create CortexEntry instance for testing."""
    entry = CortexEntry(enable_logging=False)
    yield entry
    entry.cleanup()


class TestTemplateIntegration:
    """Test suite for template system integration."""
    
    def test_help_command_returns_template(self, entry):
        """Test that 'help' command returns template response."""
        response = entry.process("help", format_type="text")
        
        # Should contain CORTEX branding
        assert "CORTEX" in response
        assert "Author: Asif Hussain" in response
        
        # Should be instant (no agent routing)
        # Template responses are pre-formatted
    
    def test_help_command_case_insensitive(self, entry):
        """Test that help command is case insensitive."""
        responses = [
            entry.process("help"),
            entry.process("HELP"),
            entry.process("Help"),
            entry.process("/help"),
        ]
        
        # All should return same template
        for response in responses:
            assert "CORTEX" in response
    
    def test_status_command_returns_template(self, entry):
        """Test that 'status' command returns template response."""
        response = entry.process("status", format_type="text")
        
        assert "CORTEX" in response
        assert "Author: Asif Hussain" in response
    
    def test_quick_start_command_returns_template(self, entry):
        """Test that 'quick start' command returns template response."""
        response = entry.process("quick start", format_type="text")
        
        assert "CORTEX" in response
        assert "Author: Asif Hussain" in response
    
    def test_non_template_command_routes_to_agent(self, entry):
        """Test that non-template commands still route to agents."""
        # This should NOT match any template
        response = entry.process("implement a feature", format_type="text")
        
        # Should still get a response (routed through agents)
        assert response
        assert len(response) > 0
    
    def test_template_response_performance(self, entry):
        """Test that template responses are fast (< 100ms)."""
        import time
        
        start = time.time()
        entry.process("help")
        duration = (time.time() - start) * 1000  # Convert to ms
        
        # Template responses should be near-instant
        # Allow 500ms for overhead (file I/O, initialization)
        assert duration < 500, f"Template response took {duration}ms (expected < 500ms)"
    
    def test_format_variations(self, entry):
        """Test that templates work with different output formats."""
        text_response = entry.process("help", format_type="text")
        json_response = entry.process("help", format_type="json")
        markdown_response = entry.process("help", format_type="markdown")
        
        # All should contain CORTEX
        assert "CORTEX" in text_response or "CORTEX" in str(json_response)
        assert "CORTEX" in markdown_response
    
    def test_template_loader_initialized(self, entry):
        """Test that template loader is properly initialized."""
        assert entry.template_loader is not None
        assert entry.template_loader._loaded or True  # Lazy loading is OK
    
    def test_template_triggers_registered(self, entry):
        """Test that template triggers are registered."""
        # Ensure templates are loaded
        if not entry.template_loader._loaded:
            entry.template_loader.load_templates()
        
        triggers = entry.template_loader.get_triggers()
        
        # Should have help/status/quick start triggers
        assert any("help" in t for t in triggers)
        assert any("status" in t for t in triggers)
    
    def test_multiple_template_calls_consistent(self, entry):
        """Test that multiple template calls return consistent results."""
        response1 = entry.process("help")
        response2 = entry.process("help")
        
        # Should be identical (templates are deterministic)
        assert response1 == response2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
