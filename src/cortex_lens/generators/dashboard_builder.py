"""
Dashboard Builder

Generates dashboards from templates based on repository type.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .base import BaseGenerator

logger = logging.getLogger(__name__)


class DashboardBuilder(BaseGenerator):
    """
    Build dashboards from templates
    
    Selects appropriate template and injects data.
    """
    
    def __init__(self):
        """Initialize dashboard builder"""
        super().__init__()
        self.templates_dir = Path(__file__).parent.parent / 'templates'
    
    def build(
        self,
        repo_path: Path,
        data: Dict[str, Any],
        narrative: Dict[str, Any],
        classification: Dict[str, Any],
        output_dir: Optional[str],
        template: Optional[str]
    ) -> Path:
        """
        Build dashboard (wrapper for generate)
        
        Args:
            repo_path: Repository path
            data: Collected data
            narrative: Generated narrative
            classification: Classification results
            output_dir: Output directory
            template: Template name (or auto-detect)
            
        Returns:
            Path to dashboard
        """
        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = Path.cwd() / 'cortex-lens-output' / repo_path.name
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Build dashboard
        return self.generate(
            data={
                'data': data,
                'narrative': narrative,
                'classification': classification
            },
            output_path=output_path,
            template=template
        )
    
    def generate(
        self,
        data: Dict[str, Any],
        output_path: Path,
        **kwargs
    ) -> Path:
        """
        Generate dashboard
        
        Args:
            data: Combined data (data, narrative, classification)
            output_path: Output directory
            **kwargs: Additional options (template)
            
        Returns:
            Path to index.html
        """
        logger.info("Building dashboard...")
        
        template_name = kwargs.get('template')
        if not template_name:
            # Auto-detect from classification
            classification = data.get('classification', {})
            template_name = classification.get('dashboard_template', 'fullstack-web-dashboard')
        
        logger.info(f"Using template: {template_name}")
        
        # Create simple HTML dashboard (stub implementation)
        dashboard_html = self._generate_simple_dashboard(data, template_name)
        
        # Write to file
        index_path = output_path / 'index.html'
        index_path.write_text(dashboard_html, encoding='utf-8')
        
        logger.info(f"✅ Dashboard built: {index_path}")
        
        return index_path
    
    def _generate_simple_dashboard(
        self,
        data: Dict[str, Any],
        template_name: str
    ) -> str:
        """Generate simple HTML dashboard (stub)"""
        analysis_data = data.get('data', {})
        narrative = data.get('narrative', {})
        classification = data.get('classification', {})
        
        metadata = analysis_data.get('metadata', {})
        health = analysis_data.get('health', {})
        
        # Simple HTML template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('repo_name', 'Repository')} - CORTEX Lens</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            margin-top: 0;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
            padding: 15px 25px;
            background: #f7f9fc;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .metric strong {{
            display: block;
            font-size: 24px;
            color: #667eea;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f7f9fc;
            border-radius: 10px;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            background: #667eea;
            color: white;
            font-size: 12px;
            margin: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 {metadata.get('repo_name', 'Repository Analysis')}</h1>
        
        <div class="section">
            <h2>📊 Overview</h2>
            <p><strong>Repository Type:</strong> 
                <span class="badge">{classification.get('primary_type', 'unknown')}</span>
            </p>
            <p><strong>Confidence:</strong> {classification.get('confidence', 0):.1%}</p>
            
            <div class="metric">
                <span>Total Files</span>
                <strong>{health.get('total_files', 0):,}</strong>
            </div>
            <div class="metric">
                <span>Lines of Code</span>
                <strong>{health.get('total_loc', 0):,}</strong>
            </div>
            <div class="metric">
                <span>Health Score</span>
                <strong>{health.get('health_score', 0):.1f}/100</strong>
            </div>
        </div>
        
        <div class="section">
            <h2>📝 Executive Summary</h2>
            <p>{narrative.get('executive_summary', 'No summary available')}</p>
        </div>
        
        <div class="section">
            <h2>💡 Key Capabilities</h2>
            <ul>
                {''.join(f'<li>{cap}</li>' for cap in narrative.get('key_capabilities', []))}
            </ul>
        </div>
        
        <div class="section">
            <h2>🔍 Technical Highlights</h2>
            <ul>
                {''.join(f'<li>{highlight}</li>' for highlight in narrative.get('technical_highlights', []))}
            </ul>
        </div>
        
        <div class="section">
            <h2>📌 Recommendations</h2>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in narrative.get('recommendations', []))}
            </ul>
        </div>
        
        <hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;">
        
        <p style="text-align: center; color: #999; font-size: 12px;">
            Generated by CORTEX Lens v1.0.0 | Template: {template_name}
        </p>
    </div>
</body>
</html>
"""
        
        return html
