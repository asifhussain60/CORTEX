"""
Onboarded Repositories Package (Phase 28)

This package manages repository profiles for external repositories that
CORTEX interacts with. Profiles enable loose-coupled interaction and
ensure deletion safety.

Components:
- profile_schema: Data models for repository profiles
- profile_store: Persistence layer for profile storage/retrieval
"""

from cortex_brain.onboarded_repos.profile_schema import (
    LooseCoupling,
    RepositoryProfile,
    RepositoryStructure,
    SecurityMetadata,
    Standards,
    TechStack,
)
from cortex_brain.onboarded_repos.profile_store import (
    ProfileNotFoundError,
    ProfileStore,
)

__all__ = [
    "RepositoryProfile",
    "TechStack",
    "RepositoryStructure",
    "Standards",
    "SecurityMetadata",
    "LooseCoupling",
    "ProfileStore",
    "ProfileNotFoundError",
]
