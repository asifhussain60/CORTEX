"""
Tests for CORTEX Help System

Validates help generation, formatting, and intelligent request handling.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from src.cortex_help import (
    show_help,
    get_quick_reference,
    handle_help_request,
    cortex_help,
    HelpFormat
)
from src.plugins.command_registry import CommandCategory, get_command_registry


class TestHelpGeneration:
    """Test help text generation in various formats"""
    
    def test_concise_help_generates(self):
        """Concise help should generate without errors"""
        help_text = show_help(HelpFormat.CONCISE)
        
        assert help_text is not None
        assert len(help_text) > 0
        assert "CORTEX" in help_text
        assert "commands" in help_text.lower()
    
    def test_concise_help_has_bullets(self):
        """Concise help should use bullet points"""
        help_text = show_help(HelpFormat.CONCISE)
        
        assert "•" in help_text or "-" in help_text
        assert "PLATFORM" in help_text or "Platform" in help_text
    
    def test_concise_help_shows_natural_language(self):
        """Concise help should show natural language equivalents"""
        help_text = show_help(HelpFormat.CONCISE)
        
        # Should mention natural language is available
        assert any(keyword in help_text.lower() for keyword in ['natural language', 'say', 'tip'])
    
    def test_detailed_help_generates(self):
        """Detailed help should generate without errors"""
        help_text = show_help(HelpFormat.DETAILED)
        
        assert help_text is not None
        assert len(help_text) > 0
        assert "Command Reference" in help_text
    
    def test_detailed_help_has_examples(self):
        """Detailed help should include examples"""
        help_text = show_help(HelpFormat.DETAILED)
        
        # Should have examples section
        assert "Example" in help_text or "example" in help_text
    
    def test_category_help_generates(self):
        """Category help should generate without errors"""
        help_text = show_help(HelpFormat.CATEGORY)
        
        assert help_text is not None
        assert len(help_text) > 0
        assert "Category" in help_text
    
    def test_category_help_has_table(self):
        """Category help should include summary table"""
        help_text = show_help(HelpFormat.CATEGORY)
        
        # Markdown table markers
        assert "|" in help_text
        assert "Category" in help_text


class TestCategoryFiltering:
    """Test category-specific help"""
    
    def test_platform_commands_only(self):
        """Should filter to platform commands only"""
        help_text = show_help(HelpFormat.CONCISE, CommandCategory.PLATFORM)
        
        assert "Platform" in help_text or "PLATFORM" in help_text
        # Should be shorter than full help
        full_help = show_help(HelpFormat.CONCISE)
        assert len(help_text) < len(full_help)
    
    def test_session_commands_only(self):
        """Should filter to session commands only"""
        help_text = show_help(HelpFormat.CONCISE, CommandCategory.SESSION)
        
        assert "Session" in help_text or "SESSION" in help_text
        assert "/resume" in help_text or "/status" in help_text


class TestQuickReference:
    """Test quick reference functionality"""
    
    def test_quick_reference_generates(self):
        """Quick reference should generate without errors"""
        quick_ref = get_quick_reference()
        
        assert quick_ref is not None
        assert len(quick_ref) > 0
    
    def test_quick_reference_is_concise(self):
        """Quick reference should be shorter than full help"""
        quick_ref = get_quick_reference()
        full_help = show_help(HelpFormat.CONCISE)
        
        assert len(quick_ref) < len(full_help)
    
    def test_quick_reference_has_essentials(self):
        """Quick reference should include essential commands"""
        quick_ref = get_quick_reference()
        
        assert "/help" in quick_ref
        assert "/setup" in quick_ref
        assert "natural language" in quick_ref.lower()


class TestIntelligentHandling:
    """Test intelligent help request handling"""
    
    def test_handles_detailed_request(self):
        """Should detect request for detailed help"""
        result = handle_help_request("show detailed help")
        
        assert "Command Reference" in result
        assert "Example" in result or "example" in result
    
    def test_handles_quick_request(self):
        """Should detect request for quick help"""
        result = handle_help_request("quick reference")
        
        # Should be concise
        assert len(result) < 500
        assert "Quick" in result or "CORTEX" in result
    
    def test_handles_category_request(self):
        """Should detect category-specific request"""
        result = handle_help_request("show platform commands")
        
        assert "Platform" in result or "PLATFORM" in result
    
    def test_handles_generic_request(self):
        """Should handle generic help request"""
        result = handle_help_request("help")
        
        assert result is not None
        assert "CORTEX" in result
    
    def test_defaults_to_concise(self):
        """Should default to concise for ambiguous requests"""
        result = handle_help_request("show commands")
        
        # Should be concise format
        assert "•" in result or "-" in result


class TestConvenienceFunctions:
    """Test convenience wrapper functions"""
    
    def test_cortex_help_function(self):
        """cortex_help() should work as quick access"""
        result = cortex_help()
        
        assert result is not None
        assert "CORTEX" in result
    
    def test_cortex_help_is_concise(self):
        """cortex_help() should return concise format"""
        result = cortex_help()
        expected = show_help(HelpFormat.CONCISE)
        
        assert result == expected


class TestHelpIntegration:
    """Test help system integration with command registry"""
    
    def test_includes_registered_commands(self):
        """Help should include all registered commands"""
        registry = get_command_registry()
        all_commands = registry.get_all_commands()
        
        help_text = show_help(HelpFormat.CONCISE)
        
        # Check that core commands are present
        assert "/help" in help_text
        assert "/status" in help_text
        assert "/resume" in help_text
    
    def test_shows_command_stats(self):
        """Help should show command statistics"""
        help_text = show_help(HelpFormat.CONCISE)
        
        # Should show stats
        assert "commands" in help_text.lower()
        assert any(char.isdigit() for char in help_text)  # Has numbers
    
    def test_handles_empty_category(self):
        """Should handle category with no commands gracefully"""
        # Use a category that might not have commands
        help_text = show_help(HelpFormat.CONCISE, CommandCategory.CUSTOM)
        
        # Should not crash
        assert help_text is not None


class TestHelpFormatting:
    """Test help text formatting and readability"""
    
    def test_concise_uses_markdown(self):
        """Concise help should use markdown formatting"""
        help_text = show_help(HelpFormat.CONCISE)
        
        # Should have markdown elements
        assert "**" in help_text or "*" in help_text
        assert "`" in help_text
    
    def test_has_clear_sections(self):
        """Help should have clear section headers"""
        help_text = show_help(HelpFormat.CONCISE)
        
        # Should have category headers
        assert any(category.value.upper() in help_text 
                  for category in CommandCategory)
    
    def test_readable_line_length(self):
        """Help lines should not be excessively long"""
        help_text = show_help(HelpFormat.CONCISE)
        lines = help_text.split('\n')
        
        # Most lines should be under 100 chars for readability
        long_lines = [line for line in lines if len(line) > 120]
        assert len(long_lines) < len(lines) * 0.2  # Less than 20% long lines


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
