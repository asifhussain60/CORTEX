# dependency_graph_generator

Dependency Graph Generator - Visualize module dependencies.

Generates dependency graphs in Mermaid and DOT formats using
AST analysis of import relationships.


## Table of Contents

### Classes
- [DependencyNode](#dependencynode)
- [DependencyGraphGenerator](#dependencygraphgenerator)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, json, logging, pathlib, typing


## Classes

### DependencyNode

```python
class DependencyNode
```

**Decorators:** `dataclass`

Node in dependency graph.


**Attributes:**

- `name`: str
- `type`: str
- `file_path`: str
- `dependencies`: List[str]



---

### DependencyGraphGenerator

```python
class DependencyGraphGenerator
```

Generate visual dependency graphs.


**Methods:**

  #### `generate_module_graph`

  ```python
  generate_module_graph(self, target_path: Path, format: str) -> str
  ```

  Generate module-level dependency graph.

Args:
    target_path: Specific directory or None for full project
    format: Output format ("mermaid", "dot", "json")
    
Returns:
    Graph representation in specified format
    
Raises:
    ValueError: If format is not supported

  **Parameters:**

  - `self`
  - `target_path` (Path) = `None`: Specific directory or None for full project
  - `format` (str) = `'mermaid'`: Output format ("mermaid", "dot", "json")


  **Returns:** str
    Graph representation in specified format


  #### `detect_circular_dependencies`

  ```python
  detect_circular_dependencies(self) -> str
  ```

  Generate visualization highlighting circular dependencies.

Returns:
    Mermaid graph with circular deps highlighted in red

  **Parameters:**

  - `self`


  **Returns:** str
    Mermaid graph with circular deps highlighted in red



---
