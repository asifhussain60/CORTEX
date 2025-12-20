"""
Tests for Knowledge Graph Database

Validates CRUD operations, transactions, and validation enforcement.
"""

import pytest
from src.core.knowledge_graph.database import GraphDatabase
from src.core.knowledge_graph.schema import NodeType, RelationshipType


class TestNodeOperations:
    """Test node CRUD operations"""
    
    def test_create_node(self, temp_db):
        """Can create valid node"""
        node_id = temp_db.create_node(
            NodeType.PHASE,
            {"name": "Foundation", "number": 1, "status": "complete"}
        )
        
        assert node_id is not None
        node = temp_db.get_node(node_id)
        assert node["type"] == "phase"
        assert node["properties"]["name"] == "Foundation"
    
    def test_create_node_invalid(self, temp_db):
        """Cannot create invalid node"""
        with pytest.raises(ValueError, match="validation failed"):
            temp_db.create_node(
                NodeType.PHASE,
                {"name": "Foundation"}  # Missing required 'number' and 'status'
            )
    
    def test_update_node(self, temp_db):
        """Can update node properties"""
        node_id = temp_db.create_node(
            NodeType.PHASE,
            {"name": "Foundation", "number": 1, "status": "pending"}
        )
        
        temp_db.update_node(node_id, {"status": "complete", "progress_percent": 100})
        
        node = temp_db.get_node(node_id)
        assert node["properties"]["status"] == "complete"
        assert node["properties"]["progress_percent"] == 100
    
    def test_update_node_invalid(self, temp_db):
        """Cannot update node with invalid properties"""
        node_id = temp_db.create_node(
            NodeType.PHASE,
            {"name": "Foundation", "number": 1, "status": "pending"}
        )
        
        # Try to update with invalid type
        with pytest.raises(ValueError):
            temp_db.update_node(node_id, {"number": "not_an_integer"})
    
    def test_delete_node(self, temp_db):
        """Can delete node"""
        node_id = temp_db.create_node(
            NodeType.PHASE,
            {"name": "Foundation", "number": 1, "status": "complete"}
        )
        
        temp_db.delete_node(node_id)
        
        node = temp_db.get_node(node_id)
        assert node is None
    
    def test_find_nodes_by_type(self, populated_db):
        """Can find nodes by type"""
        phases = populated_db.find_nodes(NodeType.PHASE)
        assert len(phases) == 2
        assert all(n["type"] == "phase" for n in phases)
    
    def test_find_nodes_with_filters(self, populated_db):
        """Can find nodes with property filters"""
        complete_phases = populated_db.find_nodes(
            NodeType.PHASE,
            filters={"status": "complete"}
        )
        
        assert len(complete_phases) == 1
        assert complete_phases[0]["properties"]["name"] == "Foundation"


class TestRelationshipOperations:
    """Test relationship CRUD operations"""
    
    def test_create_relationship(self, temp_db):
        """Can create valid relationship"""
        phase_id = temp_db.create_node(
            NodeType.PHASE,
            {"name": "Foundation", "number": 1, "status": "complete"}
        )
        
        week_id = temp_db.create_node(
            NodeType.WEEK,
            {"number": 1, "status": "complete"}
        )
        
        rel_id = temp_db.create_relationship(
            RelationshipType.INCLUDES,
            phase_id,
            week_id
        )
        
        assert rel_id is not None
        
        rels = temp_db.find_relationships(from_node_id=phase_id)
        assert len(rels) == 1
        assert rels[0]["type"] == "includes"
    
    def test_create_relationship_invalid(self, temp_db):
        """Cannot create invalid relationship"""
        phase_id = temp_db.create_node(
            NodeType.PHASE,
            {"name": "Foundation", "number": 1, "status": "complete"}
        )
        
        orch_id = temp_db.create_node(
            NodeType.ORCHESTRATOR,
            {"name": "ExecutionOrchestrator", "status": "complete"}
        )
        
        # INCLUDES cannot connect Phase → Orchestrator
        with pytest.raises(ValueError, match="validation failed"):
            temp_db.create_relationship(
                RelationshipType.INCLUDES,
                phase_id,
                orch_id
            )
    
    def test_delete_relationship(self, temp_db):
        """Can delete relationship"""
        phase_id = temp_db.create_node(
            NodeType.PHASE,
            {"name": "Foundation", "number": 1, "status": "complete"}
        )
        
        week_id = temp_db.create_node(
            NodeType.WEEK,
            {"number": 1, "status": "complete"}
        )
        
        rel_id = temp_db.create_relationship(
            RelationshipType.INCLUDES,
            phase_id,
            week_id
        )
        
        temp_db.delete_relationship(rel_id)
        
        rels = temp_db.find_relationships(from_node_id=phase_id)
        assert len(rels) == 0
    
    def test_cascade_delete(self, temp_db):
        """Deleting node cascades to relationships"""
        phase_id = temp_db.create_node(
            NodeType.PHASE,
            {"name": "Foundation", "number": 1, "status": "complete"}
        )
        
        week_id = temp_db.create_node(
            NodeType.WEEK,
            {"number": 1, "status": "complete"}
        )
        
        temp_db.create_relationship(
            RelationshipType.INCLUDES,
            phase_id,
            week_id
        )
        
        # Delete phase should delete relationship
        temp_db.delete_node(phase_id)
        
        rels = temp_db.find_relationships(to_node_id=week_id)
        assert len(rels) == 0
    
    def test_find_relationships_by_type(self, populated_db):
        """Can find relationships by type"""
        rels = populated_db.find_relationships(
            relationship_type=RelationshipType.MIGRATES
        )
        
        assert len(rels) == 2
        assert all(r["type"] == "migrates" for r in rels)


class TestMetadata:
    """Test metadata operations"""
    
    def test_set_get_metadata(self, temp_db):
        """Can set and get metadata"""
        temp_db.set_metadata("test_key", "test_value")
        
        value = temp_db.get_metadata("test_key")
        assert value == "test_value"
    
    def test_metadata_upsert(self, temp_db):
        """Metadata updates existing key"""
        temp_db.set_metadata("key", "value1")
        temp_db.set_metadata("key", "value2")
        
        value = temp_db.get_metadata("key")
        assert value == "value2"
    
    def test_metadata_nonexistent(self, temp_db):
        """Nonexistent metadata returns None"""
        value = temp_db.get_metadata("nonexistent")
        assert value is None


class TestTransactions:
    """Test transaction behavior"""
    
    def test_transaction_rollback(self, temp_db):
        """Failed transaction rolls back"""
        try:
            with temp_db.connection() as conn:
                cursor = conn.cursor()
                
                # Create valid node
                cursor.execute(
                    "INSERT INTO nodes (id, type, properties, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    ("test1", "phase", '{"name": "Test", "number": 1, "status": "complete"}', "2025-12-19", "2025-12-19")
                )
                
                # Force error
                raise ValueError("Simulated error")
        except ValueError:
            pass
        
        # Node should not exist (rolled back)
        node = temp_db.get_node("test1")
        assert node is None
    
    def test_clear_all(self, populated_db):
        """Clear all removes all data"""
        # Verify data exists
        phases = populated_db.find_nodes(NodeType.PHASE)
        assert len(phases) > 0
        
        # Clear
        populated_db.clear_all()
        
        # Verify empty
        phases = populated_db.find_nodes(NodeType.PHASE)
        assert len(phases) == 0
