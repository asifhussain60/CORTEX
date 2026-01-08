"""
Enhanced Vacuum Orchestrator - CORTEX 6.0
feat08-cleanup Phase 1

Generic pattern-based cleanup with dry-run, rollback, and multi-repo support

Author: Asif Hussain
Version: 2.0.0
Created: 2026-01-08
"""

import json
import shutil
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from enum import Enum


class CleanupCategory(str, Enum):
    """Cleanup categories"""
    PYTHON_CACHE = "python_cache"
    BUILD_ARTIFACTS = "build_artifacts"
    TEST_CACHE = "test_cache"
    LOG_FILES = "log_files"
    TEMP_FILES = "temp_files"
    NODE_MODULES = "node_modules"
    SYSTEM_FILES = "system_files"
    CUSTOM = "custom"


@dataclass
class CleanupPattern:
    """Represents a cleanup pattern"""
    category: CleanupCategory
    pattern: str
    description: str
    size_threshold_mb: Optional[float] = None
    age_days: Optional[int] = None
    
    def matches(self, path: Path) -> bool:
        """Check if path matches this pattern"""
        import fnmatch
        path_str = str(path)
        return fnmatch.fnmatch(path_str, self.pattern)


@dataclass
class CleanupItem:
    """Represents an item to be cleaned"""
    path: Path
    category: CleanupCategory
    size_bytes: int
    is_directory: bool
    pattern_matched: str
    
    @property
    def size_mb(self) -> float:
        """Size in megabytes"""
        return self.size_bytes / (1024 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "path": str(self.path),
            "category": self.category.value,
            "size_bytes": self.size_bytes,
            "size_mb": round(self.size_mb, 2),
            "is_directory": self.is_directory,
            "pattern_matched": self.pattern_matched
        }


@dataclass
class CleanupResult:
    """Result of cleanup operation"""
    items_found: int
    items_deleted: int
    total_size_bytes: int
    total_freed_bytes: int
    duration_seconds: float
    dry_run: bool
    errors: List[str]
    
    @property
    def total_size_mb(self) -> float:
        """Total size in MB"""
        return self.total_size_bytes / (1024 * 1024)
    
    @property
    def total_freed_mb(self) -> float:
        """Total freed in MB"""
        return self.total_freed_bytes / (1024 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "items_found": self.items_found,
            "items_deleted": self.items_deleted,
            "total_size_mb": round(self.total_size_mb, 2),
            "total_freed_mb": round(self.total_freed_mb, 2),
            "duration_seconds": round(self.duration_seconds, 2),
            "dry_run": self.dry_run,
            "errors": self.errors
        }


class VacuumOrchestrator:
    """
    Enhanced Vacuum Orchestrator v2.0
    
    Features:
    - Generic pattern-based cleanup
    - Dry-run mode with preview
    - Rollback capability
    - Multi-repo support
    - Category-based organization
    """
    
    # Default cleanup patterns
    DEFAULT_PATTERNS = [
        # Python cache
        CleanupPattern(CleanupCategory.PYTHON_CACHE, "**/__pycache__", "Python bytecode cache"),
        CleanupPattern(CleanupCategory.PYTHON_CACHE, "**/*.pyc", "Python compiled files"),
        CleanupPattern(CleanupCategory.PYTHON_CACHE, "**/*.pyo", "Python optimized files"),
        CleanupPattern(CleanupCategory.PYTHON_CACHE, "**/*.pyd", "Python dynamic modules"),
        
        # Test cache
        CleanupPattern(CleanupCategory.TEST_CACHE, "**/.pytest_cache", "Pytest cache"),
        CleanupPattern(CleanupCategory.TEST_CACHE, "**/.coverage", "Coverage data"),
        CleanupPattern(CleanupCategory.TEST_CACHE, "**/htmlcov", "Coverage HTML reports"),
        CleanupPattern(CleanupCategory.TEST_CACHE, "**/.tox", "Tox environments"),
        
        # Build artifacts
        CleanupPattern(CleanupCategory.BUILD_ARTIFACTS, "**/dist", "Distribution files"),
        CleanupPattern(CleanupCategory.BUILD_ARTIFACTS, "**/build", "Build files"),
        CleanupPattern(CleanupCategory.BUILD_ARTIFACTS, "**/*.egg-info", "Egg info"),
        CleanupPattern(CleanupCategory.BUILD_ARTIFACTS, "**/.eggs", "Egg files"),
        
        # Node modules
        CleanupPattern(CleanupCategory.NODE_MODULES, "**/node_modules", "Node.js modules"),
        
        # Log files
        CleanupPattern(CleanupCategory.LOG_FILES, "**/*.log", "Log files"),
        
        # System files
        CleanupPattern(CleanupCategory.SYSTEM_FILES, "**/.DS_Store", "macOS metadata"),
        CleanupPattern(CleanupCategory.SYSTEM_FILES, "**/Thumbs.db", "Windows thumbnails"),
        CleanupPattern(CleanupCategory.SYSTEM_FILES, "**/._.DS_Store", "macOS resource forks"),
        
        # Temp files
        CleanupPattern(CleanupCategory.TEMP_FILES, "**/*.tmp", "Temporary files"),
        CleanupPattern(CleanupCategory.TEMP_FILES, "**/*.temp", "Temporary files"),
        CleanupPattern(CleanupCategory.TEMP_FILES, "**/tmp/**", "Temp directories"),
    ]
    
    def __init__(
        self,
        workspace_root: Path,
        patterns: Optional[List[CleanupPattern]] = None,
        exclude_patterns: Optional[List[str]] = None
    ):
        """
        Initialize Vacuum Orchestrator
        
        Args:
            workspace_root: Root directory to clean
            patterns: Custom cleanup patterns (uses defaults if None)
            exclude_patterns: Patterns to exclude from cleanup
        """
        self.workspace_root = Path(workspace_root)
        self.patterns = patterns or self.DEFAULT_PATTERNS
        self.exclude_patterns = exclude_patterns or []
        self.cleanup_items: List[CleanupItem] = []
        self.backup_dir: Optional[Path] = None
        
    def scan(self) -> List[CleanupItem]:
        """
        Scan for items matching cleanup patterns
        
        Returns:
            List of items to be cleaned
        """
        self.cleanup_items = []
        
        for pattern in self.patterns:
            matches = self.workspace_root.glob(pattern.pattern)
            
            for path in matches:
                # Skip if excluded
                if self._is_excluded(path):
                    continue
                
                # Skip if doesn't exist
                if not path.exists():
                    continue
                
                # Get size
                size_bytes = self._get_size(path)
                
                # Check size threshold
                if pattern.size_threshold_mb:
                    size_mb = size_bytes / (1024 * 1024)
                    if size_mb < pattern.size_threshold_mb:
                        continue
                
                # Create cleanup item
                item = CleanupItem(
                    path=path,
                    category=pattern.category,
                    size_bytes=size_bytes,
                    is_directory=path.is_dir(),
                    pattern_matched=pattern.pattern
                )
                
                self.cleanup_items.append(item)
        
        return self.cleanup_items
    
    def preview(self) -> Dict[str, Any]:
        """
        Generate preview of cleanup operation
        
        Returns:
            Preview report with statistics
        """
        if not self.cleanup_items:
            self.scan()
        
        # Group by category
        by_category: Dict[CleanupCategory, List[CleanupItem]] = {}
        for item in self.cleanup_items:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append(item)
        
        # Calculate statistics
        total_size = sum(item.size_bytes for item in self.cleanup_items)
        
        category_stats = {}
        for category, items in by_category.items():
            cat_size = sum(item.size_bytes for item in items)
            category_stats[category.value] = {
                "count": len(items),
                "size_bytes": cat_size,
                "size_mb": round(cat_size / (1024 * 1024), 2),
                "items": [item.to_dict() for item in items[:5]]  # First 5 items
            }
        
        return {
            "workspace": str(self.workspace_root),
            "timestamp": datetime.now().isoformat(),
            "total_items": len(self.cleanup_items),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_category": category_stats
        }
    
    def cleanup(self, dry_run: bool = False, create_backup: bool = False) -> CleanupResult:
        """
        Execute cleanup operation
        
        Args:
            dry_run: If True, only simulate (don't delete)
            create_backup: If True, backup items before deletion
        
        Returns:
            CleanupResult with operation details
        """
        start_time = time.time()
        errors = []
        deleted_count = 0
        freed_bytes = 0
        
        # Scan if not already done
        if not self.cleanup_items:
            self.scan()
        
        # Create backup if requested
        if create_backup and not dry_run:
            self.backup_dir = self._create_backup_dir()
        
        # Process each item
        for item in self.cleanup_items:
            try:
                if not dry_run:
                    # Backup if requested
                    if create_backup:
                        self._backup_item(item)
                    
                    # Delete
                    if item.is_directory:
                        shutil.rmtree(item.path)
                    else:
                        item.path.unlink()
                    
                    deleted_count += 1
                    freed_bytes += item.size_bytes
            except Exception as e:
                errors.append(f"{item.path}: {str(e)}")
        
        duration = time.time() - start_time
        
        return CleanupResult(
            items_found=len(self.cleanup_items),
            items_deleted=deleted_count,
            total_size_bytes=sum(item.size_bytes for item in self.cleanup_items),
            total_freed_bytes=freed_bytes,
            duration_seconds=duration,
            dry_run=dry_run,
            errors=errors
        )
    
    def rollback(self) -> bool:
        """
        Rollback last cleanup operation from backup
        
        Returns:
            True if successful, False otherwise
        """
        if not self.backup_dir or not self.backup_dir.exists():
            return False
        
        try:
            # Restore from backup
            for backup_item in self.backup_dir.rglob("*"):
                if backup_item.is_file():
                    # Calculate original path
                    rel_path = backup_item.relative_to(self.backup_dir)
                    original_path = self.workspace_root / rel_path
                    
                    # Create parent directories
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy back
                    shutil.copy2(backup_item, original_path)
            
            return True
        except Exception:
            return False
    
    def _is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded"""
        import fnmatch
        path_str = str(path)
        
        for exclude_pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path_str, exclude_pattern):
                return True
        
        return False
    
    def _get_size(self, path: Path) -> int:
        """Get size of file or directory"""
        if path.is_file():
            return path.stat().st_size
        
        # Directory - sum all files
        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except (PermissionError, OSError):
            pass
        
        return total
    
    def _create_backup_dir(self) -> Path:
        """Create backup directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.workspace_root / ".vacuum_backup" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def _backup_item(self, item: CleanupItem) -> None:
        """Backup an item before deletion"""
        if not self.backup_dir:
            return
        
        try:
            rel_path = item.path.relative_to(self.workspace_root)
            backup_path = self.backup_dir / rel_path
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            if item.is_directory:
                shutil.copytree(item.path, backup_path)
            else:
                shutil.copy2(item.path, backup_path)
        except Exception:
            pass  # Backup failure shouldn't stop cleanup


class MultiRepoVacuum:
    """
    Multi-repository vacuum support
    Cleans multiple repositories with unified reporting
    """
    
    def __init__(self, repo_roots: List[Path]):
        """
        Initialize multi-repo vacuum
        
        Args:
            repo_roots: List of repository root paths
        """
        self.repo_roots = [Path(root) for root in repo_roots]
        self.vacuums: Dict[Path, VacuumOrchestrator] = {}
        
        for root in self.repo_roots:
            self.vacuums[root] = VacuumOrchestrator(root)
    
    def scan_all(self) -> Dict[Path, List[CleanupItem]]:
        """Scan all repositories"""
        results = {}
        for root, vacuum in self.vacuums.items():
            results[root] = vacuum.scan()
        return results
    
    def preview_all(self) -> Dict[str, Any]:
        """Generate unified preview"""
        previews = {}
        total_items = 0
        total_size = 0
        
        for root, vacuum in self.vacuums.items():
            preview = vacuum.preview()
            previews[str(root)] = preview
            total_items += preview["total_items"]
            total_size += preview["total_size_bytes"]
        
        return {
            "total_repos": len(self.repo_roots),
            "total_items": total_items,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "repositories": previews
        }
    
    def cleanup_all(self, dry_run: bool = False) -> Dict[Path, CleanupResult]:
        """Clean all repositories"""
        results = {}
        for root, vacuum in self.vacuums.items():
            results[root] = vacuum.cleanup(dry_run=dry_run)
        return results


def generate_cleanup_report(result: CleanupResult, output_path: Optional[Path] = None) -> str:
    """
    Generate human-readable cleanup report
    
    Args:
        result: Cleanup result
        output_path: Optional path to save report
    
    Returns:
        Report text
    """
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║            VACUUM CLEANUP REPORT                             ║
╚══════════════════════════════════════════════════════════════╝

Mode: {"DRY-RUN (Simulation)" if result.dry_run else "EXECUTE (Real Cleanup)"}
Duration: {result.duration_seconds:.2f} seconds

Items Found: {result.items_found}
Items Deleted: {result.items_deleted}

Total Size: {result.total_size_mb:.2f} MB
Space Freed: {result.total_freed_mb:.2f} MB

Status: {"✅ SUCCESS" if not result.errors else "⚠️  COMPLETED WITH ERRORS"}
"""
    
    if result.errors:
        report += f"\nErrors ({len(result.errors)}):\n"
        for error in result.errors[:10]:  # First 10 errors
            report += f"  - {error}\n"
        if len(result.errors) > 10:
            report += f"  ... and {len(result.errors) - 10} more\n"
    
    if output_path:
        output_path.write_text(report)
    
    return report
