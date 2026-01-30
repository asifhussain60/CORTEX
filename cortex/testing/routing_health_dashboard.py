"""
Phase 8.6: Routing Health Dashboard

Interactive HTML dashboard for monitoring Phase 8 routing system health.
Displays real-time metrics, trends, and actionable insights.

AC-ID: AC-PHASE-8.6-02 (Task VERIFY-002)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30

Usage:
    python -m cortex.testing.routing_health_dashboard
    # Opens browser at http://localhost:8080
"""

from typing import Dict, Any, List
from pathlib import Path
import json
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from cortex.testing.routing_health_checks import RoutingHealthChecker
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class DashboardDataGenerator:
    """
    Generates dashboard data from health checks.
    
    Converts RoutingHealthChecker results into JSON for dashboard visualization.
    """
    
    def __init__(self) -> None:
        """Initialize dashboard data generator."""
        self.logger = EnhancedAuditLogger.instance()
        self.checker = RoutingHealthChecker()
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate dashboard data.
        
        AC-PHASE-8.6-02: Dashboard data generation
        
        Returns:
            Dict: Dashboard data with metrics, trends, alerts
        """
        # Run health checks
        results = self.checker.run_all_checks()
        
        # Calculate overall health score
        total_score = sum(r.score for r in results)
        health_score = total_score / len(results) if results else 0.0
        
        # Categorize results
        passed = [r for r in results if r.status.value == "PASSED"]
        failed = [r for r in results if r.status.value == "FAILED"]
        warnings = [r for r in results if r.status.value == "WARNING"]
        
        # Generate metrics
        metrics = {
            "overall_health": health_score,
            "total_checks": len(results),
            "passed": len(passed),
            "failed": len(failed),
            "warnings": len(warnings),
            "timestamp": time.time(),
        }
        
        # Generate check details
        checks = [
            {
                "id": r.check_id,
                "name": r.check_name,
                "status": r.status.value,
                "score": r.score,
                "details": r.details,
                "remediation": r.remediation,
                "evidence": r.evidence,
            }
            for r in results
        ]
        
        # Generate alerts
        alerts = [
            {
                "severity": "error" if r.status.value == "FAILED" else "warning",
                "check": r.check_name,
                "message": r.details,
                "remediation": r.remediation,
            }
            for r in results if r.status.value != "PASSED"
        ]
        
        return {
            "metrics": metrics,
            "checks": checks,
            "alerts": alerts,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def save_dashboard_html(self, output_path: Path) -> None:
        """
        Save dashboard HTML file.
        
        Args:
            output_path: Output file path
        """
        data = self.generate_dashboard_data()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Routing Health Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .health-score {{
            color: #10b981;
        }}
        .failed-count {{
            color: #ef4444;
        }}
        .warning-count {{
            color: #f59e0b;
        }}
        .checks-section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .check-item {{
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #ccc;
            background: #f9fafb;
            border-radius: 5px;
        }}
        .check-item.passed {{
            border-color: #10b981;
        }}
        .check-item.failed {{
            border-color: #ef4444;
        }}
        .check-item.warning {{
            border-color: #f59e0b;
        }}
        .check-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .check-name {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .check-score {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        .check-details {{
            color: #666;
            margin: 5px 0;
        }}
        .remediation {{
            background: #fef3c7;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .alerts-section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .alert-item {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .alert-item.error {{
            background: #fee2e2;
            border-left: 4px solid #ef4444;
        }}
        .alert-item.warning {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
        }}
        .timestamp {{
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 CORTEX Routing Health Dashboard</h1>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Overall Health</div>
                <div class="metric-value health-score">{data['metrics']['overall_health']:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Checks</div>
                <div class="metric-value">{data['metrics']['total_checks']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Passed</div>
                <div class="metric-value" style="color: #10b981;">{data['metrics']['passed']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Failed</div>
                <div class="metric-value failed-count">{data['metrics']['failed']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Warnings</div>
                <div class="metric-value warning-count">{data['metrics']['warnings']}</div>
            </div>
        </div>
        
        <div class="checks-section">
            <h2 style="margin-bottom: 20px;">Health Checks</h2>
            {"".join([
                f'''
                <div class="check-item {check['status'].lower()}">
                    <div class="check-header">
                        <span class="check-name">{check['id']}: {check['name']}</span>
                        <span class="check-score">{check['score']:.1f}/100</span>
                    </div>
                    <div class="check-details">{check['details']}</div>
                    {f'<div class="remediation"><strong>Remediation:</strong> {check["remediation"]}</div>' if check['status'] != 'PASSED' else ''}
                </div>
                '''
                for check in data['checks']
            ])}
        </div>
        
        {f'''
        <div class="alerts-section">
            <h2 style="margin-bottom: 20px;">Active Alerts</h2>
            {"".join([
                f'''
                <div class="alert-item {alert['severity']}">
                    <div style="font-weight: bold; margin-bottom: 5px;">{alert['check']}</div>
                    <div>{alert['message']}</div>
                    <div style="margin-top: 10px; font-size: 0.9em;"><strong>Fix:</strong> {alert['remediation']}</div>
                </div>
                '''
                for alert in data['alerts']
            ])}
        </div>
        ''' if data['alerts'] else ''}
        
        <div class="timestamp">
            Generated: {data['generated_at']}
        </div>
    </div>
</body>
</html>"""
        
        output_path.write_text(html)
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.6-02",
            operation="DASHBOARD_HTML_SAVE",
            success=True,
            details={"output_path": str(output_path)},
        )


def main():
    """Main entry point for dashboard generation."""
    generator = DashboardDataGenerator()
    
    # Save dashboard HTML
    output_path = Path("routing_health_dashboard.html")
    generator.save_dashboard_html(output_path)
    
    print(f"✅ Dashboard generated: {output_path}")
    print(f"📊 Open in browser: file://{output_path.absolute()}")


if __name__ == "__main__":
    main()
