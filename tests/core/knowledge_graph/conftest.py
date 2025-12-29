"""Test utilities for knowledge graph tests"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.core.knowledge_graph.database import GraphDatabase


@pytest.fixture
def temp_db() -> Generator[GraphDatabase, None, None]:
    """Create temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_graph.db"
        db = GraphDatabase(str(db_path))
        yield db


@pytest.fixture
def populated_db(temp_db: GraphDatabase) -> GraphDatabase:
    """Database with sample data for testing"""
    from src.core.knowledge_graph.schema import NodeType, RelationshipType
    
    # Create phases
    phase1_id = temp_db.create_node(
        NodeType.PHASE,
        {"name": "Foundation", "number": 1, "status": "complete"}
    )
    
    phase2_id = temp_db.create_node(
        NodeType.PHASE,
        {"name": "Core Migration", "number": 2, "status": "active"}
    )
    
    # Create weeks
    week1_id = temp_db.create_node(
        NodeType.WEEK,
        {"number": 1, "status": "complete", "description": "Setup"}
    )
    
    week2_id = temp_db.create_node(
        NodeType.WEEK,
        {"number": 2, "status": "active", "description": "ExecutionOrchestrator"}
    )
    
    # Create orchestrators
    exec_orch_id = temp_db.create_node(
        NodeType.ORCHESTRATOR,
        {
            "name": "ExecutionOrchestrator",
            "status": "complete",
            "priority": 1,
            "estimated_hours": 40,
            "actual_hours": 35,
            "test_coverage": 92.5
        }
    )
    
    doc_orch_id = temp_db.create_node(
        NodeType.ORCHESTRATOR,
        {
            "name": "DocumentationOrchestrator",
            "status": "active",
            "priority": 2,
            "estimated_hours": 30
        }
    )
    
    # Create relationships
    temp_db.create_relationship(RelationshipType.INCLUDES, phase1_id, week1_id)
    temp_db.create_relationship(RelationshipType.INCLUDES, phase2_id, week2_id)
    temp_db.create_relationship(RelationshipType.MIGRATES, week1_id, exec_orch_id)
    temp_db.create_relationship(RelationshipType.MIGRATES, week2_id, doc_orch_id)
    
    return temp_db
