"""
RollbackManager - State Snapshot and Restore
Implements OE-007: Transaction Rollback on Orchestrator Failure
"""

import json
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib


class RollbackManager:
    """
    Manages state snapshots and rollback capability for orchestrators.
    
    Enables:
    - Creating snapshots of orchestrator state + files
    - Restoring to previous snapshot on failure
    - Listing and managing snapshots
    - Automatic cleanup of old snapshots
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize RollbackManager with snapshot storage location."""
        self.workspace_root = workspace_root or Path.cwd()
        self.snapshots_dir = self.workspace_root / "cortex-brain" / "tier1" / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
    def create_snapshot(
        self,
        orchestrator: str,
        state: Dict[str, Any],
        description: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> str:
        """
        Create a snapshot of orchestrator state and optional files.
        
        Args:
            orchestrator: Name of the orchestrator (e.g., 'planning_v5')
            state: State dictionary to snapshot
            description: Optional description of the snapshot
            files: Optional list of file paths to include in snapshot
            
        Returns:
            Snapshot ID (UUID)
        """
        snapshot_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Create snapshot directory
        snapshot_path = self.snapshots_dir / snapshot_id
        snapshot_path.mkdir(parents=True, exist_ok=True)
        
        # Save state
        state_file = snapshot_path / "state.json"
        state_file.write_text(json.dumps(state, indent=2))
        
        # Save files if provided
        file_info = {}
        if files:
            files_dir = snapshot_path / "files"
            files_dir.mkdir(exist_ok=True)
            
            for file_path in files:
                src_path = Path(file_path)
                if src_path.exists():
                    # Calculate relative path from workspace root
                    try:
                        rel_path = src_path.relative_to(self.workspace_root)
                    except ValueError:
                        rel_path = src_path.name
                    
                    # Create destination with same structure
                    dest_path = files_dir / str(rel_path)
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file (handles both text and binary)
                    shutil.copy2(src_path, dest_path)
                    
                    # Store file info
                    file_info[str(rel_path)] = {
                        "original_path": str(src_path),
                        "size": src_path.stat().st_size,
                        "checksum": self._calculate_checksum(src_path)
                    }
        
        # Save metadata
        metadata = {
            "id": snapshot_id,
            "orchestrator": orchestrator,
            "description": description or f"Snapshot of {orchestrator}",
            "created_at": timestamp,
            "state": state,
            "files": file_info
        }
        
        metadata_file = snapshot_path / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        return snapshot_id
    
    def restore_snapshot(
        self,
        snapshot_id: str,
        restore_files: bool = False
    ) -> Dict[str, Any]:
        """
        Restore state from a snapshot.
        
        Args:
            snapshot_id: ID of the snapshot to restore
            restore_files: If True, also restore files from snapshot
            
        Returns:
            Restored state dictionary
            
        Raises:
            ValueError: If snapshot doesn't exist
        """
        snapshot_path = self.snapshots_dir / snapshot_id
        
        if not snapshot_path.exists():
            raise ValueError(f"Snapshot {snapshot_id} not found")
        
        # Load metadata
        metadata_file = snapshot_path / "metadata.json"
        metadata = json.loads(metadata_file.read_text())
        
        # Restore files if requested
        if restore_files and metadata["files"]:
            files_dir = snapshot_path / "files"
            
            for rel_path, file_info in metadata["files"].items():
                src_path = files_dir / rel_path
                dest_path = Path(file_info["original_path"])
                
                if src_path.exists():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
        
        return metadata["state"]
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get snapshot metadata without restoring.
        
        Args:
            snapshot_id: ID of the snapshot
            
        Returns:
            Snapshot metadata or None if not found
        """
        snapshot_path = self.snapshots_dir / snapshot_id
        
        if not snapshot_path.exists():
            return None
        
        metadata_file = snapshot_path / "metadata.json"
        return json.loads(metadata_file.read_text())
    
    def list_snapshots(
        self,
        orchestrator: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all snapshots, optionally filtered by orchestrator.
        
        Args:
            orchestrator: Optional orchestrator name to filter by
            
        Returns:
            List of snapshot metadata dictionaries
        """
        snapshots = []
        
        for snapshot_dir in self.snapshots_dir.iterdir():
            if snapshot_dir.is_dir():
                metadata_file = snapshot_dir / "metadata.json"
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text())
                    
                    if orchestrator is None or metadata["orchestrator"] == orchestrator:
                        snapshots.append(metadata)
        
        # Sort by creation time (newest first)
        snapshots.sort(key=lambda x: x["created_at"], reverse=True)
        
        return snapshots
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """
        Delete a snapshot.
        
        Args:
            snapshot_id: ID of the snapshot to delete
            
        Returns:
            True if deleted, False if not found
        """
        snapshot_path = self.snapshots_dir / snapshot_id
        
        if not snapshot_path.exists():
            return False
        
        shutil.rmtree(snapshot_path)
        return True
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()
