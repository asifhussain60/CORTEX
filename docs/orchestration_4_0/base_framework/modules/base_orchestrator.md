# base_orchestrator

Base Orchestrator for CORTEX 4.0

Provides template method pattern for all orchestrators with:
- Phase management
- Error handling
- Lifecycle hooks
- Dependency injection integration
- Progress tracking


## Table of Contents

### Classes
- [BaseOrchestrator](#baseorchestrator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** abc, datetime, error_handler, logging, phase_manager, typing


## Classes

### BaseOrchestrator

```python
class BaseOrchestrator(ABC)
```

Abstract base class for all CORTEX 4.0 orchestrators.

Template Method Pattern:
1. _setup() - Initialize orchestrator-specific resources
2. _register_phases() - Define phases for this orchestrator
3. _execute_phase(phase_name) - Execute a single phase
4. _teardown() - Cleanup resources

Subclasses must implement these methods.


**Methods:**

  #### `execute`

  ```python
  execute(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]
  ```

  Main execution entry point (Template Method).

Orchestrates the full workflow:
1. Setup
2. Register phases
3. Execute phases in order
4. Handle errors
5. Teardown

Args:
    context: Execution context data
    
Returns:
    Execution result dictionary
    
Raises:
    RuntimeError: If orchestrator already running or critical error occurs

  **Parameters:**

  - `self`
  - `context` (Optional[Dict[str, Any]]) = `None`: Execution context data


  **Returns:** Dict[str, Any]
    Execution result dictionary


  #### `get_status`

  ```python
  get_status(self) -> Dict[str, Any]
  ```

  Get current orchestrator status.

Returns:
    Dictionary with status information

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with status information



---
