# src.plugins.base_plugin

Base Plugin System for CORTEX 2.0

Provides abstract base class and infrastructure for all CORTEX plugins.
Plugins extend CORTEX functionality without modifying core code.

Architecture:
- BasePlugin: Abstract class all plugins must inherit from
- PluginMetadata: Standardized plugin information
- Hook System: Lifecycle hooks for plugin execution
- Configuration: JSON schema validation for plugin settings

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

## Functions

### `_get_command_registry()`

Lazy import of command registry to avoid circular dependencies.
