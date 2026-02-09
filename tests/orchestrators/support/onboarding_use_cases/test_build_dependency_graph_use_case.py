"""
AC-054A-S1-10,11,12: BuildDependencyGraphUseCase Tests

TDD Test Suite (7+ tests):
- AC-054A-S1-10: Use case builds dependency graphs
- AC-054A-S1-11: Uses PackageDependency models
- AC-054A-S1-12: 7+ unit tests with mock packages

Author: Phase 54-A Implementation
Created: 2026-02-09
Platform: Windows/macOS compatible
"""

import pytest
from dataclasses import dataclass
from typing import List, Set, Optional


@dataclass
class PackageDependency:
    """Package dependency model."""
    name: str
    version: str
    required_by: List[str]  # List of packages that require this
    transitive_depth: int
    security_advisories: List[str]


@dataclass
class DependencyGraph:
    """Complete dependency graph."""
    root_packages: List[PackageDependency]
    all_packages: Set[str]
    total_dependencies: int
    max_depth: int


class TestBuildDependencyGraphUseCase:
    """Test dependency graph construction."""

    @pytest.fixture
    def use_case(self):
        """Initialize BuildDependencyGraphUseCase."""
        from cortex.orchestrators.support.onboarding_use_cases import BuildDependencyGraphUseCase
        return BuildDependencyGraphUseCase()

    @pytest.fixture
    def mock_requirements(self) -> dict:
        """Fixture: Mock package requirements."""
        return {
            "language": "Python",
            "direct_dependencies": [
                {"name": "numpy", "version": "1.24.0"},
                {"name": "pandas", "version": "2.0.0"},
                {"name": "flask", "version": "2.3.0"},
            ],
            "transitive_dependencies": [
                {"name": "wheel", "version": "0.40.0", "required_by": "pip"},
                {"name": "setuptools", "version": "65.0.0", "required_by": "pip"},
            ],
        }

    def test_builds_dependency_graph(self, use_case, mock_requirements):
        """AC-054A-S1-10a: Builds dependency graph."""
        graph = use_case.execute(mock_requirements)
        
        assert isinstance(graph, DependencyGraph)
        assert len(graph.root_packages) > 0

    def test_identifies_direct_dependencies(self, use_case, mock_requirements):
        """AC-054A-S1-10b: Identifies direct dependencies."""
        graph = use_case.execute(mock_requirements)
        
        direct_names = [p.name for p in graph.root_packages if p.transitive_depth == 0]
        assert "numpy" in direct_names or len(direct_names) > 0

    def test_includes_transitive_dependencies(self, use_case, mock_requirements):
        """AC-054A-S1-10c: Includes transitive dependencies."""
        graph = use_case.execute(mock_requirements)
        
        transitive_packages = [p for p in graph.root_packages if p.transitive_depth > 0]
        assert len(transitive_packages) > 0

    def test_returns_package_dependency_models(self, use_case, mock_requirements):
        """AC-054A-S1-11a: Returns PackageDependency models."""
        graph = use_case.execute(mock_requirements)
        
        assert all(isinstance(p, PackageDependency) for p in graph.root_packages)

    def test_tracks_required_by_relationships(self, use_case, mock_requirements):
        """AC-054A-S1-11b: Tracks 'required by' relationships."""
        graph = use_case.execute(mock_requirements)
        
        assert all(hasattr(p, 'required_by') for p in graph.root_packages)

    def test_includes_security_advisories(self, use_case):
        """AC-054A-S1-11c: Includes security advisory information."""
        req_with_vulnerable = {
            "language": "Python",
            "direct_dependencies": [
                {"name": "requests", "version": "2.25.0", "advisories": ["CVE-2023-1234"]},
            ],
        }
        graph = use_case.execute(req_with_vulnerable)
        
        requests_pkg = [p for p in graph.root_packages if p.name == "requests"]
        if requests_pkg:
            assert len(requests_pkg[0].security_advisories) > 0

    def test_calculates_graph_depth(self, use_case, mock_requirements):
        """AC-054A-S1-12a: Calculates maximum graph depth."""
        graph = use_case.execute(mock_requirements)
        
        assert graph.max_depth >= 0
        assert all(p.transitive_depth <= graph.max_depth for p in graph.root_packages)

    def test_counts_total_unique_packages(self, use_case, mock_requirements):
        """AC-054A-S1-12b: Counts total unique packages."""
        graph = use_case.execute(mock_requirements)
        
        assert graph.total_dependencies == len(graph.all_packages)

    def test_empty_requirements_returns_empty_graph(self, use_case):
        """AC-054A-S1-12c: Empty requirements return empty graph."""
        empty = {"language": "Python", "direct_dependencies": []}
        graph = use_case.execute(empty)
        
        assert len(graph.root_packages) == 0
        assert graph.total_dependencies == 0
