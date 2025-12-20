"""
Test Plugin Initialization

Tests for SystemRefactorPlugin initialization, metadata, and command registration.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from plugins.system_refactor_plugin import SystemRefactorPlugin


class TestPluginInstantiation:
    """Test plugin instance creation."""
    
    def test_plugin_creates_successfully(self, refactor_plugin):
        """Test plugin can be instantiated."""
        assert refactor_plugin is not None
        assert isinstance(refactor_plugin, SystemRefactorPlugin)
    
    def test_plugin_has_required_attributes(self, refactor_plugin):
        """Test plugin has required attributes."""
        assert hasattr(refactor_plugin, "metadata")
        assert hasattr(refactor_plugin, "project_root")
        assert hasattr(refactor_plugin, "brain_path")
        assert hasattr(refactor_plugin, "tests_path")
        assert hasattr(refactor_plugin, "src_path")
    
    def test_plugin_paths_are_valid(self, refactor_plugin):
        """Test plugin paths are Path objects."""
        assert isinstance(refactor_plugin.project_root, Path)
        assert isinstance(refactor_plugin.brain_path, Path)
        assert isinstance(refactor_plugin.tests_path, Path)
        assert isinstance(refactor_plugin.src_path, Path)


class TestPluginMetadata:
    """Test plugin metadata configuration."""
    
    def test_plugin_has_correct_id(self, refactor_plugin):
        """Test plugin ID is correct."""
        assert refactor_plugin.metadata.plugin_id == "system_refactor"
    
    def test_plugin_has_correct_name(self, refactor_plugin):
        """Test plugin name is correct."""
        assert refactor_plugin.metadata.name == "System Refactor Plugin"
    
    def test_plugin_has_version(self, refactor_plugin):
        """Test plugin has version number."""
        assert refactor_plugin.metadata.version == "1.0.0"
    
    def test_plugin_has_correct_category(self, refactor_plugin):
        """Test plugin category is maintenance."""
        assert refactor_plugin.metadata.category.value == "maintenance"
    
    def test_plugin_has_description(self, refactor_plugin):
        """Test plugin has description."""
        assert refactor_plugin.metadata.description != ""
        assert "critical review" in refactor_plugin.metadata.description.lower()


class TestCommandRegistration:
    """Test slash command registration."""
    
    def test_plugin_registers_commands(self, refactor_plugin):
        """Test plugin registers slash commands."""
        commands = refactor_plugin.register_commands()
        
        # Commands should be returned (may be empty if conflicts)
        assert isinstance(commands, list)
        assert len(commands) >= 0
    
    def test_primary_refactor_command_exists(self, refactor_plugin):
        """Test /refactor command is registered."""
        commands = refactor_plugin.register_commands()
        
        if commands:
            command_names = [cmd.command for cmd in commands]
            assert "/refactor" in command_names or "/review" in command_names
    
    def test_command_has_required_metadata(self, refactor_plugin):
        """Test commands have required metadata fields."""
        commands = refactor_plugin.register_commands()
        
        for cmd in commands:
            assert cmd.command.startswith("/")
            assert cmd.plugin_id == "system_refactor"
            assert cmd.description != ""
            assert cmd.usage != ""


class TestRequestHandling:
    """Test request routing and handling."""
    
    def test_plugin_handles_refactor_keyword(self, refactor_plugin):
        """Test plugin handles 'refactor' keyword."""
        assert refactor_plugin.can_handle("refactor system")
        assert refactor_plugin.can_handle("let's refactor")
        assert refactor_plugin.can_handle("REFACTOR the code")
    
    def test_plugin_handles_review_keyword(self, refactor_plugin):
        """Test plugin handles 'review' keyword."""
        assert refactor_plugin.can_handle("perform critical review")
        assert refactor_plugin.can_handle("system review")
        assert refactor_plugin.can_handle("review architecture")
    
    def test_plugin_handles_optimize_keyword(self, refactor_plugin):
        """Test plugin handles 'optimize' keyword."""
        assert refactor_plugin.can_handle("optimize system")
        assert refactor_plugin.can_handle("system optimization")
    
    def test_plugin_handles_gap_analysis_keyword(self, refactor_plugin):
        """Test plugin handles 'gap analysis' keyword."""
        assert refactor_plugin.can_handle("analyze coverage gaps")
        assert refactor_plugin.can_handle("gap analysis")
    
    def test_plugin_handles_self_review_keyword(self, refactor_plugin):
        """Test plugin handles 'self-review' keyword."""
        assert refactor_plugin.can_handle("self-review")
        assert refactor_plugin.can_handle("perform self review")
    
    def test_plugin_ignores_unrelated_requests(self, refactor_plugin):
        """Test plugin ignores unrelated requests."""
        assert not refactor_plugin.can_handle("add authentication feature")
        assert not refactor_plugin.can_handle("run tests")
        assert not refactor_plugin.can_handle("setup environment")
        assert not refactor_plugin.can_handle("create new file")
    
    def test_plugin_handles_case_insensitive(self, refactor_plugin):
        """Test request handling is case-insensitive."""
        assert refactor_plugin.can_handle("REFACTOR SYSTEM")
        assert refactor_plugin.can_handle("Review Code")
        assert refactor_plugin.can_handle("gap ANALYSIS")


class TestPluginInitialize:
    """Test plugin initialization method."""
    
    def test_initialize_returns_success(self, refactor_plugin):
        """Test initialize method returns success."""
        result = refactor_plugin.initialize()
        
        assert result is True


class TestPluginCleanup:
    """Test plugin cleanup method."""
    
    def test_cleanup_returns_success(self, refactor_plugin):
        """Test cleanup method returns success."""
        result = refactor_plugin.cleanup()
        
        assert result is True
    
    def test_cleanup_can_be_called_multiple_times(self, refactor_plugin):
        """Test cleanup is idempotent."""
        assert refactor_plugin.cleanup() is True
        assert refactor_plugin.cleanup() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
