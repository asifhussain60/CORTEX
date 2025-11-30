"""
Dashboard Generator Orchestrator

Purpose: Generate interactive D3.js-powered dashboards for CORTEX system health,
         architecture quality, test coverage, and development metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.utils.data_collector import DashboardDataCollector
from src.utils.chart_config_builder import ChartConfigBuilder


class DashboardGenerator:
    """
    Generates interactive HTML dashboards with D3.js visualizations.
    
    Features:
    - Health trend charts with forecasts
    - Integration heatmaps (7-layer scoring)
    - Test coverage gauges
    - Code quality radar charts
    - Responsive layout with export functionality
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize dashboard generator.
        
        Args:
            cortex_root: Path to CORTEX root directory (auto-detect if None)
        """
        self.logger = logging.getLogger(__name__)
        
        # Auto-detect CORTEX root
        if cortex_root is None:
            cortex_root = self._detect_cortex_root()
        
        self.cortex_root = Path(cortex_root)
        self.brain_path = self.cortex_root / "cortex-brain"
        self.output_dir = self.brain_path / "documents" / "analysis" / "dashboards"
        self.templates_dir = self.cortex_root / "templates"
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.data_collector = DashboardDataCollector(self.brain_path)
        self.chart_builder = ChartConfigBuilder()
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        self.logger.info(f"DashboardGenerator initialized at {self.cortex_root}")
    
    def _detect_cortex_root(self) -> Path:
        """Auto-detect CORTEX root directory."""
        current = Path.cwd()
        
        # Check current directory
        if (current / "cortex-brain").exists():
            return current
        
        # Check parent directories (up to 3 levels)
        for _ in range(3):
            current = current.parent
            if (current / "cortex-brain").exists():
                return current
        
        # Fallback to cwd
        return Path.cwd()
    
    def generate(
        self,
        output_filename: Optional[str] = None,
        days: int = 30,
        include_charts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete dashboard with all charts.
        
        Args:
            output_filename: Custom filename (default: dashboard-{timestamp}.html)
            days: Number of days of historical data to include
            include_charts: List of chart types to include (None = all)
        
        Returns:
            Dict with keys: success, file_path, message, charts_generated
        """
        try:
            start_time = datetime.now()
            self.logger.info(f"Generating dashboard (last {days} days)...")
            
            # Collect data from all sources
            data = self._collect_all_data(days)
            
            # Build chart configurations
            chart_configs = self._build_chart_configs(data, include_charts)
            
            # Render HTML
            html_content = self._render_dashboard(data, chart_configs)
            
            # Write to file
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output_filename = f"dashboard-{timestamp}.html"
            
            output_path = self.output_dir / output_filename
            output_path.write_text(html_content, encoding='utf-8')
            
            # Create symlink to latest
            latest_link = self.output_dir / "dashboard-latest.html"
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(output_path.name)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'file_path': str(output_path),
                'message': f'Dashboard generated in {elapsed:.2f}s',
                'charts_generated': len(chart_configs),
                'data_points': sum(len(d) for d in data.values() if isinstance(d, list))
            }
            
            self.logger.info(f"Dashboard generated: {output_path} ({elapsed:.2f}s)")
            return result
            
        except Exception as e:
            self.logger.error(f"Dashboard generation failed: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Dashboard generation failed: {str(e)}',
                'charts_generated': 0
            }
    
    def _collect_all_data(self, days: int) -> Dict[str, Any]:
        """
        Collect data from all Tier databases.
        
        Args:
            days: Number of days of historical data
        
        Returns:
            Dict with keys: health_snapshots, test_results, code_metrics, 
                           git_activity, performance_data
        """
        since = datetime.now() - timedelta(days=days)
        
        data = {
            'health_snapshots': self.data_collector.fetch_health_snapshots(since),
            'test_results': self.data_collector.fetch_test_results(since),
            'code_metrics': self.data_collector.fetch_code_metrics(since),
            'git_activity': self.data_collector.fetch_git_activity(since),
            'performance_data': self.data_collector.fetch_performance_data(since),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'days_included': days,
                'cortex_version': self._get_cortex_version()
            }
        }
        
        self.logger.info(f"Data collected: {sum(len(d) for d in data.values() if isinstance(d, list))} total data points")
        return data
    
    def _build_chart_configs(
        self,
        data: Dict[str, Any],
        include_charts: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Build D3.js chart configurations.
        
        Args:
            data: Collected data from databases
            include_charts: List of chart types to include
        
        Returns:
            Dict mapping chart_id to D3.js config
        """
        all_charts = {
            'health_trend': self.chart_builder.build_health_trend_config(
                data['health_snapshots']
            ),
            'integration_heatmap': self.chart_builder.build_integration_heatmap_config(
                data['health_snapshots']
            ),
            'coverage_gauge': self.chart_builder.build_coverage_gauge_config(
                data['test_results']
            ),
            'quality_radar': self.chart_builder.build_quality_radar_config(
                data['code_metrics']
            )
        }
        
        # Filter if specific charts requested
        if include_charts:
            all_charts = {
                k: v for k, v in all_charts.items() 
                if k in include_charts
            }
        
        self.logger.info(f"Built {len(all_charts)} chart configurations")
        return all_charts
    
    def _render_dashboard(
        self,
        data: Dict[str, Any],
        chart_configs: Dict[str, Dict]
    ) -> str:
        """
        Render HTML dashboard using Jinja2 template.
        
        Args:
            data: Collected data
            chart_configs: Chart configurations
        
        Returns:
            Complete HTML content
        """
        # Check if template exists, create if not
        template_path = self.templates_dir / "dashboard.html.j2"
        if not template_path.exists():
            self._create_default_template(template_path)
        
        template = self.jinja_env.get_template("dashboard.html.j2")
        
        # Ensure chart_configs is a proper dictionary (convert any Undefined values to empty dict)
        safe_chart_configs = {}
        for key, value in chart_configs.items():
            if value is not None:
                safe_chart_configs[key] = value
        
        html = template.render(
            data=data,
            chart_configs=safe_chart_configs,  # Fixed: was 'charts', template expects 'chart_configs'
            charts=safe_chart_configs,  # Keep for backward compatibility
            metadata=data.get('metadata', {}),
            color_palette=self._get_color_palette(),
            d3_version='7.8.5'
        )
        
        return html
    
    def _create_default_template(self, template_path: Path):
        """Create default Jinja2 template if it doesn't exist."""
        default_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Dashboard - {{ metadata.generated_at[:10] }}</title>
    <script src="https://d3js.org/d3.v{{ d3_version }}.min.js"></script>
    <link rel="stylesheet" href="dashboard.css">
</head>
<body>
    <header>
        <h1>🧠 CORTEX System Dashboard</h1>
        <p class="timestamp">Generated: {{ metadata.generated_at }}</p>
        <p class="version">CORTEX v{{ metadata.cortex_version }}</p>
    </header>
    
    <main class="dashboard-grid">
        {% for chart_id, config in charts.items() %}
        <div class="chart-container" id="{{ chart_id }}-container">
            <h2>{{ config.title }}</h2>
            <svg id="{{ chart_id }}"></svg>
        </div>
        {% endfor %}
    </main>
    
    <script>
        // Chart data and configs
        const data = {{ data | tojson }};
        const charts = {{ charts | tojson }};
        const colorPalette = {{ color_palette | tojson }};
        
        // Render each chart
        Object.keys(charts).forEach(chartId => {
            renderChart(chartId, charts[chartId], data);
        });
        
        function renderChart(chartId, config, data) {
            // Chart rendering logic will be implemented in Phase 1
            console.log(`Rendering ${chartId}:`, config);
        }
    </script>
</body>
</html>'''
        
        template_path.write_text(default_template, encoding='utf-8')
        self.logger.info(f"Created default template: {template_path}")
    
    def _get_color_palette(self) -> Dict[str, str]:
        """Get dashboard color palette."""
        return {
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#3b82f6',
            'background': '#f9fafb',
            'card': '#ffffff',
            'border': '#e5e7eb',
            'text_primary': '#111827',
            'text_secondary': '#6b7280',
            'forecast': '#8b5cf6'
        }
    
    def _get_cortex_version(self) -> str:
        """Get CORTEX version from VERSION file."""
        version_file = self.cortex_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return "3.2.0"
    
    def export_chart(
        self,
        chart_id: str,
        format: str = 'png',
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export individual chart to PNG/SVG/PDF.
        
        Args:
            chart_id: Chart identifier (health_trend, integration_heatmap, etc.)
            format: Export format ('png', 'svg', 'pdf')
            output_filename: Custom filename (default: {chart_id}-{timestamp}.{format})
        
        Returns:
            Dict with keys: success, file_path, message
        """
        # Placeholder for Phase 2 implementation
        self.logger.warning(f"Export functionality not yet implemented (chart={chart_id}, format={format})")
        return {
            'success': False,
            'message': 'Export functionality will be implemented in Phase 2'
        }
