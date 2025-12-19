# type_extractor

Type Extractor - Analyze type hints and generate type documentation

Extracts and formats Python type hints for documentation.


## Table of Contents

### Classes
- [TypeExtractor](#typeextractor)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** ast, typing


## Classes

### TypeExtractor

```python
class TypeExtractor
```

Extracts and formats type information from Python code

Handles:
- Basic types (int, str, bool, etc.)
- Generic types (List[int], Dict[str, Any], etc.)
- Optional types (Optional[str], Union[str, None])
- Custom class types
- Type aliases


**Methods:**

  #### `extract_type_info`

  ```python
  extract_type_info(self, annotation: Optional[ast.expr]) -> Dict[str, Any]
  ```

  Extract detailed type information from an annotation

Args:
    annotation: AST annotation node
    
Returns:
    Dictionary with type information:
    - 'raw': Raw string representation
    - 'base': Base type name
    - 'args': Type arguments (for generics)
    - 'optional': Whether type is Optional
    - 'complexity': Type complexity score (0-10)

  **Parameters:**

  - `self`
  - `annotation` (Optional[ast.expr]): AST annotation node


  **Returns:** Dict[str, Any]
    Dictionary with type information: - 'raw': Raw string representation - 'base': Base type name - 'args': Type arguments (for generics) - 'optional': Whether type is Optional - 'complexity': Type complexity score (0-10)


  #### `format_type_for_docs`

  ```python
  format_type_for_docs(self, type_info: Dict[str, Any]) -> str
  ```

  Format type information for documentation

Args:
    type_info: Type information dict from extract_type_info
    
Returns:
    Formatted type string suitable for documentation

  **Parameters:**

  - `self`
  - `type_info` (Dict[str, Any]): Type information dict from extract_type_info


  **Returns:** str
    Formatted type string suitable for documentation


  #### `extract_return_type_description`

  ```python
  extract_return_type_description(self, docstring: Optional[str]) -> Optional[str]
  ```

  Extract return type description from docstring

Looks for Returns: section in Google-style docstrings

Args:
    docstring: Method or function docstring
    
Returns:
    Description of return type, or None if not found

  **Parameters:**

  - `self`
  - `docstring` (Optional[str]): Method or function docstring


  **Returns:** Optional[str]
    Description of return type, or None if not found


  #### `extract_param_descriptions`

  ```python
  extract_param_descriptions(self, docstring: Optional[str]) -> Dict[str, str]
  ```

  Extract parameter descriptions from docstring

Parses Args: section in Google-style docstrings

Args:
    docstring: Method or function docstring
    
Returns:
    Dict mapping parameter names to descriptions

  **Parameters:**

  - `self`
  - `docstring` (Optional[str]): Method or function docstring


  **Returns:** Dict[str, str]
    Dict mapping parameter names to descriptions



---
