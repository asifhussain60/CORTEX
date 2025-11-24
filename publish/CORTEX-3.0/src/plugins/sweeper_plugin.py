"""
Aggressive File Sweeper Plugin for CORTEX 2.0

Scans workspace for unnecessary files and moves them to OS Recycle Bin.
Fully reversible - files can be restored from Recycle Bin/Trash.

Safety through INTELLIGENCE + OS-native reversibility:
- Smart classification rules (age, size, location, patterns)
- Whitelist protection (respects cleanup-rules.yaml)
- Recycle Bin instead of permanent deletion (uses send2trash)
- Minimal audit trail (JSON log for tracking only)

Target Files:
- *.md (reference docs, session reports, backups)
- *.log (logs)
- *.bak, *.backup (manual backups)
- *.tmp, *.temp (temporary files)
- *.pyc, __pycache__ (Python cache)
- *-BACKUP-*, *-OLD-* (backup patterns)
- *-REFERENCE.md, *-IMPLEMENTATION.md, *-QUICK-REFERENCE.md (reference docs)
- Dated duplicates (file.2024-11-10.md)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
Date: November 12, 2025
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from send2trash import send2trash

from src.plugins.base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginCategory,
    PluginPriority,
    HookPoint
)

logger = logging.getLogger(__name__)


class FileCategory(Enum):
    """Classification categories for files"""
    ESSENTIAL = "essential"  # Core CORTEX files (KEEP)
    ACTIVE = "active"  # Currently used files (KEEP)
    REFERENCE = "reference"  # Reference docs, may delete if old
    BACKUP = "backup"  # Manual backups (DELETE)
    LOG = "log"  # Log files (DELETE if old)
    CACHE = "cache"  # Cache files (DELETE)
    TEMP = "temp"  # Temporary files (DELETE)
    SESSION = "session"  # Session reports (DELETE if old)
    DUPLICATE = "duplicate"  # Dated duplicates (DELETE)
    UNKNOWN = "unknown"  # Unclassified (KEEP for safety)


@dataclass
class FileClassification:
    """Classification result for a file"""
    path: Path
    category: FileCategory
    action: str  # "keep" or "delete"
    reason: str
    size_bytes: int
    age_days: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SweeperStats:
    """Statistics from sweeper execution"""
    files_scanned: int = 0
    files_deleted: int = 0
    files_kept: int = 0
    space_freed_bytes: int = 0
    execution_time_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    @property
    def space_freed_mb(self) -> float:
        return self.space_freed_bytes / (1024 * 1024)


class SweeperPlugin(BasePlugin):
    """
    Aggressive file sweeper - moves clutter to Recycle Bin (reversible).
    
    Usage:
        sweeper = SweeperPlugin()
        sweeper.initialize()
        results = sweeper.execute({"workspace_root": "/path/to/cortex"})
    """
    
    # File extensions to scan
    SCAN_EXTENSIONS = {
        '.md', '.log', '.bak', '.backup', '.tmp', '.temp',
        '.pyc', '.pyo', '.cache', '.old', '.orig'
    }
    
    # Backup file patterns
    BACKUP_PATTERNS = [
        '*-BACKUP-*', '*-backup-*', '*.backup.*',
        '*-OLD-*', '*-old-*', '*.old.*',
        '*.bak', '*.backup', '*.orig'
    ]
    
    # Session/report patterns
    SESSION_PATTERNS = [
        'SESSION-*.md', '*-SESSION.md',
        '*-REPORT-*.md', '*-REPORT.md', '*REPORT*.md',
        '*-PROGRESS.md', 'PHASE-*-PROGRESS.md',
        '*-CONTINUED-*.md'
    ]
    
    # Reference documentation patterns (NEW!)
    REFERENCE_DOC_PATTERNS = [
        '*-REFERENCE.md', '*-reference.md',
        '*-IMPLEMENTATION.md', '*-implementation.md',
        '*-QUICK-REFERENCE.md', '*-quick-reference.md',
        '*-GUIDE.md', '*-guide.md',
        '*-INSTRUCTIONS.md', '*-instructions.md',
        '*-MANUAL.md', '*-manual.md',
        '*-SUMMARY.md', '*-summary.md'
    ]
    
    # Dated duplicate patterns (file.2024-11-10.md)
    DATED_PATTERNS = [
        '*.202[0-9]-[0-1][0-9]-[0-3][0-9].*',
        '*.[0-9][0-9][0-9][0-9][0-1][0-9][0-3][0-9].*'
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize sweeper plugin"""
        super().__init__(config)
        
        self.workspace_root: Optional[Path] = None
        self.protected_dirs: Set[Path] = set()
        self.protected_patterns: Set[str] = set()
        self.stats = SweeperStats()
        self.audit_log: List[Dict[str, Any]] = []
    
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            plugin_id="sweeper",
            name="File Sweeper",
            version="1.0.0",
            category=PluginCategory.MAINTENANCE,
            priority=PluginPriority.MEDIUM,
            description="File sweeper - moves clutter to Recycle Bin (reversible)",
            author="Asif Hussain",
            dependencies=[],
            hooks=[HookPoint.ON_STARTUP.value],
            config_schema={}
        )
    
    def initialize(self) -> bool:
        """Initialize sweeper plugin"""
        try:
            logger.info("Initializing File Sweeper plugin...")
            
            # Load protected items from cleanup rules if available
            self._load_protected_items()
            
            logger.info("File Sweeper plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize sweeper: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute file sweeping.
        
        Args:
            context: Must contain 'workspace_root' key
        
        Returns:
            Dictionary with execution results
        """
        start_time = datetime.now()
        
        try:
            # Get workspace root
            workspace = context.get('workspace_root')
            if not workspace:
                return {
                    "success": False,
                    "error": "workspace_root not provided"
                }
            
            self.workspace_root = Path(workspace).resolve()
            
            logger.info("=" * 80)
            logger.info("CORTEX FILE SWEEPER")
            logger.info("=" * 80)
            logger.info(f"Workspace: {self.workspace_root}")
            logger.info(f"Mode: RECYCLE BIN (OS-native reversibility)")
            logger.info("=" * 80)
            
            # Reset stats
            self.stats = SweeperStats()
            self.audit_log = []
            
            # Scan and classify files
            classifications = self._scan_and_classify()
            
            # Delete classified files
            self._execute_deletions(classifications)
            
            # Save audit log
            self._save_audit_log()
            
            # Calculate execution time
            self.stats.execution_time_seconds = (
                datetime.now() - start_time
            ).total_seconds()
            
            # Print summary
            self._print_summary()
            
            return {
                "success": True,
                "stats": {
                    "files_scanned": self.stats.files_scanned,
                    "files_deleted": self.stats.files_deleted,
                    "files_kept": self.stats.files_kept,
                    "space_freed_mb": round(self.stats.space_freed_mb, 2),
                    "execution_time": round(self.stats.execution_time_seconds, 2)
                },
                "errors": self.stats.errors
            }
            
        except Exception as e:
            logger.error(f"Sweeper execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup(self) -> bool:
        """Cleanup sweeper resources"""
        return True
    
    def _load_protected_items(self) -> None:
        """Load protected directories and patterns from cleanup-rules.yaml"""
        try:
            rules_file = Path("cortex-brain/cleanup-rules.yaml")
            
            if not rules_file.exists():
                # Use defaults
                self._set_default_protections()
                return
            
            import yaml
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            # Load protected directories
            for dir_path in rules.get("protected_directories", []):
                self.protected_dirs.add(Path(dir_path))
            
            # Load protected patterns
            self.protected_patterns = set(rules.get("protected_patterns", []))
            
            logger.info(f"Loaded {len(self.protected_dirs)} protected directories")
            logger.info(f"Loaded {len(self.protected_patterns)} protected patterns")
            
        except Exception as e:
            logger.warning(f"Failed to load cleanup rules: {e}")
            self._set_default_protections()
    
    def _set_default_protections(self) -> None:
        """Set default protected items if rules file not available"""
        self.protected_dirs = {
            Path("src"),
            Path("tests"),
            Path(".git"),
            Path(".github"),
            Path(".venv"),
            Path("cortex-brain/tier1"),
            Path("cortex-brain/tier2"),
            Path("cortex-brain/tier3"),
            Path("cortex-brain/schemas")
        }
        
        self.protected_patterns = {
            "*.py",  # Source files
            "*.yaml", "*.yml",  # Config files
            "*.json",  # Data files
            "*.db", "*.sql",  # Databases
            "README.md", "LICENSE",
            "requirements.txt", "package.json",
            "*.config.*"
        }
    
    def _is_protected(self, path: Path) -> bool:
        """Check if path is protected from deletion"""
        path = path.resolve()
        
        # Check protected directories
        for protected_dir in self.protected_dirs:
            full_protected = (self.workspace_root / protected_dir).resolve()
            if path == full_protected or full_protected in path.parents:
                return True
        
        # Check protected patterns
        for pattern in self.protected_patterns:
            if path.match(pattern):
                return True
        
        return False
    
    def _scan_and_classify(self) -> List[FileClassification]:
        """Scan workspace and classify files"""
        classifications = []
        
        logger.info("Scanning workspace...")
        
        # Walk directory tree
        for root, dirs, files in os.walk(self.workspace_root):
            root_path = Path(root)
            
            # Skip protected directories
            if self._is_protected(root_path):
                dirs[:] = []  # Don't recurse into protected dirs
                continue
            
            # Classify each file
            for filename in files:
                file_path = root_path / filename
                
                self.stats.files_scanned += 1
                
                # Skip if protected
                if self._is_protected(file_path):
                    continue
                
                # Skip if not a target extension
                if file_path.suffix.lower() not in self.SCAN_EXTENSIONS:
                    # Check for extensionless patterns
                    if not any(file_path.match(p) for p in self.BACKUP_PATTERNS + self.SESSION_PATTERNS):
                        continue
                
                # Classify the file
                classification = self._classify_file(file_path)
                classifications.append(classification)
        
        logger.info(f"Scanned {self.stats.files_scanned} files")
        logger.info(f"Classified {len(classifications)} files for review")
        
        return classifications
    
    def _classify_file(self, path: Path) -> FileClassification:
        """Classify a single file"""
        try:
            stat = path.stat()
            size_bytes = stat.st_size
            age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
            
            # Determine category and action
            category, action, reason = self._determine_category(path, age_days)
            
            return FileClassification(
                path=path,
                category=category,
                action=action,
                reason=reason,
                size_bytes=size_bytes,
                age_days=age_days,
                metadata={
                    "extension": path.suffix,
                    "location": str(path.parent.relative_to(self.workspace_root))
                }
            )
            
        except Exception as e:
            logger.error(f"Error classifying {path}: {e}")
            return FileClassification(
                path=path,
                category=FileCategory.UNKNOWN,
                action="keep",
                reason=f"Error: {e}",
                size_bytes=0,
                age_days=0
            )
    
    def _determine_category(self, path: Path, age_days: int) -> tuple:
        """
        Determine file category and action.
        
        Returns:
            (category, action, reason)
        """
        filename = path.name.lower()
        
        # Check for backup patterns
        for pattern in self.BACKUP_PATTERNS:
            if path.match(pattern):
                return (
                    FileCategory.BACKUP,
                    "delete",
                    "Manual backup file (Git provides versioning)"
                )
        
        # Check for dated duplicates
        for pattern in self.DATED_PATTERNS:
            if path.match(pattern):
                return (
                    FileCategory.DUPLICATE,
                    "delete",
                    "Dated duplicate file"
                )
        
        # Check for session reports
        for pattern in self.SESSION_PATTERNS:
            if path.match(pattern):
                if age_days > 30:
                    return (
                        FileCategory.SESSION,
                        "delete",
                        f"Old session report ({age_days} days old)"
                    )
                else:
                    return (
                        FileCategory.SESSION,
                        "keep",
                        f"Recent session report ({age_days} days old)"
                    )
        
        # Check for reference documentation (NEW!)
        for pattern in self.REFERENCE_DOC_PATTERNS:
            if path.match(pattern):
                if age_days > 60:
                    return (
                        FileCategory.REFERENCE,
                        "delete",
                        f"Old reference doc ({age_days} days old)"
                    )
                else:
                    return (
                        FileCategory.REFERENCE,
                        "keep",
                        f"Recent reference doc ({age_days} days old)"
                    )
        
        # Check by extension
        ext = path.suffix.lower()
        
        if ext in ['.bak', '.backup', '.old', '.orig']:
            return (
                FileCategory.BACKUP,
                "delete",
                "Backup file extension"
            )
        
        if ext in ['.log']:
            if age_days > 30:
                return (
                    FileCategory.LOG,
                    "delete",
                    f"Old log file ({age_days} days old)"
                )
            else:
                return (
                    FileCategory.LOG,
                    "keep",
                    f"Recent log file ({age_days} days old)"
                )
        
        if ext in ['.tmp', '.temp']:
            return (
                FileCategory.TEMP,
                "delete",
                "Temporary file"
            )
        
        if ext in ['.pyc', '.pyo', '.cache']:
            return (
                FileCategory.CACHE,
                "delete",
                "Python cache file"
            )
        
        if ext == '.md':
            # Markdown files - check location and age
            if 'cortex-brain' in str(path):
                # Brain files - be conservative
                if age_days > 60 and 'REPORT' in filename.upper():
                    return (
                        FileCategory.REFERENCE,
                        "delete",
                        f"Old brain report ({age_days} days old)"
                    )
            
            # Keep by default
            return (
                FileCategory.REFERENCE,
                "keep",
                "Markdown file (keeping for safety)"
            )
        
        # Unknown - keep for safety
        return (
            FileCategory.UNKNOWN,
            "keep",
            "Unclassified file (keeping for safety)"
        )
    
    def _execute_deletions(self, classifications: List[FileClassification]) -> None:
        """Execute file deletions via Recycle Bin"""
        delete_list = [c for c in classifications if c.action == "delete"]
        
        if not delete_list:
            logger.info("No files to delete")
            return
        
        logger.info(f"Moving {len(delete_list)} files to Recycle Bin...")
        
        for classification in delete_list:
            try:
                # Move to Recycle Bin (OS-native, reversible)
                send2trash(str(classification.path))
                
                # Update stats
                self.stats.files_deleted += 1
                self.stats.space_freed_bytes += classification.size_bytes
                
                # Add to audit log
                self.audit_log.append({
                    "path": str(classification.path.relative_to(self.workspace_root)),
                    "category": classification.category.value,
                    "reason": classification.reason,
                    "size_bytes": classification.size_bytes,
                    "age_days": classification.age_days,
                    "moved_to_recycle_bin_at": datetime.now().isoformat(),
                    "recoverable": True
                })
                
                logger.debug(f"Moved to Recycle Bin: {classification.path}")
                
            except Exception as e:
                error_msg = f"Failed to move {classification.path} to Recycle Bin: {e}"
                logger.error(error_msg)
                self.stats.errors.append(error_msg)
        
        # Count kept files
        self.stats.files_kept = len(classifications) - self.stats.files_deleted
    
    def _save_audit_log(self) -> None:
        """Save minimal audit log for recovery"""
        if not self.audit_log:
            return
        
        try:
            log_dir = self.workspace_root / "cortex-brain" / "sweeper-logs"
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            log_file = log_dir / f"sweeper-{timestamp}.json"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "mode": "recycle_bin",
                    "recoverable": True,
                    "recovery_instructions": "Files can be restored from your OS Recycle Bin/Trash",
                    "stats": {
                        "files_deleted": self.stats.files_deleted,
                        "space_freed_mb": round(self.stats.space_freed_mb, 2)
                    },
                    "deleted_files": self.audit_log
                }, f, indent=2)
            
            logger.info(f"Audit log saved: {log_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save audit log: {e}")
    
    def _print_summary(self) -> None:
        """Print execution summary"""
        logger.info("=" * 80)
        logger.info("SWEEPER SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Files scanned:     {self.stats.files_scanned:,}")
        logger.info(f"Files moved:       {self.stats.files_deleted:,} (to Recycle Bin)")
        logger.info(f"Files kept:        {self.stats.files_kept:,}")
        logger.info(f"Space freed:       {self.stats.space_freed_mb:.2f} MB")
        logger.info(f"Execution time:    {self.stats.execution_time_seconds:.2f}s")
        logger.info("")
        logger.info(f"Recovery:          Files can be restored from Recycle Bin")
        
        if self.stats.errors:
            logger.info(f"Errors:            {len(self.stats.errors)}")
        
        logger.info("=" * 80)


def register() -> BasePlugin:
    """Register sweeper plugin"""
    return SweeperPlugin()
