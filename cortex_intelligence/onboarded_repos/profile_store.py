"""
Repository Profile Store for Persistence (Phase 28.1.2)

This module provides the persistence layer for repository profiles,
enabling save/load/delete operations with graceful error handling.

Authority: phase-28-repository-onboarding-system.yaml
Created: 2026-02-06
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile


class ProfileNotFoundError(Exception):
    """Raised when attempting to load a profile that doesn't exist."""
    
    pass


class ProfileStore:
    """
    Persistence layer for repository profiles.
    
    Profiles are stored as YAML files in the storage_path directory.
    File names are normalized (lowercase, hyphens→underscores).
    
    Attributes:
        storage_path: Directory where profiles are stored
    
    Example:
        >>> store = ProfileStore()
        >>> profile = RepositoryProfile(name="KSESSIONS", ...)
        >>> store.save(profile)
        >>> loaded = store.load("KSESSIONS")
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize ProfileStore.
        
        Args:
            storage_path: Directory for profile storage
                         (default: cortex_brain/onboarded_repos/)
        """
        if storage_path is None:
            # Default to cortex_brain/onboarded_repos/
            project_root = Path(__file__).parent.parent.parent
            storage_path = project_root / "cortex_brain" / "onboarded_repos"
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize repository name for file system storage.
        
        Converts to lowercase and replaces hyphens with underscores.
        
        Args:
            name: Repository name
            
        Returns:
            Normalized name (lowercase, underscores)
        
        Example:
            >>> self._normalize_name("KSESSIONS")
            "ksessions"
            >>> self._normalize_name("Multi-Word-Repo")
            "multi_word_repo"
        """
        normalized = name.lower()
        normalized = re.sub(r'[-\s]+', '_', normalized)
        return normalized
    
    def _get_profile_path(self, name: str) -> Path:
        """Get file path for a repository profile."""
        normalized_name = self._normalize_name(name)
        return self.storage_path / f"{normalized_name}.yaml"
    
    def save(self, profile: RepositoryProfile) -> Path:
        """
        Save repository profile to disk.
        
        Args:
            profile: RepositoryProfile to save
            
        Returns:
            Path to saved profile file
        
        Example:
            >>> store.save(profile)
            Path('/path/to/ksessions.yaml')
        """
        profile_path = self._get_profile_path(profile.name)
        yaml_content = profile.to_yaml()
        
        profile_path.write_text(yaml_content, encoding='utf-8')
        
        return profile_path
    
    def load(self, name: str) -> RepositoryProfile:
        """
        Load repository profile from disk.
        
        Args:
            name: Repository name
            
        Returns:
            RepositoryProfile instance
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        
        Example:
            >>> profile = store.load("KSESSIONS")
        """
        profile_path = self._get_profile_path(name)
        
        if not profile_path.exists():
            raise ProfileNotFoundError(
                f"Profile not found for repository: {name}\n"
                f"Expected path: {profile_path}"
            )
        
        yaml_content = profile_path.read_text(encoding='utf-8')
        return RepositoryProfile.from_yaml(yaml_content)
    
    def exists(self, name: str) -> bool:
        """
        Check if a repository profile exists.
        
        Args:
            name: Repository name
            
        Returns:
            True if profile exists, False otherwise
        
        Example:
            >>> store.exists("KSESSIONS")
            True
        """
        profile_path = self._get_profile_path(name)
        return profile_path.exists()
    
    def delete(self, name: str) -> None:
        """
        Delete repository profile from disk.
        
        Args:
            name: Repository name
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        
        Example:
            >>> store.delete("OLD_REPO")
        """
        profile_path = self._get_profile_path(name)
        
        if not profile_path.exists():
            raise ProfileNotFoundError(
                f"Cannot delete - profile not found: {name}"
            )
        
        profile_path.unlink()
    
    def list_all(self) -> List[RepositoryProfile]:
        """
        List all repository profiles.
        
        Returns:
            List of RepositoryProfile instances
        
        Example:
            >>> profiles = store.list_all()
            >>> for profile in profiles:
            ...     print(profile.name)
        """
        profiles = []
        
        for profile_file in self.storage_path.glob("*.yaml"):
            try:
                yaml_content = profile_file.read_text(encoding='utf-8')
                profile = RepositoryProfile.from_yaml(yaml_content)
                profiles.append(profile)
            except Exception as e:
                # Log but don't fail on corrupted profile
                print(f"Warning: Failed to load profile {profile_file}: {e}")
        
        return profiles
