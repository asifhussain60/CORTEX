"""
CORTEX 3.0 - EPMO Health Dashboard
==================================

Web-based dashboard for EPMO health monitoring and remediation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from .validation_suite import EPMOHealthValidator, ValidationResult, HealthDimension
from .remediation_engine import RemediationEngine


class HealthDashboard:
    """Web-based dashboard for EPMO health monitoring."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator = EPMOHealthValidator()
        self.remediation_engine = RemediationEngine()
        
    def generate_dashboard_data(self, epmo_path: Path) -> Dict[str, Any]:
        """Generate comprehensive dashboard data."""
        # Run health validation
        health_report = self.validator.validate_epmo_health(epmo_path, self.project_root)
        
        # Generate remediation plan
        all_results = []
        for dimension_results in health_report['dimension_scores'].values():
            all_results.extend(dimension_results.get('results', []))
        
        remediation_plan = self.remediation_engine.generate_remediation_plan(all_results)
        effort_estimate = self.remediation_engine.estimate_total_effort(remediation_plan)
        
        # Compile dashboard data
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'epmo_path': str(epmo_path),
            'overall_score': health_report['overall_score'],
            'health_grade': self._calculate_health_grade(health_report['overall_score']),
            'dimension_breakdown': self._format_dimension_breakdown(health_report),
            'remediation_plan': self._format_remediation_plan(remediation_plan),
            'effort_estimate': effort_estimate,
            'historical_trends': self._get_historical_trends(epmo_path),
            'actionable_insights': self._generate_insights(health_report, remediation_plan)
        }
        
        return dashboard_data
    
    def generate_html_dashboard(self, epmo_path: Path, output_path: Path) -> bool:
        """Generate HTML dashboard file."""
        try:
            dashboard_data = self.generate_dashboard_data(epmo_path)
            html_content = self._generate_html_template(dashboard_data)
            
            with open(output_path, 'w') as f:
                f.write(html_content)
            
            return True
        except Exception:
            return False
    
    def update_historical_data(self, epmo_path: Path, health_report: Dict[str, Any]) -> None:
        """Update historical health data for trending."""
        history_file = self.project_root / 'cortex-brain' / 'health-reports' / f'{epmo_path.name}_history.json'
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        # Add new entry
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': health_report['overall_score'],
            'dimension_scores': {
                dim_name: scores['score'] 
                for dim_name, scores in health_report['dimension_scores'].items()
            }
        }
        
        history.append(history_entry)
        
        # Keep only last 30 entries
        history = history[-30:]
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def _calculate_health_grade(self, score: float) -> str:
        """Calculate letter grade from health score."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _format_dimension_breakdown(self, health_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format dimension scores for dashboard display."""
        breakdown = []
        
        for dimension, scores in health_report['dimension_scores'].items():
            breakdown.append({
                'dimension': dimension.value,
                'score': scores['score'],
                'weight': scores['weight'],
                'weighted_score': scores['weighted_score'],
                'status': 'Excellent' if scores['score'] >= 85 else
                         'Good' if scores['score'] >= 70 else
                         'Fair' if scores['score'] >= 55 else 'Poor',
                'result_count': len(scores.get('results', []))
            })
        
        return sorted(breakdown, key=lambda x: x['weighted_score'], reverse=True)
    
    def _format_remediation_plan(self, remediation_plan: List) -> List[Dict[str, Any]]:
        """Format remediation plan for dashboard display."""
        formatted_plan = []
        
        for action in remediation_plan:
            formatted_plan.append({
                'action_type': action.action_type,
                'description': action.description,
                'auto_fixable': action.auto_fixable,
                'estimated_hours': action.estimated_effort_minutes / 60,
                'priority': 'High' if action.priority == 1 else
                           'Medium' if action.priority == 2 else 'Low'
            })
        
        return formatted_plan
    
    def _get_historical_trends(self, epmo_path: Path) -> List[Dict[str, Any]]:
        """Get historical health trends."""
        history_file = self.project_root / 'cortex-brain' / 'health-reports' / f'{epmo_path.name}_history.json'
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _generate_insights(self, health_report: Dict[str, Any], remediation_plan: List) -> List[str]:
        """Generate actionable insights from health data."""
        insights = []
        overall_score = health_report['overall_score']
        
        # Overall health insight
        if overall_score >= 85:
            insights.append("🎉 Excellent EPMO health! Focus on maintaining current quality standards.")
        elif overall_score >= 70:
            insights.append("✅ Good EPMO health with room for targeted improvements.")
        else:
            insights.append("⚠️ EPMO health needs attention. Prioritize high-impact remediation actions.")
        
        # Dimension-specific insights
        dimension_scores = health_report['dimension_scores']
        
        # Find weakest dimension
        weakest_dim = min(dimension_scores.items(), key=lambda x: x[1]['weighted_score'])
        insights.append(f"🎯 Primary focus area: {weakest_dim[0].value} (score: {weakest_dim[1]['score']:.1f})")
        
        # Auto-fix opportunities
        auto_fixable_count = sum(1 for action in remediation_plan if action.auto_fixable)
        if auto_fixable_count > 0:
            insights.append(f"🔧 {auto_fixable_count} issues can be auto-fixed to improve health score quickly.")
        
        # Effort estimate insight
        if remediation_plan:
            total_hours = sum(action.estimated_effort_minutes for action in remediation_plan) / 60
            insights.append(f"📊 Estimated remediation effort: {total_hours:.1f} hours across {len(remediation_plan)} actions.")
        
        return insights
    
    def _generate_html_template(self, data: Dict[str, Any]) -> str:
        """Generate HTML dashboard template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX 3.0 - EPMO Health Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; margin-bottom: 5px; }}
        .header p {{ color: #7f8c8d; margin: 0; }}
        .dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .score-card {{ text-align: center; }}
        .score-number {{ font-size: 3em; font-weight: bold; color: {self._get_score_color(data['overall_score'])}; }}
        .score-grade {{ font-size: 1.5em; color: #7f8c8d; }}
        .dimension {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #ecf0f1; }}
        .dimension:last-child {{ border-bottom: none; }}
        .dimension-name {{ font-weight: 500; }}
        .dimension-score {{ font-weight: bold; color: #2c3e50; }}
        .remediation-item {{ padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #3498db; }}
        .auto-fix {{ border-left-color: #27ae60; }}
        .insights {{ grid-column: 1 / -1; }}
        .insight {{ padding: 10px; margin: 5px 0; background: #e8f4fd; border-radius: 4px; border-left: 4px solid #3498db; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CORTEX 3.0 - EPMO Health Dashboard</h1>
        <p>Generated on {data['timestamp'][:19]} for {data['epmo_path']}</p>
    </div>
    
    <div class="dashboard">
        <div class="card score-card">
            <h2>Overall Health Score</h2>
            <div class="score-number">{data['overall_score']:.1f}</div>
            <div class="score-grade">Grade: {data['health_grade']}</div>
        </div>
        
        <div class="card">
            <h2>Dimension Breakdown</h2>
            {''.join(f'<div class="dimension"><span class="dimension-name">{dim["dimension"]}</span><span class="dimension-score">{dim["score"]:.1f}</span></div>' for dim in data['dimension_breakdown'])}
        </div>
        
        <div class="card">
            <h2>Remediation Plan</h2>
            <p><strong>Total Actions:</strong> {len(data['remediation_plan'])}</p>
            <p><strong>Estimated Effort:</strong> {data['effort_estimate']['total_hours']:.1f} hours</p>
            {''.join(f'<div class="remediation-item {"auto-fix" if action["auto_fixable"] else ""}"><strong>{action["priority"]} Priority:</strong> {action["description"]} <em>({action["estimated_hours"]:.1f}h)</em></div>' for action in data['remediation_plan'][:5])}
        </div>
        
        <div class="card">
            <h2>Effort Breakdown</h2>
            <p><strong>Auto-fixable:</strong> {data['effort_estimate']['auto_fixable_actions']} actions</p>
            <p><strong>Manual:</strong> {data['effort_estimate']['manual_actions']} actions</p>
            <p><strong>Estimated Completion:</strong> {data['effort_estimate']['estimated_completion']}</p>
        </div>
        
        <div class="card insights">
            <h2>Actionable Insights</h2>
            {''.join(f'<div class="insight">{insight}</div>' for insight in data['actionable_insights'])}
        </div>
    </div>
</body>
</html>"""
    
    def _get_score_color(self, score: float) -> str:
        """Get color for score display."""
        if score >= 85:
            return '#27ae60'  # Green
        elif score >= 70:
            return '#f39c12'  # Orange
        else:
            return '#e74c3c'  # Red