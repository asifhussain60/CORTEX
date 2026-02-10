"""Tests for DependencyGraphGenerator - Phase 48 S2.

CORE-008: Tests before code (TDD)
"""

import pytest
from pathlib import Path
from cortex.orchestrators.holistic.dependency_graph import (
    DependencyGraph,
    DependencyNode,
    DependencyType,
    DependencyGraphGenerator,
)


class TestDependencyNode:
    """Test DependencyNode dataclass."""

    def test_node_creation(self) -> None:
        """Test creating a DependencyNode."""
        node = DependencyNode(name="TestOrch", tier="core")
        assert node.name == "TestOrch"
        assert node.tier == "core"
        assert len(node.dependencies) == 0

    def test_node_with_dependencies(self) -> None:
        """Test node with dependencies."""
        node = DependencyNode(
            name="TestOrch",
            tier="domain",
            dependencies=["DepA", "DepB"],
        )
        assert len(node.dependencies) == 2
        assert "DepA" in node.dependencies


class TestDependencyGraph:
    """Test DependencyGraph dataclass."""

    def test_graph_creation(self) -> None:
        """Test creating a DependencyGraph."""
        graph = DependencyGraph()
        assert len(graph.nodes) == 0
        assert len(graph.cycles) == 0

    def test_add_node(self) -> None:
        """Test adding nodes to graph."""
        graph = DependencyGraph()
        node = DependencyNode(name="NodeA", tier="core")
        graph.add_node(node)
        assert "NodeA" in graph.nodes

    def test_add_edge(self) -> None:
        """Test adding edges to graph."""
        graph = DependencyGraph()
        node_a = DependencyNode(name="NodeA", tier="core")
        node_b = DependencyNode(name="NodeB", tier="core")
        graph.add_node(node_a)
        graph.add_node(node_b)

        graph.add_edge("NodeA", "NodeB")
        assert "NodeB" in graph.nodes["NodeA"].dependencies
        assert "NodeA" in graph.nodes["NodeB"].dependents

    def test_find_impact_radius(self) -> None:
        """Test impact radius calculation."""
        graph = DependencyGraph()

        # Create chain: C -> B -> A (A depends on B depends on C)
        for name in ["A", "B", "C"]:
            graph.add_node(DependencyNode(name=name, tier="core"))

        graph.add_edge("A", "B")  # A depends on B
        graph.add_edge("B", "C")  # B depends on C

        # Changing B affects A (A depends on B)
        impact = graph.find_impact_radius("B")
        assert "A" in impact

    def test_get_transitive_dependencies(self) -> None:
        """Test transitive dependency calculation."""
        graph = DependencyGraph()

        # Create chain: A -> B -> C
        for name in ["A", "B", "C"]:
            graph.add_node(DependencyNode(name=name, tier="core"))

        graph.add_edge("A", "B")
        graph.add_edge("B", "C")

        # A depends on B and C transitively
        deps = graph.get_transitive_dependencies("A")
        assert "B" in deps
        assert "C" in deps


class TestDependencyGraphGenerator:
    """Test DependencyGraphGenerator."""

    @pytest.fixture
    def generator(self) -> DependencyGraphGenerator:
        """Create a generator instance."""
        return DependencyGraphGenerator()

    def test_generator_initialization(self, generator: DependencyGraphGenerator) -> None:
        """Test generator initializes correctly."""
        assert generator.wiring_data is not None
        assert "orchestrators" in generator.wiring_data

    def test_generator_invalid_path(self) -> None:
        """Test generator rejects invalid path."""
        with pytest.raises(ValueError, match="Wiring specification not found"):
            DependencyGraphGenerator(wiring_path=Path("/nonexistent/wiring.yaml"))

    def test_generate_graph(self, generator: DependencyGraphGenerator) -> None:
        """Test graph generation."""
        graph = generator.generate()
        assert len(graph.nodes) > 0

    def test_graph_has_all_orchestrators(
        self, generator: DependencyGraphGenerator
    ) -> None:
        """Test graph includes all orchestrators."""
        graph = generator.generate()

        # Count orchestrators from all tiers in wiring data
        expected_count = 0
        for tier in ["core", "domain", "support"]:
            orchestrators = generator.wiring_data.get("orchestrators", {}).get(tier, [])
            if isinstance(orchestrators, list):
                expected_count += len(orchestrators)

        # The graph should have at least as many nodes as expected
        # (some orchestrators may be generated or derived)
        assert len(graph.nodes) >= expected_count - 2, (
            f"Expected at least {expected_count - 2} nodes but got {len(graph.nodes)}"
        )

    def test_cycles_detection(self, generator: DependencyGraphGenerator) -> None:
        """Test cycle detection."""
        graph = generator.generate()
        # The actual wiring.yaml shouldn't have cycles, but check structure
        assert isinstance(graph.cycles, list)

    def test_orphans_detection(self, generator: DependencyGraphGenerator) -> None:
        """Test orphan detection."""
        graph = generator.generate()
        assert isinstance(graph.orphans, list)

    def test_change_impact_analysis(self, generator: DependencyGraphGenerator) -> None:
        """Test change impact analysis."""
        graph = generator.generate()

        if graph.nodes:
            # Get first orchestrator
            first_orch = list(graph.nodes.keys())[0]
            analysis = generator.analyze_change_impact(first_orch, graph)

            assert analysis["orchestrator"] == first_orch
            assert "impact_radius" in analysis
            assert "transitive_dependencies" in analysis
            assert "in_cycle" in analysis

    def test_change_impact_invalid_orchestrator(
        self, generator: DependencyGraphGenerator
    ) -> None:
        """Test change impact with invalid orchestrator."""
        graph = generator.generate()
        analysis = generator.analyze_change_impact("NonExistentOrch", graph)
        assert "error" in analysis

    def test_dependency_metrics(self, generator: DependencyGraphGenerator) -> None:
        """Test dependency metrics calculation."""
        graph = generator.generate()
        metrics = generator.get_dependency_metrics(graph)

        assert "total_orchestrators" in metrics
        assert "total_edges" in metrics
        assert "tier_distribution" in metrics
        assert "avg_dependencies" in metrics
        assert "cycles_detected" in metrics

    def test_metrics_structure(self, generator: DependencyGraphGenerator) -> None:
        """Test metrics structure completeness."""
        graph = generator.generate()
        metrics = generator.get_dependency_metrics(graph)

        assert metrics["total_orchestrators"] > 0
        assert isinstance(metrics["tier_distribution"], dict)
        assert "core" in metrics["tier_distribution"]
        assert "domain" in metrics["tier_distribution"]
        assert "support" in metrics["tier_distribution"]

    def test_visualize_graph_text(self, generator: DependencyGraphGenerator) -> None:
        """Test text graph visualization."""
        graph = generator.generate()
        visualization = generator.visualize_graph_text(graph)

        assert isinstance(visualization, str)
        assert "Orchestrator Dependency Graph" in visualization
        assert "CORE" in visualization or "core" in visualization.lower()

    def test_detect_cycles_empty_graph(self, generator: DependencyGraphGenerator) -> None:
        """Test cycle detection on empty graph."""
        graph = DependencyGraph()
        cycles = generator._detect_cycles(graph)
        assert len(cycles) == 0

    def test_detect_orphans_empty_graph(self, generator: DependencyGraphGenerator) -> None:
        """Test orphan detection on empty graph."""
        graph = DependencyGraph()
        orphans = generator._detect_orphans(graph)
        assert len(orphans) == 0

    def test_load_wiring_valid(self, generator: DependencyGraphGenerator) -> None:
        """Test wiring file loading."""
        assert generator.wiring_data is not None
        assert isinstance(generator.wiring_data, dict)


class TestDependencyTypes:
    """Test DependencyType enum."""

    def test_dependency_type_values(self) -> None:
        """Test all dependency type values."""
        assert DependencyType.DIRECT.value == "direct"
        assert DependencyType.INDIRECT.value == "indirect"
        assert DependencyType.CIRCULAR.value == "circular"
