# architecture_diagram_generator

Architecture Diagram Generator - Visualize system architecture.

Generates architecture diagrams showing layers, components, and
their relationships.


## Table of Contents

### Classes
- [ArchitectureDiagramGenerator](#architecturediagramgenerator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, typing


## Classes

### ArchitectureDiagramGenerator

```python
class ArchitectureDiagramGenerator
```

Generate architecture diagrams.


**Methods:**

  #### `generate_layer_diagram`

  ```python
  generate_layer_diagram(self) -> str
  ```

  Generate layered architecture diagram.

Returns:
    Mermaid diagram showing architectural layers

  **Parameters:**

  - `self`


  **Returns:** str
    Mermaid diagram showing architectural layers


  #### `generate_component_diagram`

  ```python
  generate_component_diagram(self, component: str) -> str
  ```

  Generate detailed component diagram.

Args:
    component: Component name (e.g., "planning_orchestrator")
    
Returns:
    Mermaid diagram showing component internals

  **Parameters:**

  - `self`
  - `component` (str): Component name (e.g., "planning_orchestrator")


  **Returns:** str
    Mermaid diagram showing component internals



---
