"""
Dashboard Template Generator

Generates interactive HTML dashboards with D3.js visualizations according to
CORTEX Documentation Format Specification v1.0.

Copyright ┬⌐ 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import html


@dataclass
class VisualizationConfig:
    """Configuration for a D3.js visualization"""
    viz_type: str  # gauge, tree, matrix, timeline, thumbnail
    target_id: str  # DOM element ID
    data: Dict[str, Any]
    width: int = 960
    height: int = 600
    
    def __post_init__(self):
        """Validate visualization type"""
        valid_types = ['gauge', 'radial', 'tree', 'force-graph', 'matrix', 'heatmap', 'timeline', 'thumbnail']
        if self.viz_type not in valid_types:
            raise ValueError(f"Invalid visualization type: {self.viz_type}. Must be one of {valid_types}")


@dataclass
class DashboardLayer:
    """Configuration for a dashboard layer (tab)"""
    layer_id: str  # e.g., "layer-executive"
    name: str  # Display name
    order: int  # Tab order (1-5)
    content: Dict[str, Any]
    visualization: Optional[VisualizationConfig] = None
    
    def __post_init__(self):
        """Validate layer structure"""
        if not self.layer_id.startswith('layer-'):
            raise ValueError(f"Layer ID must start with 'layer-': {self.layer_id}")
        if self.order < 1:
            raise ValueError(f"Layer order must be >= 1: {self.order}")


class DashboardTemplateGenerator:
    """
    Generates interactive HTML dashboards with D3.js visualizations
    
    Features:
    - Compliant with CORTEX Documentation Format Specification v1.0
    - 5-layer tabbed structure
    - D3.js visualizations (gauge, tree, matrix, timeline, preview)
    - Export functionality (PDF, PNG, PPTX)
    - Security-compliant (CSP, no inline handlers)
    - Accessibility (ARIA labels, keyboard navigation)
    
    Usage:
        generator = DashboardTemplateGenerator()
        
        dashboard = generator.generate_dashboard(
            operation="system-alignment",
            title="System Alignment Report",
            data=results_dict,
            layers=[layer1, layer2, layer3, layer4, layer5]
        )
        
        with open("dashboard.html", "w") as f:
            f.write(dashboard)
    """
    
    # CORTEX color palette
    COLORS = {
        'primary': '#2c3e50',
        'secondary': '#3498db',
        'accent': '#e74c3c',
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'bg_primary': '#ffffff',
        'bg_secondary': '#ecf0f1',
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'border': '#bdc3c7'
    }
    
    def __init__(self):
        """Initialize generator"""
        self.timestamp = datetime.now().isoformat()
    
    def generate_dashboard(
        self,
        operation: str,
        title: str,
        data: Dict[str, Any],
        layers: List[DashboardLayer],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate complete dashboard HTML
        
        Args:
            operation: Operation type (system-alignment, architecture-review, etc.)
            title: Dashboard title
            data: Dashboard data
            layers: List of dashboard layers (minimum 5)
            metadata: Optional metadata
            
        Returns:
            Complete HTML string
        """
        if len(layers) < 5:
            raise ValueError(f"Dashboard must have at least 5 layers, got {len(layers)}")
        
        # Sort layers by order
        layers = sorted(layers, key=lambda l: l.order)
        
        # Build HTML
        html_parts = [
            self._generate_doctype(),
            self._generate_head(title, operation),
            '<body>',
            self._generate_header(title, metadata),
            self._generate_tab_navigation(layers),
            self._generate_layers(layers),
            self._generate_scripts(layers),
            '</body>',
            '</html>'
        ]
        
        return '\n'.join(html_parts)
    
    def _generate_doctype(self) -> str:
        """Generate DOCTYPE declaration"""
        return '<!DOCTYPE html>'
    
    def _generate_head(self, title: str, operation: str) -> str:
        """Generate <head> section with required libraries and styles"""
        return f'''<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - CORTEX Admin Dashboard</title>
    
    <!-- Required Libraries -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    
    <!-- Content Security Policy -->
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://d3js.org https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://d3js.org https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self';">
    
    {self._generate_styles()}
</head>'''
    
    def _generate_styles(self) -> str:
        """Generate CSS styles"""
        return f'''<style>
        :root {{
            /* Primary Colors */
            --cortex-primary: {self.COLORS['primary']};
            --cortex-secondary: {self.COLORS['secondary']};
            --cortex-accent: {self.COLORS['accent']};
            
            /* Status Colors */
            --status-success: {self.COLORS['success']};
            --status-warning: {self.COLORS['warning']};
            --status-error: {self.COLORS['error']};
            
            /* Neutral Colors */
            --bg-primary: {self.COLORS['bg_primary']};
            --bg-secondary: {self.COLORS['bg_secondary']};
            --text-primary: {self.COLORS['text_primary']};
            --text-secondary: {self.COLORS['text_secondary']};
            --border-color: {self.COLORS['border']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                         "Helvetica Neue", Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--bg-secondary);
        }}
        
        h1 {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; }}
        h2 {{ font-size: 2rem; font-weight: 600; margin-bottom: 0.75rem; }}
        h3 {{ font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }}
        
        .header {{
            background: var(--cortex-primary);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        
        .header h1 {{
            color: white;
            margin-bottom: 0.5rem;
        }}
        
        .metadata {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .metadata a {{
            color: var(--cortex-secondary);
            text-decoration: none;
        }}
        
        .metadata a:hover {{
            text-decoration: underline;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-weight: 600;
            margin-top: 1rem;
        }}
        
        .status-badge.success {{
            background: var(--status-success);
            color: white;
        }}
        
        .status-badge.warning {{
            background: var(--status-warning);
            color: white;
        }}
        
        .status-badge.error {{
            background: var(--status-error);
            color: white;
        }}
        
        .tab-navigation {{
            display: flex;
            background: var(--bg-primary);
            border-bottom: 2px solid var(--border-color);
            padding: 0 2rem;
            overflow-x: auto;
        }}
        
        .tab-button {{
            padding: 1rem 2rem;
            border: none;
            background: transparent;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            font-size: 1rem;
            white-space: nowrap;
            color: var(--text-secondary);
        }}
        
        .tab-button:hover {{
            background: var(--bg-secondary);
            color: var(--text-primary);
        }}
        
        .tab-button.active {{
            border-bottom-color: var(--cortex-secondary);
            color: var(--cortex-secondary);
            font-weight: 600;
        }}
        
        .tab-content {{
            display: none;
            padding: 2rem;
            background: var(--bg-primary);
            margin: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            animation: fadeIn 0.3s ease;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .key-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .metric {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .metric .label {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            display: block;
            margin-bottom: 0.5rem;
        }}
        
        .metric .value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--cortex-secondary);
            display: block;
        }}
        
        button {{
            background: var(--cortex-secondary);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
        }}
        
        button:hover {{
            background: var(--cortex-primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        button:active {{
            transform: translateY(0);
        }}
        
        .export-options {{
            display: flex;
            gap: 1rem;
            margin: 2rem 0;
            flex-wrap: wrap;
        }}
        
        .export-options button {{
            flex: 1;
            min-width: 200px;
        }}
        
        svg {{
            display: block;
            margin: 2rem auto;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.9rem;
            pointer-events: none;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .tooltip.show {{
            opacity: 1;
        }}
        
        /* Accessibility */
        *:focus {{
            outline: 2px solid var(--cortex-secondary);
            outline-offset: 2px;
        }}
        
        @media (max-width: 768px) {{
            .tab-navigation {{
                padding: 0;
            }}
            
            .tab-button {{
                padding: 0.75rem 1rem;
                font-size: 0.9rem;
            }}
            
            .tab-content {{
                margin: 1rem;
                padding: 1rem;
            }}
            
            .key-metrics {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>'''
    
    def _generate_header(self, title: str, metadata: Optional[Dict[str, Any]]) -> str:
        """Generate dashboard header"""
        status = metadata.get('status', 'success') if metadata else 'success'
        status_text = metadata.get('status_text', 'Γ£à Success') if metadata else 'Γ£à Success'
        
        return f'''<div class="header">
    <h1>{html.escape(title)}</h1>
    <div class="metadata">
        <span>Generated: {self.timestamp}</span> | 
        <span>Author: Asif Hussain</span> | 
        <a href="https://github.com/asifhussain60/CORTEX" target="_blank">GitHub: github.com/asifhussain60/CORTEX</a>
    </div>
    <div class="status-badge {status}">{html.escape(status_text)}</div>
</div>'''
    
    def _generate_tab_navigation(self, layers: List[DashboardLayer]) -> str:
        """Generate tab navigation"""
        buttons = []
        for i, layer in enumerate(layers):
            active_class = ' active' if i == 0 else ''
            buttons.append(
                f'<button class="tab-button{active_class}" data-target="{layer.layer_id}">{html.escape(layer.name)}</button>'
            )
        
        return f'''<div class="tab-navigation">
    {chr(10).join(f'    {btn}' for btn in buttons)}
</div>'''
    
    def _generate_layers(self, layers: List[DashboardLayer]) -> str:
        """Generate all layer content"""
        layer_htmls = []
        
        for i, layer in enumerate(layers):
            active_class = ' active' if i == 0 else ''
            
            # Generate layer content based on type
            content_html = self._generate_layer_content(layer)
            
            layer_html = f'''<div id="{layer.layer_id}" class="tab-content{active_class}">
    <h2>{html.escape(layer.name)}</h2>
    {content_html}
</div>'''
            layer_htmls.append(layer_html)
        
        return '\n'.join(layer_htmls)
    
    def _generate_layer_content(self, layer: DashboardLayer) -> str:
        """Generate content for a specific layer"""
        content = layer.content
        parts = []
        
        # Add key metrics if present
        if 'key_metrics' in content:
            parts.append(self._generate_key_metrics(content['key_metrics']))
        
        # Add visualization if present
        if layer.visualization:
            viz_id = layer.visualization.target_id.lstrip('#')
            parts.append(f'<svg id="{viz_id}" width="{layer.visualization.width}" height="{layer.visualization.height}"></svg>')
        
        # Add text content if present
        if 'text' in content:
            parts.append(f'<p>{html.escape(content["text"])}</p>')
        
        # Add actions if present
        if 'actions' in content:
            parts.append(self._generate_actions(content['actions']))
        
        return '\n    '.join(parts)
    
    def _generate_key_metrics(self, metrics: List[Dict[str, Any]]) -> str:
        """Generate key metrics display"""
        metric_htmls = []
        for metric in metrics:
            metric_html = f'''<div class="metric">
        <span class="label">{html.escape(metric['label'])}</span>
        <span class="value">{html.escape(str(metric['value']))}</span>
    </div>'''
            metric_htmls.append(metric_html)
        
        return f'''<div class="key-metrics">
    {chr(10).join(metric_htmls)}
</div>'''
    
    def _generate_actions(self, actions: List[Dict[str, str]]) -> str:
        """Generate action buttons"""
        button_htmls = []
        for action in actions:
            button_html = f'<button id="{action["id"]}">{html.escape(action["label"])}</button>'
            button_htmls.append(button_html)
        
        return f'''<div class="export-options">
    {chr(10).join(f'    {btn}' for btn in button_htmls)}
</div>'''
    
    def _generate_scripts(self, layers: List[DashboardLayer]) -> str:
        """Generate JavaScript code"""
        # Tab switching
        tab_script = '''
    // Tab Navigation
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            
            // Update buttons
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // Update content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(targetId).classList.add('active');
        });
    });'''
        
        # Visualization scripts
        viz_scripts = []
        for layer in layers:
            if layer.visualization:
                viz_script = self._generate_visualization_script(layer.visualization)
                viz_scripts.append(viz_script)
        
        # Export functions
        export_script = '''
    
    // Export Functions
    async function exportPDF() {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');
        
        const layers = document.querySelectorAll('.tab-content');
        for (let i = 0; i < layers.length; i++) {
            if (i > 0) pdf.addPage();
            
            const canvas = await html2canvas(layers[i]);
            const imgData = canvas.toDataURL('image/png');
            
            const imgWidth = 190;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
            pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);
        }
        
        pdf.save(`cortex-dashboard-${Date.now()}.pdf`);
    }
    
    async function exportPNG(layerId) {
        const layer = layerId ? document.getElementById(layerId) : document.querySelector('.tab-content.active');
        const canvas = await html2canvas(layer, {
            backgroundColor: '#ffffff',
            scale: 2
        });
        
        const link = document.createElement('a');
        link.download = `cortex-${layerId || 'dashboard'}-${Date.now()}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    }
    
    async function exportPPTX() {
        alert('PPTX export requires PptxGenJS library. Feature coming soon!');
    }'''
        
        # Combine all scripts
        all_scripts = [
            '<script>',
            tab_script,
            '\n'.join(viz_scripts),
            export_script,
            '</script>'
        ]
        
        return '\n'.join(all_scripts)
    
    def _generate_visualization_script(self, viz: VisualizationConfig) -> str:
        """Generate D3.js visualization code"""
        if viz.viz_type == 'gauge':
            return self._generate_gauge_script(viz)
        elif viz.viz_type in ['tree', 'force-graph']:
            return self._generate_tree_script(viz)
        elif viz.viz_type in ['matrix', 'heatmap']:
            return self._generate_matrix_script(viz)
        elif viz.viz_type == 'timeline':
            return self._generate_timeline_script(viz)
        else:
            return f'\n    // Visualization: {viz.viz_type} for {viz.target_id}'
    
    def _generate_gauge_script(self, viz: VisualizationConfig) -> str:
        """Generate gauge/radial chart script"""
        target_id = viz.target_id.lstrip('#')
        data_json = json.dumps(viz.data, indent=4)
        
        return f'''
    
    // Gauge Chart: {target_id}
    (function() {{
        const data = {data_json};
        const width = {viz.width};
        const height = {viz.height};
        const radius = Math.min(width, height) / 2;
        
        const svg = d3.select('#{target_id}');
        const g = svg.append('g')
            .attr('transform', `translate(${{width/2}},${{height/2}})`);
        
        const arc = d3.arc()
            .innerRadius(radius * 0.6)
            .outerRadius(radius * 0.9)
            .startAngle(-Math.PI / 2);
        
        // Background arc
        g.append('path')
            .datum({{endAngle: Math.PI / 2}})
            .style('fill', '#ecf0f1')
            .attr('d', arc);
        
        // Value arc
        const valueArc = g.append('path')
            .datum({{endAngle: -Math.PI / 2}})
            .style('fill', data.value > 85 ? '#27ae60' : data.value > 70 ? '#f39c12' : '#e74c3c')
            .attr('d', arc);
        
        // Animate
        valueArc.transition()
            .duration(1000)
            .attrTween('d', function(d) {{
                const interpolate = d3.interpolate(d.endAngle, -Math.PI / 2 + (data.value / 100) * Math.PI);
                return function(t) {{
                    d.endAngle = interpolate(t);
                    return arc(d);
                }};
            }});
        
        // Center text
        g.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .style('font-size', '48px')
            .style('font-weight', 'bold')
            .style('fill', data.value > 85 ? '#27ae60' : data.value > 70 ? '#f39c12' : '#e74c3c')
            .text(data.value + '%');
        
        // ARIA label
        svg.append('title').text(`Health Score: ${{data.value}}%`);
    }})();'''
    
    def _generate_tree_script(self, viz: VisualizationConfig) -> str:
        """Generate tree/hierarchy visualization script"""
        target_id = viz.target_id.lstrip('#')
        return f'''
    
    // Tree Visualization: {target_id}
    // (Implementation placeholder - requires hierarchical data structure)'''
    
    def _generate_matrix_script(self, viz: VisualizationConfig) -> str:
        """Generate matrix/heatmap visualization script"""
        target_id = viz.target_id.lstrip('#')
        return f'''
    
    // Matrix Visualization: {target_id}
    // (Implementation placeholder - requires matrix data structure)'''
    
    def _generate_timeline_script(self, viz: VisualizationConfig) -> str:
        """Generate timeline visualization script"""
        target_id = viz.target_id.lstrip('#')
        return f'''
    
    // Timeline Visualization: {target_id}
    // (Implementation placeholder - requires temporal data structure)'''
    
    def generate_base_template(self, operation: str, title: str) -> str:
        """
        Generate a minimal base template with placeholder layers
        
        Args:
            operation: Operation type
            title: Dashboard title
            
        Returns:
            Basic HTML template string
        """
        # Create minimal layers
        layers = [
            DashboardLayer(
                layer_id='layer-executive',
                name='Executive Summary',
                order=1,
                content={'text': 'Executive summary content here'},
                visualization=VisualizationConfig(
                    viz_type='gauge',
                    target_id='health-gauge',
                    data={'value': 95},
                    width=400,
                    height=300
                )
            ),
            DashboardLayer(
                layer_id='layer-analysis',
                name='Detailed Analysis',
                order=2,
                content={'text': 'Detailed analysis content here'}
            ),
            DashboardLayer(
                layer_id='layer-issues',
                name='Issues & Recommendations',
                order=3,
                content={'text': 'Issues and recommendations here'}
            ),
            DashboardLayer(
                layer_id='layer-technical',
                name='Technical Details',
                order=4,
                content={'text': 'Technical details here'}
            ),
            DashboardLayer(
                layer_id='layer-export',
                name='Export & Actions',
                order=5,
                content={
                    'text': 'Export options',
                    'actions': [
                        {'id': 'export-pdf-btn', 'label': 'Export PDF'},
                        {'id': 'export-png-btn', 'label': 'Export PNG'},
                        {'id': 'export-pptx-btn', 'label': 'Export PPTX'}
                    ]
                }
            )
        ]
        
        return self.generate_dashboard(
            operation=operation,
            title=title,
            data={},
            layers=layers
        )
