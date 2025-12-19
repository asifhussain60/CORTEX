# deploy_utility

Deploy Utility

Fast, lightweight deployment management for CORTEX production releases.
Replaces orchestrator with focused utility for deployment workflows.

Features:
- Pre-deployment validation (tests, lint, coverage)
- Architecture documentation sync via DocSyncHook
- Version bumping (semantic versioning)
- Git tagging and production branch deployment
- Dry-run mode for preview

Operations:
1. execute_deployment - Main deployment workflow
2. validate_pre_deployment - Run validation checks
3. sync_architecture_docs - Update ARCHITECTURE.md
4. bump_version - Increment version number
5. deploy_to_production - Deploy to production branch

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [execute_deployment](#execute_deployment)
- [validate_pre_deployment](#validate_pre_deployment)
- [sync_architecture_docs](#sync_architecture_docs)
- [bump_version](#bump_version)
- [deploy_to_production](#deploy_to_production)


## Overview

- **Classes:** 0
- **Functions:** 5
- **Dependencies:** logging, pathlib, src, subprocess, typing


## Functions

### execute_deployment

```python
execute_deployment(cortex_root: Path, dry_run: bool) -> Dict[str, Any]
```

Execute complete deployment workflow.

Args:
    cortex_root: Path to CORTEX repository root
    dry_run: If True, preview without making changes
    
Returns:
    Dict with deployment results:
        - success: bool
        - version: str (new version number)
        - architecture_synced: bool
        - message: str


**Parameters:**

- `cortex_root` (Path): Path to CORTEX repository root
- `dry_run` (bool) = `False`: If True, preview without making changes


**Returns:** Dict[str, Any]
  Dict with deployment results: - success: bool - version: str (new version number) - architecture_synced: bool - message: str


---

### validate_pre_deployment

```python
validate_pre_deployment(cortex_root: Path) -> Dict[str, Any]
```

Run pre-deployment validation checks.

Args:
    cortex_root: Path to CORTEX repository root
    
Returns:
    Dict with validation results:
        - success: bool
        - message: str


**Parameters:**

- `cortex_root` (Path): Path to CORTEX repository root


**Returns:** Dict[str, Any]
  Dict with validation results: - success: bool - message: str


---

### sync_architecture_docs

```python
sync_architecture_docs(cortex_root: Path, dry_run: bool) -> Dict[str, Any]
```

Synchronize architecture documentation before deployment.

Uses DocSyncHook to update ARCHITECTURE.md based on code changes.

Args:
    cortex_root: Path to CORTEX repository root
    dry_run: If True, show what would be updated
    
Returns:
    Dict with sync results:
        - success: bool
        - changes_detected: bool
        - files_updated: list
        - message: str


**Parameters:**

- `cortex_root` (Path): Path to CORTEX repository root
- `dry_run` (bool) = `False`: If True, show what would be updated


**Returns:** Dict[str, Any]
  Dict with sync results: - success: bool - changes_detected: bool - files_updated: list - message: str


---

### bump_version

```python
bump_version(cortex_root: Path, dry_run: bool) -> Dict[str, Any]
```

Bump version number in VERSION file.

Simple patch version increment (e.g., 3.2.1 -> 3.2.2).

Args:
    cortex_root: Path to CORTEX repository root
    dry_run: If True, show new version without writing
    
Returns:
    Dict with version bump results:
        - success: bool
        - version: str (new version)
        - previous_version: str
        - message: str


**Parameters:**

- `cortex_root` (Path): Path to CORTEX repository root
- `dry_run` (bool) = `False`: If True, show new version without writing


**Returns:** Dict[str, Any]
  Dict with version bump results: - success: bool - version: str (new version) - previous_version: str - message: str


---

### deploy_to_production

```python
deploy_to_production(cortex_root: Path, dry_run: bool) -> Dict[str, Any]
```

Deploy to production branch.

Args:
    cortex_root: Path to CORTEX repository root
    dry_run: If True, show deployment steps without executing
    
Returns:
    Dict with deployment results:
        - success: bool
        - message: str


**Parameters:**

- `cortex_root` (Path): Path to CORTEX repository root
- `dry_run` (bool) = `False`: If True, show deployment steps without executing


**Returns:** Dict[str, Any]
  Dict with deployment results: - success: bool - message: str


---
