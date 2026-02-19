"""
FileFactory — Consolidated file creation with unified templates.

Merges 677+546 line factories into single canonical implementation.

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import textwrap


@dataclass
class FileTemplate:
    """Template for file creation."""
    
    name: str
    extension: str
    header: str
    body: str
    footer: Optional[str] = None


class FileFactory:
    """Consolidated factory for creating project files."""
    
    def __init__(self) -> None:
        """Initialize FileFactory with standard templates."""
        self.templates: Dict[str, FileTemplate] = self._load_templates()
    
    def _load_templates(self) -> Dict[str, FileTemplate]:
        """Load standard file templates.
        
        Returns:
            Dictionary mapping template names to FileTemplate instances.
        """
        return {
            "python": self._template_python(),
            "yaml": self._template_yaml(),
            "markdown": self._template_markdown(),
            "test": self._template_test(),
        }
    
    @staticmethod
    def _template_python() -> FileTemplate:
        """Create Python file template with docstring and type hints."""
        return FileTemplate(
            name="python",
            extension=".py",
            header='"""Module docstring.\n\nAuthority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)\n"""\n\n',
            body="",
            footer="\n\nif __name__ == '__main__':\n    pass\n",
        )
    
    @staticmethod
    def _template_yaml() -> FileTemplate:
        """Create YAML file template."""
        return FileTemplate(
            name="yaml",
            extension=".yaml",
            header="# ============================================================================\n# YAML Configuration\n# ============================================================================\n\n",
            body="",
            footer=None,
        )
    
    @staticmethod
    def _template_markdown() -> FileTemplate:
        """Create Markdown file template."""
        return FileTemplate(
            name="markdown",
            extension=".md",
            header="# Title\n\n",
            body="",
            footer=None,
        )
    
    @staticmethod
    def _template_test() -> FileTemplate:
        """Create test file template with pytest structure."""
        return FileTemplate(
            name="test",
            extension=".py",
            header='"""Test suite.\n\nAuthority: CORE-008 (TDD mandatory)\n"""\n\nimport pytest\n\n',
            body="",
            footer="\n\nif __name__ == '__main__':\n    pytest.main([__file__, '-v'])\n",
        )
    
    def create_python_file(
        self,
        path: Path,
        module_docstring: str = "Module docstring.",
        imports: Optional[List[str]] = None,
        content: str = "",
    ) -> None:
        """Create a Python file with optional imports and content.
        
        Args:
            path: File path to create.
            module_docstring: Module docstring (CORE-012).
            imports: List of import statements.
            content: Module body content.
            
        Raises:
            FileExistsError: If file already exists.
        """
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            f'"""Module: {module_docstring}',
            "",
            "Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)",
            '"""',
            "",
        ]
        
        if imports:
            lines.extend(imports)
            lines.append("")
        
        if content:
            lines.append(content)
        
        lines.append("")
        
        path.write_text("\n".join(lines))
    
    def create_yaml_file(
        self,
        path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        content: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a YAML file with metadata and content.
        
        Args:
            path: File path to create.
            metadata: Optional metadata dictionary.
            content: YAML content dictionary.
            
        Raises:
            FileExistsError: If file already exists.
        """
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        import yaml
        
        data = {}
        if metadata:
            data["metadata"] = metadata
        if content:
            data.update(content)
        
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
        path.write_text(yaml_str)
    
    def create_test_file(
        self,
        path: Path,
        test_class_name: str = "TestModule",
        test_methods: Optional[List[str]] = None,
    ) -> None:
        """Create a test file with pytest structure.
        
        Args:
            path: File path to create.
            test_class_name: Name of test class (CORE-028 PascalCase).
            test_methods: List of test method names.
            
        Raises:
            FileExistsError: If file already exists.
        """
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            '"""Test suite.',
            "",
            "Authority: CORE-008 (TDD mandatory) | CORE-011 (type hints) | CORE-012 (docstrings)",
            '"""',
            "",
            "import pytest",
            "",
            "",
            f"class {test_class_name}:",
            f'    """Test class for module testing."""',
            "",
        ]
        
        if test_methods:
            for method_name in test_methods:
                lines.extend([
                    f"    def test_{method_name}(self) -> None:",
                    f'        """Test: {method_name}."""',
                    "        assert True, 'Test placeholder'",
                    "",
                ])
        else:
            lines.extend([
                "    def test_placeholder(self) -> None:",
                '        """Placeholder test."""',
                "        assert True",
                "",
            ])
        
        lines.extend([
            "",
            "if __name__ == '__main__':",
            "    pytest.main([__file__, '-v'])",
            "",
        ])
        
        path.write_text("\n".join(lines))
    
    def create_markdown_file(
        self,
        path: Path,
        title: str,
        sections: Optional[List[tuple[str, str]]] = None,
    ) -> None:
        """Create a Markdown file with sections.
        
        Args:
            path: File path to create.
            title: Document title (becomes H1).
            sections: List of (section_title, section_content) tuples.
            
        Raises:
            FileExistsError: If file already exists.
        """
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [f"# {title}", ""]
        
        if sections:
            for section_title, section_content in sections:
                lines.append(f"## {section_title}")
                lines.append("")
                lines.append(section_content)
                lines.append("")
        
        path.write_text("\n".join(lines))


# Singleton instance
_factory_instance: Optional[FileFactory] = None


def get_file_factory() -> FileFactory:
    """Get or create the singleton FileFactory instance.
    
    Returns:
        FileFactory: The singleton instance.
    """
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = FileFactory()
    return _factory_instance
