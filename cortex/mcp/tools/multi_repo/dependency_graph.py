"""Dependency Graph MCP Tool - PHASE-DEPLOYMENT-003-mcp-expansion.

Show inter-project dependencies.

Author: CORTEX Framework
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class DependencyGraph:
    """MCP tool for building project dependency graphs.

    Analyzes inter-project dependencies and detects cycles.
    """

    def __init__(self, base_path: str = "D:\\PROJECTS"):
        """Initialize dependency graph.

        Args:
            base_path: Base path containing projects.
        """
        self.base_path = base_path

    def build(self, projects: List[str]) -> Dict[str, Any]:
        """Build dependency graph for projects.

        Args:
            projects: List of project names to analyze.

        Returns:
            Dependency graph with nodes, edges, cycles, build order.
        """
        dependencies = self._scan_dependencies(projects)

        # Build nodes and edges
        nodes = list(dependencies.keys())
        edges = []

        for project, deps in dependencies.items():
            for dep in deps:
                edges.append({"from": project, "to": dep})

        # Detect cycles
        cycles = self._detect_cycles(dependencies)
        has_cycles = len(cycles) > 0

        # Calculate build order (topological sort)
        build_order = self._topological_sort(dependencies) if not has_cycles else []

        return {
            "nodes": nodes,
            "edges": edges,
            "has_cycles": has_cycles,
            "cycles": cycles,
            "build_order": build_order,
            "dependency_map": dependencies,
        }

    def _scan_dependencies(self, projects: List[str]) -> Dict[str, List[str]]:
        """Scan project dependencies.

        Args:
            projects: Projects to scan.

        Returns:
            Dictionary mapping project to its dependencies.
        """
        dependencies = {}

        for project in projects:
            project_path = Path(self.base_path) / project
            deps = self._get_project_dependencies(project_path, projects)
            dependencies[project] = deps

        return dependencies

    def _get_project_dependencies(
        self,
        project_path: Path,
        all_projects: List[str],
    ) -> List[str]:
        """Get dependencies for a single project.

        Args:
            project_path: Path to project.
            all_projects: List of all project names.

        Returns:
            List of project dependencies.
        """
        deps = []

        # Check requirements.txt for references to other projects
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            try:
                content = req_file.read_text()
                for proj in all_projects:
                    if proj.lower() in content.lower() and proj != project_path.name:
                        deps.append(proj)
            except Exception:
                pass

        # Check imports in Python files
        try:
            for py_file in project_path.rglob("*.py"):
                try:
                    content = py_file.read_text(errors="ignore")
                    for proj in all_projects:
                        if f"from {proj.lower()}" in content.lower() or \
                           f"import {proj.lower()}" in content.lower():
                            if proj != project_path.name and proj not in deps:
                                deps.append(proj)
                except Exception:
                    continue
        except Exception:
            pass

        return deps

    def _detect_cycles(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies.

        Args:
            dependencies: Dependency map.

        Returns:
            List of cycles found.
        """
        cycles = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    cycle = dfs(neighbor, path.copy())
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            rec_stack.remove(node)
            return None

        for node in dependencies:
            if node not in visited:
                cycle = dfs(node, [])
                if cycle:
                    cycles.append(cycle)

        return cycles

    def _topological_sort(self, dependencies: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort for build order.

        Args:
            dependencies: Dependency map.

        Returns:
            Build order (dependencies first).
        """
        in_degree = {node: 0 for node in dependencies}

        for deps in dependencies.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1

        # Find nodes with no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for dep in dependencies.get(node, []):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

        # Reverse to get dependencies first
        return result[::-1]


__all__ = ["DependencyGraph"]
