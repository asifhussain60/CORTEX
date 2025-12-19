# python_ast_parser

Python AST parser using built-in ast module


## Table of Contents

### Classes
- [PythonASTParser](#pythonastparser)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** ast, ast_parser, logging, models, pathlib, typing


## Classes

### PythonASTParser

```python
class PythonASTParser(ASTParser)
```

Python AST parser using Python's ast module


**Methods:**

  #### `parse`

  ```python
  parse(self, file_path: Path, content: str) -> Optional[ASTNode]
  ```

  Parse Python file into AST

Args:
    file_path: Path to Python file
    content: Python source code
    
Returns:
    Root ASTNode or None if parsing fails

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to Python file
  - `content` (str): Python source code


  **Returns:** Optional[ASTNode]
    Root ASTNode or None if parsing fails


  #### `extract_elements`

  ```python
  extract_elements(self, ast_node: ASTNode, file_path: Path) -> List[CodeElement]
  ```

  Extract Python code elements (classes, functions, methods)

Args:
    ast_node: Root AST node
    file_path: Path to source file
    
Returns:
    List of CodeElements

  **Parameters:**

  - `self`
  - `ast_node` (ASTNode): Root AST node
  - `file_path` (Path): Path to source file


  **Returns:** List[CodeElement]
    List of CodeElements


  #### `calculate_complexity`

  ```python
  calculate_complexity(self, ast_node: ASTNode) -> ComplexityMetrics
  ```

  Calculate complexity metrics for Python code

Args:
    ast_node: AST node to analyze
    
Returns:
    ComplexityMetrics

  **Parameters:**

  - `self`
  - `ast_node` (ASTNode): AST node to analyze


  **Returns:** ComplexityMetrics
    ComplexityMetrics



---
