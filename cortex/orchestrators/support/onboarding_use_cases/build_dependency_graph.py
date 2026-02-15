"""
AC-054A-S1-07,08,09: BuildDependencyGraphUseCase Implementation

Use case for building dependency graphs from repository analysis.

Author: Phase 54-A Implementation (TDD)
Created: 2026-02-15
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class PackageDependency:
    """Package dependency model."""
    name: str
    version: str
    required_by: List[str] = field(default_factory=list)
    transitive_depth: int = 0
    security_advisories: List[str] = field(default_factory=list)


@dataclass
class DependencyGraph:
    """Complete dependency graph."""
    root_packages: List[PackageDependency]
    all_packages: Set[str]
    total_dependencies: int
    max_depth: int


class BuildDependencyGraphUseCase:
    """
    Build dependency graph from repository data.
    
    Constructs graph structure showing package dependencies
    and transitive relationships.
    """
    
    def __init__(self) -> None:
        """Initialize dependency graph builder."""
        pass
    
    def execute(self, repo_data: Dict[str, Any]) -> DependencyGraph:
        """
        Execute dependency graph building.
        
        Args:
            repo_data: Repository analysis data with dependencies
        
        Returns:
            DependencyGraph object
        """
        # Extract direct dependencies
        direct_deps = repo_data.get("direct_dependencies", [])
        transitive_deps = repo_data.get("transitive_dependencies", [])
        
        # Build root packages (direct dependencies)
        root_packages = []
        all_packages = set()
        
        for dep in direct_deps:
            if isinstance(dep, dict):
                name = dep.get("name", "")
                version = dep.get("version", "")
                pkg = PackageDependency(
                    name=name,
                    version=version,
                    required_by=[],
                    transitive_depth=0,
                    security_advisories=[]
                )
                root_packages.append(pkg)
                all_packages.add(name)
        
        # Add transitive dependencies
        for dep in transitive_deps:
            if isinstance(dep, dict):
                name = dep.get("name", "")
                version = dep.get("version", "")
                required_by_list = [dep.get("required_by", "")] if dep.get("required_by") else []
                advisories = dep.get("advisories", [])
                pkg = PackageDependency(
                    name=name,
                    version=version,
                    required_by=required_by_list,
                    transitive_depth=1,
                    security_advisories=advisories if isinstance(advisories, list) else []
                )
                root_packages.append(pkg)
                all_packages.add(name)
        
        # Also process direct dependencies for advisories
        for i, pkg in enumerate(root_packages):
            if pkg.transitive_depth == 0:  # Direct dependency
                # Check if original data has advisories
                for dep in direct_deps:
                    if isinstance(dep, dict) and dep.get("name") == pkg.name:
                        advisories = dep.get("advisories", [])
                        if advisories:
                            # Update with advisories
                            root_packages[i] = PackageDependency(
                                name=pkg.name,
                                version=pkg.version,
                                required_by=pkg.required_by,
                                transitive_depth=pkg.transitive_depth,
                                security_advisories=advisories if isinstance(advisories, list) else []
                            )
        
        max_depth = max((p.transitive_depth for p in root_packages), default=0)
        
        return DependencyGraph(
            root_packages=root_packages,
            all_packages=all_packages,
            total_dependencies=len(root_packages),
            max_depth=max_depth
        )
