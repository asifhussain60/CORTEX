"""
Tests for Hybrid Brain Manager (Option 2)
==========================================

**Test Coverage:**
- Shared Tier 2 path resolution
- Per-repo Tier 1/3 path resolution
- Repository ID generation
- Database path management
- Legacy migration
- Architecture info reporting
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import sqlite3

from src.tier0.hybrid_brain_manager import (
    HybridBrainManager,
    get_manager,
    get_tier1_path,
    get_tier2_path,
    get_tier3_path
)


@pytest.fixture
def temp_repo_root():
    """Create temporary repository root."""
    temp_dir = Path(tempfile.mkdtemp()) / "test-repo"
    temp_dir.mkdir(parents=True, exist_ok=True)
    yield temp_dir
    shutil.rmtree(temp_dir.parent)


@pytest.fixture
def temp_shared_dir():
    """Create temporary shared directory."""
    temp_dir = Path(tempfile.mkdtemp()) / ".cortex" / "shared"
    temp_dir.mkdir(parents=True, exist_ok=True)
    yield temp_dir
    shutil.rmtree(temp_dir.parent.parent)


@pytest.fixture
def temp_legacy_brain():
    """Create temporary legacy brain directory with sample data."""
    temp_dir = Path(tempfile.mkdtemp()) / "cortex-brain"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create legacy structure
    (temp_dir / "tier1").mkdir()
    (temp_dir / "tier2").mkdir()
    (temp_dir / "tier3").mkdir()
    
    # Create sample database files
    tier1_db = temp_dir / "tier1" / "working-memory.db"
    tier2_db = temp_dir / "tier2" / "knowledge-graph.db"
    tier3_db = temp_dir / "tier3" / "development_context.db"
    
    for db_path in [tier1_db, tier2_db, tier3_db]:
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test_data (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO test_data VALUES (1, 'test')")
        conn.commit()
        conn.close()
    
    yield temp_dir
    shutil.rmtree(temp_dir.parent)


class TestHybridBrainManager:
    """Test HybridBrainManager class."""
    
    def test_initialization(self, temp_repo_root):
        """Test manager initialization."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        assert manager.repo_root == temp_repo_root
        assert manager.repo_cortex_dir == temp_repo_root / ".cortex"
    
    def test_get_tier1_path_per_repo(self, temp_repo_root):
        """Test Tier 1 path is per-repository."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        tier1_path = manager.get_tier1_path()
        
        assert tier1_path == temp_repo_root / ".cortex" / "tier1"
        assert tier1_path.exists()  # Should be created
    
    def test_get_tier2_path_shared(self, temp_repo_root):
        """Test Tier 2 path is shared (not in repo)."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        # Monkey patch shared location
        manager.SHARED_TIER2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        
        tier2_path = manager.get_tier2_path()
        
        assert tier2_path == manager.SHARED_TIER2
        assert tier2_path.exists()  # Should be created
        
        # Verify it's NOT in repo
        assert temp_repo_root not in tier2_path.parents
    
    def test_get_tier3_path_per_repo(self, temp_repo_root):
        """Test Tier 3 path is per-repository."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        tier3_path = manager.get_tier3_path()
        
        assert tier3_path == temp_repo_root / ".cortex" / "tier3"
        assert tier3_path.exists()  # Should be created
    
    def test_database_paths(self, temp_repo_root):
        """Test database path generation."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        # Monkey patch shared location
        manager.SHARED_TIER2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        
        tier1_db = manager.get_tier1_db_path()
        tier2_db = manager.get_tier2_db_path()
        tier3_db = manager.get_tier3_db_path()
        
        assert tier1_db.name == "working-memory.db"
        assert tier2_db.name == "knowledge-graph.db"
        assert tier3_db.name == "development_context.db"
        
        # Tier 1 and 3 in repo, Tier 2 shared
        assert temp_repo_root in tier1_db.parents
        assert temp_repo_root not in tier2_db.parents  # Shared!
        assert temp_repo_root in tier3_db.parents
    
    def test_repository_id_generation(self, temp_repo_root):
        """Test repository ID is based on directory name."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        repo_id = manager.get_repository_id()
        
        assert repo_id == temp_repo_root.name
    
    def test_is_hybrid_architecture_enabled(self, temp_repo_root):
        """Test checking if hybrid architecture is enabled."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        # Before creating shared tier2
        manager.SHARED_TIER2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        assert manager.is_hybrid_architecture_enabled() is False
        
        # After creating shared tier2
        manager.get_tier2_path()  # Creates directory
        assert manager.is_hybrid_architecture_enabled() is True
    
    def test_get_architecture_info(self, temp_repo_root):
        """Test getting architecture configuration info."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        info = manager.get_architecture_info()
        
        assert info["architecture_type"] == "hybrid"
        assert info["version"] == "2.0"
        assert info["repo_id"] == temp_repo_root.name
        assert "tier1_db" in info
        assert "tier2_db" in info
        assert "tier3_db" in info
    
    def test_migrate_from_legacy_tier1(self, temp_repo_root, temp_legacy_brain):
        """Test migrating Tier 1 from legacy brain."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        summary = manager.migrate_from_legacy(temp_legacy_brain)
        
        assert summary["tier1_migrated"] is True
        assert (temp_repo_root / ".cortex" / "tier1" / "working-memory.db").exists()
    
    def test_migrate_from_legacy_tier2(self, temp_repo_root, temp_legacy_brain):
        """Test migrating Tier 2 from legacy brain to shared location."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        # Monkey patch shared location
        manager.SHARED_TIER2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        
        summary = manager.migrate_from_legacy(temp_legacy_brain)
        
        assert summary["tier2_migrated"] is True
        assert manager.get_tier2_db_path().exists()
        
        # Verify it's in shared location, not repo
        assert temp_repo_root not in manager.get_tier2_db_path().parents
    
    def test_migrate_from_legacy_tier3(self, temp_repo_root, temp_legacy_brain):
        """Test migrating Tier 3 from legacy brain."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        summary = manager.migrate_from_legacy(temp_legacy_brain)
        
        assert summary["tier3_migrated"] is True
        assert (temp_repo_root / ".cortex" / "tier3" / "development_context.db").exists()
    
    def test_migrate_from_legacy_complete(self, temp_repo_root, temp_legacy_brain):
        """Test complete legacy migration."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        # Monkey patch shared location
        manager.SHARED_TIER2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        
        summary = manager.migrate_from_legacy(temp_legacy_brain)
        
        assert summary["tier1_migrated"] is True
        assert summary["tier2_migrated"] is True
        assert summary["tier3_migrated"] is True
        assert len(summary["errors"]) == 0
    
    def test_migrate_from_nonexistent_legacy(self, temp_repo_root):
        """Test migration fails gracefully with nonexistent legacy dir."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        nonexistent = temp_repo_root / "nonexistent-brain"
        
        with pytest.raises(FileNotFoundError):
            manager.migrate_from_legacy(nonexistent)
    
    def test_ensure_directories_creates_all(self, temp_repo_root):
        """Test _ensure_directories creates all required directories."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        # Monkey patch shared location
        manager.SHARED_TIER2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        
        manager._ensure_directories()
        
        assert (temp_repo_root / ".cortex").exists()
        assert (temp_repo_root / ".cortex" / "tier1").exists()
        assert (temp_repo_root / ".cortex" / "tier3").exists()
        assert manager.SHARED_TIER2.exists()


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_get_tier1_path_convenience(self, temp_repo_root):
        """Test get_tier1_path() convenience function."""
        path = get_tier1_path(repo_root=temp_repo_root)
        
        assert path == temp_repo_root / ".cortex" / "tier1"
    
    def test_get_tier2_path_convenience(self, temp_repo_root):
        """Test get_tier2_path() convenience function."""
        manager = get_manager(repo_root=temp_repo_root)
        manager.SHARED_TIER2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        
        path = get_tier2_path(repo_root=temp_repo_root)
        
        assert path == manager.SHARED_TIER2
    
    def test_get_tier3_path_convenience(self, temp_repo_root):
        """Test get_tier3_path() convenience function."""
        path = get_tier3_path(repo_root=temp_repo_root)
        
        assert path == temp_repo_root / ".cortex" / "tier3"
    
    def test_singleton_manager(self):
        """Test singleton pattern for manager instance."""
        manager1 = get_manager()
        manager2 = get_manager()
        
        assert manager1 is manager2


class TestHybridVsLegacyArchitecture:
    """Test differences between hybrid and legacy architectures."""
    
    def test_tier2_location_difference(self, temp_repo_root):
        """Test Tier 2 is in different location than legacy."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        # Monkey patch shared location
        manager.SHARED_TIER2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        
        tier2_path = manager.get_tier2_path()
        legacy_tier2_path = temp_repo_root / "cortex-brain" / "tier2"
        
        assert tier2_path != legacy_tier2_path
        assert temp_repo_root not in tier2_path.parents
    
    def test_tier1_tier3_location_similar_to_legacy(self, temp_repo_root):
        """Test Tier 1/3 remain in repo (similar to legacy)."""
        manager = HybridBrainManager(repo_root=temp_repo_root)
        
        tier1_path = manager.get_tier1_path()
        tier3_path = manager.get_tier3_path()
        
        # Both should be in repo (like legacy)
        assert temp_repo_root in tier1_path.parents
        assert temp_repo_root in tier3_path.parents


class TestMultiRepoScenario:
    """Test hybrid architecture with multiple repositories."""
    
    def test_shared_tier2_across_repos(self, temp_repo_root):
        """Test Tier 2 is shared across multiple repos."""
        # Create two repo managers
        repo1 = temp_repo_root / "repo1"
        repo2 = temp_repo_root / "repo2"
        repo1.mkdir(parents=True)
        repo2.mkdir(parents=True)
        
        manager1 = HybridBrainManager(repo_root=repo1)
        manager2 = HybridBrainManager(repo_root=repo2)
        
        # Monkey patch shared location (same for both)
        shared_tier2 = temp_repo_root.parent / ".cortex" / "shared" / "tier2"
        manager1.SHARED_TIER2 = shared_tier2
        manager2.SHARED_TIER2 = shared_tier2
        
        # Both should point to same Tier 2
        tier2_path1 = manager1.get_tier2_path()
        tier2_path2 = manager2.get_tier2_path()
        
        assert tier2_path1 == tier2_path2
    
    def test_isolated_tier1_per_repo(self, temp_repo_root):
        """Test Tier 1 is isolated per repository."""
        repo1 = temp_repo_root / "repo1"
        repo2 = temp_repo_root / "repo2"
        repo1.mkdir(parents=True)
        repo2.mkdir(parents=True)
        
        manager1 = HybridBrainManager(repo_root=repo1)
        manager2 = HybridBrainManager(repo_root=repo2)
        
        tier1_path1 = manager1.get_tier1_path()
        tier1_path2 = manager2.get_tier1_path()
        
        # Should be different paths
        assert tier1_path1 != tier1_path2
        assert repo1 in tier1_path1.parents
        assert repo2 in tier1_path2.parents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
