# code_analyzer

Code Analyzer - Extract metadata and structure from Python code

Uses AST (Abstract Syntax Tree) to analyze Python files and extract:
- Classes and their methods
- Function signatures and docstrings
- Type hints and annotations
- Inheritance hierarchies
- Module structure


## Table of Contents

### Classes
- [MethodInfo](#methodinfo)
- [ClassInfo](#classinfo)
- [FunctionInfo](#functioninfo)
- [ModuleInfo](#moduleinfo)
- [CodeAnalyzer](#codeanalyzer)


## Overview

- **Classes:** 5
- **Functions:** 0
- **Dependencies:** ast, dataclasses, inspect, pathlib, typing


## Classes

### MethodInfo

```python
class MethodInfo
```

**Decorators:** `dataclass`

Information about a class method


**Attributes:**

- `name`: str
- `signature`: str
- `docstring`: Optional[str]
- `return_type`: Optional[str]
- `parameters`: List[Dict[str, Any]]
- `is_abstract`: bool
- `is_property`: bool
- `decorators`: List[str]
- `line_number`: int



---

### ClassInfo

```python
class ClassInfo
```

**Decorators:** `dataclass`

Information about a class


**Attributes:**

- `name`: str
- `docstring`: Optional[str]
- `base_classes`: List[str]
- `methods`: List[MethodInfo]
- `attributes`: List[Dict[str, Any]]
- `is_abstract`: bool
- `decorators`: List[str]
- `line_number`: int



---

### FunctionInfo

```python
class FunctionInfo
```

**Decorators:** `dataclass`

Information about a standalone function


**Attributes:**

- `name`: str
- `signature`: str
- `docstring`: Optional[str]
- `return_type`: Optional[str]
- `parameters`: List[Dict[str, Any]]
- `decorators`: List[str]
- `line_number`: int



---

### ModuleInfo

```python
class ModuleInfo
```

**Decorators:** `dataclass`

Information about a Python module


**Attributes:**

- `name`: str
- `path`: Path
- `docstring`: Optional[str]
- `classes`: List[ClassInfo]
- `functions`: List[FunctionInfo]
- `imports`: List[str]
- `dependencies`: Set[str]



---

### CodeAnalyzer

```python
class CodeAnalyzer
```

Analyzes Python code using AST to extract structural information

Example:
    analyzer = CodeAnalyzer()
    module_info = analyzer.analyze_file(Path("my_module.py"))
    
    # Access extracted information
    for cls in module_info.classes:
        print(f"Class: {cls.name}")
        for method in cls.methods:
            print(f"  Method: {method.name} - {method.signature}")


**Methods:**

  #### `analyze_file`

  ```python
  analyze_file(self, file_path: Path) -> ModuleInfo
  ```

  Analyze a Python file and extract all metadata

Args:
    file_path: Path to the Python file
    
Returns:
    ModuleInfo containing all extracted information
    
Raises:
    SyntaxError: If the file contains invalid Python syntax
    FileNotFoundError: If the file doesn't exist

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to the Python file


  **Returns:** ModuleInfo
    ModuleInfo containing all extracted information



---
