#!/usr/bin/env python3
"""
Checkpoint Manager (P0-T5)

Git-based checkpoint system with StateManager integration.
Creates tagged snapshots after each phase for easy rollback.

Part of: CORTEX 6.0 Remediation Plan - Phase P0
Author: GitHub Copilot + Asif Hussain
Created: 2026-01-08

Usage:
    # Create checkpoint
    python -m src.tools.checkpoint_manager create CP0 "Baseline checkpoint"
    
    # List checkpoints
    python -m src.tools.checkpoint_manager list
    
    # Restore checkpoint
    python -m src.tools.checkpoint_manager restore CP0
    
    # Validate checkpoint
    python -m src.tools.checkpoint_manager validate CP0
"""

import subprocess
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class CheckpointType(Enum):
    """Types of checkpoints."""
    BASELINE = "baseline"  # Initial state
    PHASE = "phase"  # End of phase
    TASK = "task"  # End of significant task
    EMERGENCY = "emergency"  # Manual emergency checkpoint


@dataclass
class Checkpoint:
    """Represents a remediation checkpoint."""
    id: str
    name: str
    type: CheckpointType
    description: str
    timestamp: str
    git_commit: str
    git_tag: str
    phase_id: Optional[str] = None
    task_id: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'description': self.description,
            'timestamp': self.timestamp,
            'git_commit': self.git_commit,
            'git_tag': self.git_tag,
            'phase_id': self.phase_id,
            'task_id': self.task_id,
            'metrics': self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            type=CheckpointType(data['type']),
            description=data['description'],
            timestamp=data['timestamp'],
            git_commit=data['git_commit'],
            git_tag=data['git_tag'],
            phase_id=data.get('phase_id'),
            task_id=data.get('task_id'),
            metrics=data.get('metrics', {})
        )


class CheckpointManager:
    """Manages remediation checkpoints with git integration."""
    
    def __init__(self, workspace_root: Optional[Path] = None, checkpoint_dir: Optional[Path] = None):
        """
        Initialize checkpoint manager.
        
        Args:
            workspace_root: Git repository root
            checkpoint_dir: Directory to store checkpoint metadata
        """
        if workspace_root is None:
            self.workspace_root = Path(__file__).parent.parent.parent
        else:
            self.workspace_root = Path(workspace_root)
        
        if checkpoint_dir is None:
            self.checkpoint_dir = self.workspace_root / ".asif" / "AI-Learning" / "cortex6-fixes" / "checkpoints"
        else:
            self.checkpoint_dir = Path(checkpoint_dir)
        
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints: List[Checkpoint] = []
        self._load_checkpoints()
    
    def _run_git_command(self, args: List[str]) -> str:
        """Run git command and return output."""
        result = subprocess.run(
            ['git'] + args,
            cwd=self.workspace_root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    def _get_current_commit(self) -> str:
        """Get current git commit hash."""
        return self._run_git_command(['rev-parse', 'HEAD'])
    
    def _get_current_branch(self) -> str:
        """Get current git branch."""
        return self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
    
    def _load_checkpoints(self) -> None:
        """Load existing checkpoints from metadata files."""
        self.checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob("CP*.yaml"):
            with open(checkpoint_file) as f:
                data = yaml.safe_load(f)
            self.checkpoints.append(Checkpoint.from_dict(data))
        
        # Sort by timestamp
        self.checkpoints.sort(key=lambda c: c.timestamp)
    
    def create_checkpoint(
        self,
        checkpoint_id: str,
        name: str,
        description: str,
        checkpoint_type: CheckpointType = CheckpointType.PHASE,
        phase_id: Optional[str] = None,
        task_id: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """
        Create a new checkpoint.
        
        Args:
            checkpoint_id: Unique checkpoint ID (e.g., CP0, CP1)
            name: Human-readable name
            description: Detailed description
            checkpoint_type: Type of checkpoint
            phase_id: Associated phase ID
            task_id: Associated task ID
            metrics: Additional metrics to store
        
        Returns:
            Created checkpoint
        """
        # Ensure working directory is clean
        status = self._run_git_command(['status', '--porcelain'])
        if status:
            print(f"⚠️ Warning: Working directory has uncommitted changes")
            print("Committing changes before checkpoint...")
            self._run_git_command(['add', '-A'])
            self._run_git_command(['commit', '-m', f'Auto-commit for checkpoint {checkpoint_id}'])
        
        # Get current state
        commit_hash = self._get_current_commit()
        branch = self._get_current_branch()
        timestamp = datetime.now().isoformat()
        
        # Create git tag
        tag_name = f"checkpoint-{checkpoint_id}"
        try:
            self._run_git_command(['tag', '-a', tag_name, '-m', name])
        except subprocess.CalledProcessError:
            print(f"⚠️ Tag {tag_name} already exists, using existing tag")
        
        # Create checkpoint object
        checkpoint = Checkpoint(
            id=checkpoint_id,
            name=name,
            type=checkpoint_type,
            description=description,
            timestamp=timestamp,
            git_commit=commit_hash,
            git_tag=tag_name,
            phase_id=phase_id,
            task_id=task_id,
            metrics=metrics or {}
        )
        
        # Save metadata
        metadata_file = self.checkpoint_dir / f"{checkpoint_id}.yaml"
        with open(metadata_file, 'w') as f:
            yaml.dump(checkpoint.to_dict(), f, default_flow_style=False, sort_keys=False)
        
        self.checkpoints.append(checkpoint)
        print(f"✅ Checkpoint created: {checkpoint_id} ({commit_hash[:8]})")
        
        return checkpoint
    
    def list_checkpoints(self) -> List[Checkpoint]:
        """List all checkpoints."""
        return self.checkpoints
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Get checkpoint by ID."""
        for checkpoint in self.checkpoints:
            if checkpoint.id == checkpoint_id:
                return checkpoint
        return None
    
    def validate_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Validate that checkpoint still exists in git.
        
        Args:
            checkpoint_id: Checkpoint ID to validate
        
        Returns:
            True if checkpoint is valid
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            print(f"❌ Checkpoint {checkpoint_id} not found in metadata")
            return False
        
        # Check if commit exists
        try:
            self._run_git_command(['cat-file', '-t', checkpoint.git_commit])
        except subprocess.CalledProcessError:
            print(f"❌ Commit {checkpoint.git_commit} not found in git")
            return False
        
        # Check if tag exists
        try:
            self._run_git_command(['show-ref', '--tags', checkpoint.git_tag])
        except subprocess.CalledProcessError:
            print(f"⚠️ Tag {checkpoint.git_tag} not found (not critical)")
        
        print(f"✅ Checkpoint {checkpoint_id} is valid")
        return True
    
    def restore_checkpoint(self, checkpoint_id: str, force: bool = False) -> None:
        """
        Restore to a checkpoint state.
        
        Args:
            checkpoint_id: Checkpoint ID to restore
            force: Force restore even with uncommitted changes
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        # Check for uncommitted changes
        status = self._run_git_command(['status', '--porcelain'])
        if status and not force:
            raise RuntimeError(
                "Working directory has uncommitted changes. "
                "Commit or stash changes, or use --force to override."
            )
        
        print(f"🔄 Restoring checkpoint: {checkpoint.name}")
        print(f"   Commit: {checkpoint.git_commit}")
        print(f"   Timestamp: {checkpoint.timestamp}")
        
        # Checkout commit
        self._run_git_command(['checkout', checkpoint.git_commit])
        
        print(f"✅ Restored to checkpoint {checkpoint_id}")
        print(f"⚠️ You are now in 'detached HEAD' state")
        print(f"   To return to branch: git checkout {self._get_current_branch()}")
    
    def diff_checkpoints(self, checkpoint_id1: str, checkpoint_id2: str) -> str:
        """
        Show diff between two checkpoints.
        
        Args:
            checkpoint_id1: First checkpoint
            checkpoint_id2: Second checkpoint
        
        Returns:
            Diff output
        """
        cp1 = self.get_checkpoint(checkpoint_id1)
        cp2 = self.get_checkpoint(checkpoint_id2)
        
        if not cp1 or not cp2:
            raise ValueError("One or both checkpoints not found")
        
        return self._run_git_command(['diff', cp1.git_commit, cp2.git_commit])
    
    def generate_checkpoint_report(self) -> Dict[str, Any]:
        """Generate comprehensive checkpoint report."""
        return {
            'total_checkpoints': len(self.checkpoints),
            'checkpoints': [cp.to_dict() for cp in self.checkpoints],
            'latest_checkpoint': self.checkpoints[-1].to_dict() if self.checkpoints else None,
            'generated_at': datetime.now().isoformat()
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage CORTEX remediation checkpoints")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create checkpoint
    create_parser = subparsers.add_parser('create', help='Create new checkpoint')
    create_parser.add_argument('id', help='Checkpoint ID (e.g., CP0)')
    create_parser.add_argument('name', help='Checkpoint name')
    create_parser.add_argument('--description', default='', help='Detailed description')
    create_parser.add_argument('--type', choices=['baseline', 'phase', 'task', 'emergency'],
                              default='phase', help='Checkpoint type')
    create_parser.add_argument('--phase', help='Phase ID')
    create_parser.add_argument('--task', help='Task ID')
    
    # List checkpoints
    subparsers.add_parser('list', help='List all checkpoints')
    
    # Validate checkpoint
    validate_parser = subparsers.add_parser('validate', help='Validate checkpoint')
    validate_parser.add_argument('id', help='Checkpoint ID')
    
    # Restore checkpoint
    restore_parser = subparsers.add_parser('restore', help='Restore to checkpoint')
    restore_parser.add_argument('id', help='Checkpoint ID')
    restore_parser.add_argument('--force', action='store_true', help='Force restore')
    
    # Diff checkpoints
    diff_parser = subparsers.add_parser('diff', help='Show diff between checkpoints')
    diff_parser.add_argument('id1', help='First checkpoint ID')
    diff_parser.add_argument('id2', help='Second checkpoint ID')
    
    # Generate report
    subparsers.add_parser('report', help='Generate checkpoint report')
    
    args = parser.parse_args()
    
    manager = CheckpointManager()
    
    if args.command == 'create':
        checkpoint_type = CheckpointType(args.type)
        manager.create_checkpoint(
            args.id,
            args.name,
            args.description,
            checkpoint_type,
            args.phase,
            args.task
        )
    
    elif args.command == 'list':
        print("\n📍 CORTEX Remediation Checkpoints\n")
        print(f"{'ID':<8} {'Name':<30} {'Type':<12} {'Timestamp':<20} {'Commit':<10}")
        print("=" * 80)
        for cp in manager.list_checkpoints():
            print(f"{cp.id:<8} {cp.name:<30} {cp.type.value:<12} {cp.timestamp[:19]:<20} {cp.git_commit[:8]:<10}")
    
    elif args.command == 'validate':
        manager.validate_checkpoint(args.id)
    
    elif args.command == 'restore':
        manager.restore_checkpoint(args.id, args.force)
    
    elif args.command == 'diff':
        diff = manager.diff_checkpoints(args.id1, args.id2)
        print(diff)
    
    elif args.command == 'report':
        report = manager.generate_checkpoint_report()
        print(yaml.dump(report, default_flow_style=False, sort_keys=False))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
