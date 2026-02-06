"""
Integration test for KSESSIONS onboarding (Phase 28.2.1)
Tests actual KSESSIONS repository onboarding with profile generation
"""

import pytest
from pathlib import Path
from datetime import datetime


def test_ksessions_onboarding_complete():
    """Test complete KSESSIONS onboarding with real repository."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        get_repository_onboarding_orchestrator
    )
    from cortex_brain.onboarded_repos import ProfileStore
    from tempfile import TemporaryDirectory
    
    orchestrator = get_repository_onboarding_orchestrator()
    
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        ksessions_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
        
        # Skip test if KSESSIONS doesn't exist
        if not ksessions_path.exists():
            pytest.skip("KSESSIONS repository not found")
        
        # Onboard KSESSIONS
        profile = orchestrator.onboard_repository_with_profile(
            repo_path=ksessions_path,
            profile_store=store
        )
        
        # Verify profile generated
        assert profile is not None
        assert profile.name == "KSESSIONS"
        assert profile.path == str(ksessions_path.absolute())
        assert profile.onboarded_at is not None
        
        # Verify profile saved
        assert store.exists("KSESSIONS")
        
        # Verify profile can be loaded
        loaded_profile = store.load("KSESSIONS")
        assert loaded_profile.name == "KSESSIONS"


def test_ksessions_profile_valid():
    """Test that KSESSIONS profile contains expected metadata."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        get_repository_onboarding_orchestrator
    )
    from tempfile import TemporaryDirectory
    from cortex_brain.onboarded_repos import ProfileStore
    
    orchestrator = get_repository_onboarding_orchestrator()
    
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        ksessions_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
        
        if not ksessions_path.exists():
            pytest.skip("KSESSIONS repository not found")
        
        profile = orchestrator.onboard_repository_with_profile(
            repo_path=ksessions_path,
            profile_store=store
        )
        
        # Verify tech stack populated
        assert profile.tech_stack is not None
        assert profile.tech_stack.primary_language is not None
        assert len(profile.tech_stack.languages) > 0
        
        # Verify structure metadata
        assert profile.structure is not None
        
        # Verify loose coupling metadata
        assert profile.loose_coupling is not None
        assert profile.loose_coupling.deletion_safe is True


def test_ksessions_deletion_safety():
    """Test that CORTEX continues gracefully if KSESSIONS is deleted."""
    from cortex_brain.onboarded_repos import ProfileStore, RepositoryProfile
    from tempfile import TemporaryDirectory
    from datetime import datetime
    
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        # Create a mock profile (simulating KSESSIONS onboarding)
        profile = RepositoryProfile(
            name="KSESSIONS_MOCK",
            path="/tmp/nonexistent_ksessions",
            onboarded_at=datetime.now()
        )
        
        # Save profile
        store.save(profile)
        
        # Load profile (should work even if path doesn't exist)
        loaded = store.load("KSESSIONS_MOCK")
        assert loaded is not None
        
        # Update exists flag
        loaded.validate_exists()
        assert loaded.exists is False  # Path doesn't exist
        
        # CORTEX should continue without errors (graceful degradation)
        assert loaded.loose_coupling.fallback_strategy == "use_cached_profile"
