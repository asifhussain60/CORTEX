"""Routing Health Dashboard - generates HTML dashboard for health monitoring."""

import time
from pathlib import Path
from typing import Any, Dict, List

from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.testing.routing_health_checks import RoutingHealthChecker


class DashboardDataGenerator:
    """Generates dashboard data from health checks."""

    def __init__(self) -> None:
        self.logger = EnhancedAuditLogger.instance()
        self.checker = RoutingHealthChecker()

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate dashboard data from health checks."""
        results = self.checker.run_all_checks()
        total_score = sum(r.score for r in results)
        health_score = total_score / len(results) if results else 0.0

        passed = [r for r in results if r.status.value == "PASSED"]
        failed = [r for r in results if r.status.value == "FAILED"]
        warnings = [r for r in results if r.status.value == "WARNING"]

        return {
            "metrics": {
                "overall_health": health_score,
                "total_checks": len(results),
                "passed": len(passed),
                "failed": len(failed),
                "warnings": len(warnings),
                "timestamp": time.time(),
            },
            "checks": [
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
            ],
            "alerts": [
                {
                    "severity": "error" if r.status.value == "FAILED" else "warning",
                    "check": r.check_name,
                    "message": r.details,
                    "remediation": r.remediation,
                }
                for r in results if r.status.value != "PASSED"
            ],
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def save_dashboard_html(self, output_path: Path) -> None:
        """Save dashboard HTML file."""
        data = self.generate_dashboard_data()
        m = data["metrics"]
        
        checks_html = ""
        for c in data["checks"]:
            rem = ""
            if c["status"] != "PASSED":
                rem = '<div class="remediation"><strong>Fix:</strong> ' + c["remediation"] + '</div>'
            checks_html += (
                '<div class="check-item ' + c["status"].lower() + '">'
                '<div class="check-header">'
                '<span class="check-name">' + c["id"] + ': ' + c["name"] + '</span>'
                '<span class="check-score">' + str(round(c["score"], 1)) + '/100</span>'
                '</div>'
                '<div class="check-details">' + c["details"] + '</div>'
                + rem + '</div>'
            )
        
        alerts_html = ""
        if data["alerts"]:
            alert_items = ""
            for a in data["alerts"]:
                alert_items += (
                    '<div class="alert-item ' + a["severity"] + '">'
                    '<div style="font-weight:bold">' + a["check"] + '</div>'
                    '<div>' + a["message"] + '</div>'
                    '<div style="margin-top:10px"><strong>Fix:</strong> ' + a["remediation"] + '</div>'
                    '</div>'
                )
            alerts_html = '<div class="alerts-section"><h2>Alerts</h2>' + alert_items + '</div>'

        html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Health Dashboard</title>
<style>
body{font-family:sans-serif;background:#667eea;padding:20px;color:#333}
.container{max-width:1200px;margin:0 auto}
h1{text-align:center;color:white;margin-bottom:30px}
.metrics-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:20px;margin-bottom:30px}
.metric-card{background:white;padding:20px;border-radius:10px;text-align:center}
.metric-value{font-size:2em;font-weight:bold;margin:10px 0}
.checks-section,.alerts-section{background:white;padding:30px;border-radius:10px;margin-bottom:30px}
.check-item{padding:15px;margin:10px 0;border-left:4px solid #ccc;background:#f9f9f9}
.check-item.passed{border-color:#10b981}
.check-item.failed{border-color:#ef4444}
.check-item.warning{border-color:#f59e0b}
.check-header{display:flex;justify-content:space-between;margin-bottom:10px}
.check-name{font-weight:bold}
.remediation{background:#fef3c7;padding:10px;margin-top:10px;border-radius:5px}
.alert-item{padding:15px;margin:10px 0;border-radius:5px}
.alert-item.error{background:#fee2e2;border-left:4px solid #ef4444}
.alert-item.warning{background:#fef3c7;border-left:4px solid #f59e0b}
.timestamp{text-align:center;color:white;margin-top:20px}
</style></head><body>
<div class="container">
<h1>CORTEX Health Dashboard</h1>
<div class="metrics-grid">
<div class="metric-card"><div class="metric-label">Health</div><div class="metric-value" style="color:#10b981">""" + str(round(m["overall_health"], 1)) + """%</div></div>
<div class="metric-card"><div class="metric-label">Total</div><div class="metric-value">""" + str(m["total_checks"]) + """</div></div>
<div class="metric-card"><div class="metric-label">Passed</div><div class="metric-value" style="color:#10b981">""" + str(m["passed"]) + """</div></div>
<div class="metric-card"><div class="metric-label">Failed</div><div class="metric-value" style="color:#ef4444">""" + str(m["failed"]) + """</div></div>
<div class="metric-card"><div class="metric-label">Warnings</div><div class="metric-value" style="color:#f59e0b">""" + str(m["warnings"]) + """</div></div>
</div>
<div class="checks-section"><h2>Health Checks</h2>""" + checks_html + """</div>
""" + alerts_html + """
<div class="timestamp">Generated: """ + data["generated_at"] + """</div>
</div></body></html>"""

        output_path.write_text(html)
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.6-02",
            operation="DASHBOARD_HTML_SAVE",
            success=True,
            details={"output_path": str(output_path)},
        )


def main() -> None:
    """Generate dashboard."""
    generator = DashboardDataGenerator()
    output_path = Path("routing_health_dashboard.html")
    generator.save_dashboard_html(output_path)
    print("Dashboard generated: " + str(output_path))


if __name__ == "__main__":
    main()
