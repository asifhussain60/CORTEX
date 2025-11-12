"""
CORTEX Router Command Expansion Tests

Tests for slash command expansion in the router before intent detection.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plugins.command_registry import CommandMetadata, CommandCategory, PluginCommandRegistry


class TestRouterCommandExpansion:
    """Test router command expansion integration."""
    
    @pytest.fixture
    def mock_router(self):
        """Create mock router with command registry."""
        try:
            # Try to import router - skip tests if not available
            from router import CortexRouter
            with patch('src.router.IntentRouter'), \
                 patch('src.router.SessionManager'), \
                 patch('src.router.ContextInjector'):
                return CortexRouter(db_path=":memory:")
        except (ImportError, AttributeError):
            pytest.skip("Router module not yet implemented")
    
    def test_slash_command_expanded_before_routing(self, mock_router):
        """Test that slash commands are expanded before intent detection."""
        # Register test command
        mock_router.command_registry.register_command(
            CommandMetadata(
                command="/testcmd",
                natural_language_equivalent="test action",
                plugin_id="test",
                description="Test",
                category=CommandCategory.TESTING
            )
        )
        
        # Mock intent router to verify expansion
        with patch.object(mock_router.intent_router, 'route_request') as mock_route:
            mock_route.return_value = {
                'intent': 'TEST',
                'confidence': 0.95
            }
            
            # Process slash command
            result = mock_router.process_request("/testcmd")
            
            # Verify router received expanded natural language, not slash command
            mock_route.assert_called_once()
            call_args = mock_route.call_args[0][0]
            assert call_args == "test action"
            assert result['command_used'] == "/testcmd"
    
    def test_natural_language_passes_through(self, mock_router):
        """Test that natural language bypasses command expansion."""
        with patch.object(mock_router.intent_router, 'route_request') as mock_route:
            mock_route.return_value = {
                'intent': 'PLAN',
                'confidence': 0.90
            }
            
            # Process natural language
            natural_request = "add a feature"
            result = mock_router.process_request(natural_request)
            
            # Verify it was passed through unchanged
            mock_route.assert_called_once_with(natural_request)
            assert result['command_used'] is None
    
    def test_unknown_slash_command_passes_through(self, mock_router):
        """Test that unknown slash commands pass through unchanged."""
        with patch.object(mock_router.intent_router, 'route_request') as mock_route:
            mock_route.return_value = {
                'intent': 'ASK',
                'confidence': 0.60
            }
            
            # Process unknown command
            result = mock_router.process_request("/unknown")
            
            # Should pass through as-is (not expanded)
            mock_route.assert_called_once_with("/unknown")
            assert result['command_used'] is None


class TestCommandAliasExpansion:
    """Test that command aliases expand correctly."""
    
    def test_primary_and_alias_expand_identically(self):
        """Test that primary command and alias expand to same natural language."""
        registry = PluginCommandRegistry()
        
        registry.register_command(
            CommandMetadata(
                command="/primary",
                natural_language_equivalent="the action",
                plugin_id="test",
                description="Test",
                category=CommandCategory.CUSTOM,
                aliases=["/p", "/pri"]
            )
        )
        
        # All should expand to same natural language
        assert registry.expand_command("/primary") == "the action"
        assert registry.expand_command("/p") == "the action"
        assert registry.expand_command("/pri") == "the action"


class TestPlatformCommandExpansion:
    """Test platform switch command expansions."""
    
    def test_mac_command_expansion(self):
        """Test /mac expands correctly."""
        registry = PluginCommandRegistry()
        
        registry.register_command(
            CommandMetadata(
                command="/mac",
                natural_language_equivalent="switched to mac",
                plugin_id="platform_switch",
                description="Switch to Mac",
                category=CommandCategory.PLATFORM,
                aliases=["/macos", "/darwin"]
            )
        )
        
        assert registry.expand_command("/mac") == "switched to mac"
        assert registry.expand_command("/macos") == "switched to mac"
        assert registry.expand_command("/darwin") == "switched to mac"
    
    def test_windows_command_expansion(self):
        """Test /windows expands correctly."""
        registry = PluginCommandRegistry()
        
        registry.register_command(
            CommandMetadata(
                command="/windows",
                natural_language_equivalent="switched to windows",
                plugin_id="platform_switch",
                description="Switch to Windows",
                category=CommandCategory.PLATFORM,
                aliases=["/win"]
            )
        )
        
        assert registry.expand_command("/windows") == "switched to windows"
        assert registry.expand_command("/win") == "switched to windows"
    
    def test_setup_command_expansion(self):
        """Test /setup expands correctly."""
        registry = PluginCommandRegistry()
        
        registry.register_command(
            CommandMetadata(
                command="/setup",
                natural_language_equivalent="setup environment",
                plugin_id="platform_switch",
                description="Setup environment",
                category=CommandCategory.PLATFORM,
                aliases=["/env"]
            )
        )
        
        assert registry.expand_command("/setup") == "setup environment"
        assert registry.expand_command("/env") == "setup environment"


class TestCommandExpansionPerformance:
    """Test that command expansion is fast."""
    
    def test_expansion_is_fast(self):
        """Test that command expansion meets performance target."""
        import time
        
        registry = PluginCommandRegistry()
        
        # Register many commands
        for i in range(100):
            registry.register_command(
                CommandMetadata(
                    command=f"/cmd{i}",
                    natural_language_equivalent=f"action {i}",
                    plugin_id="perf_test",
                    description=f"Command {i}",
                    category=CommandCategory.CUSTOM
                )
            )
        
        # Test lookup performance
        start = time.perf_counter()
        for _ in range(1000):
            registry.expand_command("/cmd50")
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        # Should be fast (< 5ms for 1000 lookups)
        assert elapsed_ms < 5.0
    
    def test_is_command_is_fast(self):
        """Test that command detection is O(1)."""
        import time
        
        registry = PluginCommandRegistry()
        
        # Register many commands
        for i in range(100):
            registry.register_command(
                CommandMetadata(
                    command=f"/cmd{i}",
                    natural_language_equivalent=f"action {i}",
                    plugin_id="perf_test",
                    description=f"Command {i}",
                    category=CommandCategory.CUSTOM
                )
            )
        
        # Test detection performance
        start = time.perf_counter()
        for _ in range(1000):
            registry.is_command("/cmd50")
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        # Should be extremely fast
        assert elapsed_ms < 1.0


class TestCommandExpansionEdgeCases:
    """Test edge cases in command expansion."""
    
    def test_empty_string(self):
        """Test expansion of empty string."""
        registry = PluginCommandRegistry()
        assert registry.expand_command("") is None
    
    def test_whitespace_only(self):
        """Test expansion of whitespace."""
        registry = PluginCommandRegistry()
        assert registry.expand_command("   ") is None
    
    def test_slash_only(self):
        """Test expansion of just slash."""
        registry = PluginCommandRegistry()
        assert registry.expand_command("/") is None
    
    def test_case_sensitivity(self):
        """Test that commands are case-sensitive."""
        registry = PluginCommandRegistry()
        
        registry.register_command(
            CommandMetadata(
                command="/Test",
                natural_language_equivalent="test action",
                plugin_id="test",
                description="Test",
                category=CommandCategory.TESTING
            )
        )
        
        # Exact case should work
        assert registry.expand_command("/Test") == "test action"
        
        # Different case should not match (unless explicitly registered)
        assert registry.expand_command("/test") is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-k", "not TestRouterCommandExpansion"])  # Skip router tests that need mocking
