"""
Tests for Repository Discovery Service

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
from src.operations.modules.dashboard.repository_discovery_service import (
    RepositoryDiscoveryService,
    RepoMetadata,
    discover_and_register_repositories
)


@pytest.fixture
def mock_config(tmp_path):
    """Mock dashboard config"""
    repos_path = tmp_path / "repos"
    repos_path.mkdir()
    registry_path = tmp_path / "registry.json"
    
    config = Mock()
    config.get_path = Mock(side_effect=lambda key: {
        'repos': repos_path,
        'repository_registry': registry_path
    }.get(key))
    
    collector_config = Mock()
    collector_config.required_files = [
        "health-data.json",
        "tech-stack.json",
        "security.json",
        "architecture.json",
        "code-organization.json",
        "team-metrics.json",
        "vendors.json",
        "metadata.json"
    ]
    config.get_collector_config = Mock(return_value=collector_config)
    
    discovery_config = Mock()
    discovery_config.min_data_files = 3
    discovery_config.require_metadata = True
    discovery_config.auto_scan = True
    config.get_discovery_config = Mock(return_value=discovery_config)
    
    return config


@pytest.fixture
def service(mock_config):
    """Create discovery service with mocked config"""
    with patch('src.operations.modules.dashboard.repository_discovery_service.get_config', return_value=mock_config):
        return RepositoryDiscoveryService()


def test_discovery_service_initialization(service, mock_config):
    """Test service initializes correctly"""
    assert service.repos_path == mock_config.get_path('repos')
    assert service.registry_path == mock_config.get_path('repository_registry')


def test_validate_repository_with_minimal_files(service, tmp_path):
    """Test validation with minimum required files"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    
    # Create minimal files
    (repo_path / "health-data.json").write_text("{}")
    (repo_path / "metadata.json").write_text("{}")
    (repo_path / "tech-stack.json").write_text("{}")
    
    # Should be valid
    assert service.validate_repository(repo_path)


def test_validate_repository_missing_files(service, tmp_path):
    """Test validation fails with too few files"""
    repo_path = tmp_path / "invalid-repo"
    repo_path.mkdir()
    
    # Only one file
    (repo_path / "health-data.json").write_text("{}")
    
    # Should be invalid
    assert not service.validate_repository(repo_path)


def test_validate_repository_missing_metadata(service, tmp_path):
    """Test validation fails without metadata when required"""
    repo_path = tmp_path / "no-metadata-repo"
    repo_path.mkdir()
    
    # Create files without metadata
    (repo_path / "health-data.json").write_text("{}")
    (repo_path / "tech-stack.json").write_text("{}")
    (repo_path / "security.json").write_text("{}")
    (repo_path / "architecture.json").write_text("{}")
    
    # Should be invalid (missing metadata)
    assert not service.validate_repository(repo_path)


def test_scan_repositories_finds_valid_repos(service, mock_config):
    """Test scanning finds valid repositories"""
    repos_path = mock_config.get_path('repos')
    
    # Create valid repo
    valid_repo = repos_path / "valid-repo"
    valid_repo.mkdir()
    (valid_repo / "health-data.json").write_text("{}")
    (valid_repo / "metadata.json").write_text('{"repository_name": "Valid Repo"}')
    (valid_repo / "tech-stack.json").write_text("{}")
    (valid_repo / "security.json").write_text("{}")
    
    # Create invalid repo
    invalid_repo = repos_path / "invalid-repo"
    invalid_repo.mkdir()
    (invalid_repo / "single-file.json").write_text("{}")
    
    discovered = service.scan_repositories()
    
    assert len(discovered) == 1
    assert discovered[0].id == "valid-repo"
    assert discovered[0].name == "Valid Repo"
    assert discovered[0].data_files == 4


def test_scan_repositories_skips_hidden_directories(service, mock_config):
    """Test scanning skips hidden directories"""
    repos_path = mock_config.get_path('repos')
    
    # Create hidden directory
    hidden_repo = repos_path / ".hidden-repo"
    hidden_repo.mkdir()
    (hidden_repo / "health-data.json").write_text("{}")
    (hidden_repo / "metadata.json").write_text("{}")
    (hidden_repo / "tech-stack.json").write_text("{}")
    (hidden_repo / "security.json").write_text("{}")
    
    discovered = service.scan_repositories()
    
    assert len(discovered) == 0


def test_extract_metadata(service, tmp_path):
    """Test metadata extraction"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    
    # Create files
    (repo_path / "health-data.json").write_text('{"summary": {"total_files": 100}}')
    (repo_path / "metadata.json").write_text('{"repository_name": "Test Repo", "collection_date": "2025-12-06T10:00:00"}')
    (repo_path / "tech-stack.json").write_text("{}")
    
    # Mock repos_path
    service.repos_path = tmp_path
    
    metadata = service._extract_metadata(repo_path)
    
    assert metadata.id == "test-repo"
    assert metadata.name == "Test Repo"
    assert metadata.data_files == 3
    assert "health-data.json" in metadata.data_file_list
    assert metadata.total_size > 0


def test_register_repositories_creates_registry(service, mock_config):
    """Test repository registration"""
    repos = [
        RepoMetadata(
            id="repo1",
            name="Repo 1",
            path="data/repos/repo1",
            discovered="2025-12-06T10:00:00",
            last_updated="2025-12-06T09:00:00",
            status="active",
            data_files=5,
            data_file_list=["health-data.json", "metadata.json"],
            file_sizes={"health-data.json": 1024, "metadata.json": 512},
            total_size=1536
        )
    ]
    
    service.register_repositories(repos)
    
    registry_path = mock_config.get_path('repository_registry')
    assert registry_path.exists()
    
    with open(registry_path) as f:
        registry = json.load(f)
    
    assert registry['total_repositories'] == 1
    assert registry['repositories'][0]['id'] == "repo1"
    assert registry['repositories'][0]['name'] == "Repo 1"


def test_remove_missing_repositories(service, mock_config):
    """Test removal of missing repositories"""
    repos_path = mock_config.get_path('repos')
    registry_path = mock_config.get_path('repository_registry')
    
    # Create existing repo
    existing_repo = repos_path / "existing"
    existing_repo.mkdir()
    (existing_repo / "health-data.json").write_text("{}")
    (existing_repo / "metadata.json").write_text("{}")
    (existing_repo / "tech-stack.json").write_text("{}")
    (existing_repo / "security.json").write_text("{}")
    
    # Create registry with existing + missing repo
    registry = {
        "repositories": [
            {"id": "existing", "name": "Existing", "data_files": 4},
            {"id": "missing", "name": "Missing", "data_files": 3}
        ],
        "total_repositories": 2,
        "last_scan": "2025-12-06T10:00:00"
    }
    
    with open(registry_path, 'w') as f:
        json.dump(registry, f)
    
    removed = service.remove_missing_repositories()
    
    assert len(removed) == 1
    assert "missing" in removed
    
    # Verify registry updated
    with open(registry_path) as f:
        updated = json.load(f)
    
    assert updated['total_repositories'] == 1
    assert updated['repositories'][0]['id'] == "existing"


def test_get_repository_count(service, mock_config):
    """Test getting repository count"""
    registry_path = mock_config.get_path('repository_registry')
    
    # Create registry
    registry = {
        "repositories": [
            {"id": "repo1", "name": "Repo 1"},
            {"id": "repo2", "name": "Repo 2"}
        ],
        "total_repositories": 2
    }
    
    with open(registry_path, 'w') as f:
        json.dump(registry, f)
    
    count = service.get_repository_count()
    assert count == 2


def test_get_repository_by_id(service, mock_config):
    """Test getting specific repository"""
    registry_path = mock_config.get_path('repository_registry')
    
    # Create registry
    registry = {
        "repositories": [
            {"id": "repo1", "name": "Repo 1"},
            {"id": "repo2", "name": "Repo 2"}
        ],
        "total_repositories": 2
    }
    
    with open(registry_path, 'w') as f:
        json.dump(registry, f)
    
    repo = service.get_repository_by_id("repo2")
    assert repo is not None
    assert repo['id'] == "repo2"
    assert repo['name'] == "Repo 2"
    
    # Test non-existent
    missing = service.get_repository_by_id("repo3")
    assert missing is None


def test_discover_and_register_repositories_convenience(mock_config):
    """Test convenience function"""
    repos_path = mock_config.get_path('repos')
    
    # Create valid repo
    valid_repo = repos_path / "test-repo"
    valid_repo.mkdir()
    (valid_repo / "health-data.json").write_text("{}")
    (valid_repo / "metadata.json").write_text('{"repository_name": "Test Repo"}')
    (valid_repo / "tech-stack.json").write_text("{}")
    (valid_repo / "security.json").write_text("{}")
    
    with patch('src.operations.modules.dashboard.repository_discovery_service.get_config', return_value=mock_config):
        repos = discover_and_register_repositories()
    
    assert len(repos) == 1
    assert repos[0].id == "test-repo"
    
    # Verify registry created
    registry_path = mock_config.get_path('repository_registry')
    assert registry_path.exists()
