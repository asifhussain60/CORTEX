"""
Data models for refactoring operations.

AC_START: AC-PHASE24.1.1-003
Description: Core data models for refactoring requests and results
Authority: Phase 24 - External Refactoring Tools Integration
Compliance: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class RefactoringLanguage(Enum):
    """Supported programming languages for refactoring.

    Maps to external tool adapters (Rope, Roslyn, TypeScript LS, Java LSP).
    """
    PYTHON = "python"
    CSHARP = "csharp"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"


@dataclass
class RefactoringRequest:
    """Request for a refactoring operation.

    Attributes:
        operation: Refactoring operation name (e.g., "extract_method")
        file_path: Path to file to refactor
        language: Programming language of the file
        parameters: Operation-specific parameters (e.g., line ranges, names)

    Example:
        >>> request = RefactoringRequest(
        ...     operation="extract_method",
        ...     file_path=Path("src/app.py"),
        ...     language=RefactoringLanguage.PYTHON,
        ...     parameters={"start_line": 10, "end_line": 20, "new_name": "calculate"}
        ... )
    """
    operation: str
    file_path: Path
    language: RefactoringLanguage
    parameters: Dict[str, Any]


@dataclass
class RefactoringResult:
    """Result of a refactoring operation.

    Attributes:
        success: Whether the refactoring completed successfully
        modified_files: List of files modified by the refactoring
        description: Human-readable description of what was done
        warnings: List of warnings generated during refactoring
        errors: List of errors encountered (if success=False)
        metadata: Additional tool-specific metadata

    Example:
        >>> result = RefactoringResult(
        ...     success=True,
        ...     modified_files=[Path("src/app.py")],
        ...     description="Extracted method 'calculate' from lines 10-20",
        ...     warnings=["Consider renaming parameter 'x' to 'value'"]
        ... )
    """
    success: bool
    modified_files: List[Path]
    description: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# AC_COMPLETE: AC-PHASE24.1.1-003 ✅
