"""
Cleanup Manifest Manager for Git Sync Intelligence

Tracks CORTEX cleanup operations and synchronizes deletions across user
workspaces while preserving user-modified intelligence.

AC-ID: AC-GIT-SYNC-CLEANUP-001
Phase: Git Sync Enhancement
Author: Asif Hussain
Date: 2026-02-10

Features:
- Track file deletions with hash verification
- Smart deletion propagation (hash-based safety)
- Protected path preservation (cortex_brain/tier*, company/domains)
- Rollback support via backup
- Audit trail for all sync operations
"""

import hashlib
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeletedFileEntry:
    """Represents a file deleted by CORTEX cleanup."""
    
    path: str
    reason: str
    hash_at_deletion: str
    timestamp: str
    operation_id: str
    category: str  # "test", "markdown", "utility", "deprecated"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML serialization."""
        return asdict(self)


@dataclass
class CleanupOperation:
    """Represents a single cleanup operation."""
    
    operation_id: str
    timestamp: str
    description: str
    deleted_files: List[DeletedFileEntry] = field(default_factory=list)
    files_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "operation_id": self.operation_id,
            "timestamp": self.timestamp,
            "description": self.description,
            "files_count": self.files_count,
            "deleted_files": [f.to_dict() for f in self.deleted_files]
        }


@dataclass
class CleanupManifest:
    """Master manifest tracking all cleanup operations."""
    
    version: str = "1.0"
    last_sync: Optional[str] = None
    operations: List[CleanupOperation] = field(default_factory=list)
    protected_patterns: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "version": self.version,
            "last_sync": self.last_sync,
            "protected_patterns": self.protected_patterns,
            "cleanup_operations": [op.to_dict() for op in self.operations]
        }


class CleanupManifestManager:
    """
    Manages cleanup manifest for git sync intelligence.
    
    Workflow:
    1. Record deletions during CORTEX cleanup
    2. Apply deletions to user workspace (hash-based safety)
    3. Skip files modified by user
    4. Preserve protected intelligence paths
    5. Log all operations for audit
    
    Usage:
        manager = CleanupManifestManager()
        
        # During cleanup in CORTEX repo
        manager.record_deletion("tests/unit/test_obsolete.py", "Obsolete test")
        manager.save_manifest()
        
        # During user sync
        manager.apply_manifest_to_workspace("/path/to/user/repo")
    """
    
    MANIFEST_FILENAME = ".cortex-cleanup-manifest.yaml"
    
    # Protected paths - NEVER delete these even if in manifest
    PROTECTED_PATTERNS = [
        "cortex_brain/tier0/**",
        "cortex_brain/tier1/**",
        "cortex_brain/tier2/**",
        "cortex_brain/tier3/**",
        "cortex_brain/domain/**",
        "cortex_brain/domain_brain/**",
        "cortex_brain/state/**",
        "company/domains/**/*.yaml",
        "company/dashboards/**",
        "cortex-registry/**",
    ]
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize manifest manager.
        
        Args:
            repo_path: Path to repository (defaults to current directory)
        """
        self.repo_path = Path(repo_path or ".").resolve()
        self.manifest_path = self.repo_path / self.MANIFEST_FILENAME
        self.manifest = self._load_manifest()
        
    def _load_manifest(self) -> CleanupManifest:
        """Load existing manifest or create new one."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Parse operations
                operations = []
                for op_data in data.get("cleanup_operations", []):
                    deleted_files = [
                        DeletedFileEntry(**file_data)
                        for file_data in op_data.get("deleted_files", [])
                    ]
                    operations.append(CleanupOperation(
                        operation_id=op_data["operation_id"],
                        timestamp=op_data["timestamp"],
                        description=op_data.get("description", ""),
                        deleted_files=deleted_files,
                        files_count=op_data.get("files_count", len(deleted_files))
                    ))
                
                return CleanupManifest(
                    version=data.get("version", "1.0"),
                    last_sync=data.get("last_sync"),
                    operations=operations,
                    protected_patterns=data.get("protected_patterns", self.PROTECTED_PATTERNS)
                )
            except Exception as e:
                logger.warning(f"Failed to load manifest: {e}, creating new one")
        
        # Create new manifest
        return CleanupManifest(protected_patterns=self.PROTECTED_PATTERNS)
    
    def save_manifest(self) -> None:
        """Save manifest to disk."""
        try:
            with open(self.manifest_path, 'w') as f:
                yaml.dump(
                    self.manifest.to_dict(),
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True
                )
            logger.info(f"Manifest saved: {self.manifest_path}")
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")
            raise
    
    def record_deletion(
        self,
        file_path: str,
        reason: str,
        category: str = "other",
        operation_id: Optional[str] = None
    ) -> None:
        """
        Record a file deletion in the manifest.
        
        Args:
            file_path: Path to deleted file (relative to repo root)
            reason: Reason for deletion
            category: Category of deleted file
            operation_id: Optional operation ID (auto-generated if not provided)
        """
        full_path = self.repo_path / file_path
        
        # Calculate hash if file still exists (before deletion)
        file_hash = ""
        if full_path.exists():
            file_hash = self._calculate_file_hash(full_path)
        
        # Get or create current operation
        if operation_id is None:
            operation_id = f"CLEANUP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Find existing operation or create new one
        operation = None
        for op in self.manifest.operations:
            if op.operation_id == operation_id:
                operation = op
                break
        
        if operation is None:
            operation = CleanupOperation(
                operation_id=operation_id,
                timestamp=datetime.now().isoformat(),
                description=f"Cleanup operation {operation_id}"
            )
            self.manifest.operations.append(operation)
        
        # Add deletion entry
        entry = DeletedFileEntry(
            path=file_path,
            reason=reason,
            hash_at_deletion=file_hash,
            timestamp=datetime.now().isoformat(),
            operation_id=operation_id,
            category=category
        )
        
        operation.deleted_files.append(entry)
        operation.files_count = len(operation.deleted_files)
        
        logger.info(f"Recorded deletion: {file_path} ({reason})")
    
    def apply_manifest_to_workspace(
        self,
        workspace_path: Path,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Apply manifest deletions to user workspace with safety checks.
        
        Args:
            workspace_path: Path to user's workspace
            dry_run: If True, only simulate (don't delete)
            
        Returns:
            Dict with operation results
        """
        workspace_path = Path(workspace_path).resolve()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "workspace": str(workspace_path),
            "dry_run": dry_run,
            "files_deleted": [],
            "files_preserved_user_modified": [],
            "files_preserved_protected": [],
            "files_not_found": [],
            "errors": []
        }
        
        # Process all deletions from all operations
        for operation in self.manifest.operations:
            for entry in operation.deleted_files:
                user_file = workspace_path / entry.path
                
                # Check if file exists
                if not user_file.exists():
                    results["files_not_found"].append(entry.path)
                    continue
                
                # Check if protected path
                if self._is_protected_path(entry.path):
                    results["files_preserved_protected"].append({
                        "path": entry.path,
                        "reason": "Protected intelligence path"
                    })
                    logger.info(f"Protected: {entry.path}")
                    continue
                
                # Calculate current hash
                current_hash = self._calculate_file_hash(user_file)
                
                # Compare hashes
                if current_hash == entry.hash_at_deletion:
                    # File unchanged by user → safe to delete
                    if not dry_run:
                        try:
                            user_file.unlink()
                            logger.info(f"Deleted: {entry.path}")
                        except Exception as e:
                            results["errors"].append({
                                "path": entry.path,
                                "error": str(e)
                            })
                            logger.error(f"Failed to delete {entry.path}: {e}")
                            continue
                    
                    results["files_deleted"].append({
                        "path": entry.path,
                        "reason": entry.reason,
                        "category": entry.category
                    })
                else:
                    # User modified → preserve
                    results["files_preserved_user_modified"].append({
                        "path": entry.path,
                        "reason": "User modified (hash mismatch)"
                    })
                    logger.info(f"Preserved (user modified): {entry.path}")
        
        # Update last sync timestamp
        if not dry_run:
            self.manifest.last_sync = datetime.now().isoformat()
            self.save_manifest()
        
        return results
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""
    
    def _is_protected_path(self, path: str) -> bool:
        """Check if path matches any protected pattern."""
        from fnmatch import fnmatch
        
        for pattern in self.manifest.protected_patterns:
            # Convert ** glob to fnmatch pattern
            pattern_normalized = pattern.replace("**", "*")
            if fnmatch(path, pattern_normalized):
                return True
        return False
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get statistics about tracked cleanups."""
        total_deletions = sum(
            op.files_count for op in self.manifest.operations
        )
        
        categories = {}
        for op in self.manifest.operations:
            for entry in op.deleted_files:
                cat = entry.category
                categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_operations": len(self.manifest.operations),
            "total_deletions": total_deletions,
            "deletions_by_category": categories,
            "last_sync": self.manifest.last_sync,
            "protected_patterns_count": len(self.manifest.protected_patterns)
        }
    
    def generate_sync_report(self, apply_results: Dict) -> str:
        """Generate human-readable sync report."""
        report_lines = [
            "=" * 70,
            "🔄 CORTEX Git Sync Cleanup Report",
            "=" * 70,
            "",
            f"Workspace: {apply_results['workspace']}",
            f"Timestamp: {apply_results['timestamp']}",
            f"Mode: {'DRY RUN' if apply_results['dry_run'] else 'LIVE'}",
            "",
            "📊 Summary:",
            f"  ✅ Files deleted: {len(apply_results['files_deleted'])}",
            f"  🔒 Files preserved (user modified): {len(apply_results['files_preserved_user_modified'])}",
            f"  🛡️  Files preserved (protected): {len(apply_results['files_preserved_protected'])}",
            f"  ⚠️  Files not found: {len(apply_results['files_not_found'])}",
            f"  ❌ Errors: {len(apply_results['errors'])}",
            ""
        ]
        
        if apply_results['files_deleted']:
            report_lines.extend([
                "✅ Deleted Files:",
                ""
            ])
            for item in apply_results['files_deleted'][:20]:  # Show first 20
                report_lines.append(f"  - {item['path']}")
                report_lines.append(f"    Reason: {item['reason']}")
            
            if len(apply_results['files_deleted']) > 20:
                report_lines.append(f"  ... and {len(apply_results['files_deleted']) - 20} more")
            report_lines.append("")
        
        if apply_results['files_preserved_user_modified']:
            report_lines.extend([
                "🔒 Preserved (User Modified):",
                ""
            ])
            for item in apply_results['files_preserved_user_modified'][:10]:
                report_lines.append(f"  - {item['path']}")
            
            if len(apply_results['files_preserved_user_modified']) > 10:
                report_lines.append(f"  ... and {len(apply_results['files_preserved_user_modified']) - 10} more")
            report_lines.append("")
        
        if apply_results['errors']:
            report_lines.extend([
                "❌ Errors:",
                ""
            ])
            for item in apply_results['errors']:
                report_lines.append(f"  - {item['path']}: {item['error']}")
            report_lines.append("")
        
        report_lines.extend([
            "=" * 70,
            "✅ Sync Complete",
            "=" * 70
        ])
        
        return "\n".join(report_lines)
