"""
Git History Analyzer for CORTEX

Analyzes git commit history to identify frequently edited files and active development areas.
Works with any git repository structure (single or multiple repos).

Features:
- Parses git log for recent commits
- Tracks file change frequency
- Maps changes to application boundaries
- Handles multiple git repositories in workspace
- Configurable lookback period

Performance Target: <2s for 7-day history

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


@dataclass
class FileChangeInfo:
    """Information about file changes in git"""
    file_path: str
    commit_count: int
    additions: int
    deletions: int
    last_modified: datetime
    commits: List[str] = field(default_factory=list)
    application_name: Optional[str] = None


@dataclass
class ApplicationGitActivity:
    """Git activity for an application"""
    name: str
    path: str
    total_commits: int = 0
    files_changed: List[FileChangeInfo] = field(default_factory=list)
    commit_frequency: float = 0.0  # commits per day
    activity_score: float = 0.0
    contributors: List[str] = field(default_factory=list)


class GitHistoryAnalyzer:
    """
    Analyzes git commit history to detect development activity patterns.
    
    Analysis Methods:
    1. Parse git log for recent commits
    2. Track file change frequency
    3. Identify frequently modified files
    4. Map changes to applications
    
    Scoring:
    - Commits in last 24 hours: 30 points per commit
    - Commits in last 7 days: 20 points per commit
    - High-change files (10+ commits): +10 points
    - Multiple contributors: +5 points per contributor
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize git history analyzer.
        
        Args:
            config: Configuration dictionary with:
                - workspace_path: Path to workspace root
                - applications: List of discovered applications
                - lookback_days: How far back to analyze (default: 7)
                - max_commits: Performance limit (default: 1000)
        """
        self.workspace_path = Path(config['workspace_path'])
        self.applications = config.get('applications', [])
        self.lookback_days = config.get('lookback_days', 7)
        self.max_commits = config.get('max_commits', 1000)
        
        # Find all git repositories in workspace
        self.git_repos = self._find_git_repositories()
        
        logger.info(f"Initialized Git History Analyzer: {self.workspace_path}")
        logger.info(f"Found {len(self.git_repos)} git repositories, lookback: {self.lookback_days} days")
    
    def _find_git_repositories(self) -> List[Path]:
        """
        Find all git repositories in workspace.
        
        Returns:
            List of paths to .git directories
        """
        git_repos = []
        
        try:
            # Look for .git directories
            for root, dirs, files in os.walk(self.workspace_path):
                if '.git' in dirs:
                    repo_path = Path(root)
                    git_repos.append(repo_path)
                    logger.debug(f"Found git repository: {repo_path}")
                    
                    # Don't recurse into .git directories
                    dirs.remove('.git')
                
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in {
                    'node_modules', '__pycache__', 'venv', '.venv',
                    'dist', 'build', 'target', 'bin', 'obj'
                }]
        
        except Exception as e:
            logger.error(f"Error finding git repositories: {e}")
        
        return git_repos
    
    def analyze_git_activity(self) -> Dict[str, ApplicationGitActivity]:
        """
        Analyze git commit history for all repositories.
        
        Returns:
            Dictionary mapping application name to git activity
        """
        logger.info("Starting git history analysis...")
        
        # Collect file changes from all repositories
        all_file_changes = {}
        
        for repo_path in self.git_repos:
            file_changes = self._analyze_repository(repo_path)
            
            # Merge with existing changes
            for file_path, change_info in file_changes.items():
                if file_path in all_file_changes:
                    # Merge change info
                    existing = all_file_changes[file_path]
                    existing.commit_count += change_info.commit_count
                    existing.additions += change_info.additions
                    existing.deletions += change_info.deletions
                    existing.commits.extend(change_info.commits)
                    
                    if change_info.last_modified > existing.last_modified:
                        existing.last_modified = change_info.last_modified
                else:
                    all_file_changes[file_path] = change_info
        
        # Map to applications
        app_activity = self._map_to_applications(all_file_changes)
        
        # Calculate activity scores
        self._calculate_activity_scores(app_activity)
        
        logger.info(f"Git analysis complete: {len(all_file_changes)} files changed across {len(app_activity)} applications")
        
        return app_activity
    
    def _analyze_repository(self, repo_path: Path) -> Dict[str, FileChangeInfo]:
        """
        Analyze a single git repository.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dictionary mapping file path to FileChangeInfo
        """
        file_changes = {}
        
        try:
            # Build git log command
            since_date = datetime.now() - timedelta(days=self.lookback_days)
            since_str = since_date.strftime('%Y-%m-%d')
            
            cmd = [
                'git', '-C', str(repo_path),
                'log',
                f'--since={since_str}',
                '--numstat',
                '--pretty=format:%H|%an|%ad',
                '--date=iso',
                f'--max-count={self.max_commits}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"Git log failed for {repo_path}: {result.stderr}")
                return file_changes
            
            # Parse git log output
            file_changes = self._parse_git_log(result.stdout, repo_path)
            
            logger.debug(f"Analyzed {repo_path}: {len(file_changes)} files changed")
        
        except subprocess.TimeoutExpired:
            logger.error(f"Git log timeout for {repo_path}")
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_path}: {e}")
        
        return file_changes
    
    def _parse_git_log(self, log_output: str, repo_path: Path) -> Dict[str, FileChangeInfo]:
        """
        Parse git log --numstat output.
        
        Args:
            log_output: Git log output
            repo_path: Repository path
            
        Returns:
            Dictionary mapping file path to FileChangeInfo
        """
        file_changes = {}
        current_commit = None
        current_author = None
        current_date = None
        
        for line in log_output.split('\n'):
            line = line.strip()
            
            if not line:
                continue
            
            # Parse commit header (format: HASH|AUTHOR|DATE)
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 3:
                    current_commit = parts[0]
                    current_author = parts[1]
                    try:
                        current_date = datetime.fromisoformat(parts[2].replace(' ', 'T').split('+')[0].split('-')[0].strip())
                    except:
                        current_date = datetime.now()
                    continue
            
            # Parse numstat line (format: additions deletions filename)
            parts = line.split('\t')
            if len(parts) >= 3:
                try:
                    additions = int(parts[0]) if parts[0] != '-' else 0
                    deletions = int(parts[1]) if parts[1] != '-' else 0
                    file_name = parts[2]
                    
                    # Build absolute file path
                    file_path = str(repo_path / file_name)
                    
                    if file_path not in file_changes:
                        file_changes[file_path] = FileChangeInfo(
                            file_path=file_path,
                            commit_count=0,
                            additions=0,
                            deletions=0,
                            last_modified=current_date,
                            commits=[]
                        )
                    
                    change_info = file_changes[file_path]
                    change_info.commit_count += 1
                    change_info.additions += additions
                    change_info.deletions += deletions
                    
                    if current_commit:
                        change_info.commits.append(current_commit)
                    
                    if current_date and current_date > change_info.last_modified:
                        change_info.last_modified = current_date
                
                except (ValueError, IndexError) as e:
                    logger.debug(f"Error parsing numstat line: {line}: {e}")
                    continue
        
        return file_changes
    
    def _map_to_applications(
        self,
        file_changes: Dict[str, FileChangeInfo]
    ) -> Dict[str, ApplicationGitActivity]:
        """
        Map file changes to application boundaries.
        
        Args:
            file_changes: Dictionary of file changes
            
        Returns:
            Dictionary mapping application name to git activity
        """
        app_activity = {}
        
        # Initialize application activity
        for app in self.applications:
            app_name = app['name']
            app_activity[app_name] = ApplicationGitActivity(
                name=app_name,
                path=app['path']
            )
        
        # Map files to applications
        for file_path, change_info in file_changes.items():
            app_name = self._find_application_for_file(Path(file_path))
            
            if app_name and app_name in app_activity:
                change_info.application_name = app_name
                
                app_activity[app_name].files_changed.append(change_info)
                app_activity[app_name].total_commits += change_info.commit_count
        
        # Calculate commit frequency (commits per day)
        for activity in app_activity.values():
            if activity.total_commits > 0:
                activity.commit_frequency = activity.total_commits / max(self.lookback_days, 1)
        
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
    
    def _calculate_activity_scores(self, app_activity: Dict[str, ApplicationGitActivity]) -> None:
        """
        Calculate git activity scores for each application.
        
        Scoring:
        - Commits in last 24 hours: 30 points per commit
        - Commits in last 7 days: 20 points per commit
        - High-change files (10+ commits): +10 points per file
        - Frequent commits (>5/day): +20 points
        
        Args:
            app_activity: Dictionary of application activity (modified in place)
        """
        now = datetime.now()
        one_day_ago = now - timedelta(days=1)
        
        for app_name, activity in app_activity.items():
            score = 0.0
            high_change_files = 0
            
            for file_change in activity.files_changed:
                # Recent commits score higher
                if file_change.last_modified >= one_day_ago:
                    score += file_change.commit_count * 30
                else:
                    score += file_change.commit_count * 20
                
                # Bonus for high-change files
                if file_change.commit_count >= 10:
                    high_change_files += 1
                    score += 10
            
            # Bonus for frequent commits
            if activity.commit_frequency > 5:
                score += 20
            
            activity.activity_score = score
            
            if score > 0:
                logger.info(f"Application '{app_name}' git score: {score:.1f} "
                          f"({activity.total_commits} commits, "
                          f"{high_change_files} high-change files, "
                          f"{activity.commit_frequency:.1f} commits/day)")
    
    def get_top_active_applications(self, count: int = 3) -> List[ApplicationGitActivity]:
        """
        Get top N applications by git activity.
        
        Args:
            count: Number of applications to return
            
        Returns:
            List of ApplicationGitActivity sorted by score (descending)
        """
        app_activity = self.analyze_git_activity()
        
        # Filter and sort by activity score
        active_apps = [
            activity for activity in app_activity.values()
            if activity.activity_score > 0
        ]
        
        active_apps.sort(key=lambda x: x.activity_score, reverse=True)
        
        return active_apps[:count]
    
    def to_dict(self, app_activity: ApplicationGitActivity) -> Dict[str, Any]:
        """Convert ApplicationGitActivity to dictionary"""
        return {
            'name': app_activity.name,
            'path': app_activity.path,
            'total_commits': app_activity.total_commits,
            'commit_frequency': app_activity.commit_frequency,
            'activity_score': app_activity.activity_score,
            'high_change_files': len([f for f in app_activity.files_changed if f.commit_count >= 10]),
            'top_changed_files': [
                {
                    'path': f.file_path,
                    'commit_count': f.commit_count,
                    'additions': f.additions,
                    'deletions': f.deletions,
                    'last_modified': f.last_modified.isoformat()
                }
                for f in sorted(app_activity.files_changed, key=lambda x: x.commit_count, reverse=True)[:10]
            ]
        }


# Import os for walk function
import os
