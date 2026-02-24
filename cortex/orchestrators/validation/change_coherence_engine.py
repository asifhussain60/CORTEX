"""
Change Coherence Engine - Core orchestrator for holistic edit validation.

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

Purpose:
    Ensures ALL file modifications maintain coherence with the entire file:
    1. PRE-EDIT: Load full file context + detect existing structure
    2. POST-EDIT: Validate coherence + best practice compliance
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.orchestrators.validation.coherence_models import (
    Change,
    CoherenceReport,
    CoherenceStatus,
    DuplicateMatch,
    FileStructure,
    PreEditContext,
    Section,
    SectionType,
    ValidationResult,
    VersionMarker,
)

logger = logging.getLogger(__name__)

@dataclass
class ConflictCheckResult:
    """Result of checking a proposed change for conflicts.
    
    Attributes:
        has_conflict: Whether a conflict was detected
        conflict_reason: Description of the conflict
        conflicting_sections: Sections that conflict with the change
    """
    
    has_conflict: bool
    conflict_reason: str = ""
    conflicting_sections: List[Section] = field(default_factory=list)

class ChangeCoherenceEngine:
    """Orchestrator ensuring file modifications maintain coherence.
    
    The Change Coherence Engine (CCE) wraps file modification operations
    with pre-edit context loading and post-edit coherence validation.
    
    Key capabilities:
        - Full file context loading before any edit
        - Section and structure detection
        - Duplicate content identification
        - Version marker consistency checking
        - Audit trail for traceability
    
    Example:
        >>> cce = ChangeCoherenceEngine()
        >>> context = cce.pre_edit(Path("document.md"))
        >>> # ... apply changes ...
        >>> report = cce.post_edit(Path("document.md"))
        >>> if not report.passed:
        ...     print(report.recommendations)
    """
    
    def __init__(self) -> None:
        """Initialize the Change Coherence Engine."""
        self._audit_entries: List[Dict[str, Any]] = []
        self._pre_edit_contexts: Dict[str, PreEditContext] = {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def pre_edit(
        self,
        file_path: Path,
        proposed_changes: Optional[List[Change]] = None,
    ) -> PreEditContext:
        """Load full file context before applying edits.
        
        This method MUST be called before any file modifications to establish
        baseline context for coherence validation.
        
        Args:
            file_path: Path to the file to be edited
            proposed_changes: Optional list of proposed changes for conflict checking
            
        Returns:
            PreEditContext containing file structure, existing duplicates, etc.
            
        Raises:
            FileNotFoundError: If file_path does not exist
        """
        self._logger.info(f"Pre-edit analysis for: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load full file content
        content = file_path.read_text(encoding="utf-8")
        
        # Determine file type
        file_type = self._detect_file_type(file_path)
        
        # Analyze structure
        structure = self._analyze_structure(content, file_path, file_type)
        
        # Find existing duplicates
        duplicates = self._find_duplicates(structure.sections)
        
        # Create context
        context = PreEditContext(
            file_path=file_path,
            original_content=content,
            structure=structure,
            existing_duplicates=duplicates,
            relevant_practices=[],  # TODO: Load from knowledge YAMLs
        )
        
        # Store for post-edit comparison
        self._pre_edit_contexts[str(file_path)] = context
        
        # Audit log
        self.audit_log(
            operation="pre_edit",
            file_path=str(file_path),
            sections_count=len(structure.sections),
            version_markers_count=len(structure.version_markers),
            existing_duplicates_count=len(duplicates),
        )
        
        return context
    
    def post_edit(
        self,
        file_path: Path,
        changes_applied: Optional[List[Change]] = None,
    ) -> CoherenceReport:
        """Validate coherence after edits have been applied.
        
        Compares current file state against pre-edit context to detect:
        - New duplicates introduced
        - Version inconsistencies
        - Best practice violations
        
        Args:
            file_path: Path to the edited file
            changes_applied: Optional list of changes that were applied
            
        Returns:
            CoherenceReport with validation results and recommendations
        """
        self._logger.info(f"Post-edit validation for: {file_path}")
        
        # Load current content
        content = file_path.read_text(encoding="utf-8")
        file_type = self._detect_file_type(file_path)
        
        # Analyze current structure
        current_structure = self._analyze_structure(content, file_path, file_type)
        
        # Get pre-edit context if available
        pre_context = self._pre_edit_contexts.get(str(file_path))
        
        # Run validations
        validation_results: List[ValidationResult] = []
        
        # Check for new duplicates
        current_duplicates = self._find_duplicates(current_structure.sections)
        new_duplicates = self._find_new_duplicates(
            current_duplicates,
            pre_context.existing_duplicates if pre_context else [],
        )
        
        if new_duplicates:
            validation_results.append(ValidationResult(
                check_name="duplicate_detection",
                status=CoherenceStatus.FAILED,
                message=f"Found {len(new_duplicates)} new duplicate section(s)",
                details={"duplicates": [d.original_section.name for d in new_duplicates]},
                suggested_fix="Consolidate duplicate sections into single canonical version",
            ))
        else:
            validation_results.append(ValidationResult(
                check_name="duplicate_detection",
                status=CoherenceStatus.PASSED,
                message="No new duplicates introduced",
            ))
        
        # Check version consistency
        version_consistent = current_structure.has_version_consistency()
        if not version_consistent:
            versions = [vm.version for vm in current_structure.version_markers]
            validation_results.append(ValidationResult(
                check_name="version_consistency",
                status=CoherenceStatus.FAILED,
                message="Version markers are inconsistent",
                details={"versions_found": versions},
                suggested_fix="Update all version markers to match",
            ))
        else:
            validation_results.append(ValidationResult(
                check_name="version_consistency",
                status=CoherenceStatus.PASSED,
                message="All version markers are consistent",
            ))
        
        # Determine overall status
        failed_count = len([vr for vr in validation_results if vr.status == CoherenceStatus.FAILED])
        if failed_count > 0:
            overall_status = CoherenceStatus.FAILED
        elif any(vr.status == CoherenceStatus.WARNING for vr in validation_results):
            overall_status = CoherenceStatus.WARNING
        else:
            overall_status = CoherenceStatus.PASSED
        
        # Generate recommendations
        recommendations = self._generate_recommendations(validation_results, new_duplicates)
        
        # Create report
        report = CoherenceReport(
            file_path=file_path,
            status=overall_status,
            validation_results=validation_results,
            duplicates_found=new_duplicates,
            version_consistent=version_consistent,
            best_practice_violations=[],  # TODO: Implement
            recommendations=recommendations,
        )
        
        # Audit log
        self.audit_log(
            operation="post_edit",
            file_path=str(file_path),
            coherence_status=overall_status.value,
            validations_passed=len(validation_results) - failed_count,
            validations_failed=failed_count,
            new_duplicates_count=len(new_duplicates),
        )
        
        return report
    
    def validate_coherence(
        self,
        content: str,
        file_type: str = "markdown",
        file_path: Optional[Path] = None,
    ) -> CoherenceReport:
        """Validate coherence of file content.
        
        Standalone validation without pre/post edit context.
        
        Args:
            content: File content to validate
            file_type: Type of file (markdown, python, yaml)
            file_path: Optional path for reporting
            
        Returns:
            CoherenceReport with validation results
        """
        path = file_path or Path("inline_content")
        
        # Analyze structure
        structure = self._analyze_structure(content, path, file_type)
        
        # Find duplicates
        duplicates = self._find_duplicates(structure.sections)
        
        # Check version consistency
        version_consistent = structure.has_version_consistency()
        
        # Build validation results
        validation_results: List[ValidationResult] = []
        
        if duplicates:
            validation_results.append(ValidationResult(
                check_name="duplicate_detection",
                status=CoherenceStatus.WARNING,
                message=f"Found {len(duplicates)} duplicate section(s)",
                details={"duplicates": [d.original_section.name for d in duplicates]},
                suggested_fix="Consolidate duplicate sections",
            ))
        
        if not version_consistent:
            validation_results.append(ValidationResult(
                check_name="version_consistency",
                status=CoherenceStatus.WARNING,
                message="Version markers are inconsistent",
            ))
        
        # Determine overall status
        if not validation_results:
            overall_status = CoherenceStatus.PASSED
        elif any(vr.status == CoherenceStatus.FAILED for vr in validation_results):
            overall_status = CoherenceStatus.FAILED
        else:
            overall_status = CoherenceStatus.WARNING if validation_results else CoherenceStatus.PASSED
        
        # Generate recommendations
        recommendations = []
        if duplicates:
            recommendations.append(
                f"Consider consolidating {len(duplicates)} duplicate section(s)"
            )
        if not version_consistent:
            recommendations.append("Update version markers to be consistent")
        
        return CoherenceReport(
            file_path=path,
            status=overall_status,
            validation_results=validation_results,
            duplicates_found=duplicates,
            version_consistent=version_consistent,
            recommendations=recommendations,
        )
    
    def check_change_conflicts(
        self,
        context: PreEditContext,
        change: Change,
    ) -> ConflictCheckResult:
        """Check if a proposed change conflicts with existing content.
        
        Args:
            context: Pre-edit context with file structure
            change: Proposed change to check
            
        Returns:
            ConflictCheckResult indicating if conflict exists
        """
        conflicts: List[Section] = []
        
        # Check if new content duplicates existing sections
        if change.new_content:
            # Extract section names from new content
            new_sections = self._extract_section_names(change.new_content)
            
            for new_name in new_sections:
                existing = context.structure.get_section_by_name(new_name)
                if existing:
                    conflicts.append(existing)
        
        if conflicts:
            conflict_names = [s.name for s in conflicts]
            return ConflictCheckResult(
                has_conflict=True,
                conflict_reason=f"Section(s) already exist: {', '.join(conflict_names)}",
                conflicting_sections=conflicts,
            )
        
        return ConflictCheckResult(has_conflict=False)
    
    # =========================================================================
    # AUDIT LOGGING
    # =========================================================================
    
    def audit_log(self, **kwargs: Any) -> None:
        """Record an audit entry.
        
        Args:
            **kwargs: Key-value pairs to record in audit entry
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        self._audit_entries.append(entry)
        self._logger.debug(f"Audit entry: {entry}")
    
    def get_audit_entries(self) -> List[Dict[str, Any]]:
        """Get all audit entries.
        
        Returns:
            List of audit entry dictionaries
        """
        return list(self._audit_entries)
    
    def clear_audit_log(self) -> None:
        """Clear all audit entries."""
        self._audit_entries.clear()
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect file type from extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            File type string (markdown, python, yaml, etc.)
        """
        suffix = file_path.suffix.lower()
        type_map = {
            ".md": "markdown",
            ".markdown": "markdown",
            ".py": "python",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".js": "javascript",
            ".ts": "typescript",
        }
        return type_map.get(suffix, "unknown")
    
    def _analyze_structure(
        self,
        content: str,
        file_path: Path,
        file_type: str,
    ) -> FileStructure:
        """Analyze file structure to detect sections and markers.
        
        Args:
            content: File content
            file_path: Path to file
            file_type: Type of file
            
        Returns:
            FileStructure with detected sections and markers
        """
        sections: List[Section] = []
        version_markers: List[VersionMarker] = []
        
        lines = content.splitlines()
        total_lines = len(lines)
        
        if file_type == "markdown":
            sections = self._parse_markdown_sections(lines)
            version_markers = self._find_version_markers(lines)
        elif file_type == "python":
            sections = self._parse_python_sections(lines)
        elif file_type == "yaml":
            sections = self._parse_yaml_sections(lines)
        
        return FileStructure(
            file_path=file_path,
            file_type=file_type,
            sections=sections,
            version_markers=version_markers,
            total_lines=total_lines,
        )
    
    def _parse_markdown_sections(self, lines: List[str]) -> List[Section]:
        """Parse markdown content into sections.
        
        Args:
            lines: Lines of markdown content
            
        Returns:
            List of detected Section objects
        """
        sections: List[Section] = []
        current_section: Optional[Section] = None
        
        for i, line in enumerate(lines, start=1):
            # Check for headers
            h1_match = re.match(r"^# (.+)$", line)
            h2_match = re.match(r"^## (.+)$", line)
            h3_match = re.match(r"^### (.+)$", line)
            
            if h1_match:
                if current_section:
                    current_section.end_line = i - 1
                    sections.append(current_section)
                current_section = Section(
                    name=h1_match.group(1).strip(),
                    section_type=SectionType.MARKDOWN_H1,
                    start_line=i,
                    end_line=i,
                    level=1,
                )
            elif h2_match:
                if current_section:
                    current_section.end_line = i - 1
                    sections.append(current_section)
                current_section = Section(
                    name=h2_match.group(1).strip(),
                    section_type=SectionType.MARKDOWN_H2,
                    start_line=i,
                    end_line=i,
                    level=2,
                )
            elif h3_match:
                if current_section:
                    current_section.end_line = i - 1
                    sections.append(current_section)
                current_section = Section(
                    name=h3_match.group(1).strip(),
                    section_type=SectionType.MARKDOWN_H3,
                    start_line=i,
                    end_line=i,
                    level=3,
                )
        
        # Close last section
        if current_section:
            current_section.end_line = len(lines)
            sections.append(current_section)
        
        return sections
    
    def _parse_python_sections(self, lines: List[str]) -> List[Section]:
        """Parse Python content into sections (classes/functions).
        
        Args:
            lines: Lines of Python content
            
        Returns:
            List of detected Section objects
        """
        sections: List[Section] = []
        
        for i, line in enumerate(lines, start=1):
            # Check for class definitions
            class_match = re.match(r"^class (\w+)", line)
            if class_match:
                sections.append(Section(
                    name=class_match.group(1),
                    section_type=SectionType.PYTHON_CLASS,
                    start_line=i,
                    end_line=i,  # Would need proper parsing for end
                    level=1,
                ))
            
            # Check for function definitions
            func_match = re.match(r"^def (\w+)", line)
            if func_match:
                sections.append(Section(
                    name=func_match.group(1),
                    section_type=SectionType.PYTHON_FUNCTION,
                    start_line=i,
                    end_line=i,
                    level=2,
                ))
        
        return sections
    
    def _parse_yaml_sections(self, lines: List[str]) -> List[Section]:
        """Parse YAML content into sections (top-level keys).
        
        Args:
            lines: Lines of YAML content
            
        Returns:
            List of detected Section objects
        """
        sections: List[Section] = []
        
        for i, line in enumerate(lines, start=1):
            # Top-level keys (no indentation)
            key_match = re.match(r"^(\w[\w_-]*)\s*:", line)
            if key_match:
                sections.append(Section(
                    name=key_match.group(1),
                    section_type=SectionType.YAML_KEY,
                    start_line=i,
                    end_line=i,
                    level=1,
                ))
        
        return sections
    
    def _find_version_markers(self, lines: List[str]) -> List[VersionMarker]:
        """Find version markers in file content.
        
        Args:
            lines: Lines of content
            
        Returns:
            List of detected VersionMarker objects
        """
        markers: List[VersionMarker] = []
        
        # Pattern for version strings
        version_patterns = [
            r"\*\*Version:\*\*\s*([\d.]+)",  # **Version:** 1.0
            r"Version:\s*([\d.]+)",           # Version: 1.0
            r"\bv([\d.]+)\b",                 # v1.0
        ]
        
        for i, line in enumerate(lines, start=1):
            for pattern in version_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    version = match.group(1)
                    
                    # Determine location
                    if i <= 5:
                        location = "header"
                    elif i >= len(lines) - 5:
                        location = "footer"
                    else:
                        location = "inline"
                    
                    markers.append(VersionMarker(
                        version=version,
                        location=location,
                        line_number=i,
                        raw_text=line,
                    ))
        
        return markers
    
    def _find_duplicates(self, sections: List[Section]) -> List[DuplicateMatch]:
        """Find duplicate sections by name.
        
        Args:
            sections: List of sections to check
            
        Returns:
            List of DuplicateMatch objects
        """
        duplicates: List[DuplicateMatch] = []
        seen: Dict[str, Section] = {}
        
        for section in sections:
            name_lower = section.name.lower()
            if name_lower in seen:
                duplicates.append(DuplicateMatch(
                    original_section=seen[name_lower],
                    duplicate_section=section,
                    similarity=1.0,
                    is_exact=True,
                ))
            else:
                seen[name_lower] = section
        
        return duplicates
    
    def _find_new_duplicates(
        self,
        current: List[DuplicateMatch],
        previous: List[DuplicateMatch],
    ) -> List[DuplicateMatch]:
        """Find duplicates that are new (not in previous state).
        
        Args:
            current: Current duplicate matches
            previous: Previous duplicate matches
            
        Returns:
            List of new DuplicateMatch objects
        """
        if not previous:
            return current
        
        previous_names = {
            d.original_section.name.lower() for d in previous
        }
        
        return [
            d for d in current
            if d.original_section.name.lower() not in previous_names
        ]
    
    def _extract_section_names(self, content: str) -> List[str]:
        """Extract section names from content.
        
        Args:
            content: Content to parse
            
        Returns:
            List of section names found
        """
        names: List[str] = []
        
        # Markdown headers
        for match in re.finditer(r"^#{1,6}\s+(.+)$", content, re.MULTILINE):
            names.append(match.group(1).strip())
        
        return names
    
    def _generate_recommendations(
        self,
        validation_results: List[ValidationResult],
        duplicates: List[DuplicateMatch],
    ) -> List[str]:
        """Generate recommendations based on validation results.
        
        Args:
            validation_results: List of validation results
            duplicates: List of duplicate matches
            
        Returns:
            List of recommendation strings
        """
        recommendations: List[str] = []
        
        for result in validation_results:
            if result.suggested_fix and result.status != CoherenceStatus.PASSED:
                recommendations.append(result.suggested_fix)
        
        if duplicates:
            dup_names = list(set(d.original_section.name for d in duplicates))
            recommendations.append(
                f"Duplicate sections detected: {', '.join(dup_names[:3])}"
                + (" (and more)" if len(dup_names) > 3 else "")
            )
        
        return recommendations

# AC_COMPLETE: AC-ENH-101-004 ✅ ChangeCoherenceEngine implementation
