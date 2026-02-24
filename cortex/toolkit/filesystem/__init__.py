"""Filesystem intelligence — hierarchical scanning and organization detection.

Components:
    HierarchicalScanner:    Recursive file discovery with depth tracking
    ScannedFile:            Dataclass for discovered files with metadata
    OrganizationAdapter:    Protocol for custom organization detection
    FilenameIntelligence:   Pattern extraction and metadata from filenames
    OrganizationDetector:   Domain detection from directory structure

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case naming
"""

from cortex.toolkit.filesystem.hierarchical_scanner import (
    HierarchicalScanner,
    ScannedFile,
    OrganizationAdapter,
    DefaultOrganizationAdapter,
)

__all__ = [
    "HierarchicalScanner",
    "ScannedFile",
    "OrganizationAdapter",
    "DefaultOrganizationAdapter",
]
