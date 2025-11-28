"""
Phase Checkpoint Manager for workflow phase tracking.

This module manages metadata for workflow phase checkpoints, enabling
rollback to specific phases and progress tracking.

Example:
    >>> manager = PhaseCheckpointManager()
    >>> checkpoint_id = manager.create_pre_work_checkpoint(
    ...     operation="Authentication feature",
    ...     session_id="feature-auth-001"
    ... )
    >>> print(f"Pre-work checkpoint created: {checkpoint_id}")
    >>> 
    >>> checkpoint_id = manager.create_phase_checkpoint(
    ...     phase="phase-1-foundation",
    ...     session_id="feature-auth-001",
    ...     metrics={"tests_passing": 25, "coverage": 92.5}
    ... )
    >>> print(f"Phase checkpoint created: {checkpoint_id}")
"""

import json
import logging
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class PhaseCheckpointManager:
    """
    Manages phase checkpoint metadata for workflows.
    
    Stores checkpoint metadata in .cortex/phase-checkpoints-{session_id}.json
    files for resumable workflows and rollback support.
    
    Integrates with GitCheckpointOrchestrator for automated checkpoint creation
    during workflow phases.
    
    Attributes:
        cortex_root: Path to repository root
        checkpoint_dir: Path to .cortex metadata directory
        git_checkpoint: GitCheckpointOrchestrator instance for checkpoint creation
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize manager with cortex root directory.
        
        Args:
            cortex_root: Path to repository root (default: current directory)
        """
        self.cortex_root = cortex_root if cortex_root else Path.cwd()
        self.checkpoint_dir = self.cortex_root / ".cortex"
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Initialize GitCheckpointOrchestrator for checkpoint creation
        from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
        self.git_checkpoint = GitCheckpointOrchestrator(project_root=self.cortex_root)
    
    def _get_metadata_file(self, session_id: str) -> Path:
        """Get metadata file path for session."""
        return self.checkpoint_dir / f"phase-checkpoints-{session_id}.json"
    
    def store_checkpoint_metadata(
        self,
        session_id: str,
        phase: str,
        checkpoint_id: str,
        commit_sha: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store checkpoint metadata for workflow phase.
        
        Args:
            session_id: Unique session identifier (e.g., "feature-xyz")
            phase: Phase name (e.g., "phase-1-foundation")
            checkpoint_id: Checkpoint identifier (e.g., "ckpt-001")
            commit_sha: Git commit SHA for checkpoint
            metrics: Optional performance/progress metrics
        
        Example:
            >>> manager = PhaseCheckpointManager()
            >>> manager.store_checkpoint_metadata(
            ...     session_id="auth-feature",
            ...     phase="phase-2-implementation",
            ...     checkpoint_id="ckpt-002",
            ...     commit_sha="def456abc789",
            ...     metrics={"tests_passing": 45, "coverage": 92.5}
            ... )
        """
        metadata_file = self._get_metadata_file(session_id)
        
        # Load existing metadata
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                'session_id': session_id,
                'created_at': datetime.now(UTC).isoformat(),
                'checkpoints': []
            }
        
        # Add new checkpoint
        checkpoint = {
            'phase': phase,
            'checkpoint_id': checkpoint_id,
            'commit_sha': commit_sha,
            'created_at': datetime.now(UTC).isoformat(),
            'metrics': metrics or {}
        }
        
        data['checkpoints'].append(checkpoint)
        
        # Save metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_checkpoint_metadata(
        self, 
        session_id: str, 
        phase: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get checkpoint metadata for specific phase.
        
        Args:
            session_id: Session identifier
            phase: Phase name to retrieve
        
        Returns:
            Checkpoint metadata dictionary or None if not found
        
        Example:
            >>> manager = PhaseCheckpointManager()
            >>> metadata = manager.get_checkpoint_metadata("auth-feature", "phase-1")
            >>> if metadata:
            ...     print(f"Checkpoint: {metadata['checkpoint_id']}")
        """
        metadata_file = self._get_metadata_file(session_id)
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find checkpoint for phase
            for checkpoint in data['checkpoints']:
                if checkpoint['phase'] == phase:
                    return checkpoint
            
            return None
        
        except (json.JSONDecodeError, KeyError):
            return None
    
    def list_checkpoints(self, session_id: str) -> List[Dict[str, Any]]:
        """
        List all checkpoints for session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of checkpoint dictionaries (empty if session doesn't exist)
        
        Example:
            >>> manager = PhaseCheckpointManager()
            >>> checkpoints = manager.list_checkpoints("auth-feature")
            >>> for cp in checkpoints:
            ...     print(f"{cp['phase']}: {cp['commit_sha'][:7]}")
        """
        metadata_file = self._get_metadata_file(session_id)
        
        if not metadata_file.exists():
            return []
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('checkpoints', [])
        
        except (json.JSONDecodeError, KeyError):
            return []
    
    # INCREMENT 9: Phase Checkpoint Creation
    
    def _create_checkpoint_with_metadata(
        self,
        checkpoint_type: str,
        message: str,
        session_id: str,
        phase: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Internal helper to create checkpoint and store metadata.
        
        Args:
            checkpoint_type: Type for git checkpoint (e.g., "pre-work", "phase-X")
            message: Commit message
            session_id: Session identifier
            phase: Phase name for metadata storage
            metrics: Optional metrics to store
        
        Returns:
            Checkpoint ID if successful, None if failed
        """
        # Create git checkpoint
        checkpoint_result = self.git_checkpoint.create_checkpoint(
            session_id=session_id,
            checkpoint_type=checkpoint_type,
            message=message
        )
        
        if not checkpoint_result.get('success'):
            logger.warning(
                f"Checkpoint creation failed for {checkpoint_type}: "
                f"{checkpoint_result.get('message', 'Unknown error')}"
            )
            return None
        
        checkpoint_id = checkpoint_result['checkpoint_id']
        commit_sha = checkpoint_result['commit_sha']
        
        # Store metadata
        self.store_checkpoint_metadata(
            session_id=session_id,
            phase=phase,
            checkpoint_id=checkpoint_id,
            commit_sha=commit_sha,
            metrics=metrics
        )
        
        logger.info(f"✅ Checkpoint created: {checkpoint_id} (phase: {phase})")
        return checkpoint_id
    
    def create_pre_work_checkpoint(
        self,
        operation: str,
        session_id: str
    ) -> Optional[str]:
        """
        Create pre-work checkpoint before operation starts.
        
        This checkpoint captures the repository state before any work begins,
        enabling complete rollback if needed.
        
        Args:
            operation: Description of operation about to begin
            session_id: Unique session identifier
        
        Returns:
            Checkpoint ID if successful, None if failed
        
        Example:
            >>> manager = PhaseCheckpointManager()
            >>> checkpoint_id = manager.create_pre_work_checkpoint(
            ...     operation="Authentication feature implementation",
            ...     session_id="feature-auth-001"
            ... )
            >>> if checkpoint_id:
            ...     print(f"✅ Pre-work checkpoint created: {checkpoint_id}")
            ... else:
            ...     print("⚠️ Checkpoint creation failed")
        """
        if not operation or not session_id:
            logger.error("Operation and session_id are required for pre-work checkpoint")
            return None
        
        message = f"Pre-work checkpoint: {operation}"
        
        return self._create_checkpoint_with_metadata(
            checkpoint_type="pre-work",
            message=message,
            session_id=session_id,
            phase="pre-work",
            metrics=None
        )
    
    def create_phase_checkpoint(
        self,
        phase: str,
        session_id: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create phase checkpoint after phase completion.
        
        This checkpoint captures progress after completing a workflow phase,
        enabling rollback to specific phases if issues arise.
        
        Args:
            phase: Phase name (e.g., "phase-1-foundation", "phase-2-implementation")
            session_id: Unique session identifier
            metrics: Optional performance/progress metrics (e.g., tests_passing, coverage)
        
        Returns:
            Checkpoint ID if successful, None if failed
        
        Example:
            >>> manager = PhaseCheckpointManager()
            >>> checkpoint_id = manager.create_phase_checkpoint(
            ...     phase="phase-2-implementation",
            ...     session_id="feature-auth-001",
            ...     metrics={"tests_passing": 45, "coverage": 92.5, "duration": 300}
            ... )
            >>> if checkpoint_id:
            ...     print(f"✅ Phase checkpoint created: {checkpoint_id}")
            ... else:
            ...     print("⚠️ Checkpoint creation failed")
        """
        if not phase or not session_id:
            logger.error("Phase and session_id are required for phase checkpoint")
            return None
        
        message = f"Phase {phase} complete"
        
        return self._create_checkpoint_with_metadata(
            checkpoint_type=f"phase-{phase}",
            message=message,
            session_id=session_id,
            phase=phase,
            metrics=metrics
        )
