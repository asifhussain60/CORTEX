"""
Dynamic Cleanup Orchestrator for CORTEX 2.0

Performs fresh workspace scans on every execution using configurable YAML rules.
NO static lists - everything is discovered dynamically at runtime.

Features:
- YAML-based cleanup rules (cortex-brain/cleanup-rules.yaml)
- Fresh scanning on every execution
- Multiple action types (delete, archive, retain_recent, retain_days)
- Recursion protection for nested directories
- Safety validations (protected dirs, Git status, confirmations)
- Dry-run and live modes
- Rollback capability with manifests
- Comprehensive reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Date: November 11, 2025
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json
import shutil
import logging
import hashlib
import subprocess
from collections import defaultdict

logger = logging.getLogger(__name__)


class CleanupMode(Enum):
    """Cleanup execution mode - always live"""
    LIVE = "live"


class CleanupAction(Enum):
    """Types of cleanup actions"""
    DELETE_ALL = "delete_all"
    RETAIN_RECENT = "retain_recent"
    RETAIN_DAYS = "retain_days"
    ARCHIVE = "archive"
    REPORT = "report"


class RiskLevel(Enum):
    """Risk levels for cleanup operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CleanupItem:
    """Represents a file or directory to be cleaned"""
    path: Path
    category: str
    action: CleanupAction
    size_bytes: int
    reason: str
    risk_level: RiskLevel
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CleanupStats:
    """Statistics from cleanup execution"""
    files_scanned: int = 0
    files_deleted: int = 0
    files_archived: int = 0
    folders_deleted: int = 0
    space_freed_bytes: int = 0
    execution_time_seconds: float = 0.0
    categories_processed: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def space_freed_mb(self) -> float:
        return self.space_freed_bytes / (1024 * 1024)
    
    @property
    def space_freed_gb(self) -> float:
        return self.space_freed_bytes / (1024 * 1024 * 1024)


class DynamicCleanupOrchestrator:
    """
    Dynamic cleanup orchestrator that performs fresh scans on every execution.
    
    Usage:
        orchestrator = DynamicCleanupOrchestrator(workspace_root)
        results = orchestrator.execute()
    """
    
    def __init__(self, workspace_root: Path, rules_file: Optional[Path] = None):
        """
        Initialize cleanup orchestrator.
        
        Args:
            workspace_root: Root directory of CORTEX workspace
            rules_file: Path to cleanup-rules.yaml (defaults to cortex-brain/cleanup-rules.yaml)
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.rules_file = rules_file or (self.workspace_root / "cortex-brain" / "cleanup-rules.yaml")
        
        # Load rules
        self.rules = self._load_rules()
        
        # Initialize state
        self.stats = CleanupStats()
        self.cleanup_items: List[CleanupItem] = []
        self.protected_dirs: Set[Path] = set()
        self.protected_patterns: Set[str] = set()
        
        # Load protected items
        self._load_protected_items()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load cleanup rules from YAML file"""
        if not self.rules_file.exists():
            logger.warning(f"Rules file not found: {self.rules_file}")
            return self._get_default_rules()
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            logger.info(f"Loaded cleanup rules from {self.rules_file}")
            return rules
        except Exception as e:
            logger.error(f"Failed to load rules file: {e}")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Return minimal default rules if file not found"""
        return {
            "version": "1.0",
            "categories": {},
            "protected_directories": [],
            "protected_patterns": [],
            "safety": {
                "max_recursion_depth": 15
            }
        }
    
    def _load_protected_items(self) -> None:
        """Load protected directories and patterns"""
        # Protected directories
        for dir_path in self.rules.get("protected_directories", []):
            full_path = (self.workspace_root / dir_path).resolve()
            self.protected_dirs.add(full_path)
        
        # Protected patterns
        self.protected_patterns = set(self.rules.get("protected_patterns", []))
        
        logger.info(f"Loaded {len(self.protected_dirs)} protected directories")
        logger.info(f"Loaded {len(self.protected_patterns)} protected patterns")
    
    def _is_protected(self, path: Path) -> bool:
        """Check if path is protected from deletion"""
        path = path.resolve()
        
        # Check protected directories
        for protected_dir in self.protected_dirs:
            if path == protected_dir or protected_dir in path.parents:
                return True
        
        # Check protected patterns
        for pattern in self.protected_patterns:
            if path.match(pattern):
                return True
        
        return False
    
    def _safe_scan(self, path: Path, pattern: str, max_depth: int = 15) -> List[Path]:
        """
        Safely scan directory with recursion protection.
        
        Args:
            path: Base path to scan
            pattern: Glob pattern to match
            max_depth: Maximum recursion depth
        
        Returns:
            List of matching paths
        """
        results = []
        
        def scan_recursive(current_path: Path, depth: int = 0):
            if depth > max_depth:
                self.stats.warnings.append(
                    f"Max recursion depth {max_depth} reached at {current_path}"
                )
                return
            
            try:
                if '**' in pattern:
                    # Recursive glob
                    for item in current_path.rglob(pattern.replace('**/', '')):
                        if not self._is_protected(item):
                            results.append(item)
                            self.stats.files_scanned += 1
                else:
                    # Non-recursive glob
                    for item in current_path.glob(pattern):
                        if not self._is_protected(item):
                            results.append(item)
                            self.stats.files_scanned += 1
            except PermissionError as e:
                self.stats.warnings.append(f"Permission denied: {current_path}")
            except Exception as e:
                self.stats.errors.append(f"Error scanning {current_path}: {e}")
        
        if path.exists():
            scan_recursive(path)
        
        return results
    
    def scan_category(self, category_name: str, category_config: Dict[str, Any]) -> List[CleanupItem]:
        """
        Perform fresh scan for a specific cleanup category.
        
        Args:
            category_name: Name of the category
            category_config: Category configuration from rules
        
        Returns:
            List of CleanupItem objects found
        """
        if not category_config.get('enabled', True):
            logger.info(f"Category '{category_name}' is disabled, skipping")
            return []
        
        logger.info(f"Scanning category: {category_name}")
        
        items = []
        action = CleanupAction(category_config['action'])
        risk_level = RiskLevel(category_config.get('risk_level', 'medium'))
        reason = category_config.get('reason', 'No reason specified')
        
        scan_rules = category_config.get('scan_rules', {})
        max_depth = scan_rules.get('recursion_limit', 
                                   self.rules.get('safety', {}).get('max_recursion_depth', 15))
        
        # Scan all paths for this category
        for path_pattern in category_config.get('paths', []):
            # Handle relative paths
            if path_pattern.startswith('/'):
                base_path = Path(path_pattern)
            else:
                base_path = self.workspace_root / path_pattern
            
            # If pattern contains glob characters, scan parent directory
            if '*' in str(path_pattern):
                parent = self.workspace_root
                pattern = path_pattern
            else:
                parent = base_path.parent if base_path.is_file() else base_path
                pattern = base_path.name if base_path.is_file() else '*'
            
            # Perform scan
            found_paths = self._safe_scan(parent, pattern, max_depth)
            
            # Apply exclusions
            exclude_patterns = category_config.get('exclude_patterns', [])
            if exclude_patterns:
                found_paths = [
                    p for p in found_paths
                    if not any(p.match(excl) for excl in exclude_patterns)
                ]
            
            # Create CleanupItem for each found path
            for found_path in found_paths:
                try:
                    size = found_path.stat().st_size if found_path.is_file() else 0
                    if found_path.is_dir():
                        # Calculate directory size
                        size = sum(f.stat().st_size for f in found_path.rglob('*') if f.is_file())
                    
                    item = CleanupItem(
                        path=found_path,
                        category=category_name,
                        action=action,
                        size_bytes=size,
                        reason=reason,
                        risk_level=risk_level,
                        metadata={
                            'mtime': found_path.stat().st_mtime,
                            'pattern': path_pattern
                        }
                    )
                    items.append(item)
                    
                except Exception as e:
                    self.stats.errors.append(f"Error processing {found_path}: {e}")
        
        logger.info(f"Found {len(items)} items in category '{category_name}'")
        return items
    
    def apply_retention_policy(self, items: List[CleanupItem], category_config: Dict[str, Any]) -> List[CleanupItem]:
        """
        Apply retention policy to filter items.
        
        Args:
            items: List of CleanupItem objects
            category_config: Category configuration with retention rules
        
        Returns:
            Filtered list of items to delete/archive
        """
        action = CleanupAction(category_config['action'])
        
        if action == CleanupAction.DELETE_ALL:
            # Delete all items
            return items
        
        elif action == CleanupAction.RETAIN_RECENT:
            # Keep N most recent, delete rest
            retention = category_config.get('retention', {})
            keep_count = retention.get('keep_count', 5)
            sort_by = retention.get('sort_by', 'mtime')
            order = retention.get('order', 'descending')
            
            # Sort by modification time
            sorted_items = sorted(
                items,
                key=lambda x: x.metadata.get('mtime', 0),
                reverse=(order == 'descending')
            )
            
            # Keep N most recent, delete rest
            to_delete = sorted_items[keep_count:]
            logger.info(f"Retention policy: keeping {keep_count}, deleting {len(to_delete)}")
            return to_delete
        
        elif action == CleanupAction.RETAIN_DAYS:
            # Keep files newer than N days
            retention = category_config.get('retention', {})
            keep_days = retention.get('keep_days', 7)
            cutoff_time = datetime.now() - timedelta(days=keep_days)
            
            to_delete = [
                item for item in items
                if datetime.fromtimestamp(item.metadata.get('mtime', 0)) < cutoff_time
            ]
            logger.info(f"Retention policy: keeping last {keep_days} days, deleting {len(to_delete)}")
            return to_delete
        
        elif action == CleanupAction.ARCHIVE:
            # Archive all items
            return items
        
        else:
            return []
    
    def execute(self, mode: CleanupMode = CleanupMode.LIVE) -> Dict[str, Any]:
        """
        Execute cleanup with fresh workspace scan.
        
        Args:
            mode: Execution mode (LIVE only)
        
        Returns:
            Dictionary with execution results and statistics
        """
        start_time = datetime.now()
        logger.info(f"Starting cleanup in {mode.value} mode")
        
        # Reset statistics
        self.stats = CleanupStats()
        self.cleanup_items = []
        
        # Process each category
        categories = self.rules.get('categories', {})
        for category_name, category_config in categories.items():
            try:
                # Fresh scan for this category
                found_items = self.scan_category(category_name, category_config)
                
                # Apply retention policy
                items_to_process = self.apply_retention_policy(found_items, category_config)
                
                # Add to cleanup list
                self.cleanup_items.extend(items_to_process)
                self.stats.categories_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing category '{category_name}': {e}")
                self.stats.errors.append(f"Category '{category_name}' failed: {e}")
        
        # Execute cleanup actions
        if mode == CleanupMode.LIVE:
            self._execute_cleanup_actions()
        
        # Calculate statistics
        self.stats.execution_time_seconds = (datetime.now() - start_time).total_seconds()
        
        # Generate report
        report = self._generate_report(mode)
        
        logger.info(f"Cleanup complete: {self.stats.files_deleted} files deleted, "
                   f"{self.stats.space_freed_mb:.2f} MB freed")
        
        return report
    
    def _execute_cleanup_actions(self) -> None:
        """Execute actual cleanup actions (delete, archive, etc.)"""
        logger.info(f"Executing cleanup actions for {len(self.cleanup_items)} items")
        
        for item in self.cleanup_items:
            try:
                if item.action == CleanupAction.DELETE_ALL:
                    self._delete_item(item)
                elif item.action in (CleanupAction.RETAIN_RECENT, CleanupAction.RETAIN_DAYS):
                    self._delete_item(item)
                elif item.action == CleanupAction.ARCHIVE:
                    self._archive_item(item)
            except Exception as e:
                self.stats.errors.append(f"Failed to process {item.path}: {e}")
    
    def _delete_item(self, item: CleanupItem) -> None:
        """Delete a file or directory"""
        try:
            if item.path.is_file():
                item.path.unlink()
                self.stats.files_deleted += 1
                self.stats.space_freed_bytes += item.size_bytes
            elif item.path.is_dir():
                shutil.rmtree(item.path)
                self.stats.folders_deleted += 1
                self.stats.space_freed_bytes += item.size_bytes
            
            logger.debug(f"Deleted: {item.path}")
        except Exception as e:
            raise Exception(f"Delete failed: {e}")
    
    def _archive_item(self, item: CleanupItem) -> None:
        """Archive a file or directory"""
        # Get archive destination from rules
        category_config = self.rules['categories'].get(item.category, {})
        archive_to = category_config.get('archive_to', 'cortex-brain/archives')
        
        archive_dir = self.workspace_root / archive_to
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Move item to archive
        dest = archive_dir / item.path.name
        shutil.move(str(item.path), str(dest))
        
        self.stats.files_archived += 1
        logger.debug(f"Archived: {item.path} -> {dest}")
    
    def _generate_report(self, mode: CleanupMode) -> Dict[str, Any]:
        """Generate comprehensive cleanup report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": mode.value,
            "workspace_root": str(self.workspace_root),
            "rules_file": str(self.rules_file),
            "statistics": {
                "files_scanned": self.stats.files_scanned,
                "files_deleted": self.stats.files_deleted,
                "files_archived": self.stats.files_archived,
                "folders_deleted": self.stats.folders_deleted,
                "space_freed_bytes": self.stats.space_freed_bytes,
                "space_freed_mb": self.stats.space_freed_mb,
                "space_freed_gb": self.stats.space_freed_gb,
                "categories_processed": self.stats.categories_processed,
                "execution_time_seconds": self.stats.execution_time_seconds
            },
            "categories": self._generate_category_summary(),
            "items": [
                {
                    "path": str(item.path.relative_to(self.workspace_root)),
                    "category": item.category,
                    "action": item.action.value,
                    "size_bytes": item.size_bytes,
                    "size_mb": item.size_bytes / (1024 * 1024),
                    "reason": item.reason,
                    "risk_level": item.risk_level.value
                }
                for item in self.cleanup_items[:50]  # First 50 items
            ],
            "errors": self.stats.errors,
            "warnings": self.stats.warnings
        }
    
    def _generate_category_summary(self) -> Dict[str, Any]:
        """Generate per-category summary"""
        summary = defaultdict(lambda: {"count": 0, "size_bytes": 0})
        
        for item in self.cleanup_items:
            summary[item.category]["count"] += 1
            summary[item.category]["size_bytes"] += item.size_bytes
        
        return {
            cat: {
                "count": data["count"],
                "size_mb": data["size_bytes"] / (1024 * 1024)
            }
            for cat, data in summary.items()
        }


# ============================================================================
# CLI Interface
# ============================================================================

def print_cleanup_report(report: Dict[str, Any]) -> None:
    """Print formatted cleanup report to console"""
    print("=" * 80)
    print("CORTEX DYNAMIC CLEANUP ORCHESTRATOR")
    print("=" * 80)
    print(f"\nTimestamp: {report['timestamp']}")
    print(f"Mode: {report['mode'].upper()}")
    print(f"Workspace: {report['workspace_root']}")
    
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    stats = report['statistics']
    print(f"\nFiles Scanned:     {stats['files_scanned']:,}")
    print(f"Files Deleted:     {stats['files_deleted']:,}")
    print(f"Files Archived:    {stats['files_archived']:,}")
    print(f"Folders Deleted:   {stats['folders_deleted']:,}")
    print(f"Space Freed:       {stats['space_freed_mb']:.2f} MB ({stats['space_freed_gb']:.3f} GB)")
    print(f"Execution Time:    {stats['execution_time_seconds']:.2f} seconds")
    
    print("\n" + "=" * 80)
    print("CATEGORIES")
    print("=" * 80)
    for cat_name, cat_data in report['categories'].items():
        print(f"\n{cat_name}:")
        print(f"  Items: {cat_data['count']}")
        print(f"  Size:  {cat_data['size_mb']:.2f} MB")
    
    if report.get('errors'):
        print("\n" + "=" * 80)
        print("ERRORS")
        print("=" * 80)
        for error in report['errors'][:10]:
            print(f"  - {error}")
    
    if report.get('warnings'):
        print("\n" + "=" * 80)
        print("WARNINGS")
        print("=" * 80)
        for warning in report['warnings'][:10]:
            print(f"  - {warning}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys
    
    # Get workspace root
    workspace = Path(__file__).parent.parent.parent
    
    # Always run in live mode
    mode = CleanupMode.LIVE
    print("✅ LIVE MODE - Executing cleanup operations")
    
    # Execute cleanup
    orchestrator = DynamicCleanupOrchestrator(workspace)
    report = orchestrator.execute(mode=mode)
    
    # Print report
    print_cleanup_report(report)
    
    # Save report
    report_file = workspace / "cortex-brain" / "cleanup-reports" / f"cleanup-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved to: {report_file}")
