# diagram_generator

Diagram Generator - Generate D3.js interactive diagrams

Creates interactive visualizations:
- Phase flow diagrams (orchestrator execution flow)
- Class hierarchy diagrams (inheritance structure)
- Sequence diagrams (method call sequences)


## Table of Contents

### Classes
- [DiagramGenerator](#diagramgenerator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** dataclasses, extractors, json, pathlib, typing


## Classes

### DiagramGenerator

```python
class DiagramGenerator
```

Generates D3.js-based interactive diagrams for documentation

Output is HTML with embedded D3.js visualization code.
Diagrams are fully interactive with zoom, pan, and hover tooltips.


**Methods:**

  #### `generate_class_hierarchy`

  ```python
  generate_class_hierarchy(self, modules: List[ModuleInfo], output_path: Path, title: str) -> Path
  ```

  Generate interactive class hierarchy diagram

Shows inheritance relationships with:
- Classes as nodes
- Inheritance as directed edges
- Method counts as node size
- Abstract classes highlighted

Args:
    modules: List of analyzed modules
    output_path: Where to save the HTML diagram
    title: Diagram title
    
Returns:
    Path to generated HTML file

  **Parameters:**

  - `self`
  - `modules` (List[ModuleInfo]): List of analyzed modules
  - `output_path` (Path): Where to save the HTML diagram
  - `title` (str) = `'Class Hierarchy'`: Diagram title


  **Returns:** Path
    Path to generated HTML file


  #### `generate_phase_flow_diagram`

  ```python
  generate_phase_flow_diagram(self, phase_data: List[Dict[str, Any]], output_path: Path, title: str) -> Path
  ```

  Generate phase flow diagram for an orchestrator

Shows:
- Phase sequence as flowchart
- Decision points
- Error handling paths
- Success/failure outcomes

Args:
    phase_data: List of phase definitions with transitions
    output_path: Where to save the HTML diagram
    title: Diagram title
    
Returns:
    Path to generated HTML file

  **Parameters:**

  - `self`
  - `phase_data` (List[Dict[str, Any]]): List of phase definitions with transitions
  - `output_path` (Path): Where to save the HTML diagram
  - `title` (str) = `'Phase Flow'`: Diagram title


  **Returns:** Path
    Path to generated HTML file


  #### `generate_sequence_diagram`

  ```python
  generate_sequence_diagram(self, sequences: List[Dict[str, Any]], output_path: Path, title: str) -> Path
  ```

  Generate sequence diagram showing method calls

Args:
    sequences: List of method call sequences
    output_path: Where to save the HTML diagram
    title: Diagram title
    
Returns:
    Path to generated HTML file

  **Parameters:**

  - `self`
  - `sequences` (List[Dict[str, Any]]): List of method call sequences
  - `output_path` (Path): Where to save the HTML diagram
  - `title` (str) = `'Sequence Diagram'`: Diagram title


  **Returns:** Path
    Path to generated HTML file



---
