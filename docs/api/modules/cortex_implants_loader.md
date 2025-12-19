# cortex_implants_loader

CORTEX Implants Loader

Loads and validates repository-specific governance rules from .cortex-implants/ folders.
Each repository maintains its own implants with strict isolation.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0


## Table of Contents

### Classes
- [EnforcementLevel](#enforcementlevel)
- [RepositoryType](#repositorytype)
- [ImplantGovernance](#implantgovernance)
- [CodingStandards](#codingstandards)
- [ArchitecturePatterns](#architecturepatterns)
- [BusinessRules](#businessrules)
- [TechStack](#techstack)
- [SecurityPolicy](#securitypolicy)
- [CortexImplants](#corteximplants)
- [CortexImplantsLoader](#corteximplantsloader)

### Functions
- [get_cortex_implants_loader](#get_cortex_implants_loader)
- [load_cortex_implants](#load_cortex_implants)


## Overview

- **Classes:** 10
- **Functions:** 2
- **Dependencies:** dataclasses, enum, logging, pathlib, typing, yaml


## Classes

### EnforcementLevel

```python
class EnforcementLevel(Enum)
```

Company rule enforcement levels.



---

### RepositoryType

```python
class RepositoryType(Enum)
```

Repository types.



---

### ImplantGovernance

```python
class ImplantGovernance
```

**Decorators:** `dataclass`

Implant governance configuration.


**Attributes:**

- `version`: str
- `company_name`: str
- `division`: str
- `contact`: str
- `repo_name`: str
- `repo_type`: RepositoryType
- `language`: str
- `framework`: str
- `enforcement_level`: EnforcementLevel
- `block_on_violation`: bool
- `require_approval_override`: bool
- `rules_enabled`: List[str]
- `integration_flags`: Dict[str, bool]
- `priority`: str


**Methods:**

  #### `is_rule_enabled`

  ```python
  is_rule_enabled(self, rule_name: str) -> bool
  ```

  Check if a rule category is enabled.

  **Parameters:**

  - `self`
  - `rule_name` (str)


  **Returns:** bool



---

### CodingStandards

```python
class CodingStandards
```

**Decorators:** `dataclass`

Coding standards configuration.


**Attributes:**

- `naming_conventions`: Dict[str, Any]
- `file_organization`: Dict[str, Any]
- `code_style`: Dict[str, Any]
- `imports`: Dict[str, Any]
- `documentation`: Dict[str, Any]



---

### ArchitecturePatterns

```python
class ArchitecturePatterns
```

**Decorators:** `dataclass`

Architecture patterns configuration.


**Attributes:**

- `required_patterns`: List[Dict[str, Any]]
- `anti_patterns`: List[Dict[str, Any]]
- `layer_boundaries`: List[Dict[str, Any]]



---

### BusinessRules

```python
class BusinessRules
```

**Decorators:** `dataclass`

Business rules configuration.


**Attributes:**

- `domain_validations`: List[Dict[str, Any]]
- `workflow_rules`: List[Dict[str, Any]]
- `compliance`: List[Dict[str, Any]]



---

### TechStack

```python
class TechStack
```

**Decorators:** `dataclass`

Tech stack configuration.


**Attributes:**

- `approved_libraries`: Dict[str, List[Dict[str, Any]]]
- `forbidden_libraries`: List[Dict[str, Any]]
- `language_features`: Dict[str, Any]



---

### SecurityPolicy

```python
class SecurityPolicy
```

**Decorators:** `dataclass`

Security policy configuration.


**Attributes:**

- `authentication`: Dict[str, Any]
- `authorization`: Dict[str, Any]
- `data_protection`: Dict[str, Any]
- `input_validation`: Dict[str, Any]
- `secrets_management`: Dict[str, Any]



---

### CortexImplants

```python
class CortexImplants
```

**Decorators:** `dataclass`

Complete cortex implants configuration.


**Attributes:**

- `governance`: ImplantGovernance
- `coding_standards`: Optional[CodingStandards]
- `architecture_patterns`: Optional[ArchitecturePatterns]
- `business_rules`: Optional[BusinessRules]
- `tech_stack`: Optional[TechStack]
- `security_policy`: Optional[SecurityPolicy]
- `repo_path`: Path


**Methods:**

  #### `is_rule_enabled`

  ```python
  is_rule_enabled(self, rule_name: str) -> bool
  ```

  Check if a rule category is enabled.

  **Parameters:**

  - `self`
  - `rule_name` (str)


  **Returns:** bool


  #### `get_priority`

  ```python
  get_priority(self) -> str
  ```

  Get priority level (HIGH/MEDIUM/LOW).

  **Parameters:**

  - `self`


  **Returns:** str



---

### CortexImplantsLoader

```python
class CortexImplantsLoader
```

Loads cortex implants from .cortex-implants/ folders.

Features:
- Auto-detection of .cortex-implants/ in repo root
- Schema validation
- Caching for performance
- Repo boundary enforcement
- Version compatibility checking

Usage:
    loader = CortexImplantsLoader()
    implants = loader.load(repo_path)
    
    if implants.is_rule_enabled("CODING_STANDARDS"):
        standards = implants.coding_standards


**Methods:**

  #### `load`

  ```python
  load(self, repo_path: Path) -> Optional[CortexImplants]
  ```

  Load cortex implants from repository.

Args:
    repo_path: Path to repository root
    
Returns:
    CortexImplants object or None if not found
    
Raises:
    FileNotFoundError: If required files missing
    ValueError: If schema validation fails

  **Parameters:**

  - `self`
  - `repo_path` (Path): Path to repository root


  **Returns:** Optional[CortexImplants]
    CortexImplants object or None if not found


  #### `clear_cache`

  ```python
  clear_cache(self, repo_path: Optional[Path]) -> None
  ```

  Clear loader cache.

Args:
    repo_path: Clear specific repo, or all if None

  **Parameters:**

  - `self`
  - `repo_path` (Optional[Path]) = `None`: Clear specific repo, or all if None


  **Returns:** None


  #### `get_all_repos_with_cortex_implants`

  ```python
  get_all_repos_with_cortex_implants(self, workspace_root: Path) -> List[CortexImplants]
  ```

  Find all repos with .cortex-implants in workspace.

Args:
    workspace_root: VS Code workspace root
    
Returns:
    List of CortexImplants objects

  **Parameters:**

  - `self`
  - `workspace_root` (Path): VS Code workspace root


  **Returns:** List[CortexImplants]
    List of CortexImplants objects



---

## Functions

### get_cortex_implants_loader

```python
get_cortex_implants_loader() -> CortexImplantsLoader
```

Get singleton loader instance.


**Returns:** CortexImplantsLoader


---

### load_cortex_implants

```python
load_cortex_implants(repo_path: Path) -> Optional[CortexImplants]
```

Convenience function to load cortex implants.

Args:
    repo_path: Path to repository
    
Returns:
    CortexImplants or None


**Parameters:**

- `repo_path` (Path): Path to repository


**Returns:** Optional[CortexImplants]
  CortexImplants or None


---
