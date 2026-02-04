"""
DiagramData models for visualization generation.

Supports Mermaid, PlantUML, and D3.js diagram formats for real-time
architecture visualization during repository onboarding.

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any
import json


class DiagramType(Enum):
    """
    Supported diagram types for visualization.
    
    - MERMAID: Mermaid.js (flowcharts, sequence, class diagrams)
    - PLANTUML: PlantUML (component, deployment, class diagrams)
    - D3: D3.js (force-directed graphs, trees, hierarchies)
    """
    MERMAID = "mermaid"
    PLANTUML = "plantuml"
    D3 = "d3"


@dataclass
class DiagramData:
    """
    Base diagram data structure for all visualization types.
    
    Attributes:
        diagram_type: Type of diagram (Mermaid, PlantUML, D3)
        title: Human-readable diagram title
        content: Diagram content (syntax varies by type)
        metadata: Additional diagram metadata (author, generated date, etc.)
    
    Example:
        >>> diagram = DiagramData(
        ...     diagram_type=DiagramType.MERMAID,
        ...     title="System Architecture",
        ...     content="graph TD\\n  A --> B",
        ...     metadata={"author": "CORTEX", "repo": "test"}
        ... )
        >>> diagram.to_dict()
        {'diagram_type': 'mermaid', 'title': 'System Architecture', ...}
    
    Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
    """
    diagram_type: DiagramType
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize diagram to dictionary.
        
        Returns:
            Dictionary with diagram_type, title, content, metadata
        
        Example:
            >>> diagram.to_dict()
            {
                'diagram_type': 'mermaid',
                'title': 'Architecture',
                'content': 'graph TD...',
                'metadata': {...}
            }
        """
        return {
            "diagram_type": self.diagram_type.value,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """
        Serialize diagram to JSON string.
        
        Returns:
            JSON string representation of diagram
        
        Example:
            >>> diagram.to_json()
            '{"diagram_type": "mermaid", "title": "Architecture", ...}'
        """
        return json.dumps(self.to_dict())


@dataclass
class MermaidDiagram(DiagramData):
    """
    Mermaid.js diagram for flowcharts, sequence diagrams, class diagrams.
    
    Attributes:
        title: Diagram title
        content: Mermaid syntax (e.g., "graph TD\\n  A --> B")
        metadata: Additional metadata (direction, style, theme)
    
    Mermaid Syntax Examples:
        - Flowchart: "flowchart TD\\n  A[Start] --> B[End]"
        - Sequence: "sequenceDiagram\\n  User->>API: Request"
        - Class: "classDiagram\\n  Class01 <|-- Class02"
    
    Usage:
        >>> mermaid = MermaidDiagram(
        ...     title="Request Flow",
        ...     content="flowchart LR\\n  Client --> Server",
        ...     metadata={"direction": "LR"}
        ... )
    
    Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 4
    """
    
    def __init__(self, title: str, content: str, metadata: Dict[str, Any]):
        """Initialize Mermaid diagram."""
        super().__init__(
            diagram_type=DiagramType.MERMAID,
            title=title,
            content=content,
            metadata=metadata
        )


@dataclass
class PlantUMLDiagram(DiagramData):
    """
    PlantUML diagram for component, deployment, and class diagrams.
    
    Attributes:
        title: Diagram title
        content: PlantUML syntax (must include @startuml/@enduml)
        metadata: Additional metadata (skin, namespace, theme)
    
    PlantUML Syntax Examples:
        - Component: "@startuml\\ncomponent [Web]\\n@enduml"
        - Class: "@startuml\\nclass User {\\n  +name\\n}\\n@enduml"
        - Deployment: "@startuml\\nnode Server\\n@enduml"
    
    Usage:
        >>> plantuml = PlantUMLDiagram(
        ...     title="Component View",
        ...     content="@startuml\\ncomponent [API]\\n@enduml",
        ...     metadata={"skin": "aws"}
        ... )
    
    Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 4
    """
    
    def __init__(self, title: str, content: str, metadata: Dict[str, Any]):
        """Initialize PlantUML diagram."""
        super().__init__(
            diagram_type=DiagramType.PLANTUML,
            title=title,
            content=content,
            metadata=metadata
        )


@dataclass
class D3Diagram(DiagramData):
    """
    D3.js diagram for interactive force-directed graphs and hierarchies.
    
    Attributes:
        title: Diagram title
        content: JSON string with D3 data structure (nodes, links, or tree)
        metadata: Additional metadata (layout, zoom, pan, algorithm)
    
    D3 Data Structure Examples:
        - Graph: {"nodes": [{"id": "A"}], "links": [{"source": "A", "target": "B"}]}
        - Tree: {"name": "root", "children": [{"name": "child1"}]}
        - Hierarchy: {"name": "root", "value": 100, "children": [...]}
    
    Usage:
        >>> d3_data = {"nodes": [{"id": "A"}], "links": []}
        >>> d3 = D3Diagram(
        ...     title="Dependency Graph",
        ...     content=json.dumps(d3_data),
        ...     metadata={"layout": "force", "zoom_enabled": True}
        ... )
    
    Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 5
    """
    
    def __init__(self, title: str, content: str, metadata: Dict[str, Any]):
        """Initialize D3 diagram."""
        super().__init__(
            diagram_type=DiagramType.D3,
            title=title,
            content=content,
            metadata=metadata
        )
