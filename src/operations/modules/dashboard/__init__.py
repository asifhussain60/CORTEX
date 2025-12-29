"""
Dashboard Operations Modules

Purpose: Modular components for dashboard operations including discovery,
         data collection, and repository management.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from .repository_discovery_service import (
    RepositoryDiscoveryService,
    RepoMetadata,
    discover_and_register_repositories
)

__all__ = [
    'RepositoryDiscoveryService',
    'RepoMetadata',
    'discover_and_register_repositories'
]
