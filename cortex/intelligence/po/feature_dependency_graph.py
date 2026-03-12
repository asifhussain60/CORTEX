"""Feature Dependency Graph — builds a D3.js-compatible adjacency graph (GAP-129-11)."""

from __future__ import annotations

from typing import Any, Dict, List, Set


class FeatureDependencyGraph:
    """Converts a flat feature list with ``depends_on`` metadata into D3 graph JSON.

    Output schema:
    {
        "nodes": [{"id": str, "name": str}],
        "links": [{"source": str, "target": str}]
    }
    """

    def build(self, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build D3-compatible dependency graph.

        Each feature dict may have:
        - ``id``         — unique identifier (required)
        - ``name``       — display name (defaults to id)
        - ``depends_on`` — list of feature IDs this feature depends on

        Args:
            features: List of feature descriptors.

        Returns:
            D3-compatible dict with ``nodes`` and ``links`` keys.
        """
        node_ids: Set[str] = set()
        nodes: List[Dict[str, str]] = []
        links: List[Dict[str, str]] = []

        for feat in features:
            fid = str(feat.get("id", ""))
            fname = str(feat.get("name", fid))
            if fid and fid not in node_ids:
                nodes.append({"id": fid, "name": fname})
                node_ids.add(fid)

        for feat in features:
            fid = str(feat.get("id", ""))
            deps = feat.get("depends_on", []) or []
            if isinstance(deps, str):
                deps = [deps]
            for dep in deps:
                dep_str = str(dep)
                # Add dependency as a node if not already present
                if dep_str and dep_str not in node_ids:
                    nodes.append({"id": dep_str, "name": dep_str})
                    node_ids.add(dep_str)
                if fid and dep_str:
                    links.append({"source": dep_str, "target": fid})

        return {"nodes": nodes, "links": links}

    def critical_path(self, features: List[Dict[str, Any]]) -> List[str]:
        """Return a topologically sorted list of feature IDs (longest dependency chain first).

        Uses Kahn's algorithm for topological sort.
        """
        from collections import deque

        adj: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}

        for feat in features:
            fid = str(feat.get("id", ""))
            if fid:
                adj.setdefault(fid, set())
                in_degree.setdefault(fid, 0)
                for dep in feat.get("depends_on", []) or []:
                    dep_str = str(dep)
                    adj.setdefault(dep_str, set())
                    adj[dep_str].add(fid)
                    in_degree[fid] = in_degree.get(fid, 0) + 1
                    in_degree.setdefault(dep_str, 0)

        queue = deque(k for k, v in in_degree.items() if v == 0)
        order: List[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in sorted(adj.get(node, [])):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return order
