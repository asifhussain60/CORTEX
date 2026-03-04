"""
Data models for Change Coherence Engine.

ENH-101: Models for file structure, changes, and coherence validation.

AC_START: AC-ENH-101-002
Authority: ENH-101-change-coherence-engine.yaml Stage S1
Compliance: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ChangeType(Enum):  # CORE-035-scoped — domain-specific variant
    """Type of change being applied to a file."""

    INSERT = "insert"
    REPLACE = "replace"
    DELETE = "delete"
    MOVE = "move"


class CoherenceStatus(Enum):  # CORE-035-scoped — domain-specific variant
    """Status of coherence validation."""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class SectionType(Enum):  # CORE-035-scoped — domain-specific variant
    """Type of section in a file."""

    MARKDOWN_H1 = "markdown_h1"
    MARKDOWN_H2 = "markdown_h2"
    MARKDOWN_H3 = "markdown_h3"
    PYTHON_CLASS = "python_class"
    PYTHON_FUNCTION = "python_function"
    YAML_KEY = "yaml_key"
    CODE_BLOCK = "code_block"
    UNKNOWN = "unknown"


@dataclass
class Section:
    """Represents a section within a file.

    Attributes:
        name: Section identifier (header text, class name, etc.)
        section_type: Type of section (markdown header, python class, etc.)
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed, inclusive)
        content: Raw content of the section
        level: Nesting level (1 for H1, 2 for H2, etc.)
        parent: Parent section name if nested
    """

    name: str
    section_type: SectionType
    start_line: int
    end_line: int
    content: str = ""
    level: int = 1
    parent: Optional[str] = None

    def __hash__(self) -> int:
        """Hash based on name and line range."""
        return hash((self.name, self.start_line, self.end_line))

    def overlaps(self, other: Section) -> bool:
        """Check if this section overlaps with another.

        Args:
            other: Another section to check overlap with

        Returns:
            True if sections overlap, False otherwise
        """
        return not (self.end_line < other.start_line or self.start_line > other.end_line)


@dataclass
class VersionMarker:
    """Version marker found in a file.

    Attributes:
        version: Version string (e.g., "8.1", "v2.0")
        location: Where found ("header", "footer", "inline")
        line_number: Line number where found
        raw_text: Original text containing version
    """

    version: str
    location: str
    line_number: int
    raw_text: str = ""

    def matches(self, other: VersionMarker) -> bool:
        """Check if versions match.

        Args:
            other: Another version marker to compare

        Returns:
            True if versions are equal, False otherwise
        """
        return self.version == other.version


@dataclass
class FileStructure:
    """Analyzed structure of a file.

    Attributes:
        file_path: Path to the analyzed file
        file_type: Type of file (markdown, python, yaml, etc.)
        sections: List of detected sections
        version_markers: List of version markers found
        total_lines: Total number of lines in file
        metadata: Additional metadata extracted
    """

    file_path: Path
    file_type: str
    sections: List[Section] = field(default_factory=list)
    version_markers: List[VersionMarker] = field(default_factory=list)
    total_lines: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_section_by_name(self, name: str) -> Optional[Section]:
        """Find a section by its name.

        Args:
            name: Section name to find

        Returns:
            Section if found, None otherwise
        """
        for section in self.sections:
            if section.name == name:
                return section
        return None

    def get_sections_by_type(self, section_type: SectionType) -> List[Section]:
        """Get all sections of a specific type.

        Args:
            section_type: Type of sections to find

        Returns:
            List of matching sections
        """
        return [s for s in self.sections if s.section_type == section_type]

    def has_version_consistency(self) -> bool:
        """Check if all version markers are consistent.

        Returns:
            True if all versions match or only one version exists
        """
        if len(self.version_markers) <= 1:
            return True
        first_version = self.version_markers[0].version
        return all(vm.version == first_version for vm in self.version_markers)


@dataclass
class Change:
    """Represents a change to be applied to a file.

    Attributes:
        change_type: Type of change (insert, replace, delete, move)
        target_line: Target line number for the change
        old_content: Content being replaced/deleted (if applicable)
        new_content: New content being inserted/replacing
        description: Human-readable description of the change
    """

    change_type: ChangeType
    target_line: int
    old_content: str = ""
    new_content: str = ""
    description: str = ""

    def affects_lines(self) -> tuple[int, int]:
        """Get the range of lines affected by this change.

        Returns:
            Tuple of (start_line, end_line) affected
        """
        if self.change_type == ChangeType.INSERT:
            return (self.target_line, self.target_line)

        old_lines = len(self.old_content.splitlines()) if self.old_content else 0
        return (self.target_line, self.target_line + max(0, old_lines - 1))


@dataclass
class DuplicateMatch:
    """A detected duplicate or near-duplicate content.

    Attributes:
        original_section: The original/canonical section
        duplicate_section: The duplicate section found
        similarity: Similarity score (0.0 to 1.0)
        is_exact: Whether it's an exact match (100%)
    """

    original_section: Section
    duplicate_section: Section
    similarity: float
    is_exact: bool = False

    def __post_init__(self) -> None:
        """Set is_exact based on similarity."""
        self.is_exact = self.similarity >= 0.99


@dataclass
class ValidationResult:  # CORE-035-scoped — domain-specific ValidationResult variant
    """Result of a single validation check.

    Attributes:
        check_name: Name of the validation check
        status: Pass/Warning/Fail status
        message: Human-readable result message
        details: Additional details about the result
        suggested_fix: Suggested fix if validation failed
    """

    check_name: str
    status: CoherenceStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggested_fix: Optional[str] = None

    @property
    def passed(self) -> bool:
        """Check if validation passed."""
        return self.status == CoherenceStatus.PASSED


@dataclass
class PreEditContext:
    """Context gathered before applying edits.

    Attributes:
        file_path: Path to the file being edited
        original_content: Full content before edits
        structure: Analyzed file structure
        existing_duplicates: Already-present duplicate content
        relevant_practices: Applicable best practices from knowledge YAMLs
    """

    file_path: Path
    original_content: str
    structure: FileStructure
    existing_duplicates: List[DuplicateMatch] = field(default_factory=list)
    relevant_practices: List[Dict[str, Any]] = field(default_factory=list)

    def has_section(self, name: str) -> bool:
        """Check if a section with given name exists.

        Args:
            name: Section name to check

        Returns:
            True if section exists, False otherwise
        """
        return self.structure.get_section_by_name(name) is not None


@dataclass
class CoherenceReport:
    """Final report from coherence validation.

    Attributes:
        file_path: Path to the validated file
        status: Overall coherence status
        validation_results: Individual validation results
        duplicates_found: New duplicates introduced
        version_consistent: Whether versions are consistent
        best_practice_violations: Violations of best practices
        recommendations: Suggested improvements
    """

    file_path: Path
    status: CoherenceStatus
    validation_results: List[ValidationResult] = field(default_factory=list)
    duplicates_found: List[DuplicateMatch] = field(default_factory=list)
    version_consistent: bool = True
    best_practice_violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Check if overall coherence passed."""
        return self.status == CoherenceStatus.PASSED

    @property
    def has_issues(self) -> bool:
        """Check if any issues were found."""
        return (
            len(self.duplicates_found) > 0
            or not self.version_consistent
            or len(self.best_practice_violations) > 0
        )

    def get_failed_validations(self) -> List[ValidationResult]:
        """Get all failed validation results.

        Returns:
            List of failed ValidationResult objects
        """
        return [vr for vr in self.validation_results if vr.status == CoherenceStatus.FAILED]

    def summary(self) -> str:
        """Generate a summary of the coherence report.

        Returns:
            Human-readable summary string
        """
        lines = [
            f"Coherence Report: {self.file_path.name}",
            f"Status: {self.status.value.upper()}",
            f"Validations: {len(self.validation_results)} ({len(self.get_failed_validations())} failed)",
            f"Duplicates: {len(self.duplicates_found)}",
            f"Version Consistent: {'Yes' if self.version_consistent else 'No'}",
            f"Best Practice Violations: {len(self.best_practice_violations)}",
        ]
        return "\n".join(lines)


# AC_COMPLETE: AC-ENH-101-002 ✅ Data models for CCE
