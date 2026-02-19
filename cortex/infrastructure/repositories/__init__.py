"""
Phase 54-A: Repository Pattern Implementation

Repository abstraction for onboarding profile storage.

Repositories:
- JSONProfileRepository: JSON file-based profile storage
- RepositoryInterface: Abstract base for future implementations (SQLite, API)

Author: Phase 54-A Implementation
Created: 2026-02-09
"""

from .json_profile_repository import JSONProfileRepository
from .repository_interface import RepositoryInterface

__all__ = [
    "JSONProfileRepository",
    "RepositoryInterface",
]
