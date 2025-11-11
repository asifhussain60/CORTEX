"""
CORTEX Plugin Command Registry

Extensible system for plugins to register slash commands and natural language aliases.
Enables /command shortcuts while maintaining natural language as primary interface.

Design Principles:
- Plugin-driven: Each plugin declares its own commands
- No conflicts: Automatic detection and resolution
- Discoverable: Auto-generated help and command listing
- Scalable: O(1) lookup performance even with 100+ commands

Architecture:
    Plugin → CommandMetadata → Registry → Router

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CommandCategory(Enum):
    """Command categories for organization and help display"""
    PLATFORM = "platform"          # Platform/environment management
    WORKFLOW = "workflow"          # Task/workflow control
    SESSION = "session"            # Session/conversation management
    DOCUMENTATION = "documentation"  # Docs and help
    TESTING = "testing"            # Test execution
    MAINTENANCE = "maintenance"    # Cleanup, optimization
    EXTENSION = "extension"        # Extension management
    CUSTOM = "custom"              # User-defined


@dataclass
class CommandMetadata:
    """
    Metadata for a plugin command.
    
    Example:
        CommandMetadata(
            command="/mac",
            natural_language_equivalent="switched to mac",
            plugin_id="platform_switch",
            description="Switch to macOS development environment",
            category=CommandCategory.PLATFORM,
            aliases=["/macos", "/darwin"],
            examples=["@cortex /mac", "switched to mac"],
            requires_online=False
        )
    """
    command: str                              # Slash command (e.g., "/mac")
    natural_language_equivalent: str          # Expanded to this before routing
    plugin_id: str                            # Which plugin handles this
    description: str                          # Help text
    category: CommandCategory                 # For organization
    aliases: List[str] = field(default_factory=list)  # Alternative commands
    examples: List[str] = field(default_factory=list)  # Usage examples
    requires_online: bool = False             # Needs brain connection?
    parameters: Optional[Dict[str, str]] = None  # Future: command arguments


class PluginCommandRegistry:
    """
    Central registry for all plugin commands.
    
    Features:
    - Automatic conflict detection
    - O(1) command lookup
    - Auto-generated help text
    - Plugin discovery
    
    Usage:
        registry = PluginCommandRegistry()
        
        # Plugin registers commands during initialization
        registry.register_command(CommandMetadata(
            command="/mac",
            natural_language_equivalent="switched to mac",
            plugin_id="platform_switch",
            ...
        ))
        
        # Router expands commands
        expanded = registry.expand_command("/mac")
        # → "switched to mac"
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._commands: Dict[str, CommandMetadata] = {}  # command → metadata
        self._plugin_commands: Dict[str, List[str]] = {}  # plugin_id → [commands]
        self._category_commands: Dict[CommandCategory, List[str]] = {}  # category → [commands]
        self._all_command_strings: Set[str] = set()  # Fast membership check
        
        # Register core CORTEX commands (not plugin-specific)
        self._register_core_commands()
    
    def _register_core_commands(self):
        """Register built-in CORTEX commands that aren't plugin-specific."""
        core_commands = [
            CommandMetadata(
                command="/help",
                natural_language_equivalent="show me all available commands",
                plugin_id="core",
                description="Show all available commands and help",
                category=CommandCategory.DOCUMENTATION,
                aliases=["/h", "/?"],
                examples=["@cortex /help", "/help"]
            ),
            CommandMetadata(
                command="/status",
                natural_language_equivalent="show progress",
                plugin_id="core",
                description="Show current work status and progress",
                category=CommandCategory.SESSION,
                aliases=["/progress"],
                examples=["@cortex /status", "status"]
            ),
            CommandMetadata(
                command="/resume",
                natural_language_equivalent="resume work",
                plugin_id="core",
                description="Resume from where you left off",
                category=CommandCategory.SESSION,
                aliases=["/continue"],
                examples=["@cortex /resume", "resume"]
            ),
        ]
        
        for cmd in core_commands:
            self._register_command_internal(cmd)
    
    def register_command(self, metadata: CommandMetadata) -> bool:
        """
        Register a plugin command.
        
        Args:
            metadata: Command metadata from plugin
        
        Returns:
            True if registered successfully, False if conflict detected
        
        Raises:
            ValueError: If command format is invalid
        """
        # Validate command format
        if not metadata.command.startswith('/'):
            raise ValueError(f"Command must start with /: {metadata.command}")
        
        if len(metadata.command) < 2:
            raise ValueError(f"Command too short: {metadata.command}")
        
        # Check for conflicts
        if metadata.command in self._commands:
            existing = self._commands[metadata.command]
            logger.error(
                f"Command conflict: {metadata.command} already registered by "
                f"{existing.plugin_id} (attempted by {metadata.plugin_id})"
            )
            return False
        
        # Check alias conflicts
        for alias in metadata.aliases:
            if alias in self._all_command_strings:
                logger.warning(
                    f"Alias conflict: {alias} already exists. Skipping alias."
                )
                metadata.aliases.remove(alias)
        
        return self._register_command_internal(metadata)
    
    def _register_command_internal(self, metadata: CommandMetadata) -> bool:
        """Internal registration (no conflict checks)."""
        # Register primary command
        self._commands[metadata.command] = metadata
        self._all_command_strings.add(metadata.command)
        
        # Register aliases
        for alias in metadata.aliases:
            self._commands[alias] = metadata
            self._all_command_strings.add(alias)
        
        # Track by plugin
        if metadata.plugin_id not in self._plugin_commands:
            self._plugin_commands[metadata.plugin_id] = []
        self._plugin_commands[metadata.plugin_id].append(metadata.command)
        
        # Track by category
        if metadata.category not in self._category_commands:
            self._category_commands[metadata.category] = []
        self._category_commands[metadata.category].append(metadata.command)
        
        logger.info(
            f"✓ Registered command: {metadata.command} → {metadata.plugin_id}"
        )
        return True
    
    def expand_command(self, user_input: str) -> Optional[str]:
        """
        Expand slash command to natural language.
        
        Args:
            user_input: Raw user input (might be command or natural language)
        
        Returns:
            Natural language equivalent, or None if not a command
        
        Example:
            expand_command("/mac") → "switched to mac"
            expand_command("switched to mac") → None (already natural language)
        """
        stripped = user_input.strip()
        
        # Check if it's a registered command
        if stripped in self._commands:
            metadata = self._commands[stripped]
            logger.debug(
                f"Expanding command: {stripped} → {metadata.natural_language_equivalent}"
            )
            return metadata.natural_language_equivalent
        
        # Not a command, pass through as-is
        return None
    
    def get_command_metadata(self, command: str) -> Optional[CommandMetadata]:
        """
        Get metadata for a command.
        
        Args:
            command: Command string (e.g., "/mac")
        
        Returns:
            CommandMetadata if found, None otherwise
        """
        return self._commands.get(command)
    
    def get_plugin_commands(self, plugin_id: str) -> List[CommandMetadata]:
        """
        Get all commands registered by a plugin.
        
        Args:
            plugin_id: Plugin identifier
        
        Returns:
            List of CommandMetadata objects
        """
        command_strings = self._plugin_commands.get(plugin_id, [])
        return [self._commands[cmd] for cmd in command_strings]
    
    def get_all_commands(self) -> List[CommandMetadata]:
        """
        Get all registered commands.
        
        Returns:
            List of all CommandMetadata objects (deduplicated)
        """
        # Return only primary commands (not aliases)
        seen = set()
        commands = []
        
        for cmd, metadata in self._commands.items():
            if metadata.command not in seen:
                commands.append(metadata)
                seen.add(metadata.command)
        
        return commands
    
    def get_commands_by_category(self, category: CommandCategory) -> List[CommandMetadata]:
        """
        Get commands in a category.
        
        Args:
            category: CommandCategory enum value
        
        Returns:
            List of CommandMetadata objects in that category
        """
        command_strings = self._category_commands.get(category, [])
        return [self._commands[cmd] for cmd in command_strings]
    
    def generate_help_text(self, category: Optional[CommandCategory] = None) -> str:
        """
        Generate formatted help text for commands.
        
        Args:
            category: Optional category to filter by
        
        Returns:
            Markdown-formatted help text
        """
        if category:
            commands = self.get_commands_by_category(category)
            title = f"# {category.value.title()} Commands\n\n"
        else:
            commands = self.get_all_commands()
            title = "# Available CORTEX Commands\n\n"
        
        if not commands:
            return title + "*No commands available*\n"
        
        # Group by category
        by_category: Dict[CommandCategory, List[CommandMetadata]] = {}
        for cmd in commands:
            if cmd.category not in by_category:
                by_category[cmd.category] = []
            by_category[cmd.category].append(cmd)
        
        # Build help text
        help_text = title
        help_text += "*Commands are shortcuts. Natural language works everywhere!*\n\n"
        
        for cat, cmds in sorted(by_category.items(), key=lambda x: x[0].value):
            help_text += f"## {cat.value.title()}\n\n"
            
            for cmd_meta in sorted(cmds, key=lambda x: x.command):
                help_text += f"**`{cmd_meta.command}`** - {cmd_meta.description}\n"
                
                if cmd_meta.aliases:
                    aliases_str = ", ".join(f"`{a}`" for a in cmd_meta.aliases)
                    help_text += f"  *Aliases: {aliases_str}*\n"
                
                if cmd_meta.examples:
                    help_text += f"  *Example: {cmd_meta.examples[0]}*\n"
                
                help_text += "\n"
        
        return help_text
    
    def is_command(self, user_input: str) -> bool:
        """
        Check if user input is a registered command.
        
        Args:
            user_input: Raw user input
        
        Returns:
            True if it's a registered command
        """
        return user_input.strip() in self._all_command_strings
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with registry stats
        """
        return {
            'total_commands': len(self._all_command_strings),
            'unique_commands': len(set(m.command for m in self._commands.values())),
            'total_plugins': len(self._plugin_commands),
            'categories': len(self._category_commands)
        }


# Global singleton instance
_registry_instance: Optional[PluginCommandRegistry] = None


def get_command_registry() -> PluginCommandRegistry:
    """
    Get global command registry instance (singleton).
    
    Returns:
        PluginCommandRegistry singleton
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = PluginCommandRegistry()
    return _registry_instance
