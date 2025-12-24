"""
Tests for WorkspaceRegistry

Tests workspace registration, discovery, and persistence.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import pytest
import uuid
import json
import yaml
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from src.core.workspace_registry import (
    WorkspaceRegistry,
    RegisteredWorkspace,
    WorkspaceStatus,
    get_workspace_registry
)
from src.core.workspace_detector import WorkspaceInfo, WorkspaceDetectionMethod
from src.core.ide_detector import IDEType


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX root structure."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # Create cortex-brain structure
    brain_dir = cortex_root / "cortex-brain"
    brain_dir.mkdir()
    
    config_dir = brain_dir / "config"
    config_dir.mkdir()
    
    return cortex_root


@pytest.fixture
def temp_user_workspace(tmp_path):
    """Create temporary user workspace."""
    workspace = tmp_path / "UserApp"
    workspace.mkdir()
    
    # Add project markers
    (workspace / "pyproject.toml").write_text("[project]\nname = 'userapp'")
    (workspace / ".git").mkdir()
    
    return workspace


@pytest.fixture
def registry(temp_cortex_root):
    """Create WorkspaceRegistry with temp root."""
    return WorkspaceRegistry(cortex_root=temp_cortex_root)


@pytest.fixture
def sample_workspace_info(temp_user_workspace):
    """Create sample WorkspaceInfo."""
    return WorkspaceInfo(
        workspace_id="test-workspace",
        path=temp_user_workspace,
        name="UserApp",
        project_type="python",
        ide_type=IDEType.VSCODE,
        detection_method=WorkspaceDetectionMethod.CWD_SEARCH
    )


class TestWorkspaceRegistry:
    """Test WorkspaceRegistry initialization and basic operations."""
    
    def test_initialization(self, registry, temp_cortex_root):
        """Test registry initializes with correct paths."""
        assert registry.cortex_root == temp_cortex_root
        assert registry.registry_file == temp_cortex_root / "cortex-brain" / "config" / "workspace-registry.yaml"
        assert isinstance(registry.workspaces, dict)
    
    def test_registry_file_created(self, registry):
        """Test registry file is created on first save."""
        # Initially no file
        assert not registry.registry_file.exists()
        
        # Register workspace triggers save
        with patch.object(registry, 'register_current_workspace') as mock_register:
            mock_workspace = RegisteredWorkspace(
                workspace_id=str(uuid.uuid4()),
                path="/fake/path",
                name="TestWorkspace",
                project_type="python",
                status=WorkspaceStatus.ACTIVE,
                first_seen=datetime.now().isoformat(),
                last_accessed=datetime.now().isoformat()
            )
            registry.workspaces[mock_workspace.workspace_id] = mock_workspace
            registry._save_registry()
        
        # File now exists
        assert registry.registry_file.exists()
    
    def test_empty_registry_loads_without_error(self, registry):
        """Test loading empty registry doesn't raise errors."""
        assert len(registry.workspaces) == 0


class TestWorkspaceRegistration:
    """Test workspace registration functionality."""
    
    def test_register_new_workspace(self, registry, sample_workspace_info):
        """Test registering a new workspace."""
        registered = registry.register_workspace(sample_workspace_info)
        
        assert registered.workspace_id
        assert uuid.UUID(registered.workspace_id)  # Valid UUID
        assert registered.path == str(sample_workspace_info.path)
        assert registered.name == "UserApp"
        assert registered.project_type == "python"
        assert registered.status == WorkspaceStatus.ACTIVE
        assert registered.first_seen
        assert registered.last_accessed
    
    def test_register_creates_cortex_directory(self, registry, sample_workspace_info):
        """Test registration creates .cortex directory."""
        registered = registry.register_workspace(sample_workspace_info)
        
        cortex_dir = sample_workspace_info.path / ".cortex"
        assert cortex_dir.exists()
        assert cortex_dir.is_dir()
    
    def test_register_creates_workspace_id_file(self, registry, sample_workspace_info):
        """Test registration creates workspace-id.txt."""
        registered = registry.register_workspace(sample_workspace_info)
        
        id_file = sample_workspace_info.path / ".cortex" / "workspace-id.txt"
        assert id_file.exists()
        assert id_file.read_text().strip() == registered.workspace_id
    
    def test_register_creates_config_file(self, registry, sample_workspace_info, temp_cortex_root):
        """Test registration creates config.json."""
        registered = registry.register_workspace(sample_workspace_info)
        
        config_file = sample_workspace_info.path / ".cortex" / "config.json"
        assert config_file.exists()
        
        config_data = json.loads(config_file.read_text())
        assert config_data['cortex_installation'] == str(temp_cortex_root)
        assert config_data['workspace_id'] == registered.workspace_id
        assert 'created' in config_data
    
    def test_register_existing_workspace_updates_last_accessed(self, registry, sample_workspace_info):
        """Test re-registering workspace updates last_accessed."""
        # Register first time
        first = registry.register_workspace(sample_workspace_info)
        first_accessed = first.last_accessed
        
        # Register again
        import time
        time.sleep(0.01)  # Ensure timestamp differs
        second = registry.register_workspace(sample_workspace_info)
        
        assert second.workspace_id == first.workspace_id
        assert second.last_accessed != first_accessed
    
    def test_register_adds_to_registry_dict(self, registry, sample_workspace_info):
        """Test registered workspace added to registry dictionary."""
        registered = registry.register_workspace(sample_workspace_info)
        
        assert registered.workspace_id in registry.workspaces
        assert registry.workspaces[registered.workspace_id] == registered


class TestWorkspaceRetrieval:
    """Test workspace lookup functionality."""
    
    def test_get_by_path_exact_match(self, registry, sample_workspace_info):
        """Test get_by_path with exact path match."""
        registered = registry.register_workspace(sample_workspace_info)
        
        found = registry.get_by_path(str(sample_workspace_info.path))
        assert found is not None
        assert found.workspace_id == registered.workspace_id
    
    def test_get_by_path_normalized(self, registry, sample_workspace_info):
        """Test get_by_path normalizes paths."""
        registered = registry.register_workspace(sample_workspace_info)
        
        # Add trailing slash
        path_with_slash = str(sample_workspace_info.path) + "/"
        found = registry.get_by_path(path_with_slash)
        assert found is not None
        assert found.workspace_id == registered.workspace_id
    
    def test_get_by_path_not_found(self, registry):
        """Test get_by_path returns None for unknown path."""
        found = registry.get_by_path("/nonexistent/path")
        assert found is None
    
    def test_get_by_id_found(self, registry, sample_workspace_info):
        """Test get_by_id with valid UUID."""
        registered = registry.register_workspace(sample_workspace_info)
        
        found = registry.get_by_id(registered.workspace_id)
        assert found is not None
        assert found.workspace_id == registered.workspace_id
    
    def test_get_by_id_not_found(self, registry):
        """Test get_by_id returns None for unknown UUID."""
        fake_uuid = str(uuid.uuid4())
        found = registry.get_by_id(fake_uuid)
        assert found is None


class TestWorkspaceListing:
    """Test workspace listing and filtering."""
    
    def test_list_workspaces_empty(self, registry):
        """Test listing with no workspaces."""
        workspaces = registry.list_workspaces()
        assert workspaces == []
    
    def test_list_workspaces_all(self, registry, temp_user_workspace):
        """Test listing all workspaces."""
        # Register multiple workspaces
        for i in range(3):
            workspace_dir = temp_user_workspace.parent / f"App{i}"
            workspace_dir.mkdir()
            (workspace_dir / "pyproject.toml").write_text("")
            
            workspace_info = WorkspaceInfo(
                workspace_id=f"app{i}",
                path=workspace_dir,
                name=f"App{i}",
                project_type="python",
                ide_type=IDEType.VSCODE,
                detection_method=WorkspaceDetectionMethod.CWD_SEARCH
            )
            registry.register_workspace(workspace_info)
        
        workspaces = registry.list_workspaces()
        assert len(workspaces) == 3
    
    def test_list_workspaces_sorted_by_last_accessed(self, registry, temp_user_workspace):
        """Test workspaces sorted by last accessed (most recent first)."""
        import time
        
        # Register 3 workspaces with delays
        workspace_ids = []
        for i in range(3):
            workspace_dir = temp_user_workspace.parent / f"App{i}"
            workspace_dir.mkdir()
            (workspace_dir / "pyproject.toml").write_text("")
            
            workspace_info = WorkspaceInfo(
                workspace_id=f"app{i}",
                path=workspace_dir,
                name=f"App{i}",
                project_type="python",
                ide_type=IDEType.VSCODE,
                detection_method=WorkspaceDetectionMethod.CWD_SEARCH
            )
            registered = registry.register_workspace(workspace_info)
            workspace_ids.append(registered.workspace_id)
            time.sleep(0.01)
        
        workspaces = registry.list_workspaces()
        
        # Most recent (App2) should be first
        assert workspaces[0].name == "App2"
        assert workspaces[2].name == "App0"
    
    def test_list_workspaces_filter_by_status(self, registry, temp_user_workspace):
        """Test filtering workspaces by status."""
        # Register 2 workspaces
        for i in range(2):
            workspace_dir = temp_user_workspace.parent / f"App{i}"
            workspace_dir.mkdir()
            (workspace_dir / "pyproject.toml").write_text("")
            
            workspace_info = WorkspaceInfo(
                workspace_id=f"app{i}",
                path=workspace_dir,
                name=f"App{i}",
                project_type="python",
                ide_type=IDEType.VSCODE,
                detection_method=WorkspaceDetectionMethod.CWD_SEARCH
            )
            registered = registry.register_workspace(workspace_info)
            
            # Archive first workspace
            if i == 0:
                registry.archive_workspace(registered.workspace_id)
        
        # Filter for active only
        active = registry.list_workspaces(status=WorkspaceStatus.ACTIVE)
        assert len(active) == 1
        assert active[0].name == "App1"
        
        # Filter for archived only
        archived = registry.list_workspaces(status=WorkspaceStatus.ARCHIVED)
        assert len(archived) == 1
        assert archived[0].name == "App0"


class TestWorkspaceArchiving:
    """Test workspace archiving functionality."""
    
    def test_archive_workspace_success(self, registry, sample_workspace_info):
        """Test archiving a workspace."""
        registered = registry.register_workspace(sample_workspace_info)
        
        success = registry.archive_workspace(registered.workspace_id)
        assert success is True
        
        # Verify status changed
        workspace = registry.get_by_id(registered.workspace_id)
        assert workspace.status == WorkspaceStatus.ARCHIVED
    
    def test_archive_workspace_not_found(self, registry):
        """Test archiving non-existent workspace."""
        fake_uuid = str(uuid.uuid4())
        success = registry.archive_workspace(fake_uuid)
        assert success is False


class TestWorkspacePersistence:
    """Test registry persistence to YAML."""
    
    def test_save_and_load_registry(self, registry, sample_workspace_info):
        """Test saving and loading registry preserves data."""
        # Register workspace
        registered = registry.register_workspace(sample_workspace_info)
        
        # Create new registry instance (loads from file)
        new_registry = WorkspaceRegistry(cortex_root=registry.cortex_root)
        
        # Verify data loaded
        assert len(new_registry.workspaces) == 1
        loaded = new_registry.get_by_id(registered.workspace_id)
        assert loaded is not None
        assert loaded.name == "UserApp"
        assert loaded.project_type == "python"
    
    def test_registry_yaml_format(self, registry, sample_workspace_info):
        """Test registry YAML file structure."""
        registered = registry.register_workspace(sample_workspace_info)
        
        # Read YAML file
        with open(registry.registry_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'version' in data
        assert 'cortex_root' in data
        assert 'updated' in data
        assert 'workspaces' in data
        assert registered.workspace_id in data['workspaces']


class TestAutoDiscovery:
    """Test automatic workspace discovery."""
    
    def test_auto_discover_git_repos(self, registry, tmp_path):
        """Test discovering git repositories."""
        # Create 2 git repos with project markers
        for i in range(2):
            repo = tmp_path / f"Repo{i}"
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / "package.json").write_text("{}")
        
        discovered = registry.auto_discover_workspaces([tmp_path])
        assert discovered == 2
        assert len(registry.workspaces) == 2
    
    def test_auto_discover_skips_existing(self, registry, temp_user_workspace):
        """Test auto-discovery skips already registered workspaces."""
        # Register manually
        workspace_info = WorkspaceInfo(
            workspace_id="manual",
            path=temp_user_workspace,
            name="UserApp",
            project_type="python",
            ide_type=IDEType.VSCODE,
            detection_method=WorkspaceDetectionMethod.CWD_SEARCH
        )
        registry.register_workspace(workspace_info)
        
        # Try auto-discovery
        discovered = registry.auto_discover_workspaces([temp_user_workspace.parent])
        assert discovered == 0  # Already registered


class TestGlobalRegistryInstance:
    """Test global registry singleton."""
    
    def test_get_workspace_registry_singleton(self):
        """Test get_workspace_registry returns same instance."""
        registry1 = get_workspace_registry()
        registry2 = get_workspace_registry()
        
        assert registry1 is registry2
