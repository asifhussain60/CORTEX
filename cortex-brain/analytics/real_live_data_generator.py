"""
Real Live Data Dashboard Generator

Generates interactive Chart.js dashboards from analytics databases for MkDocs documentation.

Features:
    - Conditional data detection (only generates if data exists)
    - Per-application dashboards with metrics trends
    - Aggregate cross-application statistics
    - Chart.js visualizations (line charts, bar charts, gauges)
    - Static chart images for PDF export
    - Smart navigation injection (hidden if no data)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "cortex-brain"))

from analytics.analytics_db_manager import AnalyticsDBManager
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RealLiveDataGenerator:
    """
    Generates Real Live Data dashboards from analytics databases.
    
    Workflow:
        1. Detect analytics databases (per-app + aggregate)
        2. Query latest metrics for each application
        3. Generate Chart.js HTML templates
        4. Create dashboard pages in docs/real-live-data/
        5. Return navigation structure if data exists
    """
    
    def __init__(self, analytics_root: Path, docs_output_dir: Path):
        """
        Initialize Real Live Data generator.
        
        Args:
            analytics_root: Path to cortex-brain/analytics/
            docs_output_dir: Path to docs/ directory for output
        """
        self.analytics_root = Path(analytics_root)
        self.docs_output_dir = Path(docs_output_dir)
        self.db_manager = AnalyticsDBManager(self.analytics_root)
        
        # Output directories
        self.dashboard_dir = self.docs_output_dir / "real-live-data"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    def has_data(self) -> bool:
        """
        Check if any analytics data exists.
        
        Returns:
            True if at least one feedback report exists, False otherwise
        """
        try:
            # Check per-app databases
            per_app_dir = self.analytics_root / "per-app"
            if per_app_dir.exists():
                for app_dir in per_app_dir.iterdir():
                    if app_dir.is_dir():
                        db_file = app_dir / "metrics.db"
                        if db_file.exists():
                            with self.db_manager.get_connection(app_name=app_dir.name) as conn:
                                cursor = conn.cursor()
                                cursor.execute("SELECT COUNT(*) FROM feedback_reports")
                                count = cursor.fetchone()[0]
                                if count > 0:
                                    return True
            
            # Check aggregate database
            aggregate_db = self.analytics_root / "aggregate" / "cross-app-metrics.db"
            if aggregate_db.exists():
                with self.db_manager.get_connection(aggregate=True) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM feedback_reports")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        return True
            
            return False
        
        except Exception as e:
            logger.warning(f"Error checking for analytics data: {e}")
            return False
    
    def get_applications(self) -> List[str]:
        """
        Get list of applications with analytics data.
        
        Returns:
            List of application names
        """
        apps = []
        per_app_dir = self.analytics_root / "per-app"
        
        if per_app_dir.exists():
            for app_dir in per_app_dir.iterdir():
                if app_dir.is_dir():
                    db_file = app_dir / "metrics.db"
                    if db_file.exists():
                        try:
                            with self.db_manager.get_connection(app_name=app_dir.name) as conn:
                                cursor = conn.cursor()
                                cursor.execute("SELECT COUNT(*) FROM feedback_reports")
                                count = cursor.fetchone()[0]
                                if count > 0:
                                    apps.append(app_dir.name)
                        except Exception as e:
                            logger.warning(f"Error reading {app_dir.name} database: {e}")
        
        return sorted(apps)
    
    def generate_app_dashboard(self, app_name: str) -> Optional[Path]:
        """
        Generate dashboard page for a specific application.
        
        Args:
            app_name: Application name
        
        Returns:
            Path to generated dashboard file, or None if generation failed
        """
        try:
            # Query latest metrics
            latest = self.db_manager.get_latest_metrics(app_name)
            if not latest:
                logger.warning(f"No metrics found for {app_name}")
                return None
            
            # Query health score
            health_score = self.db_manager.get_health_score(app_name)
            
            # Query critical issues
            issues = self.db_manager.get_critical_issues(app_name)
            
            # Generate HTML
            html_content = self._generate_app_dashboard_html(
                app_name, latest, health_score, issues
            )
            
            # Write to file
            output_file = self.dashboard_dir / f"{app_name.lower().replace(' ', '-')}.md"
            output_file.write_text(html_content, encoding='utf-8')
            
            logger.info(f"Generated dashboard for {app_name}: {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"Error generating dashboard for {app_name}: {e}")
            return None
    
    def generate_aggregate_dashboard(self) -> Optional[Path]:
        """
        Generate aggregate cross-application statistics dashboard.
        
        Returns:
            Path to generated dashboard file, or None if generation failed
        """
        try:
            apps = self.get_applications()
            if not apps:
                return None
            
            # Collect metrics for all apps
            app_metrics = {}
            for app_name in apps:
                metrics = self.db_manager.get_latest_metrics(app_name)
                health = self.db_manager.get_health_score(app_name)
                if metrics:
                    app_metrics[app_name] = {
                        'metrics': metrics,
                        'health_score': health or 0
                    }
            
            # Generate HTML
            html_content = self._generate_aggregate_dashboard_html(app_metrics)
            
            # Write to file
            output_file = self.dashboard_dir / "overview.md"
            output_file.write_text(html_content, encoding='utf-8')
            
            logger.info(f"Generated aggregate dashboard: {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"Error generating aggregate dashboard: {e}")
            return None
    
    def _generate_app_dashboard_html(
        self, 
        app_name: str, 
        metrics: Dict, 
        health_score: Optional[float],
        issues: List[Dict]
    ) -> str:
        """Generate HTML content for application dashboard."""
        
        # Extract metrics safely
        test_coverage = metrics.get('tdd_coverage', 0) or 0
        build_success = metrics.get('build_success_rate', 0) or 0
        sprint_velocity = metrics.get('sprint_velocity', 0) or 0
        security_vulns = metrics.get('security_vulnerabilities', 0) or 0
        
        html = f"""# {app_name} - Real Live Data

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Health Score

<div style="text-align: center; margin: 20px 0;">
    <div style="font-size: 48px; font-weight: bold; color: {'#22c55e' if (health_score or 0) >= 80 else '#f59e0b' if (health_score or 0) >= 60 else '#ef4444'};">
        {health_score or 0:.1f}/100
    </div>
    <div style="font-size: 14px; color: #64748b; margin-top: 10px;">
        Overall Application Health
    </div>
</div>

## 🎯 Key Metrics

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6;">
        <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Test Coverage</div>
        <div style="font-size: 32px; font-weight: bold; color: #1e293b; margin-top: 8px;">{test_coverage:.1f}%</div>
    </div>
    
    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #22c55e;">
        <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Build Success</div>
        <div style="font-size: 32px; font-weight: bold; color: #1e293b; margin-top: 8px;">{build_success:.1f}%</div>
    </div>
    
    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
        <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Sprint Velocity</div>
        <div style="font-size: 32px; font-weight: bold; color: #1e293b; margin-top: 8px;">{sprint_velocity:.1f}</div>
    </div>
    
    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid {'#ef4444' if security_vulns > 0 else '#22c55e'};">
        <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Security Vulnerabilities</div>
        <div style="font-size: 32px; font-weight: bold; color: #1e293b; margin-top: 8px;">{int(security_vulns)}</div>
    </div>
</div>

## 📈 Trends

<canvas id="trendsChart" style="max-width: 800px; max-height: 400px; margin: 20px auto;"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('trendsChart').getContext('2d');
new Chart(ctx, {{
    type: 'line',
    data: {{
        labels: ['Last Report'],
        datasets: [
            {{
                label: 'Test Coverage (%)',
                data: [{test_coverage}],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4
            }},
            {{
                label: 'Build Success (%)',
                data: [{build_success}],
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                tension: 0.4
            }}
        ]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: true,
        plugins: {{
            title: {{
                display: true,
                text: 'Quality Metrics Trends'
            }},
            legend: {{
                display: true,
                position: 'top'
            }}
        }},
        scales: {{
            y: {{
                beginAtZero: true,
                max: 100,
                ticks: {{
                    callback: function(value) {{
                        return value + '%';
                    }}
                }}
            }}
        }}
    }}
}});
</script>

## ⚠️ Critical Issues

"""
        
        if issues:
            html += "<table>\n<thead>\n<tr><th>Severity</th><th>Category</th><th>Description</th><th>Status</th></tr>\n</thead>\n<tbody>\n"
            for issue in issues:
                severity_emoji = "🔴" if issue['severity'] == 'critical' else "🟠" if issue['severity'] == 'high' else "🟡"
                html += f"<tr><td>{severity_emoji} {issue['severity'].upper()}</td><td>{issue['category']}</td><td>{issue['description']}</td><td>{issue['status']}</td></tr>\n"
            html += "</tbody>\n</table>\n"
        else:
            html += "<div style='padding: 20px; background: #f0fdf4; border-radius: 8px; border-left: 4px solid #22c55e;'>\n"
            html += "✅ <strong>No critical issues reported</strong>\n"
            html += "</div>\n"
        
        html += f"""
---

**Data Source:** Analytics Database (cortex-brain/analytics/per-app/{app_name}/metrics.db)  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return html
    
    def _generate_aggregate_dashboard_html(self, app_metrics: Dict[str, Dict]) -> str:
        """Generate HTML content for aggregate dashboard."""
        
        html = f"""# Real Live Data - Overview

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🌐 Cross-Application Statistics

<div style="text-align: center; margin: 30px 0;">
    <div style="font-size: 18px; color: #64748b;">
        Tracking <strong>{len(app_metrics)}</strong> applications
    </div>
</div>

## 📊 Application Health Comparison

<canvas id="healthComparisonChart" style="max-width: 800px; max-height: 400px; margin: 20px auto;"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('healthComparisonChart').getContext('2d');
new Chart(ctx, {{
    type: 'bar',
    data: {{
        labels: {json.dumps([app for app in app_metrics.keys()])},
        datasets: [{{
            label: 'Health Score',
            data: {json.dumps([app_metrics[app]['health_score'] for app in app_metrics.keys()])},
            backgroundColor: {json.dumps([
                '#22c55e' if app_metrics[app]['health_score'] >= 80 else 
                '#f59e0b' if app_metrics[app]['health_score'] >= 60 else 
                '#ef4444' 
                for app in app_metrics.keys()
            ])},
            borderColor: '#1e293b',
            borderWidth: 1
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: true,
        plugins: {{
            title: {{
                display: true,
                text: 'Application Health Scores'
            }},
            legend: {{
                display: false
            }}
        }},
        scales: {{
            y: {{
                beginAtZero: true,
                max: 100,
                ticks: {{
                    callback: function(value) {{
                        return value + '/100';
                    }}
                }}
            }}
        }}
    }}
}});
</script>

## 📋 Application Summary

<table>
<thead>
<tr>
    <th>Application</th>
    <th>Health Score</th>
    <th>Test Coverage</th>
    <th>Build Success</th>
    <th>Sprint Velocity</th>
</tr>
</thead>
<tbody>
"""
        
        for app_name, data in sorted(app_metrics.items()):
            metrics = data['metrics']
            health = data['health_score']
            
            health_emoji = "🟢" if health >= 80 else "🟡" if health >= 60 else "🔴"
            
            html += f"""<tr>
    <td><a href="{app_name.lower().replace(' ', '-')}/">{app_name}</a></td>
    <td>{health_emoji} {health:.1f}/100</td>
    <td>{metrics.get('tdd_coverage', 0) or 0:.1f}%</td>
    <td>{metrics.get('build_success_rate', 0) or 0:.1f}%</td>
    <td>{metrics.get('sprint_velocity', 0) or 0:.1f}</td>
</tr>
"""
        
        html += """</tbody>
</table>

---

**Data Source:** Analytics Databases (cortex-brain/analytics/)  
**Generated:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
"""
        
        return html
    
    def generate_all_dashboards(self) -> Dict[str, List[Path]]:
        """
        Generate all dashboards (per-app + aggregate).
        
        Returns:
            Dictionary with 'app_dashboards' and 'aggregate_dashboard' paths
        """
        result = {
            'app_dashboards': [],
            'aggregate_dashboard': None
        }
        
        # Generate per-app dashboards
        apps = self.get_applications()
        for app_name in apps:
            dashboard_path = self.generate_app_dashboard(app_name)
            if dashboard_path:
                result['app_dashboards'].append(dashboard_path)
        
        # Generate aggregate dashboard
        if apps:
            aggregate_path = self.generate_aggregate_dashboard()
            if aggregate_path:
                result['aggregate_dashboard'] = aggregate_path
        
        return result
    
    def get_navigation_structure(self) -> Optional[Dict]:
        """
        Get MkDocs navigation structure for Real Live Data section.
        
        Returns:
            Navigation dict if data exists, None otherwise
        """
        if not self.has_data():
            return None
        
        apps = self.get_applications()
        if not apps:
            return None
        
        nav_structure = {
            'Real Live Data': [
                {'Overview': 'real-live-data/overview.md'}
            ]
        }
        
        # Add per-app links
        for app_name in apps:
            app_file = f"{app_name.lower().replace(' ', '-')}.md"
            nav_structure['Real Live Data'].append({
                app_name: f'real-live-data/{app_file}'
            })
        
        return nav_structure


def main():
    """Test Real Live Data generator."""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    analytics_root = project_root / "cortex-brain" / "analytics"
    docs_output_dir = project_root / "docs"
    
    generator = RealLiveDataGenerator(analytics_root, docs_output_dir)
    
    print("=" * 60)
    print("REAL LIVE DATA GENERATOR - TEST")
    print("=" * 60)
    
    # Check for data
    has_data = generator.has_data()
    print(f"\nData exists: {has_data}")
    
    if has_data:
        apps = generator.get_applications()
        print(f"Applications with data: {apps}")
        
        # Generate dashboards
        print("\nGenerating dashboards...")
        result = generator.generate_all_dashboards()
        
        print(f"\nGenerated {len(result['app_dashboards'])} app dashboards")
        if result['aggregate_dashboard']:
            print(f"Generated aggregate dashboard: {result['aggregate_dashboard']}")
        
        # Get navigation structure
        nav = generator.get_navigation_structure()
        if nav:
            print("\nNavigation structure:")
            print(json.dumps(nav, indent=2))
    else:
        print("\nNo analytics data found. Dashboards will not be generated.")
        print("Navigation link will be hidden in MkDocs.")


if __name__ == "__main__":
    main()
