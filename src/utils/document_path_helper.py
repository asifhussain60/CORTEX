"""
Document Path Helper

Centralized helper for resolving document paths using user-configured preferences.
All document generation in CORTEX should use this module to respect user path configuration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Optional
import logging

from src.setup.modules.path_resolver import PathResolver


# Global PathResolver instance (lazy-initialized)
_path_resolver: Optional[PathResolver] = None
_logger = logging.getLogger(__name__)


def get_path_resolver(workspace_root: Optional[str] = None) -> PathResolver:
    """
    Get the global PathResolver instance (singleton pattern).
    
    Args:
        workspace_root: Optional workspace root (auto-detected if not provided)
    
    Returns:
        PathResolver instance
    """
    global _path_resolver
    
    if _path_resolver is None:
        _path_resolver = PathResolver(workspace_root=workspace_root)
    
    return _path_resolver


def get_document_path(
    category: str,
    filename: str,
    create: bool = True,
    workspace_root: Optional[str] = None
) -> Path:
    """
    Get full path for a document in the specified category.
    
    Categories:
    - reports: Validation reports, status reports, completion reports
    - analysis: Code analysis, architecture analysis
    - summaries: Project summaries, progress summaries
    - investigations: Bug investigations, issue analysis
    - planning: Feature plans, ADO work items, roadmaps
    - implementation-guides: How-to guides, tutorials
    
    Args:
        category: Document category
        filename: Document filename (e.g., "validation-report.md")
        create: Create directory if it doesn't exist (default: True)
        workspace_root: Optional workspace root
    
    Returns:
        Full path to document
    
    Example:
        # Get path for a validation report
        path = get_document_path("reports", "setup-validation.md")
        # Returns: Path("cortex-brain/documents/reports/setup-validation.md")
        
        # Write content
        path.write_text(report_content)
    """
    resolver = get_path_resolver(workspace_root)
    return Path(resolver.get_document_path(category, filename, create=create))


def get_reports_directory(create: bool = True, workspace_root: Optional[str] = None) -> Path:
    """Get configured reports directory."""
    resolver = get_path_resolver(workspace_root)
    return Path(resolver.get_documents_directory("reports", create=create))


def get_analysis_directory(create: bool = True, workspace_root: Optional[str] = None) -> Path:
    """Get configured analysis directory."""
    resolver = get_path_resolver(workspace_root)
    return Path(resolver.get_documents_directory("analysis", create=create))


def get_summaries_directory(create: bool = True, workspace_root: Optional[str] = None) -> Path:
    """Get configured summaries directory."""
    resolver = get_path_resolver(workspace_root)
    return Path(resolver.get_documents_directory("summaries", create=create))


def get_investigations_directory(create: bool = True, workspace_root: Optional[str] = None) -> Path:
    """Get configured investigations directory."""
    resolver = get_path_resolver(workspace_root)
    return Path(resolver.get_documents_directory("investigations", create=create))


def get_planning_directory(create: bool = True, workspace_root: Optional[str] = None) -> Path:
    """Get configured planning directory."""
    resolver = get_path_resolver(workspace_root)
    return Path(resolver.get_documents_directory("planning", create=create))


def get_implementation_guides_directory(create: bool = True, workspace_root: Optional[str] = None) -> Path:
    """Get configured implementation guides directory."""
    resolver = get_path_resolver(workspace_root)
    return Path(resolver.get_documents_directory("implementation-guides", create=create))


# Backward compatibility: Hardcoded paths still work but log warnings
def get_legacy_document_path(hardcoded_path: str, category: str, filename: str) -> Path:
    """
    Handle legacy hardcoded paths with warning.
    
    Args:
        hardcoded_path: Original hardcoded path
        category: Document category
        filename: Document filename
    
    Returns:
        Configured path (or hardcoded if configuration not available)
    """
    try:
        resolver = get_path_resolver()
        configured_path = resolver.get_document_path(category, filename, create=False)
        
        if str(configured_path) != hardcoded_path:
            _logger.warning(
                f"Using configured path instead of hardcoded: {configured_path} "
                f"(was: {hardcoded_path})"
            )
        
        return Path(configured_path)
    except Exception as e:
        _logger.warning(f"Could not resolve configured path, using hardcoded: {e}")
        return Path(hardcoded_path)


# Quick reference constants for common categories
REPORTS = "reports"
ANALYSIS = "analysis"
SUMMARIES = "summaries"
INVESTIGATIONS = "investigations"
PLANNING = "planning"
IMPLEMENTATION_GUIDES = "implementation-guides"
