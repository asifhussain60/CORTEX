"""
Domain Entity Tests - RED Phase

Tests for DashboardData, Application, TabContent entities.
Following TDD: Write failing tests FIRST, then implement.

Author: Asif Hussain
"""
import pytest
from datetime import datetime
from typing import Dict, Any


def test_dashboard_data_creation():
    """Test DashboardData entity creation with valid data"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    app_id = "cortex"
    tabs = {
        "overview": {"files": 100, "health": 95.5},
        "architecture": {"nodes": 50, "edges": 120}
    }
    metadata = {
        "app_name": "CORTEX",
        "version": "3.3.0",
        "last_scan": "2025-12-04T10:00:00"
    }
    
    # Act
    data = DashboardData(app_id=app_id, tabs=tabs, metadata=metadata)
    
    # Assert
    assert data.app_id == "cortex"
    assert data.tabs == tabs
    assert data.metadata == metadata


def test_dashboard_data_immutability():
    """Test DashboardData is immutable (frozen dataclass)"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    data = DashboardData(app_id="test", tabs={}, metadata={})
    
    # Act & Assert - should raise AttributeError
    with pytest.raises(AttributeError):
        data.app_id = "modified"


def test_dashboard_data_requires_all_fields():
    """Test DashboardData requires app_id, tabs, metadata"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Act & Assert - missing required fields
    with pytest.raises(TypeError):
        DashboardData(app_id="test")  # Missing tabs, metadata


def test_dashboard_data_to_dict():
    """Test DashboardData can serialize to dictionary"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    data = DashboardData(
        app_id="cortex",
        tabs={"overview": {"files": 100}},
        metadata={"version": "3.3.0"}
    )
    
    # Act
    result = data.to_dict()
    
    # Assert
    assert isinstance(result, dict)
    assert result["app_id"] == "cortex"
    assert result["tabs"]["overview"]["files"] == 100
    assert result["metadata"]["version"] == "3.3.0"


def test_dashboard_data_from_dict():
    """Test DashboardData can deserialize from dictionary"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    data_dict = {
        "app_id": "cortex",
        "tabs": {"overview": {"files": 100}},
        "metadata": {"version": "3.3.0"}
    }
    
    # Act
    data = DashboardData.from_dict(data_dict)
    
    # Assert
    assert data.app_id == "cortex"
    assert data.tabs["overview"]["files"] == 100


def test_application_entity_creation():
    """Test Application entity creation"""
    from src.dashboard.domain.entities.application import Application
    
    # Arrange & Act
    app = Application(
        app_id="cortex",
        app_name="CORTEX",
        app_type="internal",
        data_path="/cortex-brain/dashboards/data/repos/cortex",
        last_scan=datetime(2025, 12, 4, 10, 0, 0)
    )
    
    # Assert
    assert app.app_id == "cortex"
    assert app.app_name == "CORTEX"
    assert app.app_type == "internal"
    assert app.data_path == "/cortex-brain/dashboards/data/repos/cortex"
    assert app.last_scan.year == 2025


def test_application_type_validation():
    """Test Application validates app_type is internal/external/user"""
    from src.dashboard.domain.entities.application import Application
    
    # Act & Assert - invalid app_type
    with pytest.raises(ValueError, match="app_type must be"):
        Application(
            app_id="test",
            app_name="Test",
            app_type="invalid",  # Should be internal/external/user
            data_path="/test",
            last_scan=datetime.now()
        )


def test_application_immutability():
    """Test Application entity is immutable"""
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    app = Application(
        app_id="test",
        app_name="Test",
        app_type="internal",
        data_path="/test",
        last_scan=datetime.now()
    )
    
    # Act & Assert
    with pytest.raises(AttributeError):
        app.app_name = "Modified"


def test_tab_content_creation():
    """Test TabContent entity creation"""
    from src.dashboard.domain.entities.tab_content import TabContent
    
    # Arrange & Act
    tab = TabContent(
        tab_name="overview",
        data={
            "files": 100,
            "health": 95.5,
            "issues": 5
        },
        last_updated=datetime(2025, 12, 4, 10, 0, 0)
    )
    
    # Assert
    assert tab.tab_name == "overview"
    assert tab.data["files"] == 100
    assert tab.data["health"] == 95.5
    assert tab.last_updated.year == 2025


def test_tab_content_validates_tab_name():
    """Test TabContent validates tab_name is one of 7 valid tabs"""
    from src.dashboard.domain.entities.tab_content import TabContent
    
    # Act & Assert - invalid tab name
    with pytest.raises(ValueError, match="tab_name must be one of"):
        TabContent(
            tab_name="invalid_tab",  # Not in valid list
            data={},
            last_updated=datetime.now()
        )


def test_tab_content_accepts_all_valid_tabs():
    """Test TabContent accepts all 7 valid tab names"""
    from src.dashboard.domain.entities.tab_content import TabContent
    
    valid_tabs = ["overview", "techstack", "architecture", "health", "metrics", "security", "reports"]
    
    for tab_name in valid_tabs:
        # Act
        tab = TabContent(
            tab_name=tab_name,
            data={},
            last_updated=datetime.now()
        )
        
        # Assert
        assert tab.tab_name == tab_name


def test_tab_content_immutability():
    """Test TabContent is immutable"""
    from src.dashboard.domain.entities.tab_content import TabContent
    
    # Arrange
    tab = TabContent(
        tab_name="overview",
        data={},
        last_updated=datetime.now()
    )
    
    # Act & Assert
    with pytest.raises(AttributeError):
        tab.tab_name = "modified"
