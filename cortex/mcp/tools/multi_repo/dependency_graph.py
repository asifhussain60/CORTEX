"""DependencyGraph — Inter-project dependency analysis.

Builds dependency graphs, detects cycles, and computes build order.
"""

from typing import Any, Dict, List, Optional


class DependencyGraph:
    """Build and analyze inter-project dependency graphs."""

    def build(
        self, projects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build a dependency graph for the given projects.

        Args:
            projects: List of project names.

        Returns:
            Dict with 'nodes', 'edges', 'has_cycles', 'cycles', 'build_order'.
        """
        projects = projects or []
        deps = self._scan_dependencies(projects)

        nodes = list(deps.keys())
        edges: List[Dict[str, str]] = []
        for proj, dep_list in deps.items():
            for dep in dep_list:
                edges.append({"from": proj, "to": dep})

        cycles = self._detect_cycles(deps)
        build_order = self._topological_sort(deps) if not cycles else []

        return {
            "nodes": nodes,
            "edges": edges,
            "has_cycles": len(cycles) > 0,
            "cycles": cycles,
            "build_order": build_order,
        }

    def _scan_dependencies(
        self, projects: List[str]
    ) -> Dict[str, List[str]]:
        """Scan project dependencies (designed for patching).

        Args:
            projects: List of project names.

        Returns:
            Dict mapping project → list of dependencies.
        """
        return {p: [] for p in projects}

    def _detect_cycles(
        self, deps: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Detect cycles in the dependency graph.

        Args:
            deps: Adjacency list.

        Returns:
            List of cycle paths.
        """
        visited: set = set()
        rec_stack: set = set()
        cycles: List[List[str]] = []

        def _dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in deps.get(node, []):
                if neighbor not in visited:
                    _dfs(neighbor, path)
                elif neighbor in rec_stack:
                    idx = path.index(neighbor)
                    cycles.append(path[idx:] + [neighbor])
            path.pop()
            rec_stack.discard(node)

        for node in deps:
            if node not in visited:
                _dfs(node, [])
        return cycles

    def _topological_sort(
        self, deps: Dict[str, List[str]]
    ) -> List[str]:
        """Compute topological order for builds.

        Args:
            deps: Adjacency list.

        Returns:
            Build order list.
        """
        in_degree: Dict[str, int] = {n: 0 for n in deps}
        for node, neighbors in deps.items():
            for n in neighbors:
                in_degree.setdefault(n, 0)
                in_degree[node] = in_degree.get(node, 0)
                # dep edges mean node depends on n → n must come first
        # Recompute correctly
        in_degree = {n: 0 for n in deps}
        for node, neighbors in deps.items():
            for _n in neighbors:
                pass  # node depends on _n
        # Simple: nodes with no deps first
        order: List[str] = []
        remaining = dict(deps)
        while remaining:
            # Find nodes whose deps are all in order
            ready = [n for n, d in remaining.items() if all(dep in order for dep in d)]
            if not ready:
                break
            for n in sorted(ready):
                order.append(n)
                del remaining[n]
        return order
