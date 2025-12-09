#!/usr/bin/env python3
"""
Dashboard Generator (Legacy)

Generates self-contained HTML dashboards by embedding JSON data
into the report-dashboard-template.html (for orchestrator reports).
NOT used by admin dashboard.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """Generates self-contained HTML dashboards"""
    
    def __init__(self, template_path: Path):
        self.template_path = Path(template_path)
        
    def generate(
        self,
        output_path: Path,
        title: str,
        project_info: Dict[str, Any],
        quality_data: Dict[str, Any],
        security_data: Dict[str, Any],
        architecture_data: Dict[str, Any],
        techstack_data: Dict[str, Any],
        recommendations_data: list,
        uml_diagram: str = ""
    ) -> Path:
        """
        Generate self-contained dashboard HTML
        
        Args:
            output_path: Path to save dashboard.html
            title: Dashboard title
            project_info: Project metadata
            quality_data: Code quality analysis
            security_data: Security scan results
            architecture_data: Architecture graph
            techstack_data: Tech stack analysis
            recommendations_data: Recommendations list
            uml_diagram: UML diagram SVG/image data
            
        Returns:
            Path to generated dashboard
        """
        logger.info(f"Generating dashboard: {output_path}")
        
        # Load template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders
        template = template.replace('{{TITLE}}', title)
        template = template.replace('{{VERSION}}', '3.2.0')
        
        # Embed data as JavaScript
        # Map data to template-expected structure
        dashboard_data = {
            'project_info': project_info,
            'quality': quality_data,
            'security': security_data,
            'architecture': architecture_data,
            'techstack': techstack_data,
            'recommendations': recommendations_data,
            'uml_diagram': uml_diagram,
            'metadata': {
                'generatedAt': datetime.now().isoformat(),
                'version': '3.2.0'
            },
            # Add overview section for template compatibility
            'overview': {
                'executiveSummary': f"Analysis of {project_info.get('name', 'project')} containing {project_info.get('files', 0):,} files with {project_info.get('lines', 0):,} lines of code across {len(project_info.get('languages', []))} languages.",
                'keyMetrics': [
                    {'label': 'Files', 'value': f"{project_info.get('files', 0):,}", 'trend': 'stable', 'trendValue': ''},
                    {'label': 'Lines of Code', 'value': f"{project_info.get('lines', 0):,}", 'trend': 'stable', 'trendValue': ''},
                    {'label': 'Quality Score', 'value': f"{quality_data.get('score', 0):.1f}/100", 'trend': 'stable', 'trendValue': ''},
                    {'label': 'Security Issues', 'value': str(security_data.get('vulnerabilities', 0)), 'trend': 'warning' if security_data.get('vulnerabilities', 0) > 0 else 'stable', 'trendValue': ''}
                ],
                'statusIndicator': {
                    'status': 'warning' if security_data.get('vulnerabilities', 0) > 0 else 'healthy',
                    'message': f"Found {security_data.get('vulnerabilities', 0)} security vulnerabilities that require attention." if security_data.get('vulnerabilities', 0) > 0 else "No critical issues detected."
                }
            },
            # Add visualizations section (architecture graph as force graph)
            'visualizations': {
                'forceGraph': architecture_data.get('d3_data', {'nodes': [], 'links': []}),
                'timeSeries': []  # Empty for now
            }
        }
        
        # Replace the {{DASHBOARD_DATA}} placeholder in the template
        template = template.replace('{{DASHBOARD_DATA}}', json.dumps(dashboard_data, indent=2, ensure_ascii=False))
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        logger.info(f"Dashboard generated: {output_path}")
        return output_path


def generate_dashboard_html(
    template_path: Path,
    output_path: Path,
    title: str,
    project_info: Dict[str, Any],
    quality_data: Dict[str, Any],
    security_data: Dict[str, Any],
    architecture_data: Dict[str, Any],
    techstack_data: Dict[str, Any],
    recommendations_data: list,
    uml_diagram: str = ""
) -> Path:
    """
    Convenience function to generate dashboard
    
    Args:
        template_path: Path to template HTML
        output_path: Path to save dashboard
        title: Dashboard title
        project_info: Project metadata
        quality_data: Quality analysis
        security_data: Security scan
        architecture_data: Architecture graph
        techstack_data: Tech stack
        recommendations_data: Recommendations
        uml_diagram: UML diagram data
        
    Returns:
        Path to generated dashboard
    """
    generator = DashboardGenerator(template_path)
    return generator.generate(
        output_path=output_path,
        title=title,
        project_info=project_info,
        quality_data=quality_data,
        security_data=security_data,
        architecture_data=architecture_data,
        techstack_data=techstack_data,
        recommendations_data=recommendations_data,
        uml_diagram=uml_diagram
    )
