"""
CORTEX Onboarding Dashboard - Presentation Layer

This module implements the presentation layer for the onboarding dashboard,
following clean architecture principles. It bridges use cases with Jinja2 templates.

Author: Asif Hussain
Copyright: © 2024-2025
Repository: https://github.com/asifhussain60/CORTEX
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json

from src.dashboard.use_cases.load_overview import LoadOverviewUseCase
from src.dashboard.use_cases.render_architecture_graph import RenderArchitectureGraphUseCase
from src.dashboard.use_cases.analyze_quality_metrics import AnalyzeQualityMetricsUseCase
from src.dashboard.use_cases.scan_security_vulnerabilities import ScanSecurityVulnerabilitiesUseCase
from src.dashboard.use_cases.generate_recommendations import GenerateRecommendationsUseCase
from src.use_cases.render_uml_diagrams import render_uml_for_project

from src.dashboard.data.json_repositories import (
    JSONComponentRepository,
    JSONDependencyRepository,
    JSONIssueRepository,
    JSONHealthScoreRepository
)
# Note: RecommendationRepository doesn't exist yet, will use Issue repo
# from src.dashboard.data.repository_interface import IRecommendationRepository


class DashboardRenderer:
    """
    Renders the onboarding dashboard by coordinating use cases and templates.
    
    Responsibilities:
    - Initialize Jinja2 environment
    - Execute use cases to gather data
    - Transform data for template consumption
    - Render HTML output
    """
    
    def __init__(self, project_path: Path, data_dir: Path):
        """
        Initialize the dashboard renderer.
        
        Args:
            project_path: Path to the project being analyzed
            data_dir: Path to directory containing analysis JSON files
        """
        self.project_path = project_path
        self.data_dir = data_dir
        
        template_dir = Path(__file__).parents[3] / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml', 'j2']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self._register_filters()
        
        self.component_repo = JSONComponentRepository(data_dir / "components.json")
        self.dependency_repo = JSONDependencyRepository(data_dir / "dependencies.json")
        self.issue_repo = JSONIssueRepository(data_dir / "issues.json")
        self.health_repo = JSONHealthScoreRepository(data_dir / "health.json")
        # TODO: Implement RecommendationRepository when needed
        self.recommendation_repo = None  # Placeholder
        
        self.overview_use_case = LoadOverviewUseCase(
            self.component_repo,
            self.issue_repo,
            self.health_repo
        )
        self.architecture_use_case = RenderArchitectureGraphUseCase(
            self.component_repo,
            self.dependency_repo,
            self.health_repo
        )
        self.quality_use_case = AnalyzeQualityMetricsUseCase(
            self.component_repo,
            self.issue_repo
        )
        self.security_use_case = ScanSecurityVulnerabilitiesUseCase(
            self.component_repo,
            self.issue_repo
        )
        self.recommendations_use_case = GenerateRecommendationsUseCase(
            self.component_repo,
            self.issue_repo,
            self.dependency_repo
        )
    
    def _register_filters(self):
        """Register custom Jinja2 filters."""
        
        def format_number(value: int) -> str:
            """Format number with thousands separators."""
            return f"{value:,}"
        
        def round_decimal(value: float, places: int = 2) -> float:
            """Round decimal to specified places."""
            return round(value, places)
        
        self.jinja_env.filters['format_number'] = format_number
        self.jinja_env.filters['round'] = round_decimal
    
    def render(
        self,
        output_path: Path,
        enable_websocket: bool = False,
        websocket_url: str = "http://localhost:5000"
    ) -> Path:
        """
        Render the complete dashboard to HTML file.
        
        Args:
            output_path: Path where HTML file should be saved
            enable_websocket: Whether to enable WebSocket real-time updates
            websocket_url: URL of WebSocket server
            
        Returns:
            Path to generated HTML file
        """
        # Gather data from all use cases
        dashboard_data = self._gather_dashboard_data()
        
        # Load main template
        template = self.jinja_env.get_template("project_onboarding_dashboard.html.j2")
        
        # Helper to safely get data with defaults
        def safe_get(data_dict, key, default=0):
            return data_dict.get(key, default)
        
        # Prepare template context
        context = {
            # Meta
            "project_name": self.project_path.name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "enable_websocket": enable_websocket,
            "websocket_url": websocket_url,
            
            # Overview data
            "health_score": safe_get(dashboard_data["overview"], "health_score", 0),
            "health_category": self._get_health_category(safe_get(dashboard_data["overview"], "health_score", 0)),
            "health_label": self._get_health_label(safe_get(dashboard_data["overview"], "health_score", 0)),
            "health_description": safe_get(dashboard_data["overview"], "health_description", "No data"),
            "file_count": safe_get(dashboard_data["overview"], "file_count"),
            "loc_count": safe_get(dashboard_data["overview"], "loc_count"),
            "component_count": safe_get(dashboard_data["overview"], "component_count"),
            "dependency_count": safe_get(dashboard_data["overview"], "dependency_count"),
            "issue_count": safe_get(dashboard_data["overview"], "issue_count"),
            "vulnerability_count": safe_get(dashboard_data["overview"], "vulnerability_count"),
            "languages": safe_get(dashboard_data["overview"], "languages", []),
            "quick_insights": dashboard_data["overview"]["quick_insights"],
            "recent_activities": dashboard_data["overview"]["recent_activities"],
            
            # Architecture data
            "architecture_nodes": dashboard_data["architecture"]["nodes"],
            "architecture_edges": dashboard_data["architecture"]["edges"],
            "avg_complexity": dashboard_data["architecture"]["avg_complexity"],
            "max_nesting": dashboard_data["architecture"]["max_nesting"],
            "coupling_score": dashboard_data["architecture"]["coupling_score"],
            "cohesion_score": dashboard_data["architecture"]["cohesion_score"],
            "total_dependencies": dashboard_data["architecture"]["total_dependencies"],
            "circular_dependencies": dashboard_data["architecture"]["circular_dependencies"],
            "external_dependencies": dashboard_data["architecture"]["external_dependencies"],
            "max_dependency_depth": dashboard_data["architecture"]["max_dependency_depth"],
            "detected_patterns": dashboard_data["architecture"]["detected_patterns"],
            
            # Quality data
            "quality_score": dashboard_data["quality"]["overall_score"],
            "maintainability_score": dashboard_data["quality"]["maintainability_score"],
            "maintainability_category": self._get_health_category(dashboard_data["quality"]["maintainability_score"]),
            "readability_score": dashboard_data["quality"]["readability_score"],
            "readability_category": self._get_health_category(dashboard_data["quality"]["readability_score"]),
            "test_coverage": dashboard_data["quality"]["test_coverage"],
            "coverage_category": self._get_health_category(dashboard_data["quality"]["test_coverage"]),
            "documentation_score": dashboard_data["quality"]["documentation_score"],
            "docs_category": self._get_health_category(dashboard_data["quality"]["documentation_score"]),
            "code_smells": dashboard_data["quality"]["code_smells"],
            "max_complexity": dashboard_data["quality"]["max_complexity"],
            "high_complexity_files": dashboard_data["quality"]["high_complexity_files"],
            "line_coverage": dashboard_data["quality"]["line_coverage"],
            "branch_coverage": dashboard_data["quality"]["branch_coverage"],
            "function_coverage": dashboard_data["quality"]["function_coverage"],
            "uncovered_files": dashboard_data["quality"]["uncovered_files"],
            "partially_covered_files": dashboard_data["quality"]["partially_covered_files"],
            "fully_covered_files": dashboard_data["quality"]["fully_covered_files"],
            "duplication_percentage": dashboard_data["quality"]["duplication_percentage"],
            "duplicate_blocks": dashboard_data["quality"]["duplicate_blocks"],
            "duplicate_lines": dashboard_data["quality"]["duplicate_lines"],
            "top_duplications": dashboard_data["quality"]["top_duplications"],
            
            # Security data
            "security_score": dashboard_data["security"]["overall_score"],
            "security_category": self._get_health_category(dashboard_data["security"]["overall_score"]),
            "security_label": self._get_health_label(dashboard_data["security"]["overall_score"]),
            "critical_vulns": dashboard_data["security"]["critical_count"],
            "high_vulns": dashboard_data["security"]["high_count"],
            "medium_vulns": dashboard_data["security"]["medium_count"],
            "low_vulns": dashboard_data["security"]["low_count"],
            "total_vulns": dashboard_data["security"]["total_count"],
            "owasp_top_10": dashboard_data["security"]["owasp_top_10"],
            "vulnerabilities": dashboard_data["security"]["vulnerabilities"],
            "security_practices": dashboard_data["security"]["security_practices"],
            "dependency_vulnerabilities": dashboard_data["security"]["dependency_vulnerabilities"],
            "compliance_standards": dashboard_data["security"]["compliance_standards"],
            
            # Recommendations data
            "top_recommendations": dashboard_data["recommendations"]["top_recommendations"],
            "critical_high_roi_count": dashboard_data["recommendations"]["critical_high_roi_count"],
            "important_medium_roi_count": dashboard_data["recommendations"]["important_medium_roi_count"],
            "optional_low_roi_count": dashboard_data["recommendations"]["optional_low_roi_count"],
            "deferred_count": dashboard_data["recommendations"]["deferred_count"],
            "recommendation_categories": dashboard_data["recommendations"]["categories"],
            "quick_wins": dashboard_data["recommendations"]["quick_wins"],
            "total_debt_hours": dashboard_data["recommendations"]["total_debt_hours"],
            "debt_ratio": dashboard_data["recommendations"]["debt_ratio"],
            "estimated_payoff_weeks": dashboard_data["recommendations"]["estimated_payoff_weeks"],
            "refactoring_phases": dashboard_data["recommendations"]["refactoring_phases"],
            
            # UML data
            "uml_diagram_svg": dashboard_data["uml"]["svg"],
            "uml_stats": dashboard_data["uml"]["stats"],
            "uml_error": dashboard_data["uml"]["error"],
            
            # Serialized data for JavaScript
            "dashboard_data": json.dumps(dashboard_data, indent=2)
        }
        
        # Render template
        html_content = template.render(**context)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        
        return output_path
    
    def _gather_dashboard_data(self) -> Dict[str, Any]:
        """
        Gather all data needed for dashboard rendering.
        
        Returns:
            Dictionary containing all dashboard data organized by tab
        """
        # Generate UML diagram during dashboard rendering
        uml_data = self._generate_uml_diagram()
        
        return {
            "overview": self.overview_use_case.execute(),
            "architecture": self.architecture_use_case.execute(),
            "quality": self.quality_use_case.execute(),
            "security": self.security_use_case.execute(),
            "recommendations": self.recommendations_use_case.execute(),
            "uml": uml_data
        }
    
    def _generate_uml_diagram(self) -> Dict[str, Any]:
        """
        Generate UML diagram for the project.
        
        Returns:
            Dictionary with SVG diagram and statistics
        """
        try:
            svg_content, stats = render_uml_for_project(
                project_path=str(self.project_path),
                title=f"{self.project_path.name} Architecture",
                exclude_patterns=['test_', '__pycache__', '.venv', 'site-packages', 'dist']
            )
            
            return {
                'svg': svg_content,
                'stats': stats,
                'error': None
            }
        except Exception as e:
            return {
                'svg': None,
                'stats': {},
                'error': str(e)
            }
    
    def _get_health_category(self, score: float) -> str:
        """Get health category from score."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        elif score >= 20:
            return "poor"
        else:
            return "critical"
    
    def _get_health_label(self, score: float) -> str:
        """Get human-readable health label."""
        if score >= 80:
            return "Excellent Health"
        elif score >= 60:
            return "Good Health"
        elif score >= 40:
            return "Fair Health"
        elif score >= 20:
            return "Poor Health"
        else:
            return "Critical Issues"
