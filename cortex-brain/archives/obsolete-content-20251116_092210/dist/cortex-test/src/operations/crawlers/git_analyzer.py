"""
Git Analyzer Crawler

Extracts development history and activity patterns from Git.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

from .base_crawler import BaseCrawler


class GitAnalyzerCrawler(BaseCrawler):
    """
    Analyzes Git repository to extract:
    - Total commits, branches, contributors
    - Recent activity patterns
    - Hot files (most changed)
    - Branch health
    """
    
    def get_name(self) -> str:
        return "Git Analyzer"
    
    def crawl(self) -> Dict[str, Any]:
        """
        Analyze Git repository history and activity.
        
        Returns:
            Dict containing Git analysis
        """
        self.log_info("Starting Git analysis")
        
        git_data = {
            'git_available': False,
            'is_git_repo': False,
            'total_commits': 0,
            'branches': {'total': 0, 'active': 0, 'stale': 0},
            'contributors': 0,
            'recent_activity': {
                'last_7_days': 0,
                'last_30_days': 0,
                'last_90_days': 0
            },
            'hot_files': [],
            'current_branch': None
        }
        
        # Check if git is available
        if not self._is_git_available():
            self.log_warning("Git not available on system")
            return {"success": True, "data": git_data}
        
        git_data['git_available'] = True
        
        # Check if this is a git repository
        if not self._is_git_repo():
            self.log_warning("Not a Git repository")
            return {"success": True, "data": git_data}
        
        git_data['is_git_repo'] = True
        
        # Gather Git statistics
        try:
            git_data['total_commits'] = self._count_commits()
            git_data['branches'] = self._analyze_branches()
            git_data['contributors'] = self._count_contributors()
            git_data['recent_activity'] = self._analyze_recent_activity()
            git_data['hot_files'] = self._find_hot_files(limit=10)
            git_data['current_branch'] = self._get_current_branch()
            
            self.log_info(
                f"Git analysis complete: {git_data['total_commits']} commits, "
                f"{git_data['branches']['total']} branches"
            )
            
        except Exception as e:
            self.log_error(f"Git analysis failed: {e}")
            return {"success": False, "data": git_data, "error": str(e)}
        
        return {
            "success": True,
            "data": git_data
        }
    
    def _is_git_available(self) -> bool:
        """Check if git command is available."""
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                check=True,
                cwd=self.project_root
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                check=True,
                cwd=self.project_root
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _run_git_command(self, args: List[str]) -> str:
        """
        Run a git command and return output.
        
        Args:
            args: Git command arguments
            
        Returns:
            Command output as string
        """
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=self.project_root
        )
        return result.stdout.strip()
    
    def _count_commits(self) -> int:
        """Count total commits in repository."""
        try:
            output = self._run_git_command(['rev-list', '--count', 'HEAD'])
            return int(output)
        except Exception:
            return 0
    
    def _analyze_branches(self) -> Dict[str, int]:
        """
        Analyze branch statistics.
        
        Returns:
            Dict with total, active, and stale branch counts
        """
        try:
            # Get all branches
            output = self._run_git_command(['branch', '-a'])
            branches = [b.strip().lstrip('* ') for b in output.split('\n') if b.strip()]
            
            # Count branches
            local_branches = [b for b in branches if not b.startswith('remotes/')]
            
            # Analyze activity (last 90 days)
            ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            
            active_count = 0
            for branch in local_branches:
                try:
                    last_commit = self._run_git_command([
                        'log', '-1', '--format=%ci', branch
                    ])
                    if last_commit >= ninety_days_ago:
                        active_count += 1
                except Exception:
                    pass
            
            total = len(local_branches)
            stale = total - active_count
            
            return {
                'total': total,
                'active': active_count,
                'stale': stale
            }
            
        except Exception as e:
            self.log_warning(f"Could not analyze branches: {e}")
            return {'total': 0, 'active': 0, 'stale': 0}
    
    def _count_contributors(self) -> int:
        """Count unique contributors."""
        try:
            output = self._run_git_command(['shortlog', '-sn', '--all'])
            contributors = [line for line in output.split('\n') if line.strip()]
            return len(contributors)
        except Exception:
            return 0
    
    def _analyze_recent_activity(self) -> Dict[str, int]:
        """
        Analyze commit activity for recent time periods.
        
        Returns:
            Dict with commit counts for 7, 30, 90 day periods
        """
        activity = {
            'last_7_days': 0,
            'last_30_days': 0,
            'last_90_days': 0
        }
        
        try:
            # 7 days
            output = self._run_git_command([
                'rev-list', '--count', '--since=7.days.ago', 'HEAD'
            ])
            activity['last_7_days'] = int(output)
            
            # 30 days
            output = self._run_git_command([
                'rev-list', '--count', '--since=30.days.ago', 'HEAD'
            ])
            activity['last_30_days'] = int(output)
            
            # 90 days
            output = self._run_git_command([
                'rev-list', '--count', '--since=90.days.ago', 'HEAD'
            ])
            activity['last_90_days'] = int(output)
            
        except Exception as e:
            self.log_warning(f"Could not analyze recent activity: {e}")
        
        return activity
    
    def _find_hot_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find most frequently changed files.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of dicts with file path and commit count
        """
        try:
            # Get file change statistics
            output = self._run_git_command([
                'log', '--format=', '--name-only', '--diff-filter=M'
            ])
            
            # Count occurrences
            file_counts = {}
            for line in output.split('\n'):
                if line.strip():
                    file_counts[line.strip()] = file_counts.get(line.strip(), 0) + 1
            
            # Sort and limit
            sorted_files = sorted(
                file_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            return [
                {'path': path, 'commits': count}
                for path, count in sorted_files
            ]
            
        except Exception as e:
            self.log_warning(f"Could not find hot files: {e}")
            return []
    
    def _get_current_branch(self) -> str:
        """Get name of current branch."""
        try:
            return self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        except Exception:
            return None
