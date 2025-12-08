# CORTEX Plugin System

This diagram shows CORTEX's extensible plugin architecture.

**CORTEX Core** provides base functionality (routing, memory, operations).

**Plugin Registry** discovers and manages all available plugins dynamically.

**Plugins** extend CORTEX with specialized capabilities (database crawlers, platform switchers, report generators).

Each plugin registers itself on initialization, exposing commands and operations to the core system. This decoupled architecture enables adding new features without modifying core code.

Users can build custom plugins by implementing the plugin interface and dropping them in the plugins directory - CORTEX discovers them automatically.