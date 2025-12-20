"""
Infrastructure Layer - JsonDashboardRepository Tests (RED Phase)

Tests for JSON file-based dashboard persistence.
Uses tmp_path fixtures for isolated file testing.

Author: Asif Hussain
"""
import pytest
import json
from pathlib import Path


def test_json_repository_save_dashboard(tmp_path):
    """Test saving dashboard to JSON file"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    repo = JsonDashboardRepository(base_path=tmp_path)
    data = DashboardData(
        app_id="cortex",
        tabs={"overview": {"files": 100, "lines": 5000}},
        metadata={"app_name": "CORTEX", "version": "3.3.0"}
    )
    
    # Act
    repo.save(data)
    
    # Assert - File should exist
    expected_file = tmp_path / "cortex.json"
    assert expected_file.exists()
    
    # Assert - Content should be valid JSON
    with open(expected_file, 'r') as f:
        saved_data = json.load(f)
    
    assert saved_data["app_id"] == "cortex"
    assert saved_data["tabs"]["overview"]["files"] == 100
    assert saved_data["metadata"]["app_name"] == "CORTEX"


def test_json_repository_get_by_id_existing(tmp_path):
    """Test loading existing dashboard from JSON file"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange - Create test JSON file
    test_data = {
        "app_id": "cortex",
        "tabs": {"overview": {"files": 100}},
        "metadata": {"app_name": "CORTEX"}
    }
    test_file = tmp_path / "cortex.json"
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    
    # Act
    repo = JsonDashboardRepository(base_path=tmp_path)
    result = repo.get_by_id("cortex")
    
    # Assert
    assert isinstance(result, DashboardData)
    assert result.app_id == "cortex"
    assert result.tabs["overview"]["files"] == 100
    assert result.metadata["app_name"] == "CORTEX"


def test_json_repository_get_by_id_not_found(tmp_path):
    """Test loading non-existent dashboard raises FileNotFoundError"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    # Arrange
    repo = JsonDashboardRepository(base_path=tmp_path)
    
    # Act & Assert
    with pytest.raises(FileNotFoundError, match="Dashboard not found"):
        repo.get_by_id("nonexistent")


def test_json_repository_exists_true(tmp_path):
    """Test exists() returns True for existing dashboard"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    # Arrange - Create test file
    test_file = tmp_path / "cortex.json"
    test_file.write_text('{"app_id": "cortex", "tabs": {}, "metadata": {}}')
    
    # Act
    repo = JsonDashboardRepository(base_path=tmp_path)
    result = repo.exists("cortex")
    
    # Assert
    assert result is True


def test_json_repository_exists_false(tmp_path):
    """Test exists() returns False for non-existent dashboard"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    # Arrange
    repo = JsonDashboardRepository(base_path=tmp_path)
    
    # Act
    result = repo.exists("nonexistent")
    
    # Assert
    assert result is False


def test_json_repository_overwrites_existing_file(tmp_path):
    """Test saving dashboard overwrites existing file"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange - Create initial file
    test_file = tmp_path / "cortex.json"
    test_file.write_text('{"app_id": "cortex", "tabs": {"old": "data"}, "metadata": {}}')
    
    # Act - Save new data
    repo = JsonDashboardRepository(base_path=tmp_path)
    new_data = DashboardData(
        app_id="cortex",
        tabs={"new": "data"},
        metadata={"updated": True}
    )
    repo.save(new_data)
    
    # Assert - File should contain new data only
    with open(test_file, 'r') as f:
        saved_data = json.load(f)
    
    assert saved_data["tabs"] == {"new": "data"}
    assert saved_data["metadata"] == {"updated": True}
    assert "old" not in saved_data["tabs"]


def test_json_repository_handles_invalid_json(tmp_path):
    """Test repository handles corrupted JSON file gracefully"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    # Arrange - Create invalid JSON file
    test_file = tmp_path / "corrupted.json"
    test_file.write_text('{"invalid json without closing brace')
    
    # Act & Assert
    repo = JsonDashboardRepository(base_path=tmp_path)
    with pytest.raises(ValueError, match="Invalid JSON"):
        repo.get_by_id("corrupted")


def test_json_repository_creates_base_directory_if_missing(tmp_path):
    """Test repository creates base directory if it doesn't exist"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange - Use non-existent subdirectory
    nested_path = tmp_path / "dashboards" / "data"
    assert not nested_path.exists()
    
    # Act
    repo = JsonDashboardRepository(base_path=nested_path)
    data = DashboardData(
        app_id="test",
        tabs={},
        metadata={}
    )
    repo.save(data)
    
    # Assert - Directory and file should be created
    assert nested_path.exists()
    assert (nested_path / "test.json").exists()


def test_json_repository_validates_app_id_format(tmp_path):
    """Test repository validates app_id contains only safe characters"""
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    # Arrange
    repo = JsonDashboardRepository(base_path=tmp_path)
    
    # Act & Assert - Test various invalid app_ids
    invalid_ids = ["../etc/passwd", "app/id", "app\\id", "app:id", "app*id"]
    
    for invalid_id in invalid_ids:
        with pytest.raises(ValueError, match="Invalid app_id"):
            repo.get_by_id(invalid_id)
