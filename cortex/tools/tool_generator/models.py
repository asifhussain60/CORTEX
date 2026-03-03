"""
Tool Generator models — ToolType, GenerationConfig, GeneratedTool, GenerationResult.

Phase 103-j: extracted from tool_generator.py (1,426L) god-object.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, List, Optional


class ToolType(Enum):
    """Types of tools that can be generated."""

    CLI_COMMAND = auto()
    API_CLIENT = auto()
    TEST_HARNESS = auto()
    DOCUMENTATION = auto()
    CONFIG_VALIDATOR = auto()
    MOCK_SERVICE = auto()
    INTEGRATION_ADAPTER = auto()


@dataclass
class GenerationConfig:
    """Configuration for tool generation."""

    tool_type: ToolType
    output_dir: Path = field(default_factory=lambda: Path("generated"))
    include_tests: bool = True
    include_docs: bool = True
    python_version: str = "3.9"
    style_guide: str = "pep8"
    type_hints: bool = True
    docstrings: bool = True
    class_prefix: str = ""
    class_suffix: str = ""
    function_prefix: str = ""
    function_suffix: str = ""
    overwrite: bool = False
    dry_run: bool = False


@dataclass
class GeneratedTool:
    """A generated tool/file."""

    name: str
    tool_type: ToolType
    content: str
    path: Path
    template_source: str
    generated_at: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)

    def write(self, base_dir: Optional[Path] = None) -> Path:
        """Write the generated tool to disk."""
        output_path = base_dir / self.path if base_dir else self.path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.content)
        return output_path


@dataclass
class GenerationResult:
    """Result of tool generation."""

    success: bool
    tools: List[GeneratedTool] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_tool(self, tool: GeneratedTool) -> None:
        """Add a generated tool."""
        self.tools.append(tool)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.success = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
