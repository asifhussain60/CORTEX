# pr_context_utility

PR Context Utility

Lightweight dependency-driven Pull Request context building.

Core Operations:
- build_pr_context: Main workflow for building dependency graph
- extract_imports: Multi-language import parsing
- detect_language: File language detection
- resolve_import_path: Import name to file path resolution
- find_test_files: Locate test files for changed files

Version: 3.0.0 (Migrated from PRContextBuilder v1.0)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [Language](#language)
- [FileNode](#filenode)
- [DependencyGraph](#dependencygraph)

### Functions
- [detect_language](#detect_language)
- [extract_imports](#extract_imports)
- [is_test_file](#is_test_file)
- [estimate_tokens](#estimate_tokens)
- [resolve_import_path](#resolve_import_path)
- [find_test_files](#find_test_files)
- [build_pr_context](#build_pr_context)


## Overview

- **Classes:** 3
- **Functions:** 7
- **Dependencies:** dataclasses, enum, os, pathlib, re, time, typing


## Classes

### Language

```python
class Language(Enum)
```

Supported languages



---

### FileNode

```python
class FileNode
```

**Decorators:** `dataclass`

File in dependency graph


**Attributes:**

- `path`: str
- `language`: Language
- `imports`: List[str]
- `is_test`: bool
- `is_changed`: bool
- `token_estimate`: int
- `level`: int



---

### DependencyGraph

```python
class DependencyGraph
```

**Decorators:** `dataclass`

PR dependency graph


**Attributes:**

- `nodes`: Dict[str, FileNode]
- `changed_files`: List[str]
- `direct_imports`: List[str]
- `test_files`: List[str]
- `indirect_deps`: List[str]
- `total_tokens`: int



---

## Functions

### detect_language

```python
detect_language(filepath: str) -> Language
```

Detect language from file extension

Args:
    filepath: Path to file
    
Returns:
    Detected language
    
Example:
    >>> lang = detect_language("src/main.py")
    >>> print(lang)
    Language.PYTHON


**Parameters:**

- `filepath` (str): Path to file


**Returns:** Language
  Detected language


---

### extract_imports

```python
extract_imports(filepath: str, content: str) -> List[str]
```

Extract imports from file content

Args:
    filepath: Path to file
    content: File content
    
Returns:
    List of imported module names
    
Example:
    >>> imports = extract_imports("main.py", "import os\nfrom pathlib import Path")
    >>> print(imports)
    ['os', 'pathlib']


**Parameters:**

- `filepath` (str): Path to file
- `content` (str): File content


**Returns:** List[str]
  List of imported module names


---

### is_test_file

```python
is_test_file(filepath: str) -> bool
```

Check if file is a test file

Args:
    filepath: Path to file
    
Returns:
    True if test file
    
Example:
    >>> is_test = is_test_file("test_main.py")
    >>> print(is_test)
    True


**Parameters:**

- `filepath` (str): Path to file


**Returns:** bool
  True if test file


---

### estimate_tokens

```python
estimate_tokens(content: Optional[str], filepath: Optional[str]) -> int
```

Estimate token count

Args:
    content: File content
    filepath: Path to file
    
Returns:
    Estimated tokens
    
Example:
    >>> tokens = estimate_tokens(content="print('hello')")
    >>> print(tokens > 0)
    True


**Parameters:**

- `content` (Optional[str]) = `None`: File content
- `filepath` (Optional[str]) = `None`: Path to file


**Returns:** int
  Estimated tokens


---

### resolve_import_path

```python
resolve_import_path(source_file: str, import_name: str, workspace_root: str) -> Optional[str]
```

Resolve import name to file path

Args:
    source_file: Source file path
    import_name: Import module name
    workspace_root: Workspace root directory
    
Returns:
    Resolved file path or None
    
Example:
    >>> path = resolve_import_path("src/main.py", "utils.helper", "/project")
    >>> print(path)
    'src/utils/helper.py'


**Parameters:**

- `source_file` (str): Source file path
- `import_name` (str): Import module name
- `workspace_root` (str): Workspace root directory


**Returns:** Optional[str]
  Resolved file path or None


---

### find_test_files

```python
find_test_files(changed_files: List[str], workspace_root: str) -> List[str]
```

Find test files for changed files

Args:
    changed_files: List of changed files
    workspace_root: Workspace root
    
Returns:
    List of test file paths
    
Example:
    >>> tests = find_test_files(["src/main.py"], "/project")
    >>> print(len(tests) >= 0)
    True


**Parameters:**

- `changed_files` (List[str]): List of changed files
- `workspace_root` (str): Workspace root


**Returns:** List[str]
  List of test file paths


---

### build_pr_context

```python
build_pr_context(changed_files: List[str], workspace_root: str, max_files: int, token_budget: int, include_tests: bool, include_indirect: bool) -> DependencyGraph
```

Build PR dependency graph with crawl strategy

Args:
    changed_files: List of changed files
    workspace_root: Workspace root directory
    max_files: Maximum files to include
    token_budget: Maximum token budget
    include_tests: Include test files
    include_indirect: Include indirect dependencies
    
Returns:
    Dependency graph
    
Example:
    >>> graph = build_pr_context(["src/main.py"], "/project")
    >>> print(len(graph.nodes) > 0)
    True


**Parameters:**

- `changed_files` (List[str]): List of changed files
- `workspace_root` (str): Workspace root directory
- `max_files` (int) = `50`: Maximum files to include
- `token_budget` (int) = `10000`: Maximum token budget
- `include_tests` (bool) = `True`: Include test files
- `include_indirect` (bool) = `False`: Include indirect dependencies


**Returns:** DependencyGraph
  Dependency graph


---
