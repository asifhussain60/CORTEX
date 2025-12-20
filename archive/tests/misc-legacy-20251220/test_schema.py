"""
Tests for Knowledge Graph Schema

Validates node types, relationship types, and schema validation rules.
"""

import pytest
from src.core.knowledge_graph.schema import (
    NodeType,
    RelationshipType,
    NodeStatus,
    validate_node,
    validate_relationship,
    get_node_schema,
    get_relationship_schema
)


class TestNodeValidation:
    """Test node validation rules"""
    
    def test_phase_node_valid(self):
        """Valid phase node passes validation"""
        properties = {
            "name": "Foundation",
            "number": 1,
            "status": "complete",
            "description": "Setup infrastructure"
        }
        
        is_valid, error = validate_node(NodeType.PHASE, properties)
        assert is_valid
        assert error is None
    
    def test_phase_node_missing_required(self):
        """Phase node missing required property fails"""
        properties = {
            "name": "Foundation",
            "status": "complete"
            # Missing 'number'
        }
        
        is_valid, error = validate_node(NodeType.PHASE, properties)
        assert not is_valid
        assert "number" in error.lower()
    
    def test_orchestrator_node_valid(self):
        """Valid orchestrator node passes validation"""
        properties = {
            "name": "ExecutionOrchestrator",
            "status": "complete",
            "priority": 1,
            "estimated_hours": 40,
            "actual_hours": 35,
            "test_coverage": 92.5
        }
        
        is_valid, error = validate_node(NodeType.ORCHESTRATOR, properties)
        assert is_valid
        assert error is None
    
    def test_week_node_valid(self):
        """Valid week node passes validation"""
        properties = {
            "number": 1,
            "status": "complete",
            "description": "Foundation setup"
        }
        
        is_valid, error = validate_node(NodeType.WEEK, properties)
        assert is_valid
        assert error is None
    
    def test_validation_gate_valid(self):
        """Valid validation gate passes validation"""
        properties = {
            "name": "Phase 1 → 2 Validation",
            "from_phase": 1,
            "to_phase": 2,
            "status": "passed",
            "checks_required": 10,
            "checks_passed": 10
        }
        
        is_valid, error = validate_node(NodeType.VALIDATION_GATE, properties)
        assert is_valid
        assert error is None
    
    def test_simplification_valid(self):
        """Valid simplification node passes validation"""
        properties = {
            "name": "CORTEX Lens v2.0 Deferral",
            "decision_type": "DEFER",
            "decision_date": "2025-12-19",
            "hours_saved": 60,
            "defer_to_version": "5.0"
        }
        
        is_valid, error = validate_node(NodeType.SIMPLIFICATION, properties)
        assert is_valid
        assert error is None


class TestRelationshipValidation:
    """Test relationship validation rules"""
    
    def test_depends_on_valid(self):
        """Valid DEPENDS_ON relationship passes"""
        is_valid, error = validate_relationship(
            RelationshipType.DEPENDS_ON,
            NodeType.PHASE,
            NodeType.PREREQUISITE,
            {}
        )
        assert is_valid
        assert error is None
    
    def test_depends_on_invalid_target(self):
        """DEPENDS_ON with invalid target fails"""
        is_valid, error = validate_relationship(
            RelationshipType.DEPENDS_ON,
            NodeType.PHASE,
            NodeType.WEEK,  # Invalid target
            {}
        )
        assert not is_valid
        assert "cannot point to" in error.lower()
    
    def test_includes_valid(self):
        """Valid INCLUDES relationship passes"""
        is_valid, error = validate_relationship(
            RelationshipType.INCLUDES,
            NodeType.PHASE,
            NodeType.WEEK,
            {}
        )
        assert is_valid
        assert error is None
    
    def test_migrates_valid(self):
        """Valid MIGRATES relationship passes"""
        is_valid, error = validate_relationship(
            RelationshipType.MIGRATES,
            NodeType.WEEK,
            NodeType.ORCHESTRATOR,
            {"days": 5}
        )
        assert is_valid
        assert error is None
    
    def test_defers_valid(self):
        """Valid DEFERS relationship passes"""
        is_valid, error = validate_relationship(
            RelationshipType.DEFERS,
            NodeType.SIMPLIFICATION,
            NodeType.ORCHESTRATOR,
            {"defer_to_version": "5.0"}
        )
        assert is_valid
        assert error is None
    
    def test_parallel_with_valid(self):
        """Valid PARALLEL_WITH relationship passes"""
        is_valid, error = validate_relationship(
            RelationshipType.PARALLEL_WITH,
            NodeType.PHASE,
            NodeType.PHASE,
            {}
        )
        assert is_valid
        assert error is None


class TestSchemaRetrieving:
    """Test schema retrieval functions"""
    
    def test_get_node_schema(self):
        """Can retrieve node schemas"""
        schema = get_node_schema(NodeType.PHASE)
        assert schema.node_type == NodeType.PHASE
        assert "name" in schema.required_properties
        assert "number" in schema.required_properties
    
    def test_get_relationship_schema(self):
        """Can retrieve relationship schemas"""
        schema = get_relationship_schema(RelationshipType.DEPENDS_ON)
        assert schema.relationship_type == RelationshipType.DEPENDS_ON
        assert NodeType.PHASE in schema.allowed_from


class TestEnums:
    """Test enum definitions"""
    
    def test_node_types(self):
        """All node types defined"""
        expected = {
            "phase", "week", "orchestrator", "prerequisite",
            "milestone", "validation_gate", "metric", "simplification"
        }
        actual = {nt.value for nt in NodeType}
        assert actual == expected
    
    def test_relationship_types(self):
        """All relationship types defined"""
        expected = {
            "depends_on", "blocks", "includes", "migrates",
            "validates", "measures", "achieves", "simplifies",
            "parallel_with", "precedes", "contributes_to", "defers"
        }
        actual = {rt.value for rt in RelationshipType}
        assert actual == expected
    
    def test_node_status(self):
        """All node statuses defined"""
        expected = {"pending", "active", "complete", "blocked", "deferred"}
        actual = {ns.value for ns in NodeStatus}
        assert actual == expected
