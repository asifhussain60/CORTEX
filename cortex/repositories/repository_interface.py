"""
Repository Interface - Abstract Base for Repository Pattern

AC_START: AC-PHASE54A-S2-INTERFACE
Description: Abstract interface for repository implementations
Authority: phase-54-A-incremental-onboarding-refactor.yaml
Pattern: Strategy pattern, enables multiple storage backends
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from .json_profile_repository import RepositoryProfile, ProfileTier
from cortex.brain.core.result import Result


class RepositoryInterface(ABC):
    """Abstract repository interface for profile storage."""
    
    @abstractmethod
    def create(self, profile: RepositoryProfile) -> Result[RepositoryProfile]:
        """Create new profile."""
        pass
    
    @abstractmethod
    def get_by_id(self, profile_id: str) -> Result[RepositoryProfile]:
        """Get profile by ID."""
        pass
    
    @abstractmethod
    def update(self, profile: RepositoryProfile) -> Result[RepositoryProfile]:
        """Update existing profile."""
        pass
    
    @abstractmethod
    def delete(self, profile_id: str) -> Result[None]:
        """Delete profile."""
        pass
    
    @abstractmethod
    def list_all(self) -> Result[List[RepositoryProfile]]:
        """List all profiles."""
        pass
    
    @abstractmethod
    def list_by_tier(self, tier: ProfileTier) -> Result[List[RepositoryProfile]]:
        """List profiles by tier."""
        pass
    
    @abstractmethod
    def get_highest_precedence(self) -> Result[Optional[RepositoryProfile]]:
        """Get highest precedence profile."""
        pass
    
    @abstractmethod
    def count(self) -> Result[int]:
        """Count profiles."""
        pass
    
    @abstractmethod
    def clear(self) -> Result[None]:
        """Clear all profiles."""
        pass


# AC_COMPLETE: AC-PHASE54A-S2-INTERFACE ✅
