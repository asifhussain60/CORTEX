"""
Dashboard Configuration for Adaptive Tab Rendering.

Provides context-aware dashboard tab configuration based on repository type:
- External repositories: 5 universal tabs
- CORTEX repository: 8 tabs (5 universal + 3 CORTEX-specific)

Universal tabs are applicable to ALL repositories.
CORTEX-specific tabs are only shown for CORTEX repository.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-001
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

from cortex.visualization.repository_detector import is_cortex_repository


@dataclass
class DashboardTab:
    """
    Represents a single dashboard tab configuration.

    Attributes:
        id: Unique identifier for the tab (lowercase_with_underscores)
        name: Display name for the tab
        template: Jinja2 template filename
        is_universal: Whether tab is applicable to all repositories
        requires_cortex: Whether tab requires CORTEX repository
    """
    id: str
    name: str
    template: str
    is_universal: bool
    requires_cortex: bool


class DashboardConfiguration:
    """
    Manages context-aware dashboard tab configuration.

    Determines which tabs to display based on repository type:
    - External repository → 5 universal tabs
    - CORTEX repository → 8 tabs (5 universal + 3 CORTEX-specific)

    Example:
        ```python
        config = DashboardConfiguration()

        # Get tabs for external repository
        tabs = config.get_tabs_for_repo(Path("/path/to/flask-app"))
        # Returns: 5 tabs

        # Get tabs for CORTEX repository
        tabs = config.get_tabs_for_repo(Path("/path/to/CORTEX"))
        # Returns: 8 tabs

        # Check if specific tab is applicable
        is_applicable = config.is_tab_applicable("brain_architecture", repo_path)
        ```
    """

    def get_tabs_for_repo(self, repo_path: Path) -> List[DashboardTab]:
        """
        Get applicable dashboard tabs based on repository type.

        Args:
            repo_path: Path to repository root

        Returns:
            List of DashboardTab objects (5 for external, 8 for CORTEX)
        """
        tabs = get_universal_tabs()

        if is_cortex_repository(repo_path):
            tabs.extend(get_cortex_tabs())

        return tabs

    def is_tab_applicable(self, tab_id: str, repo_path: Path) -> bool:
        """
        Check if a specific tab is applicable to the repository.

        Args:
            tab_id: Tab identifier (e.g., "brain_architecture")
            repo_path: Path to repository root

        Returns:
            True if tab should be shown, False otherwise
        """
        # Get all applicable tabs for this repo
        applicable_tabs = self.get_tabs_for_repo(repo_path)

        # Check if tab_id is in the list
        return any(tab.id == tab_id for tab in applicable_tabs)


def get_universal_tabs() -> List[DashboardTab]:
    """
    Get universal dashboard tabs (applicable to ALL repositories).

    Returns 5 tabs:
    1. Repository Overview - Business language description
    2. Dependency Graph - Call graph + import graph
    3. Class Diagrams - UML, ERD, interfaces
    4. Temporal Analysis - Git timeline, change heatmap
    5. Impact Analysis - Change propagation

    Returns:
        List of 5 universal DashboardTab objects
    """
    return [
        DashboardTab(
            id="repository_overview",
            name="Repository Overview",
            template="repository_overview.html",
            is_universal=True,
            requires_cortex=False,
        ),
        DashboardTab(
            id="dependency_graph",
            name="Dependency Graph",
            template="dependency_graph.html",
            is_universal=True,
            requires_cortex=False,
        ),
        DashboardTab(
            id="class_diagrams",
            name="Class Diagrams",
            template="class_diagrams.html",
            is_universal=True,
            requires_cortex=False,
        ),
        DashboardTab(
            id="temporal_analysis",
            name="Temporal Analysis",
            template="temporal_analysis.html",
            is_universal=True,
            requires_cortex=False,
        ),
        DashboardTab(
            id="impact_analysis",
            name="Impact Analysis",
            template="impact_analysis.html",
            is_universal=True,
            requires_cortex=False,
        ),
    ]


def get_cortex_tabs() -> List[DashboardTab]:
    """
    Get CORTEX-specific dashboard tabs.

    Returns 3 tabs (only shown for CORTEX repository):
    6. Brain Architecture - 4-tier brain system
    7. Governance Compliance - CORE rule heatmap
    8. Orchestrator Constellation - Orchestrator wiring

    Returns:
        List of 3 CORTEX-specific DashboardTab objects
    """
    return [
        DashboardTab(
            id="brain_architecture",
            name="Brain Architecture",
            template="brain_architecture.html",
            is_universal=False,
            requires_cortex=True,
        ),
        DashboardTab(
            id="governance_compliance",
            name="Governance Compliance",
            template="governance_heatmap.html",
            is_universal=False,
            requires_cortex=True,
        ),
        DashboardTab(
            id="orchestrator_constellation",
            name="Orchestrator Constellation",
            template="orchestrator_constellation.html",
            is_universal=False,
            requires_cortex=True,
        ),
    ]
