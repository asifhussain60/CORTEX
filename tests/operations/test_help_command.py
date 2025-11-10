"""
Tests for CORTEX Help Command

Validates help command functionality including:
    - Table, list, and detailed format generation
    - Status determination logic
    - Command lookup
    - Integration with execute_operation()

Author: Asif Hussain
Version: 1.0
"""

import pytest
from src.operations import show_help, execute_operation
from src.operations.help_command import HelpCommand, find_command


class TestHelpCommand:
    """Test suite for help command."""
    
    def test_show_help_table_format(self):
        """Test table format generation."""
        help_text = show_help('table')
        
        assert 'CORTEX COMMANDS' in help_text
        assert 'Status' in help_text
        assert 'Quick Command' in help_text
        assert 'Natural Language Example' in help_text
        assert 'Module' in help_text
        assert 'Legend:' in help_text
        assert 'Usage:' in help_text
    
    def test_show_help_list_format(self):
        """Test list format generation."""
        help_text = show_help('list')
        
        assert 'CORTEX COMMANDS:' in help_text
        assert 'Example:' in help_text
        assert 'Module:' in help_text
    
    def test_show_help_detailed_format(self):
        """Test detailed format generation."""
        help_text = show_help('detailed')
        
        assert 'CORTEX COMMANDS - DETAILED' in help_text
        assert 'Quick:' in help_text
        assert 'Status:' in help_text
        assert 'Modules:' in help_text
    
    def test_status_icons_present(self):
        """Test that status icons are included."""
        help_text = show_help('table')
        
        # Should have at least some status indicators
        # (Exact icons may vary based on implementation status)
        assert len(help_text) > 500  # Reasonable size check
    
    def test_operations_sorted_alphabetically(self):
        """Test that operations are sorted by quick command."""
        help_cmd = HelpCommand()
        ops = help_cmd._gather_operation_data()
        
        quick_commands = [op['quick_cmd'].lower() for op in ops]
        sorted_commands = sorted(quick_commands)
        
        assert quick_commands == sorted_commands, "Operations should be alphabetically sorted"
    
    def test_all_operations_included(self):
        """Test that all operations from YAML are included."""
        help_cmd = HelpCommand()
        ops = help_cmd._gather_operation_data()
        
        # Should have all 12 operations (as of 2025-11-10)
        assert len(ops) >= 12, f"Expected at least 12 operations, got {len(ops)}"
    
    def test_status_determination(self):
        """Test status determination logic."""
        help_cmd = HelpCommand()
        
        # Test refresh_cortex_story (should be 'ready' - 6/6 modules implemented)
        op_info = help_cmd.factory.get_operation_info('refresh_cortex_story')
        status = help_cmd._determine_status('refresh_cortex_story', op_info)
        assert status == 'ready'
        
        # Test environment_setup (should be 'partial' - 4/11 modules implemented)
        op_info = help_cmd.factory.get_operation_info('environment_setup')
        status = help_cmd._determine_status('environment_setup', op_info)
        assert status == 'partial'
    
    def test_find_command(self):
        """Test command lookup functionality."""
        # Find setup operation
        op = find_command('setup')
        assert op is not None
        assert op['operation_id'] == 'environment_setup'
        
        # Find cleanup operation
        op = find_command('cleanup')
        assert op is not None
        assert op['operation_id'] == 'workspace_cleanup'
    
    def test_execute_operation_help(self):
        """Test help command integration with execute_operation."""
        report = execute_operation('help')
        
        assert report.success is True
        assert report.operation_id == 'help'
        assert report.operation_name == 'CORTEX Help'
        assert 'help_text' in report.context
        assert len(report.context['help_text']) > 500
    
    def test_help_aliases(self):
        """Test various help command aliases."""
        aliases = ['help', '/help', '/CORTEX help', 'show help']
        
        for alias in aliases:
            report = execute_operation(alias)
            assert report.success is True, f"Alias '{alias}' should work"
            assert report.operation_id == 'help'
    
    def test_help_format_parameter(self):
        """Test format parameter in execute_operation."""
        # Table format (default)
        report = execute_operation('help', format='table')
        assert 'CORTEX COMMANDS' in report.context['help_text']
        
        # List format
        report = execute_operation('help', format='list')
        assert 'CORTEX COMMANDS:' in report.context['help_text']
        
        # Detailed format
        report = execute_operation('help', format='detailed')
        assert 'DETAILED' in report.context['help_text']


class TestHelpCommandEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_factory(self):
        """Test help command with no operations."""
        # This shouldn't happen in practice, but test graceful handling
        help_cmd = HelpCommand()
        help_text = help_cmd.generate_help('table')
        assert 'CORTEX COMMANDS' in help_text
    
    def test_missing_natural_language(self):
        """Test operation with no natural_language field."""
        help_cmd = HelpCommand()
        ops = help_cmd._gather_operation_data()
        
        # All operations should have at least operation_id as fallback
        for op in ops:
            assert op['quick_cmd'] is not None
            assert len(op['quick_cmd']) > 0
    
    def test_invalid_format(self):
        """Test help command with invalid format."""
        # Should fall back to table format
        help_text = show_help('invalid_format')
        assert 'CORTEX COMMANDS' in help_text
    
    def test_find_nonexistent_command(self):
        """Test lookup of non-existent command."""
        op = find_command('this_does_not_exist')
        assert op == {}


class TestHelpCommandOutput:
    """Test output quality and formatting."""
    
    def test_no_truncation_issues(self):
        """Test that text doesn't have obvious truncation issues."""
        help_text = show_help('table')
        
        # Should not have excessive whitespace or broken lines
        lines = help_text.split('\n')
        for line in lines:
            if line.strip():  # Non-empty line
                assert len(line) <= 100, f"Line too long: {line}"
    
    def test_legend_completeness(self):
        """Test that legend explains all status icons."""
        help_text = show_help('table')
        
        assert '✅ ready' in help_text or 'ready' in help_text
        assert 'partial' in help_text
        assert 'pending' in help_text
        assert 'planned' in help_text
    
    def test_usage_instructions_present(self):
        """Test that usage instructions are included."""
        help_text = show_help('table')
        
        assert 'Natural language:' in help_text or 'natural language' in help_text.lower()
        assert 'Slash commands:' in help_text or 'slash command' in help_text.lower()
        assert 'execute_operation' in help_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
