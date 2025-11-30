"""
Base Incremental Orchestrator - Layer 2 of Incremental Work Management System

Provides protocol and infrastructure for breaking work into manageable chunks
with checkpoint support. All orchestrators handling complex operations should
inherit from IncrementalWorkExecutor.

Part of CORTEX 3.2.1 - Incremental Work Management System
Author: Asif Hussain
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.utils.progress_decorator import with_progress, yield_progress
from src.utils.response_monitor import ResponseSizeMonitor, create_monitor

logger = logging.getLogger(__name__)


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
    
    def __post_init__(self):
        """Validate chunk configuration"""
        valid_statuses = {"pending", "in-progress", "complete", "blocked", "failed"}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")
        
        valid_types = {"skeleton", "phase", "section", "task", "test", "method"}
        if self.chunk_type not in valid_types:
            raise ValueError(f"Invalid chunk_type: {self.chunk_type}. Must be one of {valid_types}")


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


class IncrementalWorkExecutor(ABC):
    """
    Abstract base class for incremental work execution.
    
    All orchestrators handling complex operations should inherit from this class
    to ensure consistent incremental execution with checkpoints, progress tracking,
    and response size monitoring.
    
    Key Responsibilities:
    1. Break work into chunks (≤500 tokens each)
    2. Execute chunks with dependency management
    3. Create checkpoints for user approval
    4. Track progress throughout execution
    5. Integrate with ResponseSizeMonitor
    
    Subclasses must implement:
    - break_into_chunks(): Define how to decompose work
    - execute_chunk(): Define how to execute a single chunk
    - _is_checkpoint_boundary(): Define when to create checkpoints
    """
    
    # Token limits for chunk sizing
    MAX_CHUNK_TOKENS = 500  # Maximum tokens per chunk output
    CHECKPOINT_INTERVAL = 5  # Create checkpoint every N chunks
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize incremental work executor.
        
        Args:
            brain_path: Path to CORTEX brain directory (for response monitoring)
        """
        self.brain_path = brain_path
        self.response_monitor = create_monitor(brain_path)
        self.checkpoints: List[WorkCheckpoint] = []
        self.completed_chunks: List[str] = []
        
        logger.info(f"✨ {self.__class__.__name__} initialized with incremental execution")
    
    @abstractmethod
    def break_into_chunks(self, work_request: Dict[str, Any]) -> List[WorkChunk]:
        """
        Break work request into small, manageable chunks.
        
        Implementation Rules:
        1. Each chunk should produce ≤500 tokens of output
        2. Define clear dependencies between chunks
        3. Use appropriate chunk_type for each chunk
        4. Provide descriptive chunk descriptions
        
        Args:
            work_request: Dictionary containing work details
                Expected keys: operation, context, requirements, etc.
        
        Returns:
            List of WorkChunk objects in execution order
        
        Example:
            For a plan creation request:
            - Chunk 1: Create plan file skeleton (type: skeleton)
            - Chunk 2: Add Phase 1 (type: phase)
            - Chunk 3: Add Phase 2 (type: phase)
            - ...
            - Chunk N: Review and validate plan (type: section)
        """
        pass
    
    @abstractmethod
    def execute_chunk(self, chunk: WorkChunk) -> Dict[str, Any]:
        """
        Execute a single chunk of work.
        
        Implementation Guidelines:
        1. Update chunk.status to "in-progress" at start
        2. Perform the work defined by the chunk
        3. Update chunk.status to "complete" or "failed"
        4. Return result dictionary with success status
        
        Args:
            chunk: WorkChunk to execute
        
        Returns:
            Dictionary with execution results:
            {
                "success": bool,
                "chunk_id": str,
                "output": str,  # What was produced
                "token_count": int,
                "error": Optional[str]
            }
        """
        pass
    
    def _is_checkpoint_boundary(
        self,
        chunk: WorkChunk,
        all_chunks: List[WorkChunk]
    ) -> bool:
        """
        Determine if a checkpoint should be created after this chunk.
        
        Default behavior:
        - Checkpoint after every CHECKPOINT_INTERVAL chunks
        - Checkpoint after phase boundaries (chunk_type == "phase")
        - Checkpoint at the end of all chunks
        
        Subclasses can override for custom checkpoint logic.
        
        Args:
            chunk: Current chunk that just completed
            all_chunks: All chunks in the work request
        
        Returns:
            True if checkpoint should be created
        """
        chunk_index = all_chunks.index(chunk)
        
        # Checkpoint at phase boundaries
        if chunk.chunk_type == "phase":
            return True
        
        # Checkpoint at regular intervals
        if (chunk_index + 1) % self.CHECKPOINT_INTERVAL == 0:
            return True
        
        # Checkpoint at the end
        if chunk_index == len(all_chunks) - 1:
            return True
        
        return False
    
    def _create_checkpoint(
        self,
        completed_chunks: List[WorkChunk],
        results: List[Dict[str, Any]]
    ) -> WorkCheckpoint:
        """
        Create a checkpoint from completed work.
        
        Args:
            completed_chunks: List of chunks completed so far
            results: Execution results for each chunk
        
        Returns:
            WorkCheckpoint object for user review
        """
        checkpoint_id = f"checkpoint-{len(self.checkpoints) + 1}"
        chunk_ids = [c.chunk_id for c in completed_chunks]
        
        # Generate preview summary
        preview_lines = [
            f"📊 **Checkpoint: {len(completed_chunks)} chunks completed**\n",
            "**Completed Work:**"
        ]
        
        for chunk, result in zip(completed_chunks[-5:], results[-5:]):  # Last 5 chunks
            status_icon = "✅" if result.get("success") else "❌"
            preview_lines.append(f"  {status_icon} {chunk.description}")
        
        if len(completed_chunks) > 5:
            preview_lines.insert(2, f"  ... ({len(completed_chunks) - 5} earlier chunks)")
        
        preview = "\n".join(preview_lines)
        
        # Determine if approval required (e.g., at phase boundaries)
        approval_required = any(c.chunk_type == "phase" for c in completed_chunks[-5:])
        
        checkpoint = WorkCheckpoint(
            checkpoint_id=checkpoint_id,
            chunks_completed=chunk_ids,
            preview=preview,
            approval_required=approval_required
        )
        
        self.checkpoints.append(checkpoint)
        logger.info(f"📍 Checkpoint created: {checkpoint_id}")
        
        return checkpoint
    
    def _check_dependencies(
        self,
        chunk: WorkChunk,
        completed_chunk_ids: List[str]
    ) -> bool:
        """
        Check if all dependencies for a chunk are satisfied.
        
        Args:
            chunk: Chunk to check
            completed_chunk_ids: List of chunk IDs that have been completed
        
        Returns:
            True if all dependencies are satisfied
        """
        return all(dep_id in completed_chunk_ids for dep_id in chunk.dependencies)
    
    @with_progress(operation_name="Incremental Work Execution")
    def execute_incremental(
        self,
        work_request: Dict[str, Any],
        checkpoint_callback: Optional[Callable[[WorkCheckpoint], bool]] = None
    ) -> Dict[str, Any]:
        """
        Execute work incrementally with checkpoints and progress tracking.
        
        Workflow:
        1. Break work into chunks using break_into_chunks()
        2. Execute chunks sequentially, respecting dependencies
        3. Create checkpoints at boundaries using _is_checkpoint_boundary()
        4. Report progress continuously using yield_progress()
        5. Monitor response sizes with ResponseSizeMonitor
        
        Args:
            work_request: Dictionary with work details
            checkpoint_callback: Optional function to call at checkpoints
                Signature: (checkpoint: WorkCheckpoint) -> bool
                Return True to continue, False to abort
        
        Returns:
            Dictionary with execution summary:
            {
                "success": bool,
                "chunks_executed": int,
                "checkpoints_created": int,
                "results": List[Dict],
                "aborted": bool,
                "error": Optional[str]
            }
        """
        try:
            logger.info(f"🚀 Starting incremental execution for: {work_request.get('operation', 'unknown')}")
            
            # Break work into chunks
            chunks = self.break_into_chunks(work_request)
            logger.info(f"📦 Work broken into {len(chunks)} chunks")
            
            results = []
            completed_ids = []
            
            # Execute chunks with progress tracking
            for i, chunk in enumerate(chunks, 1):
                # Check dependencies
                if not self._check_dependencies(chunk, completed_ids):
                    logger.warning(f"⚠️ Chunk {chunk.chunk_id} blocked by dependencies")
                    chunk.status = "blocked"
                    continue
                
                # Report progress
                yield_progress(i, len(chunks), f"Executing: {chunk.description}")
                
                # Execute chunk
                chunk.status = "in-progress"
                try:
                    result = self.execute_chunk(chunk)
                    
                    # Check response size
                    output = result.get("output", "")
                    check_result = self.response_monitor.check_response(output)
                    
                    if not check_result.safe:
                        logger.warning(f"⚠️ Chunk {chunk.chunk_id} output too large, auto-chunking")
                        result["auto_chunked"] = True
                        result["file_path"] = str(check_result.file_path)
                    
                    results.append(result)
                    completed_ids.append(chunk.chunk_id)
                    self.completed_chunks.append(chunk.chunk_id)
                    
                except Exception as e:
                    logger.error(f"❌ Chunk {chunk.chunk_id} failed: {e}")
                    chunk.status = "failed"
                    results.append({
                        "success": False,
                        "chunk_id": chunk.chunk_id,
                        "error": str(e)
                    })
                
                # Create checkpoint if at boundary
                if self._is_checkpoint_boundary(chunk, chunks):
                    checkpoint = self._create_checkpoint(
                        [c for c in chunks if c.chunk_id in completed_ids],
                        results
                    )
                    
                    # Call checkpoint callback if provided
                    if checkpoint_callback and checkpoint.approval_required:
                        approved = checkpoint_callback(checkpoint)
                        checkpoint.feedback = "approved" if approved else "rejected"
                        
                        if not approved:
                            logger.warning("⛔ User rejected checkpoint, aborting execution")
                            return {
                                "success": False,
                                "chunks_executed": len(results),
                                "checkpoints_created": len(self.checkpoints),
                                "results": results,
                                "aborted": True,
                                "reason": "User rejected checkpoint"
                            }
            
            logger.info(f"✅ Incremental execution complete: {len(results)} chunks executed")
            
            return {
                "success": True,
                "chunks_executed": len(results),
                "checkpoints_created": len(self.checkpoints),
                "results": results,
                "aborted": False
            }
            
        except Exception as e:
            logger.error(f"❌ Incremental execution failed: {e}")
            return {
                "success": False,
                "chunks_executed": len(results) if 'results' in locals() else 0,
                "checkpoints_created": len(self.checkpoints),
                "results": results if 'results' in locals() else [],
                "aborted": True,
                "error": str(e)
            }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of current execution state.
        
        Returns:
            Dictionary with execution statistics
        """
        return {
            "completed_chunks": len(self.completed_chunks),
            "checkpoints_created": len(self.checkpoints),
            "checkpoint_details": [cp.to_dict() for cp in self.checkpoints]
        }
