"""
Tests for Dashboard Template System

Validates template composition, data collection, rendering, and registry.
"""

import pytest
from pathlib import Path
import tempfile
import json

from src.utils.dashboard_template import (
    DashboardTemplate,
    HealthDashboardTemplate,
    PerformanceDashboardTemplate,
    GitActivityDashboardTemplate,
    DashboardTemplateRegistry,
    get_template,
    list_templates,
    render_dashboard
)


class TestHealthDashboardTemplate:
    """Test HealthDashboardTemplate functionality."""
    
    def test_initialization(self):
        """Test template initialization."""
        template = HealthDashboardTemplate()
        
        assert template.template_name == 'health_dashboard'
        assert template.title == 'CORTEX System Health Dashboard'
        assert len(template.sections) == 2
        assert template.sections[0]['id'] == 'health-overview'
        assert template.sections[1]['id'] == 'quality-metrics'
    
    def test_collect_data(self):
        """Test data collection."""
        template = HealthDashboardTemplate()
        data = template.collect_data()
        
        assert isinstance(data, dict)
        assert 'health_trend' in data
        assert 'integration_heatmap' in data
        assert 'test_coverage' in data
        assert 'code_quality' in data
    
    def test_validate_data(self):
        """Test data validation."""
        template = HealthDashboardTemplate()
        
        # Valid data (all fields present)
        valid_data = {
            'health_trend': [{'date': '2025-11-29', 'score': 85}],
            'integration_heatmap': [],
            'test_coverage': None,
            'code_quality': None
        }
        assert template.validate_data(valid_data) is True
        
        # Valid data (all None - N/A placeholders)
        na_data = {
            'health_trend': None,
            'integration_heatmap': None,
            'test_coverage': None,
            'code_quality': None
        }
        assert template.validate_data(na_data) is True
    
    def test_to_config(self):
        """Test configuration export."""
        template = HealthDashboardTemplate()
        config = template.to_config()
        
        assert config['template_name'] == 'health_dashboard'
        assert config['title'] == 'CORTEX System Health Dashboard'
        assert len(config['sections']) == 2


class TestPerformanceDashboardTemplate:
    """Test PerformanceDashboardTemplate functionality."""
    
    def test_initialization(self):
        """Test template initialization."""
        template = PerformanceDashboardTemplate()
        
        assert template.template_name == 'performance_dashboard'
        assert template.title == 'CORTEX Performance Dashboard'
        assert len(template.sections) == 2
    
    def test_collect_data(self):
        """Test data collection returns expected structure."""
        template = PerformanceDashboardTemplate()
        data = template.collect_data()
        
        assert isinstance(data, dict)
        assert 'operation_timeline' in data
        assert 'memory_usage' in data
        assert 'query_performance' in data


class TestGitActivityDashboardTemplate:
    """Test GitActivityDashboardTemplate functionality."""
    
    def test_initialization(self):
        """Test template initialization."""
        template = GitActivityDashboardTemplate()
        
        assert template.template_name == 'git_activity_dashboard'
        assert template.title == 'CORTEX Git Activity & Technical Debt'
        assert len(template.sections) == 2
    
    def test_collect_data(self):
        """Test data collection returns expected structure."""
        template = GitActivityDashboardTemplate()
        data = template.collect_data()
        
        assert isinstance(data, dict)
        assert 'commit_heatmap' in data
        assert 'debt_forecast' in data


class TestDashboardTemplateRegistry:
    """Test DashboardTemplateRegistry functionality."""
    
    def test_initialization(self):
        """Test registry initializes with default templates."""
        registry = DashboardTemplateRegistry()
        
        templates = registry.list_templates()
        assert 'health_dashboard' in templates
        assert 'performance_dashboard' in templates
        assert 'git_activity_dashboard' in templates
    
    def test_get_template(self):
        """Test template retrieval."""
        registry = DashboardTemplateRegistry()
        
        health = registry.get('health_dashboard')
        assert health is not None
        assert isinstance(health, HealthDashboardTemplate)
        
        invalid = registry.get('nonexistent')
        assert invalid is None
    
    def test_register_template(self):
        """Test template registration."""
        registry = DashboardTemplateRegistry()
        
        # Create custom template
        class CustomTemplate(DashboardTemplate):
            def __init__(self):
                super().__init__(
                    template_name='custom',
                    title='Custom Dashboard',
                    description='Test custom template',
                    sections=[]
                )
            
            def collect_data(self):
                return {}
            
            def validate_data(self, data):
                return True
        
        custom = CustomTemplate()
        registry.register(custom)
        
        # Verify registration
        retrieved = registry.get('custom')
        assert retrieved is not None
        assert retrieved.template_name == 'custom'


class TestGlobalRegistry:
    """Test global registry functions."""
    
    def test_get_template(self):
        """Test get_template function."""
        health = get_template('health_dashboard')
        assert health is not None
        assert isinstance(health, HealthDashboardTemplate)
    
    def test_list_templates(self):
        """Test list_templates function."""
        templates = list_templates()
        assert isinstance(templates, list)
        assert len(templates) >= 3
        assert 'health_dashboard' in templates


class TestDashboardRendering:
    """Test dashboard rendering functionality."""
    
    def test_render_health_dashboard(self):
        """Test rendering health dashboard."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "health.html"
            
            # Render with pre-collected data
            data = {
                'health_trend': None,
                'integration_heatmap': None,
                'test_coverage': None,
                'code_quality': None
            }
            
            result = render_dashboard('health_dashboard', output_path, data)
            
            assert result == output_path
            assert output_path.exists()
            
            # Verify HTML content
            content = output_path.read_text(encoding='utf-8')
            assert 'CORTEX System Health Dashboard' in content
            assert 'D3.js' in content or 'd3.js' in content
    
    def test_render_invalid_template(self):
        """Test rendering with invalid template name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.html"
            
            with pytest.raises(ValueError, match="Template not found"):
                render_dashboard('nonexistent', output_path)


class TestTemplateComposition:
    """Test template composition patterns."""
    
    def test_section_structure(self):
        """Test section structure is correct."""
        template = HealthDashboardTemplate()
        
        # Verify sections have required fields
        for section in template.sections:
            assert 'id' in section
            assert 'title' in section
            assert 'charts' in section
            
            # Verify charts have required fields
            for chart in section['charts']:
                assert 'id' in chart
                assert 'type' in chart
                assert 'title' in chart
                assert 'description' in chart
    
    def test_chart_types(self):
        """Test chart types are valid D3.js types."""
        valid_types = [
            'line', 'area', 'bar', 'heatmap', 'gauge', 'radar',
            'area-stacked', 'calendar-heatmap', 'line-confidence'
        ]
        
        templates = [
            HealthDashboardTemplate(),
            PerformanceDashboardTemplate(),
            GitActivityDashboardTemplate()
        ]
        
        for template in templates:
            for section in template.sections:
                for chart in section['charts']:
                    assert chart['type'] in valid_types


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
