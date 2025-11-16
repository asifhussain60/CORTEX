# src.entry_point.cortex_entry

CORTEX Main Entry Point

This module provides the unified entry point for all CORTEX interactions.
It coordinates request parsing, agent routing, and response formatting.

Usage:
    from src.entry_point import CortexEntry
    
    entry = CortexEntry()
    response = entry.process("Add authentication to the login page")
    print(response)

CORTEX 2.0 Implementation Requirement:
    After completing any work (tests, features, refactoring), ALWAYS update:
    cortex-brain/cortex-2.0-design/IMPLEMENTATION-STATUS-CHECKLIST.md
    
    This is tracked automatically via _remind_checklist_update() method.
