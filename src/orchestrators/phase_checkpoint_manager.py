"""
Phase Checkpoint Manager for workflow phase tracking.

This module manages metadata for workflow phase checkpoints, enabling
rollback to specific phases and progress tracking.

Example:
    >>> manager = PhaseCheckpointManager()
    >>> manager.store_checkpoint_metadata(
    ...     session_id="feature-xyz",
    ...     phase="phase-1-foundation",
    ...     checkpoint_id="ckpt-001",
    ...     commit_sha="abc123def456"
    ... )
    >>> 
    >>> checkpoints = manager.list_checkpoints("feature-xyz")
    >>> print(f"Found {len(checkpoints)} checkpoints")
"""

import json
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any


class PhaseCheckpointManager:
    """
    Manages phase checkpoint metadata for workflows.
    
    Stores checkpoint metadata in .cortex/phase-checkpoints-{session_id}.json
    files for resumable workflows and rollback support.
    
    Attributes:
        cortex_root: Path to repository root
        checkpoint_dir: Path to .cortex metadata directory
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
