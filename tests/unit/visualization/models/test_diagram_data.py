"""
Unit tests for DiagramData model (Phase 0).

Tests diagram data structures for Mermaid, PlantUML, and D3.js visualizations.

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import json

# Direct import to avoid circular dependency
import importlib.util

test_file = Path(__file__)
tests_dir = test_file.parent.parent.parent.parent
project_root = tests_dir.parent
diagram_file = project_root / "cortex" / "visualization" / "models" / "diagram_data.py"

spec = importlib.util.spec_from_file_location("diagram_data", diagram_file)
diagram_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagram_module)

DiagramData = diagram_module.DiagramData
DiagramType = diagram_module.DiagramType
MermaidDiagram = diagram_module.MermaidDiagram
PlantUMLDiagram = diagram_module.PlantUMLDiagram
D3Diagram = diagram_module.D3Diagram


class TestDiagramType:
    """Test DiagramType enum."""
    
    def test_all_diagram_types(self):
        """Test that all expected diagram types exist."""
        assert hasattr(DiagramType, "MERMAID")
        assert hasattr(DiagramType, "PLANTUML")
        assert hasattr(DiagramType, "D3")
    
    def test_diagram_type_values(self):
        """Test diagram type string values."""
        assert DiagramType.MERMAID.value == "mermaid"
        assert DiagramType.PLANTUML.value == "plantuml"
        assert DiagramType.D3.value == "d3"


class TestDiagramData:
    """Test DiagramData base class."""
    
    def test_create_basic_diagram(self):
        """Test creating a basic diagram."""
        diagram = DiagramData(
            diagram_type=DiagramType.MERMAID,
            title="Test Architecture",
            content="graph TD\n  A --> B",
            metadata={}
        )
        
        assert diagram.diagram_type == DiagramType.MERMAID
        assert diagram.title == "Test Architecture"
        assert "A --> B" in diagram.content
        assert isinstance(diagram.metadata, dict)
    
    def test_diagram_with_metadata(self):
        """Test diagram with rich metadata."""
        metadata = {
            "author": "CORTEX",
            "generated": "2026-02-04",
            "repo": "test-repo",
            "layers": ["backend", "frontend"]
        }
        
        diagram = DiagramData(
            diagram_type=DiagramType.PLANTUML,
            title="System Design",
            content="@startuml\nclass User\n@enduml",
            metadata=metadata
        )
        
        assert diagram.metadata["author"] == "CORTEX"
        assert diagram.metadata["repo"] == "test-repo"
        assert len(diagram.metadata["layers"]) == 2
    
    def test_to_dict_serialization(self):
        """Test diagram serialization to dictionary."""
        diagram = DiagramData(
            diagram_type=DiagramType.D3,
            title="Dependency Graph",
            content='{"nodes": [], "links": []}',
            metadata={"version": "1.0"}
        )
        
        data = diagram.to_dict()
        
        assert data["diagram_type"] == "d3"
        assert data["title"] == "Dependency Graph"
        assert data["content"] == '{"nodes": [], "links": []}'
        assert data["metadata"]["version"] == "1.0"
    
    def test_to_json_serialization(self):
        """Test diagram serialization to JSON string."""
        diagram = DiagramData(
            diagram_type=DiagramType.MERMAID,
            title="Flow Chart",
            content="flowchart LR\n  Start --> End",
            metadata={}
        )
        
        json_str = diagram.to_json()
        data = json.loads(json_str)
        
        assert data["diagram_type"] == "mermaid"
        assert data["title"] == "Flow Chart"
        assert "Start --> End" in data["content"]


class TestMermaidDiagram:
    """Test Mermaid-specific diagram functionality."""
    
    def test_create_mermaid_diagram(self):
        """Test creating a Mermaid diagram."""
        mermaid = MermaidDiagram(
            title="Class Diagram",
            content="classDiagram\n  Class01 <|-- Class02",
            metadata={"style": "dark"}
        )
        
        assert mermaid.diagram_type == DiagramType.MERMAID
        assert mermaid.title == "Class Diagram"
        assert "classDiagram" in mermaid.content
    
    def test_mermaid_flowchart(self):
        """Test Mermaid flowchart."""
        flowchart = MermaidDiagram(
            title="Request Flow",
            content="flowchart TD\n  A[Client] --> B[Server]\n  B --> C[Database]",
            metadata={"direction": "TD"}
        )
        
        assert "flowchart TD" in flowchart.content
        assert flowchart.metadata["direction"] == "TD"
    
    def test_mermaid_sequence_diagram(self):
        """Test Mermaid sequence diagram."""
        sequence = MermaidDiagram(
            title="Authentication Sequence",
            content="sequenceDiagram\n  User->>API: Login\n  API->>DB: Verify",
            metadata={"participants": ["User", "API", "DB"]}
        )
        
        assert "sequenceDiagram" in sequence.content
        assert len(sequence.metadata["participants"]) == 3


class TestPlantUMLDiagram:
    """Test PlantUML-specific diagram functionality."""
    
    def test_create_plantuml_diagram(self):
        """Test creating a PlantUML diagram."""
        plantuml = PlantUMLDiagram(
            title="Component Diagram",
            content="@startuml\ncomponent [Web] as web\n@enduml",
            metadata={"skin": "aws"}
        )
        
        assert plantuml.diagram_type == DiagramType.PLANTUML
        assert plantuml.title == "Component Diagram"
        assert "@startuml" in plantuml.content
        assert "@enduml" in plantuml.content
    
    def test_plantuml_class_diagram(self):
        """Test PlantUML class diagram."""
        class_diagram = PlantUMLDiagram(
            title="Domain Model",
            content="@startuml\nclass User {\n  +name: string\n}\n@enduml",
            metadata={"namespace": "domain"}
        )
        
        assert "class User" in class_diagram.content
        assert class_diagram.metadata["namespace"] == "domain"


class TestD3Diagram:
    """Test D3.js-specific diagram functionality."""
    
    def test_create_d3_diagram(self):
        """Test creating a D3 diagram with JSON data."""
        nodes = [
            {"id": "A", "label": "Module A"},
            {"id": "B", "label": "Module B"}
        ]
        links = [
            {"source": "A", "target": "B", "value": 1}
        ]
        
        d3_data = {
            "nodes": nodes,
            "links": links
        }
        
        d3 = D3Diagram(
            title="Dependency Graph",
            content=json.dumps(d3_data),
            metadata={"layout": "force"}
        )
        
        assert d3.diagram_type == DiagramType.D3
        assert "nodes" in d3.content
        assert "links" in d3.content
        
        # Verify JSON is valid
        parsed = json.loads(d3.content)
        assert len(parsed["nodes"]) == 2
        assert len(parsed["links"]) == 1
    
    def test_d3_hierarchical_data(self):
        """Test D3 diagram with hierarchical data."""
        tree_data = {
            "name": "root",
            "children": [
                {"name": "child1", "value": 10},
                {"name": "child2", "value": 20}
            ]
        }
        
        d3 = D3Diagram(
            title="Component Tree",
            content=json.dumps(tree_data),
            metadata={"layout": "tree", "orientation": "vertical"}
        )
        
        parsed = json.loads(d3.content)
        assert parsed["name"] == "root"
        assert len(parsed["children"]) == 2
        assert d3.metadata["layout"] == "tree"
    
    def test_d3_diagram_with_metadata(self):
        """Test D3 diagram with rich metadata."""
        d3 = D3Diagram(
            title="Network Topology",
            content='{"nodes": [], "edges": []}',
            metadata={
                "algorithm": "force-directed",
                "zoom_enabled": True,
                "pan_enabled": True,
                "node_size": "dynamic"
            }
        )
        
        assert d3.metadata["algorithm"] == "force-directed"
        assert d3.metadata["zoom_enabled"] is True


class TestDiagramInteroperability:
    """Test that different diagram types work together."""
    
    def test_multiple_diagram_types(self):
        """Test creating multiple diagram types."""
        mermaid = MermaidDiagram("Mermaid", "graph TD", {})
        plantuml = PlantUMLDiagram("PlantUML", "@startuml\n@enduml", {})
        d3 = D3Diagram("D3", '{"nodes": []}', {})
        
        diagrams = [mermaid, plantuml, d3]
        
        assert len(diagrams) == 3
        assert all(isinstance(d, DiagramData) for d in diagrams)
        assert diagrams[0].diagram_type == DiagramType.MERMAID
        assert diagrams[1].diagram_type == DiagramType.PLANTUML
        assert diagrams[2].diagram_type == DiagramType.D3
    
    def test_diagram_collection_serialization(self):
        """Test serializing a collection of diagrams."""
        diagrams = [
            MermaidDiagram("Architecture", "graph TD", {"layer": "system"}),
            PlantUMLDiagram("Classes", "@startuml\n@enduml", {"layer": "domain"}),
            D3Diagram("Dependencies", '{"nodes": []}', {"layer": "code"})
        ]
        
        serialized = [d.to_dict() for d in diagrams]
        
        assert len(serialized) == 3
        assert serialized[0]["diagram_type"] == "mermaid"
        assert serialized[1]["diagram_type"] == "plantuml"
        assert serialized[2]["diagram_type"] == "d3"
