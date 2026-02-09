"""
JSON Profile Repository - Data Access Pattern (Phase 54-A S2)

AC_START: AC-PHASE54A-S2-001
Description: Repository abstraction for repository profiles with CRUD operations
Authority: phase-54-A-incremental-onboarding-refactor.yaml, S2 task
Pattern: Data Access Object (DAO), enabling future SQLite/API migration
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json
from enum import Enum

from cortex.brain.core.result import Result, Ok, Err


class ProfileTier(Enum):
    """Repository profile tier levels (TIER-0/1/2/3)."""
    TIER_0 = "tier-0"  # Critical
    TIER_1 = "tier-1"  # High
    TIER_2 = "tier-2"  # Medium
    TIER_3 = "tier-3"  # Low


@dataclass
class RepositoryProfile:
    """Repository profile domain entity."""
    id: str
    name: str
    path: str
    tier: ProfileTier
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["tier"] = self.tier.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryProfile":
        """Create from dictionary (loaded from storage)."""
        data = data.copy()
        data["tier"] = ProfileTier(data["tier"])
        return cls(**data)


class JSONProfileRepository:
    """
    Repository pattern for repository profiles.
    
    Implements CRUD operations with tier-based precedence:
    - TIER-0 profiles take precedence (critical)
    - TIER-1 override TIER-2/3
    - TIER-2 override TIER-3
    
    Storage abstraction enables future migration to:
    - SQLite (local database)
    - PostgreSQL (distributed)
    - Redis (caching)
    - S3 (cloud storage)
    """
    
    def __init__(self, storage_path: Path) -> None:
        """
        Initialize repository.
        
        Args:
            storage_path: Path to JSON storage file
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self) -> None:
        """Ensure storage file exists."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text(json.dumps({"profiles": []}))
    
    def create(self, profile: RepositoryProfile) -> Result[RepositoryProfile]:
        """
        Create new profile.
        
        Args:
            profile: Profile to create
            
        Returns:
            Result containing created profile or error
        """
        try:
            # Check if profile already exists
            existing = self.get_by_id(profile.id)
            if existing.is_ok():
                return Err(f"Profile already exists: {profile.id}")
            
            # Load existing profiles
            data = self._load_storage()
            profiles = data.get("profiles", [])
            
            # Add new profile
            profiles.append(profile.to_dict())
            
            # Save
            self._save_storage({"profiles": profiles})
            
            return Ok(profile)
        
        except Exception as e:
            return Err(f"Failed to create profile: {str(e)}")
    
    def get_by_id(self, profile_id: str) -> Result[RepositoryProfile]:
        """
        Retrieve profile by ID.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Result containing profile or error
        """
        try:
            data = self._load_storage()
            profiles = data.get("profiles", [])
            
            for profile_data in profiles:
                if profile_data.get("id") == profile_id:
                    return Ok(RepositoryProfile.from_dict(profile_data))
            
            return Err(f"Profile not found: {profile_id}")
        
        except Exception as e:
            return Err(f"Failed to get profile: {str(e)}")
    
    def update(self, profile: RepositoryProfile) -> Result[RepositoryProfile]:
        """
        Update existing profile.
        
        Args:
            profile: Updated profile
            
        Returns:
            Result containing updated profile or error
        """
        try:
            data = self._load_storage()
            profiles = data.get("profiles", [])
            
            # Find and update
            found = False
            for i, p in enumerate(profiles):
                if p.get("id") == profile.id:
                    profile.updated_at = datetime.now().isoformat()
                    profiles[i] = profile.to_dict()
                    found = True
                    break
            
            if not found:
                return Err(f"Profile not found: {profile.id}")
            
            # Save
            self._save_storage({"profiles": profiles})
            
            return Ok(profile)
        
        except Exception as e:
            return Err(f"Failed to update profile: {str(e)}")
    
    def delete(self, profile_id: str) -> Result[None]:
        """
        Delete profile by ID.
        
        Args:
            profile_id: Profile ID to delete
            
        Returns:
            Result containing None or error
        """
        try:
            data = self._load_storage()
            profiles = data.get("profiles", [])
            
            # Find and remove
            original_count = len(profiles)
            profiles = [p for p in profiles if p.get("id") != profile_id]
            
            if len(profiles) == original_count:
                return Err(f"Profile not found: {profile_id}")
            
            # Save
            self._save_storage({"profiles": profiles})
            
            return Ok(None)
        
        except Exception as e:
            return Err(f"Failed to delete profile: {str(e)}")
    
    def list_all(self) -> Result[List[RepositoryProfile]]:
        """
        List all profiles.
        
        Returns:
            Result containing list of profiles or error
        """
        try:
            data = self._load_storage()
            profiles_data = data.get("profiles", [])
            
            profiles = [
                RepositoryProfile.from_dict(p) for p in profiles_data
            ]
            
            return Ok(profiles)
        
        except Exception as e:
            return Err(f"Failed to list profiles: {str(e)}")
    
    def list_by_tier(self, tier: ProfileTier) -> Result[List[RepositoryProfile]]:
        """
        List profiles by tier.
        
        Args:
            tier: ProfileTier to filter by
            
        Returns:
            Result containing filtered profiles or error
        """
        try:
            all_result = self.list_all()
            if all_result.is_err():
                return all_result
            
            all_profiles = all_result.unwrap()
            filtered = [p for p in all_profiles if p.tier == tier]
            
            return Ok(filtered)
        
        except Exception as e:
            return Err(f"Failed to list by tier: {str(e)}")
    
    def get_highest_precedence(self) -> Result[Optional[RepositoryProfile]]:
        """
        Get highest precedence profile (TIER-0 > TIER-1 > TIER-2 > TIER-3).
        
        Returns:
            Result containing profile or None if empty
        """
        try:
            all_result = self.list_all()
            if all_result.is_err():
                return all_result
            
            profiles = all_result.unwrap()
            if not profiles:
                return Ok(None)
            
            # Sort by tier precedence
            tier_order = {
                ProfileTier.TIER_0: 0,
                ProfileTier.TIER_1: 1,
                ProfileTier.TIER_2: 2,
                ProfileTier.TIER_3: 3,
            }
            
            sorted_profiles = sorted(
                profiles,
                key=lambda p: tier_order.get(p.tier, 999)
            )
            
            return Ok(sorted_profiles[0])
        
        except Exception as e:
            return Err(f"Failed to get highest precedence: {str(e)}")
    
    def count(self) -> Result[int]:
        """
        Count total profiles.
        
        Returns:
            Result containing count or error
        """
        try:
            data = self._load_storage()
            profiles = data.get("profiles", [])
            return Ok(len(profiles))
        
        except Exception as e:
            return Err(f"Failed to count profiles: {str(e)}")
    
    def clear(self) -> Result[None]:
        """
        Clear all profiles.
        
        Returns:
            Result containing None or error
        """
        try:
            self._save_storage({"profiles": []})
            return Ok(None)
        
        except Exception as e:
            return Err(f"Failed to clear profiles: {str(e)}")
    
    def _load_storage(self) -> Dict[str, Any]:
        """Load storage file."""
        try:
            content = self.storage_path.read_text()
            return json.loads(content)
        except Exception:
            return {"profiles": []}
    
    def _save_storage(self, data: Dict[str, Any]) -> None:
        """Save storage file."""
        self.storage_path.write_text(json.dumps(data, indent=2, default=str))


# AC_COMPLETE: AC-PHASE54A-S2-001 ✅
