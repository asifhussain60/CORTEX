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
            primary_type = classification.get('primary_type', 'fullstack_web')
            
            # Map repository type to template
            type_to_template = {
                'console_app': 'console_app',
                'api_service': 'api_service',
                'fullstack_web': 'fullstack_web',
                'library_package': 'library_package',
                'database_project': 'database_project',
                'microservices': 'microservices'
            }
            template_name = type_to_template.get(primary_type, 'fullstack_web')
        
        logger.info(f"Using template: {template_name}")
        
        # Generate dashboard from template
        dashboard_html = self._generate_from_template(data, template_name, output_path)
        
        # Write to file
        index_path = output_path / 'index.html'
        index_path.write_text(dashboard_html, encoding='utf-8')
        
        logger.info(f"✅ Dashboard built: {index_path}")
        
        return index_path
    
    def _generate_from_template(
        self,
        data: Dict[str, Any],
        template_name: str,
        output_path: Path
    ) -> str:
        """Generate dashboard from template with data injection"""
        import json
        import shutil
        
        # Get template path
        template_dir = self.templates_dir / template_name
        
        # Check if template exists
        if not template_dir.exists():
            logger.warning(f"Template '{template_name}' not found, using fallback")
            return self._generate_simple_dashboard(data, template_name)
        
        # Copy CSS and JS from base
        base_dir = self.templates_dir / 'base'
        if base_dir.exists():
            for file in ['cortex-unified.css', 'cortex-unified.js']:
                src = base_dir / file
                if src.exists():
                    shutil.copy2(src, output_path / file)
        
        # Copy components directory
        components_src = base_dir / 'components'
        components_dst = output_path / 'components'
        if components_src.exists():
            shutil.copytree(components_src, components_dst, dirs_exist_ok=True)
        
        # Read template HTML
        template_path = template_dir / 'index.html'
        if not template_path.exists():
            logger.warning(f"Template index.html not found in {template_dir}")
            return self._generate_simple_dashboard(data, template_name)
        
        html_content = template_path.read_text(encoding='utf-8')
        
        # Prepare data for injection
        analysis_data = data.get('data', {})
        narrative = data.get('narrative', {})
        classification = data.get('classification', {})
        
        # Extract template variables
        template_vars = self._extract_template_variables(
            analysis_data, narrative, classification
        )
        
        # Inject data into template
        html_content = self._inject_template_data(html_content, template_vars)
        
        # Inject analysis data JSON for JavaScript
        # Convert sets to lists for JSON serialization
        def convert_sets(obj):
            if isinstance(obj, dict):
                return {k: convert_sets(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_sets(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            else:
                return obj
        
        serializable_data = {
            'metadata': convert_sets(analysis_data.get('metadata', {})),
            'health': convert_sets(analysis_data.get('health', {})),
            'architecture': convert_sets(analysis_data.get('architecture', {})),
            'dependencies': convert_sets(analysis_data.get('dependencies', {})),
            'endpoints': convert_sets(analysis_data.get('api_endpoints', {})),
            'tests': convert_sets(analysis_data.get('test_coverage', {})),
            'security': convert_sets(analysis_data.get('security', {})),
            'narrative': convert_sets(narrative),
            'classification': convert_sets(classification)
        }
        
        analysis_json = json.dumps(serializable_data, indent=2)
        
        html_content = html_content.replace(
            '{{ analysis_data_json }}',
            analysis_json
        )
        
        return html_content
    
    def _generate_simple_dashboard(
        self,
        data: Dict[str, Any],
        template_name: str
    ) -> str:
        """Generate simple HTML dashboard (fallback)"""
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


    def _extract_template_variables(
        self,
        analysis_data: Dict[str, Any],
        narrative: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract variables for template injection"""
        import datetime
        
        metadata = analysis_data.get('metadata', {})
        health = analysis_data.get('health', {})
        architecture = analysis_data.get('architecture', {})
        dependencies = analysis_data.get('dependencies', {})
        api_endpoints = analysis_data.get('api_endpoints', {})
        test_coverage = analysis_data.get('test_coverage', {})
        
        return {
            # Metadata
            'repository_name': metadata.get('repo_name', 'Unknown'),
            'repo_type': classification.get('primary_type', 'unknown'),
            'repo_type_display': classification.get('primary_type', 'unknown').replace('_', ' ').title(),
            'primary_language': metadata.get('primary_language', 'Unknown'),
            'analysis_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            
            # Health metrics
            'health_score': int(health.get('health_score', 0)),
            'health_score_class': self._get_score_class(health.get('health_score', 0)),
            'total_files': health.get('total_files', 0),
            'total_lines': health.get('total_loc', 0),
            
            # Architecture
            'entry_point': architecture.get('entry_points', [{}])[0].get('file', 'N/A') if architecture.get('entry_points') else 'N/A',
            'command_count': len(architecture.get('commands', [])),
            'commands': architecture.get('commands', [])[:10],  # Top 10
            
            # Dependencies
            'dependencies': dependencies.get('list', []),
            'deps_up_to_date': len([d for d in dependencies.get('list', []) if d.get('status') == 'up-to-date']),
            'deps_outdated': len([d for d in dependencies.get('list', []) if d.get('status') == 'outdated']),
            'deps_vulnerable': len([d for d in dependencies.get('list', []) if d.get('status') == 'vulnerable']),
            
            # API endpoints (for api_service template)
            'endpoint_count': len(api_endpoints.get('endpoints', [])),
            'endpoints': api_endpoints.get('endpoints', []),
            'api_type': api_endpoints.get('api_type', 'REST'),
            'framework': api_endpoints.get('framework', 'Unknown'),
            'auth_mechanism': api_endpoints.get('auth_mechanism', 'None'),
            
            # Testing
            'test_coverage': int(test_coverage.get('coverage_percent', 0)),
            'coverage_trend': '+2%',  # TODO: Calculate from history
            'coverage_trend_class': 'trend-up',
            'tests_passing': test_coverage.get('tests_passing', 0),
            'tests_failing': test_coverage.get('tests_failing', 0),
            'tests_skipped': test_coverage.get('tests_skipped', 0),
            
            # Security
            'security_score': int(health.get('security_score', 0)),
            'security_class': self._get_score_class(health.get('security_score', 0)),
            'security_interpretation': self._get_score_interpretation(health.get('security_score', 0)),
            'security_issues': len(analysis_data.get('security', {}).get('vulnerabilities', [])),
            'security_trend': '↓ 3',  # TODO: Calculate from history
            'security_trend_class': 'trend-down',
            'vulnerabilities': analysis_data.get('security', {}).get('vulnerabilities', []),
            
            # Narrative
            'executive_summary': narrative.get('executive_summary', ''),
            'key_capabilities': narrative.get('key_capabilities', []),
            'technical_highlights': narrative.get('technical_highlights', []),
            'recommendations': narrative.get('recommendations', []),
            
            # Additional metrics
            'avg_complexity': architecture.get('avg_complexity', 0),
            'max_complexity': architecture.get('max_complexity', 0),
            'complex_functions': len(architecture.get('complex_functions', [])),
            'maintainability_index': int(health.get('maintainability_index', 0)),
            'maintainability_class': self._get_score_class(health.get('maintainability_index', 0)),
            'maintainability_interpretation': self._get_score_interpretation(health.get('maintainability_index', 0)),
            'code_smells': analysis_data.get('code_quality', {}).get('code_smells', []),
            
            # Console app specific
            'cli_framework': architecture.get('cli_framework', 'argparse'),
            'entry_points': architecture.get('entry_points', []),
            'recent_commits': []  # TODO: Git integration
        }
    
    def _inject_template_data(
        self,
        html_content: str,
        variables: Dict[str, Any]
    ) -> str:
        """Inject variables into template using simple replacement"""
        # Replace {{ variable }} patterns
        for key, value in variables.items():
            # Handle different value types
            if isinstance(value, (list, dict)):
                # Skip complex types, handled by JavaScript
                continue
            
            # Simple string replacement
            placeholder = f'{{{{ {key} }}}}'
            html_content = html_content.replace(placeholder, str(value))
        
        # Handle filters
        if '| format_number' in html_content:
            # Find all {{ value | format_number }} patterns
            import re
            pattern = r'\{\{\s*(\w+)\s*\|\s*format_number\s*\}\}'
            for match in re.finditer(pattern, html_content):
                var_name = match.group(1)
                if var_name in variables:
                    value = variables[var_name]
                    if isinstance(value, (int, float)):
                        formatted = f'{value:,}'
                        html_content = html_content.replace(match.group(0), formatted)
        
        return html_content
    
    def _get_score_class(self, score: float) -> str:
        """Get CSS class for score"""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def _get_score_interpretation(self, score: float) -> str:
        """Get human-readable score interpretation"""
        if score >= 80:
            return 'Excellent - Well maintained and secure'
        elif score >= 60:
            return 'Good - Minor improvements recommended'
        elif score >= 40:
            return 'Fair - Several issues need attention'
        else:
            return 'Poor - Significant improvements required'

