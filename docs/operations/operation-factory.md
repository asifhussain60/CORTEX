# Operation Factory Operation

**Auto-generated:** 2025-11-15 03:35:42

---

## Overview

Operation Factory - Load and Create Operations from YAML

This factory loads operation definitions from cortex-op                    # Convert snake_case to CamelCase, but preserve common acronyms
                    words = module_name.split('_')
                    # Preserve common acronyms in uppercase
                    acronyms = {'api': 'API', 'sql': 'SQL', 'sqlite': 'SQLite', 'html': 'HTML', 'css': 'CSS', 'json': 'JSON', 'yaml': 'YAML', 'mkdocs': 'MkDocs', 'pdf': 'PDF', 'cli': 'CLI'}
                    class_name = ''.join(
                        acronyms.get(word.lower(), word.capitalize()) 
                        for word in words
                    ).yaml and
instantiates orchestrators with the appropriate modules.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

## Usage

```python
from src.operations.operation_factory import OperationFactory

operation = OperationFactory()
result = operation.execute()
```

## Methods

### `get_available_operations(self)`

Get list of available operation IDs.

Returns:
    List of operation IDs (e.g., ['environment_setup', 'refresh_cortex_story'])

### `get_operation_info(self, operation_id)`

Get information about an operation.

Args:
    operation_id: Operation identifier

Returns:
    Operation configuration dict, or None if not found

### `create_operation(self, operation_id, profile, context)`

Create orchestrator for an operation.

Args:
    operation_id: Operation identifier (e.g., 'refresh_cortex_story')
    profile: Profile to use (minimal/standard/full)
    context: Initial context dictionary

Returns:
    Configured orchestrator, or None if operation not found

Example:
    orchestrator = factory.create_operation('refresh_cortex_story')
    if orchestrator:
        report = orchestrator.execute_operation(context={'project_root': Path('.')})

### `list_operation_modules(self, operation_id, profile)`

List modules for an operation without creating orchestrator.

Args:
    operation_id: Operation identifier
    profile: Profile name

Returns:
    List of module IDs

### `get_natural_language_mappings(self)`

Get natural language → operation ID mappings.

Returns:
    Dict mapping natural language phrases to operation IDs

Example:
    {'refresh story': 'refresh_cortex_story',
     'cleanup': 'workspace_cleanup'}

### `find_operation_by_input(self, user_input)`

Find operation ID by user input (natural language or slash command).

Args:
    user_input: User's input text

Returns:
    Operation ID if found, None otherwise

Example:
    factory.find_operation_by_input("refresh story") → 'refresh_cortex_story'
    factory.find_operation_by_input("/CORTEX, cleanup") → 'workspace_cleanup'
