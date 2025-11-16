# src.operations.help_command

CORTEX Help Command - Display Available Operations

Provides concise, user-friendly display of all CORTEX operations with:
    - Quick command reference
    - Natural language examples
    - Implementation status
    - Underlying orchestration modules

Author: Asif Hussain
Version: 1.0

## Functions

### `show_help(format)`

Convenience function to display CORTEX help.

Args:
    format: Output format ('table', 'list', 'detailed')

Returns:
    Formatted help text

Example:
    print(show_help())
    print(show_help('detailed'))

### `find_command(command)`

Find operation by command.

Args:
    command: Command string to search for

Returns:
    Operation data dictionary

Example:
    op = find_command('setup')
    print(f"Operation: {op['operation_id']}")
