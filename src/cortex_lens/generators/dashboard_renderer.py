"""
Dashboard Renderer - Generates HTML dashboards from analysis data.

Features:
- Template-based HTML generation (Jinja2)
- Data injection from collector results
- Responsive dashboard creation
- Theme support (dark/light)
- Export-ready HTML packages

Author: Asif Hussain
Date: December 2025
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)


class DashboardRenderer:
    """
    Renders HTML dashboards from CORTEX Lens analysis data.
    
    Features:
    - Jinja2 template rendering
    - Data transformation for visualization
    - Static asset copying
    - Self-contained dashboard packages
    """
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize dashboard renderer.
        
        Args:
            template_dir: Directory containing templates (default: base/)
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / 'templates' / 'base'
        
        self.template_dir = template_dir
        self.template_path = template_dir / 'dashboard.html'
        self.css_path = template_dir / 'cortex-unified.css'
        self.js_path = template_dir / 'cortex-unified.js'
        
        # Simple template rendering (no Jinja2 dependency for Phase 4 MVP)
        self.use_simple_rendering = True
    
    def render(
        self,
        analysis_data: Dict[str, Any],
        output_dir: Path,
        repository_name: str = "Repository"
    ) -> Path:
        """
        Render dashboard from analysis data.
        
        Args:
            analysis_data: Complete analysis results from pipeline
            output_dir: Directory to write dashboard files
            repository_name: Name of analyzed repository
            
        Returns:
            Path to generated dashboard.html
        """
        logger.info(f"🎨 Rendering dashboard to: {output_dir}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Transform data for template
        template_data = self._prepare_template_data(analysis_data, repository_name)
        
        # Render HTML
        html_content = self._render_template(template_data)
        
        # Write dashboard files
        dashboard_path = output_dir / 'dashboard.html'
        dashboard_path.write_text(html_content, encoding='utf-8')
        
        # Copy static assets
        self._copy_static_assets(output_dir)
        
        logger.info(f"✅ Dashboard rendered: {dashboard_path}")
        return dashboard_path
    
    def _prepare_template_data(
        self,
        analysis_data: Dict[str, Any],
        repository_name: str
    ) -> Dict[str, Any]:
        """Transform analysis data for template rendering."""
        
        # Extract key metrics
        classification = analysis_data.get('classification', {})
        health_data = analysis_data.get('health', {})
        architecture_data = analysis_data.get('architecture', {})
        security_data = analysis_data.get('security', {})
        complexity_data = analysis_data.get('complexity', {})
        coverage_data = analysis_data.get('test_coverage', {})
        tech_stack_data = analysis_data.get('tech_stack', {})
        dependencies_data = analysis_data.get('dependencies', {})
        narratives_data = analysis_data.get('narratives', {})
        
        # KPI calculations
        total_files = health_data.get('total_files', 0)
        total_lines = health_data.get('total_lines', 0)
        security_issues = security_data.get('vulnerabilities_found', 0)
        test_coverage = coverage_data.get('coverage_summary', 0.0)
        
        # Health score
        health_score = health_data.get('health_score', 0)
        health_score_class = self._get_health_score_class(health_score)
        
        # Language distribution
        language_map = health_data.get('language_map', {})
        languages = [
            {
                'name': lang,
                'percentage': round(count / total_files * 100, 1) if total_files > 0 else 0
            }
            for lang, count in sorted(language_map.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Architecture
        architecture_patterns = [
            {
                'name': pattern,
                'confidence': 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'low'
            }
            for pattern, confidence in architecture_data.get('patterns', {}).items()
        ]
        
        layers = [
            {
                'name': layer.capitalize(),
                'file_count': len(files),
                'percentage': round(len(files) / total_files * 100, 1) if total_files > 0 else 0
            }
            for layer, files in architecture_data.get('layers', {}).items()
        ]
        
        # API endpoints
        api_endpoints = [
            {
                'method': endpoint.get('method', 'GET'),
                'path': endpoint.get('path', '/')
            }
            for endpoint in analysis_data.get('api_endpoints', {}).get('endpoints', [])[:10]
        ]
        
        # Security findings
        security_findings = [
            {
                'severity': finding.get('severity', 'MEDIUM'),
                'type': finding.get('type', 'unknown'),
                'file': Path(finding.get('file', '')).name,
                'line': finding.get('line', 0),
                'description': finding.get('description', '')
            }
            for finding in security_data.get('findings', [])[:20]
        ]
        
        # Complexity hotspots
        complexity_hotspots = [
            {
                'name': hotspot.get('name', 'unknown'),
                'file': Path(hotspot.get('file', '')).name,
                'cyclomatic': hotspot.get('cyclomatic', 0),
                'cognitive': hotspot.get('cognitive', 0),
                'rating': hotspot.get('complexity_rating', 'MEDIUM').upper()
            }
            for hotspot in complexity_data.get('hotspots', [])[:10]
        ]
        
        # Dependencies
        dependencies = [
            {
                'name': dep_name,
                'version': dep_info.get('version', 'unknown'),
                'type': dep_info.get('type', 'direct'),
                'source': dep_info.get('source', 'unknown')
            }
            for dep_name, dep_info in list(dependencies_data.get('packages', {}).items())[:50]
        ]
        
        # Tech stack
        frameworks = tech_stack_data.get('frameworks', [])
        databases = tech_stack_data.get('databases', [])
        build_tools = tech_stack_data.get('build_tools', [])
        
        return {
            'repository_name': repository_name,
            'repo_type': classification.get('repo_type', 'unknown'),
            'repo_type_display': classification.get('repo_type', 'unknown').replace('_', ' ').title(),
            'primary_language': classification.get('primary_language', 'unknown'),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            
            # KPIs
            'total_files': total_files,
            'total_lines': total_lines,
            'security_issues': security_issues,
            'test_coverage': round(test_coverage, 1),
            'health_score': health_score,
            'health_score_class': health_score_class,
            
            # Trends (placeholder for future comparison)
            'security_trend': '',
            'security_trend_class': '',
            'coverage_trend': '',
            'coverage_trend_class': '',
            
            # Language distribution
            'languages': languages,
            
            # Architecture
            'architecture_patterns': architecture_patterns,
            'layers': layers,
            'api_endpoints': api_endpoints,
            
            # Security
            'security_findings': security_findings,
            
            # Complexity
            'avg_cyclomatic': round(complexity_data.get('complexity_summary', {}).get('avg_cyclomatic', 0), 2),
            'avg_cognitive': round(complexity_data.get('complexity_summary', {}).get('avg_cognitive', 0), 2),
            'maintainability_index': round(complexity_data.get('complexity_summary', {}).get('avg_maintainability', 0), 1),
            'complexity_hotspots': complexity_hotspots,
            
            # Dependencies
            'total_dependencies': len(dependencies_data.get('packages', {})),
            'direct_dependencies': sum(1 for d in dependencies_data.get('packages', {}).values() if d.get('type') == 'direct'),
            'transitive_dependencies': sum(1 for d in dependencies_data.get('packages', {}).values() if d.get('type') == 'transitive'),
            'dependencies': dependencies,
            
            # Test coverage
            'total_tests': coverage_data.get('total_tests', 0),
            'avg_assertions': round(coverage_data.get('test_quality_metrics', {}).get('avg_assertions_per_test', 0), 1),
            'unit_tests': coverage_data.get('tests_by_type', {}).get('unit', 0),
            'integration_tests': coverage_data.get('tests_by_type', {}).get('integration', 0),
            
            # Tech stack
            'frameworks': frameworks,
            'databases': databases,
            'build_tools': build_tools,
            
            # Business Intelligence Narratives (Phase 5)
            'narratives': {
                'use_cases': narratives_data.get('use_cases', []),
                'problem_domain': narratives_data.get('problem_domain', {}),
                'business_flows': narratives_data.get('business_flows', []),
                'stakeholders': narratives_data.get('stakeholders', {}),
                'competitive_position': narratives_data.get('competitive_position', {}),
                'risks': narratives_data.get('risks', []),
                'evolution': narratives_data.get('evolution', {})
            },
            
            # Full data as JSON for charts
            'analysis_data_json': json.dumps(analysis_data, indent=2),
        }
    
    def _get_health_score_class(self, score: int) -> str:
        """Get CSS class for health score."""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def _render_template(self, data: Dict[str, Any]) -> str:
        """Render HTML template with data (simple string replacement)."""
        
        # Read template
        template_content = self.template_path.read_text(encoding='utf-8')
        
        # Simple variable replacement (MVP approach)
        # For production, use Jinja2
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                continue  # Skip complex types for MVP
            
            placeholder = f'{{{{ {key} }}}}'
            template_content = template_content.replace(placeholder, str(value))
        
        # Handle loops (simplified for MVP)
        template_content = self._render_simple_loops(template_content, data)
        
        return template_content
    
    def _render_simple_loops(self, template: str, data: Dict[str, Any]) -> str:
        """Simple loop rendering for MVP (replace with Jinja2 for production)."""
        
        # For MVP, just remove Jinja2 syntax and use JavaScript to render data
        # JavaScript will read from analysis_data_json and populate dynamically
        
        # Remove {% %} blocks
        import re
        template = re.sub(r'\{%.*?%\}', '', template)
        
        return template
    
    def _copy_static_assets(self, output_dir: Path):
        """Copy CSS and JS files to output directory."""
        
        if self.css_path.exists():
            shutil.copy(self.css_path, output_dir / 'cortex-unified.css')
            logger.debug("📋 Copied CSS")
        
        if self.js_path.exists():
            shutil.copy(self.js_path, output_dir / 'cortex-unified.js')
            logger.debug("📋 Copied JS")
    
    def _format_number(self, num: int) -> str:
        """Format numbers for display (e.g., 1000 -> 1K)."""
        if num >= 1_000_000:
            return f'{num / 1_000_000:.1f}M'
        elif num >= 1_000:
            return f'{num / 1_000:.1f}K'
        return str(num)
