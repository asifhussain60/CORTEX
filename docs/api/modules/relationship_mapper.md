# relationship_mapper

Relationship Mapper - Extract entity relationship graphs from code

Builds graphs for:
- File→Function relationships (function definitions and calls)
- File→File relationships (imports and dependencies)
- Feature→File relationships (implementation spanning multiple files)

Author: Asif Hussain


## Table of Contents

### Classes
- [CodeRelationship](#coderelationship)
- [RelationshipMapper](#relationshipmapper)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** ast, dataclasses, hashlib, json, pathlib, re, typing


## Classes

### CodeRelationship

```python
class CodeRelationship
```

**Decorators:** `dataclass`

Represents a relationship between code entities


**Attributes:**

- `source`: str
- `target`: str
- `relationship_type`: str
- `strength`: float
- `context`: str



---

### RelationshipMapper

```python
class RelationshipMapper
```

Extract and store code entity relationships


**Methods:**

  #### `extract_code_relationships`

  ```python
  extract_code_relationships(self, file_path: str, code_content: str) -> List[Dict[str, Any]]
  ```

  Extract file→function relationships from Python code

Args:
    file_path: Path to the file being analyzed
    code_content: Python source code
    
Returns:
    List of relationship dicts with type, name, line number

  **Parameters:**

  - `self`
  - `file_path` (str): Path to the file being analyzed
  - `code_content` (str): Python source code


  **Returns:** List[Dict[str, Any]]
    List of relationship dicts with type, name, line number


  #### `extract_import_relationships`

  ```python
  extract_import_relationships(self, file_path: str, code_content: str) -> List[Dict[str, Any]]
  ```

  Extract file→file import relationships

Args:
    file_path: Path to the file being analyzed
    code_content: Python source code
    
Returns:
    List of import relationship dicts

  **Parameters:**

  - `self`
  - `file_path` (str): Path to the file being analyzed
  - `code_content` (str): Python source code


  **Returns:** List[Dict[str, Any]]
    List of import relationship dicts


  #### `build_feature_graph`

  ```python
  build_feature_graph(self, feature_files: Dict[str, List[str]]) -> Dict[str, List[str]]
  ```

  Build feature→file relationship graph

Args:
    feature_files: Dict mapping feature names to file lists
    
Returns:
    Feature graph dict

  **Parameters:**

  - `self`
  - `feature_files` (Dict[str, List[str]]): Dict mapping feature names to file lists


  **Returns:** Dict[str, List[str]]
    Feature graph dict


  #### `store_relationship`

  ```python
  store_relationship(self, source: str, target: str, relationship_type: str, strength: float, context: str) -> str
  ```

  Store relationship in Tier 2 knowledge graph

Args:
    source: Source entity (file, function, class)
    target: Target entity
    relationship_type: Type of relationship
    strength: Relationship strength (0.0-1.0)
    context: Description of relationship
    
Returns:
    Relationship ID

  **Parameters:**

  - `self`
  - `source` (str): Source entity (file, function, class)
  - `target` (str): Target entity
  - `relationship_type` (str): Type of relationship
  - `strength` (float) = `0.5`: Relationship strength (0.0-1.0)
  - `context` (str) = `''`: Description of relationship


  **Returns:** str
    Relationship ID


  #### `get_related_files`

  ```python
  get_related_files(self, file_path: str, relationship_type: Optional[str]) -> List[Dict[str, Any]]
  ```

  Get files related to given file

Args:
    file_path: Source file path
    relationship_type: Optional filter by relationship type
    
Returns:
    List of related files with relationship info

  **Parameters:**

  - `self`
  - `file_path` (str): Source file path
  - `relationship_type` (Optional[str]) = `None`: Optional filter by relationship type


  **Returns:** List[Dict[str, Any]]
    List of related files with relationship info



---
