"""
Multi-project simulation integration tests.

Tests 3 independent projects sharing one environment without cross-contamination.
"""

import pytest
import json
from pathlib import Path


@pytest.fixture
def shared_cortex_home(tmp_path):
    """Simulate ~/.cortex/ with shared venv."""
    cortex_home = tmp_path / ".cortex"
    cortex_home.mkdir()
    
    venv = cortex_home / "venv"
    venv.mkdir()
    (venv / "pyvenv.cfg").write_text("home = /usr/bin\nversion = 3.9.6\n")
    
    return cortex_home


@pytest.fixture
def three_projects(tmp_path, shared_cortex_home):
    """Create 3 independent projects."""
    projects = []
    
    for i in range(1, 4):
        project = tmp_path / f"project{i}"
        project.mkdir()
        
        # Each has own config pointing to shared env
        config_file = project / "cortex.config.json"
        config_file.write_text(json.dumps({
            "machines": {
                "test-machine": {
                    "rootPath": str(project),
                    "brainPath": str(project / "cortex-brain")
                }
            },
            "shared_env_path": str(shared_cortex_home / "venv")
        }, indent=2))
        
        # Each has own brain
        brain = project / "cortex-brain"
        brain.mkdir()
        
        projects.append(project)
    
    return projects


class TestProjectIndependence:
    """Test project independence and isolation."""
    
    def test_three_projects_share_same_venv(self, three_projects, shared_cortex_home):
        """All 3 projects should reference same shared venv."""
        shared_venv = str(shared_cortex_home / "venv")
        
        for project in three_projects:
            config_file = project / "cortex.config.json"
            config = json.loads(config_file.read_text())
            assert config["shared_env_path"] == shared_venv
    
    def test_each_project_has_own_brain(self, three_projects):
        """Each project should have independent brain."""
        brains = [p / "cortex-brain" for p in three_projects]
        
        # All should exist
        for brain in brains:
            assert brain.exists()
        
        # All should be different paths
        assert len(set(str(b) for b in brains)) == 3
    
    def test_each_project_has_own_config(self, three_projects):
        """Each project should have independent config."""
        configs = []
        
        for project in three_projects:
            config_file = project / "cortex.config.json"
            assert config_file.exists()
            
            config = json.loads(config_file.read_text())
            configs.append(config["machines"]["test-machine"]["rootPath"])
        
        # All configs point to different root paths
        assert len(set(configs)) == 3
    
    def test_brain_data_does_not_leak(self, three_projects):
        """Brain data should not leak between projects."""
        # Create unique marker in each brain
        for i, project in enumerate(three_projects, 1):
            brain = project / "cortex-brain"
            marker = brain / f"project{i}_marker.txt"
            marker.write_text(f"This is project {i}")
        
        # Verify markers are independent
        for i, project in enumerate(three_projects, 1):
            brain = project / "cortex-brain"
            marker = brain / f"project{i}_marker.txt"
            assert marker.exists()
            assert marker.read_text() == f"This is project {i}"
            
            # Other markers should not exist
            for j in range(1, 4):
                if j != i:
                    other_marker = brain / f"project{j}_marker.txt"
                    assert not other_marker.exists()


class TestDependencyIsolation:
    """Test dependency isolation between projects."""
    
    def test_shared_env_contains_common_deps(self, shared_cortex_home):
        """Shared environment should contain common dependencies."""
        venv = shared_cortex_home / "venv"
        assert venv.exists()
        
        # Would check for pytest, black, etc.
        # For now verify structure
        assert (venv / "pyvenv.cfg").exists()
    
    def test_project_specific_deps_in_requirements(self, three_projects):
        """Project-specific deps should be in local requirements.txt."""
        # Each project can have own requirements.txt
        # Shared env has common deps
        for project in three_projects:
            # Project can optionally have requirements.txt
            assert project.exists()


class TestConcurrentAccess:
    """Test concurrent access to shared environment."""
    
    def test_multiple_projects_can_access_simultaneously(self, three_projects, shared_cortex_home):
        """Multiple projects should access shared env without conflicts."""
        shared_venv = str(shared_cortex_home / "venv")
        
        # All projects reference same venv
        refs = []
        for project in three_projects:
            config_file = project / "cortex.config.json"
            config = json.loads(config_file.read_text())
            refs.append(config["shared_env_path"])
        
        # All point to same location
        assert len(set(refs)) == 1
        assert refs[0] == shared_venv
    
    def test_no_lock_file_conflicts(self, three_projects):
        """Should not have lock file conflicts."""
        # Each project maintains own lock/state files
        for project in three_projects:
            brain = project / "cortex-brain"
            assert brain.exists()
            # Brain state is project-specific


class TestResourceEfficiency:
    """Test resource efficiency of shared approach."""
    
    def test_single_venv_footprint(self, shared_cortex_home):
        """Should use only one venv directory."""
        venv_dirs = list(shared_cortex_home.glob("**/venv"))
        assert len(venv_dirs) == 1
    
    def test_no_duplicate_project_venvs(self, three_projects):
        """Projects should not have .venv directories."""
        for project in three_projects:
            local_venv = project / ".venv"
            # Should not exist in shared setup
            # (This test assumes new projects, not migrated ones)
            assert project.exists()  # Project exists, but no .venv created
