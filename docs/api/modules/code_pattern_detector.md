# code_pattern_detector

Code Pattern Detector - Lightweight Pattern Detection for AI Instructions

Performs FAST, HIGH-LEVEL pattern detection to generate AI instructions.
This is TIER 1 scanning for setup - just enough intelligence for copilot-instructions.md.

**Two-Tier Strategy:**
- **TIER 1 (This Module):** Lightweight setup scan (<3 seconds)
  - Purpose: Generate copilot-instructions.md and CORTEX.prompt.md enhancements
  - Method: Regex + import detection (minimal AST)
  - Detects: Framework, auth hint, API hint, ORM hint (4-5 patterns max)
  - Triggers: `setup copilot instructions`

- **TIER 2 (Dashboard Collectors):** Deep analysis (30-60 seconds, background)
  - Purpose: Detailed metrics, complexity, dependencies, code quality
  - Method: Full AST analysis with caching
  - Modules: code_metrics_collector, complexity_analyzer, dependency_analyzer
  - Triggers: `onboard application`

**Philosophy:** Setup needs just enough intelligence to write good instructions.
Deep analysis happens during application onboarding.

Part of CORTEX 3.9.0 - AST-Powered Copilot Instructions Enhancement
Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [DomainPatterns](#domainpatterns)
- [PatternCache](#patterncache)

### Functions
- [detect_patterns](#detect_patterns)
- [detect_python_patterns](#detect_python_patterns)
- [detect_typescript_patterns](#detect_typescript_patterns)
- [detect_csharp_patterns](#detect_csharp_patterns)
- [detect_java_patterns](#detect_java_patterns)
- [detect_generic_patterns](#detect_generic_patterns)


## Overview

- **Classes:** 2
- **Functions:** 10
- **Dependencies:** ast, concurrent, dataclasses, json, logging, pathlib, re, time, typing


## Classes

### DomainPatterns

```python
class DomainPatterns
```

**Decorators:** `dataclass`

Detected code patterns for AI instruction generation.


**Attributes:**

- `architecture`: List[str]
- `auth_method`: Optional[str]
- `api_style`: Optional[str]
- `data_access`: Optional[str]
- `testing_patterns`: List[str]
- `framework_specifics`: Dict[str, str]
- `custom_conventions`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary for serialization.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `pattern_count`

  ```python
  pattern_count(self) -> int
  ```

  Count total patterns detected.

  **Parameters:**

  - `self`


  **Returns:** int



---

### PatternCache

```python
class PatternCache
```

Cache detected patterns to avoid re-scanning.


**Methods:**

  #### `get_cache_path`

  ```python
  get_cache_path(self, project_root: Path) -> Path
  ```

  Get cache file path for project.

  **Parameters:**

  - `self`
  - `project_root` (Path)


  **Returns:** Path


  #### `load`

  ```python
  load(self, project_root: Path) -> Optional[DomainPatterns]
  ```

  Load cached patterns if available and fresh.

  **Parameters:**

  - `self`
  - `project_root` (Path)


  **Returns:** Optional[DomainPatterns]


  #### `save`

  ```python
  save(self, project_root: Path, patterns: DomainPatterns)
  ```

  Save patterns to cache.

  **Parameters:**

  - `self`
  - `project_root` (Path)
  - `patterns` (DomainPatterns)



---

## Functions

### detect_patterns

```python
detect_patterns(project_root: Path, language: str, use_cache: bool) -> DomainPatterns
```

Detect code patterns via efficient AST analysis.

**Performance Optimized:**
- Scans ONLY key files (5-10 max)
- Uses cache to avoid re-scanning
- Parallel file processing
- Early termination on pattern detection

Args:
    project_root: Project root directory
    language: Primary language (Python, JavaScript, C#, Java, etc.)
    use_cache: Use cached results if available

Returns:
    DomainPatterns with detected patterns

Example:
    >>> patterns = detect_patterns(Path("/path/to/project"), "Python")
    >>> patterns.architecture
    ['Repository Pattern', 'Service Layer']


**Parameters:**

- `project_root` (Path): Project root directory
- `language` (str): Primary language (Python, JavaScript, C#, Java, etc.)
- `use_cache` (bool) = `True`: Use cached results if available


**Returns:** DomainPatterns
  DomainPatterns with detected patterns


---

### detect_python_patterns

```python
detect_python_patterns(project_root: Path) -> DomainPatterns
```

Detect Python patterns via LIGHTWEIGHT regex + import scanning.

**TIER 1 Approach (Fast):**
- Scans ONLY 3-5 key files (entry points + config)
- Uses regex + simple string matching (NOT deep AST)
- Detects 4-5 high-level patterns max
- Completes in <3 seconds

**Detected Patterns:**
- Framework: FastAPI, Flask, Django (from imports)
- Auth hint: JWT, OAuth (from imports)
- API hint: REST decorators
- ORM hint: SQLAlchemy, Django ORM (from imports)
- Architecture hint: Repository/Service (from filenames only)


**Parameters:**

- `project_root` (Path)


**Returns:** DomainPatterns


---

### detect_typescript_patterns

```python
detect_typescript_patterns(project_root: Path) -> DomainPatterns
```

Detect TypeScript/JavaScript patterns via package.json + simple regex.

TIER 1: Check package.json for framework hints, minimal file scanning.


**Parameters:**

- `project_root` (Path)


**Returns:** DomainPatterns


---

### detect_csharp_patterns

```python
detect_csharp_patterns(project_root: Path) -> DomainPatterns
```

Detect C# patterns via .csproj and minimal file checks.

TIER 1: Check project files, detect ASP.NET/Entity Framework hints.


**Parameters:**

- `project_root` (Path)


**Returns:** DomainPatterns


---

### detect_java_patterns

```python
detect_java_patterns(project_root: Path) -> DomainPatterns
```

Detect Java patterns via pom.xml/build.gradle checks.

TIER 1: Check build files for Spring/JPA hints.


**Parameters:**

- `project_root` (Path)


**Returns:** DomainPatterns


---

### detect_generic_patterns

```python
detect_generic_patterns(project_root: Path) -> DomainPatterns
```

Generic pattern detection for unsupported languages.


**Parameters:**

- `project_root` (Path)


**Returns:** DomainPatterns


---
