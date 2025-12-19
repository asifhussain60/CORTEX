# ast_engine

AST Engine - Non-invasive wrapper for CORTEX Lens integration.

Provides programmatic interface to CORTEX Lens AST capabilities
without modifying Lens codebase. Maintains Lens independence.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ASTEngine](#astengine)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, typing


## Classes

### ASTEngine

```python
class ASTEngine
```

Non-invasive CORTEX Lens wrapper for AST analysis.


**Methods:**

  #### `find_semantic_duplicates`

  ```python
  find_semantic_duplicates(self, similarity_threshold: float, min_lines: int) -> List[Dict[str, Any]]
  ```

  Find semantically similar code blocks using AST comparison.

Args:
    similarity_threshold: Minimum similarity score (0.0-1.0)
    min_lines: Minimum lines for duplicate consideration
    
Returns:
    List of duplicate groups with file locations and similarity scores

  **Parameters:**

  - `self`
  - `similarity_threshold` (float) = `0.85`: Minimum similarity score (0.0-1.0)
  - `min_lines` (int) = `10`: Minimum lines for duplicate consideration


  **Returns:** List[Dict[str, Any]]
    List of duplicate groups with file locations and similarity scores


  #### `find_orphaned_tests`

  ```python
  find_orphaned_tests(self, test_patterns: List[str]) -> List[Path]
  ```

  Identify test files with no corresponding source files.

Args:
    test_patterns: Glob patterns for test file matching
    
Returns:
    List of orphaned test file paths

  **Parameters:**

  - `self`
  - `test_patterns` (List[str]) = `None`: Glob patterns for test file matching


  **Returns:** List[Path]
    List of orphaned test file paths


  #### `analyze_test_gaps`

  ```python
  analyze_test_gaps(self, target_file: Path) -> Dict[str, Any]
  ```

  Identify functions/classes without corresponding tests.

Args:
    target_file: Source file to analyze for test coverage
    
Returns:
    Dict with untested functions, classes, and coverage percentage

  **Parameters:**

  - `self`
  - `target_file` (Path): Source file to analyze for test coverage


  **Returns:** Dict[str, Any]
    Dict with untested functions, classes, and coverage percentage


  #### `find_unused_imports`

  ```python
  find_unused_imports(self, target_files: List[Path]) -> List[Dict[str, Any]]
  ```

  Find unused import statements across codebase.

Args:
    target_files: Specific files to analyze, or None for all
    
Returns:
    List of files with unused imports

  **Parameters:**

  - `self`
  - `target_files` (List[Path]) = `None`: Specific files to analyze, or None for all


  **Returns:** List[Dict[str, Any]]
    List of files with unused imports


  #### `detect_dead_code`

  ```python
  detect_dead_code(self, target_paths: List[Path]) -> List[Dict[str, Any]]
  ```

  Detect unreachable or unused code blocks.

Args:
    target_paths: Paths to analyze, or None for full project
    
Returns:
    List of dead code locations

  **Parameters:**

  - `self`
  - `target_paths` (List[Path]) = `None`: Paths to analyze, or None for full project


  **Returns:** List[Dict[str, Any]]
    List of dead code locations


  #### `get_architecture_insights`

  ```python
  get_architecture_insights(self) -> Dict[str, Any]
  ```

  Generate high-level architecture insights.

Returns:
    Architecture metrics and patterns

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Architecture metrics and patterns


  #### `is_available`

  ```python
  is_available(self) -> bool
  ```

  Check if CORTEX Lens is available.

  **Parameters:**

  - `self`


  **Returns:** bool



---
