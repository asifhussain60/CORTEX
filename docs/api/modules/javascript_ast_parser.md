# javascript_ast_parser

JavaScript/TypeScript AST parser using tree-sitter


## Table of Contents

### Classes
- [JavaScriptASTParser](#javascriptastparser)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** ast_parser, logging, models, pathlib, tree_sitter, tree_sitter_javascript, typing


## Classes

### JavaScriptASTParser

```python
class JavaScriptASTParser(ASTParser)
```

JavaScript/TypeScript AST parser using tree-sitter-javascript


**Methods:**

  #### `parse`

  ```python
  parse(self, file_path: Path, content: str) -> Optional[ASTNode]
  ```

  Parse JavaScript/TypeScript file into AST

Args:
    file_path: Path to JS/TS file
    content: JavaScript/TypeScript source code
    
Returns:
    Root ASTNode or None if parsing fails

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to JS/TS file
  - `content` (str): JavaScript/TypeScript source code


  **Returns:** Optional[ASTNode]
    Root ASTNode or None if parsing fails


  #### `extract_elements`

  ```python
  extract_elements(self, ast_node: ASTNode, file_path: Path) -> List[CodeElement]
  ```

  Extract JavaScript code elements (functions, classes, exports)

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

  Calculate complexity metrics for JavaScript code

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
