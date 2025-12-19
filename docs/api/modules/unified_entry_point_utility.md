# unified_entry_point_utility

Unified Entry Point Utility - CORTEX Operation Routing and Coordination

Universal routing system for all CORTEX operations with workflow execution,
summary generation, ADO-formatted output, and CLI wrapper routing.

Part of CORTEX 3.2.1 - Unified Entry Point System
Sprint 13a Migration: unified_entry_point_orchestrator (544 lines) → unified_entry_point_utility (~600 lines)
Phase 3 & 4 Enhancement: CLI wrapper routing for execution_method-based dispatch
Author: Asif Hussain

Operations:
- execute_code_review: Route to code review workflow
- execute_ado_story: Create and track ADO user story
- execute_ado_feature: Create and track ADO feature
- generate_work_summary: Generate ADO-formatted summary
- initialize_orchestrators: Dynamic orchestrator initialization
- generate_code_review_summary: Format code review results for ADO
- generate_story_summary: Format story creation for ADO
- generate_feature_summary: Format feature creation for ADO
- save_summary: Persist summary to filesystem
- format_priority: Convert priority number to label
- route_operation: Dispatch based on execution_method (cli_wrapper|copilot_chat|internal)
- invoke_cli_wrapper: Execute CLI wrapper script with arguments


## Table of Contents

### Classes
- [OperationType](#operationtype)
- [WorkflowResult](#workflowresult)
- [OrchestratorRegistry](#orchestratorregistry)

### Functions
- [initialize_orchestrators](#initialize_orchestrators)
- [execute_code_review](#execute_code_review)
- [execute_ado_story](#execute_ado_story)
- [execute_ado_feature](#execute_ado_feature)
- [generate_work_summary](#generate_work_summary)
- [perform_code_review](#perform_code_review)
- [generate_code_review_summary](#generate_code_review_summary)
- [generate_story_summary](#generate_story_summary)
- [generate_feature_summary](#generate_feature_summary)
- [save_summary](#save_summary)
- [format_priority](#format_priority)
- [review_pr](#review_pr)
- [create_user_story](#create_user_story)
- [create_feature](#create_feature)
- [check_planning_gate](#check_planning_gate)
- [route_operation](#route_operation)
- [invoke_cli_wrapper](#invoke_cli_wrapper)


## Overview

- **Classes:** 3
- **Functions:** 18
- **Dependencies:** dataclasses, datetime, enum, json, logging, pathlib, shutil, src, subprocess, sys, tempfile, time, typing


## Classes

### OperationType

```python
class OperationType(Enum)
```

Types of operations supported by unified entry point.



---

### WorkflowResult

```python
class WorkflowResult
```

**Decorators:** `dataclass`

Complete workflow execution result with metrics and output.


**Attributes:**

- `operation_type`: OperationType
- `success`: bool
- `work_item_id`: Optional[str]
- `files_created`: List[str]
- `files_modified`: List[str]
- `files_analyzed`: List[str]
- `tests_created`: List[str]
- `documentation_created`: List[str]
- `implementation_notes`: str
- `technical_decisions`: List[str]
- `issues_found`: List[Dict[str, Any]]
- `recommendations`: List[str]
- `duration_seconds`: float
- `test_coverage`: float
- `risk_score`: int
- `started_at`: datetime
- `completed_at`: Optional[datetime]
- `ado_summary`: Optional[str]


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

### OrchestratorRegistry

```python
class OrchestratorRegistry
```

**Decorators:** `dataclass`

Registry of available orchestrators.


**Attributes:**

- `code_review`: Optional[Any]
- `ado_work_item`: Optional[Any]
- `planning`: Optional[Any]


**Methods:**

  #### `is_available`

  ```python
  is_available(self, operation_type: OperationType) -> bool
  ```

  Check if orchestrator is available for operation type

  **Parameters:**

  - `self`
  - `operation_type` (OperationType)


  **Returns:** bool



---

## Functions

### initialize_orchestrators

```python
initialize_orchestrators(cortex_root: Path) -> OrchestratorRegistry
```

Initialize all available orchestrators dynamically.

Gracefully handles missing orchestrators, allowing partial functionality.

Args:
    cortex_root: CORTEX root directory

Returns:
    OrchestratorRegistry with available orchestrators

Example:
    >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
    >>> registry.is_available(OperationType.CODE_REVIEW)
    True


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** OrchestratorRegistry
  OrchestratorRegistry with available orchestrators


---

### execute_code_review

```python
execute_code_review(cortex_root: Path, registry: OrchestratorRegistry, pr_info: str, depth: str, focus_areas: Optional[List[str]]) -> WorkflowResult
```

Execute code review workflow with routing to specialized orchestrator.

Args:
    cortex_root: CORTEX root directory
    registry: OrchestratorRegistry with initialized orchestrators
    pr_info: PR link, ID, or diff text
    depth: Review depth (quick/standard/deep)
    focus_areas: Areas to focus on (security, performance, etc.)

Returns:
    WorkflowResult with code review analysis

Example:
    >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
    >>> result = execute_code_review(Path("/path"), registry, "PR#123")
    >>> result.success
    True
    >>> result.risk_score
    35


**Parameters:**

- `cortex_root` (Path): CORTEX root directory
- `registry` (OrchestratorRegistry): OrchestratorRegistry with initialized orchestrators
- `pr_info` (str): PR link, ID, or diff text
- `depth` (str) = `'standard'`: Review depth (quick/standard/deep)
- `focus_areas` (Optional[List[str]]) = `None`: Areas to focus on (security, performance, etc.)


**Returns:** WorkflowResult
  WorkflowResult with code review analysis


---

### execute_ado_story

```python
execute_ado_story(cortex_root: Path, registry: OrchestratorRegistry, title: str, description: str, acceptance_criteria: Optional[List[str]], **kwargs) -> WorkflowResult
```

Create ADO user story and track implementation.

Args:
    cortex_root: CORTEX root directory
    registry: OrchestratorRegistry with initialized orchestrators
    title: Story title
    description: Story description
    acceptance_criteria: List of acceptance criteria
    **kwargs: Additional metadata (priority, assigned_to, etc.)

Returns:
    WorkflowResult with story creation details

Example:
    >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
    >>> result = execute_ado_story(Path("/path"), registry, "User Login", "As a user...")
    >>> result.success
    True
    >>> result.work_item_id
    'STORY-12345'


**Parameters:**

- `cortex_root` (Path): CORTEX root directory
- `registry` (OrchestratorRegistry): OrchestratorRegistry with initialized orchestrators
- `title` (str): Story title
- `description` (str): Story description
- `acceptance_criteria` (Optional[List[str]]) = `None`: List of acceptance criteria
- `**kwargs`


**Returns:** WorkflowResult
  WorkflowResult with story creation details


---

### execute_ado_feature

```python
execute_ado_feature(cortex_root: Path, registry: OrchestratorRegistry, title: str, description: str, related_stories: Optional[List[str]], **kwargs) -> WorkflowResult
```

Create ADO feature and track implementation.

Args:
    cortex_root: CORTEX root directory
    registry: OrchestratorRegistry with initialized orchestrators
    title: Feature title
    description: Feature description
    related_stories: List of related story IDs
    **kwargs: Additional metadata (priority, assigned_to, etc.)

Returns:
    WorkflowResult with feature creation details

Example:
    >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
    >>> result = execute_ado_feature(Path("/path"), registry, "Authentication System", "...")
    >>> result.success
    True
    >>> result.work_item_id
    'FEATURE-678'


**Parameters:**

- `cortex_root` (Path): CORTEX root directory
- `registry` (OrchestratorRegistry): OrchestratorRegistry with initialized orchestrators
- `title` (str): Feature title
- `description` (str): Feature description
- `related_stories` (Optional[List[str]]) = `None`: List of related story IDs
- `**kwargs`


**Returns:** WorkflowResult
  WorkflowResult with feature creation details


---

### generate_work_summary

```python
generate_work_summary(registry: OrchestratorRegistry, work_item_id: str) -> Tuple[bool, str, Optional[str]]
```

Generate comprehensive work summary for ADO work item.

Args:
    registry: OrchestratorRegistry with initialized orchestrators
    work_item_id: Work item identifier

Returns:
    Tuple of (success, message, ado_markdown)

Example:
    >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
    >>> success, msg, markdown = generate_work_summary(registry, "STORY-12345")
    >>> success
    True
    >>> "# Work Summary" in markdown
    True


**Parameters:**

- `registry` (OrchestratorRegistry): OrchestratorRegistry with initialized orchestrators
- `work_item_id` (str): Work item identifier


**Returns:** Tuple[bool, str, Optional[str]]
  Tuple of (success, message, ado_markdown)


---

### perform_code_review

```python
perform_code_review(code_review_orch: Any, pr_info: str, depth: str, focus_areas: Optional[List[str]]) -> Dict[str, Any]
```

Perform code review analysis through orchestrator.

Args:
    code_review_orch: Code review orchestrator instance
    pr_info: PR information
    depth: Review depth
    focus_areas: Areas to focus on

Returns:
    Dictionary with review results

Example:
    >>> orch = CodeReviewOrchestrator("/path")
    >>> result = perform_code_review(orch, "PR#123", "standard", None)
    >>> result['files_analyzed']
    ['src/main.py', 'src/utils.py']


**Parameters:**

- `code_review_orch` (Any): Code review orchestrator instance
- `pr_info` (str): PR information
- `depth` (str): Review depth
- `focus_areas` (Optional[List[str]]): Areas to focus on


**Returns:** Dict[str, Any]
  Dictionary with review results


---

### generate_code_review_summary

```python
generate_code_review_summary(result: WorkflowResult) -> str
```

Generate ADO-formatted summary for code review results.

Args:
    result: WorkflowResult from code review execution

Returns:
    ADO-formatted Markdown string

Example:
    >>> result = WorkflowResult(operation_type=OperationType.CODE_REVIEW, success=True)
    >>> summary = generate_code_review_summary(result)
    >>> "# Code Review Summary" in summary
    True


**Parameters:**

- `result` (WorkflowResult): WorkflowResult from code review execution


**Returns:** str
  ADO-formatted Markdown string


---

### generate_story_summary

```python
generate_story_summary(result: WorkflowResult, metadata: Any) -> str
```

Generate ADO-formatted summary for user story creation.

Args:
    result: WorkflowResult from story creation
    metadata: Work item metadata from orchestrator

Returns:
    ADO-formatted Markdown string

Example:
    >>> result = WorkflowResult(operation_type=OperationType.ADO_STORY, success=True)
    >>> summary = generate_story_summary(result, metadata)
    >>> "# User Story Created" in summary
    True


**Parameters:**

- `result` (WorkflowResult): WorkflowResult from story creation
- `metadata` (Any): Work item metadata from orchestrator


**Returns:** str
  ADO-formatted Markdown string


---

### generate_feature_summary

```python
generate_feature_summary(result: WorkflowResult, metadata: Any) -> str
```

Generate ADO-formatted summary for feature creation.

Args:
    result: WorkflowResult from feature creation
    metadata: Work item metadata from orchestrator

Returns:
    ADO-formatted Markdown string

Example:
    >>> result = WorkflowResult(operation_type=OperationType.ADO_FEATURE, success=True)
    >>> summary = generate_feature_summary(result, metadata)
    >>> "# Feature Created" in summary
    True


**Parameters:**

- `result` (WorkflowResult): WorkflowResult from feature creation
- `metadata` (Any): Work item metadata from orchestrator


**Returns:** str
  ADO-formatted Markdown string


---

### save_summary

```python
save_summary(cortex_root: Path, result: WorkflowResult, category: str) -> bool
```

Save workflow summary to filesystem.

Args:
    cortex_root: CORTEX root directory
    result: WorkflowResult with summary
    category: Category for filing (code_review, story, feature)

Returns:
    True if saved successfully, False otherwise

Example:
    >>> success = save_summary(Path("/path"), result, "code_review")
    >>> success
    True


**Parameters:**

- `cortex_root` (Path): CORTEX root directory
- `result` (WorkflowResult): WorkflowResult with summary
- `category` (str): Category for filing (code_review, story, feature)


**Returns:** bool
  True if saved successfully, False otherwise


---

### format_priority

```python
format_priority(priority: int) -> str
```

Convert priority number to human-readable label.

Args:
    priority: Priority number (1-4)

Returns:
    Priority label string

Example:
    >>> format_priority(1)
    'High'
    >>> format_priority(3)
    'Low'


**Parameters:**

- `priority` (int): Priority number (1-4)


**Returns:** str
  Priority label string


---

### review_pr

```python
review_pr(pr_info: str, cortex_root: Path, depth: str, focus_areas: Optional[List[str]]) -> Dict[str, Any]
```

Convenience function for PR review with simplified interface.

Args:
    pr_info: PR link, ID, or diff
    cortex_root: Path to CORTEX root
    depth: Review depth
    focus_areas: Areas to focus on

Returns:
    Result dictionary with success status and summary

Example:
    >>> result = review_pr("PR#123", Path("/path/to/CORTEX"))
    >>> result['success']
    True
    >>> result['summary']
    '# Code Review Summary...'


**Parameters:**

- `pr_info` (str): PR link, ID, or diff
- `cortex_root` (Path): Path to CORTEX root
- `depth` (str) = `'standard'`: Review depth
- `focus_areas` (Optional[List[str]]) = `None`: Areas to focus on


**Returns:** Dict[str, Any]
  Result dictionary with success status and summary


---

### create_user_story

```python
create_user_story(title: str, description: str, cortex_root: Path, **kwargs) -> Dict[str, Any]
```

Convenience function for creating user story with simplified interface.

Args:
    title: Story title
    description: Story description
    cortex_root: Path to CORTEX root
    **kwargs: Additional metadata

Returns:
    Result dictionary with success status and details

Example:
    >>> result = create_user_story("Login Feature", "As a user...", Path("/path"))
    >>> result['success']
    True
    >>> result['work_item_id']
    'STORY-12345'


**Parameters:**

- `title` (str): Story title
- `description` (str): Story description
- `cortex_root` (Path): Path to CORTEX root
- `**kwargs`


**Returns:** Dict[str, Any]
  Result dictionary with success status and details


---

### create_feature

```python
create_feature(title: str, description: str, cortex_root: Path, **kwargs) -> Dict[str, Any]
```

Convenience function for creating feature with simplified interface.

Args:
    title: Feature title
    description: Feature description
    cortex_root: Path to CORTEX root
    **kwargs: Additional metadata

Returns:
    Result dictionary with success status and details

Example:
    >>> result = create_feature("Auth System", "Complete auth...", Path("/path"))
    >>> result['success']
    True
    >>> result['work_item_id']
    'FEATURE-678'


**Parameters:**

- `title` (str): Feature title
- `description` (str): Feature description
- `cortex_root` (Path): Path to CORTEX root
- `**kwargs`


**Returns:** Dict[str, Any]
  Result dictionary with success status and details


---

### check_planning_gate

```python
check_planning_gate(user_request: str, operation_id: str) -> Dict[str, Any]
```

Universal Planning Gate - ALL requests create temp plan first.

DESIGN PRINCIPLE: Planning is mandatory, not optional.
Every request creates temp plan → refine → approve → execute.
No "plan" keyword needed.

Args:
    user_request: User's original request
    operation_id: Operation being invoked
    
Returns:
    Dict with planning_required flag:
    {
        "planning_required": bool,
        "reason": str,
        "bypass_allowed": bool
    }


**Parameters:**

- `user_request` (str): User's original request
- `operation_id` (str): Operation being invoked


**Returns:** Dict[str, Any]
  Dict with planning_required flag: { "planning_required": bool, "reason": str, "bypass_allowed": bool }


---

### route_operation

```python
route_operation(operation_id: str, cortex_root: Path, operation_config: Dict[str, Any], **kwargs) -> Dict[str, Any]
```

Route operation based on execution_method field.

Dispatches to appropriate handler:
- cli_wrapper: Invoke CLI wrapper script
- copilot_chat: Return chat routing metadata
- internal: Log and reject (not user-invokable)

Args:
    operation_id: Operation identifier from cortex-operations.yaml
    cortex_root: CORTEX root directory
    operation_config: Operation configuration from YAML
    **kwargs: Additional arguments to pass to CLI wrapper

Returns:
    Dict with execution result:
    {
        "success": bool,
        "execution_method": str,
        "output": str,
        "exit_code": int,
        "message": str
    }

Example:
    >>> config = {"execution_method": "cli_wrapper", "cli_script": "scripts/cli_wrappers/align_wrapper.py"}
    >>> result = route_operation("align", Path("/cortex"), config)
    >>> result['success']
    True


**Parameters:**

- `operation_id` (str): Operation identifier from cortex-operations.yaml
- `cortex_root` (Path): CORTEX root directory
- `operation_config` (Dict[str, Any]): Operation configuration from YAML
- `**kwargs`


**Returns:** Dict[str, Any]
  Dict with execution result: { "success": bool, "execution_method": str, "output": str, "exit_code": int, "message": str }


---

### invoke_cli_wrapper

```python
invoke_cli_wrapper(operation_id: str, cortex_root: Path, cli_script: str, output_format: str, verbose: bool, **kwargs) -> Dict[str, Any]
```

Invoke CLI wrapper script and capture output.

Executes CLI wrapper with standard arguments (--output, --verbose, --project-root)
plus any custom arguments from kwargs.

Args:
    operation_id: Operation identifier
    cortex_root: CORTEX root directory
    cli_script: Relative path to CLI wrapper script
    output_format: Output format (text|json)
    verbose: Enable verbose output
    **kwargs: Additional CLI arguments (converted to --key value)

Returns:
    Dict with execution result:
    {
        "success": bool,
        "execution_method": "cli_wrapper",
        "output": str,
        "exit_code": int,
        "message": str,
        "duration_seconds": float
    }

Example:
    >>> result = invoke_cli_wrapper("align", Path("/cortex"), "scripts/cli_wrappers/align_wrapper.py", auto_fix=True)
    >>> result['success']
    True
    >>> result['exit_code']
    0


**Parameters:**

- `operation_id` (str): Operation identifier
- `cortex_root` (Path): CORTEX root directory
- `cli_script` (str): Relative path to CLI wrapper script
- `output_format` (str) = `'text'`: Output format (text|json)
- `verbose` (bool) = `False`: Enable verbose output
- `**kwargs`


**Returns:** Dict[str, Any]
  Dict with execution result: { "success": bool, "execution_method": "cli_wrapper", "output": str, "exit_code": int, "message": str, "duration_seconds": float }


---
