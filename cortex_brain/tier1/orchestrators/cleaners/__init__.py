"""Cleaners Package - Re-exports from cleaners_base module.

Maintains backward compatibility for imports like:
- from tier1.orchestrators.cleaners import Cleaner
- from tier1.orchestrators.cleaners.md_organizer import MDOrganizerCleaner

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from ..cleaners_base import (
    Cleaner,
    DataCleaner,
    FormatCleaner,
    CleaningRule,
    CleanerType,
)

# Stub classes for test compatibility
class CleanerInterface:
    """Cleaner interface for backward compatibility."""

    def clean(self, data):
        """Clean data."""
        raise NotImplementedError


class Analysis:
    """Analysis result."""

    pass


class Report:
    """Report result."""

    pass


class RollbackResult:
    """Rollback result."""

    pass


class CleanerRegistry:
    """Registry for cleaner instances."""
    
    def __init__(self):
        self.cleaners = {}
    
    def register(self, name: str, cleaner):
        """Register a cleaner."""
        self.cleaners[name] = cleaner
    
    def get(self, name: str):
        """Get a cleaner by name."""
        return self.cleaners.get(name)


__all__ = [
    "Cleaner",
    "DataCleaner",
    "FormatCleaner",
    "CleaningRule",
    "CleanerType",
    "CleanerInterface",
    "Analysis",
    "Report",
    "RollbackResult",
    "CleanerRegistry",
]
