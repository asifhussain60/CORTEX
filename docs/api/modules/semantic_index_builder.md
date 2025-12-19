# semantic_index_builder

Semantic index builder using SQLite FTS5


## Table of Contents

### Classes
- [SemanticIndexBuilder](#semanticindexbuilder)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, models, pathlib, sqlite3, typing


## Classes

### SemanticIndexBuilder

```python
class SemanticIndexBuilder
```

Build and maintain FTS5 semantic search index


**Methods:**

  #### `build_index`

  ```python
  build_index(self, elements: List[CodeElement]) -> dict
  ```

  Build FTS5 index from code elements

Args:
    elements: List of code elements to index
    
Returns:
    Index metadata dictionary

  **Parameters:**

  - `self`
  - `elements` (List[CodeElement]): List of code elements to index


  **Returns:** dict
    Index metadata dictionary


  #### `index_element`

  ```python
  index_element(self, element: CodeElement) -> None
  ```

  Index a single code element

Args:
    element: Code element to index

  **Parameters:**

  - `self`
  - `element` (CodeElement): Code element to index


  **Returns:** None


  #### `update_element`

  ```python
  update_element(self, element: CodeElement) -> None
  ```

  Update indexed element

Args:
    element: Code element with updates

  **Parameters:**

  - `self`
  - `element` (CodeElement): Code element with updates


  **Returns:** None


  #### `remove_element`

  ```python
  remove_element(self, element_id: str) -> None
  ```

  Remove element from index

Args:
    element_id: ID of element to remove

  **Parameters:**

  - `self`
  - `element_id` (str): ID of element to remove


  **Returns:** None


  #### `close`

  ```python
  close(self) -> None
  ```

  Close database connection

  **Parameters:**

  - `self`


  **Returns:** None



---
