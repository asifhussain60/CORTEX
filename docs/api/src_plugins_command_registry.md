# src.plugins.command_registry

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

## Functions

### `get_command_registry()`

Get global command registry instance (singleton).

Returns:
    PluginCommandRegistry singleton
