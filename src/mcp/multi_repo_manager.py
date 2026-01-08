"""
Multi-Repo Manager for CORTEX MCP

Manages multiple repositories with discovery, cross-repo operations, and isolation.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P2
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
import subprocess
import json


logger = logging.getLogger("cortex.mcp.multi_repo")


@dataclass
class Repository:
    """Repository metadata"""
    path: Path
    name: str
    brain_path: Optional[Path] = None
    config: Dict[str, Any] = field(default_factory=dict)
    is_cortex_enabled: bool = False
    
    def __post_init__(self):
        self.path = Path(self.path).resolve()
        if self.brain_path:
            self.brain_path = Path(self.brain_path).resolve()


class RepoDiscovery:
    """
    Repository discovery system.
    
    Discovers Git repositories in workspace and identifies CORTEX-enabled repos.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        logger.info(f"RepoDiscovery initialized with workspace: {self.workspace_root}")
    
    def discover_repos(self, max_depth: int = 3) -> List[Repository]:
        """
        Discover all Git repositories in workspace.
        
        Args:
            max_depth: Maximum directory depth to search
            
        Returns:
            List of discovered repositories
        """
        repos = []
        
        def search_dir(path: Path, depth: int):
            if depth > max_depth:
                return
            
            # Check if this is a git repo
            if (path / ".git").exists():
                repo = self._create_repository(path)
                repos.append(repo)
                return  # Don't search subdirs of a git repo
            
            # Search subdirectories
            try:
                for item in path.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        search_dir(item, depth + 1)
            except PermissionError:
                pass
        
        search_dir(self.workspace_root, 0)
        logger.info(f"Discovered {len(repos)} repositories")
        return repos
    
    def _create_repository(self, path: Path) -> Repository:
        """Create Repository object with metadata"""
        name = path.name
        
        # Check for CORTEX brain
        brain_path = path / "cortex-brain"
        is_cortex_enabled = brain_path.exists()
        
        # Load config if available
        config = {}
        config_file = path / "cortex.config.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config for {name}: {e}")
        
        return Repository(
            path=path,
            name=name,
            brain_path=brain_path if is_cortex_enabled else None,
            config=config,
            is_cortex_enabled=is_cortex_enabled
        )
    
    def find_repo_by_name(self, name: str, repos: Optional[List[Repository]] = None) -> Optional[Repository]:
        """Find repository by name"""
        if repos is None:
            repos = self.discover_repos()
        
        for repo in repos:
            if repo.name == name:
                return repo
        return None
    
    def find_cortex_repos(self, repos: Optional[List[Repository]] = None) -> List[Repository]:
        """Find all CORTEX-enabled repositories"""
        if repos is None:
            repos = self.discover_repos()
        
        return [repo for repo in repos if repo.is_cortex_enabled]


class CrossRepoOperations:
    """
    Cross-repository operations.
    
    Executes operations across multiple repositories with coordination.
    """
    
    def __init__(self):
        self.active_repos: Set[str] = set()
        logger.info("CrossRepoOperations initialized")
    
    def execute_command(self, repos: List[Repository], command: str) -> Dict[str, Any]:
        """
        Execute command across multiple repositories.
        
        Args:
            repos: List of repositories
            command: Command to execute
            
        Returns:
            Dict mapping repo name to result
        """
        results = {}
        
        for repo in repos:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=repo.path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                results[repo.name] = {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            except Exception as e:
                results[repo.name] = {
                    "success": False,
                    "error": str(e)
                }
        
        logger.info(f"Executed command across {len(repos)} repos")
        return results
    
    def sync_repos(self, repos: List[Repository]) -> Dict[str, bool]:
        """
        Sync repositories (git pull).
        
        Args:
            repos: List of repositories
            
        Returns:
            Dict mapping repo name to success status
        """
        results = {}
        
        for repo in repos:
            try:
                result = subprocess.run(
                    ["git", "pull", "--rebase"],
                    cwd=repo.path,
                    capture_output=True,
                    timeout=60
                )
                results[repo.name] = result.returncode == 0
            except Exception as e:
                logger.error(f"Sync failed for {repo.name}: {e}")
                results[repo.name] = False
        
        return results
    
    def search_across_repos(self, repos: List[Repository], pattern: str) -> Dict[str, List[str]]:
        """
        Search for pattern across repositories.
        
        Args:
            repos: List of repositories
            pattern: Search pattern (regex)
            
        Returns:
            Dict mapping repo name to list of matching lines
        """
        results = {}
        
        for repo in repos:
            try:
                result = subprocess.run(
                    ["grep", "-r", "-n", pattern, "."],
                    cwd=repo.path,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    matches = result.stdout.strip().split('\n')
                    results[repo.name] = matches
            except Exception:
                pass
        
        return results


class RepoIsolation:
    """
    Repository isolation system.
    
    Ensures operations in one repository don't affect others.
    Provides workspace isolation and context switching.
    """
    
    def __init__(self):
        self.current_repo: Optional[Repository] = None
        self.repo_contexts: Dict[str, Dict[str, Any]] = {}
        logger.info("RepoIsolation initialized")
    
    def switch_context(self, repo: Repository) -> bool:
        """
        Switch execution context to repository.
        
        Args:
            repo: Target repository
            
        Returns:
            True if successful
        """
        try:
            # Save current context if exists
            if self.current_repo:
                self.repo_contexts[self.current_repo.name] = {
                    "cwd": os.getcwd()
                }
            
            # Switch to new repo
            os.chdir(repo.path)
            self.current_repo = repo
            
            logger.info(f"Switched context to {repo.name}")
            return True
        except Exception as e:
            logger.error(f"Context switch failed: {e}")
            return False
    
    def get_isolated_env(self, repo: Repository) -> Dict[str, str]:
        """
        Get isolated environment variables for repository.
        
        Args:
            repo: Repository
            
        Returns:
            Environment dict
        """
        env = os.environ.copy()
        
        # Add repo-specific env vars
        env["CORTEX_REPO_NAME"] = repo.name
        env["CORTEX_REPO_PATH"] = str(repo.path)
        
        if repo.brain_path:
            env["CORTEX_BRAIN_PATH"] = str(repo.brain_path)
        
        return env
    
    def execute_isolated(self, repo: Repository, command: str) -> Dict[str, Any]:
        """
        Execute command in isolated repository context.
        
        Args:
            repo: Repository
            command: Command to execute
            
        Returns:
            Execution result
        """
        env = self.get_isolated_env(repo)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=repo.path,
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class MultiRepoManager:
    """
    Central multi-repository manager.
    
    Coordinates discovery, cross-repo operations, and isolation.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.discovery = RepoDiscovery(self.workspace_root)
        self.cross_repo = CrossRepoOperations()
        self.isolation = RepoIsolation()
        self.repos: List[Repository] = []
        logger.info(f"MultiRepoManager initialized for {self.workspace_root}")
    
    def initialize(self):
        """Initialize manager and discover repositories"""
        self.repos = self.discovery.discover_repos()
        logger.info(f"Initialized with {len(self.repos)} repositories")
    
    def get_repos(self) -> List[Repository]:
        """Get all discovered repositories"""
        if not self.repos:
            self.initialize()
        return self.repos
    
    def get_cortex_repos(self) -> List[Repository]:
        """Get CORTEX-enabled repositories"""
        return self.discovery.find_cortex_repos(self.get_repos())
    
    def execute_cross_repo(self, command: str, repo_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute command across repositories.
        
        Args:
            command: Command to execute
            repo_names: Optional list of repo names (default: all CORTEX repos)
            
        Returns:
            Results dict
        """
        if repo_names:
            repos = [r for r in self.get_repos() if r.name in repo_names]
        else:
            repos = self.get_cortex_repos()
        
        return self.cross_repo.execute_command(repos, command)
    
    def sync_all(self) -> Dict[str, bool]:
        """Sync all CORTEX-enabled repositories"""
        return self.cross_repo.sync_repos(self.get_cortex_repos())


# Global instance
_manager: Optional[MultiRepoManager] = None


def get_multi_repo_manager(workspace_root: Optional[Path] = None) -> MultiRepoManager:
    """Get global MultiRepoManager instance"""
    global _manager
    if _manager is None:
        _manager = MultiRepoManager(workspace_root)
        _manager.initialize()
    return _manager
