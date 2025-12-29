"""
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
"""

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.utils.progress_decorator import with_progress, yield_progress
from src.utils.response_monitor import ResponseSizeMonitor, create_monitor

logger = logging.getLogger(__name__)


# ========================================
# Data Classes
# ========================================

@dataclass
class WorkChunk:
    """
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
    """
    chunk_id: str
    chunk_type: str  # skeleton, phase, section, task, test, method
    description: str
    estimated_tokens: int
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in-progress, complete, blocked, failed
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary for serialization"""
        return asdict(self)


@dataclass
class WorkCheckpoint:
    """
    Checkpoint for user approval and progress tracking.
    
    Attributes:
        checkpoint_id: Unique identifier for this checkpoint
        chunks_completed: List of chunk_ids that have been completed
        preview: Summary of work done at this checkpoint
        approval_required: Whether user approval is needed to proceed
        feedback: User feedback on the checkpoint (set after approval)
        timestamp: When this checkpoint was created
    """
    checkpoint_id: str
    chunks_completed: List[str]
    preview: str
    approval_required: bool
    feedback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary for serialization"""
        return {
            "checkpoint_id": self.checkpoint_id,
            "chunks_completed": self.chunks_completed,
            "preview": self.preview,
            "approval_required": self.approval_required,
            "feedback": self.feedback,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class IncrementalExecutionContext:
    """
    Context for incremental execution workflow.
    
    Tracks state across chunk execution, checkpoint creation,
    and progress monitoring.
    """
    chunks: List[WorkChunk] = field(default_factory=list)
    completed_chunk_ids: List[str] = field(default_factory=list)
    checkpoints: List[WorkCheckpoint] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    response_monitor: Optional[ResponseSizeMonitor] = None
    brain_path: Optional[Path] = None
    
    # Configuration
    max_chunk_tokens: int = 500
    checkpoint_interval: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for reporting"""
        return {
            "total_chunks": len(self.chunks),
            "completed_chunks": len(self.completed_chunk_ids),
            "checkpoints_created": len(self.checkpoints),
            "results_count": len(self.results),
            "max_chunk_tokens": self.max_chunk_tokens,
            "checkpoint_interval": self.checkpoint_interval
        }


# ========================================
# Core Operations
# ========================================

def create_work_chunk(
    chunk_id: str,
    chunk_type: str,
    description: str,
    estimated_tokens: int,
    dependencies: Optional[List[str]] = None,
    status: str = "pending",
    output_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> WorkChunk:
    """
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
    """
    valid_types = {"skeleton", "phase", "section", "task", "test", "method"}
    if chunk_type not in valid_types:
        raise ValueError(f"Invalid chunk_type: {chunk_type}. Must be one of {valid_types}")
    
    valid_statuses = {"pending", "in-progress", "complete", "blocked", "failed"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
    
    chunk = WorkChunk(
        chunk_id=chunk_id,
        chunk_type=chunk_type,
        description=description,
        estimated_tokens=estimated_tokens,
        dependencies=dependencies or [],
        status=status,
        output_path=output_path,
        metadata=metadata or {}
    )
    
    logger.debug(f"✨ Created WorkChunk: {chunk_id} ({chunk_type})")
    return chunk


def create_checkpoint(
    checkpoint_id: str,
    completed_chunks: List[WorkChunk],
    results: List[Dict[str, Any]],
    approval_required: bool = False
) -> WorkCheckpoint:
    """
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
    """
    chunk_ids = [c.chunk_id for c in completed_chunks]
    
    # Generate preview summary
    preview_lines = [
        f"📊 **Checkpoint: {len(completed_chunks)} chunks completed**\n",
        "**Completed Work:**"
    ]
    
    # Show last 5 chunks
    recent_chunks = completed_chunks[-5:]
    recent_results = results[-5:]
    
    for chunk, result in zip(recent_chunks, recent_results):
        status_icon = "✅" if result.get("success") else "❌"
        preview_lines.append(f"  {status_icon} {chunk.description}")
    
    if len(completed_chunks) > 5:
        preview_lines.insert(2, f"  ... ({len(completed_chunks) - 5} earlier chunks)")
    
    preview = "\n".join(preview_lines)
    
    # Auto-detect if approval required (phase boundaries)
    if not approval_required:
        approval_required = any(c.chunk_type == "phase" for c in recent_chunks)
    
    checkpoint = WorkCheckpoint(
        checkpoint_id=checkpoint_id,
        chunks_completed=chunk_ids,
        preview=preview,
        approval_required=approval_required
    )
    
    logger.info(f"📍 Checkpoint created: {checkpoint_id}")
    return checkpoint


def check_dependencies(
    chunk: WorkChunk,
    completed_chunk_ids: List[str]
) -> Tuple[bool, List[str]]:
    """
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
    """
    missing = [dep_id for dep_id in chunk.dependencies if dep_id not in completed_chunk_ids]
    satisfied = len(missing) == 0
    
    if not satisfied:
        logger.debug(f"⚠️ Chunk {chunk.chunk_id} missing dependencies: {missing}")
    
    return satisfied, missing


def is_checkpoint_boundary(
    chunk: WorkChunk,
    all_chunks: List[WorkChunk],
    checkpoint_interval: int = 5
) -> Tuple[bool, str]:
    """
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
    """
    try:
        chunk_index = all_chunks.index(chunk)
    except ValueError:
        logger.warning(f"⚠️ Chunk {chunk.chunk_id} not found in all_chunks list")
        return False, "chunk not in list"
    
    # Checkpoint at phase boundaries
    if chunk.chunk_type == "phase":
        return True, f"Phase boundary (type: {chunk.chunk_type})"
    
    # Checkpoint at regular intervals
    if (chunk_index + 1) % checkpoint_interval == 0:
        return True, f"Regular interval ({chunk_index + 1} chunks)"
    
    # Checkpoint at the end
    if chunk_index == len(all_chunks) - 1:
        return True, "Final chunk"
    
    return False, "No checkpoint trigger"


def validate_chunk(chunk: WorkChunk) -> Tuple[bool, List[str]]:
    """
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
    """
    errors = []
    
    valid_types = {"skeleton", "phase", "section", "task", "test", "method"}
    if chunk.chunk_type not in valid_types:
        errors.append(f"Invalid chunk_type: {chunk.chunk_type}. Must be one of {valid_types}")
    
    valid_statuses = {"pending", "in-progress", "complete", "blocked", "failed"}
    if chunk.status not in valid_statuses:
        errors.append(f"Invalid status: {chunk.status}. Must be one of {valid_statuses}")
    
    if chunk.estimated_tokens <= 0:
        errors.append(f"estimated_tokens must be positive, got: {chunk.estimated_tokens}")
    
    if not chunk.chunk_id or not chunk.chunk_id.strip():
        errors.append("chunk_id cannot be empty")
    
    if not chunk.description or not chunk.description.strip():
        errors.append("description cannot be empty")
    
    is_valid = len(errors) == 0
    
    if not is_valid:
        logger.warning(f"❌ Chunk {chunk.chunk_id} validation failed: {errors}")
    
    return is_valid, errors


def monitor_response_size(
    output: str,
    response_monitor: ResponseSizeMonitor,
    chunk_id: str
) -> Dict[str, Any]:
    """
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
    """
    check_result = response_monitor.check_response(output)
    
    result = {
        "safe": check_result.safe,
        "token_count": check_result.token_count,
        "auto_chunked": not check_result.safe,
        "file_path": str(check_result.file_path) if check_result.file_path else None
    }
    
    if not check_result.safe:
        logger.warning(
            f"⚠️ Chunk {chunk_id} output too large ({check_result.token_count} tokens), "
            f"auto-chunked to {check_result.file_path}"
        )
    
    return result


def get_execution_summary(context: IncrementalExecutionContext) -> Dict[str, Any]:
    """
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
    """
    total_chunks = len(context.chunks)
    completed_chunks = len(context.completed_chunk_ids)
    
    # Calculate success rate
    successful_results = sum(1 for r in context.results if r.get("success", False))
    success_rate = (successful_results / len(context.results)) if context.results else 0.0
    
    # Identify failed and blocked chunks
    failed_chunks = [c.chunk_id for c in context.chunks if c.status == "failed"]
    blocked_chunks = [c.chunk_id for c in context.chunks if c.status == "blocked"]
    
    return {
        "completed_chunks": completed_chunks,
        "total_chunks": total_chunks,
        "checkpoints_created": len(context.checkpoints),
        "checkpoint_details": [cp.to_dict() for cp in context.checkpoints],
        "success_rate": success_rate,
        "failed_chunks": failed_chunks,
        "blocked_chunks": blocked_chunks,
        "context": context.to_dict()
    }


@with_progress(operation_name="Incremental Work Execution")
def execute_incremental_workflow(
    chunks: List[WorkChunk],
    chunk_executor: Callable[[WorkChunk], Dict[str, Any]],
    brain_path: Optional[Path] = None,
    checkpoint_callback: Optional[Callable[[WorkCheckpoint], bool]] = None,
    checkpoint_interval: int = 5,
    max_chunk_tokens: int = 500
) -> Dict[str, Any]:
    """
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
    """
    context = IncrementalExecutionContext(
        chunks=chunks,
        brain_path=brain_path,
        max_chunk_tokens=max_chunk_tokens,
        checkpoint_interval=checkpoint_interval,
        response_monitor=create_monitor(brain_path) if brain_path else None
    )
    
    try:
        logger.info(f"🚀 Starting incremental execution with {len(chunks)} chunks")
        
        # Execute chunks with progress tracking
        for i, chunk in enumerate(chunks, 1):
            # Check dependencies
            satisfied, missing = check_dependencies(chunk, context.completed_chunk_ids)
            if not satisfied:
                logger.warning(f"⚠️ Chunk {chunk.chunk_id} blocked by dependencies: {missing}")
                chunk.status = "blocked"
                continue
            
            # Report progress
            yield_progress(i, len(chunks), f"Executing: {chunk.description}")
            
            # Execute chunk
            chunk.status = "in-progress"
            try:
                result = chunk_executor(chunk)
                
                # Monitor response size if available
                if context.response_monitor and "output" in result:
                    monitor_result = monitor_response_size(
                        result["output"],
                        context.response_monitor,
                        chunk.chunk_id
                    )
                    result.update(monitor_result)
                
                chunk.status = "complete"
                context.results.append(result)
                context.completed_chunk_ids.append(chunk.chunk_id)
                
            except Exception as e:
                logger.error(f"❌ Chunk {chunk.chunk_id} failed: {e}")
                chunk.status = "failed"
                context.results.append({
                    "success": False,
                    "chunk_id": chunk.chunk_id,
                    "error": str(e)
                })
            
            # Check for checkpoint boundary
            should_checkpoint, reason = is_checkpoint_boundary(
                chunk, chunks, context.checkpoint_interval
            )
            
            if should_checkpoint:
                completed_chunks = [c for c in chunks if c.chunk_id in context.completed_chunk_ids]
                checkpoint = create_checkpoint(
                    checkpoint_id=f"checkpoint-{len(context.checkpoints) + 1}",
                    completed_chunks=completed_chunks,
                    results=context.results
                )
                context.checkpoints.append(checkpoint)
                
                logger.info(f"📍 Checkpoint created: {checkpoint.checkpoint_id} ({reason})")
                
                # Call checkpoint callback if provided
                if checkpoint_callback and checkpoint.approval_required:
                    approved = checkpoint_callback(checkpoint)
                    checkpoint.feedback = "approved" if approved else "rejected"
                    
                    if not approved:
                        logger.warning("⛔ User rejected checkpoint, aborting execution")
                        summary = get_execution_summary(context)
                        return {
                            "success": False,
                            "chunks_executed": len(context.results),
                            "checkpoints_created": len(context.checkpoints),
                            "results": context.results,
                            "aborted": True,
                            "reason": "User rejected checkpoint",
                            "summary": summary
                        }
        
        logger.info(f"✅ Incremental execution complete: {len(context.results)} chunks executed")
        summary = get_execution_summary(context)
        
        return {
            "success": True,
            "chunks_executed": len(context.results),
            "checkpoints_created": len(context.checkpoints),
            "results": context.results,
            "aborted": False,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ Incremental execution failed: {e}")
        summary = get_execution_summary(context)
        return {
            "success": False,
            "chunks_executed": len(context.results),
            "checkpoints_created": len(context.checkpoints),
            "results": context.results,
            "aborted": True,
            "error": str(e),
            "summary": summary
        }


# ========================================
# Self-Test
# ========================================

def _run_self_tests() -> None:
    """Self-test for base incremental utility operations"""
    import time
    
    print("🧪 Running Base Incremental Utility Self-Tests...\n")
    start_time = time.time()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: create_work_chunk
    tests_total += 1
    try:
        chunk = create_work_chunk(
            chunk_id="test-chunk-1",
            chunk_type="phase",
            description="Test Phase 1",
            estimated_tokens=300
        )
        assert chunk.chunk_id == "test-chunk-1"
        assert chunk.status == "pending"
        print("✅ Test 1: create_work_chunk - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: create_work_chunk - FAILED: {e}")
    
    # Test 2: validate_chunk
    tests_total += 1
    try:
        chunk = create_work_chunk("chunk-2", "task", "Task 2", 100)
        is_valid, errors = validate_chunk(chunk)
        assert is_valid
        assert len(errors) == 0
        print("✅ Test 2: validate_chunk - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: validate_chunk - FAILED: {e}")
    
    # Test 3: check_dependencies
    tests_total += 1
    try:
        chunk = create_work_chunk("chunk-3", "task", "Task 3", 100, dependencies=["chunk-1", "chunk-2"])
        satisfied, missing = check_dependencies(chunk, ["chunk-1"])
        assert not satisfied
        assert "chunk-2" in missing
        
        satisfied, missing = check_dependencies(chunk, ["chunk-1", "chunk-2"])
        assert satisfied
        assert len(missing) == 0
        print("✅ Test 3: check_dependencies - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: check_dependencies - FAILED: {e}")
    
    # Test 4: is_checkpoint_boundary
    tests_total += 1
    try:
        chunks = [create_work_chunk(f"chunk-{i}", "task", f"Task {i}", 100) for i in range(5)]
        phase_chunk = create_work_chunk("chunk-phase", "phase", "Phase 1", 300)
        chunks.append(phase_chunk)
        
        should_create, reason = is_checkpoint_boundary(phase_chunk, chunks)
        assert should_create
        assert "phase" in reason.lower()
        print("✅ Test 4: is_checkpoint_boundary - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4: is_checkpoint_boundary - FAILED: {e}")
    
    # Test 5: create_checkpoint
    tests_total += 1
    try:
        chunks = [create_work_chunk(f"chunk-{i}", "task", f"Task {i}", 100) for i in range(3)]
        results = [{"success": True, "chunk_id": c.chunk_id, "output": f"Result {i}"} for i, c in enumerate(chunks)]
        
        checkpoint = create_checkpoint("cp-1", chunks, results, approval_required=True)
        assert checkpoint.checkpoint_id == "cp-1"
        assert len(checkpoint.chunks_completed) == 3
        assert checkpoint.approval_required
        print("✅ Test 5: create_checkpoint - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 5: create_checkpoint - FAILED: {e}")
    
    # Test 6: get_execution_summary
    tests_total += 1
    try:
        context = IncrementalExecutionContext()
        context.chunks = [create_work_chunk(f"chunk-{i}", "task", f"Task {i}", 100) for i in range(3)]
        context.completed_chunk_ids = ["chunk-0", "chunk-1"]
        context.results = [
            {"success": True, "chunk_id": "chunk-0"},
            {"success": True, "chunk_id": "chunk-1"}
        ]
        
        summary = get_execution_summary(context)
        assert summary["completed_chunks"] == 2
        assert summary["total_chunks"] == 3
        assert summary["success_rate"] == 1.0
        print("✅ Test 6: get_execution_summary - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 6: get_execution_summary - FAILED: {e}")
    
    # Test 7: execute_incremental_workflow
    tests_total += 1
    try:
        def mock_executor(chunk: WorkChunk) -> Dict[str, Any]:
            return {"success": True, "chunk_id": chunk.chunk_id, "output": f"Result for {chunk.chunk_id}"}
        
        chunks = [create_work_chunk(f"chunk-{i}", "task", f"Task {i}", 100) for i in range(3)]
        result = execute_incremental_workflow(chunks, mock_executor)
        
        assert result["success"]
        assert result["chunks_executed"] == 3
        assert not result["aborted"]
        print("✅ Test 7: execute_incremental_workflow - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 7: execute_incremental_workflow - FAILED: {e}")
    
    # Test 8: Invalid chunk validation
    tests_total += 1
    try:
        try:
            create_work_chunk("bad", "invalid_type", "Bad chunk", 100)
            assert False, "Should have raised ValueError"
        except ValueError as ve:
            assert "Invalid chunk_type" in str(ve)
        print("✅ Test 8: Invalid chunk validation - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 8: Invalid chunk validation - FAILED: {e}")
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {tests_passed}/{tests_total} passed ({tests_passed/tests_total*100:.1f}%)")
    print(f"⏱️  Execution time: {elapsed:.3f}s")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
    else:
        print(f"❌ {tests_total - tests_passed} test(s) failed")


if __name__ == "__main__":
    _run_self_tests()
