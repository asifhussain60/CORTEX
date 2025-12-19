# file_tracker

CORTEX Tier 1: File Tracker
Tracks file modifications during conversations

Task 1.4: FileTracker
Duration: 1 hour


## Table of Contents

### Classes
- [FileTracker](#filetracker)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, pathlib, re, typing


## Classes

### FileTracker

```python
class FileTracker
```

Tracks file modifications during conversations

Responsibilities:
- Extract file paths from text
- Normalize file paths
- Track file modification patterns
- Associate files with conversations


**Methods:**

  #### `extract_files_from_text`

  ```python
  extract_files_from_text(self, text: str) -> List[str]
  ```

  Extract file paths from text

Args:
    text: Text to analyze
    
Returns:
    List of normalized file paths

  **Parameters:**

  - `self`
  - `text` (str): Text to analyze


  **Returns:** List[str]
    List of normalized file paths


  #### `track_file_modifications`

  ```python
  track_file_modifications(self, before_text: str, after_text: str) -> List[str]
  ```

  Compare two texts to find newly mentioned files

Args:
    before_text: Text before operation
    after_text: Text after operation
    
Returns:
    List of newly mentioned files

  **Parameters:**

  - `self`
  - `before_text` (str): Text before operation
  - `after_text` (str): Text after operation


  **Returns:** List[str]
    List of newly mentioned files


  #### `get_file_patterns`

  ```python
  get_file_patterns(self, files: List[str]) -> Dict[str, List[str]]
  ```

  Group files by type/pattern and directory

Args:
    files: List of file paths
    
Returns:
    Dictionary mapping patterns to file lists

  **Parameters:**

  - `self`
  - `files` (List[str]): List of file paths


  **Returns:** Dict[str, List[str]]
    Dictionary mapping patterns to file lists


  #### `get_directory_hierarchy`

  ```python
  get_directory_hierarchy(self, files: List[str]) -> Dict[str, int]
  ```

  Get directory modification counts

Args:
    files: List of file paths
    
Returns:
    Dictionary mapping directories to file counts

  **Parameters:**

  - `self`
  - `files` (List[str]): List of file paths


  **Returns:** Dict[str, int]
    Dictionary mapping directories to file counts


  #### `get_file_statistics`

  ```python
  get_file_statistics(self, files: List[str]) -> Dict
  ```

  Get statistics about files

Args:
    files: List of file paths
    
Returns:
    Statistics dictionary

  **Parameters:**

  - `self`
  - `files` (List[str]): List of file paths


  **Returns:** Dict
    Statistics dictionary


  #### `format_file_list`

  ```python
  format_file_list(self, files: List[str], max_files: int) -> str
  ```

  Format file list for display

Args:
    files: List of file paths
    max_files: Maximum files to display
    
Returns:
    Formatted string

  **Parameters:**

  - `self`
  - `files` (List[str]): List of file paths
  - `max_files` (int) = `10`: Maximum files to display


  **Returns:** str
    Formatted string



---
