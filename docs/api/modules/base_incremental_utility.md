# base_incremental_utility

Base Incremental Utility - Layer 2 Incremental Work Management Operations

Provides protocol and infrastructure for breaking work into manageable chunks
with checkpoint support. All orchestrators handling complex operations should
use these operations for incremental execution.

Part of CORTEX 3.2.1 - Incremental Work Management System
Sprint 10 Migration: base_incremental_orchestrator (421 lines) → base_incremental_utility (~500 lines)
Author: Asif Hussain

Operations:
- create_work_chunk: Create WorkChunk with validation
- create_checkpoint: Create WorkCheckpoint from completed work
- check_dependencies: Verify chunk dependencies satisfied
- is_checkpoint_boundary: Determine if checkpoint needed
- execute_incremental_workflow: Execute work with chunks, checkpoints, progress
- get_execution_summary: Get current execution statistics
- validate_chunk: Validate chunk configuration
- monitor_response_size: Check response size and auto-chunk if needed


## Table of Contents

### Classes
- [WorkChunk](#workchunk)
- [WorkCheckpoint](#workcheckpoint)
- [IncrementalExecutionContext](#incrementalexecutioncontext)

### Functions
- [create_work_chunk](#create_work_chunk)
- [create_checkpoint](#create_checkpoint)
- [check_dependencies](#check_dependencies)
- [is_checkpoint_boundary](#is_checkpoint_boundary)
- [validate_chunk](#validate_chunk)
- [monitor_response_size](#monitor_response_size)
- [get_execution_summary](#get_execution_summary)
- [execute_incremental_workflow](#execute_incremental_workflow)


## Overview

- **Classes:** 3
- **Functions:** 9
- **Dependencies:** dataclasses, datetime, logging, pathlib, src, time, typing


## Classes

### WorkChunk

```python
class WorkChunk
```

**Decorators:** `dataclass`

Represents a single unit of work in incremental execution.

Attributes:
    chunk_id: Unique identifier for this chunk
    chunk_type: Type classification (skeleton, phase, section, task, test, method)
    description: Human-readable description of what this chunk does
    estimated_tokens: Estimated response size in tokens
    dependencies: List of chunk_ids that must complete before this chunk
    status: Current execution status
    output_path: Optional file path where chunk output is written
    metadata: Additional chunk-specific data


**Attributes:**

- `chunk_id`: str
- `chunk_type`: str
- `description`: str
- `estimated_tokens`: int
- `dependencies`: List[str]
- `status`: str
- `output_path`: Optional[str]
- `metadata`: Dict[str, Any]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert chunk to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### WorkCheckpoint

```python
class WorkCheckpoint
```

**Decorators:** `dataclass`

Checkpoint for user approval and progress tracking.

Attributes:
    checkpoint_id: Unique identifier for this checkpoint
    chunks_completed: List of chunk_ids that have been completed
    preview: Summary of work done at this checkpoint
    approval_required: Whether user approval is needed to proceed
    feedback: User feedback on the checkpoint (set after approval)
    timestamp: When this checkpoint was created


**Attributes:**

- `checkpoint_id`: str
- `chunks_completed`: List[str]
- `preview`: str
- `approval_required`: bool
- `feedback`: Optional[str]
- `timestamp`: datetime


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert checkpoint to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### IncrementalExecutionContext

```python
class IncrementalExecutionContext
```

**Decorators:** `dataclass`

Context for incremental execution workflow.

Tracks state across chunk execution, checkpoint creation,
and progress monitoring.


**Attributes:**

- `chunks`: List[WorkChunk]
- `completed_chunk_ids`: List[str]
- `checkpoints`: List[WorkCheckpoint]
- `results`: List[Dict[str, Any]]
- `response_monitor`: Optional[ResponseSizeMonitor]
- `brain_path`: Optional[Path]
- `max_chunk_tokens`: int
- `checkpoint_interval`: int


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert context to dictionary for reporting

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

## Functions

### create_work_chunk

```python
create_work_chunk(chunk_id: str, chunk_type: str, description: str, estimated_tokens: int, dependencies: Optional[List[str]], status: str, output_path: Optional[str], metadata: Optional[Dict[str, Any]]) -> WorkChunk
```

Create a WorkChunk with validation.

Args:
    chunk_id: Unique identifier for this chunk
    chunk_type: Type classification (skeleton, phase, section, task, test, method)
    description: Human-readable description
    estimated_tokens: Estimated response size in tokens
    dependencies: List of chunk_ids that must complete before this chunk
    status: Current execution status (default: "pending")
    output_path: Optional file path where chunk output is written
    metadata: Additional chunk-specific data

Returns:
    WorkChunk object

Raises:
    ValueError: If chunk_type or status is invalid

Example:
    >>> chunk = create_work_chunk(
    ...     chunk_id="chunk-1",
    ...     chunk_type="phase",
    ...     description="Create Phase 1",
    ...     estimated_tokens=300
    ... )
    >>> chunk.status
    'pending'


**Parameters:**

- `chunk_id` (str): Unique identifier for this chunk
- `chunk_type` (str): Type classification (skeleton, phase, section, task, test, method)
- `description` (str): Human-readable description
- `estimated_tokens` (int): Estimated response size in tokens
- `dependencies` (Optional[List[str]]) = `None`: List of chunk_ids that must complete before this chunk
- `status` (str) = `'pending'`: Current execution status (default: "pending")
- `output_path` (Optional[str]) = `None`: Optional file path where chunk output is written
- `metadata` (Optional[Dict[str, Any]]) = `None`: Additional chunk-specific data


**Returns:** WorkChunk
  WorkChunk object


---

### create_checkpoint

```python
create_checkpoint(checkpoint_id: str, completed_chunks: List[WorkChunk], results: List[Dict[str, Any]], approval_required: bool) -> WorkCheckpoint
```

Create a checkpoint from completed work.

Generates preview summary of last 5 chunks and determines
if user approval is required based on chunk types.

Args:
    checkpoint_id: Unique identifier for this checkpoint
    completed_chunks: List of chunks completed so far
    results: Execution results for each chunk
    approval_required: Whether user approval is needed (default: False)

Returns:
    WorkCheckpoint object for user review

Example:
    >>> checkpoint = create_checkpoint(
    ...     checkpoint_id="checkpoint-1",
    ...     completed_chunks=[chunk1, chunk2],
    ...     results=[result1, result2],
    ...     approval_required=True
    ... )
    >>> checkpoint.approval_required
    True


**Parameters:**

- `checkpoint_id` (str): Unique identifier for this checkpoint
- `completed_chunks` (List[WorkChunk]): List of chunks completed so far
- `results` (List[Dict[str, Any]]): Execution results for each chunk
- `approval_required` (bool) = `False`: Whether user approval is needed (default: False)


**Returns:** WorkCheckpoint
  WorkCheckpoint object for user review


---

### check_dependencies

```python
check_dependencies(chunk: WorkChunk, completed_chunk_ids: List[str]) -> Tuple[bool, List[str]]
```

Check if all dependencies for a chunk are satisfied.

Args:
    chunk: Chunk to check
    completed_chunk_ids: List of chunk IDs that have been completed

Returns:
    Tuple of (satisfied: bool, missing_dependencies: List[str])
    - satisfied: True if all dependencies are met
    - missing_dependencies: List of dependency IDs not yet completed

Example:
    >>> chunk = create_work_chunk("chunk-2", "task", "Task 2", 100, dependencies=["chunk-1"])
    >>> satisfied, missing = check_dependencies(chunk, ["chunk-1"])
    >>> satisfied
    True
    >>> missing
    []


**Parameters:**

- `chunk` (WorkChunk): Chunk to check
- `completed_chunk_ids` (List[str]): List of chunk IDs that have been completed


**Returns:** Tuple[bool, List[str]]
  Tuple of (satisfied: bool, missing_dependencies: List[str]) - satisfied: True if all dependencies are met - missing_dependencies: List of dependency IDs not yet completed


---

### is_checkpoint_boundary

```python
is_checkpoint_boundary(chunk: WorkChunk, all_chunks: List[WorkChunk], checkpoint_interval: int) -> Tuple[bool, str]
```

Determine if a checkpoint should be created after this chunk.

Default checkpoint triggers:
1. After every checkpoint_interval chunks (default: 5)
2. After phase boundaries (chunk_type == "phase")
3. At the end of all chunks

Args:
    chunk: Current chunk that just completed
    all_chunks: All chunks in the work request
    checkpoint_interval: Create checkpoint every N chunks (default: 5)

Returns:
    Tuple of (should_checkpoint: bool, reason: str)
    - should_checkpoint: True if checkpoint should be created
    - reason: Explanation of why checkpoint triggered

Example:
    >>> chunk = create_work_chunk("chunk-5", "phase", "Phase 1", 300)
    >>> chunks = [create_work_chunk(f"chunk-{i}", "task", f"Task {i}", 100) for i in range(5)]
    >>> chunks.append(chunk)
    >>> should_create, reason = is_checkpoint_boundary(chunk, chunks)
    >>> should_create
    True
    >>> "phase" in reason.lower()
    True


**Parameters:**

- `chunk` (WorkChunk): Current chunk that just completed
- `all_chunks` (List[WorkChunk]): All chunks in the work request
- `checkpoint_interval` (int) = `5`: Create checkpoint every N chunks (default: 5)


**Returns:** Tuple[bool, str]
  Tuple of (should_checkpoint: bool, reason: str) - should_checkpoint: True if checkpoint should be created - reason: Explanation of why checkpoint triggered


---

### validate_chunk

```python
validate_chunk(chunk: WorkChunk) -> Tuple[bool, List[str]]
```

Validate chunk configuration.

Checks:
1. chunk_type is valid
2. status is valid
3. estimated_tokens is positive
4. chunk_id is non-empty
5. description is non-empty

Args:
    chunk: WorkChunk to validate

Returns:
    Tuple of (is_valid: bool, errors: List[str])
    - is_valid: True if chunk passes all validation checks
    - errors: List of validation error messages

Example:
    >>> chunk = create_work_chunk("chunk-1", "phase", "Phase 1", 300)
    >>> is_valid, errors = validate_chunk(chunk)
    >>> is_valid
    True
    >>> errors
    []


**Parameters:**

- `chunk` (WorkChunk): WorkChunk to validate


**Returns:** Tuple[bool, List[str]]
  Tuple of (is_valid: bool, errors: List[str]) - is_valid: True if chunk passes all validation checks - errors: List of validation error messages


---

### monitor_response_size

```python
monitor_response_size(output: str, response_monitor: ResponseSizeMonitor, chunk_id: str) -> Dict[str, Any]
```

Check response size and auto-chunk if needed.

Integrates with ResponseSizeMonitor to detect oversized outputs
and automatically write them to files.

Args:
    output: Output text to check
    response_monitor: ResponseSizeMonitor instance
    chunk_id: ID of chunk that produced this output

Returns:
    Dictionary with monitoring results:
    {
        "safe": bool,  # True if output size is safe
        "token_count": int,
        "auto_chunked": bool,  # True if output was auto-chunked to file
        "file_path": Optional[str]  # Path if auto-chunked
    }

Example:
    >>> monitor = create_monitor(Path("/path/to/brain"))
    >>> result = monitor_response_size("Short output", monitor, "chunk-1")
    >>> result["safe"]
    True
    >>> result["auto_chunked"]
    False


**Parameters:**

- `output` (str): Output text to check
- `response_monitor` (ResponseSizeMonitor): ResponseSizeMonitor instance
- `chunk_id` (str): ID of chunk that produced this output


**Returns:** Dict[str, Any]
  Dictionary with monitoring results: { "safe": bool,  # True if output size is safe "token_count": int, "auto_chunked": bool,  # True if output was auto-chunked to file "file_path": Optional[str]  # Path if auto-chunked }


---

### get_execution_summary

```python
get_execution_summary(context: IncrementalExecutionContext) -> Dict[str, Any]
```

Get summary of current execution state.

Args:
    context: IncrementalExecutionContext with execution state

Returns:
    Dictionary with execution statistics:
    {
        "completed_chunks": int,
        "total_chunks": int,
        "checkpoints_created": int,
        "checkpoint_details": List[Dict],
        "success_rate": float,
        "failed_chunks": List[str],
        "blocked_chunks": List[str]
    }

Example:
    >>> context = IncrementalExecutionContext()
    >>> context.chunks = [create_work_chunk(f"chunk-{i}", "task", f"Task {i}", 100) for i in range(3)]
    >>> context.completed_chunk_ids = ["chunk-0", "chunk-1"]
    >>> summary = get_execution_summary(context)
    >>> summary["completed_chunks"]
    2


**Parameters:**

- `context` (IncrementalExecutionContext): IncrementalExecutionContext with execution state


**Returns:** Dict[str, Any]
  Dictionary with execution statistics: { "completed_chunks": int, "total_chunks": int, "checkpoints_created": int, "checkpoint_details": List[Dict], "success_rate": float, "failed_chunks": List[str], "blocked_chunks": List[str] }


---

### execute_incremental_workflow

```python
execute_incremental_workflow(chunks: List[WorkChunk], chunk_executor: Callable[[WorkChunk], Dict[str, Any]], brain_path: Optional[Path], checkpoint_callback: Optional[Callable[[WorkCheckpoint], bool]], checkpoint_interval: int, max_chunk_tokens: int) -> Dict[str, Any]
```

**Decorators:** `with_progress`

Execute work incrementally with checkpoints and progress tracking.

This is the main workflow orchestrator for incremental execution.

Workflow:
1. Initialize execution context
2. Execute chunks sequentially, respecting dependencies
3. Create checkpoints at boundaries
4. Report progress continuously
5. Monitor response sizes with ResponseSizeMonitor

Args:
    chunks: List of WorkChunk objects to execute
    chunk_executor: Function to execute a single chunk
        Signature: (chunk: WorkChunk) -> Dict[str, Any]
        Must return: {"success": bool, "chunk_id": str, "output": str, ...}
    brain_path: Path to CORTEX brain directory (for response monitoring)
    checkpoint_callback: Optional function to call at checkpoints
        Signature: (checkpoint: WorkCheckpoint) -> bool
        Return True to continue, False to abort
    checkpoint_interval: Create checkpoint every N chunks (default: 5)
    max_chunk_tokens: Maximum tokens per chunk output (default: 500)

Returns:
    Dictionary with execution summary:
    {
        "success": bool,
        "chunks_executed": int,
        "checkpoints_created": int,
        "results": List[Dict],
        "aborted": bool,
        "error": Optional[str],
        "summary": Dict  # From get_execution_summary()
    }

Example:
    >>> def execute_chunk(chunk: WorkChunk) -> Dict[str, Any]:
    ...     # Execute chunk logic
    ...     return {"success": True, "chunk_id": chunk.chunk_id, "output": "result"}
    >>> chunks = [create_work_chunk(f"chunk-{i}", "task", f"Task {i}", 100) for i in range(3)]
    >>> result = execute_incremental_workflow(chunks, execute_chunk)
    >>> result["success"]
    True


**Parameters:**

- `chunks` (List[WorkChunk]): List of WorkChunk objects to execute
- `chunk_executor` (Callable[[WorkChunk], Dict[str, Any]]): Function to execute a single chunk
- `brain_path` (Optional[Path]) = `None`: Path to CORTEX brain directory (for response monitoring)
- `checkpoint_callback` (Optional[Callable[[WorkCheckpoint], bool]]) = `None`: Optional function to call at checkpoints
- `checkpoint_interval` (int) = `5`: Create checkpoint every N chunks (default: 5)
- `max_chunk_tokens` (int) = `500`: Maximum tokens per chunk output (default: 500)


**Returns:** Dict[str, Any]
  Dictionary with execution summary: { "success": bool, "chunks_executed": int, "checkpoints_created": int, "results": List[Dict], "aborted": bool, "error": Optional[str], "summary": Dict  # From get_execution_summary() }


---
