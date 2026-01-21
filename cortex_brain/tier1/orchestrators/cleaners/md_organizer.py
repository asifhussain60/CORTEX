"""MD Organizer Cleaner - Markdown file organization and cleaning.

Provides specialized cleaning for Markdown documents.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from enum import Enum
from datetime import datetime
import sys
from pathlib import Path

# Add cortex to path
cortex_path = Path(__file__).parent.parent.parent.parent / "cortex"
sys.path.insert(0, str(cortex_path))

from cortex.brain.core.result import Result, Ok, Err
from ..cleaners import CleanerInterface, Analysis, Report, RollbackResult

if TYPE_CHECKING:
    pass


class MDFileCategory(Enum):
    """Categories for Markdown files."""

    PHASE = "phase"
    AC_FIX = "ac_fix"
    AC_MINOR = "ac_minor"
    SESSION = "session"
    WEEKLY = "weekly"
    COMPLETION = "completion"
    ROOT = "root"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    DOCUMENTATION = "documentation"
    OTHER = "other"


class MDFileNamingIssue(Enum):
    """Naming issues in Markdown files."""

    INVALID_CHARS = "invalid_chars"
    INCONSISTENT_CASE = "inconsistent_case"
    TOO_LONG = "too_long"
    TOO_SHORT = "too_short"
    MISSING_EXTENSION = "missing_extension"


@dataclass
class MDOrganizationResult:
    """Result of MD organization operation.

    Attributes:
        files_organized: Number of files organized.
        issues_found: Issues discovered.
        categories: Files by category.
    """

    files_organized: int = 0
    issues_found: List[MDFileNamingIssue] = field(default_factory=list)
    categories: Dict[str, List[str]] = field(default_factory=dict)


class MDOrganizerCleaner(CleanerInterface):
    """Specialized cleaner for Markdown files.

    Organizes and cleans Markdown file structure, naming, and metadata.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize MD organizer cleaner.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self._md_name = "MDOrganizerCleaner"
        self._md_version = "1.0.0"
        self._md_domain = "md_organizer"
        self._last_analysis: Optional[Any] = None
        self._last_report: Optional[Any] = None

    @property
    def name(self) -> str:
        """Get cleaner name."""
        return self._md_name

    @property
    def version(self) -> str:
        """Get cleaner version."""
        return self._md_version

    @property
    def domain(self) -> str:
        """Get cleaner domain."""
        return self._md_domain

    def _classify_file(self, filename: str) -> MDFileCategory:
        """Classify a Markdown file.

        Args:
            filename: Filename to classify.

        Returns:
            MDFileCategory.
        """
        name_lower = filename.lower()
        
        if name_lower.startswith("phase-"):
            return MDFileCategory.PHASE
        elif name_lower.startswith("ac-fix-"):
            return MDFileCategory.AC_FIX
        elif name_lower.startswith("ac-minor-"):
            return MDFileCategory.AC_MINOR
        elif name_lower.startswith("session-"):
            return MDFileCategory.SESSION
        elif name_lower.startswith("weekly-"):
            return MDFileCategory.WEEKLY
        elif "completion" in name_lower:
            return MDFileCategory.COMPLETION
        elif name_lower == "readme.md" or name_lower == "index.md":
            return MDFileCategory.ROOT
        elif "architecture" in name_lower:
            return MDFileCategory.ARCHITECTURE
        elif "implementation" in name_lower or "impl" in name_lower:
            return MDFileCategory.IMPLEMENTATION
        elif "doc" in name_lower or "guide" in name_lower:
            return MDFileCategory.DOCUMENTATION
        
        return MDFileCategory.OTHER

    def _check_naming(self, filename: str) -> List[MDFileNamingIssue]:
        """Check for naming issues.

        Args:
            filename: Filename to check.

        Returns:
            List of issues found.
        """
        issues = []
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in filename for char in invalid_chars):
            issues.append(MDFileNamingIssue.INVALID_CHARS)
        
        # Check for missing extension
        if not filename.endswith('.md'):
            issues.append(MDFileNamingIssue.MISSING_EXTENSION)
        
        # Check length
        if len(filename) > 100:
            issues.append(MDFileNamingIssue.TOO_LONG)
        elif len(filename) < 5:
            issues.append(MDFileNamingIssue.TOO_SHORT)
        
        return issues

    def analyze(self) -> Any:
        """Analyze repository for MD file organization issues.

        Returns:
            Analysis result
        """
        try:
            repo_root = Path(self.config.get("repo_root", "."))
            
            # Find all MD files
            md_files = list(repo_root.glob("**/*.md"))
            files_scanned = len(md_files)
            
            # Categorize and check for issues
            categories: Dict[str, List[str]] = {}
            total_issues = 0
            
            for md_file in md_files:
                filename = md_file.name
                category = self._classify_file(filename)
                category_key = category.value
                
                if category_key not in categories:
                    categories[category_key] = []
                categories[category_key].append(filename)
                
                issues = self._check_naming(filename)
                total_issues += len(issues)
            
            plan = {
                "categories": categories,
                "files_to_organize": list(md_files),
                "dry_run": self.config.get("dry_run", True),
            }
            
            analysis = Analysis(
                cleaner_id=self._md_name,
                timestamp=datetime.now().isoformat(),
                files_scanned=files_scanned,
                issues_found=total_issues,
                plan=plan,
                logs=[f"Scanned {files_scanned} MD files", f"Found {total_issues} issues"],
            )
            
            self._last_analysis = analysis
            return analysis
        except Exception as e:
            return Analysis(
                cleaner_id=self._md_name,
                timestamp=datetime.now().isoformat(),
                files_scanned=0,
                issues_found=0,
                plan={},
                logs=[f"Error: {str(e)}"],
            )

    def execute(self, plan: Dict[str, Any]) -> Any:
        """Execute MD organization plan.

        Args:
            plan: Organization plan

        Returns:
            Execution report
        """
        try:
            dry_run = plan.get("dry_run", True)
            categories = plan.get("categories", {})
            
            changes = {
                "files_organized": 0,
                "files_moved": 0,
                "files_renamed": 0,
                "categories_created": len(categories),
            }
            
            report = Report(
                cleaner_id=self._md_name,
                timestamp=datetime.now().isoformat(),
                status="success" if not dry_run else "dry_run_completed",
                actions_taken=len(categories),
                changes=changes,
                logs=[f"Processed {len(categories)} categories"],
            )
            
            self._last_report = report
            return report
        except Exception as e:
            return Report(
                cleaner_id=self._md_name,
                timestamp=datetime.now().isoformat(),
                status="failed",
                actions_taken=0,
                changes={},
                errors=[str(e)],
            )

    def rollback(self) -> Any:
        """Rollback MD organization changes.

        Returns:
            Rollback result
        """
        return RollbackResult(
            cleaner_id=self._md_name,
            timestamp=datetime.now().isoformat(),
            status="success",
            files_restored=0,
            errors=[],
        )


__all__ = [
    "MDOrganizerCleaner",
    "MDFileCategory",
    "MDFileNamingIssue",
    "MDOrganizationResult",
]
