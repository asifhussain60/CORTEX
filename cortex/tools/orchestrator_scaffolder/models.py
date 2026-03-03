"""
Orchestrator Scaffolder models — ScaffoldType, ScaffoldConfig, ScaffoldedFile, ScaffoldResult.

Phase 103-i: extracted from orchestrator_scaffolder.py (1,455L) god-object.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional


class ScaffoldType(Enum):
    """Types of scaffold outputs."""

    ORCHESTRATOR = auto()
    TEST = auto()
    CONFIG = auto()
    INTEGRATION = auto()
    FULL = auto()


@dataclass
class ScaffoldConfig:
    """Configuration for scaffolding."""

    output_dir: Path = field(default_factory=lambda: Path("src/orchestrators"))
    domain: str = "general"
    tier: int = 1
    include_tests: bool = True
    include_config: bool = True
    include_integrations: bool = True
    scaffold_type: ScaffoldType = ScaffoldType.FULL
    type_hints: bool = True
    docstrings: bool = True
    async_support: bool = False
    class_suffix: str = "Orchestrator"
    test_prefix: str = "test_"
    config_suffix: str = "_config"
    overwrite: bool = False
    dry_run: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScaffoldedFile:
    """A scaffolded file."""

    path: Path
    content: str
    file_type: str
    generated_at: datetime = field(default_factory=datetime.now)

    def write(self, base_dir: Optional[Path] = None) -> Path:
        """Write file to disk."""
        output_path = base_dir / self.path if base_dir else self.path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.content)
        return output_path

    @property
    def line_count(self) -> int:
        """Get number of lines in file."""
        return len(self.content.splitlines())


@dataclass
class ScaffoldResult:
    """Result of scaffolding operation."""

    success: bool
    files: List[ScaffoldedFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_file(self, file: ScaffoldedFile) -> None:
        """Add a scaffolded file."""
        self.files.append(file)

    def add_error(self, message: str) -> None:
        """Add an error."""
        self.errors.append(message)
        self.success = False

    def add_warning(self, message: str) -> None:
        """Add a warning."""
        self.warnings.append(message)

    @property
    def total_lines(self) -> int:
        """Get total lines of generated code."""
        return sum(f.line_count for f in self.files)

    def write_all(self, base_dir: Optional[Path] = None) -> List[Path]:
        """Write all files to disk."""
        written = []
        for f in self.files:
            written.append(f.write(base_dir))
        return written
