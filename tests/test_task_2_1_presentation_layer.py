"""
Tests for Task 2.1 - Presentation Layer Templates

This test suite validates the presentation layer implementation:
- DashboardRenderer initialization
- Template rendering without errors
- Data transformation for templates
- Jinja2 filter registration
- HTML output generation

Author: Asif Hussain
Copyright: © 2024-2025
"""

import pytest
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock, MagicMock, patch

from src.dashboard.presentation.dashboard_renderer import DashboardRenderer
from src.dashboard.domain.component import Component
from src.dashboard.domain.dependency import Dependency
from src.dashboard.domain.issue import Issue
from src.dashboard.domain.recommendation import Recommendation


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory with test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        
        # Create test data files
        components_data = {
            "components": [
                {
                    "id": "comp1",
                    "name": "TestComponent",
                    "file_path": "test/component.py",
                    "health_score": 85.0,
                    "loc": 100,
                    "complexity": 5
                }
            ]
        }
        (data_dir / "components.json").write_text(json.dumps(components_data))
        
        dependencies_data = {
            "dependencies": []
        }
        (data_dir / "dependencies.json").write_text(json.dumps(dependencies_data))
        
        issues_data = {
            "issues": []
        }
        (data_dir / "issues.json").write_text(json.dumps(issues_data))
        
        recommendations_data = {
            "recommendations": []
        }
        (data_dir / "recommendations.json").write_text(json.dumps(recommendations_data))
        
        yield data_dir


class TestDashboardRenderer:
    """Test DashboardRenderer class."""
    
    def test_renderer_initialization(self, temp_project_dir, temp_data_dir):
        """Test renderer initializes with correct configuration."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        
        assert renderer.project_path == temp_project_dir
        assert renderer.data_dir == temp_data_dir
        assert renderer.jinja_env is not None
        assert renderer.component_repo is not None
        assert renderer.dependency_repo is not None
        assert renderer.issue_repo is not None
        assert renderer.recommendation_repo is not None
    
    def test_jinja2_filters_registered(self, temp_project_dir, temp_data_dir):
        """Test custom Jinja2 filters are registered."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        
        assert 'format_number' in renderer.jinja_env.filters
        assert 'round' in renderer.jinja_env.filters
    
    def test_format_number_filter(self, temp_project_dir, temp_data_dir):
        """Test format_number filter works correctly."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        format_number = renderer.jinja_env.filters['format_number']
        
        assert format_number(1000) == "1,000"
        assert format_number(1000000) == "1,000,000"
        assert format_number(42) == "42"
    
    def test_round_filter(self, temp_project_dir, temp_data_dir):
        """Test round filter works correctly."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        round_filter = renderer.jinja_env.filters['round']
        
        assert round_filter(3.14159, 2) == 3.14
        assert round_filter(10.5, 0) == 10.0
        assert round_filter(2.718281828, 4) == 2.7183
    
    def test_get_health_category(self, temp_project_dir, temp_data_dir):
        """Test health category mapping."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        
        assert renderer._get_health_category(85.0) == "excellent"
        assert renderer._get_health_category(70.0) == "good"
        assert renderer._get_health_category(50.0) == "fair"
        assert renderer._get_health_category(30.0) == "poor"
        assert renderer._get_health_category(10.0) == "critical"
    
    def test_get_health_label(self, temp_project_dir, temp_data_dir):
        """Test health label generation."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        
        assert renderer._get_health_label(85.0) == "Excellent Health"
        assert renderer._get_health_label(70.0) == "Good Health"
        assert renderer._get_health_label(50.0) == "Fair Health"
        assert renderer._get_health_label(30.0) == "Poor Health"
        assert renderer._get_health_label(10.0) == "Critical Issues"
    
    @patch('src.dashboard.presentation.dashboard_renderer.LoadOverviewUseCase')
    @patch('src.dashboard.presentation.dashboard_renderer.RenderArchitectureGraphUseCase')
    @patch('src.dashboard.presentation.dashboard_renderer.AnalyzeQualityMetricsUseCase')
    @patch('src.dashboard.presentation.dashboard_renderer.ScanSecurityVulnerabilitiesUseCase')
    @patch('src.dashboard.presentation.dashboard_renderer.GenerateRecommendationsUseCase')
    def test_gather_dashboard_data(
        self,
        mock_rec_usecase,
        mock_sec_usecase,
        mock_qual_usecase,
        mock_arch_usecase,
        mock_overview_usecase,
        temp_project_dir,
        temp_data_dir
    ):
        """Test dashboard data gathering from use cases."""
        # Setup mocks
        mock_overview_usecase.return_value.execute.return_value = {
            "health_score": 75.0,
            "file_count": 100
        }
        mock_arch_usecase.return_value.execute.return_value = {
            "nodes": [],
            "edges": []
        }
        mock_qual_usecase.return_value.execute.return_value = {
            "overall_score": 80.0
        }
        mock_sec_usecase.return_value.execute.return_value = {
            "overall_score": 70.0
        }
        mock_rec_usecase.return_value.execute.return_value = {
            "top_recommendations": []
        }
        
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        data = renderer._gather_dashboard_data()
        
        assert "overview" in data
        assert "architecture" in data
        assert "quality" in data
        assert "security" in data
        assert "recommendations" in data
        assert data["overview"]["health_score"] == 75.0
    
    def test_render_creates_html_file(self, temp_project_dir, temp_data_dir):
        """Test render() creates HTML file."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        
        # Mock use case execution to return minimal data
        with patch.object(renderer, '_gather_dashboard_data') as mock_gather:
            mock_gather.return_value = {
                "overview": {
                    "health_score": 75.0,
                    "health_description": "Test description",
                    "file_count": 100,
                    "loc_count": 5000,
                    "component_count": 10,
                    "dependency_count": 20,
                    "issue_count": 5,
                    "vulnerability_count": 2,
                    "languages": [],
                    "quick_insights": [],
                    "recent_activities": []
                },
                "architecture": {
                    "nodes": [],
                    "edges": [],
                    "avg_complexity": 5.0,
                    "max_nesting": 3,
                    "coupling_score": 60,
                    "cohesion_score": 70,
                    "total_dependencies": 20,
                    "circular_dependencies": 0,
                    "external_dependencies": 5,
                    "max_dependency_depth": 4,
                    "detected_patterns": []
                },
                "quality": {
                    "overall_score": 80.0,
                    "maintainability_score": 75.0,
                    "readability_score": 85.0,
                    "test_coverage": 70.0,
                    "documentation_score": 60.0,
                    "code_smells": [],
                    "max_complexity": 10,
                    "high_complexity_files": 3,
                    "line_coverage": 70.0,
                    "branch_coverage": 65.0,
                    "function_coverage": 75.0,
                    "uncovered_files": 10,
                    "partially_covered_files": 15,
                    "fully_covered_files": 25,
                    "duplication_percentage": 5.0,
                    "duplicate_blocks": 10,
                    "duplicate_lines": 200,
                    "top_duplications": []
                },
                "security": {
                    "overall_score": 70.0,
                    "critical_count": 0,
                    "high_count": 1,
                    "medium_count": 3,
                    "low_count": 5,
                    "total_count": 9,
                    "owasp_top_10": [],
                    "vulnerabilities": [],
                    "security_practices": [],
                    "dependency_vulnerabilities": [],
                    "compliance_standards": []
                },
                "recommendations": {
                    "top_recommendations": [],
                    "critical_high_roi_count": 0,
                    "important_medium_roi_count": 2,
                    "optional_low_roi_count": 5,
                    "deferred_count": 3,
                    "categories": [],
                    "quick_wins": [],
                    "total_debt_hours": 40,
                    "debt_ratio": 15.0,
                    "estimated_payoff_weeks": 2,
                    "refactoring_phases": []
                }
            }
            
            output_path = temp_project_dir / "dashboard.html"
            result = renderer.render(output_path)
            
            assert result == output_path
            assert output_path.exists()
            assert output_path.stat().st_size > 0
    
    def test_render_html_contains_expected_sections(self, temp_project_dir, temp_data_dir):
        """Test rendered HTML contains expected sections."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        
        with patch.object(renderer, '_gather_dashboard_data') as mock_gather:
            mock_gather.return_value = {
                "overview": {
                    "health_score": 75.0,
                    "health_description": "Good health",
                    "file_count": 100,
                    "loc_count": 5000,
                    "component_count": 10,
                    "dependency_count": 20,
                    "issue_count": 5,
                    "vulnerability_count": 2,
                    "languages": [],
                    "quick_insights": [],
                    "recent_activities": []
                },
                "architecture": {
                    "nodes": [],
                    "edges": [],
                    "avg_complexity": 5.0,
                    "max_nesting": 3,
                    "coupling_score": 60,
                    "cohesion_score": 70,
                    "total_dependencies": 20,
                    "circular_dependencies": 0,
                    "external_dependencies": 5,
                    "max_dependency_depth": 4,
                    "detected_patterns": []
                },
                "quality": {
                    "overall_score": 80.0,
                    "maintainability_score": 75.0,
                    "readability_score": 85.0,
                    "test_coverage": 70.0,
                    "documentation_score": 60.0,
                    "code_smells": [],
                    "max_complexity": 10,
                    "high_complexity_files": 3,
                    "line_coverage": 70.0,
                    "branch_coverage": 65.0,
                    "function_coverage": 75.0,
                    "uncovered_files": 10,
                    "partially_covered_files": 15,
                    "fully_covered_files": 25,
                    "duplication_percentage": 5.0,
                    "duplicate_blocks": 10,
                    "duplicate_lines": 200,
                    "top_duplications": []
                },
                "security": {
                    "overall_score": 70.0,
                    "critical_count": 0,
                    "high_count": 1,
                    "medium_count": 3,
                    "low_count": 5,
                    "total_count": 9,
                    "owasp_top_10": [],
                    "vulnerabilities": [],
                    "security_practices": [],
                    "dependency_vulnerabilities": [],
                    "compliance_standards": []
                },
                "recommendations": {
                    "top_recommendations": [],
                    "critical_high_roi_count": 0,
                    "important_medium_roi_count": 2,
                    "optional_low_roi_count": 5,
                    "deferred_count": 3,
                    "categories": [],
                    "quick_wins": [],
                    "total_debt_hours": 40,
                    "debt_ratio": 15.0,
                    "estimated_payoff_weeks": 2,
                    "refactoring_phases": []
                }
            }
            
            output_path = temp_project_dir / "dashboard.html"
            renderer.render(output_path)
            
            html_content = output_path.read_text()
            
            # Check for essential HTML structure
            assert "<!DOCTYPE html>" in html_content
            assert "<html" in html_content
            assert "CORTEX" in html_content
            
            # Check for tab navigation
            assert "overview" in html_content.lower()
            assert "architecture" in html_content.lower()
            assert "quality" in html_content.lower()
            assert "security" in html_content.lower()
            assert "recommendations" in html_content.lower()
            
            # Check for health score display
            assert "75" in html_content  # health score
    
    def test_render_with_websocket_enabled(self, temp_project_dir, temp_data_dir):
        """Test rendering with WebSocket support enabled."""
        renderer = DashboardRenderer(temp_project_dir, temp_data_dir)
        
        with patch.object(renderer, '_gather_dashboard_data') as mock_gather:
            mock_gather.return_value = self._get_minimal_dashboard_data()
            
            output_path = temp_project_dir / "dashboard_ws.html"
            renderer.render(
                output_path,
                enable_websocket=True,
                websocket_url="ws://localhost:8000"
            )
            
            html_content = output_path.read_text()
            assert "socket.io" in html_content
            assert "ws://localhost:8000" in html_content or "localhost:8000" in html_content
    
    def _get_minimal_dashboard_data(self):
        """Helper method to get minimal dashboard data for testing."""
        return {
            "overview": {
                "health_score": 75.0,
                "health_description": "Test",
                "file_count": 100,
                "loc_count": 5000,
                "component_count": 10,
                "dependency_count": 20,
                "issue_count": 5,
                "vulnerability_count": 2,
                "languages": [],
                "quick_insights": [],
                "recent_activities": []
            },
            "architecture": {
                "nodes": [],
                "edges": [],
                "avg_complexity": 5.0,
                "max_nesting": 3,
                "coupling_score": 60,
                "cohesion_score": 70,
                "total_dependencies": 20,
                "circular_dependencies": 0,
                "external_dependencies": 5,
                "max_dependency_depth": 4,
                "detected_patterns": []
            },
            "quality": {
                "overall_score": 80.0,
                "maintainability_score": 75.0,
                "readability_score": 85.0,
                "test_coverage": 70.0,
                "documentation_score": 60.0,
                "code_smells": [],
                "max_complexity": 10,
                "high_complexity_files": 3,
                "line_coverage": 70.0,
                "branch_coverage": 65.0,
                "function_coverage": 75.0,
                "uncovered_files": 10,
                "partially_covered_files": 15,
                "fully_covered_files": 25,
                "duplication_percentage": 5.0,
                "duplicate_blocks": 10,
                "duplicate_lines": 200,
                "top_duplications": []
            },
            "security": {
                "overall_score": 70.0,
                "critical_count": 0,
                "high_count": 1,
                "medium_count": 3,
                "low_count": 5,
                "total_count": 9,
                "owasp_top_10": [],
                "vulnerabilities": [],
                "security_practices": [],
                "dependency_vulnerabilities": [],
                "compliance_standards": []
            },
            "recommendations": {
                "top_recommendations": [],
                "critical_high_roi_count": 0,
                "important_medium_roi_count": 2,
                "optional_low_roi_count": 5,
                "deferred_count": 3,
                "categories": [],
                "quick_wins": [],
                "total_debt_hours": 40,
                "debt_ratio": 15.0,
                "estimated_payoff_weeks": 2,
                "refactoring_phases": []
            }
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
