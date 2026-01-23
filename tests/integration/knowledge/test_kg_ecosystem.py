"""
Knowledge Ecosystem Tests - KnowledgeIndexer, Querier, Inference, Exchange.

Tests for indexing, querying, reasoning, and exchange of knowledge graph entities.
"""

import pytest
from typing import Dict, List, Any, Set
from datetime import datetime

from cortex.brain.domain_brain.kg_indexer import KnowledgeIndexer
from cortex.brain.domain_brain.kg_querier import KnowledgeQuerier
from cortex.brain.domain_brain.kg_inference import KnowledgeInference
from cortex.brain.domain_brain.kg_exchange import KnowledgeExchange


class TestKnowledgeIndexer:
    """Tests for KnowledgeIndexer."""

    def test_indexer_initializes(self) -> None:
        """Test indexer initialization."""
        indexer = KnowledgeIndexer()
        assert indexer is not None
        assert len(indexer.entity_index) == 0

    def test_indexer_indexes_entities(self) -> None:
        """Test indexing entities."""
        indexer = KnowledgeIndexer()
        
        entity = {
            "id": "entity_001",
            "type": "concept",
            "name": "Machine Learning",
            "description": "Algorithms that learn from data",
        }
        
        indexer.add_entity(entity)
        assert indexer.get_entity("entity_001") is not None

    def test_indexer_full_text_search(self) -> None:
        """Test full-text search functionality."""
        indexer = KnowledgeIndexer()
        
        entities = [
            {"id": "e1", "type": "concept", "name": "Machine Learning", "description": "Learning algorithms"},
            {"id": "e2", "type": "concept", "name": "Deep Learning", "description": "Neural networks"},
            {"id": "e3", "type": "concept", "name": "Python", "description": "Programming language"},
        ]
        
        for entity in entities:
            indexer.add_entity(entity)
        
        results = indexer.search("Learning")
        assert len(results) >= 2
        assert any(r["id"] == "e1" for r in results)
        assert any(r["id"] == "e2" for r in results)

    def test_indexer_relationship_indexing(self) -> None:
        """Test relationship indexing."""
        indexer = KnowledgeIndexer()
        
        relationship = {
            "source_id": "e1",
            "target_id": "e2",
            "type": "is_subclass_of",
            "properties": {"confidence": 0.95},
        }
        
        indexer.add_relationship(relationship)
        relationships = indexer.get_relationships("e1")
        assert len(relationships) > 0

    def test_indexer_batch_operations(self) -> None:
        """Test batch indexing."""
        indexer = KnowledgeIndexer()
        
        entities = [
            {"id": f"e{i}", "type": "concept", "name": f"Entity {i}"}
            for i in range(10)
        ]
        
        indexer.batch_add_entities(entities)
        assert len(indexer.entity_index) == 10


class TestKnowledgeQuerier:
    """Tests for KnowledgeQuerier."""

    def test_querier_initializes(self) -> None:
        """Test querier initialization."""
        querier = KnowledgeQuerier()
        assert querier is not None

    def test_querier_simple_query(self) -> None:
        """Test simple entity query."""
        querier = KnowledgeQuerier()
        querier.index_entity({"id": "e1", "type": "concept", "name": "AI"})
        
        result = querier.query_by_id("e1")
        assert result is not None
        assert result["id"] == "e1"

    def test_querier_filter_query(self) -> None:
        """Test filtered queries."""
        querier = KnowledgeQuerier()
        
        entities = [
            {"id": "e1", "type": "concept", "domain": "ML"},
            {"id": "e2", "type": "concept", "domain": "NLP"},
            {"id": "e3", "type": "concept", "domain": "ML"},
        ]
        
        for entity in entities:
            querier.index_entity(entity)
        
        results = querier.query_by_filter({"type": "concept", "domain": "ML"})
        assert len(results) == 2

    def test_querier_relationship_traversal(self) -> None:
        """Test relationship path queries."""
        querier = KnowledgeQuerier()
        
        querier.index_entity({"id": "e1", "type": "concept"})
        querier.index_entity({"id": "e2", "type": "concept"})
        querier.index_relationship({"source_id": "e1", "target_id": "e2", "type": "related_to"})
        
        path = querier.find_relationship_path("e1", "e2")
        assert path is not None
        assert len(path) > 0

    def test_querier_complex_query_performance(self) -> None:
        """Test query performance."""
        querier = KnowledgeQuerier()
        
        # Index many entities
        for i in range(100):
            querier.index_entity({"id": f"e{i}", "type": "concept", "value": i})
        
        import time
        start = time.time()
        results = querier.query_by_filter({"type": "concept"})
        elapsed = (time.time() - start) * 1000  # ms
        
        assert elapsed < 500  # Should complete in <500ms
        assert len(results) == 100


class TestKnowledgeInference:
    """Tests for KnowledgeInference."""

    def test_inference_initializes(self) -> None:
        """Test inference engine initialization."""
        inference = KnowledgeInference()
        assert inference is not None

    def test_inference_transitive_closure(self) -> None:
        """Test transitive closure reasoning."""
        inference = KnowledgeInference()
        
        # A -> B, B -> C, should infer A -> C
        inference.add_relationship("e1", "e2", "parent_of")
        inference.add_relationship("e2", "e3", "parent_of")
        
        inferred = inference.compute_transitive_closure("e1", "parent_of")
        assert "e3" in inferred

    def test_inference_impact_analysis(self) -> None:
        """Test impact analysis."""
        inference = KnowledgeInference()
        
        # Set up dependency chain
        inference.add_relationship("e1", "e2", "depends_on")
        inference.add_relationship("e2", "e3", "depends_on")
        
        impact = inference.analyze_impact("e1")
        assert len(impact) > 0
        assert "e2" in impact or "e3" in impact

    def test_inference_rule_application(self) -> None:
        """Test rule-based inference."""
        inference = KnowledgeInference()
        
        rule = {
            "condition": {"type": "concept", "domain": "ML"},
            "action": "tag_as_ai_related",
        }
        
        inference.add_rule(rule)
        
        entity = {"id": "e1", "type": "concept", "domain": "ML"}
        result = inference.apply_rules(entity)
        assert result is not None

    def test_inference_consistency_check(self) -> None:
        """Test consistency checking."""
        inference = KnowledgeInference()
        
        # Add relationships
        inference.add_relationship("e1", "e2", "is_a")
        inference.add_relationship("e2", "e3", "is_a")
        
        is_consistent = inference.check_consistency()
        assert isinstance(is_consistent, bool)


class TestKnowledgeExchange:
    """Tests for KnowledgeExchange."""

    def test_exchange_initializes(self) -> None:
        """Test exchange protocol initialization."""
        exchange = KnowledgeExchange()
        assert exchange is not None

    def test_exchange_export_entities(self) -> None:
        """Test entity export."""
        exchange = KnowledgeExchange()
        
        entities = [
            {"id": "e1", "type": "concept", "name": "AI"},
            {"id": "e2", "type": "concept", "name": "ML"},
        ]
        
        exported = exchange.export_entities(entities)
        assert exported is not None
        assert len(exported) == 2

    def test_exchange_import_entities(self) -> None:
        """Test entity import."""
        exchange = KnowledgeExchange()
        
        data = [
            {"id": "e1", "type": "concept", "name": "AI"},
            {"id": "e2", "type": "concept", "name": "ML"},
        ]
        
        imported = exchange.import_entities(data)
        assert imported is not None
        assert len(imported) == 2

    def test_exchange_serialization(self) -> None:
        """Test knowledge serialization."""
        exchange = KnowledgeExchange()
        
        knowledge = {
            "entities": [{"id": "e1", "type": "concept"}],
            "relationships": [{"source": "e1", "target": "e2", "type": "related"}],
        }
        
        serialized = exchange.serialize(knowledge)
        assert serialized is not None
        
        deserialized = exchange.deserialize(serialized)
        assert deserialized is not None

    def test_exchange_format_conversion(self) -> None:
        """Test format conversions (JSON, GraphML, etc)."""
        exchange = KnowledgeExchange()
        
        knowledge = {"entities": [{"id": "e1"}], "relationships": []}
        
        json_format = exchange.to_json(knowledge)
        assert json_format is not None
        
        back = exchange.from_json(json_format)
        assert back is not None


class TestKnowledgeIntegration:
    """Integration tests for knowledge ecosystem."""

    def test_indexer_querier_integration(self) -> None:
        """Test indexer and querier together."""
        indexer = KnowledgeIndexer()
        querier = KnowledgeQuerier()
        
        entity = {"id": "e1", "type": "concept", "name": "Machine Learning"}
        indexer.add_entity(entity)
        querier.index_entity(entity)
        
        result = querier.query_by_id("e1")
        assert result is not None

    def test_querier_inference_integration(self) -> None:
        """Test querier with inference."""
        querier = KnowledgeQuerier()
        inference = KnowledgeInference()
        
        querier.index_entity({"id": "e1", "type": "concept"})
        querier.index_entity({"id": "e2", "type": "concept"})
        querier.index_relationship({"source_id": "e1", "target_id": "e2", "type": "parent_of"})
        
        inference.add_relationship("e1", "e2", "parent_of")
        inference.add_relationship("e2", "e3", "parent_of")
        
        result = inference.compute_transitive_closure("e1", "parent_of")
        assert result is not None

    def test_end_to_end_knowledge_pipeline(self) -> None:
        """Test complete knowledge pipeline."""
        indexer = KnowledgeIndexer()
        querier = KnowledgeQuerier()
        inference = KnowledgeInference()
        exchange = KnowledgeExchange()
        
        # 1. Index entities
        entities = [{"id": f"e{i}", "type": "concept"} for i in range(5)]
        indexer.batch_add_entities(entities)
        
        # 2. Query entities
        for entity in entities:
            querier.index_entity(entity)
        
        results = querier.query_by_filter({"type": "concept"})
        assert len(results) == 5
        
        # 3. Apply inference
        for i in range(4):
            inference.add_relationship(f"e{i}", f"e{i+1}", "related_to")
        
        closure = inference.compute_transitive_closure("e0", "related_to")
        assert closure is not None
        
        # 4. Export knowledge
        exported = exchange.export_entities(entities)
        assert exported is not None
