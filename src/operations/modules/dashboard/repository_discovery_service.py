"""
Repository Discovery Service

Automatically discovers, validates, and registers repositories for admin dashboard.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from src.dashboard_config import get_config

logger = logging.getLogger(__name__)


@dataclass
class RepoMetadata:
    """Repository metadata"""
    id: str
    name: str
    path: str
    discovered: str
    last_updated: str
    status: str  # active, inactive, missing
    data_files: int
    data_file_list: List[str]
    file_sizes: Dict[str, int]  # filename -> size in bytes
    total_size: int


class RepositoryDiscoveryService:
    """
    Discovers and validates repositories in the data/repos/ directory.
    """
    
    def __init__(self):
        """Initialize discovery service"""
        self.config = get_config()
        self.repos_path = self.config.get_path('repos')
        self.registry_path = self.config.get_path('repository_registry')
        self.collector_config = self.config.get_collector_config()
        self.discovery_config = self.config.get_discovery_config()
        
        logger.info(f"Repository discovery initialized: {self.repos_path}")
    
    def scan_repositories(self) -> List[RepoMetadata]:
        """
        Scan repos directory for valid repositories.
        
        Returns:
            List of discovered repository metadata
        """
        logger.info("Scanning for repositories...")
        
        if not self.repos_path.exists():
            logger.warning(f"Repos path does not exist: {self.repos_path}")
            self.repos_path.mkdir(parents=True, exist_ok=True)
            return []
        
        discovered = []
        
        for item in self.repos_path.iterdir():
            if not item.is_dir():
                continue
            
            # Skip hidden directories
            if item.name.startswith('.'):
                continue
            
            # Validate repository
            if self.validate_repository(item):
                metadata = self._extract_metadata(item)
                discovered.append(metadata)
                logger.info(f"Discovered: {metadata.name} ({metadata.data_files} files)")
            else:
                logger.debug(f"Skipped invalid repository: {item.name}")
        
        logger.info(f"Discovery complete: {len(discovered)} repositories found")
        return discovered
    
    def validate_repository(self, repo_path: Path) -> bool:
        """
        Validate that directory contains valid repository data.
        
        Args:
            repo_path: Path to repository directory
        
        Returns:
            True if valid, False otherwise
        """
        if not repo_path.exists() or not repo_path.is_dir():
            return False
        
        # Check for required files
        data_files = list(repo_path.glob('*.json'))
        
        if len(data_files) < self.discovery_config.min_data_files:
            logger.debug(f"{repo_path.name}: Too few data files ({len(data_files)})")
            return False
        
        # Check for metadata if required
        if self.discovery_config.require_metadata:
            metadata_file = repo_path / "metadata.json"
            if not metadata_file.exists():
                logger.debug(f"{repo_path.name}: Missing metadata.json")
                return False
        
        return True
    
    def _extract_metadata(self, repo_path: Path) -> RepoMetadata:
        """Extract metadata from repository directory"""
        data_files = list(repo_path.glob('*.json'))
        
        # Load metadata.json if exists
        metadata_file = repo_path / "metadata.json"
        repo_name = repo_path.name
        last_updated = datetime.now().isoformat()
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    meta = json.load(f)
                    repo_name = meta.get('repository_name', repo_path.name)
                    last_updated = meta.get('collection_date', last_updated)
            except Exception as e:
                logger.warning(f"Failed to load metadata for {repo_path.name}: {e}")
        
        # Calculate file sizes
        file_sizes = {}
        total_size = 0
        for file in data_files:
            size = file.stat().st_size
            file_sizes[file.name] = size
            total_size += size
        
        return RepoMetadata(
            id=repo_path.name,
            name=repo_name,
            path=str(repo_path.relative_to(self.repos_path.parent.parent)),
            discovered=datetime.now().isoformat(),
            last_updated=last_updated,
            status='active',
            data_files=len(data_files),
            data_file_list=[f.name for f in data_files],
            file_sizes=file_sizes,
            total_size=total_size
        )
    
    def register_repositories(self, repositories: List[RepoMetadata]) -> None:
        """
        Register discovered repositories in registry file.
        
        Args:
            repositories: List of repository metadata to register
        """
        logger.info(f"Registering {len(repositories)} repositories...")
        
        # Load existing registry if exists
        existing_registry = self._load_registry()
        
        # Merge with discovered repos
        registry = {
            "repositories": [asdict(repo) for repo in repositories],
            "last_scan": datetime.now().isoformat(),
            "total_repositories": len(repositories),
            "scan_config": {
                "auto_scan": self.discovery_config.auto_scan,
                "min_data_files": self.discovery_config.min_data_files,
                "require_metadata": self.discovery_config.require_metadata
            }
        }
        
        # Save registry
        self._save_registry(registry)
        logger.info(f"Registry updated: {self.registry_path}")
    
    def remove_missing_repositories(self) -> List[str]:
        """
        Remove repositories from registry that no longer exist.
        
        Returns:
            List of removed repository IDs
        """
        logger.info("Checking for missing repositories...")
        
        registry = self._load_registry()
        if not registry or 'repositories' not in registry:
            return []
        
        removed = []
        active_repos = []
        
        for repo in registry['repositories']:
            repo_path = self.repos_path / repo['id']
            
            if repo_path.exists() and self.validate_repository(repo_path):
                active_repos.append(repo)
            else:
                removed.append(repo['id'])
                logger.info(f"Removed missing repository: {repo['id']}")
        
        if removed:
            registry['repositories'] = active_repos
            registry['total_repositories'] = len(active_repos)
            registry['last_scan'] = datetime.now().isoformat()
            self._save_registry(registry)
        
        return removed
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from file"""
        if not self.registry_path.exists():
            return {}
        
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {}
    
    def _save_registry(self, registry: Dict[str, Any]) -> None:
        """Save registry to file"""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def get_repository_count(self) -> int:
        """Get total count of registered repositories"""
        registry = self._load_registry()
        return registry.get('total_repositories', 0)
    
    def get_repository_by_id(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get specific repository metadata"""
        registry = self._load_registry()
        repos = registry.get('repositories', [])
        
        for repo in repos:
            if repo['id'] == repo_id:
                return repo
        
        return None


# Convenience function
def discover_and_register_repositories() -> List[RepoMetadata]:
    """
    Convenience function to discover and register all repositories.
    
    Returns:
        List of discovered repositories
    """
    service = RepositoryDiscoveryService()
    
    # Scan for repositories
    repos = service.scan_repositories()
    
    # Register them
    service.register_repositories(repos)
    
    # Remove missing
    removed = service.remove_missing_repositories()
    
    if removed:
        logger.info(f"Removed {len(removed)} missing repositories")
    
    return repos


__all__ = ['RepositoryDiscoveryService', 'RepoMetadata', 'discover_and_register_repositories']
