"""
Phase 54-A S2 - Repository Pattern Tests
Tests for JSONProfileRepository CRUD operations and tier precedence

AC_START: AC-PHASE54A-S2-TESTS
Description: 15 unit tests for repository pattern
Authority: phase-54-A-incremental-onboarding-refactor.yaml
TDD: Tests written first (2026-02-09)
"""

import pytest
from pathlib import Path

from cortex.repositories.json_profile_repository import (
    JSONProfileRepository,
    RepositoryProfile,
    ProfileTier,
)


class TestJSONProfileRepository:
    """Tests for JSONProfileRepository."""
    
    @pytest.fixture
    def storage_path(self, tmp_path):
        """Create temporary storage path."""
        return tmp_path / "profiles.json"
    
    @pytest.fixture
    def repository(self, storage_path):
        """Create repository instance."""
        return JSONProfileRepository(storage_path)
    
    @pytest.fixture
    def sample_profile(self):
        """Create sample profile."""
        return RepositoryProfile(
            id="repo-001",
            name="test-repo",
            path="/path/to/repo",
            tier=ProfileTier.TIER_1,
            metadata={"language": "python"},
        )
    
    # ==== CRUD Tests ====
    
    def test_create_profile_success(self, repository, sample_profile):
        """Test successful profile creation."""
        result = repository.create(sample_profile)
        assert result.is_ok()
        assert result.unwrap().id == "repo-001"
    
    def test_create_duplicate_fails(self, repository, sample_profile):
        """Test creating duplicate profile fails."""
        repository.create(sample_profile)
        result = repository.create(sample_profile)
        assert result.is_err()
    
    def test_get_by_id_success(self, repository, sample_profile):
        """Test retrieving profile by ID."""
        repository.create(sample_profile)
        result = repository.get_by_id("repo-001")
        
        assert result.is_ok()
        profile = result.unwrap()
        assert profile.name == "test-repo"
    
    def test_get_by_id_not_found(self, repository):
        """Test get returns error when not found."""
        result = repository.get_by_id("nonexistent")
        assert result.is_err()
    
    def test_update_profile_success(self, repository, sample_profile):
        """Test updating profile."""
        repository.create(sample_profile)
        
        # Update
        sample_profile.name = "updated-repo"
        result = repository.update(sample_profile)
        
        assert result.is_ok()
        updated = repository.get_by_id("repo-001").unwrap()
        assert updated.name == "updated-repo"
    
    def test_update_nonexistent_fails(self, repository, sample_profile):
        """Test updating nonexistent profile fails."""
        result = repository.update(sample_profile)
        assert result.is_err()
    
    def test_delete_profile_success(self, repository, sample_profile):
        """Test deleting profile."""
        repository.create(sample_profile)
        result = repository.delete("repo-001")
        
        assert result.is_ok()
        # Verify it's deleted
        result = repository.get_by_id("repo-001")
        assert result.is_err()
    
    def test_delete_nonexistent_fails(self, repository):
        """Test deleting nonexistent profile fails."""
        result = repository.delete("nonexistent")
        assert result.is_err()
    
    # ==== List/Query Tests ====
    
    def test_list_all_profiles(self, repository, sample_profile):
        """Test listing all profiles."""
        repository.create(sample_profile)
        
        profile2 = RepositoryProfile(
            id="repo-002",
            name="another-repo",
            path="/path/to/another",
            tier=ProfileTier.TIER_2,
        )
        repository.create(profile2)
        
        result = repository.list_all()
        assert result.is_ok()
        profiles = result.unwrap()
        assert len(profiles) == 2
    
    def test_list_by_tier(self, repository):
        """Test listing profiles by tier."""
        # Create profiles of different tiers
        tier0_profile = RepositoryProfile(
            id="t0", name="tier0", path="/t0", tier=ProfileTier.TIER_0
        )
        tier1_profile = RepositoryProfile(
            id="t1", name="tier1", path="/t1", tier=ProfileTier.TIER_1
        )
        tier0_profile2 = RepositoryProfile(
            id="t0-2", name="tier0-2", path="/t0-2", tier=ProfileTier.TIER_0
        )
        
        repository.create(tier0_profile)
        repository.create(tier1_profile)
        repository.create(tier0_profile2)
        
        # List TIER-0
        result = repository.list_by_tier(ProfileTier.TIER_0)
        assert result.is_ok()
        profiles = result.unwrap()
        assert len(profiles) == 2
    
    def test_count_profiles(self, repository, sample_profile):
        """Test counting profiles."""
        repository.create(sample_profile)
        repository.create(RepositoryProfile(
            id="repo-002",
            name="another",
            path="/another",
            tier=ProfileTier.TIER_2,
        ))
        
        result = repository.count()
        assert result.is_ok()
        assert result.unwrap() == 2
    
    # ==== Tier Precedence Tests ====
    
    def test_get_highest_precedence_tier0_wins(self, repository):
        """Test TIER-0 has highest precedence."""
        # Create profiles of different tiers
        tier3 = RepositoryProfile("t3", "t3", "/t3", ProfileTier.TIER_3)
        tier1 = RepositoryProfile("t1", "t1", "/t1", ProfileTier.TIER_1)
        tier0 = RepositoryProfile("t0", "t0", "/t0", ProfileTier.TIER_0)
        tier2 = RepositoryProfile("t2", "t2", "/t2", ProfileTier.TIER_2)
        
        # Create in random order
        repository.create(tier3)
        repository.create(tier1)
        repository.create(tier2)
        repository.create(tier0)
        
        # Get highest precedence
        result = repository.get_highest_precedence()
        assert result.is_ok()
        highest = result.unwrap()
        
        # Should be TIER-0
        assert highest.tier == ProfileTier.TIER_0
        assert highest.id == "t0"
    
    def test_tier_precedence_order(self, repository):
        """Test tier precedence order is correct."""
        # Create only TIER-2 and TIER-3
        tier2 = RepositoryProfile("t2", "t2", "/t2", ProfileTier.TIER_2)
        tier3 = RepositoryProfile("t3", "t3", "/t3", ProfileTier.TIER_3)
        
        repository.create(tier3)
        repository.create(tier2)
        
        result = repository.get_highest_precedence()
        highest = result.unwrap()
        
        # TIER-2 should be highest (lower is better)
        assert highest.tier == ProfileTier.TIER_2
    
    # ==== Storage/Utility Tests ====
    
    def test_clear_all_profiles(self, repository, sample_profile):
        """Test clearing all profiles."""
        repository.create(sample_profile)
        
        result = repository.clear()
        assert result.is_ok()
        
        count_result = repository.count()
        assert count_result.unwrap() == 0
    
    def test_storage_persistence(self, storage_path):
        """Test profiles persist across repository instances."""
        # Create and add profile
        repo1 = JSONProfileRepository(storage_path)
        profile = RepositoryProfile(
            id="persistent",
            name="test",
            path="/test",
            tier=ProfileTier.TIER_1,
        )
        repo1.create(profile)
        
        # Create new instance and retrieve
        repo2 = JSONProfileRepository(storage_path)
        result = repo2.get_by_id("persistent")
        
        assert result.is_ok()
        assert result.unwrap().name == "test"


class TestRepositoryProfileEntity:
    """Tests for RepositoryProfile dataclass."""
    
    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        profile = RepositoryProfile(
            id="test",
            name="test-repo",
            path="/path",
            tier=ProfileTier.TIER_1,
            metadata={"key": "value"},
        )
        
        data = profile.to_dict()
        assert data["id"] == "test"
        assert data["tier"] == "tier-1"  # Enum converted to string
        assert data["metadata"]["key"] == "value"
    
    def test_profile_from_dict(self):
        """Test creating profile from dictionary."""
        data = {
            "id": "test",
            "name": "test-repo",
            "path": "/path",
            "tier": "tier-1",
            "metadata": {"key": "value"},
            "created_at": "2026-02-09T00:00:00",
            "updated_at": "2026-02-09T00:00:00",
        }
        
        profile = RepositoryProfile.from_dict(data)
        assert profile.id == "test"
        assert profile.tier == ProfileTier.TIER_1
        assert profile.metadata["key"] == "value"
    
    def test_profile_roundtrip(self):
        """Test profile survives dict conversion roundtrip."""
        original = RepositoryProfile(
            id="original",
            name="test",
            path="/path",
            tier=ProfileTier.TIER_2,
            metadata={"lang": "python", "size": 1024},
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = RepositoryProfile.from_dict(data)
        
        assert restored.id == original.id
        assert restored.tier == original.tier
        assert restored.metadata == original.metadata


class TestProfileTierEnum:
    """Tests for ProfileTier enumeration."""
    
    def test_tier_values(self):
        """Test tier enum values."""
        assert ProfileTier.TIER_0.value == "tier-0"
        assert ProfileTier.TIER_1.value == "tier-1"
        assert ProfileTier.TIER_2.value == "tier-2"
        assert ProfileTier.TIER_3.value == "tier-3"
    
    def test_tier_comparison(self):
        """Test tier values for precedence."""
        # All tiers should be distinct
        tiers = [ProfileTier.TIER_0, ProfileTier.TIER_1, ProfileTier.TIER_2, ProfileTier.TIER_3]
        assert len(set(tiers)) == 4


# AC_COMPLETE: AC-PHASE54A-S2-TESTS ✅
