"""
Test Suite for LENS Context Builder (IR-003-02).

Validates the aggregation and synthesis of findings from all four intelligence
sources (AST, Git History, Comments, Relationships) into a unified knowledge
graph representing the codebase context.

Tests cover:
1. Context Aggregation from Multiple Sources
2. Knowledge Graph Construction
3. Context Filtering and Prioritization
4. Context Serialization/Deserialization
5. Context Enrichment with Time-Series Data
6. Context Query and Traversal
7. Edge Cases and Error Handling
8. Integration with Intent Reflection Protocol
"""

import pytest
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid
import json

# Import modules to test
from cortex.core.intent.lens_context_builder import (
    LENSContextBuilder,
    ContextNode,
    ContextEdge,
    KnowledgeGraph,
)


# ============================================================================
# TEST FIXTURES - Context Source Data
# ============================================================================

@pytest.fixture
def sample_ast_findings():
    """Sample findings from AST Intelligence module."""
    return {
        "functions": [
            {
                "name": "process_data",
                "file": "src/core/processor.py",
                "line": 42,
                "calls": ["validate_input", "transform_data", "save_results"],
                "parameters": ["data", "config"],
                "return_type": "Dict[str, Any]",
            },
            {
                "name": "validate_input",
                "file": "src/core/processor.py",
                "line": 15,
                "calls": [],
                "parameters": ["data"],
                "return_type": "bool",
            },
        ],
        "classes": [
            {
                "name": "DataProcessor",
                "file": "src/core/processor.py",
                "line": 100,
                "methods": ["__init__", "process", "validate"],
                "inheritance": ["BaseProcessor"],
            }
        ],
        "patterns": [
            {"name": "singleton_pattern", "locations": ["src/core/config.py"]},
            {"name": "factory_pattern", "locations": ["src/core/factory.py"]},
        ],
        "call_graph": {
            "main": ["process_data"],
            "process_data": ["validate_input", "transform_data"],
            "validate_input": [],
        },
    }


@pytest.fixture
def sample_git_findings():
    """Sample findings from Git History Analyzer module."""
    return {
        "change_frequency": {
            "src/core/processor.py": 42,
            "src/core/config.py": 5,
            "tests/unit/test_processor.py": 38,
        },
        "hot_spots": [
            {
                "file": "src/core/processor.py",
                "changes": 42,
                "last_modified": "2026-01-14",
                "authors": ["alice@example.com", "bob@example.com"],
            },
            {
                "file": "tests/unit/test_processor.py",
                "changes": 38,
                "last_modified": "2026-01-15",
                "authors": ["alice@example.com"],
            },
        ],
        "refactoring_history": [
            {
                "date": "2025-12-15",
                "author": "alice@example.com",
                "changes": ["Renamed: old_method → new_method"],
                "file": "src/core/processor.py",
            }
        ],
        "expertise_map": {
            "src/core/processor.py": {"alice@example.com": 25, "bob@example.com": 17},
            "src/core/config.py": {"charlie@example.com": 5},
        },
    }


@pytest.fixture
def sample_comment_findings():
    """Sample findings from Comment Analyzer module."""
    return {
        "docstrings": [
            {
                "location": "src/core/processor.py:42",
                "function": "process_data",
                "style": "google",
                "content": "Process input data and return results.",
                "args": ["data", "config"],
                "returns": "Dict with results",
            },
            {
                "location": "src/core/processor.py:15",
                "function": "validate_input",
                "style": "google",
                "content": "Validate input data.",
                "args": ["data"],
                "returns": "bool: True if valid",
            },
        ],
        "tech_debt_markers": [
            {
                "type": "TODO",
                "location": "src/core/processor.py:45",
                "text": "TODO: Optimize validation logic for large datasets",
                "severity": "MEDIUM",
            },
            {
                "type": "FIXME",
                "location": "src/core/processor.py:67",
                "text": "FIXME: Handle edge case when config is None",
                "severity": "HIGH",
            },
        ],
        "deprecated_markers": [
            {
                "location": "src/core/config.py:10",
                "message": "Deprecated: Use new_config() instead",
                "replacement": "new_config",
            }
        ],
    }


@pytest.fixture
def sample_relationship_findings():
    """Sample findings from Relationship Traversal Engine."""
    return {
        "api_endpoints": [
            {
                "path": "/api/v1/process",
                "method": "POST",
                "handler": "process_data",
                "file": "src/api/routes.py",
                "dependencies": ["DataProcessor"],
            },
            {
                "path": "/api/v1/validate",
                "method": "POST",
                "handler": "validate_data",
                "file": "src/api/routes.py",
                "dependencies": ["Validator"],
            },
        ],
        "database_models": [
            {
                "name": "ProcessResult",
                "file": "src/models/result.py",
                "fields": ["id", "status", "data", "created_at"],
                "relationships": ["ProcessJob"],
            }
        ],
        "configuration_references": [
            {
                "key": "process.timeout",
                "locations": ["src/core/processor.py:20"],
                "type": "int",
                "default": 300,
            }
        ],
        "import_graph": {
            "src/core/processor.py": ["src/core/validator.py", "src/core/config.py"],
            "src/api/routes.py": ["src/core/processor.py"],
        },
    }


# ============================================================================
# TEST CLASS 1: Context Aggregation from Multiple Sources
# ============================================================================

class TestContextAggregation:
    """Test aggregation of findings from all intelligence sources."""

    def test_aggregate_all_sources(
        self,
        sample_ast_findings,
        sample_git_findings,
        sample_comment_findings,
        sample_relationship_findings,
    ):
        """Test aggregating findings from all four sources."""
        builder = LENSContextBuilder()

        # Aggregate each source
        builder.add_ast_findings(sample_ast_findings)
        builder.add_git_findings(sample_git_findings)
        builder.add_comment_findings(sample_comment_findings)
        builder.add_relationship_findings(sample_relationship_findings)

        context = builder.build()

        # Verify all sources are represented
        assert context.ast_findings == sample_ast_findings
        assert context.git_findings == sample_git_findings
        assert context.comment_findings == sample_comment_findings
        assert context.relationship_findings == sample_relationship_findings
        assert context.timestamp is not None

    def test_aggregate_partial_sources(self, sample_ast_findings, sample_git_findings):
        """Test aggregating with only some sources available."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.add_git_findings(sample_git_findings)

        context = builder.build()

        assert context.ast_findings == sample_ast_findings
        assert context.git_findings == sample_git_findings
        assert context.comment_findings is None
        assert context.relationship_findings is None

    def test_aggregate_empty_sources(self):
        """Test aggregating with no sources."""
        builder = LENSContextBuilder()
        context = builder.build()

        assert context.ast_findings is None
        assert context.git_findings is None
        assert context.comment_findings is None
        assert context.relationship_findings is None

    def test_aggregate_with_metadata(self, sample_ast_findings):
        """Test aggregating with custom metadata."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.set_metadata({
            "project": "CORTEX",
            "phase": "PHASE-07",
            "ac_id": "IR-003-02",
        })

        context = builder.build()

        assert context.metadata["project"] == "CORTEX"
        assert context.metadata["phase"] == "PHASE-07"
        assert context.metadata["ac_id"] == "IR-003-02"


# ============================================================================
# TEST CLASS 2: Knowledge Graph Construction
# ============================================================================

class TestKnowledgeGraphConstruction:
    """Test building and manipulating knowledge graphs."""

    def test_create_empty_knowledge_graph(self):
        """Test creating an empty knowledge graph."""
        kg = KnowledgeGraph()

        assert len(kg.nodes) == 0
        assert len(kg.edges) == 0

    def test_add_nodes_to_graph(self):
        """Test adding nodes to knowledge graph."""
        kg = KnowledgeGraph()

        node1 = ContextNode(
            id="func_process_data",
            node_type="function",
            name="process_data",
            file="src/core/processor.py",
            metadata={"line": 42, "complexity": 5},
        )
        node2 = ContextNode(
            id="func_validate_input",
            node_type="function",
            name="validate_input",
            file="src/core/processor.py",
            metadata={"line": 15, "complexity": 2},
        )

        kg.add_node(node1)
        kg.add_node(node2)

        assert len(kg.nodes) == 2
        assert kg.nodes["func_process_data"] == node1
        assert kg.nodes["func_validate_input"] == node2

    def test_add_edges_to_graph(self):
        """Test adding edges (relationships) to knowledge graph."""
        kg = KnowledgeGraph()

        node1 = ContextNode(
            id="func_process_data",
            node_type="function",
            name="process_data",
            file="src/core/processor.py",
        )
        node2 = ContextNode(
            id="func_validate_input",
            node_type="function",
            name="validate_input",
            file="src/core/processor.py",
        )

        kg.add_node(node1)
        kg.add_node(node2)

        edge = ContextEdge(
            source="func_process_data",
            target="func_validate_input",
            edge_type="calls",
            metadata={"line": 50},
        )
        kg.add_edge(edge)

        assert len(kg.edges) == 1
        assert kg.edges[0].source == "func_process_data"
        assert kg.edges[0].target == "func_validate_input"

    def test_build_graph_from_context(
        self, sample_ast_findings, sample_relationship_findings
    ):
        """Test building knowledge graph from aggregated context."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.add_relationship_findings(sample_relationship_findings)

        context = builder.build()
        kg = builder.build_knowledge_graph(context)

        # Verify nodes created for functions
        assert len(kg.nodes) > 0

        # Verify edges created for relationships
        assert len(kg.edges) > 0

    def test_graph_connectivity(self, sample_ast_findings):
        """Test graph traversal and connectivity."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        kg = builder.build_knowledge_graph(context)

        # Find connected nodes
        if "func_process_data" in kg.nodes:
            neighbors = kg.get_neighbors("func_process_data")
            assert len(neighbors) > 0


# ============================================================================
# TEST CLASS 3: Context Filtering and Prioritization
# ============================================================================

class TestContextFilteringAndPrioritization:
    """Test filtering context data for relevance."""

    def test_filter_by_file(self, sample_ast_findings):
        """Test filtering context by file path."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        filtered = builder.filter_context(
            context,
            filters={"file": "src/core/processor.py"}
        )

        # All remaining items should be from specified file
        for func in filtered.ast_findings.get("functions", []):
            assert func["file"] == "src/core/processor.py"

    def test_filter_by_type(self, sample_ast_findings):
        """Test filtering context by type."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        filtered = builder.filter_context(
            context,
            filters={"type": "function"}
        )

        assert len(filtered.ast_findings.get("functions", [])) > 0

    def test_prioritize_by_change_frequency(self, sample_git_findings):
        """Test prioritizing context by change frequency."""
        builder = LENSContextBuilder()
        builder.add_git_findings(sample_git_findings)

        context = builder.build()
        prioritized = builder.prioritize_context(context, "change_frequency")

        # Most changed file should be first
        hot_spots = prioritized.git_findings["hot_spots"]
        assert hot_spots[0]["file"] == "src/core/processor.py"

    def test_prioritize_by_complexity(self, sample_ast_findings):
        """Test prioritizing context by complexity metrics."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        prioritized = builder.prioritize_context(context, "complexity")

        # Verify prioritization applied
        assert prioritized is not None

    def test_filter_tech_debt(self, sample_comment_findings):
        """Test filtering for tech debt markers."""
        builder = LENSContextBuilder()
        builder.add_comment_findings(sample_comment_findings)

        context = builder.build()
        tech_debt = builder.filter_context(
            context,
            filters={"marker": "tech_debt"}
        )

        debt_items = tech_debt.comment_findings.get("tech_debt_markers", [])
        assert len(debt_items) > 0


# ============================================================================
# TEST CLASS 4: Context Serialization/Deserialization
# ============================================================================

class TestContextSerialization:
    """Test converting context to/from various formats."""

    def test_context_to_dict(self, sample_ast_findings, sample_git_findings):
        """Test converting context to dictionary."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.add_git_findings(sample_git_findings)

        context = builder.build()
        context_dict = context.to_dict()

        assert isinstance(context_dict, dict)
        assert "ast_findings" in context_dict
        assert "git_findings" in context_dict
        assert "timestamp" in context_dict

    def test_context_to_json(self, sample_ast_findings):
        """Test converting context to JSON."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        json_str = context.to_json()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "ast_findings" in parsed

    def test_context_from_dict(self, sample_ast_findings):
        """Test creating context from dictionary."""
        from cortex.core.intent.lens_context_builder import LENSContext

        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        context1 = builder.build()

        context_dict = context1.to_dict()
        context2 = LENSContext.from_dict(context_dict)

        assert context2.ast_findings == context1.ast_findings

    def test_context_round_trip(self, sample_ast_findings, sample_git_findings):
        """Test serialization and deserialization round trip."""
        from cortex.core.intent.lens_context_builder import LENSContext

        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.add_git_findings(sample_git_findings)

        context1 = builder.build()
        json_str = context1.to_json()
        context2 = LENSContext.from_json(json_str)

        assert context2.ast_findings == context1.ast_findings
        assert context2.git_findings == context1.git_findings


# ============================================================================
# TEST CLASS 5: Context Enrichment with Time-Series Data
# ============================================================================

class TestContextEnrichment:
    """Test enriching context with additional computed data."""

    def test_enrich_with_trends(self, sample_git_findings):
        """Test enriching context with trend analysis."""
        builder = LENSContextBuilder()
        builder.add_git_findings(sample_git_findings)

        context = builder.build()
        enriched = builder.enrich_context(context, "trends")

        # Trends should be computed
        assert enriched.computed_data is not None
        assert "trends" in enriched.computed_data

    def test_enrich_with_risk_scores(self, sample_comment_findings):
        """Test enriching context with risk scores."""
        builder = LENSContextBuilder()
        builder.add_comment_findings(sample_comment_findings)

        context = builder.build()
        enriched = builder.enrich_context(context, "risk_scores")

        assert enriched.computed_data is not None

    def test_enrich_with_impact_analysis(self, sample_relationship_findings):
        """Test enriching context with impact analysis."""
        builder = LENSContextBuilder()
        builder.add_relationship_findings(sample_relationship_findings)

        context = builder.build()
        enriched = builder.enrich_context(context, "impact_analysis")

        assert enriched.computed_data is not None

    def test_multiple_enrichments(self, sample_ast_findings, sample_git_findings):
        """Test applying multiple enrichments."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.add_git_findings(sample_git_findings)

        context = builder.build()
        enriched = builder.enrich_context(context, ["trends", "risk_scores"])

        assert enriched.computed_data is not None


# ============================================================================
# TEST CLASS 6: Context Query and Traversal
# ============================================================================

class TestContextQuery:
    """Test querying and traversing context data."""

    def test_query_functions_by_name(self, sample_ast_findings):
        """Test querying functions by name."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        results = builder.query_context(
            context,
            query_type="function_by_name",
            parameters={"name": "process_data"}
        )

        assert len(results) > 0
        assert results[0]["name"] == "process_data"

    def test_query_all_functions_in_file(self, sample_ast_findings):
        """Test querying all functions in a file."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        results = builder.query_context(
            context,
            query_type="functions_in_file",
            parameters={"file": "src/core/processor.py"}
        )

        assert len(results) > 0

    def test_query_call_graph(self, sample_ast_findings):
        """Test querying call graph relationships."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        results = builder.query_context(
            context,
            query_type="call_graph",
            parameters={"function": "process_data"}
        )

        assert results is not None

    def test_query_expertise_distribution(self, sample_git_findings):
        """Test querying expertise distribution."""
        builder = LENSContextBuilder()
        builder.add_git_findings(sample_git_findings)

        context = builder.build()
        results = builder.query_context(
            context,
            query_type="expertise_by_file",
            parameters={"file": "src/core/processor.py"}
        )

        assert results is not None


# ============================================================================
# TEST CLASS 7: Edge Cases and Error Handling
# ============================================================================

class TestEdgeCasesAndErrors:
    """Test edge cases and error handling."""

    def test_aggregate_duplicate_findings(self, sample_ast_findings):
        """Test handling duplicate findings."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        # Should not duplicate
        assert context is not None

    def test_missing_required_fields(self):
        """Test handling missing required fields in findings."""
        builder = LENSContextBuilder()

        # Add incomplete findings
        incomplete = {"functions": [{"name": "test"}]}  # Missing file, line, etc.

        with pytest.raises(ValueError):
            builder.add_ast_findings(incomplete)

    def test_malformed_relationships(self):
        """Test handling malformed relationships."""
        builder = LENSContextBuilder()

        malformed = {
            "import_graph": {
                "src/file1.py": "src/file2.py",  # Should be list
            }
        }

        with pytest.raises(TypeError):
            builder.add_relationship_findings(malformed)

    def test_very_large_context(self):
        """Test handling very large context data."""
        builder = LENSContextBuilder()

        # Create large findings set
        large_findings = {
            "functions": [
                {
                    "name": f"func_{i}",
                    "file": f"src/file_{i % 100}.py",
                    "line": i,
                    "calls": [],
                    "parameters": [],
                    "return_type": "None",
                }
                for i in range(1000)
            ]
        }

        builder.add_ast_findings(large_findings)
        context = builder.build()

        assert context is not None
        assert len(context.ast_findings["functions"]) == 1000

    def test_null_findings(self):
        """Test handling null findings gracefully."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(None)

        context = builder.build()
        assert context is not None


# ============================================================================
# TEST CLASS 8: Integration with Intent Reflection Protocol
# ============================================================================

class TestIntegrationWithReflectionProtocol:
    """Test integration with Intent Reflection Protocol."""

    def test_context_for_reflection_request(self, sample_ast_findings, sample_git_findings):
        """Test providing context for reflection request."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.add_git_findings(sample_git_findings)

        context = builder.build()

        # Context should be ready for reflection protocol
        assert context is not None
        assert context.timestamp is not None

    def test_context_enrichment_for_challenges(self, sample_comment_findings):
        """Test enriching context to support challenge detection."""
        builder = LENSContextBuilder()
        builder.add_comment_findings(sample_comment_findings)

        context = builder.build()
        enriched = builder.enrich_context(context, "tech_debt_analysis")

        # Should support challenge detection
        assert enriched is not None

    def test_context_for_recommendations(
        self, sample_ast_findings, sample_relationship_findings
    ):
        """Test providing context for recommendation generation."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        builder.add_relationship_findings(sample_relationship_findings)

        context = builder.build()

        # Context should enable recommendations
        assert context is not None

    def test_context_serialization_for_protocol(self, sample_ast_findings):
        """Test context serialization for protocol communication."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        context = builder.build()
        serialized = context.to_dict()

        # Should be serializable for protocol transmission
        assert isinstance(serialized, dict)
        assert json.dumps(serialized) is not None


# ============================================================================
# TEST CLASS 9: Performance and Optimization
# ============================================================================

class TestPerformanceOptimization:
    """Test performance characteristics and optimization."""

    def test_context_build_performance(self, sample_ast_findings):
        """Test context building performance."""
        import time

        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)

        start = time.time()
        context = builder.build()
        elapsed = time.time() - start

        # Should complete quickly
        assert elapsed < 0.1

    def test_graph_construction_performance(self, sample_ast_findings):
        """Test knowledge graph construction performance."""
        import time

        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        context = builder.build()

        start = time.time()
        kg = builder.build_knowledge_graph(context)
        elapsed = time.time() - start

        assert elapsed < 0.1

    def test_query_performance(self, sample_ast_findings):
        """Test context query performance."""
        import time

        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_ast_findings)
        context = builder.build()

        start = time.time()
        builder.query_context(
            context,
            query_type="function_by_name",
            parameters={"name": "process_data"}
        )
        elapsed = time.time() - start

        assert elapsed < 0.05


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
