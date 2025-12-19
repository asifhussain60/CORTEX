# semantic_search_engine

Semantic search engine with FTS5 ranking


## Table of Contents

### Classes
- [SearchResult](#searchresult)
- [SemanticSearchEngine](#semanticsearchengine)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, models, pathlib, sqlite3, typing


## Classes

### SearchResult

```python
class SearchResult
```

**Decorators:** `dataclass`

Search result with ranking


**Attributes:**

- `element_name`: str
- `element_type`: str
- `file_path`: Path
- `line_start`: int
- `line_end`: int
- `score`: float
- `snippet`: str
- `rank`: int



---

### SemanticSearchEngine

```python
class SemanticSearchEngine
```

Search semantic index with ranking


**Methods:**

  #### `search`

  ```python
  search(self, query: str, limit: int) -> List[SearchResult]
  ```

  Search index with ranking

Args:
    query: Search query
    limit: Maximum results to return
    
Returns:
    List of ranked search results

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `limit` (int) = `10`: Maximum results to return


  **Returns:** List[SearchResult]
    List of ranked search results


  #### `search_by_type`

  ```python
  search_by_type(self, query: str, element_type: str, limit: int) -> List[SearchResult]
  ```

  Search by element type

Args:
    query: Search query
    element_type: Filter by type (class, function, method)
    limit: Maximum results
    
Returns:
    List of filtered search results

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `element_type` (str): Filter by type (class, function, method)
  - `limit` (int) = `10`: Maximum results


  **Returns:** List[SearchResult]
    List of filtered search results


  #### `find_symbol`

  ```python
  find_symbol(self, symbol_name: str) -> Optional[SearchResult]
  ```

  Find symbol by exact name

Args:
    symbol_name: Exact symbol name
    
Returns:
    Search result or None

  **Parameters:**

  - `self`
  - `symbol_name` (str): Exact symbol name


  **Returns:** Optional[SearchResult]
    Search result or None


  #### `find_references`

  ```python
  find_references(self, symbol_name: str) -> List[SearchResult]
  ```

  Find references to symbol

Args:
    symbol_name: Symbol to find references to
    
Returns:
    List of elements referencing the symbol

  **Parameters:**

  - `self`
  - `symbol_name` (str): Symbol to find references to


  **Returns:** List[SearchResult]
    List of elements referencing the symbol


  #### `close`

  ```python
  close(self) -> None
  ```

  Close database connection

  **Parameters:**

  - `self`


  **Returns:** None



---
