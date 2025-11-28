"""
Rollback Orchestrator - Foundation for checkpoint rollback operations.

Provides base capabilities for rolling back work to previous checkpoints created
by PhaseCheckpointManager during TDD workflows.

INCREMENT 11: Rollback Orchestrator Foundation
- Checkpoint listing from PhaseCheckpointManager
- Checkpoint validation before rollback
- Checkpoint summary formatting
- Foundation for command parsing (INCREMENT 12)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Status: GREEN PHASE (implementing to pass tests)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager


class RollbackOrchestrator:
    """
    Orchestrates rollback operations to previous checkpoints.
    
    Uses PhaseCheckpointManager for checkpoint metadata and provides
    user-friendly rollback commands with validation.
    """
    
    def __init__(self, cortex_dir: Path):
        """
        Initialize rollback orchestrator.
        
        Args:
            cortex_dir: Path to CORTEX directory
        """
        self.cortex_dir = Path(cortex_dir)
        self.checkpoint_manager = PhaseCheckpointManager(cortex_root=cortex_dir)
    
    def list_checkpoints(self, session_id: str) -> List[Dict[str, Any]]:
        """
        List all checkpoints for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of checkpoint metadata dictionaries
        """
        return self.checkpoint_manager.list_checkpoints(session_id=session_id)
    
    def validate_checkpoint(self, session_id: str, checkpoint_id: str) -> bool:
        """
        Validate that a checkpoint exists.
        
        Args:
            session_id: Session identifier
            checkpoint_id: Checkpoint identifier to validate
            
        Returns:
            True if checkpoint exists, False otherwise
            
        Example:
            >>> orchestrator = RollbackOrchestrator(cortex_dir=Path("/project"))
            >>> orchestrator.validate_checkpoint("session-1", "checkpoint-abc123")
            True
        """
        checkpoints = self.checkpoint_manager.list_checkpoints(session_id=session_id)
        
        # Handle empty checkpoint list gracefully
        if not checkpoints:
            return False
            
        return any(cp.get('checkpoint_id') == checkpoint_id for cp in checkpoints)
    
    def format_checkpoint_summary(self, session_id: str, checkpoint_id: str) -> str:
        """
        Format checkpoint metadata as human-readable summary.
        
        Searches PhaseCheckpointManager checkpoint list to find matching checkpoint_id,
        then formats phase, commit_sha, created_at, and metrics into readable string.
        
        Args:
            session_id: Session identifier
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Formatted summary string showing checkpoint details
            
        Example:
            >>> orchestrator = RollbackOrchestrator(cortex_dir=Path("/project"))
            >>> print(orchestrator.format_checkpoint_summary("session-1", "checkpoint-abc123"))
            Checkpoint: checkpoint-abc123
            Session: session-1
            Phase: implementation
            Commit SHA: abc1234
            Created: 2025-11-27T14:30:22
            Metrics:
              tests: 10
              coverage: 85.5
        """
        checkpoints = self.checkpoint_manager.list_checkpoints(session_id=session_id)
        
        # Find checkpoint by ID
        metadata = None
        for cp in checkpoints:
            if cp.get('checkpoint_id') == checkpoint_id:
                metadata = cp
                break
        
        if not metadata:
            return f"Checkpoint '{checkpoint_id}' not found"
        
        lines = []
        lines.append(f"Checkpoint: {checkpoint_id}")
        lines.append(f"Session: {session_id}")
        lines.append(f"Phase: {metadata.get('phase', 'unknown')}")
        
        # Handle commit_sha gracefully (may be None)
        commit_sha = metadata.get('commit_sha')
        if commit_sha:
            lines.append(f"Commit SHA: {commit_sha[:7]}")
        else:
            lines.append("Commit SHA: unknown")
            
        lines.append(f"Created: {metadata.get('created_at', 'unknown')}")
        
        # Format metrics if present
        metrics = metadata.get('metrics')
        if metrics:
            lines.append("Metrics:")
            for key, value in metrics.items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
