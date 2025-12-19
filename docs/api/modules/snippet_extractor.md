# snippet_extractor

Code snippet extraction with context


## Table of Contents

### Classes
- [CodeSnippet](#codesnippet)
- [SnippetExtractor](#snippetextractor)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, models, pathlib, re, typing


## Classes

### CodeSnippet

```python
class CodeSnippet
```

**Decorators:** `dataclass`

Code snippet with context


**Attributes:**

- `code`: str
- `start_line`: int
- `end_line`: int
- `context_before`: str
- `context_after`: str
- `highlighted`: str



---

### SnippetExtractor

```python
class SnippetExtractor
```

Extract code snippets with surrounding context


**Methods:**

  #### `extract_snippet`

  ```python
  extract_snippet(self, element: CodeElement, context_lines: int) -> Optional[CodeSnippet]
  ```

  Extract code snippet with context

Args:
    element: Code element to extract
    context_lines: Number of context lines before/after
    
Returns:
    CodeSnippet with context or None

  **Parameters:**

  - `self`
  - `element` (CodeElement): Code element to extract
  - `context_lines` (int) = `3`: Number of context lines before/after


  **Returns:** Optional[CodeSnippet]
    CodeSnippet with context or None


  #### `highlight_matches`

  ```python
  highlight_matches(self, snippet: str, query: str) -> str
  ```

  Highlight search matches in snippet

Args:
    snippet: Code snippet
    query: Search query to highlight
    
Returns:
    Highlighted snippet

  **Parameters:**

  - `self`
  - `snippet` (str): Code snippet
  - `query` (str): Search query to highlight


  **Returns:** str
    Highlighted snippet


  #### `get_surrounding_context`

  ```python
  get_surrounding_context(self, file_path: Path, line_number: int, context_lines: int) -> str
  ```

  Get surrounding context for a line

Args:
    file_path: Path to file
    line_number: Target line number
    context_lines: Lines of context
    
Returns:
    Context string

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to file
  - `line_number` (int): Target line number
  - `context_lines` (int) = `3`: Lines of context


  **Returns:** str
    Context string



---
