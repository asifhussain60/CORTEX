# ast_parser

Base AST parser for code intelligence


## Table of Contents

### Classes
- [ASTParser](#astparser)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** abc, logging, models, pathlib, typing


## Classes

### ASTParser

```python
class ASTParser(ABC)
```

Base class for language-specific AST parsing


**Methods:**

  #### `parse`

  *Decorators:* `abstractmethod`

  ```python
  parse(self, file_path: Path, content: str) -> Optional[ASTNode]
  ```

  Parse file content into AST

Args:
    file_path: Path to the file
    content: File content as string
    
Returns:
    Root ASTNode or None if parsing fails

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to the file
  - `content` (str): File content as string


  **Returns:** Optional[ASTNode]
    Root ASTNode or None if parsing fails


  #### `extract_elements`

  *Decorators:* `abstractmethod`

  ```python
  extract_elements(self, ast: ASTNode, file_path: Path) -> List[CodeElement]
  ```

  Extract code elements from AST

Args:
    ast: Root AST node
    file_path: Path to the source file
    
Returns:
    List of extracted CodeElements

  **Parameters:**

  - `self`
  - `ast` (ASTNode): Root AST node
  - `file_path` (Path): Path to the source file


  **Returns:** List[CodeElement]
    List of extracted CodeElements


  #### `calculate_complexity`

  *Decorators:* `abstractmethod`

  ```python
  calculate_complexity(self, ast: ASTNode) -> ComplexityMetrics
  ```

  Calculate complexity metrics for AST node

Args:
    ast: AST node to analyze
    
Returns:
    ComplexityMetrics for the node

  **Parameters:**

  - `self`
  - `ast` (ASTNode): AST node to analyze


  **Returns:** ComplexityMetrics
    ComplexityMetrics for the node


  #### `supports_language`

  ```python
  supports_language(self, language: str) -> bool
  ```

  Check if parser supports language

Args:
    language: Language name
    
Returns:
    True if language is supported

  **Parameters:**

  - `self`
  - `language` (str): Language name


  **Returns:** bool
    True if language is supported



---
