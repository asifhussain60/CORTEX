"""
Tests for Enhanced Mermaid Renderer.

Authority: CORE-008 (TDD)
Phase: 14 - LENS Dashboard Implementation
Task: 009 - Mermaid Renderer Tests
AC-ID: LENS-DASH-003
"""

import pytest
from pathlib import Path

from cortex.visualization.renderers.mermaid_renderer import (
    MermaidDiagram,
    MermaidRenderer,
)


@pytest.fixture
def renderer():
    """Create MermaidRenderer instance."""
    return MermaidRenderer(repo_path=Path("/test/repo"))


@pytest.fixture
def sample_classes():
    """Sample class data for class diagrams."""
    return {
        "classes": [
            {
                "name": "User",
                "attributes": [
                    {"name": "id", "type": "int"},
                    {"name": "name", "type": "str"},
                ],
                "methods": [
                    {
                        "name": "save",
                        "parameters": [{"name": "self"}],
                        "return_type": "None",
                    }
                ],
                "bases": [],
            },
            {
                "name": "AdminUser",
                "attributes": [],
                "methods": [],
                "bases": ["User"],
            },
        ]
    }


# Tests for initialization

def test_renderer_initialization():
    """Test MermaidRenderer initialization."""
    renderer = MermaidRenderer()
    assert renderer.repo_path == Path.cwd()


# Tests for generate_class_diagram

def test_generate_class_diagram_basic(renderer, sample_classes):
    """Test basic class diagram generation."""
    diagram = renderer.generate_class_diagram(sample_classes)
    
    assert isinstance(diagram, MermaidDiagram)
    assert diagram.diagram_type == "classDiagram"
    assert "classDiagram" in diagram.content
    assert "class User" in diagram.content


def test_class_diagram_with_inheritance(renderer, sample_classes):
    """Test class diagram includes inheritance."""
    diagram = renderer.generate_class_diagram(sample_classes)
    
    assert "User <|-- AdminUser" in diagram.content


def test_class_diagram_includes_methods(renderer, sample_classes):
    """Test class diagram includes methods."""
    diagram = renderer.generate_class_diagram(sample_classes, include_methods=True)
    
    assert "save" in diagram.content


def test_class_diagram_excludes_methods(renderer, sample_classes):
    """Test class diagram can exclude methods."""
    diagram = renderer.generate_class_diagram(sample_classes, include_methods=False)
    
    assert "save" not in diagram.content


def test_class_diagram_includes_attributes(renderer, sample_classes):
    """Test class diagram includes attributes."""
    diagram = renderer.generate_class_diagram(sample_classes, include_attributes=True)
    
    assert "+id: int" in diagram.content
    assert "+name: str" in diagram.content


# Tests for generate_erd

def test_generate_erd_basic(renderer):
    """Test basic ERD generation."""
    models = [
        {
            "name": "User",
            "fields": [
                {"name": "id", "type": "int", "constraints": ["PK"]},
                {"name": "email", "type": "string", "constraints": []},
            ],
            "relationships": [],
        }
    ]
    
    diagram = renderer.generate_erd(models)
    
    assert diagram.diagram_type == "erDiagram"
    assert "erDiagram" in diagram.content
    assert "User" in diagram.content


def test_erd_with_relationships(renderer):
    """Test ERD includes relationships."""
    models = [
        {
            "name": "User",
            "fields": [{"name": "id", "type": "int"}],
            "relationships": [
                {"target": "Order", "type": "one_to_many"}
            ],
        },
        {
            "name": "Order",
            "fields": [{"name": "id", "type": "int"}],
            "relationships": [],
        },
    ]
    
    diagram = renderer.generate_erd(models)
    
    assert "User" in diagram.content
    assert "Order" in diagram.content
    assert "||--o{" in diagram.content or "has" in diagram.content


def test_erd_field_constraints(renderer):
    """Test ERD includes field constraints."""
    models = [
        {
            "name": "User",
            "fields": [
                {"name": "id", "type": "int", "constraints": ["PK", "NOT NULL"]},
            ],
            "relationships": [],
        }
    ]
    
    diagram = renderer.generate_erd(models)
    
    assert "PK" in diagram.content


# Tests for generate_state_diagram

def test_generate_state_diagram_basic(renderer):
    """Test basic state diagram generation."""
    states = {
        "states": ["pending", "active", "completed"],
        "transitions": [
            {"from": "pending", "to": "active", "label": "start"},
            {"from": "active", "to": "completed", "label": "finish"},
        ],
        "final_states": ["completed"],
    }
    
    diagram = renderer.generate_state_diagram(states)
    
    assert diagram.diagram_type == "stateDiagram"
    assert "stateDiagram-v2" in diagram.content
    assert "pending" in diagram.content


def test_state_diagram_with_transitions(renderer):
    """Test state diagram includes transitions."""
    states = {
        "states": ["draft", "published"],
        "transitions": [
            {"from": "draft", "to": "published", "label": "publish"},
        ],
        "final_states": [],
    }
    
    diagram = renderer.generate_state_diagram(states)
    
    assert "draft --> published" in diagram.content
    assert "publish" in diagram.content


def test_state_diagram_initial_state(renderer):
    """Test state diagram marks initial state."""
    states = {
        "states": ["initial"],
        "transitions": [],
        "final_states": [],
    }
    
    diagram = renderer.generate_state_diagram(states)
    
    assert "[*] --> initial" in diagram.content


def test_state_diagram_final_states(renderer):
    """Test state diagram marks final states."""
    states = {
        "states": ["done"],
        "transitions": [],
        "final_states": ["done"],
    }
    
    diagram = renderer.generate_state_diagram(states)
    
    assert "done --> [*]" in diagram.content


# Tests for generate_sequence_diagram

def test_generate_sequence_diagram_basic(renderer):
    """Test basic sequence diagram generation."""
    routes = [
        {
            "actor": "Client",
            "target": "API",
            "method": "GET /users",
            "response": "200 OK",
        }
    ]
    
    diagram = renderer.generate_sequence_diagram(routes)
    
    assert diagram.diagram_type == "sequenceDiagram"
    assert "sequenceDiagram" in diagram.content
    assert "Client" in diagram.content


def test_sequence_diagram_participants(renderer):
    """Test sequence diagram declares participants."""
    routes = [
        {
            "actor": "Client",
            "target": "Server",
            "method": "POST /login",
            "response": "JWT token",
        }
    ]
    
    diagram = renderer.generate_sequence_diagram(routes)
    
    assert "participant Client" in diagram.content
    assert "participant Server" in diagram.content


def test_sequence_diagram_interactions(renderer):
    """Test sequence diagram shows interactions."""
    routes = [
        {
            "actor": "User",
            "target": "API",
            "method": "GET /data",
            "response": "JSON",
        }
    ]
    
    diagram = renderer.generate_sequence_diagram(routes)
    
    assert "User->>+API" in diagram.content
    assert "GET /data" in diagram.content


# Tests for generate_architecture_diagram

def test_generate_architecture_diagram_basic(renderer):
    """Test basic architecture diagram generation."""
    packages = [
        {"name": "api", "label": "API Layer", "dependencies": ["models"]},
        {"name": "models", "label": "Data Models", "dependencies": []},
    ]
    
    diagram = renderer.generate_architecture_diagram(packages)
    
    assert diagram.diagram_type == "architecture"
    assert "graph TD" in diagram.content
    assert "api" in diagram.content


def test_architecture_diagram_dependencies(renderer):
    """Test architecture diagram shows dependencies."""
    packages = [
        {"name": "frontend", "dependencies": ["api"]},
        {"name": "api", "dependencies": ["database"]},
        {"name": "database", "dependencies": []},
    ]
    
    diagram = renderer.generate_architecture_diagram(packages)
    
    assert "frontend --> api" in diagram.content
    assert "api --> database" in diagram.content


def test_architecture_diagram_labels(renderer):
    """Test architecture diagram uses labels."""
    packages = [
        {"name": "api", "label": "REST API", "dependencies": []},
    ]
    
    diagram = renderer.generate_architecture_diagram(packages)
    
    assert "api[REST API]" in diagram.content


# Tests for metadata

def test_diagram_metadata_class_count(renderer, sample_classes):
    """Test class diagram metadata includes counts."""
    diagram = renderer.generate_class_diagram(sample_classes)
    
    assert diagram.metadata["class_count"] == 2


def test_diagram_metadata_erd_counts(renderer):
    """Test ERD metadata includes counts."""
    models = [
        {"name": "User", "fields": [], "relationships": [{"target": "Order", "type": "one_to_many"}]},
        {"name": "Order", "fields": [], "relationships": []},
    ]
    
    diagram = renderer.generate_erd(models)
    
    assert diagram.metadata["entity_count"] == 2
    assert diagram.metadata["relationship_count"] == 1


def test_diagram_metadata_state_counts(renderer):
    """Test state diagram metadata includes counts."""
    states = {
        "states": ["a", "b", "c"],
        "transitions": [{"from": "a", "to": "b"}],
        "final_states": [],
    }
    
    diagram = renderer.generate_state_diagram(states)
    
    assert diagram.metadata["state_count"] == 3
    assert diagram.metadata["transition_count"] == 1


# Integration tests

def test_all_diagram_types_generate_successfully(renderer, sample_classes):
    """Test all 5 diagram types can be generated."""
    # Class diagram
    class_diagram = renderer.generate_class_diagram(sample_classes)
    assert "classDiagram" in class_diagram.content
    
    # ERD
    models = [{"name": "User", "fields": [], "relationships": []}]
    erd = renderer.generate_erd(models)
    assert "erDiagram" in erd.content
    
    # State diagram
    states = {"states": ["a"], "transitions": [], "final_states": []}
    state_diagram = renderer.generate_state_diagram(states)
    assert "stateDiagram" in state_diagram.content
    
    # Sequence diagram
    routes = [{"actor": "A", "target": "B", "method": "call", "response": "ok"}]
    seq_diagram = renderer.generate_sequence_diagram(routes)
    assert "sequenceDiagram" in seq_diagram.content
    
    # Architecture diagram
    packages = [{"name": "pkg", "dependencies": []}]
    arch_diagram = renderer.generate_architecture_diagram(packages)
    assert "graph TD" in arch_diagram.content
