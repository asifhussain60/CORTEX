"""
FileSystem Activity Monitor for CORTEX

Monitors filesystem for recent file changes to detect active development areas.
Works independently of editor (VS Code, Cursor, IntelliJ, Vim, etc.).

Features:
- Tracks file modification times (mtime)
- Detects editor lock files (.swp, ~, .tmp)
- Identifies recently accessed files
- Maps activity to application boundaries
- NO VS Code extension dependency

Performance Target: <500ms for 1000 files

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import time

logger = logging.getLogger(__name__)


@dataclass
class FileActivity:
    """Information about file activity"""
    path: str
    modified_time: datetime
    size_bytes: int
    is_locked: bool
    application_name: Optional[str] = None


@dataclass
class ApplicationActivity:
    """Aggregated activity for an application"""
    name: str
    path: str
    recent_changes: List[FileActivity] = field(default_factory=list)
    locked_files: List[str] = field(default_factory=list)
    total_modifications: int = 0
    last_activity: Optional[datetime] = None
    activity_score: float = 0.0


class FileSystemActivityMonitor:
    """
    Monitors filesystem for development activity without editor API dependency.
    
    Detection Methods:
    1. File modification times (mtime) - primary signal
    2. Editor lock files (.swp, ~, .tmp) - indicates active editing
    3. Recent file access patterns
    
    Scoring:
    - Files modified <15 min: 40 points
    - Files modified <1 hour: 30 points
    - Files modified <6 hours: 20 points
    - Files modified <24 hours: 10 points
    - Editor lock files present: +10 points
    """
    
    # Editor lock file patterns
    LOCK_FILE_PATTERNS = [
        '.swp',      # Vim swap files
        '.swo',      # Vim swap files
        '~',         # Backup files (Emacs, etc.)
        '.tmp',      # Temporary files
        '#',         # Emacs autosave
        '.lock',     # Generic lock files
    ]
    
    # File extensions to monitor (development files)
    MONITORED_EXTENSIONS = {
        # ColdFusion
        '.cfm', '.cfc', '.cfml',
        # Java
        '.java', '.jsp', '.xml',
        # JavaScript/TypeScript
        '.js', '.jsx', '.ts', '.tsx', '.vue',
        # Python
        '.py', '.pyi',
        # C#
        '.cs', '.cshtml', '.razor',
        # Web
        '.html', '.css', '.scss', '.sass', '.less',
        # Config
        '.json', '.yaml', '.yml', '.toml', '.ini',
        # SQL
        '.sql',
        # Markdown
        '.md',
    }
    
    # Directories to skip
    SKIP_DIRECTORIES = {
        'node_modules',
        '.git',
        '.svn',
        '__pycache__',
        'bin',
        'obj',
        'dist',
        'build',
        'target',
        '.pytest_cache',
        '.venv',
        'venv',
        'vendor',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize filesystem activity monitor.
        
        Args:
            config: Configuration dictionary with:
                - workspace_path: Path to workspace root
                - applications: List of discovered applications (from WorkspaceTopology)
                - time_window_hours: How far back to look (default: 24)
                - max_files_to_scan: Performance limit (default: 10000)
        """
        self.workspace_path = Path(config['workspace_path'])
        self.applications = config.get('applications', [])
        self.time_window_hours = config.get('time_window_hours', 24)
        self.max_files_to_scan = config.get('max_files_to_scan', 10000)
        
        # Activity tracking
        self.cutoff_time = datetime.now() - timedelta(hours=self.time_window_hours)
        self.files_scanned = 0
        self.files_with_activity = []
        
        logger.info(f"Initialized FileSystem Activity Monitor: {self.workspace_path}")
        logger.info(f"Time window: {self.time_window_hours} hours, Max files: {self.max_files_to_scan}")
    
    def scan_workspace_activity(self) -> Dict[str, ApplicationActivity]:
        """
        Scan workspace for recent file activity.
        
        Returns:
            Dictionary mapping application name to ApplicationActivity
        """
        start_time = time.time()
        
        logger.info("Starting workspace activity scan...")
        
        # Scan for recent file changes
        recent_files = self._scan_recent_files()
        
        # Detect lock files
        lock_files = self._detect_lock_files()
        
        # Map files to applications
        app_activity = self._map_to_applications(recent_files, lock_files)
        
        # Calculate activity scores
        self._calculate_activity_scores(app_activity)
        
        elapsed = time.time() - start_time
        logger.info(f"Activity scan complete: {len(recent_files)} active files in {elapsed:.2f}s")
        
        return app_activity
    
    def _scan_recent_files(self) -> List[FileActivity]:
        """
        Scan workspace for recently modified files.
        
        Returns:
            List of FileActivity for files modified within time window
        """
        recent_files = []
        self.files_scanned = 0
        
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip directories we don't care about
                dirs[:] = [d for d in dirs if d not in self.SKIP_DIRECTORIES]
                
                # Performance limit
                if self.files_scanned >= self.max_files_to_scan:
                    logger.warning(f"Hit scan limit: {self.max_files_to_scan} files")
                    break
                
                for filename in files:
                    # Only monitor development files
                    if not any(filename.endswith(ext) for ext in self.MONITORED_EXTENSIONS):
                        continue
                    
                    file_path = Path(root) / filename
                    self.files_scanned += 1
                    
                    try:
                        stat = file_path.stat()
                        mtime = datetime.fromtimestamp(stat.st_mtime)
                        
                        # Check if modified within time window
                        if mtime >= self.cutoff_time:
                            recent_files.append(FileActivity(
                                path=str(file_path),
                                modified_time=mtime,
                                size_bytes=stat.st_size,
                                is_locked=False
                            ))
                    
                    except Exception as e:
                        logger.debug(f"Error reading file {file_path}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error scanning workspace: {e}")
        
        logger.info(f"Scanned {self.files_scanned} files, found {len(recent_files)} with recent activity")
        return recent_files
    
    def _detect_lock_files(self) -> Set[str]:
        """
        Detect editor lock files indicating active editing.
        
        Returns:
            Set of file paths that have associated lock files
        """
        lock_files = set()
        
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                dirs[:] = [d for d in dirs if d not in self.SKIP_DIRECTORIES]
                
                for filename in files:
                    # Check if this is a lock file
                    is_lock_file = any(
                        filename.endswith(pattern) or filename.startswith(pattern)
                        for pattern in self.LOCK_FILE_PATTERNS
                    )
                    
                    if is_lock_file:
                        # Map lock file to original file
                        # e.g., .file.txt.swp -> file.txt
                        original_name = filename
                        for pattern in self.LOCK_FILE_PATTERNS:
                            original_name = original_name.replace(pattern, '')
                        original_name = original_name.lstrip('.')
                        
                        original_path = Path(root) / original_name
                        if original_path.exists():
                            lock_files.add(str(original_path))
                            logger.debug(f"Detected lock file for: {original_path}")
        
        except Exception as e:
            logger.error(f"Error detecting lock files: {e}")
        
        logger.info(f"Detected {len(lock_files)} files with editor locks")
        return lock_files
    
    def _map_to_applications(
        self,
        recent_files: List[FileActivity],
        lock_files: Set[str]
    ) -> Dict[str, ApplicationActivity]:
        """
        Map file activity to application boundaries.
        
        Args:
            recent_files: List of recently modified files
            lock_files: Set of file paths with lock files
            
        Returns:
            Dictionary mapping application name to activity
        """
        app_activity = {}
        
        # Initialize application activity tracking
        for app in self.applications:
            app_name = app['name']
            app_activity[app_name] = ApplicationActivity(
                name=app_name,
                path=app['path']
            )
        
        # Map files to applications
        for file_activity in recent_files:
            file_path = Path(file_activity.path)
            
            # Find which application this file belongs to
            app_name = self._find_application_for_file(file_path)
            
            if app_name and app_name in app_activity:
                # Mark if file is locked
                file_activity.is_locked = file_activity.path in lock_files
                file_activity.application_name = app_name
                
                # Add to application activity
                app_activity[app_name].recent_changes.append(file_activity)
                app_activity[app_name].total_modifications += 1
                
                if file_activity.is_locked:
                    app_activity[app_name].locked_files.append(file_activity.path)
                
                # Update last activity time
                if (not app_activity[app_name].last_activity or 
                    file_activity.modified_time > app_activity[app_name].last_activity):
                    app_activity[app_name].last_activity = file_activity.modified_time
        
        return app_activity
    
    def _find_application_for_file(self, file_path: Path) -> Optional[str]:
        """
        Determine which application a file belongs to.
        
        Args:
            file_path: Path to file
            
        Returns:
            Application name or None
        """
        file_str = str(file_path)
        
        for app in self.applications:
            app_path = app['path']
            if file_str.startswith(app_path):
                return app['name']
        
        return None
    
    def _calculate_activity_scores(self, app_activity: Dict[str, ApplicationActivity]) -> None:
        """
        Calculate activity scores for each application.
        
        Scoring:
        - Files modified <15 min: 40 points
        - Files modified <1 hour: 30 points
        - Files modified <6 hours: 20 points
        - Files modified <24 hours: 10 points
        - Editor lock files present: +10 points per file
        
        Args:
            app_activity: Dictionary of application activity (modified in place)
        """
        now = datetime.now()
        
        for app_name, activity in app_activity.items():
            score = 0.0
            
            for file_activity in activity.recent_changes:
                age_minutes = (now - file_activity.modified_time).total_seconds() / 60
                
                if age_minutes < 15:
                    score += 40
                elif age_minutes < 60:
                    score += 30
                elif age_minutes < 360:  # 6 hours
                    score += 20
                else:
                    score += 10
                
                # Bonus for locked files (actively being edited)
                if file_activity.is_locked:
                    score += 10
            
            activity.activity_score = score
            
            if score > 0:
                logger.info(f"Application '{app_name}' activity score: {score:.1f} "
                          f"({activity.total_modifications} files, "
                          f"{len(activity.locked_files)} locked)")
    
    def get_top_active_applications(self, count: int = 3) -> List[ApplicationActivity]:
        """
        Get top N most active applications.
        
        Args:
            count: Number of applications to return
            
        Returns:
            List of ApplicationActivity sorted by score (descending)
        """
        app_activity = self.scan_workspace_activity()
        
        # Filter and sort by activity score
        active_apps = [
            activity for activity in app_activity.values()
            if activity.activity_score > 0
        ]
        
        active_apps.sort(key=lambda x: x.activity_score, reverse=True)
        
        return active_apps[:count]
    
    def to_dict(self, app_activity: ApplicationActivity) -> Dict[str, Any]:
        """Convert ApplicationActivity to dictionary"""
        return {
            'name': app_activity.name,
            'path': app_activity.path,
            'total_modifications': app_activity.total_modifications,
            'locked_files_count': len(app_activity.locked_files),
            'activity_score': app_activity.activity_score,
            'last_activity': app_activity.last_activity.isoformat() if app_activity.last_activity else None,
            'recent_changes': [
                {
                    'path': f.path,
                    'modified_time': f.modified_time.isoformat(),
                    'is_locked': f.is_locked
                }
                for f in app_activity.recent_changes[:10]  # Limit to 10 most recent
            ]
        }
