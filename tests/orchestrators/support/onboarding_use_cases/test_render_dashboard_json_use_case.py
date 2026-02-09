"""
AC-054A-S1-13,14,15: RenderDashboardJSONUseCase Tests

TDD Test Suite (10+ tests):
- AC-054A-S1-13: Use case converts to RepoDashboardModel
- AC-054A-S1-14: Validates schema v3.0
- AC-054A-S1-15: 10+ unit tests with model validation

Author: Phase 54-A Implementation
Created: 2026-02-09
Platform: Windows/macOS compatible
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class DashboardSection:
    """Dashboard section model."""
    title: str
    content: Dict[str, Any]
    order: int


@dataclass
class RepoDashboardModel:
    """Repository dashboard model - schema v3.0."""
    schema_version: str
    repo_name: str
    overview: DashboardSection
    metrics: DashboardSection
    security: DashboardSection
    dependencies: DashboardSection
    team: DashboardSection
    generated_at: str


class TestRenderDashboardJSONUseCase:
    """Test dashboard JSON rendering and model conversion."""

    @pytest.fixture
    def use_case(self):
        """Initialize RenderDashboardJSONUseCase."""
        from cortex.orchestrators.support.onboarding_use_cases import RenderDashboardJSONUseCase
        return RenderDashboardJSONUseCase()

    @pytest.fixture
    def repo_analysis(self) -> dict:
        """Fixture: Complete repository analysis."""
        return {
            "name": "cortex",
            "url": "https://github.com/test/cortex",
            "overview": {
                "description": "Cognitive Real-Time Execution System",
                "stars": 5000,
                "language": "Python",
            },
            "metrics": {
                "test_coverage": 0.92,
                "code_quality": 0.88,
                "documentation": 0.85,
            },
            "security": {
                "vulnerabilities_p0": 0,
                "vulnerabilities_p1": 2,
                "vulnerabilities_p2": 5,
            },
            "dependencies": {
                "total": 42,
                "outdated": 3,
                "vulnerable": 1,
            },
            "team": {
                "contributors": 120,
                "maintainers": 5,
                "last_commit": "2026-02-09",
            },
        }

    def test_creates_dashboard_model(self, use_case, repo_analysis):
        """AC-054A-S1-13a: Creates RepoDashboardModel."""
        dashboard = use_case.execute(repo_analysis)
        
        assert isinstance(dashboard, RepoDashboardModel)

    def test_includes_all_sections(self, use_case, repo_analysis):
        """AC-054A-S1-13b: Includes all dashboard sections."""
        dashboard = use_case.execute(repo_analysis)
        
        assert hasattr(dashboard, 'overview')
        assert hasattr(dashboard, 'metrics')
        assert hasattr(dashboard, 'security')
        assert hasattr(dashboard, 'dependencies')
        assert hasattr(dashboard, 'team')

    def test_populates_overview_section(self, use_case, repo_analysis):
        """AC-054A-S1-13c: Populates overview section."""
        dashboard = use_case.execute(repo_analysis)
        
        assert dashboard.overview.title == "Overview"
        assert "description" in dashboard.overview.content
        assert dashboard.overview.order == 1

    def test_validates_schema_v3_0(self, use_case, repo_analysis):
        """AC-054A-S1-14a: Validates schema v3.0."""
        dashboard = use_case.execute(repo_analysis)
        
        assert dashboard.schema_version == "3.0"

    def test_validates_required_fields(self, use_case, repo_analysis):
        """AC-054A-S1-14b: Validates required fields present."""
        dashboard = use_case.execute(repo_analysis)
        
        assert dashboard.repo_name is not None
        assert len(dashboard.repo_name) > 0
        assert dashboard.generated_at is not None

    def test_rejects_invalid_schema(self, use_case):
        """AC-054A-S1-14c: Rejects invalid schema."""
        invalid = {"name": "test"}  # Missing required sections
        
        with pytest.raises((ValueError, TypeError)):
            use_case.execute(invalid)

    def test_sections_have_correct_order(self, use_case, repo_analysis):
        """AC-054A-S1-15a: Sections have correct order."""
        dashboard = use_case.execute(repo_analysis)
        
        sections = [
            dashboard.overview,
            dashboard.metrics,
            dashboard.security,
            dashboard.dependencies,
            dashboard.team,
        ]
        
        for i, section in enumerate(sections, 1):
            assert section.order == i

    def test_metrics_section_calculated(self, use_case, repo_analysis):
        """AC-054A-S1-15b: Metrics section calculated correctly."""
        dashboard = use_case.execute(repo_analysis)
        
        assert "test_coverage" in dashboard.metrics.content
        assert "code_quality" in dashboard.metrics.content

    def test_security_section_includes_risks(self, use_case, repo_analysis):
        """AC-054A-S1-15c: Security section includes vulnerability data."""
        dashboard = use_case.execute(repo_analysis)
        
        security_content = dashboard.security.content
        assert any("vulnerability" in str(k).lower() for k in security_content.keys())

    def test_generated_at_timestamp(self, use_case, repo_analysis):
        """AC-054A-S1-15d: Generated timestamp is ISO format."""
        dashboard = use_case.execute(repo_analysis)
        
        # Should be ISO format datetime string
        assert "T" in dashboard.generated_at or "-" in dashboard.generated_at
