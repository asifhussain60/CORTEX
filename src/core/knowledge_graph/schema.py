"""
Knowledge Graph Schema for CORTEX Master Plans

Defines node types, relationship types, and validation rules for
maintaining a queryable graph representation of project plans.

CRITICAL: This schema ensures MASTER-PLAN.md and graph stay in sync.
Any schema changes require migration script + validation.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


class NodeType(Enum):
    """8 core node types for master plan representation"""
    PHASE = "phase"
    WEEK = "week"
    ORCHESTRATOR = "orchestrator"
    PREREQUISITE = "prerequisite"
    MILESTONE = "milestone"
    VALIDATION_GATE = "validation_gate"
    METRIC = "metric"
    SIMPLIFICATION = "simplification"


class RelationshipType(Enum):
    """12 relationship types defining node connections"""
    DEPENDS_ON = "depends_on"              # Phase → Prerequisite
    BLOCKS = "blocks"                       # Prerequisite → Phase
    INCLUDES = "includes"                   # Phase → Week
    MIGRATES = "migrates"                   # Week → Orchestrator
    VALIDATES = "validates"                 # ValidationGate → Phase
    MEASURES = "measures"                   # Metric → Orchestrator
    ACHIEVES = "achieves"                   # Week → Milestone
    SIMPLIFIES = "simplifies"               # Simplification → Phase
    PARALLEL_WITH = "parallel_with"         # Phase ↔ Phase
    PRECEDES = "precedes"                   # Week → Week
    CONTRIBUTES_TO = "contributes_to"       # Orchestrator → Metric
    DEFERS = "defers"                       # Simplification → Orchestrator


class NodeStatus(Enum):
    """Status values for nodes"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


@dataclass
class NodeSchema:
    """Schema definition for a node type"""
    node_type: NodeType
    required_properties: List[str]
    optional_properties: List[str]
    property_types: Dict[str, type]
    
    def validate(self, properties: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate node properties against schema"""
        # Check required properties
        for prop in self.required_properties:
            if prop not in properties:
                return False, f"Missing required property: {prop}"
        
        # Check property types
        for prop, value in properties.items():
            if prop in self.property_types:
                expected_type = self.property_types[prop]
                if not isinstance(value, expected_type):
                    return False, f"Property '{prop}' must be {expected_type.__name__}, got {type(value).__name__}"
        
        return True, None


# Node type schemas
NODE_SCHEMAS = {
    NodeType.PHASE: NodeSchema(
        node_type=NodeType.PHASE,
        required_properties=["name", "number", "status"],
        optional_properties=["description", "start_week", "end_week", "progress_percent", "completion_date"],
        property_types={
            "name": str,
            "number": int,
            "status": str,
            "description": str,
            "start_week": int,
            "end_week": int,
            "progress_percent": (int, float),
            "completion_date": str
        }
    ),
    
    NodeType.WEEK: NodeSchema(
        node_type=NodeType.WEEK,
        required_properties=["number", "status"],
        optional_properties=["description", "start_date", "end_date", "progress_percent"],
        property_types={
            "number": int,
            "status": str,
            "description": str,
            "start_date": str,
            "end_date": str,
            "progress_percent": (int, float)
        }
    ),
    
    NodeType.ORCHESTRATOR: NodeSchema(
        node_type=NodeType.ORCHESTRATOR,
        required_properties=["name", "status"],
        optional_properties=[
            "description", "priority", "estimated_hours", "actual_hours",
            "test_coverage", "lines_of_code", "completion_date", "tests_passing",
            "docs_generated", "migration_complete"
        ],
        property_types={
            "name": str,
            "status": str,
            "description": str,
            "priority": int,
            "estimated_hours": (int, float),
            "actual_hours": (int, float),
            "test_coverage": float,
            "lines_of_code": int,
            "completion_date": str,
            "tests_passing": int,
            "docs_generated": int,
            "migration_complete": bool
        }
    ),
    
    NodeType.PREREQUISITE: NodeSchema(
        node_type=NodeType.PREREQUISITE,
        required_properties=["name", "status"],
        optional_properties=["description", "completion_date", "validation_method"],
        property_types={
            "name": str,
            "status": str,
            "description": str,
            "completion_date": str,
            "validation_method": str
        }
    ),
    
    NodeType.MILESTONE: NodeSchema(
        node_type=NodeType.MILESTONE,
        required_properties=["name", "status"],
        optional_properties=["description", "target_week", "completion_date", "category"],
        property_types={
            "name": str,
            "status": str,
            "description": str,
            "target_week": int,
            "completion_date": str,
            "category": str
        }
    ),
    
    NodeType.VALIDATION_GATE: NodeSchema(
        node_type=NodeType.VALIDATION_GATE,
        required_properties=["name", "from_phase", "to_phase", "status"],
        optional_properties=["checks_required", "checks_passed", "validation_date"],
        property_types={
            "name": str,
            "from_phase": int,
            "to_phase": int,
            "status": str,
            "checks_required": int,
            "checks_passed": int,
            "validation_date": str
        }
    ),
    
    NodeType.METRIC: NodeSchema(
        node_type=NodeType.METRIC,
        required_properties=["name", "current_value"],
        optional_properties=["target_value", "unit", "category", "last_updated"],
        property_types={
            "name": str,
            "current_value": (int, float, str),
            "target_value": (int, float, str),
            "unit": str,
            "category": str,
            "last_updated": str
        }
    ),
    
    NodeType.SIMPLIFICATION: NodeSchema(
        node_type=NodeType.SIMPLIFICATION,
        required_properties=["name", "decision_type", "decision_date"],
        optional_properties=["description", "hours_saved", "rationale", "defer_to_version"],
        property_types={
            "name": str,
            "decision_type": str,  # "DEFER", "SIMPLIFY", "REDUCE"
            "decision_date": str,
            "description": str,
            "hours_saved": (int, float),
            "rationale": str,
            "defer_to_version": str
        }
    )
}


@dataclass
class RelationshipSchema:
    """Schema definition for a relationship type"""
    relationship_type: RelationshipType
    allowed_from: List[NodeType]
    allowed_to: List[NodeType]
    required_properties: List[str]
    optional_properties: List[str]
    
    def validate(
        self,
        from_node_type: NodeType,
        to_node_type: NodeType,
        properties: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate relationship"""
        # Check node type compatibility
        if from_node_type not in self.allowed_from:
            return False, f"{self.relationship_type.value} cannot start from {from_node_type.value}"
        
        if to_node_type not in self.allowed_to:
            return False, f"{self.relationship_type.value} cannot point to {to_node_type.value}"
        
        # Check required properties
        for prop in self.required_properties:
            if prop not in properties:
                return False, f"Missing required property: {prop}"
        
        return True, None


# Relationship type schemas
RELATIONSHIP_SCHEMAS = {
    RelationshipType.DEPENDS_ON: RelationshipSchema(
        relationship_type=RelationshipType.DEPENDS_ON,
        allowed_from=[NodeType.PHASE, NodeType.ORCHESTRATOR],
        allowed_to=[NodeType.PREREQUISITE, NodeType.PHASE],
        required_properties=[],
        optional_properties=["description"]
    ),
    
    RelationshipType.BLOCKS: RelationshipSchema(
        relationship_type=RelationshipType.BLOCKS,
        allowed_from=[NodeType.PREREQUISITE, NodeType.PHASE],
        allowed_to=[NodeType.PHASE, NodeType.ORCHESTRATOR],
        required_properties=[],
        optional_properties=["description"]
    ),
    
    RelationshipType.INCLUDES: RelationshipSchema(
        relationship_type=RelationshipType.INCLUDES,
        allowed_from=[NodeType.PHASE],
        allowed_to=[NodeType.WEEK],
        required_properties=[],
        optional_properties=[]
    ),
    
    RelationshipType.MIGRATES: RelationshipSchema(
        relationship_type=RelationshipType.MIGRATES,
        allowed_from=[NodeType.WEEK],
        allowed_to=[NodeType.ORCHESTRATOR],
        required_properties=[],
        optional_properties=["days"]
    ),
    
    RelationshipType.VALIDATES: RelationshipSchema(
        relationship_type=RelationshipType.VALIDATES,
        allowed_from=[NodeType.VALIDATION_GATE],
        allowed_to=[NodeType.PHASE],
        required_properties=[],
        optional_properties=[]
    ),
    
    RelationshipType.MEASURES: RelationshipSchema(
        relationship_type=RelationshipType.MEASURES,
        allowed_from=[NodeType.METRIC],
        allowed_to=[NodeType.ORCHESTRATOR, NodeType.PHASE],
        required_properties=[],
        optional_properties=[]
    ),
    
    RelationshipType.ACHIEVES: RelationshipSchema(
        relationship_type=RelationshipType.ACHIEVES,
        allowed_from=[NodeType.WEEK, NodeType.PHASE],
        allowed_to=[NodeType.MILESTONE],
        required_properties=[],
        optional_properties=[]
    ),
    
    RelationshipType.SIMPLIFIES: RelationshipSchema(
        relationship_type=RelationshipType.SIMPLIFIES,
        allowed_from=[NodeType.SIMPLIFICATION],
        allowed_to=[NodeType.PHASE, NodeType.ORCHESTRATOR],
        required_properties=[],
        optional_properties=[]
    ),
    
    RelationshipType.PARALLEL_WITH: RelationshipSchema(
        relationship_type=RelationshipType.PARALLEL_WITH,
        allowed_from=[NodeType.PHASE],
        allowed_to=[NodeType.PHASE],
        required_properties=[],
        optional_properties=[]
    ),
    
    RelationshipType.PRECEDES: RelationshipSchema(
        relationship_type=RelationshipType.PRECEDES,
        allowed_from=[NodeType.WEEK],
        allowed_to=[NodeType.WEEK],
        required_properties=[],
        optional_properties=[]
    ),
    
    RelationshipType.CONTRIBUTES_TO: RelationshipSchema(
        relationship_type=RelationshipType.CONTRIBUTES_TO,
        allowed_from=[NodeType.ORCHESTRATOR],
        allowed_to=[NodeType.METRIC],
        required_properties=[],
        optional_properties=["contribution_value"]
    ),
    
    RelationshipType.DEFERS: RelationshipSchema(
        relationship_type=RelationshipType.DEFERS,
        allowed_from=[NodeType.SIMPLIFICATION],
        allowed_to=[NodeType.ORCHESTRATOR, NodeType.PHASE],
        required_properties=[],
        optional_properties=["defer_to_version"]
    )
}


def get_node_schema(node_type: NodeType) -> NodeSchema:
    """Get schema for a node type"""
    return NODE_SCHEMAS[node_type]


def get_relationship_schema(relationship_type: RelationshipType) -> RelationshipSchema:
    """Get schema for a relationship type"""
    return RELATIONSHIP_SCHEMAS[relationship_type]


def validate_node(node_type: NodeType, properties: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate a node against its schema"""
    schema = get_node_schema(node_type)
    return schema.validate(properties)


def validate_relationship(
    relationship_type: RelationshipType,
    from_node_type: NodeType,
    to_node_type: NodeType,
    properties: Dict[str, Any]
) -> tuple[bool, Optional[str]]:
    """Validate a relationship against its schema"""
    schema = get_relationship_schema(relationship_type)
    return schema.validate(from_node_type, to_node_type, properties)
