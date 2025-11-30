"""
Dashboard Template System - Reusable Dashboard Generation

Provides abstract template pattern for generating D3.js dashboards with
configurable layouts, charts, and data sources. Supports template composition,
inheritance, and integration with Enterprise Documentation Orchestrator.

Author: Asif Hussain
Version: 3.2.1
Status: Production Ready
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
from jinja2 import Template
from datetime import datetime
import json


class DashboardTemplate(ABC):
    """
    Abstract base class for dashboard templates.
    
    Provides template composition pattern with configurable sections,
    chart types, and data binding. Subclasses implement specific
    dashboard types (health, performance, git activity).
    """
    
    def __init__(
        self,
        template_name: str,
        title: str,
        description: str,
        sections: List[Dict[str, Any]]
    ):
        """
        Initialize dashboard template.
        
        Args:
            template_name: Unique template identifier
            title: Dashboard title
            description: Dashboard description
            sections: List of section configs with charts
        """
        self.template_name = template_name
        self.title = title
        self.description = description
        self.sections = sections
        
    @abstractmethod
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data from various sources for dashboard.
        
        Returns:
            Dict with data for all charts/sections
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate collected data meets template requirements.
        
        Args:
            data: Collected data dictionary
            
        Returns:
            True if data valid, False otherwise
        """
        pass
    
    def render(
        self,
        output_path: Path,
        data: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Render dashboard to HTML file.
        
        Args:
            output_path: Path to save rendered dashboard
            data: Optional pre-collected data (uses collect_data if None)
            
        Returns:
            Path to rendered dashboard file
        """
        # Collect data if not provided
        if data is None:
            data = self.collect_data()
        
        # Validate data
        if not self.validate_data(data):
            raise ValueError(f"Data validation failed for template: {self.template_name}")
        
        # Ensure all data fields have defaults (prevent Jinja2 Undefined issues)
        data = {k: (v if v is not None else {}) for k, v in data.items()}
        
        # Load base template
        template_path = Path(__file__).parent.parent.parent / "templates" / "dashboard.html.j2"
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Create Jinja template
        template = Template(template_content)
        
        # Build chart configs from sections
        chart_configs = []
        for section in self.sections:
            for chart in section['charts']:
                chart_config = {
                    'id': chart['id'],
                    'type': chart['type'],
                    'title': chart['title'],
                    'data': data.get(chart['id'], {})
                }
                chart_configs.append(chart_config)
        
        # Render with data
        html_content = template.render(
            title=self.title,
            description=self.description,
            sections=self.sections,
            chart_configs=chart_configs,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Write to output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def to_config(self) -> Dict[str, Any]:
        """
        Export template configuration as dictionary.
        
        Returns:
            Template config dict
        """
        return {
            'template_name': self.template_name,
            'title': self.title,
            'description': self.description,
            'sections': self.sections
        }


class HealthDashboardTemplate(DashboardTemplate):
    """
    Template for system health dashboard.
    
    Displays architecture health, integration status, test coverage,
    and code quality metrics.
    """
    
    def __init__(self):
        """Initialize health dashboard template."""
        sections = [
            {
                'id': 'health-overview',
                'title': 'System Health Overview',
                'charts': [
                    {
                        'id': 'health-trend',
                        'type': 'line',
                        'title': 'Architecture Health Trend',
                        'description': '30-day health score evolution'
                    },
                    {
                        'id': 'integration-heatmap',
                        'type': 'heatmap',
                        'title': 'Feature Integration Status',
                        'description': '7-layer validation heatmap'
                    }
                ]
            },
            {
                'id': 'quality-metrics',
                'title': 'Quality & Coverage',
                'charts': [
                    {
                        'id': 'test-coverage-gauge',
                        'type': 'gauge',
                        'title': 'Test Coverage',
                        'description': 'Overall test coverage percentage'
                    },
                    {
                        'id': 'code-quality-radar',
                        'type': 'radar',
                        'title': 'Code Quality',
                        'description': '5-dimension quality assessment'
                    }
                ]
            }
        ]
        
        super().__init__(
            template_name='health_dashboard',
            title='CORTEX System Health Dashboard',
            description='Real-time architecture health and quality metrics',
            sections=sections
        )
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect health data from Tier 3 and System Alignment.
        
        Returns:
            Dict with health trend, integration scores, coverage, quality
        """
        from src.tier3.architecture_health_history import ArchitectureHealthHistory
        from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator
        
        data = {}
        
        # Health trend data (last 30 days)
        try:
            health_history = ArchitectureHealthHistory()
            snapshots = health_history.get_snapshots(days=30)
            
            if snapshots:
                data['health_trend'] = [
                    {
                        'date': snapshot['timestamp'].isoformat(),
                        'score': snapshot['overall_score'],
                        'velocity': snapshot.get('velocity', 0)
                    }
                    for snapshot in snapshots
                ]
            else:
                data['health_trend'] = None
        except Exception as e:
            print(f"Warning: Failed to load health trend: {e}")
            data['health_trend'] = None
        
        # Integration heatmap data
        try:
            alignment = SystemAlignmentOrchestrator(Path.cwd())
            report = alignment.execute()
            
            if report and report.features:
                data['integration_heatmap'] = [
                    {
                        'feature': feature.name,
                        'layers': {
                            'discovery': feature.integration_score >= 20,
                            'import': feature.integration_score >= 40,
                            'instantiation': feature.integration_score >= 60,
                            'documentation': feature.integration_score >= 70,
                            'testing': feature.integration_score >= 80,
                            'wiring': feature.integration_score >= 90,
                            'optimization': feature.integration_score >= 100
                        },
                        'score': feature.integration_score
                    }
                    for feature in report.features[:20]  # Top 20 features
                ]
            else:
                data['integration_heatmap'] = None
        except Exception as e:
            print(f"Warning: Failed to load integration data: {e}")
            data['integration_heatmap'] = None
        
        # Test coverage data
        try:
            # TODO: Integrate with actual test coverage collector
            # For now, return None to show N/A placeholder
            data['test_coverage'] = None
        except Exception as e:
            print(f"Warning: Failed to load test coverage: {e}")
            data['test_coverage'] = None
        
        # Code quality data
        try:
            # TODO: Integrate with actual code quality analyzer
            # For now, return None to show N/A placeholder
            data['code_quality'] = None
        except Exception as e:
            print(f"Warning: Failed to load code quality: {e}")
            data['code_quality'] = None
        
        return data
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate health dashboard data.
        
        Args:
            data: Collected data dictionary
            
        Returns:
            True (always valid, uses N/A placeholders for missing data)
        """
        # All health dashboard data is optional
        # N/A placeholders shown when data is None
        return True


class PerformanceDashboardTemplate(DashboardTemplate):
    """
    Template for performance metrics dashboard.
    
    Displays operation timing, database query performance, memory usage,
    and performance trends over time.
    """
    
    def __init__(self):
        """Initialize performance dashboard template."""
        sections = [
            {
                'id': 'performance-timeline',
                'title': 'Performance Timeline',
                'charts': [
                    {
                        'id': 'operation-timeline',
                        'type': 'area-stacked',
                        'title': 'Operation Performance Breakdown',
                        'description': '4-layer timing (operation/agent/database/network)'
                    }
                ]
            },
            {
                'id': 'performance-metrics',
                'title': 'Performance Metrics',
                'charts': [
                    {
                        'id': 'memory-usage',
                        'type': 'line',
                        'title': 'Memory Usage',
                        'description': 'Memory consumption over time'
                    },
                    {
                        'id': 'query-performance',
                        'type': 'bar',
                        'title': 'Database Query Performance',
                        'description': 'Top 10 slowest queries'
                    }
                ]
            }
        ]
        
        super().__init__(
            template_name='performance_dashboard',
            title='CORTEX Performance Dashboard',
            description='Real-time performance metrics and bottleneck analysis',
            sections=sections
        )
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect performance data from Tier 1 working memory.
        
        Returns:
            Dict with operation timeline, memory usage, query performance
        """
        # TODO: Implement performance data collection
        # For now, return None for all metrics to show N/A placeholders
        return {
            'operation_timeline': None,
            'memory_usage': None,
            'query_performance': None
        }
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate performance dashboard data.
        
        Args:
            data: Collected data dictionary
            
        Returns:
            True (always valid, uses N/A placeholders for missing data)
        """
        return True


class GitActivityDashboardTemplate(DashboardTemplate):
    """
    Template for git activity dashboard.
    
    Displays commit heatmap (calendar style), contributor stats,
    and technical debt forecast.
    """
    
    def __init__(self):
        """Initialize git activity dashboard template."""
        sections = [
            {
                'id': 'git-activity',
                'title': 'Git Activity',
                'charts': [
                    {
                        'id': 'commit-heatmap',
                        'type': 'calendar-heatmap',
                        'title': 'Commit Activity (Last 53 Weeks)',
                        'description': 'GitHub-style commit heatmap'
                    }
                ]
            },
            {
                'id': 'technical-debt',
                'title': 'Technical Debt',
                'charts': [
                    {
                        'id': 'debt-forecast',
                        'type': 'line-confidence',
                        'title': 'Technical Debt Forecast',
                        'description': '3-month and 6-month projections'
                    }
                ]
            }
        ]
        
        super().__init__(
            template_name='git_activity_dashboard',
            title='CORTEX Git Activity & Technical Debt',
            description='Repository activity and debt forecasting',
            sections=sections
        )
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect git activity data from repository.
        
        Returns:
            Dict with commit heatmap, contributor stats, debt forecast
        """
        # TODO: Implement git activity data collection
        # For now, return None for all metrics to show N/A placeholders
        return {
            'commit_heatmap': None,
            'debt_forecast': None
        }
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate git activity dashboard data.
        
        Args:
            data: Collected data dictionary
            
        Returns:
            True (always valid, uses N/A placeholders for missing data)
        """
        return True


class DashboardTemplateRegistry:
    """
    Registry for dashboard templates.
    
    Provides template lookup, registration, and listing functionality.
    Supports dynamic template loading from configuration files.
    """
    
    def __init__(self):
        """Initialize template registry."""
        self._templates: Dict[str, DashboardTemplate] = {}
        self._register_default_templates()
    
    def _register_default_templates(self):
        """Register default dashboard templates."""
        self.register(HealthDashboardTemplate())
        self.register(PerformanceDashboardTemplate())
        self.register(GitActivityDashboardTemplate())
    
    def register(self, template: DashboardTemplate):
        """
        Register a dashboard template.
        
        Args:
            template: Dashboard template instance
        """
        self._templates[template.template_name] = template
    
    def get(self, template_name: str) -> Optional[DashboardTemplate]:
        """
        Get template by name.
        
        Args:
            template_name: Template identifier
            
        Returns:
            DashboardTemplate instance or None if not found
        """
        return self._templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """
        List all registered template names.
        
        Returns:
            List of template names
        """
        return list(self._templates.keys())
    
    def render_template(
        self,
        template_name: str,
        output_path: Path,
        data: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Render template by name.
        
        Args:
            template_name: Template to render
            output_path: Output file path
            data: Optional pre-collected data
            
        Returns:
            Path to rendered dashboard
            
        Raises:
            ValueError: If template not found
        """
        template = self.get(template_name)
        if template is None:
            raise ValueError(f"Template not found: {template_name}")
        
        return template.render(output_path, data)


# Global registry instance
_registry = DashboardTemplateRegistry()


def get_template(template_name: str) -> Optional[DashboardTemplate]:
    """
    Get dashboard template from global registry.
    
    Args:
        template_name: Template identifier
        
    Returns:
        DashboardTemplate instance or None
    """
    return _registry.get(template_name)


def list_templates() -> List[str]:
    """
    List all available dashboard templates.
    
    Returns:
        List of template names
    """
    return _registry.list_templates()


def render_dashboard(
    template_name: str,
    output_path: Path,
    data: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Render dashboard using named template.
    
    Args:
        template_name: Template to use
        output_path: Output file path
        data: Optional pre-collected data
        
    Returns:
        Path to rendered dashboard
    """
    return _registry.render_template(template_name, output_path, data)
