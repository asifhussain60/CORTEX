"""
Compliance Dashboard Generator for Sprint 2 - Active Compliance Dashboard

Purpose: Generate interactive HTML dashboard from compliance database
Author: Asif Hussain
Created: 2025-11-27
Sprint: 2 of Option B Comprehensive Dashboard Plan

This module generates real-time compliance dashboards showing:
- Overall compliance score
- Rule status by category (compliant, warning, violated)
- Recent protection events
- Auto-refresh JavaScript for live updates

Dashboard displays in VS Code Simple Browser with <50ms query performance.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

try:
    from jinja2 import Environment, FileSystemLoader, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("WARNING: jinja2 not available. Dashboard generation will be limited.")

from src.tier1.compliance_database import ComplianceDatabase


class ComplianceDashboardGenerator:
    """
    Generates interactive HTML compliance dashboards from compliance database.
    
    Features:
    - Real-time rule status visualization
    - Compliance score calculation
    - Recent events timeline
    - Auto-refresh every 30 seconds
    - Visual indicators (🟢🟡🔴)
    """
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize dashboard generator.
        
        Args:
            brain_path: Path to cortex-brain directory (auto-detects if None)
        """
        # Auto-detect cortex-brain path
        if brain_path is None:
            current = Path(__file__).resolve()
            for parent in [current] + list(current.parents):
                candidate = parent / "cortex-brain"
                if candidate.exists() and candidate.is_dir():
                    brain_path = candidate
                    break
            
            if brain_path is None:
                raise FileNotFoundError(
                    "Could not locate cortex-brain directory. "
                    "Please provide brain_path explicitly."
                )
        
        self.brain_path = Path(brain_path)
        self.compliance_db = ComplianceDatabase(brain_path=self.brain_path)
        
        # Template paths
        self.template_dir = self.brain_path / "templates"
        self.output_dir = self.brain_path / "dashboards"
        
        # Ensure directories exist
        self.template_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        if JINJA2_AVAILABLE:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.jinja_env = None
    
    def generate_dashboard(
        self,
        output_filename: str = "compliance-dashboard.html"
    ) -> Path:
        """
        Generate complete compliance dashboard HTML.
        
        Args:
            output_filename: Output filename (default: compliance-dashboard.html)
        
        Returns:
            Path to generated HTML file
        
        Raises:
            FileNotFoundError: If template not found
            RuntimeError: If Jinja2 not available
        """
        if not JINJA2_AVAILABLE:
            raise RuntimeError(
                "Jinja2 is required for dashboard generation. "
                "Install with: pip install jinja2"
            )
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        # Render template
        output_path = self.output_dir / output_filename
        html_content = self._render_template(metrics)
        
        # Write to file
        output_path.write_text(html_content, encoding='utf-8')
        
        return output_path
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate all dashboard metrics from compliance database.
        
        Returns:
            Dict with keys: compliance_score, rule_status, recent_events,
            statistics, generated_at
        """
        # Overall compliance score
        compliance_score = self.compliance_db.get_compliance_score()
        
        # Rule status (all rules with counts)
        rule_status = self.compliance_db.get_compliance_status()
        
        # Recent events (last 20 for dashboard display)
        recent_events = self.compliance_db.get_recent_events(limit=20)
        
        # Statistics (category breakdown, trends)
        statistics = self.compliance_db.get_statistics()
        
        # Group rules by category for organized display
        rules_by_category = self._group_rules_by_category(rule_status)
        
        # Determine overall health status
        health_status = self._determine_health_status(compliance_score)
        
        return {
            'compliance_score': round(compliance_score, 1),
            'health_status': health_status,
            'rule_status': rule_status,
            'rules_by_category': rules_by_category,
            'recent_events': recent_events,
            'statistics': statistics,
            'generated_at': datetime.now().isoformat(),
            'refresh_interval': 30  # seconds
        }
    
    def _group_rules_by_category(
        self,
        rule_status: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group rules by category for organized dashboard display.
        
        Args:
            rule_status: List of rule status dicts from compliance database
        
        Returns:
            Dict mapping category to list of rules
        """
        grouped = {}
        
        for rule in rule_status:
            category = rule.get('category', 'uncategorized')
            
            if category not in grouped:
                grouped[category] = []
            
            # Add visual indicator
            rule['indicator'] = self._get_status_indicator(
                rule['violations'],
                rule['total_checks']
            )
            
            grouped[category].append(rule)
        
        # Sort categories alphabetically
        return dict(sorted(grouped.items()))
    
    def _get_status_indicator(
        self,
        violations: int,
        total_checks: int
    ) -> Dict[str, str]:
        """
        Determine visual status indicator for a rule.
        
        Args:
            violations: Number of violations
            total_checks: Total number of checks
        
        Returns:
            Dict with keys: emoji, status_class, status_text
        """
        if violations == 0:
            return {
                'emoji': '🟢',
                'status_class': 'compliant',
                'status_text': 'Compliant'
            }
        
        if total_checks == 0:
            violation_rate = 0.0
        else:
            violation_rate = violations / total_checks
        
        if violation_rate < 0.10:  # Less than 10% violation rate
            return {
                'emoji': '🟡',
                'status_class': 'warning',
                'status_text': 'Warning'
            }
        else:
            return {
                'emoji': '🔴',
                'status_class': 'violated',
                'status_text': 'Violated'
            }
    
    def _determine_health_status(self, compliance_score: float) -> Dict[str, str]:
        """
        Determine overall system health based on compliance score.
        
        Args:
            compliance_score: Overall compliance percentage (0-100)
        
        Returns:
            Dict with keys: emoji, status_class, status_text
        """
        if compliance_score >= 90.0:
            return {
                'emoji': '🟢',
                'status_class': 'healthy',
                'status_text': 'Healthy'
            }
        elif compliance_score >= 70.0:
            return {
                'emoji': '🟡',
                'status_class': 'warning',
                'status_text': 'Warning'
            }
        else:
            return {
                'emoji': '🔴',
                'status_class': 'critical',
                'status_text': 'Critical'
            }
    
    def _render_template(self, metrics: Dict[str, Any]) -> str:
        """
        Render dashboard HTML using Jinja2 template.
        
        Args:
            metrics: Dashboard metrics from _calculate_metrics()
        
        Returns:
            Rendered HTML string
        
        Raises:
            FileNotFoundError: If template file not found
        """
        template_path = self.template_dir / "compliance-dashboard.html.j2"
        
        if not template_path.exists():
            raise FileNotFoundError(
                f"Dashboard template not found: {template_path}\n"
                f"Expected location: cortex-brain/templates/compliance-dashboard.html.j2"
            )
        
        # Load template
        template = self.jinja_env.get_template("compliance-dashboard.html.j2")
        
        # Render with metrics
        html_content = template.render(**metrics)
        
        return html_content
    
    def generate_dashboard_json(
        self,
        output_filename: str = "compliance-dashboard.json"
    ) -> Path:
        """
        Generate JSON version of dashboard data (for API consumption).
        
        Args:
            output_filename: Output filename (default: compliance-dashboard.json)
        
        Returns:
            Path to generated JSON file
        """
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        # Write to JSON file
        output_path = self.output_dir / output_filename
        
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        return output_path
    
    def get_dashboard_url(self, filename: str = "compliance-dashboard.html") -> str:
        """
        Get VS Code Simple Browser compatible URL for dashboard.
        
        Args:
            filename: Dashboard filename
        
        Returns:
            file:// URL for VS Code Simple Browser
        """
        dashboard_path = self.output_dir / filename
        return f"file://{dashboard_path.resolve()}"
    
    def refresh_dashboard(self) -> Path:
        """
        Quick refresh: regenerate dashboard with latest data.
        
        Returns:
            Path to refreshed dashboard
        """
        return self.generate_dashboard()


# Convenience functions for common operations

def generate_compliance_dashboard(
    brain_path: Optional[Path] = None,
    output_filename: str = "compliance-dashboard.html"
) -> Path:
    """
    Convenience function: Generate compliance dashboard.
    
    Args:
        brain_path: Path to cortex-brain (auto-detects if None)
        output_filename: Output filename
    
    Returns:
        Path to generated dashboard
    """
    generator = ComplianceDashboardGenerator(brain_path=brain_path)
    return generator.generate_dashboard(output_filename=output_filename)


def get_dashboard_metrics(brain_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience function: Get dashboard metrics without rendering HTML.
    
    Args:
        brain_path: Path to cortex-brain (auto-detects if None)
    
    Returns:
        Dashboard metrics dictionary
    """
    generator = ComplianceDashboardGenerator(brain_path=brain_path)
    return generator._calculate_metrics()


def open_compliance_dashboard(brain_path: Optional[Path] = None) -> str:
    """
    Convenience function: Generate dashboard and return VS Code URL.
    
    Args:
        brain_path: Path to cortex-brain (auto-detects if None)
    
    Returns:
        file:// URL for VS Code Simple Browser
    """
    generator = ComplianceDashboardGenerator(brain_path=brain_path)
    dashboard_path = generator.generate_dashboard()
    return generator.get_dashboard_url()


if __name__ == "__main__":
    # CLI usage for testing
    import sys
    
    print("CORTEX Compliance Dashboard Generator")
    print("=" * 50)
    
    try:
        generator = ComplianceDashboardGenerator()
        
        # Generate dashboard
        print("\nGenerating dashboard...")
        dashboard_path = generator.generate_dashboard()
        print(f"✅ Dashboard generated: {dashboard_path}")
        
        # Generate JSON version
        json_path = generator.generate_dashboard_json()
        print(f"✅ JSON data generated: {json_path}")
        
        # Get metrics
        metrics = generator._calculate_metrics()
        print(f"\n📊 Compliance Score: {metrics['compliance_score']}%")
        print(f"🏥 Health Status: {metrics['health_status']['emoji']} {metrics['health_status']['status_text']}")
        print(f"📋 Total Rules: {len(metrics['rule_status'])}")
        print(f"📅 Recent Events: {len(metrics['recent_events'])}")
        
        # Show URL
        url = generator.get_dashboard_url()
        print(f"\n🌐 Open in VS Code Simple Browser:")
        print(f"   {url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
