# component_discovery_scanner

Component Discovery Scanner

Discovers existing SOLID analyzers, enforcers, and dependency graphs in CORTEX codebase.
Reports unwired components that should be integrated into TDD workflow.

Author: Asif Hussain
Date: December 5, 2025


## Table of Contents

### Classes
- [DiscoveredComponent](#discoveredcomponent)
- [ComponentDiscoveryScanner](#componentdiscoveryscanner)

### Functions
- [format_discovery_report](#format_discovery_report)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** ast, dataclasses, logging, pathlib, typing


## Classes

### DiscoveredComponent

```python
class DiscoveredComponent
```

**Decorators:** `dataclass`

Represents a discovered component with its capabilities.


**Attributes:**

- `name`: str
- `file_path`: Path
- `module_path`: str
- `capabilities`: List[str]
- `is_wired`: bool
- `potential_uses`: List[str]



---

### ComponentDiscoveryScanner

```python
class ComponentDiscoveryScanner
```

Scans CORTEX codebase for unwired architectural components.


**Methods:**

  #### `discover_components`

  ```python
  discover_components(self, cortex_root: Path) -> List[DiscoveredComponent]
  ```

  Discover all architectural components in CORTEX codebase.

Args:
    cortex_root: Root directory of CORTEX
    
Returns:
    List of discovered components

  **Parameters:**

  - `self`
  - `cortex_root` (Path): Root directory of CORTEX


  **Returns:** List[DiscoveredComponent]
    List of discovered components



---

## Functions

### format_discovery_report

```python
format_discovery_report(components: List[DiscoveredComponent]) -> Dict
```

Format discovery results for reporting.

Args:
    components: List of discovered components
    
Returns:
    Report dictionary


**Parameters:**

- `components` (List[DiscoveredComponent]): List of discovered components


**Returns:** Dict
  Report dictionary


---
