"""
Security Visualization Generator

Purpose: Generate visual representations of security data
         including charts, graphs, and trend visualizations.

Version: 1.0.0
Author: CORTEX Development Team
Created: December 30, 2025
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SecurityVisualization:
    """
    Generates security-focused visualizations for CORTEX Lens.
    
    Visualization types:
    - Radar chart: OWASP Top 10 coverage
    - Timeline: Vulnerability trends over time
    - Heatmap: Risk distribution by component
    - Sankey: Data flow with security controls
    """
    
    # Color palette for security visualization
    COLORS = {
        'critical': '#9C27B0',
        'high': '#f44336',
        'medium': '#FF9800',
        'low': '#4CAF50',
        'info': '#2196F3',
        'background': '#1a1a2e',
        'text': '#ffffff',
        'grid': 'rgba(255,255,255,0.1)',
    }
    
    def __init__(self):
        """Initialize visualization generator."""
        self.chart_id_counter = 0
    
    def _next_chart_id(self) -> str:
        """Generate unique chart ID."""
        self.chart_id_counter += 1
        return f"security_chart_{self.chart_id_counter}"
    
    def generate_owasp_radar(
        self,
        owasp_data: Dict[str, Dict[str, Any]],
        container_id: Optional[str] = None
    ) -> str:
        """
        Generate radar chart for OWASP Top 10 coverage.
        
        Args:
            owasp_data: OWASP coverage data from SecurityDashboard
            container_id: Target container element ID
            
        Returns:
            HTML/JavaScript for radar chart
        """
        chart_id = container_id or self._next_chart_id()
        
        labels = [data['name'][:15] for data in owasp_data.values()]
        findings = [data['findings'] for data in owasp_data.values()]
        risk_scores = [data.get('risk_score', 0) for data in owasp_data.values()]
        
        return f'''
<div id="{chart_id}" style="max-width: 500px; margin: 0 auto;">
    <canvas id="{chart_id}_canvas"></canvas>
</div>
<script>
(function() {{
    const ctx = document.getElementById('{chart_id}_canvas').getContext('2d');
    new Chart(ctx, {{
        type: 'radar',
        data: {{
            labels: {labels},
            datasets: [
                {{
                    label: 'Findings Count',
                    data: {findings},
                    backgroundColor: 'rgba(244, 67, 54, 0.2)',
                    borderColor: '#f44336',
                    pointBackgroundColor: '#f44336',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#f44336'
                }},
                {{
                    label: 'Risk Score',
                    data: {risk_scores},
                    backgroundColor: 'rgba(156, 39, 176, 0.2)',
                    borderColor: '#9C27B0',
                    pointBackgroundColor: '#9C27B0',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#9C27B0'
                }}
            ]
        }},
        options: {{
            responsive: true,
            plugins: {{
                title: {{
                    display: true,
                    text: 'OWASP Top 10 Coverage',
                    color: '{self.COLORS['text']}'
                }},
                legend: {{
                    labels: {{ color: '{self.COLORS['text']}' }}
                }}
            }},
            scales: {{
                r: {{
                    angleLines: {{ color: '{self.COLORS['grid']}' }},
                    grid: {{ color: '{self.COLORS['grid']}' }},
                    pointLabels: {{ color: '{self.COLORS['text']}', font: {{ size: 10 }} }},
                    ticks: {{ color: '{self.COLORS['text']}', backdropColor: 'transparent' }}
                }}
            }}
        }}
    }});
}})();
</script>
'''
    
    def generate_trend_timeline(
        self,
        history: List[Dict[str, Any]],
        container_id: Optional[str] = None
    ) -> str:
        """
        Generate timeline chart showing vulnerability trends.
        
        Args:
            history: Historical scan data
            container_id: Target container element ID
            
        Returns:
            HTML/JavaScript for timeline chart
        """
        chart_id = container_id or self._next_chart_id()
        
        labels = [h.get('timestamp', '')[:10] for h in history]
        scores = [h.get('score', 100) for h in history]
        critical = [h.get('critical', 0) for h in history]
        high = [h.get('high', 0) for h in history]
        total = [h.get('total', 0) for h in history]
        
        return f'''
<div id="{chart_id}" style="height: 300px;">
    <canvas id="{chart_id}_canvas"></canvas>
</div>
<script>
(function() {{
    const ctx = document.getElementById('{chart_id}_canvas').getContext('2d');
    new Chart(ctx, {{
        type: 'line',
        data: {{
            labels: {labels},
            datasets: [
                {{
                    label: 'Security Score',
                    data: {scores},
                    borderColor: '{self.COLORS['info']}',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    fill: true,
                    yAxisID: 'y'
                }},
                {{
                    label: 'Critical Vulns',
                    data: {critical},
                    borderColor: '{self.COLORS['critical']}',
                    borderDash: [5, 5],
                    yAxisID: 'y1'
                }},
                {{
                    label: 'High Vulns',
                    data: {high},
                    borderColor: '{self.COLORS['high']}',
                    borderDash: [5, 5],
                    yAxisID: 'y1'
                }}
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                title: {{
                    display: true,
                    text: 'Security Trend Over Time',
                    color: '{self.COLORS['text']}'
                }},
                legend: {{
                    labels: {{ color: '{self.COLORS['text']}' }}
                }}
            }},
            scales: {{
                x: {{
                    grid: {{ color: '{self.COLORS['grid']}' }},
                    ticks: {{ color: '{self.COLORS['text']}' }}
                }},
                y: {{
                    type: 'linear',
                    position: 'left',
                    min: 0,
                    max: 100,
                    grid: {{ color: '{self.COLORS['grid']}' }},
                    ticks: {{ color: '{self.COLORS['text']}' }},
                    title: {{ display: true, text: 'Score', color: '{self.COLORS['text']}' }}
                }},
                y1: {{
                    type: 'linear',
                    position: 'right',
                    min: 0,
                    grid: {{ drawOnChartArea: false }},
                    ticks: {{ color: '{self.COLORS['text']}' }},
                    title: {{ display: true, text: 'Count', color: '{self.COLORS['text']}' }}
                }}
            }}
        }}
    }});
}})();
</script>
'''
    
    def generate_severity_heatmap(
        self,
        components: Dict[str, Dict[str, int]],
        container_id: Optional[str] = None
    ) -> str:
        """
        Generate heatmap showing severity distribution by component.
        
        Args:
            components: Dict mapping component names to severity counts
            container_id: Target container element ID
            
        Returns:
            HTML/CSS for heatmap visualization
        """
        chart_id = container_id or self._next_chart_id()
        
        rows = []
        for comp_name, severities in components.items():
            critical = severities.get('critical', 0)
            high = severities.get('high', 0)
            medium = severities.get('medium', 0)
            low = severities.get('low', 0)
            
            rows.append(f'''
            <tr>
                <td style="text-align: left; padding: 0.5rem;">{comp_name}</td>
                <td style="background: rgba(156, 39, 176, {min(1, critical * 0.3)}); text-align: center;">{critical}</td>
                <td style="background: rgba(244, 67, 54, {min(1, high * 0.2)}); text-align: center;">{high}</td>
                <td style="background: rgba(255, 152, 0, {min(1, medium * 0.15)}); text-align: center;">{medium}</td>
                <td style="background: rgba(76, 175, 80, {min(1, low * 0.1)}); text-align: center;">{low}</td>
            </tr>
            ''')
        
        return f'''
<div id="{chart_id}" style="overflow-x: auto;">
    <table style="width: 100%; border-collapse: collapse; color: {self.COLORS['text']};">
        <thead>
            <tr style="border-bottom: 1px solid {self.COLORS['grid']};">
                <th style="text-align: left; padding: 0.75rem;">Component</th>
                <th style="text-align: center; padding: 0.75rem; color: {self.COLORS['critical']};">Critical</th>
                <th style="text-align: center; padding: 0.75rem; color: {self.COLORS['high']};">High</th>
                <th style="text-align: center; padding: 0.75rem; color: {self.COLORS['medium']};">Medium</th>
                <th style="text-align: center; padding: 0.75rem; color: {self.COLORS['low']};">Low</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
</div>
'''
    
    def generate_data_flow_diagram(
        self,
        flows: List[Dict[str, Any]],
        container_id: Optional[str] = None
    ) -> str:
        """
        Generate Mermaid data flow diagram with security controls.
        
        Args:
            flows: List of data flow definitions with security controls
            container_id: Target container element ID
            
        Returns:
            Mermaid diagram code
        """
        lines = ['flowchart LR']
        
        for flow in flows:
            source = flow.get('source', 'Source')
            target = flow.get('target', 'Target')
            data_type = flow.get('data_type', 'data')
            controls = flow.get('security_controls', [])
            
            source_id = source.replace(' ', '_')
            target_id = target.replace(' ', '_')
            
            if controls:
                control_text = ', '.join(controls)
                lines.append(f'    {source_id}["{source}"] -->|"{data_type}<br/>🔒 {control_text}"| {target_id}["{target}"]')
            else:
                lines.append(f'    {source_id}["{source}"] -->|"{data_type}<br/>⚠️ No Controls"| {target_id}["{target}"]')
        
        mermaid_code = '\n'.join(lines)
        
        return f'''
<div id="{container_id or self._next_chart_id()}" class="mermaid">
{mermaid_code}
</div>
'''
    
    def generate_security_status_badges(
        self,
        posture: Dict[str, Any]
    ) -> str:
        """
        Generate status badges for security metrics.
        
        Args:
            posture: Security posture data
            
        Returns:
            HTML for status badges
        """
        score = posture.get('score', 100)
        risk_level = posture.get('risk_level', 'LOW')
        trend = posture.get('trend', 'stable')
        
        # Determine colors
        score_color = self.COLORS['low'] if score >= 80 else (
            self.COLORS['medium'] if score >= 60 else (
                self.COLORS['high'] if score >= 40 else self.COLORS['critical']
            )
        )
        
        risk_color = self.COLORS.get(risk_level.lower(), self.COLORS['info'])
        
        trend_icon = '📈' if trend == 'improving' else ('📉' if trend == 'declining' else '➡️')
        trend_color = self.COLORS['low'] if trend == 'improving' else (
            self.COLORS['high'] if trend == 'declining' else self.COLORS['info']
        )
        
        return f'''
<div style="display: flex; gap: 1rem; flex-wrap: wrap;">
    <span style="
        background: {score_color};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
    ">Score: {score}%</span>
    
    <span style="
        background: {risk_color};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
    ">Risk: {risk_level}</span>
    
    <span style="
        background: {trend_color};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
    ">{trend_icon} {trend.title()}</span>
</div>
'''
    
    def generate_full_security_report(
        self,
        dashboard_data: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate complete security report with all visualizations.
        
        Args:
            dashboard_data: Complete dashboard data from SecurityDashboard
            output_path: Optional path to save HTML report
            
        Returns:
            Complete HTML report
        """
        posture = dashboard_data.get('posture', {})
        owasp = dashboard_data.get('owasp_coverage', {})
        history = dashboard_data.get('history', [])
        
        # Generate components
        badges = self.generate_security_status_badges(posture)
        radar = self.generate_owasp_radar(owasp, 'owasp_radar')
        timeline = self.generate_trend_timeline(history, 'trend_timeline')
        
        # Mock component data for heatmap demo
        components = {
            'Authentication': {'critical': 0, 'high': 1, 'medium': 2, 'low': 3},
            'API Layer': {'critical': 1, 'high': 2, 'medium': 3, 'low': 1},
            'Data Access': {'critical': 0, 'high': 0, 'medium': 1, 'low': 2},
            'Frontend': {'critical': 0, 'high': 1, 'medium': 4, 'low': 2},
        }
        heatmap = self.generate_severity_heatmap(components, 'severity_heatmap')
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Security Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 2rem;
        }}
        .report-header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        .report-header h1 {{
            font-size: 2rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .section {{
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 1rem;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <h1>🛡️ CORTEX Security Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>Security Status</h2>
        {badges}
    </div>
    
    <div class="grid-2">
        <div class="section">
            <h2>OWASP Top 10 Coverage</h2>
            {radar}
        </div>
        
        <div class="section">
            <h2>Vulnerability Trend</h2>
            {timeline}
        </div>
    </div>
    
    <div class="section">
        <h2>Risk by Component</h2>
        {heatmap}
    </div>
    
    <script>mermaid.initialize({{startOnLoad:true, theme:'dark'}});</script>
</body>
</html>
'''
        
        if output_path:
            output_path.write_text(html)
            logger.info(f"Security report saved to: {output_path}")
        
        return html
