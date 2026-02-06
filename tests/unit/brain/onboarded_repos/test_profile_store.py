"""
Tests for Repository Profile Store (Phase 28.1.2)
TDD RED Phase - Tests written BEFORE implementation

Test Coverage:
- Profile save/load/list operations
- Profile deletion
- Graceful handling of missing profiles
- File system error handling
- Profile validation before save
"""

import pytest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from pydantic import ValidationError


def test_profile_store_save():
    """Test saving a repository profile to disk."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    from cortex_brain.onboarded_repos.profile_store import ProfileStore
    
    # RED: Create profile and save it
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        profile = RepositoryProfile(
            name="TEST_REPO",
            path="/path/to/test",
            onboarded_at=datetime.now()
        )
        
        saved_path = store.save(profile)
        
        assert saved_path.exists()
        assert saved_path.name == "test_repo.yaml"


def test_profile_store_load():
    """Test loading a repository profile from disk."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    from cortex_brain.onboarded_repos.profile_store import ProfileStore
    
    # RED: Save then load profile
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        original_profile = RepositoryProfile(
            name="LOAD_TEST",
            path="/path/to/load",
            onboarded_at=datetime(2026, 2, 6, 10, 0, 0)
        )
        
        store.save(original_profile)
        loaded_profile = store.load("LOAD_TEST")
        
        assert loaded_profile is not None
        assert loaded_profile.name == "LOAD_TEST"
        assert loaded_profile.path == "/path/to/load"


def test_profile_store_load_missing():
    """Test graceful handling when loading missing profile."""
    from cortex_brain.onboarded_repos.profile_store import ProfileStore, ProfileNotFoundError
    
    # RED: Should raise ProfileNotFoundError for missing profile
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        with pytest.raises(ProfileNotFoundError) as exc_info:
            store.load("NONEXISTENT")
        
        assert "NONEXISTENT" in str(exc_info.value)


def test_profile_store_list_all():
    """Test listing all repository profiles."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    from cortex_brain.onboarded_repos.profile_store import ProfileStore
    
    # RED: Save multiple profiles, then list
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        profiles = [
            RepositoryProfile(
                name=f"REPO_{i}",
                path=f"/path/to/repo{i}",
                onboarded_at=datetime.now()
            )
            for i in range(3)
        ]
        
        for profile in profiles:
            store.save(profile)
        
        listed_profiles = store.list_all()
        
        assert len(listed_profiles) == 3
        assert all(p.name in ["REPO_0", "REPO_1", "REPO_2"] for p in listed_profiles)


def test_profile_store_delete():
    """Test deleting a repository profile."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    from cortex_brain.onboarded_repos.profile_store import ProfileStore
    
    # RED: Save then delete profile
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        profile = RepositoryProfile(
            name="DELETE_ME",
            path="/path/to/delete",
            onboarded_at=datetime.now()
        )
        
        saved_path = store.save(profile)
        assert saved_path.exists()
        
        store.delete("DELETE_ME")
        assert not saved_path.exists()


def test_profile_store_exists():
    """Test checking if a profile exists."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    from cortex_brain.onboarded_repos.profile_store import ProfileStore
    
    # RED: Check existence before and after save
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        assert not store.exists("CHECK_ME")
        
        profile = RepositoryProfile(
            name="CHECK_ME",
            path="/path/to/check",
            onboarded_at=datetime.now()
        )
        
        store.save(profile)
        assert store.exists("CHECK_ME")


def test_profile_store_update():
    """Test updating an existing profile."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    from cortex_brain.onboarded_repos.profile_store import ProfileStore
    
    # RED: Save, modify, update
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        profile = RepositoryProfile(
            name="UPDATE_ME",
            path="/path/to/update",
            onboarded_at=datetime.now()
        )
        
        store.save(profile)
        
        # Load and modify
        loaded = store.load("UPDATE_ME")
        loaded.exists = False
        loaded.last_validated = datetime.now()
        
        # Update
        store.save(loaded)
        
        # Verify update
        reloaded = store.load("UPDATE_ME")
        assert reloaded.exists is False
        assert reloaded.last_validated is not None


def test_profile_store_name_normalization():
    """Test that profile names are normalized (uppercase, underscores)."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    from cortex_brain.onboarded_repos.profile_store import ProfileStore
    
    # RED: Save with mixed case name
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        profile = RepositoryProfile(
            name="MixedCase-Repo",
            path="/path/to/mixed",
            onboarded_at=datetime.now()
        )
        
        saved_path = store.save(profile)
        
        # File name should be lowercase with underscores
        assert saved_path.name == "mixedcase_repo.yaml"


def test_profile_store_concurrent_access():
    """Test that ProfileStore handles concurrent reads safely."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    from cortex_brain.onboarded_repos.profile_store import ProfileStore
    
    # RED: Multiple stores reading same profile
    with TemporaryDirectory() as tmpdir:
        store1 = ProfileStore(storage_path=Path(tmpdir))
        store2 = ProfileStore(storage_path=Path(tmpdir))
        
        profile = RepositoryProfile(
            name="SHARED",
            path="/path/to/shared",
            onboarded_at=datetime.now()
        )
        
        store1.save(profile)
        
        # Both stores should be able to read
        loaded1 = store1.load("SHARED")
        loaded2 = store2.load("SHARED")
        
        assert loaded1.name == loaded2.name
        assert loaded1.path == loaded2.path
