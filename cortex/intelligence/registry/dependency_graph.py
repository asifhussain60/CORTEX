"""
DependencyGraphBuilder — builds a global dependency DAG from registry models.

Transforms resolved registry models into a JSON-serializable graph structure
with nodes (one per artifact) and edges (from ``references.outgoing``).
Produces ``registry-graph.json`` for the D3.js graph explorer.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


class DependencyGraphBuilder:
    """Builds a dependency graph from a list of resolved registry models.

    Each model becomes a node; each outgoing reference becomes a directed edge.
    The graph is JSON-serializable for the D3.js graph explorer.
    """

    def build(self, models: List[BaseRegistryModel]) -> Dict[str, Any]:
        """Build a graph from resolved models.

        Args:
            models: Registry models with populated ``references``.

        Returns:
            A dict with ``nodes`` and ``edges`` lists.
        """
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, str]] = []
        node_ids: set = set()

        for m in models:
            if m.id not in node_ids:
                nodes.append({
                    "id": m.id,
                    "type": m.type,
                    "title": m.title,
                    "source_file": m.source_file,
                })
                node_ids.add(m.id)

            for ref in m.references.get("outgoing", []):
                edges.append({
                    "source": m.id,
                    "target": ref["target_id"],
                    "ref_type": ref.get("ref_type", "unknown"),
                })

        return {"nodes": nodes, "edges": edges}

    def to_json(self, graph: Dict[str, Any]) -> str:
        """Serialize the graph to deterministic JSON.

        Args:
            graph: The graph dict from :meth:`build`.

        Returns:
            A JSON string with sorted keys and 2-space indent.
        """
        return json.dumps(graph, sort_keys=True, indent=2, ensure_ascii=False)

    def stats(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Return summary statistics for the graph.

        Args:
            graph: The graph dict from :meth:`build`.

        Returns:
            A dict with ``node_count``, ``edge_count``, and ``types`` breakdown.
        """
        type_counts: Dict[str, int] = {}
        for node in graph.get("nodes", []):
            t = node.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "node_count": len(graph.get("nodes", [])),
            "edge_count": len(graph.get("edges", [])),
            "types": type_counts,
        }
