"""
CORTEX Knowledge Graph - Master Plan Query Engine

Provides queryable graph representation of MASTER-PLAN.md with
automatic synchronization and disaster-prevention safeguards.
"""

from .schema import (
    NodeType,
    RelationshipType,
    NodeStatus,
    validate_node,
    validate_relationship
)

__all__ = [
    "NodeType",
    "RelationshipType",
    "NodeStatus",
    "validate_node",
    "validate_relationship"
]
