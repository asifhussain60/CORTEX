"""
Enhanced Mermaid Renderer for CORTEX Visualization System.

Unified Mermaid diagram generator supporting 5 diagram types:
1. Class diagrams (UML from AST)
2. Entity-Relationship Diagrams (database models)
3. State machine diagrams (workflow states)
4. Sequence diagrams (API interactions)
5. Architecture diagrams (system components)

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
Task: 009 - Enhanced Mermaid Generator
AC-ID: LENS-DASH-003
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class MermaidDiagram:
    """
    Represents a generated Mermaid diagram.
    
    Attributes:
        diagram_type: Type of diagram (classDiagram, erDiagram, stateDiagram, etc.)
        content: Mermaid syntax string
        metadata: Additional diagram information
    """
    diagram_type: str
    content: str
    metadata: Dict


class MermaidRenderer:
    """
    Unified Mermaid diagram generator.
    
    Supports 5 diagram types without graphviz dependency:
    - Class Diagrams: UML from Python classes
    - ERD: Database models and relationships
    - State Diagrams: Workflow state machines
    - Sequence Diagrams: API call sequences
    - Architecture Diagrams: System component structure
    
    Example:
        >>> renderer = MermaidRenderer()
        >>> ast_data = {"classes": [...]}
        >>> diagram = renderer.generate_class_diagram(ast_data)
        >>> print(diagram.content)  # Valid Mermaid syntax
    """
    
    def __init__(self, repo_path: Optional[Path] = None) -> None:
        """
        Initialize Mermaid renderer.
        
        Args:
            repo_path: Optional repository path for context
        """
        self.repo_path = repo_path or Path.cwd()
    
    # =========================================================================
    # 1. CLASS DIAGRAMS
    # =========================================================================
    
    def generate_class_diagram(
        self,
        ast_analysis: Dict,
        include_methods: bool = True,
        include_attributes: bool = True
    ) -> MermaidDiagram:
        """
        Generate UML class diagram from AST analysis.
        
        Args:
            ast_analysis: AST dict with 'classes' key
            include_methods: Whether to include methods
            include_attributes: Whether to include attributes
        
        Returns:
            MermaidDiagram with class diagram syntax
        
        Example:
            >>> ast_data = {"classes": [{"name": "User", "methods": [...]}]}
            >>> diagram = renderer.generate_class_diagram(ast_data)
            >>> "classDiagram" in diagram.content
            True
        """
        classes = ast_analysis.get("classes", [])
        
        lines = ["classDiagram"]
        
        # Generate class definitions
        for cls in classes:
            class_def = self._generate_class_definition(
                cls,
                include_methods,
                include_attributes
            )
            lines.extend(class_def)
        
        # Generate inheritance relationships
        for cls in classes:
            bases = cls.get("bases", [])
            for base in bases:
                lines.append(f"    {base} <|-- {cls['name']}")
        
        content = "\n".join(lines)
        
        return MermaidDiagram(
            diagram_type="classDiagram",
            content=content,
            metadata={
                "class_count": len(classes),
                "include_methods": include_methods,
                "include_attributes": include_attributes,
            }
        )
    
    # =========================================================================
    # 2. ENTITY-RELATIONSHIP DIAGRAMS (NEW)
    # =========================================================================
    
    def generate_erd(
        self,
        database_models: List[Dict]
    ) -> MermaidDiagram:
        """
        Generate Entity-Relationship Diagram from database models.
        
        Detects SQLAlchemy, Django, and generic model patterns.
        
        Args:
            database_models: List of model dicts with fields and relationships
        
        Returns:
            MermaidDiagram with ERD syntax
        
        Example:
            >>> models = [{"name": "User", "fields": [{"name": "id", "type": "int"}]}]
            >>> diagram = renderer.generate_erd(models)
            >>> "erDiagram" in diagram.content
            True
        """
        lines = ["erDiagram"]
        
        # Define entities with attributes
        for model in database_models:
            entity_lines = self._generate_entity_definition(model)
            lines.extend(entity_lines)
        
        # Define relationships
        for model in database_models:
            relationships = model.get("relationships", [])
            for rel in relationships:
                rel_line = self._generate_relationship(
                    model["name"],
                    rel["target"],
                    rel["type"]
                )
                lines.append(rel_line)
        
        content = "\n".join(lines)
        
        return MermaidDiagram(
            diagram_type="erDiagram",
            content=content,
            metadata={
                "entity_count": len(database_models),
                "relationship_count": sum(
                    len(m.get("relationships", []))
                    for m in database_models
                ),
            }
        )
    
    # =========================================================================
    # 3. STATE MACHINE DIAGRAMS (NEW)
    # =========================================================================
    
    def generate_state_diagram(
        self,
        state_enum: Dict
    ) -> MermaidDiagram:
        """
        Generate state machine diagram from state enum or workflow.
        
        Args:
            state_enum: Dict with 'states' and 'transitions' keys
        
        Returns:
            MermaidDiagram with state diagram syntax
        
        Example:
            >>> states = {"states": ["pending", "active"], "transitions": [...]}
            >>> diagram = renderer.generate_state_diagram(states)
            >>> "stateDiagram-v2" in diagram.content
            True
        """
        states = state_enum.get("states", [])
        transitions = state_enum.get("transitions", [])
        
        lines = ["stateDiagram-v2"]
        lines.append("    [*] --> " + states[0] if states else "")
        
        # Add state transitions
        for transition in transitions:
            from_state = transition.get("from")
            to_state = transition.get("to")
            label = transition.get("label", "")
            
            if label:
                lines.append(f"    {from_state} --> {to_state}: {label}")
            else:
                lines.append(f"    {from_state} --> {to_state}")
        
        # Mark final states
        final_states = state_enum.get("final_states", [])
        for final in final_states:
            lines.append(f"    {final} --> [*]")
        
        content = "\n".join(lines)
        
        return MermaidDiagram(
            diagram_type="stateDiagram",
            content=content,
            metadata={
                "state_count": len(states),
                "transition_count": len(transitions),
            }
        )
    
    # =========================================================================
    # 4. SEQUENCE DIAGRAMS (NEW)
    # =========================================================================
    
    def generate_sequence_diagram(
        self,
        api_routes: List[Dict]
    ) -> MermaidDiagram:
        """
        Generate sequence diagram from API routes or interaction flows.
        
        Args:
            api_routes: List of API route dicts with 'actor', 'target', 'method'
        
        Returns:
            MermaidDiagram with sequence diagram syntax
        
        Example:
            >>> routes = [{"actor": "Client", "target": "API", "method": "GET /users"}]
            >>> diagram = renderer.generate_sequence_diagram(routes)
            >>> "sequenceDiagram" in diagram.content
            True
        """
        lines = ["sequenceDiagram"]
        
        # Extract unique participants
        participants = set()
        for route in api_routes:
            participants.add(route.get("actor", "Client"))
            participants.add(route.get("target", "Server"))
        
        # Declare participants
        for participant in sorted(participants):
            lines.append(f"    participant {participant}")
        
        # Generate interactions
        for route in api_routes:
            actor = route.get("actor", "Client")
            target = route.get("target", "Server")
            method = route.get("method", "")
            response = route.get("response", "")
            
            # Request
            lines.append(f"    {actor}->>+{target}: {method}")
            
            # Response
            if response:
                lines.append(f"    {target}-->>-{actor}: {response}")
        
        content = "\n".join(lines)
        
        return MermaidDiagram(
            diagram_type="sequenceDiagram",
            content=content,
            metadata={
                "participant_count": len(participants),
                "interaction_count": len(api_routes),
            }
        )
    
    # =========================================================================
    # 5. ARCHITECTURE DIAGRAMS (NEW)
    # =========================================================================
    
    def generate_architecture_diagram(
        self,
        packages: List[Dict]
    ) -> MermaidDiagram:
        """
        Generate architecture/component diagram from package structure.
        
        Args:
            packages: List of package dicts with 'name' and 'dependencies'
        
        Returns:
            MermaidDiagram with graph syntax
        
        Example:
            >>> pkgs = [{"name": "api", "dependencies": ["models"]}]
            >>> diagram = renderer.generate_architecture_diagram(pkgs)
            >>> "graph" in diagram.content
            True
        """
        lines = ["graph TD"]
        
        # Generate nodes
        for pkg in packages:
            name = pkg["name"]
            label = pkg.get("label", name)
            lines.append(f"    {name}[{label}]")
        
        # Generate dependency arrows
        for pkg in packages:
            source = pkg["name"]
            deps = pkg.get("dependencies", [])
            
            for dep in deps:
                lines.append(f"    {source} --> {dep}")
        
        content = "\n".join(lines)
        
        return MermaidDiagram(
            diagram_type="architecture",
            content=content,
            metadata={
                "package_count": len(packages),
                "dependency_count": sum(
                    len(p.get("dependencies", []))
                    for p in packages
                ),
            }
        )
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _generate_class_definition(
        self,
        cls: Dict,
        include_methods: bool,
        include_attributes: bool
    ) -> List[str]:
        """Generate Mermaid class definition lines."""
        lines = []
        class_name = cls["name"]
        
        lines.append(f"    class {class_name} {{")
        
        # Add attributes
        if include_attributes:
            attributes = cls.get("attributes", [])
            for attr in attributes:
                attr_type = attr.get("type", "Any")
                lines.append(f"        +{attr['name']}: {attr_type}")
        
        # Add methods
        if include_methods:
            methods = cls.get("methods", [])
            for method in methods:
                params = method.get("parameters", [])
                param_str = ", ".join(
                    f"{p['name']}: {p.get('type', 'Any')}"
                    for p in params
                    if p['name'] not in ['self', 'cls']
                )
                return_type = method.get("return_type", "None")
                lines.append(f"        +{method['name']}({param_str}) {return_type}")
        
        lines.append("    }")
        
        return lines
    
    def _generate_entity_definition(self, model: Dict) -> List[str]:
        """Generate ERD entity definition."""
        lines = []
        entity_name = model["name"]
        
        lines.append(f"    {entity_name} {{")
        
        fields = model.get("fields", [])
        for field in fields:
            field_type = field.get("type", "string")
            field_name = field.get("name", "")
            constraints = field.get("constraints", [])
            
            constraint_str = " ".join(constraints) if constraints else ""
            lines.append(f"        {field_type} {field_name} {constraint_str}")
        
        lines.append("    }")
        
        return lines
    
    def _generate_relationship(
        self,
        source: str,
        target: str,
        rel_type: str
    ) -> str:
        """Generate ERD relationship line."""
        # Mermaid ERD relationship syntax
        rel_map = {
            "one_to_one": "||--||",
            "one_to_many": "||--o{",
            "many_to_one": "}o--||",
            "many_to_many": "}o--o{",
        }
        
        symbol = rel_map.get(rel_type, "||--o{")
        return f"    {source} {symbol} {target}: has"
