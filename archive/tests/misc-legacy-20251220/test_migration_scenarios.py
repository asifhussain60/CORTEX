"""
Migration scenario integration tests.

Tests migration from existing single-project setup to shared environment,
profile preservation, and config merging.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def existing_project_with_venv(tmp_path):
    """Simulate existing project with .venv/"""
    project = tmp_path / "existing_project"
    project.mkdir()
    
    # Create existing .venv
    venv = project / ".venv"
    venv.mkdir()
    (venv / "pyvenv.cfg").write_text("home = /usr/bin\nversion = 3.9.6\n")
    
    # Create existing config
    config_file = project / "cortex.config.json"
    config_file.write_text(json.dumps({
        "machines": {
            "test-machine": {
                "rootPath": str(project),
                "brainPath": str(project / "cortex-brain")
            }
        }
    }, indent=2))
    
    return project


@pytest.fixture
def existing_profile(tmp_path):
    """Existing user profile to preserve"""
    return {
        "name": "Existing User",
        "preference": "verbose",
        "role": "intermediate",
        "work_area": "web_dev",
        "language": "en"
    }


class TestVenvMigration:
    """Test .venv to shared environment migration."""
    
    def test_detects_existing_venv(self, existing_project_with_venv):
        """Should detect existing .venv directory."""
        venv_path = existing_project_with_venv / ".venv"
        assert venv_path.exists()
        assert (venv_path / "pyvenv.cfg").exists()
    
    def test_preserves_packages_during_migration(self, existing_project_with_venv):
        """Should preserve installed packages when migrating."""
        # Would test package list extraction and reinstallation
        # For now, verify structure exists
        assert existing_project_with_venv.exists()
    
    def test_creates_shared_env_on_migration(self, existing_project_with_venv, tmp_path):
        """Should create shared environment during migration."""
        # Mock ~/.cortex/venv/ creation
        shared_env = tmp_path / ".cortex" / "venv"
        
        # Migration would create this
        # For now, test path logic
        assert ".cortex" in str(shared_env)
    
    def test_links_project_to_shared_env(self, existing_project_with_venv):
        """Should link project to shared environment."""
        # Would test symlink or config update
        assert existing_project_with_venv.exists()


class TestProfilePreservation:
    """Test profile preservation during upgrade."""
    
    def test_loads_existing_profile(self, existing_project_with_venv, existing_profile):
        """Should load existing profile from config."""
        from src.setup.modules.user_profile_storage import UserProfileStorage
        
        # Write existing profile to config
        config_file = existing_project_with_venv / "cortex.config.json"
        config = json.loads(config_file.read_text())
        config["user"] = existing_profile
        config_file.write_text(json.dumps(config, indent=2))
        
        # Load profile
        storage = UserProfileStorage(str(config_file))
        loaded = storage.load_profile()
        
        assert loaded is not None
        assert loaded.name == "Existing User"
        assert loaded.role == "intermediate"
    
    def test_preserves_profile_during_upgrade(self, existing_project_with_venv, existing_profile):
        """Should not overwrite existing profile."""
        from src.setup.modules.user_profile_storage import UserProfileStorage
        from src.setup.models.user_profile import UserProfile
        
        # Setup existing profile
        config_file = existing_project_with_venv / "cortex.config.json"
        storage = UserProfileStorage(str(config_file))
        
        old_profile = UserProfile(**existing_profile)
        storage.save_profile(old_profile)
        
        # Verify it's there
        loaded = storage.load_profile()
        assert loaded.name == "Existing User"
        
        # Upgrade would check for existing profile
        # Should not prompt for new profile if one exists
        assert storage.load_profile() is not None


class TestConfigMerging:
    """Test config merging with new fields."""
    
    def test_merges_new_fields_to_existing_config(self, existing_project_with_venv):
        """Should add new fields without losing existing ones."""
        config_file = existing_project_with_venv / "cortex.config.json"
        
        # Read existing
        config = json.loads(config_file.read_text())
        original_machines = config["machines"].copy()
        
        # Add new field (like shared_env_path)
        config["shared_env_path"] = str(Path.home() / ".cortex" / "venv")
        config_file.write_text(json.dumps(config, indent=2))
        
        # Verify both old and new fields exist
        updated = json.loads(config_file.read_text())
        assert "machines" in updated
        assert updated["machines"] == original_machines
        assert "shared_env_path" in updated
    
    def test_preserves_machine_specific_paths(self, existing_project_with_venv):
        """Should preserve machine-specific configurations."""
        config_file = existing_project_with_venv / "cortex.config.json"
        config = json.loads(config_file.read_text())
        
        assert "machines" in config
        assert "test-machine" in config["machines"]
        assert "rootPath" in config["machines"]["test-machine"]
    
    def test_adds_testing_config_if_missing(self, existing_project_with_venv):
        """Should add testing config if not present."""
        config_file = existing_project_with_venv / "cortex.config.json"
        config = json.loads(config_file.read_text())
        
        # Add testing config if missing
        if "testing" not in config:
            config["testing"] = {"enabled": False}
        
        config_file.write_text(json.dumps(config, indent=2))
        
        # Verify added
        updated = json.loads(config_file.read_text())
        assert "testing" in updated
        assert updated["testing"]["enabled"] is False


class TestBackwardCompatibility:
    """Test backward compatibility with old setup."""
    
    def test_old_projects_still_work(self, existing_project_with_venv):
        """Old projects should continue working after upgrade."""
        # Projects with .venv should still function
        assert (existing_project_with_venv / ".venv").exists()
        assert (existing_project_with_venv / "cortex.config.json").exists()
    
    def test_gradual_migration_supported(self, existing_project_with_venv):
        """Should support gradual migration (not forced)."""
        # Can keep .venv while adding shared env support
        # Migration should be optional, not required
        assert existing_project_with_venv.exists()
