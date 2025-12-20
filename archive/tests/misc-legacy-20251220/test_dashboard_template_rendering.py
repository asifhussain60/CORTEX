"""
Test dashboard template rendering with array-based tabs structure.

This test validates the template correctly handles the new data format:
- tabs as array (not dict)
- sections with content_type
- Multiple section renderers (metrics, table, chart, list, message)

RED Phase: These tests MUST fail initially, proving we're testing real functionality.
GREEN Phase: Template fixes will make them pass.

Author: Asif Hussain
"""
import pytest
from pathlib import Path
from flask import Flask
from src.dashboard.domain.entities.dashboard_data import DashboardData


@pytest.fixture
def app():
    """Create Flask app for template rendering tests."""
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parents[3] / 'src' / 'dashboard' / 'presentation' / 'templates'),
        static_folder=str(Path(__file__).parents[3] / 'src' / 'dashboard' / 'presentation' / 'static')
    )
    app.config['TESTING'] = True
    return app


@pytest.fixture
def mock_dashboard_data_array():
    """Mock dashboard data with array-based tabs (NEW format)."""
    return DashboardData(
        app_id="test_app",
        tabs=[
            {
                "id": "overview",
                "name": "Overview",
                "icon": "📊",
                "content_type": "overview",
                "sections": [
                    {
                        "id": "stats",
                        "title": "Project Statistics",
                        "content_type": "metrics",
                        "data": {
                            "total_files": 487,
                            "total_lines": 52340,
                            "health_score": 87.5
                        }
                    },
                    {
                        "id": "issues",
                        "title": "Top Issues",
                        "content_type": "table",
                        "data": {
                            "headers": ["Severity", "Type", "Count"],
                            "rows": [
                                ["High", "Security", 5],
                                ["Medium", "Quality", 12]
                            ]
                        }
                    }
                ]
            },
            {
                "id": "quality",
                "name": "Code Quality",
                "icon": "✨",
                "content_type": "quality",
                "sections": [
                    {
                        "id": "metrics",
                        "title": "Quality Metrics",
                        "content_type": "metrics",
                        "data": {
                            "test_coverage": 67.8,
                            "code_duplication": 12.3
                        }
                    }
                ]
            }
        ],
        metadata={
            "last_updated": "2025-12-04T14:30:00Z",
            "app_id": "test_app",
            "app_name": "Test Application",
            "status": "healthy"
        }
    )


class TestDashboardTemplateArrayStructure:
    """Test template handles array-based tabs structure."""
    
    def test_template_renders_tabs_as_array(self, app, mock_dashboard_data_array):
        """Test template iterates over tabs array, not tabs.keys()."""
        with app.test_request_context():
            from flask import render_template
            
            html = render_template(
                'dashboard_clean.html',
                app_id=mock_dashboard_data_array.app_id,
                app_name=mock_dashboard_data_array.metadata['app_name'],
                tabs=mock_dashboard_data_array.tabs,
                metadata=mock_dashboard_data_array.metadata,
                available_apps=[],
                current_app_id='test_app'
            )
            
            # Should contain tab button with data-tab="overview" (using tab.id)
            assert 'data-tab="overview"' in html, "Tab buttons should use tab.id from array"
            
            # Should NOT contain "tabs.keys()" iteration artifacts
            assert 'dict_keys' not in html.lower(), "Should not leak Python dict_keys"
    
    def test_template_renders_tab_icons(self, app, mock_dashboard_data_array):
        """Test template displays tab icons from array structure."""
        with app.test_request_context():
            from flask import render_template
            
            html = render_template(
                'dashboard_clean.html',
                app_id=mock_dashboard_data_array.app_id,
                app_name=mock_dashboard_data_array.metadata['app_name'],
                tabs=mock_dashboard_data_array.tabs,
                metadata=mock_dashboard_data_array.metadata,
                available_apps=[],
                current_app_id='test_app'
            )
            
            # Should contain emoji icons from tabs array
            assert '📊' in html, "Should render Overview tab icon"
            assert '✨' in html, "Should render Quality tab icon"
    
    def test_template_renders_tab_names(self, app, mock_dashboard_data_array):
        """Test template displays correct tab names from array."""
        with app.test_request_context():
            from flask import render_template
            
            html = render_template(
                'dashboard_clean.html',
                app_id=mock_dashboard_data_array.app_id,
                app_name=mock_dashboard_data_array.metadata['app_name'],
                tabs=mock_dashboard_data_array.tabs,
                metadata=mock_dashboard_data_array.metadata,
                available_apps=[],
                current_app_id='test_app'
            )
            
            # Should show exact tab names (not title-cased dict keys)
            assert 'Overview' in html, "Should show Overview tab name"
            assert 'Code Quality' in html, "Should show Code Quality tab name"


class TestDashboardSectionRendering:
    """Test template renders different section content types."""
    
    def test_section_metrics_rendering(self, app, mock_dashboard_data_array):
        """Test metrics section renders as grid of metric cards."""
        with app.test_request_context():
            from flask import render_template
            
            html = render_template(
                'dashboard_clean.html',
                app_id=mock_dashboard_data_array.app_id,
                app_name=mock_dashboard_data_array.metadata['app_name'],
                tabs=mock_dashboard_data_array.tabs,
                metadata=mock_dashboard_data_array.metadata,
                available_apps=[],
                current_app_id='test_app'
            )
            
            # Should render section title
            assert 'Project Statistics' in html, "Should show section title"
            
            # Should render metrics grid
            assert 'metrics-grid' in html, "Should have metrics-grid class"
            
            # Should render metric values
            assert '487' in html, "Should show total_files metric"
            assert '52340' in html, "Should show total_lines metric"
            assert '87.5' in html, "Should show health_score metric"
    
    def test_section_table_rendering(self, app, mock_dashboard_data_array):
        """Test table section renders as HTML table with headers and rows."""
        with app.test_request_context():
            from flask import render_template
            
            html = render_template(
                'dashboard_clean.html',
                app_id=mock_dashboard_data_array.app_id,
                app_name=mock_dashboard_data_array.metadata['app_name'],
                tabs=mock_dashboard_data_array.tabs,
                metadata=mock_dashboard_data_array.metadata,
                available_apps=[],
                current_app_id='test_app'
            )
            
            # Should render table container
            assert 'table-container' in html, "Should have table-container class"
            assert 'data-table' in html, "Should have data-table class"
            
            # Should render table headers
            assert '<thead>' in html, "Should have table header"
            assert 'Severity' in html, "Should show Severity header"
            assert 'Type' in html, "Should show Type header"
            
            # Should render table rows
            assert '<tbody>' in html, "Should have table body"
            assert 'High' in html, "Should show High severity row"
            assert 'Security' in html, "Should show Security type"
    
    def test_section_chart_placeholder(self, app, mock_dashboard_data_array):
        """Test chart section renders placeholder (Chart.js integration deferred)."""
        with app.test_request_context():
            from flask import render_template
            
            # Add chart section to mock data
            chart_section = {
                "id": "chart_test",
                "title": "Test Chart",
                "content_type": "chart",
                "chart_type": "bar",
                "data": {"labels": ["A", "B"], "values": [10, 20]}
            }
            mock_dashboard_data_array.tabs[0]["sections"].append(chart_section)
            
            html = render_template(
                'dashboard_clean.html',
                app_id=mock_dashboard_data_array.app_id,
                app_name=mock_dashboard_data_array.metadata['app_name'],
                tabs=mock_dashboard_data_array.tabs,
                metadata=mock_dashboard_data_array.metadata,
                available_apps=[],
                current_app_id='test_app'
            )
            
            # Should render chart placeholder
            assert 'chart-container' in html, "Should have chart-container class"
            assert 'chart-placeholder' in html, "Should show chart placeholder"
            assert 'data-chart-type="bar"' in html, "Should specify chart type"
    
    def test_section_content_type_attribute(self, app, mock_dashboard_data_array):
        """Test sections have data-content-type attribute for styling."""
        with app.test_request_context():
            from flask import render_template
            
            html = render_template(
                'dashboard_clean.html',
                app_id=mock_dashboard_data_array.app_id,
                app_name=mock_dashboard_data_array.metadata['app_name'],
                tabs=mock_dashboard_data_array.tabs,
                metadata=mock_dashboard_data_array.metadata,
                available_apps=[],
                current_app_id='test_app'
            )
            
            # Should have content-type data attributes for CSS targeting
            assert 'data-content-type="metrics"' in html, "Should mark metrics sections"
            assert 'data-content-type="table"' in html, "Should mark table sections"


class TestDashboardDataStructureCompatibility:
    """Test dashboard data matches real CORTEX/noor-canvas format."""
    
    def test_mock_data_structure_matches_real_format(self):
        """Test mock dashboard data follows same structure as CORTEX/noor-canvas."""
        # Load real CORTEX data
        import json
        cortex_data_path = Path(__file__).parents[3] / 'cortex-brain' / 'dashboards' / 'cortex' / 'dashboard_data.json'
        
        with open(cortex_data_path) as f:
            cortex_data = json.load(f)
        
        # Load mock data
        mock_data_path = Path(__file__).parents[3] / 'cortex-brain' / 'dashboards' / 'mock' / 'dashboard_data.json'
        
        with open(mock_data_path) as f:
            mock_data = json.load(f)
        
        # Both should have same top-level structure
        assert set(cortex_data.keys()) == set(mock_data.keys()), \
            "Mock and real data should have same top-level keys"
        
        # Both should have tabs as array
        assert isinstance(cortex_data['tabs'], list), "CORTEX tabs should be array"
        assert isinstance(mock_data['tabs'], list), "Mock tabs should be array"
        
        # Tab structure should match
        if cortex_data['tabs']:
            cortex_tab = cortex_data['tabs'][0]
            mock_tab = mock_data['tabs'][0]
            
            assert 'id' in cortex_tab, "CORTEX tabs should have id"
            assert 'id' in mock_tab, "Mock tabs should have id"
            
            assert 'sections' in cortex_tab, "CORTEX tabs should have sections"
            assert 'sections' in mock_tab, "Mock tabs should have sections"
    
    def test_mock_data_has_multiple_content_types(self):
        """Test mock data demonstrates all supported content types."""
        import json
        mock_data_path = Path(__file__).parents[3] / 'cortex-brain' / 'dashboards' / 'mock' / 'dashboard_data.json'
        
        with open(mock_data_path) as f:
            mock_data = json.load(f)
        
        # Collect all content types used
        content_types = set()
        for tab in mock_data['tabs']:
            for section in tab.get('sections', []):
                content_types.add(section.get('content_type'))
        
        # Should demonstrate variety of content types
        assert 'metrics' in content_types, "Should have metrics sections"
        # At least one other type besides metrics
        assert len(content_types) > 1, "Should demonstrate multiple content types"


class TestDashboardTabCount:
    """Test template displays correct tab count."""
    
    def test_tab_count_uses_array_length(self, app, mock_dashboard_data_array):
        """Test tab count shows len(tabs) for array, not dict."""
        with app.test_request_context():
            from flask import render_template
            
            html = render_template(
                'dashboard_clean.html',
                app_id=mock_dashboard_data_array.app_id,
                app_name=mock_dashboard_data_array.metadata['app_name'],
                tabs=mock_dashboard_data_array.tabs,
                metadata=mock_dashboard_data_array.metadata,
                available_apps=[],
                current_app_id='test_app'
            )
            
            # Should show correct count of 2 tabs
            assert 'Tabs: 2' in html, "Should show correct tab count from array length"
