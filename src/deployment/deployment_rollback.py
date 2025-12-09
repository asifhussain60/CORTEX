"""
Deployment Rollback Manager

Comprehensive rollback system for deployments with phase-level snapshots,
partial rollback support, validation, and manifest management.

Features:
- Phase-level snapshots (PRE_FLIGHT, BUILD, DEPLOY, VERIFY)
- Multiple rollback types (CODE_ONLY, BRAIN_ONLY, FULL)
- Pre/post-rollback validation
- Rollback manifest management
- Dry-run preview mode
- Git-based restoration with safety checks

Author: Asif Hussain
Version: 1.0.0
"""

import subprocess
import json
import logging
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
except ImportError:
    # Fallback if config not available
    CORTEX_ROOT = Path(__file__).resolve().parents[3]


class RollbackType(Enum):
    """Types of rollback operations."""
    CODE_ONLY = "code_only"  # Rollback code only (git reset)
    BRAIN_ONLY = "brain_only"  # Rollback brain state only
    FULL = "full"  # Rollback everything (code + brain + config)


@dataclass
class RollbackSnapshot:
    """Deployment rollback snapshot."""
    snapshot_id: str
    phase: str  # PRE_FLIGHT, BUILD, DEPLOY, VERIFY
    snapshot_type: RollbackType
    timestamp: str
    git_commit: str
    git_branch: str
    brain_state: Optional[Dict] = None
    config_state: Optional[Dict] = None
    metadata: Optional[Dict] = None


@dataclass
class RollbackValidation:
    """Rollback validation result."""
    snapshot_exists: bool
    git_clean: bool
    safe_to_rollback: bool
    warning: Optional[str] = None
    errors: List[str] = None


@dataclass
class RollbackResult:
    """Result of rollback operation."""
    success: bool
    snapshot_id: str
    executed: bool = False
    code_restored: bool = False
    brain_restored: bool = False
    config_restored: bool = False
    preview: Optional[str] = None
    report: Optional[Dict] = None


@dataclass
class PostRollbackValidation:
    """Post-rollback validation result."""
    system_stable: bool
    git_consistent: bool
    files_intact: bool
    errors: List[str] = None


class DeploymentRollbackManager:
    """Manages deployment rollbacks with phase-level snapshots."""
    
    def __init__(self, cortex_root: Path = None):
        """
        Initialize rollback manager.
        
        Args:
            cortex_root: Path to CORTEX root (default: from config)
        """
        self.cortex_root = cortex_root or CORTEX_ROOT
        self.rollback_dir = self.cortex_root / "cortex-brain" / "deployments" / "rollback-points"
        
        # Ensure rollback directory exists
        self.rollback_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📦 Deployment Rollback Manager initialized: {self.cortex_root}")
    
    def create_snapshot(
        self,
        phase: str,
        snapshot_type: RollbackType = RollbackType.FULL,
        metadata: Optional[Dict] = None
    ) -> RollbackSnapshot:
        """
        Create deployment snapshot.
        
        Args:
            phase: Deployment phase (PRE_FLIGHT, BUILD, DEPLOY, VERIFY)
            snapshot_type: Type of snapshot (CODE_ONLY, BRAIN_ONLY, FULL)
            metadata: Additional metadata
            
        Returns:
            RollbackSnapshot object
        """
        snapshot_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # Get current git state
        git_commit = self._get_git_commit()
        git_branch = self._get_git_branch()
        
        # Capture brain state if needed
        brain_state = None
        if snapshot_type in (RollbackType.BRAIN_ONLY, RollbackType.FULL):
            brain_state = self._capture_brain_state()
        
        # Capture config state if needed
        config_state = None
        if snapshot_type == RollbackType.FULL:
            config_state = self._capture_config_state()
        
        # Create snapshot object
        snapshot = RollbackSnapshot(
            snapshot_id=snapshot_id,
            phase=phase,
            snapshot_type=snapshot_type,
            timestamp=timestamp,
            git_commit=git_commit,
            git_branch=git_branch,
            brain_state=brain_state,
            config_state=config_state,
            metadata=metadata or {}
        )
        
        # Save snapshot manifest
        self._save_snapshot_manifest(snapshot)
        
        logger.info(f"✅ Snapshot created: {snapshot_id} (phase={phase}, type={snapshot_type.value})")
        
        return snapshot
    
    def execute_rollback(
        self,
        snapshot_id: str,
        rollback_type: RollbackType = None,
        dry_run: bool = False
    ) -> RollbackResult:
        """
        Execute rollback to snapshot.
        
        Args:
            snapshot_id: Snapshot ID to rollback to
            rollback_type: Override rollback type (default: use snapshot type)
            dry_run: If True, preview changes only
            
        Returns:
            RollbackResult with operation outcome
        """
        # Load snapshot
        snapshot = self.load_snapshot(snapshot_id)
        if not snapshot:
            return RollbackResult(
                success=False,
                snapshot_id=snapshot_id,
                executed=False
            )
        
        # Use snapshot type if not overridden
        rollback_type = rollback_type or snapshot.snapshot_type
        
        # Dry-run mode: preview only
        if dry_run:
            preview = self._generate_rollback_preview(snapshot, rollback_type)
            return RollbackResult(
                success=True,
                snapshot_id=snapshot_id,
                executed=False,
                preview=preview
            )
        
        # Execute rollback based on type
        code_restored = False
        brain_restored = False
        config_restored = False
        
        try:
            if rollback_type in (RollbackType.CODE_ONLY, RollbackType.FULL):
                self._rollback_code(snapshot)
                code_restored = True
            
            if rollback_type in (RollbackType.BRAIN_ONLY, RollbackType.FULL):
                self._rollback_brain(snapshot)
                brain_restored = True
            
            if rollback_type == RollbackType.FULL:
                self._rollback_config(snapshot)
                config_restored = True
            
            # Generate report
            report = self._generate_rollback_report(snapshot, rollback_type)
            
            return RollbackResult(
                success=True,
                snapshot_id=snapshot_id,
                executed=True,
                code_restored=code_restored,
                brain_restored=brain_restored,
                config_restored=config_restored,
                report=report
            )
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return RollbackResult(
                success=False,
                snapshot_id=snapshot_id,
                executed=False
            )
    
    def validate_rollback(self, snapshot_id: str) -> RollbackValidation:
        """
        Validate rollback is safe to execute.
        
        Args:
            snapshot_id: Snapshot ID to validate
            
        Returns:
            RollbackValidation result
        """
        errors = []
        
        # Check snapshot exists
        snapshot = self.load_snapshot(snapshot_id)
        snapshot_exists = snapshot is not None
        if not snapshot_exists:
            errors.append(f"Snapshot {snapshot_id} not found")
        
        # Check git is clean
        git_clean = self._check_git_clean()
        warning = None
        if not git_clean:
            warning = "Uncommitted changes detected - commit or stash before rollback"
        
        # Determine if safe
        safe_to_rollback = snapshot_exists and git_clean
        
        return RollbackValidation(
            snapshot_exists=snapshot_exists,
            git_clean=git_clean,
            safe_to_rollback=safe_to_rollback,
            warning=warning,
            errors=errors if errors else None
        )
    
    def validate_post_rollback(self, result: RollbackResult) -> PostRollbackValidation:
        """
        Validate system state after rollback.
        
        Args:
            result: Rollback result to validate
            
        Returns:
            PostRollbackValidation result
        """
        errors = []
        
        # Check git consistency
        git_consistent = self._check_git_consistency()
        if not git_consistent:
            errors.append("Git repository inconsistent")
        
        # Check file integrity (basic check)
        files_intact = self._check_file_integrity()
        if not files_intact:
            errors.append("File integrity check failed")
        
        # Overall system stability
        system_stable = git_consistent and files_intact
        
        return PostRollbackValidation(
            system_stable=system_stable,
            git_consistent=git_consistent,
            files_intact=files_intact,
            errors=errors if errors else None
        )
    
    def list_snapshots(
        self,
        phase: Optional[str] = None,
        snapshot_type: Optional[RollbackType] = None
    ) -> List[RollbackSnapshot]:
        """
        List available snapshots.
        
        Args:
            phase: Filter by phase (optional)
            snapshot_type: Filter by type (optional)
            
        Returns:
            List of snapshots matching filters
        """
        snapshots = []
        
        for manifest_file in self.rollback_dir.glob("*.json"):
            snapshot = self._load_snapshot_from_file(manifest_file)
            if snapshot:
                # Apply filters
                if phase and snapshot.phase != phase:
                    continue
                if snapshot_type and snapshot.snapshot_type != snapshot_type:
                    continue
                
                snapshots.append(snapshot)
        
        # Sort by timestamp (newest first)
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        
        return snapshots
    
    def get_latest_snapshot(self, phase: Optional[str] = None) -> Optional[RollbackSnapshot]:
        """
        Get most recent snapshot.
        
        Args:
            phase: Filter by phase (optional)
            
        Returns:
            Latest snapshot or None
        """
        snapshots = self.list_snapshots(phase=phase)
        return snapshots[0] if snapshots else None
    
    def load_snapshot(self, snapshot_id: str) -> Optional[RollbackSnapshot]:
        """
        Load snapshot from disk.
        
        Args:
            snapshot_id: Snapshot ID to load
            
        Returns:
            RollbackSnapshot or None if not found
        """
        manifest_file = self.rollback_dir / f"{snapshot_id}.json"
        return self._load_snapshot_from_file(manifest_file)
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """
        Delete snapshot manifest.
        
        Args:
            snapshot_id: Snapshot ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        manifest_file = self.rollback_dir / f"{snapshot_id}.json"
        
        if manifest_file.exists():
            manifest_file.unlink()
            logger.info(f"🗑️ Snapshot deleted: {snapshot_id}")
            return True
        
        return False
    
    # Private helper methods
    
    def _get_git_commit(self) -> str:
        """Get current git commit SHA."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.cortex_root,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    
    def _get_git_branch(self) -> str:
        """Get current git branch."""
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=self.cortex_root,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    
    def _capture_brain_state(self) -> Dict:
        """Capture current brain state."""
        brain_files = [
            "knowledge-graph.yaml",
            "conversation-context.jsonl",
            "lessons-learned.yaml"
        ]
        
        state = {}
        brain_dir = self.cortex_root / "cortex-brain"
        
        for filename in brain_files:
            filepath = brain_dir / filename
            if filepath.exists():
                state[filename] = filepath.read_text()
        
        return state
    
    def _capture_config_state(self) -> Dict:
        """Capture current config state."""
        config_file = self.cortex_root / "cortex.config.json"
        
        if config_file.exists():
            return {"cortex.config.json": config_file.read_text()}
        
        return {}
    
    def _check_git_clean(self) -> bool:
        """Check if git working directory is clean."""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.cortex_root,
            capture_output=True,
            text=True,
            check=False
        )
        return not result.stdout.strip()  # Empty means clean
    
    def _check_git_consistency(self) -> bool:
        """Check git repository consistency."""
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=self.cortex_root,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    
    def _check_file_integrity(self) -> bool:
        """Basic file integrity check."""
        # Check critical directories exist
        critical_dirs = ["src", "cortex-brain", "tests"]
        
        for dirname in critical_dirs:
            if not (self.cortex_root / dirname).exists():
                return False
        
        return True
    
    def _rollback_code(self, snapshot: RollbackSnapshot) -> None:
        """Rollback code via git reset."""
        subprocess.run(
            ["git", "reset", "--hard", snapshot.git_commit],
            cwd=self.cortex_root,
            check=True
        )
        logger.info(f"✅ Code rolled back to {snapshot.git_commit[:8]}")
    
    def _rollback_brain(self, snapshot: RollbackSnapshot) -> None:
        """Rollback brain state."""
        if not snapshot.brain_state:
            logger.warning("No brain state in snapshot")
            return
        
        brain_dir = self.cortex_root / "cortex-brain"
        
        for filename, content in snapshot.brain_state.items():
            filepath = brain_dir / filename
            filepath.write_text(content)
        
        logger.info("✅ Brain state restored")
    
    def _rollback_config(self, snapshot: RollbackSnapshot) -> None:
        """Rollback configuration."""
        if not snapshot.config_state:
            logger.warning("No config state in snapshot")
            return
        
        for filename, content in snapshot.config_state.items():
            filepath = self.cortex_root / filename
            filepath.write_text(content)
        
        logger.info("✅ Config restored")
    
    def _generate_rollback_preview(self, snapshot: RollbackSnapshot, rollback_type: RollbackType) -> str:
        """Generate rollback preview."""
        preview_lines = [
            f"Snapshot ID: {snapshot.snapshot_id}",
            f"Phase: {snapshot.phase}",
            f"Rollback Type: {rollback_type.value}",
            f"Git Commit: {snapshot.git_commit[:8]}",
            f"Timestamp: {snapshot.timestamp}",
            "",
            "Will restore:"
        ]
        
        if rollback_type in (RollbackType.CODE_ONLY, RollbackType.FULL):
            preview_lines.append(f"  - Code (git reset to {snapshot.git_commit[:8]})")
        
        if rollback_type in (RollbackType.BRAIN_ONLY, RollbackType.FULL):
            brain_files = len(snapshot.brain_state) if snapshot.brain_state else 0
            preview_lines.append(f"  - Brain state ({brain_files} files)")
        
        if rollback_type == RollbackType.FULL:
            config_files = len(snapshot.config_state) if snapshot.config_state else 0
            preview_lines.append(f"  - Configuration ({config_files} files)")
        
        return "\n".join(preview_lines)
    
    def _generate_rollback_report(self, snapshot: RollbackSnapshot, rollback_type: RollbackType) -> Dict:
        """Generate detailed rollback report."""
        return {
            "snapshot_id": snapshot.snapshot_id,
            "phase": snapshot.phase,
            "rollback_type": rollback_type.value,
            "git_commit": snapshot.git_commit,
            "timestamp": datetime.now().isoformat(),
            "files_restored": {
                "code": rollback_type in (RollbackType.CODE_ONLY, RollbackType.FULL),
                "brain": rollback_type in (RollbackType.BRAIN_ONLY, RollbackType.FULL),
                "config": rollback_type == RollbackType.FULL
            }
        }
    
    def _save_snapshot_manifest(self, snapshot: RollbackSnapshot) -> None:
        """Save snapshot manifest to disk."""
        manifest_file = self.rollback_dir / f"{snapshot.snapshot_id}.json"
        
        # Convert snapshot to dict
        snapshot_dict = asdict(snapshot)
        # Convert enum to string
        snapshot_dict['snapshot_type'] = snapshot.snapshot_type.value
        
        with open(manifest_file, 'w') as f:
            json.dump(snapshot_dict, f, indent=2)
    
    def _load_snapshot_from_file(self, manifest_file: Path) -> Optional[RollbackSnapshot]:
        """Load snapshot from manifest file."""
        if not manifest_file.exists():
            return None
        
        try:
            with open(manifest_file, 'r') as f:
                data = json.load(f)
            
            # Convert string back to enum
            data['snapshot_type'] = RollbackType(data['snapshot_type'])
            
            return RollbackSnapshot(**data)
            
        except Exception as e:
            logger.error(f"Failed to load snapshot from {manifest_file}: {e}")
            return None


# Convenience functions for orchestrator integration

def create_deployment_snapshot(
    phase: str,
    snapshot_type: RollbackType = RollbackType.FULL,
    cortex_root: Path = None
) -> RollbackSnapshot:
    """
    Create deployment snapshot (convenience function).
    
    Args:
        phase: Deployment phase
        snapshot_type: Type of snapshot
        cortex_root: CORTEX root path
        
    Returns:
        RollbackSnapshot object
    """
    manager = DeploymentRollbackManager(cortex_root=cortex_root)
    return manager.create_snapshot(phase=phase, snapshot_type=snapshot_type)


def execute_rollback(
    snapshot_id: str,
    rollback_type: RollbackType = None,
    dry_run: bool = False,
    cortex_root: Path = None
) -> RollbackResult:
    """
    Execute rollback (convenience function).
    
    Args:
        snapshot_id: Snapshot ID to rollback to
        rollback_type: Override rollback type
        dry_run: Preview only mode
        cortex_root: CORTEX root path
        
    Returns:
        RollbackResult
    """
    manager = DeploymentRollbackManager(cortex_root=cortex_root)
    return manager.execute_rollback(
        snapshot_id=snapshot_id,
        rollback_type=rollback_type,
        dry_run=dry_run
    )


def validate_rollback(snapshot_id: str, cortex_root: Path = None) -> RollbackValidation:
    """
    Validate rollback safety (convenience function).
    
    Args:
        snapshot_id: Snapshot ID to validate
        cortex_root: CORTEX root path
        
    Returns:
        RollbackValidation result
    """
    manager = DeploymentRollbackManager(cortex_root=cortex_root)
    return manager.validate_rollback(snapshot_id=snapshot_id)


if __name__ == "__main__":
    print("=" * 60)
    print("Deployment Rollback Manager - Direct Test")
    print("=" * 60)
    
    # Test snapshot creation
    manager = DeploymentRollbackManager()
    
    print("\n[Test 1] Creating BUILD phase snapshot...")
    snapshot = manager.create_snapshot(
        phase="BUILD",
        snapshot_type=RollbackType.FULL
    )
    print(f"✅ Snapshot created: {snapshot.snapshot_id}")
    print(f"   Phase: {snapshot.phase}")
    print(f"   Type: {snapshot.snapshot_type.value}")
    print(f"   Git commit: {snapshot.git_commit[:8]}")
    
    print("\n[Test 2] Listing all snapshots...")
    snapshots = manager.list_snapshots()
    print(f"✅ Found {len(snapshots)} snapshot(s)")
    
    print("\n[Test 3] Validating rollback...")
    validation = manager.validate_rollback(snapshot.snapshot_id)
    print(f"✅ Validation: safe={validation.safe_to_rollback}, clean={validation.git_clean}")
    
    print("\n[Test 4] Dry-run rollback preview...")
    result = manager.execute_rollback(snapshot.snapshot_id, dry_run=True)
    print(f"✅ Preview generated")
    print(result.preview)
    
    print("\n" + "=" * 60)
    print("✅ Manager tests complete")
    print("=" * 60)
