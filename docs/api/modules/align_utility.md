# align_utility

Minimal System Alignment Utility - Fast & Reliable Replacement

Lightweight replacement for SystemAlignmentOrchestrator that focuses on
essential system health checks without complex integration scoring.

Design Goals:
    - Execute in <5 seconds (full scan) or <2 seconds (incremental)
    - Clear pass/fail reporting
    - No complex dependencies
    - Admin-only execution
    - Actionable error messages
    - Auto-discovery and wiring validation
    - Incremental validation with file change tracking

Validation Checks (Phase 0 + 8 Core):
    Phase 0: Documentation Sync
        - CORTEX.prompt.md and copilot-instructions.md synchronization
        - Response format consistency
        - Document organization rules alignment
        - Version number matching
    
    Core Checks:
        1. Brain tier structure (tier0-3)
        2. Protection rules (brain-protection-rules.yaml)
        3. Response templates (response-templates.yaml)
        4. Working memory database
        5. Knowledge graph database
        6. Development context database
        7. Core Python modules (orchestrators/agents)
        8. Configuration file (cortex.config.json)

Enhancement Features (v3.2):
    - File change detection via SHA256 checksums
    - Incremental validation (only check changed features)
    - Auto-wiring discovery and validation
    - Admin vs User context detection
    - Performance metrics tracking

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.2 (Incremental)
Status: PRODUCTION


## Table of Contents

### Classes
- [ValidationResult](#validationresult)
- [AlignmentReport](#alignmentreport)
- [AlignUtility](#alignutility)

### Functions
- [safe_print](#safe_print)
- [run_align_utility](#run_align_utility)


## Overview

- **Classes:** 3
- **Functions:** 2
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, re, sqlite3, src, sys, time, typing, yaml


## Classes

### ValidationResult

```python
class ValidationResult
```

**Decorators:** `dataclass`

Result of a single validation check.


**Attributes:**

- `check_name`: str
- `passed`: bool
- `message`: str
- `details`: str
- `severity`: str


**Methods:**


---

### AlignmentReport

```python
class AlignmentReport
```

**Decorators:** `dataclass`

Complete system alignment report.


**Attributes:**

- `timestamp`: datetime
- `checks`: List[ValidationResult]
- `execution_time`: float


**Methods:**

  #### `passed_count`

  *Decorators:* `property`

  ```python
  passed_count(self) -> int
  ```

  Count of passed checks.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `total_count`

  *Decorators:* `property`

  ```python
  total_count(self) -> int
  ```

  Total checks executed.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `is_healthy`

  *Decorators:* `property`

  ```python
  is_healthy(self) -> bool
  ```

  System considered healthy if all ERROR-level checks pass.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `status_text`

  *Decorators:* `property`

  ```python
  status_text(self) -> str
  ```

  Human-readable status.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `format_console`

  ```python
  format_console(self) -> str
  ```

  Format report for console output.

  **Parameters:**

  - `self`


  **Returns:** str



---

### AlignUtility

```python
class AlignUtility
```

Minimal system alignment validator - fast and reliable with incremental support.


**Methods:**

  #### `validate_prompt_sync`

  ```python
  validate_prompt_sync(self) -> ValidationResult
  ```

  Phase 0: Check that CORTEX.prompt.md and copilot-instructions.md are synchronized.

Validates:
- Both files exist
- Response format section is consistent
- Document organization rules are consistent
- Version numbers match

  **Parameters:**

  - `self`


  **Returns:** ValidationResult


  #### `validate_brain_structure`

  ```python
  validate_brain_structure(self) -> ValidationResult
  ```

  Check that all 4 brain tiers exist.

  **Parameters:**

  - `self`


  **Returns:** ValidationResult


  #### `validate_protection_rules`

  ```python
  validate_protection_rules(self) -> ValidationResult
  ```

  Check brain-protection-rules.yaml exists and is valid.

  **Parameters:**

  - `self`


  **Returns:** ValidationResult


  #### `validate_response_templates`

  ```python
  validate_response_templates(self) -> ValidationResult
  ```

  Check response-templates.yaml exists and is valid.

  **Parameters:**

  - `self`


  **Returns:** ValidationResult


  #### `validate_database`

  ```python
  validate_database(self, db_name: str, tier: int, friendly_name: str) -> ValidationResult
  ```

  Validate a specific brain database.

  **Parameters:**

  - `self`
  - `db_name` (str)
  - `tier` (int)
  - `friendly_name` (str)


  **Returns:** ValidationResult


  #### `validate_core_modules`

  ```python
  validate_core_modules(self) -> ValidationResult
  ```

  Check that core Python modules exist (orchestrators, agents).

  **Parameters:**

  - `self`


  **Returns:** ValidationResult


  #### `validate_configuration`

  ```python
  validate_configuration(self) -> ValidationResult
  ```

  Check cortex.config.json exists and is valid.

  **Parameters:**

  - `self`


  **Returns:** ValidationResult


  #### `validate_feature_discovery`

  ```python
  validate_feature_discovery(self) -> ValidationResult
  ```

  Comprehensive feature discovery across 11 categories (admin context only).

  **Parameters:**

  - `self`


  **Returns:** ValidationResult


  #### `validate_code_quality`

  ```python
  validate_code_quality(self) -> ValidationResult
  ```

  Validate CORTEX code quality using TDD Implementation Orchestrator detection.

Runs comprehensive code quality checks:
- Security vulnerabilities (SQL injection, credentials, error handling)
- Magic values (repeated strings, hardcoded URLs, magic numbers)
- SOLID violations (god classes/methods, tight coupling, complexity)
- Code duplicates
- Redundancies (unused imports, dead code)

Leverages enhanced TDD orchestrator capabilities from sample app analysis.
Only runs in admin context on CORTEX source code.

Returns:
    ValidationResult with code quality status

  **Parameters:**

  - `self`


  **Returns:** ValidationResult
    ValidationResult with code quality status


  #### `validate_feature_wiring`

  ```python
  validate_feature_wiring(self) -> ValidationResult
  ```

  Validate that discovered features are properly wired into CORTEX.

Checks wiring for:
- Orchestrators (response-templates.yaml)
- Agents (response-templates.yaml)
- Plugins (plugin_registry.py)
- Operation Modules (cortex-operations.yaml)
- Workflows (cortex-operations.yaml or response-templates.yaml)
- Scripts (cortex-operations.yaml for user-facing)
- Dashboards (dashboard operation exists)
- Templates (all operations have templates)
- Operations (all operations registered)

Returns:
    ValidationResult with wiring status

  **Parameters:**

  - `self`


  **Returns:** ValidationResult
    ValidationResult with wiring status


  #### `scan_directory`

  ```python
  scan_directory(self, directory_path: str, pattern: str, exclude: List[str]) -> List[Path]
  ```

  Scan directory for files matching pattern.

Args:
    directory_path: Relative path from root (e.g., 'src/plugins/')
    pattern: Glob pattern to match (e.g., '*_plugin.py')
    exclude: List of paths to exclude (e.g., ['__pycache__/', '_archive/'])

Returns:
    List of Path objects matching pattern

  **Parameters:**

  - `self`
  - `directory_path` (str): Relative path from root (e.g., 'src/plugins/')
  - `pattern` (str) = `'*.py'`: Glob pattern to match (e.g., '*_plugin.py')
  - `exclude` (List[str]) = `None`: List of paths to exclude (e.g., ['__pycache__/', '_archive/'])


  **Returns:** List[Path]
    List of Path objects matching pattern


  #### `scan_yaml`

  ```python
  scan_yaml(self, yaml_path: str) -> Dict[str, Any]
  ```

  Scan YAML file for feature metadata.

Args:
    yaml_path: Path to YAML file (supports glob patterns like 'workflows/*.yaml')

Returns:
    Dictionary of parsed YAML data or empty dict on error

  **Parameters:**

  - `self`
  - `yaml_path` (str): Path to YAML file (supports glob patterns like 'workflows/*.yaml')


  **Returns:** Dict[str, Any]
    Dictionary of parsed YAML data or empty dict on error


  #### `discover_python_modules`

  ```python
  discover_python_modules(self) -> Tuple[List[Path], List[Path]]
  ```

  Discover Python orchestrators and agents.

Returns:
    Tuple of (orchestrator_paths, agent_paths)

  **Parameters:**

  - `self`


  **Returns:** Tuple[List[Path], List[Path]]
    Tuple of (orchestrator_paths, agent_paths)


  #### `discover_all_features`

  ```python
  discover_all_features(self) -> Dict[str, Any]
  ```

  Comprehensive feature discovery across all 11 CORTEX categories.

Returns:
    Dictionary mapping feature categories to discovered items:
    {
        'orchestrators': List[Path],
        'agents': List[Path],
        'operations': Dict (from YAML),
        'templates': Dict (from YAML),
        'plugins': List[Path],
        'scripts': List[Path],
        'operation_modules': List[Path],
        'workflows': Dict (from YAML),
        'brain_operations': List[Path],
        'dashboards': Dict[str, List[Path]],
        'governance_rules': List[Path]
    }

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary mapping feature categories to discovered items: { 'orchestrators': List[Path], 'agents': List[Path], 'operations': Dict (from YAML), 'templates': Dict (from YAML), 'plugins': List[Path], 'scripts': List[Path], 'operation_modules': List[Path], 'workflows': Dict (from YAML), 'brain_operations': List[Path], 'dashboards': Dict[str, List[Path]], 'governance_rules': List[Path] }


  #### `check_wiring_in_templates`

  ```python
  check_wiring_in_templates(self, module_name: str) -> bool
  ```

  Check if module is wired in response-templates.yaml.

Args:
    module_name: Name of orchestrator/agent class
    
Returns:
    True if wired, False otherwise

  **Parameters:**

  - `self`
  - `module_name` (str): Name of orchestrator/agent class


  **Returns:** bool
    True if wired, False otherwise


  #### `check_plugin_registration`

  ```python
  check_plugin_registration(self, plugin_name: str) -> bool
  ```

  Check if plugin is registered in plugin_registry.py.

Args:
    plugin_name: Name of plugin (e.g., 'performance_telemetry_plugin')
    
Returns:
    True if registered, False otherwise

  **Parameters:**

  - `self`
  - `plugin_name` (str): Name of plugin (e.g., 'performance_telemetry_plugin')


  **Returns:** bool
    True if registered, False otherwise


  #### `check_operation_module_linkage`

  ```python
  check_operation_module_linkage(self, module_name: str) -> bool
  ```

  Check if operation module is referenced by parent operation.

Args:
    module_name: Name of module (e.g., 'dashboard_launcher_module')
    
Returns:
    True if linked, False otherwise

  **Parameters:**

  - `self`
  - `module_name` (str): Name of module (e.g., 'dashboard_launcher_module')


  **Returns:** bool
    True if linked, False otherwise


  #### `check_workflow_triggers`

  ```python
  check_workflow_triggers(self, workflow_name: str) -> bool
  ```

  Check if workflow has trigger configuration.

Args:
    workflow_name: Name of workflow (e.g., 'feature_development')
    
Returns:
    True if has triggers, False otherwise

  **Parameters:**

  - `self`
  - `workflow_name` (str): Name of workflow (e.g., 'feature_development')


  **Returns:** bool
    True if has triggers, False otherwise


  #### `check_dashboard_accessibility`

  ```python
  check_dashboard_accessibility(self, dashboard_name: str) -> bool
  ```

  Check if dashboard is accessible via operation.

Args:
    dashboard_name: Name of dashboard (e.g., 'alignment-dashboard')
    
Returns:
    True if accessible, False otherwise

  **Parameters:**

  - `self`
  - `dashboard_name` (str): Name of dashboard (e.g., 'alignment-dashboard')


  **Returns:** bool
    True if accessible, False otherwise


  #### `validate_manifest_compliance`

  ```python
  validate_manifest_compliance(self) -> ValidationResult
  ```

  Validate orchestrator manifest compliance.

Checks:
- Manifest files exist
- Planning System 2.0 manifest compliance
- ADO planning manifest inheritance

Returns:
    ValidationResult with compliance status

  **Parameters:**

  - `self`


  **Returns:** ValidationResult
    ValidationResult with compliance status


  #### `check_script_operation_linkage`

  ```python
  check_script_operation_linkage(self, script_name: str) -> bool
  ```

  Check if user-facing script is linked to an operation.

Args:
    script_name: Name of script (e.g., 'cortex-upgrade')
    
Returns:
    True if linked, False otherwise

  **Parameters:**

  - `self`
  - `script_name` (str): Name of script (e.g., 'cortex-upgrade')


  **Returns:** bool
    True if linked, False otherwise


  #### `compute_file_checksums`

  ```python
  compute_file_checksums(self, file_paths: List[Path]) -> Dict[str, Dict[str, Any]]
  ```

  Compute SHA256 checksums for files.

Args:
    file_paths: List of file paths to checksum
    
Returns:
    Dictionary mapping file path to checksum metadata

  **Parameters:**

  - `self`
  - `file_paths` (List[Path]): List of file paths to checksum


  **Returns:** Dict[str, Dict[str, Any]]
    Dictionary mapping file path to checksum metadata


  #### `detect_changes`

  ```python
  detect_changes(self, previous_state: Optional[AlignmentState]) -> ChangesSummary
  ```

  Detect file changes since last alignment.

Args:
    previous_state: Previous alignment state or None
    
Returns:
    ChangesSummary with lists of added/modified/deleted files

  **Parameters:**

  - `self`
  - `previous_state` (Optional[AlignmentState]): Previous alignment state or None


  **Returns:** ChangesSummary
    ChangesSummary with lists of added/modified/deleted files


  #### `run_alignment`

  ```python
  run_alignment(self) -> AlignmentReport
  ```

  Execute validation checks with incremental support.

Returns:
    AlignmentReport with results and performance metrics

  **Parameters:**

  - `self`


  **Returns:** AlignmentReport
    AlignmentReport with results and performance metrics



---

## Functions

### safe_print

```python
safe_print(message: str) -> None
```

Print with Unicode fallback for Windows console encoding issues.


**Parameters:**

- `message` (str)


**Returns:** None


---

### run_align_utility

```python
run_align_utility(force_full: bool, quick_mode: bool) -> Dict[str, Any]
```

Entry point for align utility - callable from orchestrators or CLI.

Args:
    force_full: Force full scan even if incremental is possible
    quick_mode: Infrastructure checks only, skip feature validation

Returns:
    Dict with 'success', 'message', 'report_text', 'report_data', 'performance'


**Parameters:**

- `force_full` (bool) = `False`: Force full scan even if incremental is possible
- `quick_mode` (bool) = `False`: Infrastructure checks only, skip feature validation


**Returns:** Dict[str, Any]
  Dict with 'success', 'message', 'report_text', 'report_data', 'performance'


---
