# operation_factory

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


## Table of Contents

### Classes
- [OperationFactory](#operationfactory)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** importlib, logging, pathlib, src, typing, yaml


## Classes

### OperationFactory

```python
class OperationFactory
```

Factory for creating operation orchestrators from YAML configuration.

Loads cortex-operations.yaml and provides methods to:
    - Discover available operations
    - Load operation definitions
    - Instantiate module classes
    - Create orchestrators ready for execution

Example Usage:
    factory = OperationFactory()
    
    ops = factory.get_available_operations()
    # ['environment_setup', 'refresh_cortex_story', 'workspace_cleanup', ...]
    
    orchestrator = factory.create_operation('refresh_cortex_story')
    report = orchestrator.execute_operation(context={'project_root': Path('...')})


**Methods:**

  #### `get_available_operations`

  ```python
  get_available_operations(self) -> List[str]
  ```

  Get list of available operation IDs.

Returns:
    List of operation IDs (e.g., ['environment_setup', 'refresh_cortex_story'])

  **Parameters:**

  - `self`


  **Returns:** List[str]
    List of operation IDs (e.g., ['environment_setup', 'refresh_cortex_story'])


  #### `get_operation_info`

  ```python
  get_operation_info(self, operation_id: str) -> Optional[Dict[str, Any]]
  ```

  Get information about an operation.

Args:
    operation_id: Operation identifier

Returns:
    Operation configuration dict, or None if not found

  **Parameters:**

  - `self`
  - `operation_id` (str): Operation identifier


  **Returns:** Optional[Dict[str, Any]]
    Operation configuration dict, or None if not found


  #### `create_operation`

  ```python
  create_operation(self, operation_id: str, profile: str, context: Optional[Dict[str, Any]]) -> Optional[OperationsOrchestrator]
  ```

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

  **Parameters:**

  - `self`
  - `operation_id` (str): Operation identifier (e.g., 'refresh_cortex_story')
  - `profile` (str) = `'standard'`: Profile to use (minimal/standard/full)
  - `context` (Optional[Dict[str, Any]]) = `None`: Initial context dictionary


  **Returns:** Optional[OperationsOrchestrator]
    Configured orchestrator, or None if operation not found


  #### `list_operation_modules`

  ```python
  list_operation_modules(self, operation_id: str, profile: str) -> List[str]
  ```

  List modules for an operation without creating orchestrator.

Args:
    operation_id: Operation identifier
    profile: Profile name

Returns:
    List of module IDs

  **Parameters:**

  - `self`
  - `operation_id` (str): Operation identifier
  - `profile` (str) = `'standard'`: Profile name


  **Returns:** List[str]
    List of module IDs


  #### `get_natural_language_mappings`

  ```python
  get_natural_language_mappings(self) -> Dict[str, str]
  ```

  Get natural language → operation ID mappings.

Returns:
    Dict mapping natural language phrases to operation IDs

Example:
    {'refresh story': 'refresh_cortex_story',
     'cleanup': 'workspace_cleanup'}

  **Parameters:**

  - `self`


  **Returns:** Dict[str, str]
    Dict mapping natural language phrases to operation IDs


  #### `find_operation_by_input`

  ```python
  find_operation_by_input(self, user_input: str) -> Optional[str]
  ```

  Find operation ID by user input (natural language or slash command).

Args:
    user_input: User's input text

Returns:
    Operation ID if found, None otherwise

Example:
    factory.find_operation_by_input("refresh story") → 'refresh_cortex_story'
    factory.find_operation_by_input("/CORTEX, cleanup") → 'workspace_cleanup'

  **Parameters:**

  - `self`
  - `user_input` (str): User's input text


  **Returns:** Optional[str]
    Operation ID if found, None otherwise



---
