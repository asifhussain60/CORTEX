"""
JSON-First Adapter Implementation
Fast, simple data loading for small-to-medium repositories
Author: Asif Hussain
Date: 2026-02-04
Authority: CORE-008, CORE-030 (Implementation Truth)
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from cortex.visualization.dashboard_data_adapter import DashboardDataAdapter


logger = logging.getLogger(__name__)


class JSONAdapter(DashboardDataAdapter):
    """
    JSON-first dashboard data adapter.
    
    Architecture:
    - One dashboard.json per repository
    - Located at: {base_path}/{slug}/dashboard.json
    - Load time: ~5ms (40x faster than SQLite)
    - File size: <15KB (efficient for git versioning)
    - Suitable for: <10K files, <5 searches/month
    
    Graduation Path:
    - If search usage >5x/month: migrate to SQLite
    - If repo count >100: migrate to PostgreSQL
    - Implementation Truth: Track usage via metadata.json
    """
    
    def __init__(self, base_path: Path = None):
        """
        Initialize JSON adapter.
        
        Args:
            base_path: Root directory for dashboard data
                     Default: company/dashboards/repos/ (for compatibility)
        """
        if base_path is None:
            base_path = Path("company/dashboards/repos")
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"JSONAdapter initialized with base_path: {self.base_path}")
    
    def _get_dashboard_path(self, repo_slug: str) -> Path:
        """Get path to dashboard.json for repository."""
        return self.base_path / repo_slug / "dashboard.json"
    
    def _get_repo_dir(self, repo_slug: str) -> Path:
        """Get repository directory."""
        return self.base_path / repo_slug
    
    def load(self, repo_slug: str) -> Optional[Dict[str, Any]]:
        """
        Load dashboard data from JSON file.
        
        Args:
            repo_slug: Repository identifier
        
        Returns:
            Dictionary with dashboard data or None if not found
        """
        try:
            dashboard_path = self._get_dashboard_path(repo_slug)
            
            if not dashboard_path.exists():
                logger.debug(f"Dashboard file not found: {dashboard_path}")
                return None
            
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"Loaded dashboard for {repo_slug}")
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {repo_slug}: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Error loading dashboard {repo_slug}: {e}")
            return None
    
    def save(self, repo_slug: str, data: Dict[str, Any]) -> bool:
        """
        Save dashboard data to JSON file.
        
        Args:
            repo_slug: Repository identifier
            data: Dashboard data dictionary
        
        Returns:
            True if successful, False otherwise
        """
        try:
            repo_dir = self._get_repo_dir(repo_slug)
            repo_dir.mkdir(parents=True, exist_ok=True)
            
            dashboard_path = self._get_dashboard_path(repo_slug)
            
            # Write with indentation for readability and git diffs
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved dashboard for {repo_slug} to {dashboard_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving dashboard {repo_slug}: {e}")
            return False
    
    def list_repos(self) -> List[str]:
        """
        List all repositories with dashboard data.
        
        Returns:
            List of repository slugs
        """
        try:
            repos = []
            for repo_dir in self.base_path.iterdir():
                if repo_dir.is_dir():
                    dashboard_path = repo_dir / "dashboard.json"
                    if dashboard_path.exists():
                        repos.append(repo_dir.name)
            
            logger.debug(f"Listed {len(repos)} repositories")
            return sorted(repos)
        
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return []
    
    def search(self, query: str) -> List[str]:
        """
        Search repositories by name (simple Array.filter style).
        
        Args:
            query: Search query string
        
        Returns:
            List of matching repository slugs
        
        Note:
            This is O(n) filtering. For better performance on 100+ repos,
            graduate to SQLite adapter with FTS5 full-text search.
        """
        try:
            matching = []
            query_lower = query.lower()
            
            for repo_slug in self.list_repos():
                # Search in slug
                if query_lower in repo_slug.lower():
                    matching.append(repo_slug)
                    continue
                
                # Search in display_name (if available)
                data = self.load(repo_slug)
                if data and "repo" in data:
                    display_name = data["repo"].get("display_name", "")
                    if query_lower in display_name.lower():
                        matching.append(repo_slug)
                        continue
                
                # Search in description (if available)
                if data and "overview" in data:
                    description = data["overview"].get("summary", "")
                    if query_lower in description.lower():
                        matching.append(repo_slug)
            
            logger.debug(f"Search '{query}' returned {len(matching)} results")
            return matching
        
        except Exception as e:
            logger.error(f"Error searching repositories: {e}")
            return []
