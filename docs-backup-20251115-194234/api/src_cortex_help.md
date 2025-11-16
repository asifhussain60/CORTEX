# src.cortex_help

CORTEX Help System

Provides concise, bulletted command reference for easy memorization.
Shows entry point commands, slash commands, and natural language equivalents.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

## Functions

### `show_help(format, category)`

Generate help text for CORTEX commands.

Args:
    format: Display format (concise, detailed, or category)
    category: Optional category filter

Returns:
    Formatted help text

Examples:
    >>> print(show_help())  # Quick bulletted list
    >>> print(show_help(HelpFormat.DETAILED))  # Full details
    >>> print(show_help(category=CommandCategory.PLATFORM))  # Platform commands only

### `_generate_concise_help(registry, category)`

Generate concise bulletted help - easy to scan and remember.

Format:
• /command - Description
• /command (alias1, alias2) - Description

### `_generate_detailed_help(registry, category)`

Generate detailed help with examples and usage patterns.

### `_generate_category_help(registry)`

Generate help organized by category with command counts.

### `get_quick_reference()`

Get ultra-concise quick reference - just the essentials.

Perfect for chat responses when user asks "what commands are available?"

Returns:
    Ultra-concise command list

### `handle_help_request(request)`

Handle help requests intelligently based on what user asks for.

Args:
    request: User's help request

Returns:
    Appropriate help text

Examples:
    "show help" → concise help
    "detailed help" → detailed help
    "platform commands" → platform category help
    "quick reference" → ultra-concise reference

### `cortex_help()`

Quick access to concise help.
