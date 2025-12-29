"""
Alignment State Management

Handles serialization, deserialization, and validation of alignment state.
Supports incremental alignment with file change tracking and auto-discovery.

Features:
- Enhanced state structure with file checksums
- Change detection and diff computation
- Schema validation and migration
- Backward compatibility with legacy format
- Auto-wiring validation

Version: 1.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict


@dataclass
class FileChecksum:
    """File checksum and metadata."""
    sha256: str
    last_modified: str
    last_checked: str
    size_bytes: int
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'FileChecksum':
        """Compute checksum from file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        stat = file_path.stat()
        return cls(
            sha256=sha256_hash.hexdigest(),
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            last_checked=datetime.now().isoformat(),
            size_bytes=stat.st_size
        )


@dataclass
class FeatureScore:
    """Feature integration score with validation metadata."""
    score: int
    module_path: str
    file_hash: str
    last_validated: str
    validation_count: int
    discovered: bool
    imported: bool
    instantiated: bool
    documented: bool
    tested: bool
    wired: bool
    optimized: bool
    api_documented: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureScore':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class ChangesSummary:
    """Summary of changes detected since last alignment."""
    files_added: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    features_impacted: List[str] = field(default_factory=list)
    
    def has_changes(self) -> bool:
        """Check if any changes detected."""
        return bool(
            self.files_added or 
            self.files_modified or 
            self.files_deleted or 
            self.features_impacted
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PerformanceMetrics:
    """Performance metrics for alignment run."""
    last_run_duration_seconds: float = 0.0
    features_checked: int = 0
    features_skipped: int = 0
    cache_hit_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AlignmentState:
    """Complete alignment state with incremental tracking."""
    version: str = "3.2"
    last_alignment: str = ""
    last_full_scan: str = ""
    scan_mode: str = "full"  # full, incremental
    context_type: str = "unknown"  # admin, user, unknown
    
    file_checksums: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    feature_scores: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    changes_detected: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    overall_health: int = 0
    alignment_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "last_alignment": self.last_alignment,
            "last_full_scan": self.last_full_scan,
            "scan_mode": self.scan_mode,
            "context_type": self.context_type,
            "file_checksums": self.file_checksums,
            "feature_scores": self.feature_scores,
            "changes_detected": self.changes_detected,
            "performance_metrics": self.performance_metrics,
            "overall_health": self.overall_health,
            "alignment_history": self.alignment_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlignmentState':
        """Create from dictionary."""
        return cls(
            version=data.get("version", "3.2"),
            last_alignment=data.get("last_alignment", ""),
            last_full_scan=data.get("last_full_scan", ""),
            scan_mode=data.get("scan_mode", "full"),
            context_type=data.get("context_type", "unknown"),
            file_checksums=data.get("file_checksums", {}),
            feature_scores=data.get("feature_scores", {}),
            changes_detected=data.get("changes_detected", {}),
            performance_metrics=data.get("performance_metrics", {}),
            overall_health=data.get("overall_health", 0),
            alignment_history=data.get("alignment_history", [])
        )
    
    def should_run_full_scan(self) -> bool:
        """Determine if full scan is required."""
        if not self.last_full_scan:
            return True
        
        try:
            last_scan = datetime.fromisoformat(self.last_full_scan)
            now = datetime.now()
            hours_since_scan = (now - last_scan).total_seconds() / 3600
            
            # Force full scan after 24 hours
            return hours_since_scan >= 24
        except (ValueError, TypeError):
            return True
    
    def is_stale(self, hours: int = 48) -> bool:
        """Check if state is stale."""
        if not self.last_alignment:
            return True
        
        try:
            last_run = datetime.fromisoformat(self.last_alignment)
            now = datetime.now()
            hours_since_run = (now - last_run).total_seconds() / 3600
            return hours_since_run >= hours
        except (ValueError, TypeError):
            return True
    
    def add_to_history(self, health: int, total_features: int, 
                       critical_issues: int, warnings: int) -> None:
        """Add current run to history."""
        self.alignment_history.append({
            "timestamp": datetime.now().isoformat(),
            "overall_health": health,
            "total_features": total_features,
            "critical_issues": critical_issues,
            "warnings": warnings
        })
        
        # Keep last 10 runs only
        if len(self.alignment_history) > 10:
            self.alignment_history = self.alignment_history[-10:]


class AlignmentStateManager:
    """Manages alignment state persistence and operations."""
    
    def __init__(self, state_path: Path):
        """Initialize manager with state file path."""
        self.state_path = state_path
    
    def load(self) -> Optional[AlignmentState]:
        """Load alignment state from file."""
        if not self.state_path.exists():
            return None
        
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check version and migrate if needed
            version = data.get("version", "3.0")
            if version != "3.2":
                data = self._migrate_state(data, version)
            
            return AlignmentState.from_dict(data)
        
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️  Corrupted alignment state, will regenerate: {e}")
            return None
    
    def save(self, state: AlignmentState) -> bool:
        """Save alignment state to file."""
        try:
            # Ensure parent directory exists
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with pretty formatting
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(state.to_dict(), f, indent=2, sort_keys=False)
            
            return True
        
        except Exception as e:
            print(f"❌ Failed to save alignment state: {e}")
            return False
    
    def backup(self) -> bool:
        """Create backup of current state."""
        if not self.state_path.exists():
            return False
        
        try:
            backup_path = self.state_path.with_suffix('.json.backup')
            import shutil
            shutil.copy2(self.state_path, backup_path)
            return True
        except Exception:
            return False
    
    def _migrate_state(self, data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """Migrate state from older version to 3.2."""
        print(f"🔄 Migrating alignment state from v{from_version} to v3.2...")
        
        # Add missing fields with defaults
        if "version" not in data:
            data["version"] = "3.2"
        
        if "last_full_scan" not in data:
            data["last_full_scan"] = data.get("last_alignment", "")
        
        if "scan_mode" not in data:
            data["scan_mode"] = "full"
        
        if "context_type" not in data:
            data["context_type"] = "unknown"
        
        if "file_checksums" not in data:
            data["file_checksums"] = {}
        
        if "changes_detected" not in data:
            data["changes_detected"] = {
                "files_added": [],
                "files_modified": [],
                "files_deleted": [],
                "features_impacted": []
            }
        
        if "performance_metrics" not in data:
            data["performance_metrics"] = {
                "last_run_duration_seconds": 0.0,
                "features_checked": 0,
                "features_skipped": 0,
                "cache_hit_rate": 0.0
            }
        
        # Enhance feature_scores with new fields
        for feature_name, score_data in data.get("feature_scores", {}).items():
            if "module_path" not in score_data:
                score_data["module_path"] = ""
            if "file_hash" not in score_data:
                score_data["file_hash"] = ""
            if "last_validated" not in score_data:
                score_data["last_validated"] = score_data.get("timestamp", "")
            if "validation_count" not in score_data:
                score_data["validation_count"] = 1
        
        print("✅ Migration complete")
        return data
    
    def detect_context_type(self, project_root: Path) -> str:
        """Detect if running in admin (CORTEX) or user (dev) context."""
        # Check for CORTEX-specific markers
        admin_markers = [
            project_root / "cortex-brain" / "admin",
            project_root / "src" / "operations" / "modules" / "admin",
            project_root / ".github" / "prompts" / "CORTEX.prompt.md"
        ]
        
        is_admin = any(marker.exists() for marker in admin_markers)
        return "admin" if is_admin else "user"
    
    def compute_file_checksums(self, file_paths: List[Path]) -> Dict[str, Dict[str, Any]]:
        """Compute checksums for multiple files."""
        checksums = {}
        
        for file_path in file_paths:
            if not file_path.exists() or not file_path.is_file():
                continue
            
            try:
                checksum = FileChecksum.from_file(file_path)
                checksums[str(file_path)] = {
                    "sha256": checksum.sha256,
                    "last_modified": checksum.last_modified,
                    "last_checked": checksum.last_checked,
                    "size_bytes": checksum.size_bytes
                }
            except Exception as e:
                print(f"⚠️  Failed to compute checksum for {file_path}: {e}")
        
        return checksums
    
    def detect_file_changes(self, current_checksums: Dict[str, Dict[str, Any]], 
                           previous_state: AlignmentState) -> ChangesSummary:
        """Detect file changes between current and previous state."""
        changes = ChangesSummary()
        
        previous_checksums = previous_state.file_checksums
        
        # Find added files
        for file_path in current_checksums.keys():
            if file_path not in previous_checksums:
                changes.files_added.append(file_path)
        
        # Find modified and deleted files
        for file_path in previous_checksums.keys():
            if file_path not in current_checksums:
                changes.files_deleted.append(file_path)
            elif current_checksums[file_path]["sha256"] != previous_checksums[file_path]["sha256"]:
                changes.files_modified.append(file_path)
        
        return changes
    
    def map_files_to_features(self, file_paths: List[str], 
                             feature_scores: Dict[str, Dict[str, Any]]) -> Set[str]:
        """Map changed files to impacted features."""
        impacted_features = set()
        
        for feature_name, score_data in feature_scores.items():
            module_path = score_data.get("module_path", "")
            if module_path in file_paths:
                impacted_features.add(feature_name)
        
        return impacted_features
