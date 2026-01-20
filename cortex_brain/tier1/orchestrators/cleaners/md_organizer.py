"""MD Organizer Cleaner - Markdown file organization and cleaning.

Provides specialized cleaning for Markdown documents.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum
from ..cleaners_base import Cleaner


class MDFileCategory(Enum):
    """Categories for Markdown files."""

    DOCUMENTATION = "documentation"
    GUIDE = "guide"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    README = "readme"
    CHANGELOG = "changelog"


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
    issues_found: List[MDFileNamingIssue] = None
    categories: Dict[str, List[str]] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.issues_found is None:
            self.issues_found = []
        if self.categories is None:
            self.categories = {}


class MDOrganizerCleaner(Cleaner):
    """Specialized cleaner for Markdown files.

    Organizes and cleans Markdown file structure, naming, and metadata.
    """

    def __init__(self) -> None:
        """Initialize MD organizer cleaner."""
        super().__init__("MDOrganizerCleaner")
        self.domain = "md_organizer"

    def categorize(self, filename: str) -> MDFileCategory:
        """Categorize a Markdown file.

        Args:
            filename: Filename to categorize.

        Returns:
            MDFileCategory.
        """
        name_lower = filename.lower()
        if "readme" in name_lower:
            return MDFileCategory.README
        elif "guide" in name_lower:
            return MDFileCategory.GUIDE
        elif "changelog" in name_lower or "change" in name_lower:
            return MDFileCategory.CHANGELOG
        elif "tutorial" in name_lower:
            return MDFileCategory.TUTORIAL
        elif "reference" in name_lower or "api" in name_lower:
            return MDFileCategory.REFERENCE
        return MDFileCategory.DOCUMENTATION

    def check_naming(self, filename: str) -> List[MDFileNamingIssue]:
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

    def organize(self, files: List[str]) -> MDOrganizationResult:
        """Organize Markdown files.

        Args:
            files: List of filenames to organize.

        Returns:
            MDOrganizationResult.
        """
        result = MDOrganizationResult()
        result.files_organized = len(files)
        
        for filename in files:
            category = self.categorize(filename)
            if category.value not in result.categories:
                result.categories[category.value] = []
            result.categories[category.value].append(filename)
            
            issues = self.check_naming(filename)
            result.issues_found.extend(issues)
        
        return result


__all__ = [
    "MDOrganizerCleaner",
    "MDFileCategory",
    "MDFileNamingIssue",
    "MDOrganizationResult",
]
