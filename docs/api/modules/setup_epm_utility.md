# setup_epm_utility

Setup EPM (Entry Point Module) Utility - Copilot Instructions Generation

Generates and manages .github/copilot-instructions.md files for user repositories
with project detection, template generation, brain learning integration, and
CORTEX enhancement catalog review.

Part of CORTEX 3.2.1 - Entry Point Module System
Sprint 12a Migration: setup_epm_orchestrator (1,123 lines) → setup_epm_utility (~1,300 lines)
Author: Asif Hussain

Operations:
- detect_project_structure: Fast file-system based project analysis
- detect_language: Identify primary programming language
- detect_framework: Identify framework (Django, Flask, React, etc.)
- detect_build_system: Identify build system (pip, npm, Maven, etc.)
- detect_test_framework: Identify test framework (pytest, Jest, JUnit, etc.)
- render_template: Generate copilot-instructions.md content
- generate_build_command: Create build command for detected system
- generate_test_command: Create test command for detected framework
- schedule_brain_learning: Schedule Tier 3 pattern learning
- review_cortex_enhancements: Review CORTEX enhancement catalog
- validate_installation: Verify CORTEX bootstrap and configuration
- handle_existing_file: Merge logic for existing instructions


## Table of Contents

### Classes
- [ProjectDetection](#projectdetection)
- [CortexCapabilities](#cortexcapabilities)
- [EPMResult](#epmresult)

### Functions
- [detect_language](#detect_language)
- [detect_framework](#detect_framework)
- [detect_build_system](#detect_build_system)
- [detect_test_framework](#detect_test_framework)
- [detect_project_structure](#detect_project_structure)
- [generate_build_command](#generate_build_command)
- [generate_test_command](#generate_test_command)
- [review_cortex_enhancements](#review_cortex_enhancements)
- [render_template](#render_template)
- [schedule_brain_learning](#schedule_brain_learning)
- [handle_existing_file](#handle_existing_file)
- [validate_installation](#validate_installation)
- [execute_epm_setup](#execute_epm_setup)


## Overview

- **Classes:** 3
- **Functions:** 14
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, shutil, src, tempfile, time, typing


## Classes

### ProjectDetection

```python
class ProjectDetection
```

**Decorators:** `dataclass`

Project structure detection result.


**Attributes:**

- `language`: str
- `framework`: str
- `build_system`: str
- `test_framework`: str
- `has_readme`: bool
- `has_gitignore`: bool
- `repo_name`: str
- `timestamp`: str
- `file_count`: int


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### CortexCapabilities

```python
class CortexCapabilities
```

**Decorators:** `dataclass`

CORTEX enhancement catalog capabilities.


**Attributes:**

- `total_count`: int
- `new_count`: int
- `features`: List[Dict[str, Any]]
- `categories`: Dict[str, int]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### EPMResult

```python
class EPMResult
```

**Decorators:** `dataclass`

EPM execution result.


**Attributes:**

- `success`: bool
- `file_path`: str
- `detected`: ProjectDetection
- `cortex_capabilities`: Optional[CortexCapabilities]
- `learning_enabled`: bool
- `message`: str
- `errors`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

## Functions

### detect_language

```python
detect_language(repo_path: Path) -> str
```

Detect primary programming language.

Prioritizes Python detection, then checks for other languages.

Args:
    repo_path: Repository root path

Returns:
    Detected language name

Example:
    >>> detect_language(Path("/path/to/repo"))
    'Python'


**Parameters:**

- `repo_path` (Path): Repository root path


**Returns:** str
  Detected language name


---

### detect_framework

```python
detect_framework(repo_path: Path, language: str) -> str
```

Detect framework based on language and project markers.

Args:
    repo_path: Repository root path
    language: Detected programming language

Returns:
    Detected framework name

Example:
    >>> detect_framework(Path("/path/to/repo"), "Python")
    'Django'


**Parameters:**

- `repo_path` (Path): Repository root path
- `language` (str): Detected programming language


**Returns:** str
  Detected framework name


---

### detect_build_system

```python
detect_build_system(repo_path: Path, language: str) -> str
```

Detect build system.

Args:
    repo_path: Repository root path
    language: Detected programming language

Returns:
    Detected build system name

Example:
    >>> detect_build_system(Path("/path/to/repo"), "Python")
    'pip'


**Parameters:**

- `repo_path` (Path): Repository root path
- `language` (str): Detected programming language


**Returns:** str
  Detected build system name


---

### detect_test_framework

```python
detect_test_framework(repo_path: Path, language: str) -> str
```

Detect test framework.

Args:
    repo_path: Repository root path
    language: Detected programming language

Returns:
    Detected test framework name

Example:
    >>> detect_test_framework(Path("/path/to/repo"), "Python")
    'pytest'


**Parameters:**

- `repo_path` (Path): Repository root path
- `language` (str): Detected programming language


**Returns:** str
  Detected test framework name


---

### detect_project_structure

```python
detect_project_structure(repo_path: Path) -> ProjectDetection
```

Fast project structure detection using file system only.

Detects language, framework, build system, test framework, and
other project metadata.

Args:
    repo_path: Repository root path to analyze

Returns:
    ProjectDetection with all detected metadata

Example:
    >>> detection = detect_project_structure(Path("/path/to/repo"))
    >>> detection.language
    'Python'
    >>> detection.framework
    'Django'


**Parameters:**

- `repo_path` (Path): Repository root path to analyze


**Returns:** ProjectDetection
  ProjectDetection with all detected metadata


---

### generate_build_command

```python
generate_build_command(detection: ProjectDetection) -> str
```

Generate likely build command based on detection.

Args:
    detection: ProjectDetection result

Returns:
    Build command string

Example:
    >>> generate_build_command(detection)
    'pip install -r requirements.txt'


**Parameters:**

- `detection` (ProjectDetection): ProjectDetection result


**Returns:** str
  Build command string


---

### generate_test_command

```python
generate_test_command(detection: ProjectDetection) -> str
```

Generate likely test command based on detection.

Args:
    detection: ProjectDetection result

Returns:
    Test command string

Example:
    >>> generate_test_command(detection)
    'pytest'


**Parameters:**

- `detection` (ProjectDetection): ProjectDetection result


**Returns:** str
  Test command string


---

### review_cortex_enhancements

```python
review_cortex_enhancements(cortex_root: Optional[Path]) -> Optional[CortexCapabilities]
```

Review CORTEX enhancement catalog for available capabilities.

Scans enhancement catalog to identify new and existing CORTEX features
for inclusion in copilot instructions.

Args:
    cortex_root: CORTEX installation root (optional, auto-detected)

Returns:
    CortexCapabilities with feature list, or None if catalog not found

Example:
    >>> capabilities = review_cortex_enhancements()
    >>> capabilities.total_count
    15


**Parameters:**

- `cortex_root` (Optional[Path]) = `None`: CORTEX installation root (optional, auto-detected)


**Returns:** Optional[CortexCapabilities]
  CortexCapabilities with feature list, or None if catalog not found


---

### render_template

```python
render_template(detection: ProjectDetection, namespace: str, tier3_enabled: bool, cortex_capabilities: Optional[CortexCapabilities]) -> str
```

Render copilot-instructions.md template.

Generates Markdown content for GitHub Copilot instructions with
project-specific context and CORTEX integration.

Args:
    detection: ProjectDetection result
    namespace: Tier 3 namespace for learning
    tier3_enabled: Whether Tier 3 brain learning is enabled
    cortex_capabilities: CORTEX capabilities (optional)

Returns:
    Rendered Markdown template

Example:
    >>> content = render_template(detection, "workspace.myproject", True)
    >>> "# GitHub Copilot Instructions" in content
    True


**Parameters:**

- `detection` (ProjectDetection): ProjectDetection result
- `namespace` (str): Tier 3 namespace for learning
- `tier3_enabled` (bool): Whether Tier 3 brain learning is enabled
- `cortex_capabilities` (Optional[CortexCapabilities]) = `None`: CORTEX capabilities (optional)


**Returns:** str
  Rendered Markdown template


---

### schedule_brain_learning

```python
schedule_brain_learning(detection: ProjectDetection, namespace: str, tier3_db_path: Optional[str]) -> bool
```

Schedule brain learning for project patterns.

Records project metadata in Tier 3 database for pattern learning.

Args:
    detection: ProjectDetection result
    namespace: Tier 3 namespace for this project
    tier3_db_path: Path to Tier 3 database (optional)

Returns:
    True if scheduled successfully, False if Tier 3 unavailable

Example:
    >>> scheduled = schedule_brain_learning(detection, "workspace.myproject")
    >>> scheduled
    True


**Parameters:**

- `detection` (ProjectDetection): ProjectDetection result
- `namespace` (str): Tier 3 namespace for this project
- `tier3_db_path` (Optional[str]) = `None`: Path to Tier 3 database (optional)


**Returns:** bool
  True if scheduled successfully, False if Tier 3 unavailable


---

### handle_existing_file

```python
handle_existing_file(file_path: Path, detection: ProjectDetection) -> EPMResult
```

Handle existing copilot-instructions.md file.

Provides merge/update options when instructions already exist.

Args:
    file_path: Path to existing instructions file
    detection: Current ProjectDetection

Returns:
    EPMResult with status and message

Example:
    >>> result = handle_existing_file(Path(".github/copilot-instructions.md"), detection)
    >>> result.success
    False
    >>> "already exists" in result.message
    True


**Parameters:**

- `file_path` (Path): Path to existing instructions file
- `detection` (ProjectDetection): Current ProjectDetection


**Returns:** EPMResult
  EPMResult with status and message


---

### validate_installation

```python
validate_installation(repo_path: Path, cortex_root: Optional[Path]) -> Dict[str, Any]
```

Validate CORTEX installation and bootstrap.

Checks for:
- .github/copilot-instructions.md exists
- CORTEX brain accessible
- Tier 3 database healthy

Args:
    repo_path: Repository root path
    cortex_root: CORTEX installation root (optional)

Returns:
    Dictionary with validation results

Example:
    >>> result = validate_installation(Path("/path/to/repo"))
    >>> result["success"]
    True


**Parameters:**

- `repo_path` (Path): Repository root path
- `cortex_root` (Optional[Path]) = `None`: CORTEX installation root (optional)


**Returns:** Dict[str, Any]
  Dictionary with validation results


---

### execute_epm_setup

```python
execute_epm_setup(repo_path: Path, tier3_db_path: Optional[str], cortex_root: Optional[Path], force: bool) -> EPMResult
```

Execute complete EPM setup workflow.

Main entry point for generating copilot instructions with project
detection, template generation, and brain learning integration.

Args:
    repo_path: Repository root path
    tier3_db_path: Path to Tier 3 database (optional, auto-detected)
    cortex_root: CORTEX installation root (optional, auto-detected)
    force: If True, regenerate even if file exists

Returns:
    EPMResult with execution results

Example:
    >>> result = execute_epm_setup(Path("/path/to/repo"))
    >>> result.success
    True
    >>> result.learning_enabled
    True


**Parameters:**

- `repo_path` (Path): Repository root path
- `tier3_db_path` (Optional[str]) = `None`: Path to Tier 3 database (optional, auto-detected)
- `cortex_root` (Optional[Path]) = `None`: CORTEX installation root (optional, auto-detected)
- `force` (bool) = `False`: If True, regenerate even if file exists


**Returns:** EPMResult
  EPMResult with execution results


---
