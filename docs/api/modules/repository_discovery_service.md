# repository_discovery_service

Repository Discovery Service

Automatically discovers, validates, and registers repositories for admin dashboard.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [RepoMetadata](#repometadata)
- [RepositoryDiscoveryService](#repositorydiscoveryservice)

### Functions
- [discover_and_register_repositories](#discover_and_register_repositories)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, src, typing


## Classes

### RepoMetadata

```python
class RepoMetadata
```

**Decorators:** `dataclass`

Repository metadata


**Attributes:**

- `id`: str
- `name`: str
- `path`: str
- `discovered`: str
- `last_updated`: str
- `status`: str
- `data_files`: int
- `data_file_list`: List[str]
- `file_sizes`: Dict[str, int]
- `total_size`: int



---

### RepositoryDiscoveryService

```python
class RepositoryDiscoveryService
```

Discovers and validates repositories in the data/repos/ directory.


**Methods:**

  #### `scan_repositories`

  ```python
  scan_repositories(self) -> List[RepoMetadata]
  ```

  Scan repos directory for valid repositories.

Returns:
    List of discovered repository metadata

  **Parameters:**

  - `self`


  **Returns:** List[RepoMetadata]
    List of discovered repository metadata


  #### `validate_repository`

  ```python
  validate_repository(self, repo_path: Path) -> bool
  ```

  Validate that directory contains valid repository data.

Args:
    repo_path: Path to repository directory

Returns:
    True if valid, False otherwise

  **Parameters:**

  - `self`
  - `repo_path` (Path): Path to repository directory


  **Returns:** bool
    True if valid, False otherwise


  #### `register_repositories`

  ```python
  register_repositories(self, repositories: List[RepoMetadata]) -> None
  ```

  Register discovered repositories in registry file.

Args:
    repositories: List of repository metadata to register

  **Parameters:**

  - `self`
  - `repositories` (List[RepoMetadata]): List of repository metadata to register


  **Returns:** None


  #### `remove_missing_repositories`

  ```python
  remove_missing_repositories(self) -> List[str]
  ```

  Remove repositories from registry that no longer exist.

Returns:
    List of removed repository IDs

  **Parameters:**

  - `self`


  **Returns:** List[str]
    List of removed repository IDs


  #### `get_repository_count`

  ```python
  get_repository_count(self) -> int
  ```

  Get total count of registered repositories

  **Parameters:**

  - `self`


  **Returns:** int


  #### `get_repository_by_id`

  ```python
  get_repository_by_id(self, repo_id: str) -> Optional[Dict[str, Any]]
  ```

  Get specific repository metadata

  **Parameters:**

  - `self`
  - `repo_id` (str)


  **Returns:** Optional[Dict[str, Any]]



---

## Functions

### discover_and_register_repositories

```python
discover_and_register_repositories() -> List[RepoMetadata]
```

Convenience function to discover and register all repositories.

Returns:
    List of discovered repositories


**Returns:** List[RepoMetadata]
  List of discovered repositories


---
