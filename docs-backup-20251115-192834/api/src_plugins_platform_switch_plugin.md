# src.plugins.platform_switch_plugin

CORTEX Platform Switch Plugin

Handles automatic platform detection and configuration when switching between
development environments (Mac/Windows/Linux).

Features:
- Automatic platform detection on startup
- Stores last known platform to detect changes
- Auto-configures environment when platform changes
- Manual /setup command for forced reconfiguration

Usage:
    - Automatic: Opens CORTEX on different platform → auto-detects and configures
    - Manual: "setup environment" or /setup → forces reconfiguration

## Functions

### `register()`

Register the platform switch plugin.
