"""
Chart Config Builder

Purpose: Build D3.js chart configurations for dashboard visualizations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from typing import Dict, List, Any


class ChartConfigBuilder:
    """
    Builds D3.js chart configurations with data and styling specifications.
    
    Chart Types:
    - Health trend line chart with forecast
    - Integration heatmap (7-layer grid)
    - Test coverage circular gauge
    - Code quality radar chart
    """
    
    def __init__(self):
        """Initialize chart config builder."""
        self.logger = logging.getLogger(__name__)
        
        # Chart defaults
        self.default_width = 600
        self.default_height = 400
        self.margin = {'top': 20, 'right': 30, 'bottom': 40, 'left': 50}
        
        self.logger.info("ChartConfigBuilder initialized")
    
    def build_health_trend_config(self, snapshots: List[Dict]) -> Dict[str, Any]:
        """
        Build health trend line chart configuration.
        
        Args:
            snapshots: List of health snapshot dicts or None
        
        Returns:
            D3.js chart config with data, axes, and styling, or N/A config
        """
        # Return N/A config if no data
        if not snapshots:
            return self._build_na_config('health_trend', '📊 Architecture Health Trend (30 Days)')
        
        # Extract data points
        data_points = [
            {
                'date': snapshot['snapshot_time'][:10],
                'score': snapshot['overall_score'],
                'velocity': snapshot.get('velocity', 0),
                'direction': snapshot.get('direction', 'stable')
            }
            for snapshot in snapshots
        ]
        
        config = {
            'id': 'health_trend',
            'title': '📊 Architecture Health Trend (30 Days)',
            'type': 'line',
            'width': self.default_width,
            'height': self.default_height,
            'margin': self.margin,
            'data': data_points,
            'axes': {
                'x': {
                    'field': 'date',
                    'label': 'Date',
                    'type': 'time',
                    'format': '%Y-%m-%d'
                },
                'y': {
                    'field': 'score',
                    'label': 'Health Score (%)',
                    'domain': [0, 100],
                    'ticks': 5
                }
            },
            'line': {
                'stroke': '#3b82f6',
                'stroke_width': 2,
                'curve': 'curveMonotoneX'
            },
            'area': {
                'fill': 'rgba(59, 130, 246, 0.2)',
                'opacity': 0.3
            },
            'threshold_lines': [
                {'value': 90, 'label': 'Healthy', 'color': '#10b981', 'dash': '5,5'},
                {'value': 70, 'label': 'Warning', 'color': '#f59e0b', 'dash': '5,5'}
            ],
            'tooltip': {
                'fields': ['date', 'score', 'velocity', 'direction'],
                'format': {
                    'date': 'Date: {value}',
                    'score': 'Score: {value:.1f}%',
                    'velocity': 'Velocity: {value:+.1f}%/month',
                    'direction': 'Trend: {value}'
                }
            }
        }
        
        self.logger.info(f"Built health trend config: {len(data_points)} points")
        return config
    
    def build_integration_heatmap_config(self, snapshots: List[Dict]) -> Dict[str, Any]:
        """
        Build integration heatmap configuration (7 layers × features).
        
        Args:
            snapshots: List of health snapshot dicts or None
        
        Returns:
            D3.js heatmap config or N/A config
        """
        # Return N/A config if no data
        if not snapshots:
            return self._build_na_config('integration_heatmap', '🔥 Integration Layer Heatmap')
        
        # Use latest snapshot for heatmap
        if snapshots:
            latest = snapshots[-1]
            layer_scores = latest.get('layer_scores', {})
            
            # Create grid data
            layers = ['discovery', 'import', 'instantiation', 'documentation', 
                     'testing', 'wiring', 'optimization']
            
            data = [
                {
                    'layer': layer,
                    'score': layer_scores.get(layer, 0),
                    'status': self._get_status_from_score(layer_scores.get(layer, 0))
                }
                for layer in layers
            ]
        
        config = {
            'id': 'integration_heatmap',
            'title': '🔥 Integration Layer Heatmap',
            'type': 'heatmap',
            'width': self.default_width,
            'height': 300,
            'margin': self.margin,
            'data': data,
            'grid': {
                'rows': 1,
                'cols': 7,
                'cell_size': 60,
                'padding': 2
            },
            'color_scale': {
                'domain': [0, 70, 90, 100],
                'range': ['#ef4444', '#f59e0b', '#10b981', '#10b981'],
                'interpolate': 'interpolateRgb'
            },
            'labels': {
                'show': True,
                'format': '{value:.0f}%',
                'color': '#ffffff',
                'font_size': '14px'
            },
            'legend': {
                'show': True,
                'position': 'bottom',
                'labels': [
                    {'text': '< 70% (Critical)', 'color': '#ef4444'},
                    {'text': '70-89% (Warning)', 'color': '#f59e0b'},
                    {'text': '≥ 90% (Healthy)', 'color': '#10b981'}
                ]
            },
            'tooltip': {
                'fields': ['layer', 'score', 'status'],
                'format': {
                    'layer': 'Layer: {value}',
                    'score': 'Score: {value:.0f}%',
                    'status': 'Status: {value}'
                }
            }
        }
        
        self.logger.info(f"Built heatmap config: {len(data)} layers")
        return config
    
    def build_coverage_gauge_config(self, test_results: List[Dict]) -> Dict[str, Any]:
        """
        Build test coverage circular gauge configuration.
        
        Args:
            test_results: List of test result dicts or None
        
        Returns:
            D3.js gauge config or N/A config
        """
        # Return N/A config if no data
        if not test_results:
            return self._build_na_config('coverage_gauge', '🎯 Test Coverage Gauge')
        
        # Use latest test result
        if test_results:
            latest = test_results[-1]
            coverage = latest.get('coverage_percent', 0)
            module_coverage = latest.get('module_coverage', {})
        
        config = {
            'id': 'coverage_gauge',
            'title': '🎯 Test Coverage Gauge',
            'type': 'gauge',
            'width': self.default_width,
            'height': self.default_height,
            'margin': {'top': 40, 'right': 40, 'bottom': 40, 'left': 40},
            'data': {
                'overall': coverage,
                'modules': module_coverage
            },
            'gauge': {
                'start_angle': -1.5708,  # -π/2 in radians
                'end_angle': 1.5708,     # π/2 in radians
                'inner_radius': 80,
                'outer_radius': 120,
                'corner_radius': 5
            },
            'color': {
                'background': '#e5e7eb',
                'fill': self._get_coverage_color(coverage),
                'transition_duration': 1000
            },
            'label': {
                'show': True,
                'format': '{value:.1f}%',
                'font_size': '32px',
                'color': '#111827',
                'position': 'center'
            },
            'threshold_markers': [
                {'value': 70, 'color': '#ef4444'},
                {'value': 85, 'color': '#f59e0b'},
                {'value': 100, 'color': '#10b981'}
            ],
            'tooltip': {
                'show_modules': True,
                'format': 'Module: {key}\nCoverage: {value:.1f}%'
            }
        }
        
        self.logger.info(f"Built gauge config: {coverage:.1f}% coverage")
        return config
    
    def build_quality_radar_config(self, code_metrics: List[Dict]) -> Dict[str, Any]:
        """
        Build code quality radar chart configuration.
        
        Args:
            code_metrics: List of code metric dicts or None
        
        Returns:
            D3.js radar config or N/A config
        """
        # Return N/A config if no data
        if not code_metrics:
            return self._build_na_config('quality_radar', '🕸️ Code Quality Radar')
        
        # Use latest metrics
        if code_metrics:
            metrics = code_metrics[-1]
        
        # Normalize metrics to 0-100 scale
        data_points = [
            {
                'axis': 'Maintainability',
                'value': metrics.get('maintainability_index', 0),
                'max': 100
            },
            {
                'axis': 'Complexity',
                'value': 100 - min(100, metrics.get('cyclomatic_complexity', 0) * 8),
                'max': 100
            },
            {
                'axis': 'Documentation',
                'value': metrics.get('documentation_ratio', 0) * 100,
                'max': 100
            },
            {
                'axis': 'Test Coverage',
                'value': metrics.get('test_coverage_ratio', 0) * 100,
                'max': 100
            },
            {
                'axis': 'Security',
                'value': metrics.get('security_score', 0),
                'max': 100
            }
        ]
        
        config = {
            'id': 'quality_radar',
            'title': '🕸️ Code Quality Radar',
            'type': 'radar',
            'width': self.default_width,
            'height': self.default_height,
            'margin': {'top': 60, 'right': 60, 'bottom': 60, 'left': 60},
            'data': data_points,
            'radar': {
                'radius': 150,
                'levels': 5,
                'factor': 1,
                'factor_legend': 0.85,
                'max_value': 100
            },
            'polygon': {
                'stroke': '#3b82f6',
                'stroke_width': 2,
                'fill': 'rgba(59, 130, 246, 0.3)',
                'opacity': 0.7
            },
            'circles': {
                'show': True,
                'radius': 4,
                'fill': '#3b82f6',
                'stroke': '#ffffff',
                'stroke_width': 2
            },
            'axes': {
                'show': True,
                'line_color': '#d1d5db',
                'line_width': 1,
                'label_factor': 1.15
            },
            'legend': {
                'show': True,
                'position': 'right',
                'format': '{axis}: {value:.0f}%'
            },
            'tooltip': {
                'fields': ['axis', 'value'],
                'format': {
                    'axis': '{value}',
                    'value': 'Score: {value:.1f}%'
                }
            }
        }
        
        self.logger.info(f"Built radar config: {len(data_points)} dimensions")
        return config
    
    def _get_status_from_score(self, score: float) -> str:
        """Determine status label from score."""
        if score >= 90:
            return 'Healthy'
        elif score >= 70:
            return 'Warning'
        else:
            return 'Critical'
    
    def _get_coverage_color(self, coverage: float) -> str:
        """Get color based on coverage percentage."""
        if coverage >= 85:
            return '#10b981'  # Green
        elif coverage >= 70:
            return '#f59e0b'  # Yellow
        else:
            return '#ef4444'  # Red
    
    def _build_na_config(self, chart_id: str, title: str) -> Dict[str, Any]:
        """
        Build N/A placeholder configuration for unavailable data.
        
        Args:
            chart_id: Chart identifier
            title: Chart title
        
        Returns:
            N/A placeholder config
        """
        return {
            'id': chart_id,
            'title': title,
            'type': 'placeholder',
            'width': self.default_width,
            'height': self.default_height,
            'message': 'Data Not Available',
            'icon': '📊',
            'description': 'Database or metrics not yet available. Run system to collect data.',
            'style': {
                'background': '#f9fafb',
                'border': '2px dashed #d1d5db',
                'text_color': '#6b7280',
                'icon_size': '64px',
                'message_size': '24px',
                'description_size': '14px'
            }
        }
