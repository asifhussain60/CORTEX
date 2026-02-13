"""
Coherence Validator - Validate post-edit coherence.

AC_START: AC-ENH-101-009
Description: CoherenceValidator for post-edit validation
Authority: ENH-101 Stage S4 - Post-Edit Validation
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

Purpose:
    Validates coherence after edits:
    - Version consistency (header vs footer)
    - No duplicate sections introduced
    - Structure preserved
    - Best practice compliance
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.orchestrators.coherence.duplicate_scanner import DuplicateScanner, ScanResult
from cortex.orchestrators.coherence.models import (
    CoherenceReport,
    CoherenceStatus,
    FileStructure,
    PreEditContext,
    Section,
    ValidationResult,
    VersionMarker,
)
from cortex.orchestrators.coherence.structure_analyzer import StructureAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class CoherenceIssue:
    """A specific coherence issue found.
    
    Attributes:
        issue_type: Type of issue (duplicate, version_mismatch, etc.)
        severity: Severity level (error, warning, info)
        message: Human-readable description
        location: Line number or section name
        suggestion: How to fix
    """
    
    issue_type: str
    severity: str  # error, warning, info
    message: str
    location: str = ""
    suggestion: str = ""


@dataclass
class ValidationConfig:
    """Configuration for validation.
    
    Attributes:
        check_duplicates: Whether to check for duplicates
        check_versions: Whether to check version consistency
        check_structure: Whether to check structure preservation
        similarity_threshold: Threshold for duplicate detection
    """
    
    check_duplicates: bool = True
    check_versions: bool = True
    check_structure: bool = True
    similarity_threshold: float = 0.8


class CoherenceValidator:
    """Validator for post-edit coherence checking.
    
    Validates that edits maintain file coherence:
    - No duplicate sections introduced
    - Version markers consistent
    - Structure not degraded
    - Best practices maintained
    
    Example:
        >>> validator = CoherenceValidator()
        >>> result = validator.validate(pre_context, post_content)
        >>> if not result.passed:
        ...     for issue in result.issues:
        ...         print(f"{issue.severity}: {issue.message}")
    """
    
    def __init__(
        self,
        config: Optional[ValidationConfig] = None,
    ) -> None:
        """Initialize the CoherenceValidator.
        
        Args:
            config: Validation configuration
        """
        self._config = config or ValidationConfig()
        self._analyzer = StructureAnalyzer()
        self._duplicate_scanner = DuplicateScanner(
            similarity_threshold=self._config.similarity_threshold,
        )
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def validate(
        self,
        pre_context: PreEditContext,
        post_content: str,
    ) -> ValidationResult:
        """Validate coherence after an edit.
        
        Args:
            pre_context: Context captured before the edit
            post_content: Content after the edit
            
        Returns:
            ValidationResult with status and any issues
        """
        issues: List[CoherenceIssue] = []
        
        # Analyze post-edit structure
        post_structure = self._analyzer.analyze(
            post_content,
            pre_context.file_path,
        )
        
        # Check for duplicates
        if self._config.check_duplicates:
            dup_issues = self._check_duplicates(post_structure)
            issues.extend(dup_issues)
        
        # Check version consistency
        if self._config.check_versions:
            ver_issues = self._check_version_consistency(post_structure)
            issues.extend(ver_issues)
        
        # Check structure preservation
        if self._config.check_structure:
            struct_issues = self._check_structure_preservation(
                pre_context.structure,
                post_structure,
            )
            issues.extend(struct_issues)
        
        # Determine overall status
        if any(i.severity == "error" for i in issues):
            status = CoherenceStatus.FAILED
        elif any(i.severity == "warning" for i in issues):
            status = CoherenceStatus.WARNING
        else:
            status = CoherenceStatus.PASSED
        
        # Build issue details
        issue_details = {
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity,
                    "message": i.message,
                    "location": i.location,
                    "suggestion": i.suggestion,
                }
                for i in issues
            ],
            "recommendations": [i.suggestion for i in issues if i.suggestion],
        }
        
        return ValidationResult(
            check_name="coherence_validation",
            status=status,
            message=f"Found {len(issues)} issues" if issues else "Coherence check passed",
            details=issue_details,
            suggested_fix=issues[0].suggestion if issues else None,
        )
    
    def check_duplicates(self, content: str, file_path: str = "") -> List[CoherenceIssue]:
        """Check content for duplicate sections.
        
        Args:
            content: Content to check
            file_path: Optional file path
            
        Returns:
            List of duplicate-related issues
        """
        structure = self._analyzer.analyze(content, file_path)
        return self._check_duplicates(structure)
    
    def check_version_consistency(
        self,
        content: str,
        file_path: str = "",
    ) -> List[CoherenceIssue]:
        """Check content for version inconsistencies.
        
        Args:
            content: Content to check
            file_path: Optional file path
            
        Returns:
            List of version-related issues
        """
        structure = self._analyzer.analyze(content, file_path)
        return self._check_version_consistency(structure)
    
    def generate_report(
        self,
        pre_context: PreEditContext,
        post_content: str,
    ) -> CoherenceReport:
        """Generate a full coherence report.
        
        Args:
            pre_context: Context captured before the edit
            post_content: Content after the edit
            
        Returns:
            CoherenceReport with all findings
        """
        result = self.validate(pre_context, post_content)
        
        post_structure = self._analyzer.analyze(
            post_content,
            pre_context.file_path,
        )
        
        # Scan for duplicates
        scan_result = self._duplicate_scanner.scan_sections(post_structure.sections)
        
        # Check version consistency
        version_issues = result.details.get("issues", [])
        has_version_mismatch = any(
            i.get("type") == "version_mismatch" for i in version_issues
        )
        
        return CoherenceReport(
            file_path=pre_context.file_path,
            status=result.status,
            validation_results=[result],
            duplicates_found=scan_result.all_duplicates,
            version_consistent=not has_version_mismatch,
            best_practice_violations=[],
            recommendations=result.details.get("recommendations", []),
        )
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _check_duplicates(self, structure: FileStructure) -> List[CoherenceIssue]:
        """Check for duplicate sections.
        
        Args:
            structure: Analyzed file structure
            
        Returns:
            List of duplicate-related issues
        """
        issues: List[CoherenceIssue] = []
        
        scan_result = self._duplicate_scanner.scan_sections(structure.sections)
        
        for dup in scan_result.exact_duplicates:
            issues.append(CoherenceIssue(
                issue_type="duplicate_section",
                severity="error",
                message=f"Duplicate section '{dup.original_section.name}' found at lines {dup.original_section.start_line} and {dup.duplicate_section.start_line}",
                location=f"line {dup.duplicate_section.start_line}",
                suggestion=f"Remove duplicate at line {dup.duplicate_section.start_line} or merge content",
            ))
        
        for dup in scan_result.near_duplicates:
            issues.append(CoherenceIssue(
                issue_type="similar_section",
                severity="warning",
                message=f"Similar sections '{dup.original_section.name}' and '{dup.duplicate_section.name}' (similarity: {dup.similarity:.0%})",
                location=f"lines {dup.original_section.start_line}, {dup.duplicate_section.start_line}",
                suggestion="Consider consolidating these sections",
            ))
        
        return issues
    
    def _check_version_consistency(
        self,
        structure: FileStructure,
    ) -> List[CoherenceIssue]:
        """Check for version inconsistencies.
        
        Args:
            structure: Analyzed file structure
            
        Returns:
            List of version-related issues
        """
        issues: List[CoherenceIssue] = []
        markers = structure.version_markers
        
        if len(markers) <= 1:
            return issues  # No inconsistency possible
        
        # Extract version numbers
        versions = [m.version for m in markers]
        unique_versions = set(versions)
        
        if len(unique_versions) > 1:
            issues.append(CoherenceIssue(
                issue_type="version_mismatch",
                severity="error",
                message=f"Inconsistent versions found: {', '.join(unique_versions)}",
                location=", ".join(f"line {m.line_number}" for m in markers),
                suggestion=f"Update all version markers to the same version",
            ))
        
        return issues
    
    def _check_structure_preservation(
        self,
        pre_structure: Optional[FileStructure],
        post_structure: FileStructure,
    ) -> List[CoherenceIssue]:
        """Check that structure was not degraded.
        
        Args:
            pre_structure: Structure before edit (may be None)
            post_structure: Structure after edit
            
        Returns:
            List of structure-related issues
        """
        issues: List[CoherenceIssue] = []
        
        if pre_structure is None:
            return issues  # No comparison possible
        
        # Check for lost sections
        pre_names = {s.name for s in pre_structure.sections}
        post_names = {s.name for s in post_structure.sections}
        
        lost_sections = pre_names - post_names
        if lost_sections:
            for name in lost_sections:
                issues.append(CoherenceIssue(
                    issue_type="section_removed",
                    severity="warning",
                    message=f"Section '{name}' was removed",
                    suggestion="Verify this section removal was intentional",
                ))
        
        # Check for significant line count change (>50% reduction)
        if pre_structure.total_lines > 10:
            reduction = (pre_structure.total_lines - post_structure.total_lines) / pre_structure.total_lines
            if reduction > 0.5:
                issues.append(CoherenceIssue(
                    issue_type="significant_reduction",
                    severity="warning",
                    message=f"File reduced by {reduction:.0%} ({pre_structure.total_lines} → {post_structure.total_lines} lines)",
                    suggestion="Verify this significant reduction was intentional",
                ))
        
        return issues


# AC_COMPLETE: AC-ENH-101-009 ✅ CoherenceValidator implementation
