"""
Tests for EPM Dashboard Adapter

Validates transformation of EPM results (AlignmentReport) into
interactive dashboard layers with D3.js visualization configs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any

from src.generators.epm_dashboard_adapter import EPMDashboardAdapter
from src.generators.dashboard_template_generator import (
    DashboardTemplateGenerator,
    DashboardLayer,
    VisualizationConfig
)


# Mock AlignmentReport and related classes
@dataclass
class MockIntegrationScore:
    """Mock integration score for testing."""
    feature_name: str
    feature_type: str
    score: int
    issues: List[str] = field(default_factory=list)


@dataclass
class MockConflict:
    """Mock conflict for testing."""
    conflict_type: str
    description: str
    severity: str = 'medium'


@dataclass
class MockRemediationSuggestion:
    """Mock remediation suggestion."""
    feature_name: str
    suggestion_type: str
    content: str


@dataclass
class MockAlignmentReport:
    """Mock alignment report for testing."""
    timestamp: datetime
    overall_health: int
    critical_issues: int = 0
    warnings: int = 0
    feature_scores: Dict[str, MockIntegrationScore] = field(default_factory=dict)
    remediation_suggestions: List[MockRemediationSuggestion] = field(default_factory=list)
    catalog_features_new: int = 0
    catalog_days_since_review: int = None
    fix_templates: List[Any] = field(default_factory=list)
    
    @property
    def is_healthy(self) -> bool:
        return self.overall_health >= 80 and self.critical_issues == 0
    
    @property
    def has_warnings(self) -> bool:
        return self.warnings > 0 and self.critical_issues == 0
    
    @property
    def has_errors(self) -> bool:
        return self.critical_issues > 0


class TestEPMDashboardAdapter:
    """Test suite for EPM dashboard adapter."""
    
    def test_adapter_initialization(self):
        """Test adapter initializes correctly."""
        adapter = EPMDashboardAdapter()
        assert adapter is not None
        assert hasattr(adapter, 'transform_alignment_report')
    
    def test_transform_healthy_report(self):
        """Test transformation of healthy alignment report."""
        # Create healthy report
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=95,
            critical_issues=0,
            warnings=0,
            feature_scores={
                'test_orchestrator': MockIntegrationScore(
                    feature_name='test_orchestrator',
                    feature_type='orchestrator',
                    score=95,
                    issues=[]
                ),
                'test_agent': MockIntegrationScore(
                    feature_name='test_agent',
                    feature_type='agent',
                    score=92,
                    issues=[]
                )
            }
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report)
        
        # Validate 5 layers created
        assert len(layers) == 5
        assert all(isinstance(layer, DashboardLayer) for layer in layers)
        
        # Validate layer IDs and order
        assert layers[0].layer_id == 'layer-executive'
        assert layers[1].layer_id == 'layer-analysis'
        assert layers[2].layer_id == 'layer-issues'
        assert layers[3].layer_id == 'layer-trends'
        assert layers[4].layer_id == 'layer-actions'
        
        # Validate all layers have visualizations
        assert all(layer.visualization is not None for layer in layers)
    
    def test_executive_layer_content(self):
        """Test executive summary layer content."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=85,
            critical_issues=2,
            warnings=5,
            feature_scores={
                'feature1': MockIntegrationScore('feature1', 'orchestrator', 95, []),
                'feature2': MockIntegrationScore('feature2', 'agent', 75, ['No tests']),
                'feature3': MockIntegrationScore('feature3', 'orchestrator', 65, ['Not wired'])
            }
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report)
        executive = layers[0]
        
        # Check key metrics
        assert 'key_metrics' in executive.content
        metrics = executive.content['key_metrics']
        assert len(metrics) == 5
        
        # Find overall health metric
        health_metric = next(m for m in metrics if m['label'] == 'Overall Health')
        assert health_metric['value'] == '85%'
        
        # Check text narrative
        assert 'text' in executive.content
        assert 'System Status' in executive.content['text']
        assert '85%' in executive.content['text']
        
        # Verify gauge visualization
        assert executive.visualization.viz_type == 'gauge'
        assert executive.visualization.data['value'] == 85
    
    def test_analysis_layer_feature_table(self):
        """Test feature analysis layer builds correct table."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=80,
            feature_scores={
                'high_score': MockIntegrationScore('high_score', 'orchestrator', 95, []),
                'mid_score': MockIntegrationScore('mid_score', 'agent', 75, ['Missing doc']),
                'low_score': MockIntegrationScore('low_score', 'workflow', 55, ['Not tested', 'Not wired'])
            }
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report)
        analysis = layers[1]
        
        # Check text contains table
        assert '<table' in analysis.content['text']
        assert 'high_score' in analysis.content['text']
        assert '95%' in analysis.content['text']
        assert 'low_score' in analysis.content['text']
        
        # Verify tree visualization
        assert analysis.visualization.viz_type == 'tree'
        tree_data = analysis.visualization.data
        assert 'name' in tree_data
        assert 'children' in tree_data
    
    def test_issues_layer_with_conflicts(self):
        """Test issues layer with conflicts."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=70,
            critical_issues=3,
            warnings=5
        )
        
        conflicts = [
            MockConflict('duplicate', 'Duplicate feature detected', 'high'),
            MockConflict('naming', 'Naming convention violation', 'medium'),
            MockConflict('dependency', 'Circular dependency', 'low')
        ]
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report, conflicts)
        issues = layers[2]
        
        # Check issues content
        assert 'Critical Issues: 3' in issues.content['text']
        assert 'Warnings: 5' in issues.content['text']
        assert 'Detected Conflicts: 3' in issues.content['text']
        
        # Verify matrix visualization
        assert issues.visualization.viz_type == 'matrix'
        matrix_data = issues.visualization.data
        assert 'cells' in matrix_data
        assert len(matrix_data['cells']) == 4  # 2x2 matrix
    
    def test_issues_layer_healthy_state(self):
        """Test issues layer when system is healthy."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=95,
            critical_issues=0,
            warnings=0
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report, [])
        issues = layers[2]
        
        # Should show healthy message
        assert 'No Issues Detected' in issues.content['text']
        assert 'healthy' in issues.content['text'].lower()
    
    def test_trends_layer_timeline_data(self):
        """Test trends layer timeline visualization."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=88,
            feature_scores={'test': MockIntegrationScore('test', 'agent', 90, [])},
            catalog_features_new=3,
            catalog_days_since_review=7
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report)
        trends = layers[3]
        
        # Check timeline data
        assert trends.visualization.viz_type == 'timeline'
        timeline_data = trends.visualization.data
        assert 'series' in timeline_data
        assert len(timeline_data['series']) == 3  # Health, Features, Issues
        
        # Check narrative mentions new features
        assert '3 new features' in trends.content['text'].lower() or '3 features added' in trends.content['text'].lower()
        assert '7 days' in trends.content['text'].lower()
    
    def test_actions_layer_remediation(self):
        """Test actions layer with remediation suggestions."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=75,
            critical_issues=2,
            warnings=3,
            remediation_suggestions=[
                MockRemediationSuggestion('feature1', 'wiring', 'Add trigger to yaml'),
                MockRemediationSuggestion('feature2', 'test', 'Add unit tests')
            ],
            fix_templates=[{'type': 'auto-fix'}]  # Mock fix templates
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report)
        actions = layers[4]
        
        # Check remediation content
        assert '2 suggestions' in actions.content['text'] or 'Auto-Remediation' in actions.content['text']
        assert 'Fix Templates' in actions.content['text']
        
        # Check action buttons
        assert 'actions' in actions.content
        action_buttons = actions.content['actions']
        assert len(action_buttons) >= 3  # PDF, PNG, PPTX at minimum
        
        # Verify thumbnail visualization
        assert actions.visualization.viz_type == 'thumbnail'
    
    def test_end_to_end_dashboard_generation(self):
        """Test complete end-to-end dashboard generation."""
        # Create realistic report
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=82,
            critical_issues=1,
            warnings=4,
            feature_scores={
                f'feature_{i}': MockIntegrationScore(
                    f'feature_{i}',
                    'orchestrator' if i % 2 == 0 else 'agent',
                    85 - i * 5,
                    [] if i < 3 else ['Missing tests']
                )
                for i in range(5)
            },
            remediation_suggestions=[
                MockRemediationSuggestion('feature_4', 'test', 'Add tests')
            ],
            catalog_features_new=2
        )
        
        conflicts = [
            MockConflict('duplicate', 'Test conflict', 'medium')
        ]
        
        # Transform and generate
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report, conflicts)
        
        generator = DashboardTemplateGenerator()
        html = generator.generate_dashboard(
            operation="system-alignment",
            title="Test System Alignment Report",
            data={'overall_health': report.overall_health},
            layers=layers,
            metadata={
                'author': 'Test Adapter',
                'timestamp': report.timestamp.isoformat()
            }
        )
        
        # Validate HTML output
        assert html is not None
        assert len(html) > 1000  # Should be substantial
        assert '<!DOCTYPE html>' in html
        assert 'Test System Alignment Report' in html
        assert 'layer-executive' in html
        assert 'layer-analysis' in html
        assert 'layer-issues' in html
        assert 'layer-trends' in html
        assert 'layer-actions' in html
        
        # Check D3.js library included
        assert 'd3.js' in html or 'd3.v7' in html
        
        # Check visualizations referenced
        assert 'health-gauge' in html
        assert 'feature-tree' in html
        assert 'priority-matrix' in html
        assert 'trends-timeline' in html
    
    def test_empty_feature_scores(self):
        """Test handling of report with no features."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=100,
            feature_scores={}
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report)
        
        # Should still create 5 layers
        assert len(layers) == 5
        
        # Analysis layer should handle empty features
        analysis = layers[1]
        assert 'No features discovered' in analysis.content['text'] or analysis.content['text']
    
    def test_visualization_configs_valid(self):
        """Test all visualization configs are valid."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=85,
            feature_scores={'test': MockIntegrationScore('test', 'agent', 90, [])}
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report)
        
        # Validate each visualization
        expected_types = ['gauge', 'tree', 'matrix', 'timeline', 'thumbnail']
        
        for layer, expected_type in zip(layers, expected_types):
            assert layer.visualization is not None
            assert isinstance(layer.visualization, VisualizationConfig)
            assert layer.visualization.viz_type == expected_type
            assert layer.visualization.target_id is not None
            assert layer.visualization.width > 0
            assert layer.visualization.height > 0
            assert isinstance(layer.visualization.data, dict)
    
    def test_large_dataset_handling(self):
        """Test adapter handles large number of features."""
        # Create report with 50 features
        feature_scores = {
            f'feature_{i:03d}': MockIntegrationScore(
                f'feature_{i:03d}',
                'orchestrator' if i % 3 == 0 else 'agent' if i % 3 == 1 else 'workflow',
                60 + (i % 40),
                []
            )
            for i in range(50)
        }
        
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=75,
            feature_scores=feature_scores
        )
        
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(report)
        
        # Should successfully create layers
        assert len(layers) == 5
        
        # Analysis layer should contain all features
        analysis = layers[1]
        assert 'feature_000' in analysis.content['text']
        assert 'feature_049' in analysis.content['text']
        
        # Tree data should have all features
        tree_data = analysis.visualization.data
        total_features = sum(len(group['children']) for group in tree_data['children'])
        assert total_features == 50


class TestVisualizationDataBuilders:
    """Test specific visualization data builder methods."""
    
    def test_feature_tree_structure(self):
        """Test feature tree creates proper hierarchy."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=80,
            feature_scores={
                'orch1': MockIntegrationScore('orch1', 'orchestrator', 90, []),
                'orch2': MockIntegrationScore('orch2', 'orchestrator', 85, []),
                'agent1': MockIntegrationScore('agent1', 'agent', 92, []),
                'work1': MockIntegrationScore('work1', 'workflow', 78, [])
            }
        )
        
        adapter = EPMDashboardAdapter()
        tree_data = adapter._build_feature_tree_data(report)
        
        # Check root
        assert tree_data['name'] == 'CORTEX Features'
        assert 'children' in tree_data
        
        # Should have 3 groups (orchestrator, agent, workflow)
        assert len(tree_data['children']) == 3
        
        # Find orchestrator group
        orch_group = next(g for g in tree_data['children'] if 'orchestrator' in g['name'].lower())
        assert len(orch_group['children']) == 2
    
    def test_priority_matrix_categorization(self):
        """Test priority matrix correctly categorizes issues."""
        report = MockAlignmentReport(
            timestamp=datetime.now(),
            overall_health=70,
            critical_issues=3,
            warnings=5
        )
        
        conflicts = [
            MockConflict('high', 'High severity', 'high'),
            MockConflict('medium', 'Medium severity', 'medium'),
            MockConflict('low', 'Low severity', 'low')
        ]
        
        adapter = EPMDashboardAdapter()
        matrix_data = adapter._build_priority_matrix_data(report, conflicts)
        
        # Check matrix structure
        assert 'cells' in matrix_data
        assert len(matrix_data['cells']) == 4
        
        # Find high priority/high impact cell
        high_high = next(c for c in matrix_data['cells'] if c['priority'] == 'high' and c['impact'] == 'high')
        assert high_high['count'] > 0  # Should have critical issues + high conflicts
