"""Dependency graph generator for orchestrator mesh analysis.

Phase 48 S2: Builds and analyzes the orchestrator dependency graph.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml


class DependencyType(str, Enum):
    """Types of dependencies between orchestrators."""

    DIRECT = "direct"  # A directly depends on B
    INDIRECT = "indirect"  # A depends on B transitively
    CIRCULAR = "circular"  # A and B have circular dependency


@dataclass
class DependencyNode:
    """Node in the dependency graph."""

    name: str
    tier: str  # core, domain, support
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    health_check: Optional[str] = None


@dataclass
class DependencyGraph:
    """Complete orchestrator dependency graph."""

    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    cycles: List[List[str]] = field(default_factory=list)
    orphans: List[str] = field(default_factory=list)
    total_edges: int = 0

    def add_node(self, node: DependencyNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.name] = node

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add an edge (dependency) to the graph."""
        if from_node in self.nodes and to_node in self.nodes:
            if to_node not in self.nodes[from_node].dependencies:
                self.nodes[from_node].dependencies.append(to_node)
                self.nodes[to_node].dependents.append(from_node)
                self.total_edges += 1

    def find_impact_radius(self, node_name: str) -> Set[str]:
        """Find all nodes affected by changes to the given node.

        Args:
            node_name: Name of the node to analyze

        Returns:
            Set of all dependent nodes (directly and transitively).
        """
        if node_name not in self.nodes:
            return set()

        visited = set()
        stack = [node_name]

        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                if current in self.nodes:
                    stack.extend(self.nodes[current].dependents)

        visited.discard(node_name)  # Don't include the node itself
        return visited

    def get_transitive_dependencies(self, node_name: str) -> Set[str]:
        """Get all transitive dependencies of a node.

        Args:
            node_name: Name of the node to analyze

        Returns:
            Set of all nodes this node depends on.
        """
        if node_name not in self.nodes:
            return set()

        visited = set()
        stack = [node_name]

        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                if current in self.nodes:
                    stack.extend(self.nodes[current].dependencies)

        visited.discard(node_name)
        return visited


class DependencyGraphGenerator:
    """Generator for orchestrator dependency graphs.

    Analyzes wiring.yaml to build and validate the orchestrator mesh.
    """

    def __init__(self, wiring_path: Optional[Path] = None):
        """Initialize the graph generator.

        Args:
            wiring_path: Path to wiring.yaml file

        Raises:
            ValueError: If wiring file not found.
        """
        if wiring_path is None:
            wiring_path = (
                Path(__file__).parents[2] / "wiring" / "specifications" / "wiring.yaml"
            )

        if not wiring_path.exists():
            raise ValueError(f"Wiring specification not found: {wiring_path}")

        self.wiring_path = wiring_path
        self.wiring_data: Dict = {}
        self._load_wiring()

    def _load_wiring(self) -> None:
        """Load wiring specification.

        Raises:
            ValueError: If YAML parsing fails.
        """
        try:
            with open(self.wiring_path) as f:
                self.wiring_data = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load wiring specification: {e}")

    def generate(self) -> DependencyGraph:
        """Generate the dependency graph.

        Returns:
            DependencyGraph with all orchestrators and dependencies.
        """
        graph = DependencyGraph()

        # Load all orchestrators
        for tier in ["core", "domain", "support"]:
            for orch in self.wiring_data.get("orchestrators", {}).get(tier, []):
                node = DependencyNode(
                    name=orch["name"],
                    tier=tier,
                    dependencies=orch.get("dependencies", []),
                    health_check=orch.get("health_check"),
                )
                graph.add_node(node)

        # Build edges
        for tier in ["core", "domain", "support"]:
            for orch in self.wiring_data.get("orchestrators", {}).get(tier, []):
                for dep in orch.get("dependencies", []):
                    graph.add_edge(orch["name"], dep)

        # Detect cycles
        graph.cycles = self._detect_cycles(graph)

        # Detect orphans
        graph.orphans = self._detect_orphans(graph)

        return graph

    def _detect_cycles(self, graph: DependencyGraph) -> List[List[str]]:
        """Detect circular dependencies.

        Args:
            graph: DependencyGraph to analyze

        Returns:
            List of cycles found (each cycle is a list of nodes).
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []

        def dfs(node: str, path: List[str]) -> None:
            """DFS to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            node_obj = graph.nodes.get(node)
            if node_obj:
                for neighbor in node_obj.dependencies:
                    if neighbor not in visited:
                        dfs(neighbor, path)
                    elif neighbor in rec_stack:
                        # Found cycle
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node_name in graph.nodes:
            if node_name not in visited:
                dfs(node_name, [])

        return cycles

    def _detect_orphans(self, graph: DependencyGraph) -> List[str]:
        """Detect orchestrators with no dependents.

        Args:
            graph: DependencyGraph to analyze

        Returns:
            List of orphan node names.
        """
        orphans = []

        for node_name, node in graph.nodes.items():
            if not node.dependents and node.tier == "support":
                # It's ok for support tier to have no dependents
                pass
            elif not node.dependents and node.tier in ["core", "domain"]:
                # Core/domain should generally have dependents
                orphans.append(node_name)

        return orphans

    def analyze_change_impact(self, changed_orchestrator: str, graph: DependencyGraph) -> Dict:
        """Analyze impact of changes to an orchestrator.

        Args:
            changed_orchestrator: Name of changed orchestrator
            graph: DependencyGraph to analyze

        Returns:
            Dict with impact analysis details.
        """
        if changed_orchestrator not in graph.nodes:
            return {"error": f"Orchestrator {changed_orchestrator} not found"}

        impact_radius = graph.find_impact_radius(changed_orchestrator)
        dependencies = graph.get_transitive_dependencies(changed_orchestrator)

        return {
            "orchestrator": changed_orchestrator,
            "direct_dependents": graph.nodes[changed_orchestrator].dependents,
            "impact_radius": list(impact_radius),
            "impact_count": len(impact_radius),
            "transitive_dependencies": list(dependencies),
            "dependency_count": len(dependencies),
            "in_cycle": any(
                changed_orchestrator in cycle for cycle in graph.cycles
            ),
        }

    def get_dependency_metrics(self, graph: DependencyGraph) -> Dict:
        """Get metrics about the dependency graph.

        Args:
            graph: DependencyGraph to analyze

        Returns:
            Dict with dependency metrics.
        """
        tier_counts = {"core": 0, "domain": 0, "support": 0}
        for node in graph.nodes.values():
            tier_counts[node.tier] += 1

        avg_dependencies = 0
        if graph.nodes:
            total_deps = sum(len(n.dependencies) for n in graph.nodes.values())
            avg_dependencies = total_deps / len(graph.nodes)

        return {
            "total_orchestrators": len(graph.nodes),
            "total_edges": graph.total_edges,
            "tier_distribution": tier_counts,
            "avg_dependencies": round(avg_dependencies, 2),
            "cycles_detected": len(graph.cycles),
            "orphans_detected": len(graph.orphans),
            "orphan_list": graph.orphans,
        }

    def visualize_graph_text(self, graph: DependencyGraph) -> str:
        """Generate text visualization of the dependency graph.

        Args:
            graph: DependencyGraph to visualize

        Returns:
            Text representation of the graph.
        """
        lines = ["Orchestrator Dependency Graph", "=" * 50]

        # Group by tier
        for tier in ["core", "domain", "support"]:
            tier_nodes = [n for n in graph.nodes.values() if n.tier == tier]
            if tier_nodes:
                lines.append(f"\n{tier.upper()} ({len(tier_nodes)} orchestrators)")
                lines.append("-" * 40)

                for node in tier_nodes:
                    if node.dependencies:
                        lines.append(
                            f"  {node.name} → {', '.join(node.dependencies)}"
                        )
                    else:
                        lines.append(f"  {node.name} (no dependencies)")

        if graph.cycles:
            lines.append(f"\n⚠️  CYCLES DETECTED ({len(graph.cycles)})")
            lines.append("-" * 40)
            for cycle in graph.cycles:
                lines.append(f"  {' → '.join(cycle)}")

        if graph.orphans:
            lines.append(f"\n⚠️  ORPHANS ({len(graph.orphans)})")
            lines.append("-" * 40)
            for orphan in graph.orphans:
                lines.append(f"  {orphan}")

        return "\n".join(lines)
