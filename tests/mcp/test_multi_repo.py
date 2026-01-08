"""
Comprehensive tests for Multi-Repo Manager (feat06-mcp Phase 2).

Tests repository discovery, cross-repo operations, and isolation.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P2
"""

import pytest
import tempfile
import shutil
import json
import subprocess
from pathlib import Path
from src.mcp.multi_repo_manager import (
    MultiRepoManager,
    RepoDiscovery,
    Repository,
    CrossRepoOperations,
    RepoIsolation
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with test repos."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Create test repo 1 (CORTEX-enabled)
    repo1 = workspace / "repo1"
    repo1.mkdir()
    (repo1 / ".git").mkdir()
    (repo1 / "cortex-brain").mkdir()
    (repo1 / "cortex-brain" / "tier0").mkdir()
    
    config1 = {
        "project": "test-project-1",
        "cortex_enabled": True,
        "brain_version": "6.0.0"
    }
    with open(repo1 / "cortex.config.json", "w") as f:
        json.dump(config1, f)
    
    # Create test repo 2 (non-CORTEX)
    repo2 = workspace / "repo2"
    repo2.mkdir()
    (repo2 / ".git").mkdir()
    
    # Create test repo 3 (CORTEX-enabled)
    repo3 = workspace / "repo3"
    repo3.mkdir()
    (repo3 / ".git").mkdir()
    (repo3 / "cortex-brain").mkdir()
    
    return workspace


class TestRepoDiscovery:
    """Test repository discovery functionality."""
    
    def test_discovers_git_repos(self, temp_workspace):
        """Test discovers all Git repositories in workspace."""
        discovery = RepoDiscovery(workspace_root=temp_workspace)
        repos = discovery.discover_repos(max_depth=2)
        
        assert len(repos) == 3
        repo_names = [r.name for r in repos]
        assert "repo1" in repo_names
        assert "repo2" in repo_names
        assert "repo3" in repo_names
    
    def test_identifies_cortex_enabled_repos(self, temp_workspace):
        """Test identifies CORTEX-enabled repositories."""
        discovery = RepoDiscovery(workspace_root=temp_workspace)
        repos = discovery.discover_repos(max_depth=2)
        
        cortex_repos = [r for r in repos if r.is_cortex_enabled]
        assert len(cortex_repos) == 2
        
        non_cortex_repos = [r for r in repos if not r.is_cortex_enabled]
        assert len(non_cortex_repos) == 1
    
    def test_loads_repo_config(self, temp_workspace):
        """Test loads cortex.config.json from repositories."""
        discovery = RepoDiscovery(workspace_root=temp_workspace)
        repos = discovery.discover_repos(max_depth=2)
        
        repo1 = next(r for r in repos if r.name == "repo1")
        assert repo1.config["project"] == "test-project-1"
        assert repo1.config["cortex_enabled"] is True
    
    def test_respects_max_depth(self, temp_workspace):
        """Test respects maximum search depth."""
        # Create nested repo structure
        nested = temp_workspace / "level1" / "level2" / "level3"
        nested.mkdir(parents=True)
        (nested / ".git").mkdir()
        
        discovery = RepoDiscovery(workspace_root=temp_workspace)
        
        # Should not find nested repo with max_depth=2
        repos = discovery.discover_repos(max_depth=2)
        repo_paths = [str(r.path) for r in repos]
        assert str(nested) not in repo_paths
        
        # Should find it with max_depth=4
        repos = discovery.discover_repos(max_depth=4)
        repo_paths = [str(r.path) for r in repos]
        assert str(nested) in repo_paths
    
    def test_ignores_hidden_directories(self, temp_workspace):
        """Test ignores hidden directories during search."""
        hidden = temp_workspace / ".hidden"
        hidden.mkdir()
        (hidden / ".git").mkdir()
        
        discovery = RepoDiscovery(workspace_root=temp_workspace)
        repos = discovery.discover_repos(max_depth=2)
        
        repo_names = [r.name for r in repos]
        assert ".hidden" not in repo_names


class TestMultiRepoManager:
    """Test MultiRepoManager orchestration."""
    
    def test_manager_initialization(self):
        """Test manager initializes successfully."""
        manager = MultiRepoManager()
        manager.initialize()
        assert len(manager.repos) > 0
    
    def test_manager_lists_repos(self, temp_workspace):
        """Test manager lists all discovered repositories."""
        manager = MultiRepoManager(workspace_root=temp_workspace)
        manager.initialize()
        
        repos = manager.list_repos()
        assert len(repos) >= 3
    
    def test_manager_filters_cortex_repos(self, temp_workspace):
        """Test manager can filter CORTEX-enabled repos."""
        manager = MultiRepoManager(workspace_root=temp_workspace)
        manager.initialize()
        
        cortex_repos = manager.list_repos(cortex_enabled_only=True)
        for repo in cortex_repos:
            assert repo.is_cortex_enabled
    
    def test_manager_gets_repo_by_name(self, temp_workspace):
        """Test manager retrieves repository by name."""
        manager = MultiRepoManager(workspace_root=temp_workspace)
        manager.initialize()
        
        repo = manager.get_repo("repo1")
        assert repo is not None
        assert repo.name == "repo1"
    
    def test_manager_handles_missing_repo(self, temp_workspace):
        """Test manager handles requests for non-existent repos."""
        manager = MultiRepoManager(workspace_root=temp_workspace)
        manager.initialize()
        
        repo = manager.get_repo("nonexistent")
        assert repo is None


class TestCrossRepoOperations:
    """Test cross-repository operations."""
    
    def test_cross_repo_search(self, temp_workspace):
        """Test searching across multiple repositories."""
        # Create files in repos
        (temp_workspace / "repo1" / "test.py").write_text("def hello(): pass")
        (temp_workspace / "repo2" / "test.py").write_text("def world(): pass")
        
        cross_ops = CrossRepoOperations(workspace_root=temp_workspace)
        cross_ops.initialize()
        
        results = cross_ops.search("def ", file_pattern="*.py")
        assert len(results) >= 2
    
    def test_cross_repo_aggregation(self, temp_workspace):
        """Test aggregating data across repositories."""
        cross_ops = CrossRepoOperations(workspace_root=temp_workspace)
        cross_ops.initialize()
        
        # Aggregate repo statistics
        stats = cross_ops.aggregate_stats()
        assert "total_repos" in stats
        assert stats["total_repos"] >= 3
        assert "cortex_enabled_count" in stats
    
    def test_cross_repo_operation_isolation(self, temp_workspace):
        """Test operations maintain repository isolation."""
        cross_ops = CrossRepoOperations(workspace_root=temp_workspace)
        cross_ops.initialize()
        
        # Execute operation in repo1
        result = cross_ops.execute_in_repo(
            repo_name="repo1",
            operation="check_config"
        )
        
        assert result["repo"] == "repo1"
        assert "config" in result


class TestRepoIsolation:
    """Test repository isolation mechanisms."""
    
    def test_isolates_repo_operations(self, temp_workspace):
        """Test operations are isolated to specific repositories."""
        isolation = RepoIsolation(workspace_root=temp_workspace)
        isolation.initialize()
        
        # Create isolation context for repo1
        context = isolation.create_context("repo1")
        
        assert context.repo_name == "repo1"
        assert context.workspace_root == temp_workspace
        assert context.is_isolated
    
    def test_prevents_cross_contamination(self, temp_workspace):
        """Test prevents operations from affecting other repos."""
        isolation = RepoIsolation(workspace_root=temp_workspace)
        isolation.initialize()
        
        # Simulate operation in repo1 that should not affect repo2
        result = isolation.execute_isolated(
            repo_name="repo1",
            operation=lambda ctx: ctx.repo_name
        )
        
        assert result == "repo1"
        
        # Verify repo2 unaffected
        repo2_path = temp_workspace / "repo2"
        assert repo2_path.exists()
    
    def test_cleanup_after_operation(self, temp_workspace):
        """Test cleanup after isolated operations."""
        isolation = RepoIsolation(workspace_root=temp_workspace)
        isolation.initialize()
        
        # Execute operation with cleanup
        context = isolation.create_context("repo1")
        isolation.cleanup_context(context)
        
        # Verify cleanup occurred
        assert not hasattr(context, "_temp_resources")


class TestMultiRepoIntegration:
    """Integration tests for multi-repo functionality."""
    
    def test_full_discovery_and_operation_pipeline(self, temp_workspace):
        """Test complete pipeline: discover → select → operate."""
        # Discover
        discovery = RepoDiscovery(workspace_root=temp_workspace)
        repos = discovery.discover_repos(max_depth=2)
        
        # Select CORTEX-enabled repos
        cortex_repos = [r for r in repos if r.is_cortex_enabled]
        
        # Execute operation across selected repos
        cross_ops = CrossRepoOperations(workspace_root=temp_workspace)
        cross_ops.initialize()
        
        results = []
        for repo in cortex_repos:
            result = cross_ops.execute_in_repo(
                repo_name=repo.name,
                operation="check_config"
            )
            results.append(result)
        
        assert len(results) == 2  # repo1 and repo3
    
    def test_multi_repo_manager_coordinates_operations(self, temp_workspace):
        """Test manager coordinates complex multi-repo operations."""
        manager = MultiRepoManager(workspace_root=temp_workspace)
        manager.initialize()
        
        # Execute coordinated operation
        results = manager.execute_across_repos(
            operation="status_check",
            cortex_enabled_only=True
        )
        
        assert len(results) >= 2
        for result in results:
            assert result["status"] in ["success", "error"]
