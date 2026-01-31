"""
Tests for DashboardConfiguration.

Tests context-aware dashboard tab configuration based on repository type.

Authority: CORE-008 (TDD - Tests first)
AC-ID: LENS-DASH-001
"""

import pytest
from pathlib import Path
from cortex.visualization.dashboard_configuration import (
    DashboardConfiguration,
    DashboardTab,
    get_universal_tabs,
    get_cortex_tabs,
)


class TestDashboardTab:
    """Test suite for DashboardTab dataclass."""
    
    def test_create_universal_tab(self) -> None:
        """Test creating a universal dashboard tab."""
        # Act
        tab = DashboardTab(
            id="repository_overview",
            name="Repository Overview",
            template="repository_overview.html",
            is_universal=True,
            requires_cortex=False,
        )
        
        # Assert
        assert tab.id == "repository_overview"
        assert tab.name == "Repository Overview"
        assert tab.is_universal is True
        assert tab.requires_cortex is False
    
    def test_create_cortex_specific_tab(self) -> None:
        """Test creating a CORTEX-specific tab."""
        # Act
        tab = DashboardTab(
            id="brain_architecture",
            name="Brain Architecture",
            template="brain_architecture.html",
            is_universal=False,
            requires_cortex=True,
        )
        
        # Assert
        assert tab.requires_cortex is True
        assert tab.is_universal is False


class TestDashboardConfiguration:
    """Test suite for DashboardConfiguration class."""
    
    def test_get_tabs_for_external_repository(self, tmp_path: Path) -> None:
        """Test getting tabs for external repository (5 universal tabs)."""
        # Arrange: Create external repo structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        config = DashboardConfiguration()
        
        # Act
        tabs = config.get_tabs_for_repo(tmp_path)
        
        # Assert
        assert len(tabs) == 5
        assert all(tab.is_universal for tab in tabs)
        assert all(not tab.requires_cortex for tab in tabs)
    
    def test_get_tabs_for_cortex_repository(self, tmp_path: Path) -> None:
        """Test getting tabs for CORTEX repository (8 tabs total)."""
        # Arrange: Create CORTEX marker
        (tmp_path / "cortex_brain").mkdir()
        config = DashboardConfiguration()
        
        # Act
        tabs = config.get_tabs_for_repo(tmp_path)
        
        # Assert
        assert len(tabs) == 8
        universal_tabs = [tab for tab in tabs if tab.is_universal]
        cortex_tabs = [tab for tab in tabs if tab.requires_cortex]
        assert len(universal_tabs) == 5
        assert len(cortex_tabs) == 3
    
    def test_universal_tabs_come_first(self, tmp_path: Path) -> None:
        """Test that universal tabs (1-5) come before CORTEX tabs (6-8)."""
        # Arrange
        (tmp_path / "cortex_brain").mkdir()
        config = DashboardConfiguration()
        
        # Act
        tabs = config.get_tabs_for_repo(tmp_path)
        
        # Assert: First 5 should be universal
        for i in range(5):
            assert tabs[i].is_universal is True
        # Last 3 should be CORTEX-specific
        for i in range(5, 8):
            assert tabs[i].requires_cortex is True
    
    def test_get_universal_tabs(self) -> None:
        """Test getting universal tabs only."""
        # Act
        tabs = get_universal_tabs()
        
        # Assert
        assert len(tabs) == 5
        assert all(tab.is_universal for tab in tabs)
        
        # Check tab IDs
        tab_ids = [tab.id for tab in tabs]
        assert "repository_overview" in tab_ids
        assert "dependency_graph" in tab_ids
        assert "class_diagrams" in tab_ids
        assert "temporal_analysis" in tab_ids
        assert "impact_analysis" in tab_ids
    
    def test_get_cortex_tabs(self) -> None:
        """Test getting CORTEX-specific tabs."""
        # Act
        tabs = get_cortex_tabs()
        
        # Assert
        assert len(tabs) == 3
        assert all(tab.requires_cortex for tab in tabs)
        
        # Check tab IDs
        tab_ids = [tab.id for tab in tabs]
        assert "brain_architecture" in tab_ids
        assert "governance_compliance" in tab_ids
        assert "orchestrator_constellation" in tab_ids
    
    def test_is_tab_applicable_universal_to_external(self) -> None:
        """Test universal tab is applicable to external repo."""
        # Arrange
        config = DashboardConfiguration()
        
        # Act
        result = config.is_tab_applicable("repository_overview", Path("/external"))
        
        # Assert
        assert result is True
    
    def test_is_tab_applicable_cortex_to_external(self, tmp_path: Path) -> None:
        """Test CORTEX tab is NOT applicable to external repo."""
        # Arrange
        config = DashboardConfiguration()
        
        # Act
        result = config.is_tab_applicable("brain_architecture", tmp_path)
        
        # Assert
        assert result is False
    
    def test_is_tab_applicable_cortex_to_cortex(self, tmp_path: Path) -> None:
        """Test CORTEX tab IS applicable to CORTEX repo."""
        # Arrange
        (tmp_path / "cortex_brain").mkdir()
        config = DashboardConfiguration()
        
        # Act
        result = config.is_tab_applicable("brain_architecture", tmp_path)
        
        # Assert
        assert result is True
    
    def test_tab_ordering_consistency(self, tmp_path: Path) -> None:
        """Test tab ordering is consistent across calls."""
        # Arrange
        (tmp_path / "cortex_brain").mkdir()
        config = DashboardConfiguration()
        
        # Act
        tabs1 = config.get_tabs_for_repo(tmp_path)
        tabs2 = config.get_tabs_for_repo(tmp_path)
        
        # Assert
        tab_ids1 = [tab.id for tab in tabs1]
        tab_ids2 = [tab.id for tab in tabs2]
        assert tab_ids1 == tab_ids2
    
    def test_tab_names_are_descriptive(self) -> None:
        """Test all tabs have descriptive names."""
        # Act
        universal = get_universal_tabs()
        cortex = get_cortex_tabs()
        all_tabs = universal + cortex
        
        # Assert
        for tab in all_tabs:
            assert len(tab.name) > 5  # Descriptive names
            assert tab.name[0].isupper()  # Proper capitalization
    
    def test_tab_templates_have_html_extension(self) -> None:
        """Test all tab templates have .html extension."""
        # Act
        universal = get_universal_tabs()
        cortex = get_cortex_tabs()
        all_tabs = universal + cortex
        
        # Assert
        for tab in all_tabs:
            assert tab.template.endswith(".html")
