# architecture_graph_builder

Architecture Graph Builder

Analyzes codebase structure and generates D3.js force-directed graph data.
Detects modules, classes, functions, and their relationships (imports, calls, inheritance).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [ArchitectureNode](#architecturenode)
- [ArchitectureEdge](#architectureedge)
- [ArchitectureGraphBuilder](#architecturegraphbuilder)

### Functions
- [generate_architecture_json](#generate_architecture_json)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** ast, dataclasses, json, logging, pathlib, typing


## Classes

### ArchitectureNode

```python
class ArchitectureNode
```

**Decorators:** `dataclass`

Represents a node in the architecture graph


**Attributes:**

- `id`: str
- `name`: str
- `type`: str
- `file_path`: str
- `layer`: Optional[str]
- `size`: int
- `metadata`: Dict[str, Any]



---

### ArchitectureEdge

```python
class ArchitectureEdge
```

**Decorators:** `dataclass`

Represents an edge (relationship) in the architecture graph


**Attributes:**

- `source`: str
- `target`: str
- `type`: str
- `weight`: int



---

### ArchitectureGraphBuilder

```python
class ArchitectureGraphBuilder
```

Builds architecture graph from codebase analysis


**Methods:**

  #### `build_graph`

  ```python
  build_graph(self, file_paths: List[Path]) -> Dict[str, Any]
  ```

  Build architecture graph from Python files
Returns D3.js compatible force-directed graph data

  **Parameters:**

  - `self`
  - `file_paths` (List[Path])


  **Returns:** Dict[str, Any]



---

## Functions

### generate_architecture_json

```python
generate_architecture_json(project_path: Path, output_path: Path) -> Dict[str, Any]
```

Generate architecture.json for a project

Args:
    project_path: Path to project to analyze
    output_path: Path to save architecture.json
    
Returns:
    Architecture graph data


**Parameters:**

- `project_path` (Path): Path to project to analyze
- `output_path` (Path): Path to save architecture.json


**Returns:** Dict[str, Any]
  Architecture graph data


---
