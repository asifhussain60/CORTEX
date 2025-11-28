"""
Unit Tests for Dashboard Template Generator

Tests generation of interactive HTML dashboards with D3.js visualizations.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.generators.dashboard_template_generator import (
    DashboardTemplateGenerator,
    DashboardLayer,
    VisualizationConfig
)
from src.validators.documentation_format_validator import DocumentationFormatValidator


@pytest.fixture
def generator():
    """Create generator instance"""
    return DashboardTemplateGenerator()


@pytest.fixture
def validator():
    """Create validator instance"""
    return DocumentationFormatValidator()


@pytest.fixture
def sample_layers():
    """Create sample dashboard layers"""
    return [
        DashboardLayer(
            layer_id='layer-executive',
            name='Executive Summary',
            order=1,
            content={
                'key_metrics': [
                    {'label': 'Overall Score', 'value': '94.2%'},
                    {'label': 'Components', 'value': '47'},
                    {'label': 'Issues', 'value': '3'}
                ],
                'text': 'System is healthy with minor issues.'
            },
            visualization=VisualizationConfig(
                viz_type='gauge',
                target_id='health-gauge',
                data={'value': 94.2},
                width=400,
                height=300
            )
        ),
        DashboardLayer(
            layer_id='layer-analysis',
            name='Detailed Analysis',
            order=2,
            content={'text': 'Detailed component analysis shows strong performance.'},
            visualization=VisualizationConfig(
                viz_type='tree',
                target_id='component-tree',
                data={},
                width=960,
                height=600
            )
        ),
        DashboardLayer(
            layer_id='layer-issues',
            name='Issues & Recommendations',
            order=3,
            content={'text': '3 minor issues identified with remediation steps.'},
            visualization=VisualizationConfig(
                viz_type='matrix',
                target_id='priority-matrix',
                data={},
                width=600,
                height=600
            )
        ),
        DashboardLayer(
            layer_id='layer-technical',
            name='Technical Details',
            order=4,
            content={'text': 'Analyzed 47 files in 12.3 seconds.'},
            visualization=VisualizationConfig(
                viz_type='timeline',
                target_id='execution-timeline',
                data={},
                width=960,
                height=200
            )
        ),
        DashboardLayer(
            layer_id='layer-export',
            name='Export & Actions',
            order=5,
            content={
                'text': 'Export dashboard or create work items.',
                'actions': [
                    {'id': 'export-pdf-btn', 'label': 'Export PDF'},
                    {'id': 'export-png-btn', 'label': 'Export PNG'},
                    {'id': 'export-pptx-btn', 'label': 'Export PPTX'}
                ]
            },
            visualization=VisualizationConfig(
                viz_type='thumbnail',
                target_id='export-preview',
                data={},
                width=300,
                height=200
            )
        )
    ]


class TestDashboardTemplateGenerator:
    """Test suite for DashboardTemplateGenerator"""
    
    def test_generator_initialization(self, generator):
        """Test generator initializes correctly"""
        assert generator is not None
        assert isinstance(generator, DashboardTemplateGenerator)
        assert generator.timestamp is not None
    
    def test_generate_base_template(self, generator):
        """Test base template generation"""
        html = generator.generate_base_template(
            operation="system-alignment",
            title="Test Dashboard"
        )
        
        assert isinstance(html, str)
        assert len(html) > 0
        assert '<!DOCTYPE html>' in html
        assert 'Test Dashboard' in html
        assert 'Asif Hussain' in html
    
    def test_generate_dashboard_with_layers(self, generator, sample_layers):
        """Test full dashboard generation with custom layers"""
        html = generator.generate_dashboard(
            operation="system-alignment",
            title="System Alignment Report",
            data={'overall_score': 94.2},
            layers=sample_layers
        )
        
        assert isinstance(html, str)
        assert len(html) > 0
        
        # Check required elements
        assert '<!DOCTYPE html>' in html
        assert 'System Alignment Report' in html
        assert 'Asif Hussain' in html
        assert 'github.com/asifhussain60/CORTEX' in html
        
        # Check all layers present
        assert 'layer-executive' in html
        assert 'layer-analysis' in html
        assert 'layer-issues' in html
        assert 'layer-technical' in html
        assert 'layer-export' in html
        
        # Check libraries
        assert 'd3.v7.min.js' in html
        assert 'html2canvas' in html
        assert 'jspdf' in html
        
        # Check CSP
        assert 'Content-Security-Policy' in html
        
        # Check tab navigation
        assert 'tab-button' in html
        assert 'tab-content' in html
    
    def test_insufficient_layers_raises_error(self, generator):
        """Test that fewer than 5 layers raises error"""
        layers = [
            DashboardLayer(
                layer_id='layer-executive',
                name='Executive Summary',
                order=1,
                content={'text': 'Test'}
            ),
            DashboardLayer(
                layer_id='layer-analysis',
                name='Analysis',
                order=2,
                content={'text': 'Test'}
            )
        ]
        
        with pytest.raises(ValueError, match="at least 5 layers"):
            generator.generate_dashboard(
                operation="test",
                title="Test",
                data={},
                layers=layers
            )
    
    def test_generated_dashboard_validates(self, generator, validator, sample_layers, tmp_path):
        """Test that generated dashboard passes validation"""
        html = generator.generate_dashboard(
            operation="system-alignment",
            title="System Alignment Report",
            data={'overall_score': 94.2},
            layers=sample_layers,
            metadata={'status': 'success', 'status_text': '✅ Healthy'}
        )
        
        # Save to temp file
        test_file = tmp_path / "generated_dashboard.html"
        test_file.write_text(html, encoding='utf-8')
        
        # Validate
        result = validator.validate(str(test_file))
        
        # Should pass validation
        assert result.is_valid, f"Generated dashboard failed validation. Errors: {[e.message for e in result.errors]}"
        assert result.layer_count >= 5
        assert result.viz_count >= 1  # At least the gauge
    
    def test_html_escaping(self, generator):
        """Test that user content is properly escaped"""
        layers = [
            DashboardLayer(
                layer_id='layer-executive',
                name='Test <script>alert("xss")</script>',
                order=1,
                content={'text': '<script>alert("xss")</script>'}
            ),
            DashboardLayer(layer_id='layer-analysis', name='Test', order=2, content={}),
            DashboardLayer(layer_id='layer-issues', name='Test', order=3, content={}),
            DashboardLayer(layer_id='layer-technical', name='Test', order=4, content={}),
            DashboardLayer(layer_id='layer-export', name='Test', order=5, content={})
        ]
        
        html = generator.generate_dashboard(
            operation="test",
            title='Test <script>alert("xss")</script>',
            data={},
            layers=layers
        )
        
        # Should not contain unescaped script tags
        assert '<script>alert("xss")</script>' not in html
        assert '&lt;script&gt;' in html or '&amp;lt;script&amp;gt;' in html
    
    def test_key_metrics_generation(self, generator):
        """Test key metrics HTML generation"""
        metrics = [
            {'label': 'Score', 'value': '95%'},
            {'label': 'Count', 'value': '42'}
        ]
        
        html = generator._generate_key_metrics(metrics)
        
        assert 'key-metrics' in html
        assert 'Score' in html
        assert '95%' in html
        assert 'Count' in html
        assert '42' in html
    
    def test_action_buttons_generation(self, generator):
        """Test action buttons HTML generation"""
        actions = [
            {'id': 'btn1', 'label': 'Action 1'},
            {'id': 'btn2', 'label': 'Action 2'}
        ]
        
        html = generator._generate_actions(actions)
        
        assert 'export-options' in html
        assert 'btn1' in html
        assert 'Action 1' in html
        assert 'btn2' in html
        assert 'Action 2' in html
    
    def test_layer_ordering(self, generator):
        """Test that layers are correctly ordered"""
        layers = [
            DashboardLayer(layer_id='layer-c', name='C', order=3, content={}),
            DashboardLayer(layer_id='layer-a', name='A', order=1, content={}),
            DashboardLayer(layer_id='layer-e', name='E', order=5, content={}),
            DashboardLayer(layer_id='layer-b', name='B', order=2, content={}),
            DashboardLayer(layer_id='layer-d', name='D', order=4, content={})
        ]
        
        html = generator.generate_dashboard(
            operation="test",
            title="Test",
            data={},
            layers=layers
        )
        
        # Check that tab buttons appear in correct order
        a_pos = html.find('data-target="layer-a"')
        b_pos = html.find('data-target="layer-b"')
        c_pos = html.find('data-target="layer-c"')
        d_pos = html.find('data-target="layer-d"')
        e_pos = html.find('data-target="layer-e"')
        
        assert a_pos < b_pos < c_pos < d_pos < e_pos
    
    def test_gauge_visualization_script(self, generator):
        """Test gauge visualization script generation"""
        viz = VisualizationConfig(
            viz_type='gauge',
            target_id='test-gauge',
            data={'value': 85},
            width=400,
            height=300
        )
        
        script = generator._generate_gauge_script(viz)
        
        assert 'test-gauge' in script
        assert 'd3.select' in script
        assert 'arc' in script
        assert '85' in script
    
    def test_export_functions_included(self, generator, sample_layers):
        """Test that export functions are included in generated dashboard"""
        html = generator.generate_dashboard(
            operation="test",
            title="Test",
            data={},
            layers=sample_layers
        )
        
        assert 'exportPDF' in html
        assert 'exportPNG' in html
        assert 'exportPPTX' in html
        assert 'html2canvas' in html
        assert 'jsPDF' in html
    
    def test_tab_navigation_script(self, generator, sample_layers):
        """Test that tab navigation script is included"""
        html = generator.generate_dashboard(
            operation="test",
            title="Test",
            data={},
            layers=sample_layers
        )
        
        assert 'tab-button' in html
        assert 'addEventListener' in html
        assert 'data-target' in html
        assert 'classList' in html
    
    def test_metadata_in_header(self, generator, sample_layers):
        """Test that metadata appears in header"""
        html = generator.generate_dashboard(
            operation="test",
            title="Test Dashboard",
            data={},
            layers=sample_layers,
            metadata={'status': 'warning', 'status_text': '⚠️ Warning'}
        )
        
        assert '⚠️ Warning' in html
        assert 'status-badge warning' in html


class TestVisualizationConfig:
    """Test VisualizationConfig dataclass"""
    
    def test_valid_visualization_config(self):
        """Test creating valid visualization config"""
        viz = VisualizationConfig(
            viz_type='gauge',
            target_id='test-viz',
            data={'value': 100}
        )
        
        assert viz.viz_type == 'gauge'
        assert viz.target_id == 'test-viz'
        assert viz.data == {'value': 100}
        assert viz.width == 960  # default
        assert viz.height == 600  # default
    
    def test_invalid_visualization_type(self):
        """Test that invalid viz type raises error"""
        with pytest.raises(ValueError, match="Invalid visualization type"):
            VisualizationConfig(
                viz_type='invalid-type',
                target_id='test',
                data={}
            )
    
    def test_custom_dimensions(self):
        """Test custom width/height"""
        viz = VisualizationConfig(
            viz_type='gauge',
            target_id='test',
            data={},
            width=400,
            height=300
        )
        
        assert viz.width == 400
        assert viz.height == 300


class TestDashboardLayer:
    """Test DashboardLayer dataclass"""
    
    def test_valid_layer(self):
        """Test creating valid layer"""
        layer = DashboardLayer(
            layer_id='layer-test',
            name='Test Layer',
            order=1,
            content={'text': 'Test content'}
        )
        
        assert layer.layer_id == 'layer-test'
        assert layer.name == 'Test Layer'
        assert layer.order == 1
        assert layer.content == {'text': 'Test content'}
        assert layer.visualization is None
    
    def test_invalid_layer_id(self):
        """Test that layer ID must start with 'layer-'"""
        with pytest.raises(ValueError, match="must start with 'layer-'"):
            DashboardLayer(
                layer_id='invalid-id',
                name='Test',
                order=1,
                content={}
            )
    
    def test_invalid_order(self):
        """Test that order must be >= 1"""
        with pytest.raises(ValueError, match="order must be >= 1"):
            DashboardLayer(
                layer_id='layer-test',
                name='Test',
                order=0,
                content={}
            )
    
    def test_layer_with_visualization(self):
        """Test layer with visualization"""
        viz = VisualizationConfig(
            viz_type='gauge',
            target_id='test-viz',
            data={'value': 50}
        )
        
        layer = DashboardLayer(
            layer_id='layer-test',
            name='Test',
            order=1,
            content={},
            visualization=viz
        )
        
        assert layer.visualization is not None
        assert layer.visualization.viz_type == 'gauge'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
