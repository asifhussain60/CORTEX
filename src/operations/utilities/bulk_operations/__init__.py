"""
Bulk Operations Package

Reusable utilities for bulk file operations across CORTEX.

Modules:
- copyright_updater: Add/update copyright headers in markdown files
"""

from .copyright_updater import BulkCopyrightUpdater, PlanningDocumentRealigner

__all__ = [
    'BulkCopyrightUpdater',
    'PlanningDocumentRealigner'
]
