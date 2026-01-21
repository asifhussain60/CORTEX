"""Tests for dependency resolver (PHASE-DEPLOYMENT-002 AC-DEP-002-05).

This module tests the multi-repo dependency conflict resolution.
"""

import json
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def multi_repo_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a multi-repo workspace structure.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the PROJECTS root.
    """
    projects = tmp_path / "PROJECTS"
    projects.mkdir()
    
    # CORTEX
    cortex = projects / "CORTEX"
    cortex.mkdir()
    (cortex / "requirements.txt").write_text("pandas>=2.0.0\nrequests>=2.28.0\nsqlalchemy>=2.0.0")
    
    # KASHKOLE (financial domain)
    kashkole = projects / "KASHKOLE"
    kashkole.mkdir()
    (kashkole / "requirements.txt").write_text("pandas>=1.5.0\nnumpy>=1.24.0\nopenpyxl>=3.0.0")
    
    # KSESSIONS (session management)
    ksessions = projects / "KSESSIONS"
    ksessions.mkdir()
    (ksessions / "requirements.txt").write_text("fastapi>=0.100.0\npydantic>=2.0.0\nredis>=4.0.0")
    
    yield projects


@pytest.fixture
def resolver_module():
    """Import the dependency resolver module.
    
    Returns:
        The dependency_resolver module.
    """
    from cortex.orchestrators.onboarding import dependency_resolver
    return dependency_resolver


class TestScanMultiRepoRequirements:
    """Tests for multi-repo requirements scanning."""
    
    def test_scan_multi_repo_requirements(
        self, multi_repo_workspace: Path, resolver_module
    ) -> None:
        """Scan D:\\PROJECTS\\* for requirements.txt files.
        
        Args:
            multi_repo_workspace: Path to multi-repo workspace.
            resolver_module: The dependency resolver module.
        """
        resolver = resolver_module.DependencyResolver(multi_repo_workspace)
        repos = resolver.scan_requirements()
        
        assert len(repos) >= 3
        assert "CORTEX" in repos
        assert "KASHKOLE" in repos
        assert "KSESSIONS" in repos


class TestBuildDependencyGraph:
    """Tests for dependency graph building."""
    
    def test_build_dependency_graph(
        self, multi_repo_workspace: Path, resolver_module
    ) -> None:
        """Build dependency graph showing package → versions across repos.
        
        Args:
            multi_repo_workspace: Path to multi-repo workspace.
            resolver_module: The dependency resolver module.
        """
        resolver = resolver_module.DependencyResolver(multi_repo_workspace)
        graph = resolver.build_dependency_graph()
        
        assert "pandas" in graph
        assert len(graph["pandas"]) >= 2  # CORTEX and KASHKOLE both use pandas


class TestDetectVersionConflicts:
    """Tests for version conflict detection."""
    
    def test_detect_version_conflicts(
        self, multi_repo_workspace: Path, resolver_module
    ) -> None:
        """Detect conflicts like KASHKOLE needs pandas 1.5, CORTEX needs 2.0.
        
        Args:
            multi_repo_workspace: Path to multi-repo workspace.
            resolver_module: The dependency resolver module.
        """
        resolver = resolver_module.DependencyResolver(multi_repo_workspace)
        conflicts = resolver.detect_conflicts()
        
        # pandas has incompatible version ranges
        assert any(c.package == "pandas" for c in conflicts)


class TestSuggestResolutionStrategy:
    """Tests for resolution strategy suggestion."""
    
    def test_suggest_resolution_strategy(
        self, multi_repo_workspace: Path, resolver_module
    ) -> None:
        """Suggest resolution strategy (shared venv vs isolated).
        
        Args:
            multi_repo_workspace: Path to multi-repo workspace.
            resolver_module: The dependency resolver module.
        """
        resolver = resolver_module.DependencyResolver(multi_repo_workspace)
        strategies = resolver.suggest_resolutions()
        
        assert len(strategies) >= 1
        
        # Each strategy should have a recommendation
        for strategy in strategies:
            assert strategy.recommendation in ["unified", "isolated", "upgrade"]


class TestGenerateConflictReport:
    """Tests for conflict report generation."""
    
    def test_generate_conflict_report(
        self, multi_repo_workspace: Path, resolver_module
    ) -> None:
        """Generate conflict_resolution_report.yaml.
        
        Args:
            multi_repo_workspace: Path to multi-repo workspace.
            resolver_module: The dependency resolver module.
        """
        resolver = resolver_module.DependencyResolver(multi_repo_workspace)
        report = resolver.generate_report()
        
        assert report is not None
        assert hasattr(report, 'conflicts') or 'conflicts' in report
        assert hasattr(report, 'recommendations') or 'recommendations' in report
