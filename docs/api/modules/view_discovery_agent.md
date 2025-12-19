# view_discovery_agent

View Discovery Agent - Issue #3 Fix (P0)
Purpose: Discover element IDs from Razor/Blazor views before test generation
Created: 2025-11-23
Author: Asif Hussain

This agent addresses the critical gap in TDD workflow where tests were generated
with assumed selectors instead of discovered element IDs, causing immediate failures.


## Table of Contents

### Classes
- [ElementMapping](#elementmapping)
- [NavigationFlow](#navigationflow)
- [ViewDiscoveryAgent](#viewdiscoveryagent)

### Functions
- [discover_views_for_testing](#discover_views_for_testing)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, json, pathlib, re, sqlite3, src, typing


## Classes

### ElementMapping

```python
class ElementMapping
```

**Decorators:** `dataclass`

Represents a discovered UI element.


**Attributes:**

- `element_id`: Optional[str]
- `element_type`: str
- `data_testid`: Optional[str]
- `css_classes`: List[str]
- `user_facing_text`: Optional[str]
- `selector_strategy`: str
- `file_path`: str
- `line_number`: int
- `attributes`: Dict[str, str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for JSON serialization.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### NavigationFlow

```python
class NavigationFlow
```

**Decorators:** `dataclass`

Represents a discovered navigation path.


**Attributes:**

- `flow_name`: str
- `route`: str
- `component_name`: str
- `element_mappings`: List[ElementMapping]
- `requires_auth`: bool
- `parent_components`: List[str]



---

### ViewDiscoveryAgent

```python
class ViewDiscoveryAgent
```

Discovers element IDs and structure from Razor/Blazor views.

Capabilities:
1. Parse Razor files for element IDs and data-testid attributes
2. Extract button text and map to element IDs
3. Discover navigation routes (@page directives)
4. Generate selector strategies (ID > data-testid > class > text)
5. Flag components without IDs


**Methods:**

  #### `discover_views`

  ```python
  discover_views(self, view_paths: List[Path], output_path: Optional[Path], save_to_db: bool, project_name: Optional[str]) -> Dict[str, Any]
  ```

  Discover all elements from specified view files.

Args:
    view_paths: List of Razor/Blazor file paths to parse
    output_path: Optional path to save discovery results JSON
    save_to_db: Whether to save results to database (default: True)
    project_name: Project identifier for database storage
    
Returns:
    Dictionary with discovered elements and navigation flows

  **Parameters:**

  - `self`
  - `view_paths` (List[Path]): List of Razor/Blazor file paths to parse
  - `output_path` (Optional[Path]) = `None`: Optional path to save discovery results JSON
  - `save_to_db` (bool) = `True`: Whether to save results to database (default: True)
  - `project_name` (Optional[str]) = `None`: Project identifier for database storage


  **Returns:** Dict[str, Any]
    Dictionary with discovered elements and navigation flows


  #### `save_to_database`

  ```python
  save_to_database(self, project_name: str, elements: List[Dict[str, Any]]) -> bool
  ```

  Save discovered elements to Tier 2 database.

Args:
    project_name: Project identifier
    elements: List of discovered element dictionaries
    
Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `project_name` (str): Project identifier
  - `elements` (List[Dict[str, Any]]): List of discovered element dictionaries


  **Returns:** bool
    True if successful, False otherwise


  #### `load_from_database`

  ```python
  load_from_database(self, project_name: str, component_path: Optional[str]) -> List[Dict[str, Any]]
  ```

  Load previously discovered elements from database.

Args:
    project_name: Project identifier
    component_path: Optional specific component path filter
    
Returns:
    List of element dictionaries

  **Parameters:**

  - `self`
  - `project_name` (str): Project identifier
  - `component_path` (Optional[str]) = `None`: Optional specific component path filter


  **Returns:** List[Dict[str, Any]]
    List of element dictionaries



---

## Functions

### discover_views_for_testing

```python
discover_views_for_testing(view_directory: Path, pattern: str, output_file: Optional[Path]) -> Dict[str, Any]
```

Convenience function to discover all views in a directory.

Args:
    view_directory: Directory containing Razor/Blazor files
    pattern: File pattern to match (default: *.razor)
    output_file: Optional JSON output file path
    
Returns:
    Discovery results dictionary


**Parameters:**

- `view_directory` (Path): Directory containing Razor/Blazor files
- `pattern` (str) = `'*.razor'`: File pattern to match (default: *.razor)
- `output_file` (Optional[Path]) = `None`: Optional JSON output file path


**Returns:** Dict[str, Any]
  Discovery results dictionary


---
