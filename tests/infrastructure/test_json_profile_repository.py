"""
AC-054A-S2-01 through S2-10: JSONProfileRepository Tests

TDD Test Suite (15+ tests):
- AC-054A-S2-01: Repository implements get_by_name()
- AC-054A-S2-02: Repository implements save()
- AC-054A-S2-03: Repository implements delete()
- AC-054A-S2-04: Repository implements list_all()
- AC-054A-S2-05: Repository implements exists()
- AC-054A-S2-06: Validates OnboardingProfile schema
- AC-054A-S2-07: Rejects invalid profiles
- AC-054A-S2-08: Handles missing files gracefully
- AC-054A-S2-09: Handles write errors
- AC-054A-S2-10: Creates directories as needed

Author: Phase 54-A Implementation
Created: 2026-02-09
Platform: Windows/macOS compatible
"""

import pytest
import json
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class OnboardingProfile:
    """Onboarding profile model."""
    repo_name: str
    repo_url: str
    analysis_data: dict
    created_at: str
    updated_at: str


class TestJSONProfileRepository:
    """Test JSON profile repository implementation."""

    @pytest.fixture
    def repo_path(self, tmp_path):
        """Fixture: Temporary repository storage path."""
        storage = tmp_path / "profiles"
        return storage

    @pytest.fixture
    def repository(self, repo_path):
        """Fixture: JSONProfileRepository instance."""
        from cortex.repositories import JSONProfileRepository
        return JSONProfileRepository(storage_path=repo_path)

    @pytest.fixture
    def sample_profile(self) -> dict:
        """Fixture: Sample profile data."""
        return {
            "repo_name": "test-repo",
            "repo_url": "https://github.com/test/repo",
            "analysis_data": {
                "language": "Python",
                "stars": 100,
                "test_coverage": 0.85,
            },
            "created_at": "2026-02-09T10:00:00Z",
            "updated_at": "2026-02-09T10:00:00Z",
        }

    def test_save_profile(self, repository, sample_profile):
        """AC-054A-S2-02: Repository implements save()."""
        result = repository.save(sample_profile)
        
        assert result is not None
        assert isinstance(result, str)  # Returns file path

    def test_get_by_name(self, repository, sample_profile):
        """AC-054A-S2-01: Repository implements get_by_name()."""
        repository.save(sample_profile)
        
        retrieved = repository.get_by_name("test-repo")
        
        assert retrieved is not None
        assert retrieved["repo_name"] == "test-repo"

    def test_delete_profile(self, repository, sample_profile):
        """AC-054A-S2-03: Repository implements delete()."""
        repository.save(sample_profile)
        
        # Delete
        result = repository.delete("test-repo")
        assert result is True
        
        # Verify deleted
        retrieved = repository.get_by_name("test-repo")
        assert retrieved is None

    def test_list_all_profiles(self, repository, sample_profile):
        """AC-054A-S2-04: Repository implements list_all()."""
        # Save multiple profiles
        profile1 = {**sample_profile, "repo_name": "repo1"}
        profile2 = {**sample_profile, "repo_name": "repo2"}
        
        repository.save(profile1)
        repository.save(profile2)
        
        all_profiles = repository.list_all()
        
        assert len(all_profiles) == 2
        assert any(p["repo_name"] == "repo1" for p in all_profiles)
        assert any(p["repo_name"] == "repo2" for p in all_profiles)

    def test_exists_check(self, repository, sample_profile):
        """AC-054A-S2-05: Repository implements exists()."""
        repository.save(sample_profile)
        
        assert repository.exists("test-repo") is True
        assert repository.exists("nonexistent") is False

    def test_validates_profile_schema(self, repository):
        """AC-054A-S2-06: Validates OnboardingProfile schema."""
        invalid_profile = {
            "repo_name": "test",
            # Missing required fields
        }
        
        with pytest.raises((ValueError, TypeError, KeyError)):
            repository.save(invalid_profile)

    def test_rejects_invalid_profiles(self, repository):
        """AC-054A-S2-07: Rejects invalid profiles."""
        invalid_profiles = [
            {"repo_name": None},  # Invalid: name is None
            {"repo_url": "invalid-url"},  # Invalid: no repo_name
            {"analysis_data": "not a dict"},  # Invalid: wrong type
        ]
        
        for invalid in invalid_profiles:
            with pytest.raises((ValueError, TypeError, KeyError)):
                repository.save(invalid)

    def test_handles_missing_files(self, repository):
        """AC-054A-S2-08: Handles missing files gracefully."""
        # Try to get non-existent profile
        result = repository.get_by_name("nonexistent")
        
        assert result is None  # Should return None, not raise

    def test_handles_write_errors(self, repository, sample_profile, tmp_path):
        """AC-054A-S2-09: Handles write errors."""
        # Create read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)
        
        try:
            repo_readonly = __import__(
                "cortex.repositories",
                fromlist=["JSONProfileRepository"]
            ).JSONProfileRepository(storage_path=readonly_dir)
            
            # Should handle error gracefully
            with pytest.raises(PermissionError):
                repo_readonly.save(sample_profile)
        finally:
            readonly_dir.chmod(0o755)

    def test_creates_directories_as_needed(self, tmp_path):
        """AC-054A-S2-10: Creates directories as needed."""
        from cortex.repositories import JSONProfileRepository
        
        # Use nested path that doesn't exist
        storage_path = tmp_path / "nested" / "path" / "to" / "storage"
        
        repository = JSONProfileRepository(storage_path=storage_path)
        # Directory should be created on initialization or first save
        
        profile = {
            "repo_name": "test",
            "repo_url": "https://example.com",
            "analysis_data": {},
            "created_at": "2026-02-09T10:00:00Z",
            "updated_at": "2026-02-09T10:00:00Z",
        }
        
        repository.save(profile)
        
        # Verify directory was created
        assert storage_path.exists()


class TestJSONProfileRepositoryIntegration:
    """Integration tests for repository pattern."""

    def test_repository_file_structure(self, tmp_path):
        """Test repository creates proper file structure."""
        from cortex.repositories import JSONProfileRepository
        
        repo = JSONProfileRepository(storage_path=tmp_path)
        
        profile = {
            "repo_name": "integration-test",
            "repo_url": "https://github.com/test/integration",
            "analysis_data": {"test": True},
            "created_at": "2026-02-09T10:00:00Z",
            "updated_at": "2026-02-09T10:00:00Z",
        }
        
        result = repo.save(profile)
        
        # Should create file at: storage_path/repo_name.json
        expected_path = tmp_path / "integration-test.json"
        assert expected_path.exists()

    def test_repository_persistence(self, tmp_path):
        """Test repository data persists across instances."""
        from cortex.repositories import JSONProfileRepository
        
        # Save with first instance
        repo1 = JSONProfileRepository(storage_path=tmp_path)
        profile = {
            "repo_name": "persistent",
            "repo_url": "https://example.com",
            "analysis_data": {"persisted": True},
            "created_at": "2026-02-09T10:00:00Z",
            "updated_at": "2026-02-09T10:00:00Z",
        }
        repo1.save(profile)
        
        # Read with second instance
        repo2 = JSONProfileRepository(storage_path=tmp_path)
        retrieved = repo2.get_by_name("persistent")
        
        assert retrieved is not None
        assert retrieved["analysis_data"]["persisted"] is True
