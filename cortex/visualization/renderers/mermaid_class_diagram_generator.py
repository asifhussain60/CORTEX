"""
Mermaid Class Diagram Generator.

Generates Mermaid.js UML class diagrams from Python class metadata.
Supports inheritance relationships, method/attribute visibility, and type hints.

AC-ID: LENS-DASH-010
Author: Asif Hussain
Phase: 14
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AttributeInfo:
    """Represents a class attribute."""

    name: str
    type_hint: str
    visibility: str  # public, private, protected

    def to_mermaid(self) -> str:
        """
        Convert to Mermaid attribute format.

        Returns:
            Mermaid attribute string with visibility symbol

        Example:
            >>> attr = AttributeInfo("name", "str", "public")
            >>> attr.to_mermaid()
            '+name: str'
        """
        visibility_map = {
            "public": "+",
            "private": "-",
            "protected": "#",
        }
        symbol = visibility_map.get(self.visibility, "+")
        return f"{symbol}{self.name}: {self.type_hint}"


@dataclass
class MethodInfo:
    """Represents a class method."""

    name: str
    visibility: str  # public, private, protected
    params: list[str]
    return_type: str
    is_static: bool = False
    is_abstract: bool = False

    def to_mermaid(self) -> str:
        """
        Convert to Mermaid method format.

        Returns:
            Mermaid method string with visibility symbol

        Example:
            >>> method = MethodInfo("process", "public", ["self", "data: dict"], "bool")
            >>> method.to_mermaid()
            '+process(data: dict) bool'
        """
        visibility_map = {
            "public": "+",
            "private": "-",
            "protected": "#",
        }
        symbol = visibility_map.get(self.visibility, "+")

        # Remove 'self' and 'cls' from params
        filtered_params = [p for p in self.params if p not in ["self", "cls"]]
        params_str = ", ".join(filtered_params)

        # Add static/abstract markers
        suffix = ""
        if self.is_static:
            suffix = "$"
        elif self.is_abstract:
            suffix = "*"

        return f"{symbol}{self.name}({params_str}) {self.return_type}{suffix}"


@dataclass
class ClassInfo:
    """Represents a Python class."""

    name: str
    methods: list[MethodInfo] = field(default_factory=list)
    attributes: list[AttributeInfo] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)
    is_abstract: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClassInfo":
        """
        Create ClassInfo from dictionary.

        Args:
            data: Dictionary with class metadata

        Returns:
            ClassInfo instance

        Example:
            >>> class_data = {
            ...     "name": "TestClass",
            ...     "methods": [
            ...         {
            ...             "name": "method1",
            ...             "visibility": "public",
            ...             "params": ["self"],
            ...             "return_type": "None",
            ...         }
            ...     ],
            ...     "attributes": [
            ...         {"name": "attr1", "type": "str", "visibility": "public"}
            ...     ],
            ...     "bases": ["BaseClass"],
            ... }
            >>> class_info = ClassInfo.from_dict(class_data)
        """
        methods = [
            MethodInfo(
                name=m["name"],
                visibility=m["visibility"],
                params=m["params"],
                return_type=m["return_type"],
                is_static=m.get("is_static", False),
                is_abstract=m.get("is_abstract", False),
            )
            for m in data.get("methods", [])
        ]

        attributes = [
            AttributeInfo(
                name=a["name"],
                type_hint=a["type"],
                visibility=a["visibility"],
            )
            for a in data.get("attributes", [])
        ]

        return cls(
            name=data["name"],
            methods=methods,
            attributes=attributes,
            bases=data.get("bases", []),
            is_abstract=data.get("is_abstract", False),
        )

    def to_mermaid(self) -> str:
        """
        Convert to Mermaid class definition.

        Returns:
            Mermaid class definition with methods and attributes

        Example:
            >>> class_info.to_mermaid()
            'class TestClass {\\n  +attr1: str\\n  +method1() None\\n}'
        """
        lines = [f"class {self.name} {{"]

        # Add attributes
        for attr in self.attributes:
            lines.append(f"  {attr.to_mermaid()}")

        # Add methods
        for method in self.methods:
            lines.append(f"  {method.to_mermaid()}")

        lines.append("}")

        # Add abstract marker if needed
        if self.is_abstract:
            lines.append(f"<<abstract>> {self.name}")

        return "\n".join(lines)


class MermaidClassDiagramGenerator:
    """
    Generates Mermaid.js UML class diagrams from Python class metadata.

    Supports:
    - Inheritance relationships
    - Method and attribute visibility (public/private/protected)
    - Type hints
    - Static and abstract methods
    - Multiple inheritance

    Example:
        >>> generator = MermaidClassDiagramGenerator()
        >>> diagram = generator.generate_diagram(classes)
        >>> generator.generate_to_file(classes, Path("diagram.mmd"))
    """

    def __init__(self, direction: str = "TB") -> None:
        """
        Initialize Mermaid Class Diagram Generator.

        Args:
            direction: Diagram direction (TB=top-bottom, LR=left-right)
        """
        self.direction = direction

    def generate_diagram(self, classes: list[dict[str, Any]]) -> str:
        """
        Generate Mermaid class diagram from class metadata.

        Args:
            classes: List of class dictionaries with keys:
                    - name: Class name
                    - methods: List of method dicts
                    - attributes: List of attribute dicts
                    - bases: List of base class names
                    - is_abstract: Optional boolean

        Returns:
            Mermaid diagram as string

        Example:
            >>> classes = [
            ...     {
            ...         "name": "BaseClass",
            ...         "methods": [
            ...             {
            ...                 "name": "process",
            ...                 "visibility": "public",
            ...                 "params": ["self", "data: dict"],
            ...                 "return_type": "bool",
            ...             }
            ...         ],
            ...         "attributes": [
            ...             {"name": "name", "type": "str", "visibility": "public"}
            ...         ],
            ...         "bases": [],
            ...     },
            ...     {
            ...         "name": "SubClass",
            ...         "methods": [],
            ...         "attributes": [],
            ...         "bases": ["BaseClass"],
            ...     }
            ... ]
            >>> diagram = generator.generate_diagram(classes)
            >>> "classDiagram" in diagram
            True
            >>> "BaseClass <|-- SubClass" in diagram
            True
        """
        lines = [
            "classDiagram",
            f"  direction {self.direction}",
            "",
        ]

        # Convert to ClassInfo objects
        class_infos = [ClassInfo.from_dict(c) for c in classes]

        # Generate class definitions
        for class_info in class_infos:
            lines.append(class_info.to_mermaid())
            lines.append("")

        # Generate inheritance relationships
        relationships = self._generate_relationships(class_infos)
        if relationships:
            lines.extend(relationships)

        return "\n".join(lines)

    def _generate_relationships(
        self, class_infos: list[ClassInfo]
    ) -> list[str]:
        """
        Generate inheritance relationships.

        Args:
            class_infos: List of ClassInfo objects

        Returns:
            List of Mermaid relationship strings

        Example:
            >>> relationships = generator._generate_relationships(class_infos)
            >>> relationships
            ['BaseClass <|-- SubClass']
        """
        relationships = []

        # Build class name set for validation
        class_names = {c.name for c in class_infos}

        for class_info in class_infos:
            for base in class_info.bases:
                # Only generate relationship if base class is in diagram
                if base in class_names:
                    relationships.append(f"{base} <|-- {class_info.name}")

        return relationships

    def generate_to_file(
        self, classes: list[dict[str, Any]], output_path: Path
    ) -> None:
        """
        Generate Mermaid diagram to file.

        Args:
            classes: List of class dictionaries
            output_path: Output file path (.mmd extension recommended)

        Example:
            >>> generator.generate_to_file(classes, Path("diagram.mmd"))
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        diagram = self.generate_diagram(classes)

        with open(output_path, "w") as f:
            f.write(diagram)
