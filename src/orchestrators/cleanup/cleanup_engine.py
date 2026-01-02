"""
Cleanup Engine - Shared scanning and deletion logic.

Reuses and refactors logic from src/plugins/cleanup_orchestrator.py
for use by category cleaners.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


logger = logging.getLogger(__name__)


class CleanupAction(Enum):
    """Types of cleanup actions."""
    DELETE_ALL = "delete_all"
    RETAIN_RECENT = "retain_recent"
    RETAIN_DAYS = "retain_days"
    ARCHIVE = "archive"
    REPORT = "report"


class RiskLevel(Enum):
    """Risk levels for cleanup operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CleanupItem:
    """Represents a file or directory to be cleaned."""
    path: Path
    category: str
    action: CleanupAction
    size_bytes: int
    reason: str
    risk_level: RiskLevel
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CleanupStats:
    """Statistics from cleanup execution."""
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


class CleanupEngine:
    """
    Shared scanning and deletion logic for cleanup operations.
    
    Refactored from DynamicCleanupOrchestrator for modular use.
    """
    
    def __init__(self, workspace_root: Path, rules_path: Path):
        """
        Initialize cleanup engine.
        
        Args:
            workspace_root: Root directory of workspace
            rules_path: Path to cleanup-rules.yaml
        """
        self.workspace_root = workspace_root.resolve()
        self.rules_path = rules_path
        
        # Load rules
        self.rules = self._load_rules()
        
        # Protected items
        self.protected_dirs: Set[Path] = set()
        self.protected_patterns: Set[str] = set()
        self._load_protected_items()
        
        # Statistics
        self.stats = CleanupStats()
        self.cleanup_items: List[CleanupItem] = []
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load cleanup rules from YAML file."""
        if not self.rules_path.exists():
            logger.warning(f"Rules file not found: {self.rules_path}")
            return {'version': '1.0', 'categories': {}}
        
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            logger.info(f"Loaded cleanup rules from {self.rules_path}")
            return rules
        except Exception as e:
            logger.error(f"Failed to load rules file: {e}")
            return {'version': '1.0', 'categories': {}}
    
    def _load_protected_items(self) -> None:
        """Load protected directories and patterns."""
        # Protected directories
        for dir_path in self.rules.get("protected_directories", []):
            full_path = (self.workspace_root / dir_path).resolve()
            self.protected_dirs.add(full_path)
        
        # Protected patterns
        self.protected_patterns = set(self.rules.get("protected_patterns", []))
        
        logger.info(f"Loaded {len(self.protected_dirs)} protected directories")
    
    def _is_protected(self, path: Path) -> bool:
        """Check if path is protected from deletion."""
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
    
    def scan_category(
        self,
        category_name: str,
        category_config: Optional[Dict[str, Any]] = None
    ) -> List[CleanupItem]:
        """
        Scan workspace for items in specified category.
        
        Args:
            category_name: Category name from cleanup-rules.yaml
            category_config: Optional category config override
        
        Returns:
            List of CleanupItem objects found
        """
        # Get category config
        if category_config is None:
            category_config = self.rules.get('categories', {}).get(category_name, {})
        
        if not category_config:
            logger.warning(f"Category '{category_name}' not found in rules")
            return []
        
        if not category_config.get('enabled', True):
            logger.info(f"Category '{category_name}' is disabled")
            return []
        
        logger.info(f"Scanning category: {category_name}")
        
        items = []
        action = CleanupAction(category_config['action'])
        risk_level = RiskLevel(category_config.get('risk_level', 'medium'))
        reason = category_config.get('reason', 'No reason specified')
        
        # Scan all paths for this category
        for path_pattern in category_config.get('paths', []):
            found_paths = self._scan_pattern(path_pattern, category_config)
            
            for found_path in found_paths:
                try:
                    size = self._calculate_size(found_path)
                    
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
    
    def _scan_pattern(
        self,
        path_pattern: str,
        category_config: Dict[str, Any]
    ) -> List[Path]:
        """
        Scan for files matching pattern.
        
        Args:
            path_pattern: Glob pattern or path
            category_config: Category configuration
        
        Returns:
            List of matching paths
        """
        results = []
        
        # Handle absolute vs relative paths
        if path_pattern.startswith('/'):
            base_path = Path(path_pattern)
        else:
            base_path = self.workspace_root / path_pattern
        
        # Handle glob patterns
        if '*' in str(path_pattern):
            parent = self.workspace_root
            pattern = path_pattern
            
            try:
                if '**' in pattern:
                    # Recursive glob
                    for item in parent.rglob(pattern.replace('**/', '')):
                        if not self._is_protected(item):
                            results.append(item)
                            self.stats.files_scanned += 1
                else:
                    # Non-recursive glob
                    for item in parent.glob(pattern):
                        if not self._is_protected(item):
                            results.append(item)
                            self.stats.files_scanned += 1
            except Exception as e:
                self.stats.errors.append(f"Error scanning pattern '{pattern}': {e}")
        else:
            # Direct path
            if base_path.exists() and not self._is_protected(base_path):
                results.append(base_path)
                self.stats.files_scanned += 1
        
        # Apply exclusions
        exclude_patterns = category_config.get('exclude_patterns', [])
        if exclude_patterns:
            results = [
                p for p in results
                if not any(p.match(excl) for excl in exclude_patterns)
            ]
        
        return results
    
    def _calculate_size(self, path: Path) -> int:
        """Calculate size of file or directory."""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return 0
    
    def apply_retention_policy(
        self,
        items: List[CleanupItem],
        category_config: Dict[str, Any]
    ) -> List[CleanupItem]:
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
            return items
        
        elif action == CleanupAction.RETAIN_RECENT:
            retention = category_config.get('retention', {})
            keep_count = retention.get('keep_count', 5)
            
            # Sort by modification time (most recent first)
            sorted_items = sorted(
                items,
                key=lambda x: x.metadata.get('mtime', 0),
                reverse=True
            )
            
            # Keep N most recent, delete rest
            to_delete = sorted_items[keep_count:]
            logger.info(f"Retention: keeping {keep_count}, deleting {len(to_delete)}")
            return to_delete
        
        elif action == CleanupAction.RETAIN_DAYS:
            retention = category_config.get('retention', {})
            keep_days = retention.get('keep_days', 7)
            cutoff_time = datetime.now() - timedelta(days=keep_days)
            
            to_delete = [
                item for item in items
                if datetime.fromtimestamp(item.metadata.get('mtime', 0)) < cutoff_time
            ]
            logger.info(f"Retention: keeping last {keep_days} days, deleting {len(to_delete)}")
            return to_delete
        
        elif action == CleanupAction.ARCHIVE:
            return items
        
        return []
    
    def process_categories(self, category_names: List[str]) -> Dict[str, Any]:
        """
        Scan and clean specified categories.
        
        Args:
            category_names: List of category names to process
        
        Returns:
            Cleanup result dictionary
        """
        # Reset stats
        self.stats = CleanupStats()
        self.cleanup_items = []
        
        categories_dict = self.rules.get('categories', {})
        
        # Scan categories
        for category_name in category_names:
            category_config = categories_dict.get(category_name)
            if not category_config:
                logger.warning(f"Category '{category_name}' not found")
                continue
            
            try:
                # Scan
                found_items = self.scan_category(category_name, category_config)
                
                # Apply retention
                items_to_process = self.apply_retention_policy(found_items, category_config)
                
                # Add to cleanup list
                self.cleanup_items.extend(items_to_process)
                self.stats.categories_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing category '{category_name}': {e}")
                self.stats.errors.append(f"Category '{category_name}' failed: {e}")
        
        # Execute cleanup
        self._execute_cleanup()
        
        # Generate result
        return self._generate_result()
    
    def _execute_cleanup(self) -> None:
        """Execute actual cleanup actions."""
        logger.info(f"Executing cleanup for {len(self.cleanup_items)} items")
        
        for item in self.cleanup_items:
            try:
                if item.action in (CleanupAction.DELETE_ALL, CleanupAction.RETAIN_RECENT, CleanupAction.RETAIN_DAYS):
                    self._delete_item(item)
                elif item.action == CleanupAction.ARCHIVE:
                    self._archive_item(item)
            except Exception as e:
                self.stats.errors.append(f"Failed to process {item.path}: {e}")
    
    def _delete_item(self, item: CleanupItem) -> None:
        """Delete a file or directory."""
        import shutil
        
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
        """Archive a file or directory."""
        import shutil
        
        # Get archive location from rules
        categories_dict = self.rules.get('categories', {})
        category_config = categories_dict.get(item.category, {})
        archive_to = category_config.get('archive_to', 'cortex-brain/archives')
        
        archive_dir = self.workspace_root / archive_to
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Move item to archive
        dest = archive_dir / item.path.name
        shutil.move(str(item.path), str(dest))
        
        self.stats.files_archived += 1
        logger.debug(f"Archived: {item.path} -> {dest}")
    
    def _generate_result(self) -> Dict[str, Any]:
        """Generate cleanup result dictionary."""
        # Group items by category
        categories_summary = defaultdict(lambda: {"count": 0, "size_bytes": 0})
        
        for item in self.cleanup_items:
            categories_summary[item.category]["count"] += 1
            categories_summary[item.category]["size_bytes"] += item.size_bytes
        
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'files_scanned': self.stats.files_scanned,
                'files_deleted': self.stats.files_deleted,
                'files_archived': self.stats.files_archived,
                'folders_deleted': self.stats.folders_deleted,
                'space_freed_bytes': self.stats.space_freed_bytes,
                'space_freed_mb': self.stats.space_freed_mb,
                'categories_processed': self.stats.categories_processed
            },
            'categories': {
                cat: {
                    "count": data["count"],
                    "size_mb": data["size_bytes"] / (1024 * 1024)
                }
                for cat, data in categories_summary.items()
            },
            'errors': self.stats.errors,
            'warnings': self.stats.warnings,
            'artifacts': []
        }
