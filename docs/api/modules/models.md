# models

Discovery Data Models

Core data structures for discovery operations.

Author: Asif Hussain
Version: 1.0.0


## Table of Contents

### Classes
- [DiscoveryDepth](#discoverydepth)
- [DiscoveryScope](#discoveryscope)
- [FileInfo](#fileinfo)
- [FileInventory](#fileinventory)
- [CodeElement](#codeelement)
- [CodeAnalysisResult](#codeanalysisresult)
- [SemanticIndex](#semanticindex)
- [GitHistory](#githistory)
- [DiscoveryReport](#discoveryreport)
- [ASTNode](#astnode)
- [ComplexityMetrics](#complexitymetrics)
- [DependencyGraph](#dependencygraph)


## Overview

- **Classes:** 12
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, pathlib, typing


## Classes

### DiscoveryDepth

```python
class DiscoveryDepth(Enum)
```

Discovery depth levels.



---

### DiscoveryScope

```python
class DiscoveryScope
```

**Decorators:** `dataclass`

Defines the scope of a discovery operation.

Attributes:
    root_path: Starting directory for discovery
    include_patterns: Glob patterns to include (e.g., ["*.py", "*.cs"])
    exclude_patterns: Glob patterns to exclude (e.g., ["__pycache__", ".git"])
    max_depth: Maximum directory depth to traverse (-1 = unlimited)
    follow_symlinks: Whether to follow symbolic links
    estimated_file_count: Estimated number of files (for progress)
    depth: Discovery depth level


**Attributes:**

- `root_path`: Path
- `include_patterns`: List[str]
- `exclude_patterns`: List[str]
- `max_depth`: int
- `follow_symlinks`: bool
- `estimated_file_count`: int
- `depth`: DiscoveryDepth



---

### FileInfo

```python
class FileInfo
```

**Decorators:** `dataclass`

Metadata for a discovered file.

Attributes:
    path: Absolute path to file
    relative_path: Path relative to discovery root
    language: Detected programming language
    size_bytes: File size in bytes
    line_count: Number of lines
    modified_at: Last modification timestamp
    hash: SHA256 hash of file contents
    encoding: File encoding (e.g., utf-8)


**Attributes:**

- `path`: Path
- `relative_path`: Path
- `language`: str
- `size_bytes`: int
- `line_count`: int
- `modified_at`: datetime
- `hash`: str
- `encoding`: str



---

### FileInventory

```python
class FileInventory
```

**Decorators:** `dataclass`

Collection of discovered files with aggregate statistics.

Attributes:
    files: List of discovered files
    total_files: Total number of files
    total_size: Total size in bytes
    total_lines: Total lines of code
    languages: Language distribution (language -> file count)
    discovery_time: Time taken to discover files


**Attributes:**

- `files`: List[FileInfo]
- `total_files`: int
- `total_size`: int
- `total_lines`: int
- `languages`: Dict[str, int]
- `discovery_time`: float



---

### CodeElement

```python
class CodeElement
```

**Decorators:** `dataclass`

Represents a code element (class, function, method).

Attributes:
    type: Element type (class, function, method, variable)
    name: Element name
    file_path: Path to containing file
    line_start: Starting line number
    line_end: Ending line number
    signature: Function/method signature (for Phase 3)
    complexity: Cyclomatic complexity score (legacy) or ComplexityMetrics (Phase 3)
    dependencies: List of imported/referenced elements
    docstring: Documentation string (if present)


**Attributes:**

- `type`: str
- `name`: str
- `file_path`: Path
- `line_start`: int
- `line_end`: int
- `signature`: str
- `complexity`: Any
- `dependencies`: List[str]
- `docstring`: Optional[str]



---

### CodeAnalysisResult

```python
class CodeAnalysisResult
```

**Decorators:** `dataclass`

Results of AST-based code analysis.

Attributes:
    elements: Discovered code elements
    dependency_graph: Dependency relationships (element -> dependencies)
    complexity_metrics: Complexity statistics
    detected_patterns: Design patterns found
    analysis_time: Time taken for analysis


**Attributes:**

- `elements`: List[CodeElement]
- `dependency_graph`: Dict[str, List[str]]
- `complexity_metrics`: Dict[str, float]
- `detected_patterns`: List[str]
- `analysis_time`: float



---

### SemanticIndex

```python
class SemanticIndex
```

**Decorators:** `dataclass`

Semantic search index for codebase.

Attributes:
    index_path: Path to FTS5 index database
    indexed_files: Number of indexed files
    index_size_mb: Index size in megabytes
    search_ready: Whether index is ready for queries


**Attributes:**

- `index_path`: Path
- `indexed_files`: int
- `index_size_mb`: float
- `search_ready`: bool



---

### GitHistory

```python
class GitHistory
```

**Decorators:** `dataclass`

Git history analysis results.

Attributes:
    commit_count: Total commits analyzed
    author_count: Number of unique authors
    churn_hotspots: Files with high change frequency
    authorship_map: File ownership mapping
    evolution_timeline: Code evolution over time


**Attributes:**

- `commit_count`: int
- `author_count`: int
- `churn_hotspots`: List[Dict[str, Any]]
- `authorship_map`: Dict[str, str]
- `evolution_timeline`: List[Dict[str, Any]]



---

### DiscoveryReport

```python
class DiscoveryReport
```

**Decorators:** `dataclass`

Complete discovery operation report.

Attributes:
    summary: High-level summary
    file_inventory: File discovery results
    code_analysis: AST analysis results (if performed)
    semantic_index: Semantic index info (if created)
    git_history: Git analysis results (if performed)
    insights: Extracted insights
    recommendations: Actionable recommendations
    generated_at: Report generation timestamp
    elapsed_time: Total discovery time


**Attributes:**

- `summary`: Dict[str, Any]
- `file_inventory`: FileInventory
- `code_analysis`: Optional[CodeAnalysisResult]
- `semantic_index`: Optional[SemanticIndex]
- `git_history`: Optional[GitHistory]
- `insights`: List[str]
- `recommendations`: List[Dict[str, Any]]
- `generated_at`: datetime
- `elapsed_time`: float



---

### ASTNode

```python
class ASTNode
```

**Decorators:** `dataclass`

Represents an Abstract Syntax Tree node


**Attributes:**

- `node_type`: str
- `name`: str
- `start_line`: int
- `end_line`: int
- `children`: List['ASTNode']
- `attributes`: Dict[str, Any]



---

### ComplexityMetrics

```python
class ComplexityMetrics
```

**Decorators:** `dataclass`

Complexity metrics for code elements


**Attributes:**

- `cyclomatic_complexity`: int
- `cognitive_complexity`: int
- `lines_of_code`: int
- `number_of_parameters`: int
- `nesting_depth`: int
- `maintainability_index`: float



---

### DependencyGraph

```python
class DependencyGraph
```

**Decorators:** `dataclass`

Dependency graph representation


**Attributes:**

- `nodes`: Dict[str, CodeElement]
- `edges`: List[Tuple[str, str]]
- `cycles`: List[List[str]]



---
