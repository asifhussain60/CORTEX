# dependency_graph_builder

Dependency graph construction from code elements


## Table of Contents

### Classes
- [DependencyGraphBuilder](#dependencygraphbuilder)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, models, typing


## Classes

### DependencyGraphBuilder

```python
class DependencyGraphBuilder
```

Build and analyze dependency graphs


**Methods:**

  #### `build_graph`

  ```python
  build_graph(self, elements: List[CodeElement]) -> DependencyGraph
  ```

  Construct dependency graph from code elements

Args:
    elements: List of code elements
    
Returns:
    DependencyGraph with nodes and edges

  **Parameters:**

  - `self`
  - `elements` (List[CodeElement]): List of code elements


  **Returns:** DependencyGraph
    DependencyGraph with nodes and edges


  #### `find_dependencies`

  ```python
  find_dependencies(self, element: CodeElement, all_elements: List[CodeElement]) -> List[str]
  ```

  Find dependencies for a code element

Args:
    element: Code element to analyze
    all_elements: All available code elements
    
Returns:
    List of dependency names

  **Parameters:**

  - `self`
  - `element` (CodeElement): Code element to analyze
  - `all_elements` (List[CodeElement]): All available code elements


  **Returns:** List[str]
    List of dependency names


  #### `detect_cycles`

  ```python
  detect_cycles(self, graph: DependencyGraph) -> List[List[str]]
  ```

  Detect circular dependencies in graph

Args:
    graph: Dependency graph
    
Returns:
    List of cycles (each cycle is a list of element names)

  **Parameters:**

  - `self`
  - `graph` (DependencyGraph): Dependency graph


  **Returns:** List[List[str]]
    List of cycles (each cycle is a list of element names)



---
