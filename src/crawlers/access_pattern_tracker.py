"""
Access Pattern Tracker for CORTEX

Tracks filesystem access patterns to identify frequently accessed files and directories.
Uses file access time (atime) metadata to detect navigation patterns.

Features:
- Tracks file access times
- Detects cross-application navigation
- Builds access heat map
- Identifies workflow clusters
- NO external dependencies

Performance Target: <200ms

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


@dataclass
class AccessInfo:
    """Information about file access"""
    path: str
    access_time: datetime
    access_count: int = 1
    application_name: Optional[str] = None


@dataclass
class ApplicationAccessPattern:
    """Access patterns for an application"""
    name: str
    path: str
    accessed_files: List[AccessInfo] = field(default_factory=list)
    total_accesses: int = 0
    unique_files: int = 0
    access_frequency: float = 0.0  # accesses per hour
    activity_score: float = 0.0
    cross_app_links: List[str] = field(default_factory=list)  # Apps accessed together


class AccessPatternTracker:
    """
    Tracks filesystem access patterns to detect development activity.
    
    Detection Methods:
    1. File access times (atime) - primary signal
    2. Access frequency analysis
    3. Cross-application navigation patterns
    4. Workflow cluster detection
    
    Scoring:
    - Files accessed <1 hour: 20 points per access
    - Files accessed <6 hours: 15 points per access
    - Files accessed <24 hours: 10 points per access
    - High-frequency files (10+ accesses): +10 points
    - Cross-application navigation: +5 points per link
    
    Note: atime availability depends on filesystem mount options.
    If atime is disabled (noatime), this tracker provides minimal value.
    """
    
    # File extensions to track
    TRACKED_EXTENSIONS = {
        '.cfm', '.cfc', '.cfml',  # ColdFusion
        '.java', '.jsp', '.xml',  # Java
        '.js', '.jsx', '.ts', '.tsx', '.vue',  # JavaScript
        '.py', '.pyi',  # Python
        '.cs', '.cshtml', '.razor',  # C#
        '.html', '.css', '.scss',  # Web
        '.json', '.yaml', '.yml',  # Config
        '.sql', '.md',  # SQL, Markdown
    }
    
    # Directories to skip
    SKIP_DIRECTORIES = {
        'node_modules', '.git', '.svn', '__pycache__',
        'bin', 'obj', 'dist', 'build', 'target',
        '.pytest_cache', '.venv', 'venv', 'vendor',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize access pattern tracker.
        
        Args:
            config: Configuration dictionary with:
                - workspace_path: Path to workspace root
                - applications: List of discovered applications
                - lookback_hours: How far back to track (default: 24)
                - max_files: Performance limit (default: 5000)
        """
        self.workspace_path = Path(config['workspace_path'])
        self.applications = config.get('applications', [])
        self.lookback_hours = config.get('lookback_hours', 24)
        self.max_files = config.get('max_files', 5000)
        
        self.cutoff_time = datetime.now() - timedelta(hours=self.lookback_hours)
        self.files_checked = 0
        
        # Check if atime is available
        self.atime_available = self._check_atime_availability()
        
        logger.info(f"Initialized Access Pattern Tracker: {self.workspace_path}")
        logger.info(f"Lookback: {self.lookback_hours} hours, atime available: {self.atime_available}")
    
    def _check_atime_availability(self) -> bool:
        """
        Check if filesystem supports access time tracking.
        
        Returns:
            True if atime appears to be working, False otherwise
        """
        try:
            # Create a temporary file and check if atime changes
            test_file = self.workspace_path / '.cortex_atime_test'
            test_file.write_text('test')
            
            stat_before = test_file.stat()
            
            # Read file
            test_file.read_text()
            
            stat_after = test_file.stat()
            
            # Clean up
            test_file.unlink()
            
            # Check if atime changed
            atime_works = stat_after.st_atime != stat_before.st_atime
            
            if not atime_works:
                logger.warning("Filesystem access time (atime) appears disabled. "
                             "Access pattern tracking will have limited effectiveness.")
            
            return atime_works
        
        except Exception as e:
            logger.warning(f"Could not test atime availability: {e}")
            return False
    
    def track_access_patterns(self) -> Dict[str, ApplicationAccessPattern]:
        """
        Track file access patterns across workspace.
        
        Returns:
            Dictionary mapping application name to access patterns
        """
        logger.info("Starting access pattern analysis...")
        
        # Collect access information
        access_info = self._collect_access_info()
        
        # Detect cross-application patterns
        cross_app_links = self._detect_cross_app_navigation(access_info)
        
        # Map to applications
        app_patterns = self._map_to_applications(access_info, cross_app_links)
        
        # Calculate activity scores
        self._calculate_activity_scores(app_patterns)
        
        logger.info(f"Access pattern analysis complete: {len(access_info)} files tracked")
        
        return app_patterns
    
    def _collect_access_info(self) -> List[AccessInfo]:
        """
        Collect file access information from workspace.
        
        Returns:
            List of AccessInfo for recently accessed files
        """
        access_info = []
        access_counts = defaultdict(int)
        self.files_checked = 0
        
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip directories
                dirs[:] = [d for d in dirs if d not in self.SKIP_DIRECTORIES]
                
                # Performance limit
                if self.files_checked >= self.max_files:
                    logger.warning(f"Hit access tracking limit: {self.max_files} files")
                    break
                
                for filename in files:
                    # Only track development files
                    if not any(filename.endswith(ext) for ext in self.TRACKED_EXTENSIONS):
                        continue
                    
                    file_path = Path(root) / filename
                    self.files_checked += 1
                    
                    try:
                        stat = file_path.stat()
                        atime = datetime.fromtimestamp(stat.st_atime)
                        
                        # Check if accessed within lookback window
                        if atime >= self.cutoff_time:
                            file_str = str(file_path)
                            access_counts[file_str] += 1
                            
                            access_info.append(AccessInfo(
                                path=file_str,
                                access_time=atime,
                                access_count=access_counts[file_str]
                            ))
                    
                    except Exception as e:
                        logger.debug(f"Error reading file {file_path}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error collecting access info: {e}")
        
        logger.info(f"Checked {self.files_checked} files, found {len(access_info)} with recent access")
        
        return access_info
    
    def _detect_cross_app_navigation(self, access_info: List[AccessInfo]) -> Dict[str, Set[str]]:
        """
        Detect cross-application navigation patterns.
        
        Identifies applications that are accessed together within time windows,
        suggesting they are part of the same workflow.
        
        Args:
            access_info: List of file access information
            
        Returns:
            Dictionary mapping app name to set of linked app names
        """
        cross_app_links = defaultdict(set)
        
        # Group accesses by time windows (15-minute windows)
        window_size = timedelta(minutes=15)
        
        # Sort by access time
        sorted_accesses = sorted(access_info, key=lambda x: x.access_time)
        
        # Find apps accessed within same windows
        current_window_start = None
        current_window_apps = set()
        
        for access in sorted_accesses:
            if current_window_start is None:
                current_window_start = access.access_time
                app_name = self._find_application_for_file(Path(access.path))
                if app_name:
                    current_window_apps.add(app_name)
            else:
                # Check if still in current window
                if access.access_time - current_window_start <= window_size:
                    app_name = self._find_application_for_file(Path(access.path))
                    if app_name:
                        current_window_apps.add(app_name)
                else:
                    # Process completed window
                    if len(current_window_apps) > 1:
                        # Multiple apps accessed in same window - create links
                        for app1 in current_window_apps:
                            for app2 in current_window_apps:
                                if app1 != app2:
                                    cross_app_links[app1].add(app2)
                    
                    # Start new window
                    current_window_start = access.access_time
                    current_window_apps = set()
                    app_name = self._find_application_for_file(Path(access.path))
                    if app_name:
                        current_window_apps.add(app_name)
        
        # Process final window
        if len(current_window_apps) > 1:
            for app1 in current_window_apps:
                for app2 in current_window_apps:
                    if app1 != app2:
                        cross_app_links[app1].add(app2)
        
        # Log detected patterns
        for app, linked_apps in cross_app_links.items():
            if linked_apps:
                logger.info(f"Cross-app navigation detected: '{app}' ↔ {linked_apps}")
        
        return cross_app_links
    
    def _map_to_applications(
        self,
        access_info: List[AccessInfo],
        cross_app_links: Dict[str, Set[str]]
    ) -> Dict[str, ApplicationAccessPattern]:
        """
        Map access information to applications.
        
        Args:
            access_info: List of file access information
            cross_app_links: Cross-application navigation links
            
        Returns:
            Dictionary mapping application name to access patterns
        """
        app_patterns = {}
        
        # Initialize application patterns
        for app in self.applications:
            app_name = app['name']
            app_patterns[app_name] = ApplicationAccessPattern(
                name=app_name,
                path=app['path'],
                cross_app_links=list(cross_app_links.get(app_name, []))
            )
        
        # Map accesses to applications
        for access in access_info:
            app_name = self._find_application_for_file(Path(access.path))
            
            if app_name and app_name in app_patterns:
                access.application_name = app_name
                
                app_patterns[app_name].accessed_files.append(access)
                app_patterns[app_name].total_accesses += access.access_count
        
        # Calculate unique files and access frequency
        for pattern in app_patterns.values():
            unique_paths = set(a.path for a in pattern.accessed_files)
            pattern.unique_files = len(unique_paths)
            
            if pattern.total_accesses > 0:
                pattern.access_frequency = pattern.total_accesses / max(self.lookback_hours, 1)
        
        return app_patterns
    
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
    
    def _calculate_activity_scores(self, app_patterns: Dict[str, ApplicationAccessPattern]) -> None:
        """
        Calculate activity scores based on access patterns.
        
        Scoring:
        - Files accessed <1 hour: 20 points per access
        - Files accessed <6 hours: 15 points per access
        - Files accessed <24 hours: 10 points per access
        - High-frequency files (10+ accesses): +10 points per file
        - Cross-application links: +5 points per linked app
        
        Args:
            app_patterns: Dictionary of application patterns (modified in place)
        """
        now = datetime.now()
        
        for app_name, pattern in app_patterns.items():
            score = 0.0
            high_frequency_files = 0
            
            for access in pattern.accessed_files:
                age_hours = (now - access.access_time).total_seconds() / 3600
                
                if age_hours < 1:
                    score += access.access_count * 20
                elif age_hours < 6:
                    score += access.access_count * 15
                else:
                    score += access.access_count * 10
                
                # Bonus for high-frequency files
                if access.access_count >= 10:
                    high_frequency_files += 1
                    score += 10
            
            # Bonus for cross-application navigation
            score += len(pattern.cross_app_links) * 5
            
            pattern.activity_score = score
            
            if score > 0:
                logger.info(f"Application '{app_name}' access score: {score:.1f} "
                          f"({pattern.total_accesses} accesses, "
                          f"{pattern.unique_files} files, "
                          f"{len(pattern.cross_app_links)} cross-app links)")
    
    def get_top_accessed_applications(self, count: int = 3) -> List[ApplicationAccessPattern]:
        """
        Get top N applications by access patterns.
        
        Args:
            count: Number of applications to return
            
        Returns:
            List of ApplicationAccessPattern sorted by score (descending)
        """
        app_patterns = self.track_access_patterns()
        
        # Filter and sort by activity score
        active_apps = [
            pattern for pattern in app_patterns.values()
            if pattern.activity_score > 0
        ]
        
        active_apps.sort(key=lambda x: x.activity_score, reverse=True)
        
        return active_apps[:count]
    
    def to_dict(self, app_pattern: ApplicationAccessPattern) -> Dict[str, Any]:
        """Convert ApplicationAccessPattern to dictionary"""
        return {
            'name': app_pattern.name,
            'path': app_pattern.path,
            'total_accesses': app_pattern.total_accesses,
            'unique_files': app_pattern.unique_files,
            'access_frequency': app_pattern.access_frequency,
            'activity_score': app_pattern.activity_score,
            'cross_app_links': app_pattern.cross_app_links,
            'top_accessed_files': [
                {
                    'path': a.path,
                    'access_count': a.access_count,
                    'access_time': a.access_time.isoformat()
                }
                for a in sorted(app_pattern.accessed_files, key=lambda x: x.access_count, reverse=True)[:10]
            ]
        }
