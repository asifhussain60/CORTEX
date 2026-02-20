"""
cortex.repositories — Repository Pattern Re-exports.

The canonical implementation lives at cortex.infrastructure.repositories.
This module provides a convenience import path for backwards compatibility.

Authority: CORE-035 (Single Canonical Implementation)
"""

from cortex.infrastructure.repositories.json_profile_repository import (
    JSONProfileRepository,
)
from cortex.infrastructure.repositories.repository_interface import (
    RepositoryInterface,
)

__all__ = [
    "JSONProfileRepository",
    "RepositoryInterface",
]
