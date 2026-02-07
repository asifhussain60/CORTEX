"""
Brain State Manager: Flush & Reload Brain State

Manages brain state persistence across cortex_brain/ directory:
- Flush current state to snapshot
- Reload state from snapshot
- State validation and integrity checks
- Concurrent operation support

Phase 38 Stage 5 Implementation

CORE-011: All functions have type hints ✅
CORE-012: All public APIs have Google-style docstrings ✅
CORE-008: TDD implementation (tests first) ✅
"""

import json
import logging
import threading
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class StateSnapshot:
    """Represents a brain state snapshot.
    
    Attributes:
        path: Path to snapshot file
        timestamp: When snapshot was created
        size_bytes: Total size in bytes
        file_count: Number of files in snapshot
        checksums: File checksums for integrity
    """
    path: Path
    timestamp: datetime
    size_bytes: int
    file_count: int
    checksums: Dict[str, str] = field(default_factory=dict)


@dataclass
class FlushResult:
    """Result of flush operation.
    
    Attributes:
        success: Whether flush succeeded
        snapshot_path: Path to created snapshot
        timestamp: When flush occurred
        metadata: Additional metadata
        error_message: Error message if failed
    """
    success: bool
    snapshot_path: Optional[Path] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class ReloadResult:
    """Result of reload operation.
    
    Attributes:
        success: Whether reload succeeded
        backup_path: Path to backup created before reload
        statistics: Reload statistics
        error_message: Error message if failed
    """
    success: bool
    backup_path: Optional[Path] = None
    statistics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class StateValidationError(Exception):
    """Raised when state validation fails."""
    pass


class BrainStateManager:
    """Manages brain state flush and reload operations.
    
    Provides thread-safe state persistence for cortex_brain/ directory:
    - Flush state to timestamped snapshots
    - Reload state from snapshots with backup
    - Validate state integrity
    - Manage snapshot lifecycle
    
    Example:
        >>> manager = BrainStateManager(brain_root=Path("cortex_brain"))
        >>> result = manager.flush_state()
        >>> if result.success:
        ...     reload_result = manager.reload_state(result.snapshot_path)
    """
    
    def __init__(
        self,
        brain_root: Path,
        validate: bool = False
    ) -> None:
        """Initialize Brain State Manager.
        
        Args:
            brain_root: Path to cortex_brain directory
            validate: Whether to validate directory structure on init
            
        Raises:
            ValueError: If validate=True and structure is invalid
        """
        self.brain_root = Path(brain_root)
        self.logger = logging.getLogger(f"{__name__}.BrainStateManager")
        self._lock = threading.RLock()
        self._snapshot_dir = self.brain_root.parent / ".brain_snapshots"
        
        # Create directories if they don't exist
        self.brain_root.mkdir(parents=True, exist_ok=True)
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        if validate:
            self._validate_structure()
    
    def _validate_structure(self) -> None:
        """Validate brain root directory structure.
        
        Raises:
            ValueError: If required tier directories are missing
        """
        required_tiers = ["tier0", "tier1", "tier2", "tier3"]
        missing = []
        
        for tier in required_tiers:
            if not (self.brain_root / tier).exists():
                missing.append(tier)
        
        if missing:
            raise ValueError(
                f"Invalid brain root structure. Missing tiers: {missing}"
            )
    
    def flush_state(self) -> FlushResult:
        """Flush current brain state to snapshot.
        
        Creates timestamped snapshot of all brain state including:
        - All tier directories
        - File contents and structure
        - Metadata and checksums
        
        Returns:
            FlushResult with snapshot path and metadata
        """
        with self._lock:
            try:
                timestamp = datetime.now()
                # Use microseconds for uniqueness
                snapshot_name = f"snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond:06d}.json"
                snapshot_path = self._snapshot_dir / snapshot_name
                
                # Collect state from all tiers
                state_data = {}
                checksums = {}
                total_files = 0
                total_size = 0
                
                for tier_dir in self.brain_root.iterdir():
                    if tier_dir.is_dir() and tier_dir.name.startswith("tier"):
                        tier_name = tier_dir.name
                        state_data[tier_name] = {}
                        
                        # Recursively collect files
                        for file_path in tier_dir.rglob("*"):
                            if file_path.is_file():
                                rel_path = file_path.relative_to(self.brain_root)
                                try:
                                    content = file_path.read_text()
                                    state_data[tier_name][str(rel_path)] = content
                                    
                                    # Calculate checksum
                                    checksum = hashlib.sha256(content.encode()).hexdigest()
                                    checksums[str(rel_path)] = checksum
                                    
                                    total_files += 1
                                    total_size += len(content.encode())
                                except Exception as e:
                                    self.logger.warning(f"Failed to read {file_path}: {e}")
                
                # Create snapshot
                snapshot_obj = {
                    "version": "1.0",
                    "timestamp": timestamp.isoformat(),
                    "brain_root": str(self.brain_root),
                    "data": state_data,
                    "checksums": checksums,
                    "metadata": {
                        "total_files": total_files,
                        "total_size_bytes": total_size
                    }
                }
                
                # Write snapshot
                snapshot_path.write_text(
                    json.dumps(snapshot_obj, indent=2),
                    encoding="utf-8"
                )
                
                self.logger.info(
                    f"Flushed state to {snapshot_path} "
                    f"({total_files} files, {total_size} bytes)"
                )
                
                return FlushResult(
                    success=True,
                    snapshot_path=snapshot_path,
                    timestamp=timestamp,
                    metadata={
                        "total_files": total_files,
                        "total_size_bytes": total_size
                    }
                )
                
            except Exception as e:
                error_msg = f"Flush failed: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                return FlushResult(
                    success=False,
                    error_message=error_msg
                )
    
    def reload_state(self, snapshot_path: Path) -> ReloadResult:
        """Reload brain state from snapshot.
        
        Creates backup of current state before reload.
        Restores all files from snapshot.
        
        Args:
            snapshot_path: Path to snapshot file
            
        Returns:
            ReloadResult with statistics and backup info
        """
        with self._lock:
            try:
                # Validate snapshot exists
                if not snapshot_path.exists():
                    return ReloadResult(
                        success=False,
                        error_message=f"Snapshot not found: {snapshot_path}"
                    )
                
                # Create backup first
                backup_result = self.flush_state()
                if not backup_result.success:
                    return ReloadResult(
                        success=False,
                        error_message="Failed to create backup before reload"
                    )
                
                # Load snapshot
                try:
                    snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    return ReloadResult(
                        success=False,
                        error_message=f"Snapshot integrity error: {str(e)}"
                    )
                
                # Validate snapshot format
                if "data" not in snapshot_data:
                    return ReloadResult(
                        success=False,
                        error_message="Invalid snapshot format: missing data"
                    )
                
                # Restore files
                start_time = datetime.now()
                files_restored = 0
                
                for tier_name, tier_data in snapshot_data["data"].items():
                    for rel_path_str, content in tier_data.items():
                        # rel_path is like "tier0/governance.yaml"
                        file_path = self.brain_root / rel_path_str
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        try:
                            file_path.write_text(content, encoding="utf-8")
                            files_restored += 1
                        except Exception as e:
                            self.logger.warning(f"Failed to restore {file_path}: {e}")
                
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                self.logger.info(
                    f"Reloaded state from {snapshot_path} "
                    f"({files_restored} files in {duration:.2f}ms)"
                )
                
                return ReloadResult(
                    success=True,
                    backup_path=backup_result.snapshot_path,
                    statistics={
                        "files_restored": files_restored,
                        "restore_duration_ms": duration
                    }
                )
                
            except Exception as e:
                error_msg = f"Reload failed: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                
                # Check for permission errors
                if "permission" in str(e).lower():
                    error_msg = f"Permission denied: {str(e)}"
                
                return ReloadResult(
                    success=False,
                    error_message=error_msg
                )
    
    def validate_state(
        self,
        snapshot_path: Path,
        raise_on_error: bool = False
    ) -> bool:
        """Validate state snapshot integrity.
        
        Args:
            snapshot_path: Path to snapshot file
            raise_on_error: Whether to raise exception on validation error
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            StateValidationError: If raise_on_error=True and validation fails
        """
        try:
            if not snapshot_path.exists():
                if raise_on_error:
                    raise StateValidationError(f"Snapshot not found: {snapshot_path}")
                return False
            
            # Load snapshot
            snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
            
            # Check required fields
            if "data" not in snapshot_data:
                if raise_on_error:
                    raise StateValidationError("Missing 'data' field")
                return False
            
            # Check all tiers present
            required_tiers = {"tier0", "tier1", "tier2", "tier3"}
            present_tiers = set(snapshot_data["data"].keys())
            
            if not required_tiers.issubset(present_tiers):
                if raise_on_error:
                    missing = required_tiers - present_tiers
                    raise StateValidationError(f"Missing tiers: {missing}")
                return False
            
            # Check for null/corrupted data
            for tier_name, tier_data in snapshot_data["data"].items():
                if tier_data is None:
                    if raise_on_error:
                        raise StateValidationError(f"Corrupted data in {tier_name}")
                    return False
            
            return True
            
        except json.JSONDecodeError as e:
            if raise_on_error:
                raise StateValidationError(f"JSON decode error: {str(e)}")
            return False
        except Exception as e:
            if raise_on_error:
                raise StateValidationError(f"Validation error: {str(e)}")
            return False
    
    def get_validation_report(self, snapshot_path: Path) -> Dict[str, Any]:
        """Get detailed validation report for snapshot.
        
        Args:
            snapshot_path: Path to snapshot file
            
        Returns:
            Dictionary with validation results and issues
        """
        report = {
            "is_valid": False,
            "issues": [],
            "validation_timestamp": datetime.now().isoformat()
        }
        
        try:
            if not snapshot_path.exists():
                report["issues"].append("Snapshot file not found")
                return report
            
            snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
            
            # Check structure
            if "data" not in snapshot_data:
                report["issues"].append("Missing 'data' field")
            
            # Check tiers
            required_tiers = {"tier0", "tier1", "tier2", "tier3"}
            present_tiers = set(snapshot_data.get("data", {}).keys())
            missing_tiers = required_tiers - present_tiers
            
            if missing_tiers:
                report["issues"].append(f"Missing tiers: {missing_tiers}")
            
            report["is_valid"] = len(report["issues"]) == 0
            
        except Exception as e:
            report["issues"].append(f"Validation error: {str(e)}")
        
        return report
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current brain state (without creating snapshot).
        
        Returns:
            Dictionary with current state information
        """
        state = {
            "brain_root": str(self.brain_root),
            "timestamp": datetime.now().isoformat(),
            "tier_counts": {}
        }
        
        with self._lock:
            for tier_dir in self.brain_root.iterdir():
                if tier_dir.is_dir() and tier_dir.name.startswith("tier"):
                    file_count = len(list(tier_dir.rglob("*")))
                    state["tier_counts"][tier_dir.name] = file_count
        
        return state
    
    def list_snapshots(self) -> List[StateSnapshot]:
        """List all available snapshots.
        
        Returns:
            List of StateSnapshot objects, sorted by timestamp (newest first)
        """
        snapshots = []
        
        for snapshot_file in self._snapshot_dir.glob("snapshot_*.json"):
            try:
                snapshot_data = json.loads(snapshot_file.read_text(encoding="utf-8"))
                
                timestamp = datetime.fromisoformat(snapshot_data.get("timestamp", ""))
                metadata = snapshot_data.get("metadata", {})
                checksums = snapshot_data.get("checksums", {})
                
                snapshots.append(StateSnapshot(
                    path=snapshot_file,
                    timestamp=timestamp,
                    size_bytes=metadata.get("total_size_bytes", 0),
                    file_count=metadata.get("total_files", 0),
                    checksums=checksums
                ))
            except Exception as e:
                self.logger.warning(f"Failed to parse snapshot {snapshot_file}: {e}")
        
        # Sort by timestamp (newest first)
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        
        return snapshots
    
    def cleanup_snapshots(self, max_age_days: int = 7) -> int:
        """Delete snapshots older than max_age_days.
        
        Args:
            max_age_days: Maximum age in days to keep
            
        Returns:
            Number of snapshots deleted
        """
        cutoff = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0
        
        for snapshot in self.list_snapshots():
            if snapshot.timestamp < cutoff:
                try:
                    snapshot.path.unlink()
                    deleted_count += 1
                    self.logger.info(f"Deleted old snapshot: {snapshot.path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete {snapshot.path}: {e}")
        
        return deleted_count


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    brain_root = Path("cortex_brain")
    manager = BrainStateManager(brain_root=brain_root)
    
    # Flush state
    print("Flushing brain state...")
    flush_result = manager.flush_state()
    print(f"Flush result: {flush_result.success}")
    
    if flush_result.success:
        print(f"Snapshot: {flush_result.snapshot_path}")
        print(f"Files: {flush_result.metadata['total_files']}")
        
        # List snapshots
        snapshots = manager.list_snapshots()
        print(f"\nAvailable snapshots: {len(snapshots)}")
        
        # Validate
        is_valid = manager.validate_state(flush_result.snapshot_path)
        print(f"Snapshot valid: {is_valid}")
