"""
Universal Adapter System for CORTEX 4.0

Provides unified interface for external system integration (Azure DevOps, GitHub, FileSystem).
Supports CRUD operations with consistent error handling, caching, and rate limiting.

Author: CORTEX 4.0
Phase: 7B - Operations Simplification (Task 7.6)
"""

from .universal_adapter import (
    UniversalAdapter,
    ResourceType,
    AdapterResponse,
    AdapterError,
    AdapterFactory
)
from .azure_devops_adapter import AzureDevOpsAdapter
from .github_adapter import GitHubAdapter
from .filesystem_adapter import FileSystemAdapter

__all__ = [
    "UniversalAdapter",
    "ResourceType",
    "AdapterResponse",
    "AdapterError",
    "AdapterFactory",
    "AzureDevOpsAdapter",
    "GitHubAdapter",
    "FileSystemAdapter",
]
