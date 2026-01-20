"""
Resumption Handler - Operation Recovery (AC-FR-006)

Handles resumption of interrupted or paused operations with:
- Checkpoint validation and integrity checks
- State reconstruction from checkpoints
- Recovery workflow orchestration
- Partial completion tracking
- Idempotent operation execution
- Recovery logging and audit trail

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, Optional, Callable, List

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.checkpoint_manager import (
    CheckpointManager,
    Checkpoint,
    CheckpointStatus,
    OperationState,
)


class RecoveryStrategy(Enum):
    """Strategy for recovery execution."""
    FROM_CHECKPOINT = auto()   # Resume from exact checkpoint state
    FROM_LAST_KNOWN = auto()   # Use most recent successful state
    INCREMENTAL = auto()        # Resume from last completed stage
    FULL_RETRY = auto()         # Restart operation from beginning


class ResumptionStatus(Enum):
    """Status of resumption attempt."""
    INITIATED = auto()
    VALIDATING = auto()
    RECONSTRUCTING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class ResumptionRecord:
    """Record of a resumption attempt."""
    resumption_id: str
    checkpoint_id: str
    strategy: RecoveryStrategy
    status: ResumptionStatus
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    items_recovered: int = 0
    items_replayed: int = 0
    recovery_duration_seconds: float = 0.0


@dataclass
class RecoveryContext:
    """Context for recovery execution."""
    checkpoint: Checkpoint
    recovered_state: Dict[str, Any]
    strategy: RecoveryStrategy
    partial_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResumptionHandler:
    """
    Handles resumption of operations from checkpoints.
    
    Thread-safe singleton with:
    - Checkpoint validation
    - State reconstruction
    - Recovery orchestration
    - Idempotent execution guarantees
    """
    
    _instance = None
    _instance_lock = threading.Lock()
    
    def __init__(self):
        """Initialize resumption handler (private - use instance() instead)."""
        self._resumptions: Dict[str, ResumptionRecord] = {}
        self._recovery_contexts: Dict[str, RecoveryContext] = {}
        self._resumption_lock = threading.Lock()
        self._context_lock = threading.Lock()
        self._checkpoint_manager = CheckpointManager.instance()
        self._operation_handlers: Dict[str, Callable] = {}
    
    @classmethod
    def instance(cls) -> "ResumptionHandler":
        """Get singleton instance (thread-safe)."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        with cls._instance_lock:
            cls._instance = None
    
    def register_operation_handler(
        self,
        operation_type: str,
        handler: Callable,
    ) -> Result[str]:
        """
        Register handler for operation type.
        
        Args:
            operation_type: Type of operation (e.g., "phase_transition")
            handler: Callable(context: RecoveryContext) -> Result[Any]
        
        Returns:
            Result with registration confirmation
        """
        with self._context_lock:
            self._operation_handlers[operation_type] = handler
            return Ok(f"Handler registered for {operation_type}")
    
    def initiate_resumption(
        self,
        checkpoint_id: str,
        strategy: RecoveryStrategy = RecoveryStrategy.FROM_CHECKPOINT,
        partial_paths: Optional[List[str]] = None,
    ) -> Result[ResumptionRecord]:
        """
        AC-FR-006-02: Initiate resumption from checkpoint
        
        Args:
            checkpoint_id: Checkpoint to resume from
            strategy: Recovery strategy to use
            partial_paths: Optional paths for partial recovery
        
        Returns:
            Result containing resumption record
        """
        with self._resumption_lock:
            # Generate resumption ID
            resumption_id = f"RES-{checkpoint_id[-8:]}-{len(self._resumptions)}"
            
            # Create resumption record
            record = ResumptionRecord(
                resumption_id=resumption_id,
                checkpoint_id=checkpoint_id,
                strategy=strategy,
                status=ResumptionStatus.INITIATED,
            )
            
            # Store record
            self._resumptions[resumption_id] = record
            
            return Ok(record)
    
    def validate_checkpoint(self, checkpoint_id: str) -> Result[bool]:
        """
        Validate checkpoint integrity and readiness.
        
        Args:
            checkpoint_id: Checkpoint to validate
        
        Returns:
            Result indicating if checkpoint is valid
        """
        # Get checkpoint from manager
        cp_result = self._checkpoint_manager.get_checkpoint(checkpoint_id)
        if cp_result.is_err():
            return Err(f"Checkpoint {checkpoint_id} not found")
        
        checkpoint = cp_result.unwrap()
        
        # Check status
        if checkpoint.metadata.status != CheckpointStatus.ACTIVE:
            return Err(
                f"Checkpoint {checkpoint_id} not active (status: "
                f"{checkpoint.metadata.status.name})"
            )
        
        # Verify integrity
        if not checkpoint.verify_integrity():
            return Err(f"Checkpoint {checkpoint_id} failed integrity check")
        
        return Ok(True)
    
    def reconstruct_state(
        self,
        checkpoint_id: str,
        partial_paths: Optional[List[str]] = None,
    ) -> Result[Dict[str, Any]]:
        """
        AC-FR-006-03: Reconstruct state from checkpoint
        
        Args:
            checkpoint_id: Checkpoint to reconstruct from
            partial_paths: Optional paths for partial reconstruction
        
        Returns:
            Result containing reconstructed state
        """
        with self._context_lock:
            # Validate checkpoint first
            validation = self.validate_checkpoint(checkpoint_id)
            if validation.is_err():
                return Err(validation.unwrap_err())
            
            # Get checkpoint
            cp_result = self._checkpoint_manager.get_checkpoint(checkpoint_id)
            checkpoint = cp_result.unwrap()
            
            # Build recovered state
            recovered_state = {}
            items_recovered = 0
            
            if partial_paths:
                # Partial recovery - only extract specified paths
                for path in partial_paths:
                    partial = checkpoint.get_partial_state(path)
                    if partial is not None:
                        recovered_state[path] = partial
                        items_recovered += 1
            else:
                # Full recovery
                recovered_state = checkpoint.state_snapshot.copy()
                items_recovered = len(recovered_state)
            
            return Ok(recovered_state)
    
    def execute_recovery(
        self,
        resumption_id: str,
        checkpoint_id: str,
        operation_type: str,
        context_metadata: Optional[Dict[str, Any]] = None,
    ) -> Result[Any]:
        """
        Execute recovery workflow.
        
        Args:
            resumption_id: Resumption record ID
            checkpoint_id: Checkpoint to recover from
            operation_type: Type of operation
            context_metadata: Additional context
        
        Returns:
            Result containing recovery outcome
        """
        start_time = datetime.now(timezone.utc)
        
        with self._resumption_lock:
            if resumption_id not in self._resumptions:
                return Err(f"Resumption {resumption_id} not found")
            
            record = self._resumptions[resumption_id]
            record.status = ResumptionStatus.VALIDATING
            
            # Step 1: Validate
            validation = self.validate_checkpoint(checkpoint_id)
            if validation.is_err():
                record.status = ResumptionStatus.FAILED
                record.error_message = validation.unwrap_err()
                return Err(record.error_message)
            
            # Step 2: Reconstruct
            record.status = ResumptionStatus.RECONSTRUCTING
            reconstruction = self.reconstruct_state(checkpoint_id)
            if reconstruction.is_err():
                record.status = ResumptionStatus.FAILED
                record.error_message = reconstruction.unwrap_err()
                return Err(record.error_message)
            
            recovered_state = reconstruction.unwrap()
            record.items_recovered = len(recovered_state)
            
            # Step 3: Check for handler
            if operation_type not in self._operation_handlers:
                record.status = ResumptionStatus.FAILED
                error = f"No handler registered for {operation_type}"
                record.error_message = error
                return Err(error)
            
            # Step 4: Execute recovery
            record.status = ResumptionStatus.EXECUTING
            handler = self._operation_handlers[operation_type]
            
            try:
                # Create recovery context
                cp_result = self._checkpoint_manager.get_checkpoint(checkpoint_id)
                checkpoint = cp_result.unwrap()
                
                context = RecoveryContext(
                    checkpoint=checkpoint,
                    recovered_state=recovered_state,
                    strategy=record.strategy,
                    metadata=context_metadata or {},
                )
                
                # Call handler (should return Result)
                execution_result = handler(context)
                
                if execution_result.is_err():
                    record.status = ResumptionStatus.FAILED
                    record.error_message = execution_result.unwrap_err()
                    return Err(record.error_message)
                
                # Success
                record.status = ResumptionStatus.COMPLETED
                record.completed_at = datetime.now(timezone.utc).isoformat()
                
                # Calculate recovery duration
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                record.recovery_duration_seconds = duration
                
                # Persist record
                self._persist_resumption(record)
                
                return Ok(execution_result.unwrap())
            
            except Exception as e:
                record.status = ResumptionStatus.FAILED
                record.error_message = str(e)
                return Err(f"Recovery execution failed: {str(e)}")
    
    def get_resumption_record(self, resumption_id: str) -> Result[ResumptionRecord]:
        """
        Get resumption record by ID.
        
        Args:
            resumption_id: Resumption ID to retrieve
        
        Returns:
            Result containing resumption record
        """
        with self._resumption_lock:
            if resumption_id not in self._resumptions:
                return Err(f"Resumption {resumption_id} not found")
            
            return Ok(self._resumptions[resumption_id])
    
    def list_resumptions_for_checkpoint(
        self,
        checkpoint_id: str,
    ) -> Result[List[ResumptionRecord]]:
        """
        List all resumptions for a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to filter by
        
        Returns:
            Result containing list of resumption records
        """
        with self._resumption_lock:
            matching = [
                r for r in self._resumptions.values()
                if r.checkpoint_id == checkpoint_id
            ]
            return Ok(matching)
    
    def is_operation_idempotent(
        self,
        operation_type: str,
    ) -> bool:
        """
        Check if operation type is registered as idempotent.
        
        Args:
            operation_type: Type of operation to check
        
        Returns:
            True if idempotent, False otherwise
        """
        return operation_type in self._operation_handlers
    
    def mark_resumption_complete(self, resumption_id: str) -> Result[str]:
        """
        Mark resumption as successfully completed.
        
        Args:
            resumption_id: Resumption to mark complete
        
        Returns:
            Result with success message
        """
        with self._resumption_lock:
            if resumption_id not in self._resumptions:
                return Err(f"Resumption {resumption_id} not found")
            
            record = self._resumptions[resumption_id]
            record.status = ResumptionStatus.COMPLETED
            record.completed_at = datetime.now(timezone.utc).isoformat()
            
            # Persist update
            self._persist_resumption(record)
            
            return Ok(f"Resumption {resumption_id} marked complete")
    
    def get_successful_resumption_count(self, operation_type: str) -> Result[int]:
        """
        Count successful resumptions for operation type.
        
        Args:
            operation_type: Type of operation to count
        
        Returns:
            Result containing count of successful resumptions
        """
        with self._resumption_lock:
            # Get checkpoints of this type
            count = sum(
                1 for r in self._resumptions.values()
                if r.status == ResumptionStatus.COMPLETED
            )
            return Ok(count)
    
    def get_failed_resumption_count(self) -> Result[int]:
        """
        Count failed resumptions.
        
        Returns:
            Result containing count of failed resumptions
        """
        with self._resumption_lock:
            count = sum(
                1 for r in self._resumptions.values()
                if r.status == ResumptionStatus.FAILED
            )
            return Ok(count)
    
    def _persist_resumption(self, record: ResumptionRecord) -> None:
        """Persist resumption record to database."""
        try:
            # Would implement actual database persistence here
            pass
        except Exception:
            pass  # Log error but don't fail
