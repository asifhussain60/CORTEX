# csharp_ast_parser

C# AST parser using tree-sitter


## Table of Contents

### Classes
- [CSharpASTParser](#csharpastparser)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** ast_parser, logging, models, pathlib, tree_sitter, tree_sitter_c_sharp, typing


## Classes

### CSharpASTParser

```python
class CSharpASTParser(ASTParser)
```

C# AST parser using tree-sitter-csharp


**Methods:**

  #### `parse`

  ```python
  parse(self, file_path: Path, content: str) -> Optional[ASTNode]
  ```

  Parse C# file into AST

Args:
    file_path: Path to C# file
    content: C# source code
    
Returns:
    Root ASTNode or None if parsing fails

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to C# file
  - `content` (str): C# source code


  **Returns:** Optional[ASTNode]
    Root ASTNode or None if parsing fails


  #### `extract_elements`

  ```python
  extract_elements(self, ast_node: ASTNode, file_path: Path) -> List[CodeElement]
  ```

  Extract C# code elements (classes, methods, properties)

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

  Calculate complexity metrics for C# code

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
