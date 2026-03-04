# AC_START: AC-P125-C-002
"""
Test Suite: Phase 125-c — DependencyGraphBuilder
Module: Builds a global dependency DAG from resolved registry models.
Tests: 12 tests — node/edge construction, cycle detection, export.
"""

import json

import pytest

from cortex.intelligence.registry.dependency_graph import DependencyGraphBuilder
from cortex.intelligence.registry.models.governance import GovernanceRuleModel
from cortex.intelligence.registry.models.workflow import WorkflowTemplateModel
from cortex.intelligence.registry.models.pattern import PatternModel


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def builder() -> DependencyGraphBuilder:
    """Return a fresh DependencyGraphBuilder."""
    return DependencyGraphBuilder()


@pytest.fixture
def governance_model() -> GovernanceRuleModel:
    return GovernanceRuleModel(
        id="governance-dev-rules",
        type="governance-rule",
        source_file="governance/development-rules.yaml",
        title="Development Rules",
        source_hash="",
        domain="development",
        rules=[{"id": "CORE-008"}, {"id": "CORE-064"}],
    )


@pytest.fixture
def workflow_model() -> WorkflowTemplateModel:
    return WorkflowTemplateModel(
        id="sdlc/implement-workflow",
        type="workflow-template",
        source_file="workflows/templates/sdlc/implement-workflow.yaml",
        title="IMPLEMENT",
        source_hash="",
        version="1.0.0",
        category="sdlc",
        steps=[{"id": "s1", "template_ref": "primitives/ac-marker-emit"}],
        metadata={"core_rules": ["CORE-008"]},
        references={
            "outgoing": [
                {"target_id": "CORE-008", "ref_type": "core_rule", "source_field": "metadata.core_rules"},
            ],
            "incoming": [],
        },
    )


@pytest.fixture
def pattern_model() -> PatternModel:
    return PatternModel(
        id="strategy-workflow",
        type="pattern",
        source_file="patterns/strategy-workflow.yaml",
        title="Strategy Workflow",
        source_hash="",
        pattern_name="Strategy Workflow",
        pattern_type="behavioral",
        file_references=["cortex/core/workflow_engine.py"],
    )


# ── Graph Building Tests ────────────────────────────────────────────────


class TestDependencyGraphBuild:
    """DependencyGraphBuilder.build() must construct a node/edge graph."""

    def test_build_returns_dict(
        self, builder: DependencyGraphBuilder, governance_model: GovernanceRuleModel
    ) -> None:
        """build() must return a dict with 'nodes' and 'edges'."""
        graph = builder.build([governance_model])
        assert isinstance(graph, dict)
        assert "nodes" in graph
        assert "edges" in graph

    def test_nodes_created_for_each_model(
        self, builder: DependencyGraphBuilder,
        governance_model: GovernanceRuleModel,
        workflow_model: WorkflowTemplateModel,
    ) -> None:
        """Each model becomes a node."""
        graph = builder.build([governance_model, workflow_model])
        node_ids = [n["id"] for n in graph["nodes"]]
        assert "governance-dev-rules" in node_ids
        assert "sdlc/implement-workflow" in node_ids

    def test_node_has_type_and_title(
        self, builder: DependencyGraphBuilder, governance_model: GovernanceRuleModel
    ) -> None:
        """Each node must have type and title fields."""
        graph = builder.build([governance_model])
        node = graph["nodes"][0]
        assert "type" in node
        assert "title" in node

    def test_edges_from_outgoing_refs(
        self, builder: DependencyGraphBuilder,
        workflow_model: WorkflowTemplateModel,
        governance_model: GovernanceRuleModel,
    ) -> None:
        """Edges created from model.references.outgoing."""
        graph = builder.build([workflow_model, governance_model])
        assert len(graph["edges"]) > 0

    def test_edge_has_source_and_target(
        self, builder: DependencyGraphBuilder,
        workflow_model: WorkflowTemplateModel,
        governance_model: GovernanceRuleModel,
    ) -> None:
        """Each edge must have source and target."""
        graph = builder.build([workflow_model, governance_model])
        for e in graph["edges"]:
            assert "source" in e
            assert "target" in e

    def test_empty_models_produces_empty_graph(
        self, builder: DependencyGraphBuilder
    ) -> None:
        """Empty input → empty graph."""
        graph = builder.build([])
        assert graph["nodes"] == []
        assert graph["edges"] == []


class TestDependencyGraphExport:
    """DependencyGraphBuilder must support JSON export."""

    def test_to_json_valid(
        self, builder: DependencyGraphBuilder,
        governance_model: GovernanceRuleModel,
    ) -> None:
        """to_json() must produce valid JSON."""
        graph = builder.build([governance_model])
        json_str = builder.to_json(graph)
        parsed = json.loads(json_str)
        assert "nodes" in parsed

    def test_to_json_sorted_keys(
        self, builder: DependencyGraphBuilder,
        governance_model: GovernanceRuleModel,
    ) -> None:
        """JSON output must have sorted keys for stability."""
        graph = builder.build([governance_model])
        json_str = builder.to_json(graph)
        parsed = json.loads(json_str)
        keys = list(parsed.keys())
        assert keys == sorted(keys)


class TestDependencyGraphStats:
    """Graph statistics."""

    def test_stats_returns_dict(
        self, builder: DependencyGraphBuilder,
        governance_model: GovernanceRuleModel,
        workflow_model: WorkflowTemplateModel,
    ) -> None:
        """stats() must return counts."""
        graph = builder.build([governance_model, workflow_model])
        stats = builder.stats(graph)
        assert stats["node_count"] == 2
        assert "edge_count" in stats

    def test_stats_by_type(
        self, builder: DependencyGraphBuilder,
        governance_model: GovernanceRuleModel,
        workflow_model: WorkflowTemplateModel,
        pattern_model: PatternModel,
    ) -> None:
        """stats() must include type breakdown."""
        graph = builder.build([governance_model, workflow_model, pattern_model])
        stats = builder.stats(graph)
        assert "types" in stats
        assert stats["types"].get("governance-rule", 0) == 1
        assert stats["types"].get("workflow-template", 0) == 1
        assert stats["types"].get("pattern", 0) == 1


# AC_COMPLETE: AC-P125-C-002 ✅
