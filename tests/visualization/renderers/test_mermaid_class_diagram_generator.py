"""
Tests for MermaidClassDiagramGenerator.

AC-ID: LENS-DASH-010
Author: Asif Hussain
Phase: 14
"""

from pathlib import Path

import pytest

from cortex.visualization.renderers.mermaid_class_diagram_generator import (
    MermaidClassDiagramGenerator,
    ClassInfo,
    MethodInfo,
    AttributeInfo,
)


@pytest.fixture
def sample_classes() -> list[dict]:
    """Sample class data for testing."""
    return [
        {
            "name": "BaseClass",
            "docstring": "Base class for testing",
            "methods": [
                {
                    "name": "__init__",
                    "visibility": "public",
                    "params": ["self", "name: str"],
                    "return_type": "None",
                },
                {
                    "name": "process",
                    "visibility": "public",
                    "params": ["self", "data: dict"],
                    "return_type": "bool",
                },
            ],
            "attributes": [
                {"name": "name", "type": "str", "visibility": "public"},
                {"name": "_internal", "type": "int", "visibility": "private"},
            ],
            "bases": [],
        },
        {
            "name": "SubClass",
            "docstring": "Derived class",
            "methods": [
                {
                    "name": "process",
                    "visibility": "public",
                    "params": ["self", "data: dict"],
                    "return_type": "bool",
                },
            ],
            "attributes": [],
            "bases": ["BaseClass"],
        },
    ]


@pytest.fixture
def generator() -> MermaidClassDiagramGenerator:
    """Create generator instance."""
    return MermaidClassDiagramGenerator()


class TestAttributeInfo:
    """Test AttributeInfo dataclass."""

    def test_initialization(self) -> None:
        """Test AttributeInfo initialization."""
        attr = AttributeInfo(name="name", type_hint="str", visibility="public")
        
        assert attr.name == "name"
        assert attr.type_hint == "str"
        assert attr.visibility == "public"

    def test_to_mermaid_public(self) -> None:
        """Test Mermaid format for public attribute."""
        attr = AttributeInfo(name="name", type_hint="str", visibility="public")
        
        result = attr.to_mermaid()
        
        assert result == "+name: str"

    def test_to_mermaid_private(self) -> None:
        """Test Mermaid format for private attribute."""
        attr = AttributeInfo(name="_value", type_hint="int", visibility="private")
        
        result = attr.to_mermaid()
        
        assert result == "-_value: int"

    def test_to_mermaid_protected(self) -> None:
        """Test Mermaid format for protected attribute."""
        attr = AttributeInfo(name="_data", type_hint="dict", visibility="protected")
        
        result = attr.to_mermaid()
        
        assert result == "#_data: dict"


class TestMethodInfo:
    """Test MethodInfo dataclass."""

    def test_initialization(self) -> None:
        """Test MethodInfo initialization."""
        method = MethodInfo(
            name="process",
            visibility="public",
            params=["self", "data: dict"],
            return_type="bool",
        )
        
        assert method.name == "process"
        assert method.visibility == "public"
        assert len(method.params) == 2

    def test_to_mermaid_public_method(self) -> None:
        """Test Mermaid format for public method."""
        method = MethodInfo(
            name="process",
            visibility="public",
            params=["self", "data: dict"],
            return_type="bool",
        )
        
        result = method.to_mermaid()
        
        assert result == "+process(data: dict) bool"

    def test_to_mermaid_private_method(self) -> None:
        """Test Mermaid format for private method."""
        method = MethodInfo(
            name="_internal",
            visibility="private",
            params=["self"],
            return_type="None",
        )
        
        result = method.to_mermaid()
        
        assert result == "-_internal() None"

    def test_to_mermaid_static_method(self) -> None:
        """Test Mermaid format for static method."""
        method = MethodInfo(
            name="create",
            visibility="public",
            params=["cls", "name: str"],
            return_type="BaseClass",
            is_static=True,
        )
        
        result = method.to_mermaid()
        
        assert result == "+create(name: str) BaseClass$"


class TestClassInfo:
    """Test ClassInfo dataclass."""

    def test_from_dict(self) -> None:
        """Test creating ClassInfo from dict."""
        class_data = {
            "name": "TestClass",
            "docstring": "Test class",
            "methods": [
                {
                    "name": "method1",
                    "visibility": "public",
                    "params": ["self"],
                    "return_type": "None",
                }
            ],
            "attributes": [
                {"name": "attr1", "type": "str", "visibility": "public"}
            ],
            "bases": ["BaseClass"],
        }
        
        class_info = ClassInfo.from_dict(class_data)
        
        assert class_info.name == "TestClass"
        assert len(class_info.methods) == 1
        assert len(class_info.attributes) == 1
        assert class_info.bases == ["BaseClass"]

    def test_to_mermaid_class_definition(self) -> None:
        """Test Mermaid class definition generation."""
        class_info = ClassInfo(
            name="TestClass",
            methods=[
                MethodInfo("method1", "public", ["self"], "None")
            ],
            attributes=[
                AttributeInfo("attr1", "str", "public")
            ],
            bases=[],
        )
        
        result = class_info.to_mermaid()
        
        assert "class TestClass" in result
        assert "+attr1: str" in result
        assert "+method1() None" in result


class TestMermaidClassDiagramGenerator:
    """Test MermaidClassDiagramGenerator."""

    def test_initialization(
        self, generator: MermaidClassDiagramGenerator
    ) -> None:
        """Test generator initialization."""
        assert generator.direction == "TB"

    def test_generate_diagram(
        self, generator: MermaidClassDiagramGenerator, sample_classes: list[dict]
    ) -> None:
        """Test generating class diagram."""
        result = generator.generate_diagram(sample_classes)
        
        assert result.startswith("classDiagram")
        assert "direction TB" in result
        assert "class BaseClass" in result
        assert "class SubClass" in result
        assert "BaseClass <|-- SubClass" in result

    def test_inheritance_relationships(
        self, generator: MermaidClassDiagramGenerator
    ) -> None:
        """Test inheritance relationship generation."""
        classes = [
            {
                "name": "Parent",
                "methods": [],
                "attributes": [],
                "bases": [],
            },
            {
                "name": "Child",
                "methods": [],
                "attributes": [],
                "bases": ["Parent"],
            },
        ]
        
        result = generator.generate_diagram(classes)
        
        assert "Parent <|-- Child" in result

    def test_multiple_inheritance(
        self, generator: MermaidClassDiagramGenerator
    ) -> None:
        """Test multiple inheritance relationships."""
        classes = [
            {
                "name": "Mixin1",
                "methods": [],
                "attributes": [],
                "bases": [],
            },
            {
                "name": "Mixin2",
                "methods": [],
                "attributes": [],
                "bases": [],
            },
            {
                "name": "Child",
                "methods": [],
                "attributes": [],
                "bases": ["Mixin1", "Mixin2"],
            },
        ]
        
        result = generator.generate_diagram(classes)
        
        assert "Mixin1 <|-- Child" in result
        assert "Mixin2 <|-- Child" in result

    def test_method_visibility_symbols(
        self, generator: MermaidClassDiagramGenerator
    ) -> None:
        """Test method visibility symbols."""
        classes = [
            {
                "name": "TestClass",
                "methods": [
                    {
                        "name": "public_method",
                        "visibility": "public",
                        "params": ["self"],
                        "return_type": "None",
                    },
                    {
                        "name": "_private_method",
                        "visibility": "private",
                        "params": ["self"],
                        "return_type": "None",
                    },
                ],
                "attributes": [],
                "bases": [],
            }
        ]
        
        result = generator.generate_diagram(classes)
        
        assert "+public_method()" in result
        assert "-_private_method()" in result

    def test_attribute_visibility_symbols(
        self, generator: MermaidClassDiagramGenerator
    ) -> None:
        """Test attribute visibility symbols."""
        classes = [
            {
                "name": "TestClass",
                "methods": [],
                "attributes": [
                    {"name": "public_attr", "type": "str", "visibility": "public"},
                    {"name": "_private_attr", "type": "int", "visibility": "private"},
                ],
                "bases": [],
            }
        ]
        
        result = generator.generate_diagram(classes)
        
        assert "+public_attr: str" in result
        assert "-_private_attr: int" in result

    def test_empty_class_list(
        self, generator: MermaidClassDiagramGenerator
    ) -> None:
        """Test generating diagram with no classes."""
        result = generator.generate_diagram([])
        
        assert result.startswith("classDiagram")
        assert "direction TB" in result

    def test_generate_to_file(
        self, generator: MermaidClassDiagramGenerator, sample_classes: list[dict], tmp_path: Path
    ) -> None:
        """Test generating diagram to file."""
        output_file = tmp_path / "class_diagram.mmd"
        
        generator.generate_to_file(sample_classes, output_file)
        
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "classDiagram" in content
        assert "class BaseClass" in content

    def test_custom_direction(self) -> None:
        """Test custom diagram direction."""
        generator = MermaidClassDiagramGenerator(direction="LR")
        
        result = generator.generate_diagram([])
        
        assert "direction LR" in result

    def test_class_without_methods_or_attributes(
        self, generator: MermaidClassDiagramGenerator
    ) -> None:
        """Test class with no methods or attributes."""
        classes = [
            {
                "name": "EmptyClass",
                "methods": [],
                "attributes": [],
                "bases": [],
            }
        ]
        
        result = generator.generate_diagram(classes)
        
        assert "class EmptyClass" in result
