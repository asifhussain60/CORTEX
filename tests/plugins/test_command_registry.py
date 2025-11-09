"""
CORTEX Plugin Command Registry Tests

Tests for the extensible command system that allows plugins to register
slash commands as shortcuts to natural language.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plugins.command_registry import (
    PluginCommandRegistry,
    CommandMetadata,
    CommandCategory,
    get_command_registry
)


class TestCommandRegistryInitialization:
    """Test registry initialization and singleton pattern."""
    
    def test_registry_creation(self):
        """Test basic registry creation."""
        registry = PluginCommandRegistry()
        assert registry is not None
        assert isinstance(registry._commands, dict)
    
    def test_singleton_pattern(self):
        """Test that get_command_registry returns singleton."""
        registry1 = get_command_registry()
        registry2 = get_command_registry()
        assert registry1 is registry2
    
    def test_core_commands_registered(self):
        """Test that core commands are pre-registered."""
        registry = PluginCommandRegistry()
        
        # Check core commands exist
        assert registry.is_command("/help")
        assert registry.is_command("/status")
        assert registry.is_command("/resume")
    
    def test_registry_stats_initial(self):
        """Test initial registry statistics."""
        registry = PluginCommandRegistry()
        stats = registry.get_stats()
        
        assert stats['total_commands'] > 0  # Has core commands
        assert stats['total_plugins'] >= 1  # At least "core" plugin
        assert stats['categories'] > 0


class TestCommandRegistration:
    """Test command registration functionality."""
    
    def test_register_valid_command(self):
        """Test registering a valid command."""
        registry = PluginCommandRegistry()
        
        metadata = CommandMetadata(
            command="/test",
            natural_language_equivalent="run tests",
            plugin_id="test_plugin",
            description="Run all tests",
            category=CommandCategory.TESTING
        )
        
        success = registry.register_command(metadata)
        assert success is True
        assert registry.is_command("/test")
    
    def test_register_command_with_aliases(self):
        """Test registering command with aliases."""
        registry = PluginCommandRegistry()
        
        metadata = CommandMetadata(
            command="/platform",
            natural_language_equivalent="switch platform",
            plugin_id="platform_plugin",
            description="Switch platform",
            category=CommandCategory.PLATFORM,
            aliases=["/plat", "/p"]
        )
        
        registry.register_command(metadata)
        
        # Check primary and aliases are registered
        assert registry.is_command("/platform")
        assert registry.is_command("/plat")
        assert registry.is_command("/p")
    
    def test_command_conflict_detection(self):
        """Test that conflicting commands are rejected."""
        registry = PluginCommandRegistry()
        
        # Register first command
        metadata1 = CommandMetadata(
            command="/conflict",
            natural_language_equivalent="action one",
            plugin_id="plugin1",
            description="First plugin",
            category=CommandCategory.CUSTOM
        )
        success1 = registry.register_command(metadata1)
        assert success1 is True
        
        # Try to register conflicting command
        metadata2 = CommandMetadata(
            command="/conflict",
            natural_language_equivalent="action two",
            plugin_id="plugin2",
            description="Second plugin",
            category=CommandCategory.CUSTOM
        )
        success2 = registry.register_command(metadata2)
        assert success2 is False  # Should be rejected
    
    def test_invalid_command_format(self):
        """Test that invalid command formats are rejected."""
        registry = PluginCommandRegistry()
        
        # Missing slash
        with pytest.raises(ValueError):
            metadata = CommandMetadata(
                command="invalid",
                natural_language_equivalent="test",
                plugin_id="test",
                description="Invalid",
                category=CommandCategory.CUSTOM
            )
            registry.register_command(metadata)
        
        # Too short
        with pytest.raises(ValueError):
            metadata = CommandMetadata(
                command="/",
                natural_language_equivalent="test",
                plugin_id="test",
                description="Invalid",
                category=CommandCategory.CUSTOM
            )
            registry.register_command(metadata)


class TestCommandExpansion:
    """Test command expansion to natural language."""
    
    def test_expand_registered_command(self):
        """Test expanding a registered command."""
        registry = PluginCommandRegistry()
        
        metadata = CommandMetadata(
            command="/deploy",
            natural_language_equivalent="deploy to production",
            plugin_id="deploy_plugin",
            description="Deploy",
            category=CommandCategory.WORKFLOW
        )
        registry.register_command(metadata)
        
        expanded = registry.expand_command("/deploy")
        assert expanded == "deploy to production"
    
    def test_expand_alias(self):
        """Test expanding an alias command."""
        registry = PluginCommandRegistry()
        
        metadata = CommandMetadata(
            command="/windows",
            natural_language_equivalent="switched to windows",
            plugin_id="platform",
            description="Switch to Windows",
            category=CommandCategory.PLATFORM,
            aliases=["/win"]
        )
        registry.register_command(metadata)
        
        # Both should expand to same natural language
        assert registry.expand_command("/windows") == "switched to windows"
        assert registry.expand_command("/win") == "switched to windows"
    
    def test_expand_non_command_returns_none(self):
        """Test that non-commands return None."""
        registry = PluginCommandRegistry()
        
        expanded = registry.expand_command("not a command")
        assert expanded is None
        
        expanded = registry.expand_command("switched to mac")
        assert expanded is None  # Natural language, not command
    
    def test_expand_with_whitespace(self):
        """Test command expansion with whitespace."""
        registry = PluginCommandRegistry()
        
        metadata = CommandMetadata(
            command="/test",
            natural_language_equivalent="run tests",
            plugin_id="test",
            description="Test",
            category=CommandCategory.TESTING
        )
        registry.register_command(metadata)
        
        # Should handle whitespace
        assert registry.expand_command("  /test  ") == "run tests"


class TestCommandQuery:
    """Test querying commands from registry."""
    
    def test_get_command_metadata(self):
        """Test retrieving command metadata."""
        registry = PluginCommandRegistry()
        
        metadata = CommandMetadata(
            command="/query",
            natural_language_equivalent="search knowledge",
            plugin_id="query_plugin",
            description="Query knowledge base",
            category=CommandCategory.DOCUMENTATION
        )
        registry.register_command(metadata)
        
        retrieved = registry.get_command_metadata("/query")
        assert retrieved is not None
        assert retrieved.command == "/query"
        assert retrieved.plugin_id == "query_plugin"
    
    def test_get_plugin_commands(self):
        """Test getting all commands for a plugin."""
        registry = PluginCommandRegistry()
        
        # Register multiple commands for same plugin
        for i in range(3):
            metadata = CommandMetadata(
                command=f"/cmd{i}",
                natural_language_equivalent=f"action {i}",
                plugin_id="multi_plugin",
                description=f"Command {i}",
                category=CommandCategory.CUSTOM
            )
            registry.register_command(metadata)
        
        commands = registry.get_plugin_commands("multi_plugin")
        assert len(commands) == 3
        assert all(cmd.plugin_id == "multi_plugin" for cmd in commands)
    
    def test_get_commands_by_category(self):
        """Test getting commands by category."""
        registry = PluginCommandRegistry()
        
        # Register commands in different categories
        platform_cmd = CommandMetadata(
            command="/plat1",
            natural_language_equivalent="platform action",
            plugin_id="plat",
            description="Platform",
            category=CommandCategory.PLATFORM
        )
        testing_cmd = CommandMetadata(
            command="/test1",
            natural_language_equivalent="test action",
            plugin_id="test",
            description="Testing",
            category=CommandCategory.TESTING
        )
        
        registry.register_command(platform_cmd)
        registry.register_command(testing_cmd)
        
        platform_cmds = registry.get_commands_by_category(CommandCategory.PLATFORM)
        testing_cmds = registry.get_commands_by_category(CommandCategory.TESTING)
        
        assert len(platform_cmds) > 0
        assert len(testing_cmds) > 0
        assert all(cmd.category == CommandCategory.PLATFORM for cmd in platform_cmds)
    
    def test_get_all_commands(self):
        """Test getting all commands."""
        registry = PluginCommandRegistry()
        
        all_commands = registry.get_all_commands()
        assert len(all_commands) > 0  # Has at least core commands
        
        # Should not include duplicate aliases
        command_strings = [cmd.command for cmd in all_commands]
        assert len(command_strings) == len(set(command_strings))


class TestHelpGeneration:
    """Test help text generation."""
    
    def test_generate_help_all_commands(self):
        """Test generating help for all commands."""
        registry = PluginCommandRegistry()
        
        help_text = registry.generate_help_text()
        
        assert "Available CORTEX Commands" in help_text
        assert "Commands are shortcuts" in help_text
        assert "/help" in help_text  # Core command
    
    def test_generate_help_by_category(self):
        """Test generating help for specific category."""
        registry = PluginCommandRegistry()
        
        help_text = registry.generate_help_text(category=CommandCategory.PLATFORM)
        
        assert "Platform Commands" in help_text
        # Should not include other categories
    
    def test_help_includes_aliases(self):
        """Test that help text shows aliases."""
        registry = PluginCommandRegistry()
        
        metadata = CommandMetadata(
            command="/example",
            natural_language_equivalent="example action",
            plugin_id="example",
            description="Example command",
            category=CommandCategory.CUSTOM,
            aliases=["/ex", "/e"]
        )
        registry.register_command(metadata)
        
        help_text = registry.generate_help_text()
        
        assert "/example" in help_text
        assert "Aliases" in help_text or "/ex" in help_text


class TestIsCommand:
    """Test command detection."""
    
    def test_is_command_registered(self):
        """Test detecting registered commands."""
        registry = PluginCommandRegistry()
        
        assert registry.is_command("/help") is True
        assert registry.is_command("/resume") is True
    
    def test_is_command_not_registered(self):
        """Test detecting non-commands."""
        registry = PluginCommandRegistry()
        
        assert registry.is_command("/nonexistent") is False
        assert registry.is_command("not a command") is False
        assert registry.is_command("switched to mac") is False
    
    def test_is_command_with_whitespace(self):
        """Test command detection with whitespace."""
        registry = PluginCommandRegistry()
        
        assert registry.is_command("  /help  ") is True


class TestRegistryStats:
    """Test registry statistics."""
    
    def test_stats_after_registrations(self):
        """Test stats reflect registrations."""
        registry = PluginCommandRegistry()
        
        initial_stats = registry.get_stats()
        initial_count = initial_stats['total_commands']
        
        # Register new command
        metadata = CommandMetadata(
            command="/newcmd",
            natural_language_equivalent="new action",
            plugin_id="new_plugin",
            description="New command",
            category=CommandCategory.CUSTOM,
            aliases=["/nc"]
        )
        registry.register_command(metadata)
        
        new_stats = registry.get_stats()
        
        # Should have more commands (primary + alias)
        assert new_stats['total_commands'] > initial_count
        assert new_stats['unique_commands'] == initial_stats['unique_commands'] + 1


class TestPlatformSwitchCommands:
    """Test platform switch plugin commands (integration test)."""
    
    def test_platform_commands_registered(self):
        """Test that platform commands are available."""
        registry = get_command_registry()
        
        # Platform switch commands should be registered by plugin
        # Note: This test may fail if plugin hasn't been initialized yet
        # In real usage, plugins register commands during __init__
        
        platform_commands = registry.get_commands_by_category(CommandCategory.PLATFORM)
        assert len(platform_commands) > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
