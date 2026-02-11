"""
Compliance Governance Dashboard

AC_START: AC-PHASE60.0-S3-002
Authority: phase-60-enterprise-pattern-registry.yaml Stage 3
Purpose: Provide governance dashboard for compliance tracking
         - Dashboard generation (HTML)
         - Compliance metrics and visualization
         - Policy status overview
         - Violation tracking

Tests Target: 8 tests
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from cortex.mcp.tools.policy_tools import get_policy_mcp_tools


class ComplianceDashboard:
    """Generator for compliance governance dashboard."""

    def __init__(self, output_path: Path = None):
        """Initialize dashboard generator.

        Args:
            output_path: Path to write dashboard HTML (optional)
        """
        self.output_path = output_path or Path("compliance-dashboard.html")
        self.mcp_tools = get_policy_mcp_tools()

    def generate_dashboard(self) -> str:
        """Generate compliance dashboard HTML.

        Returns:
            HTML content for dashboard
        """
        # Get data
        policies_data = self.mcp_tools.cortex_list_policies()
        reports_data = self.mcp_tools.cortex_get_compliance_report()

        policies = policies_data.get('policies', [])
        reports = reports_data.get('reports', [])

        # Calculate metrics
        total_policies = len(policies)
        total_evaluations = reports_data.get('total_evaluations', 0)

        if reports:
            compliant_evaluations = sum(1 for r in reports if r['compliant'])
            compliance_rate = (compliant_evaluations / len(reports)) * 100
            avg_score = sum(r['score'] for r in reports) / len(reports)
        else:
            compliance_rate = 0
            avg_score = 0

        # Generate HTML
        html = self._generate_html(
            policies,
            reports,
            total_policies,
            total_evaluations,
            compliance_rate,
            avg_score
        )

        return html

    def save_dashboard(self) -> Path:
        """Generate and save dashboard to file.

        Returns:
            Path to generated dashboard file
        """
        html = self.generate_dashboard()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return self.output_path

    def _generate_html(
        self,
        policies: List[Dict[str, Any]],
        reports: List[Dict[str, Any]],
        total_policies: int,
        total_evaluations: int,
        compliance_rate: float,
        avg_score: float
    ) -> str:
        """Generate HTML dashboard content.

        Args:
            policies: List of policies
            reports: List of evaluation reports
            total_policies: Total policy count
            total_evaluations: Total evaluation count
            compliance_rate: Compliance percentage
            avg_score: Average compliance score

        Returns:
            HTML string
        """

        # Policy cards HTML
        policy_cards = ""
        for policy in policies:
            level_color = self._get_level_color(policy.get('level', 'warning'))
            policy_cards += f"""
            <div class="policy-card" style="border-left: 4px solid {level_color};">
                <h4>{policy.get('name', 'Unknown')}</h4>
                <p class="policy-id">ID: {policy.get('id', 'N/A')}</p>
                <p class="policy-level">Level: <span style="color: {level_color};">{policy.get('level', 'unknown').upper()}</span></p>
                <p class="policy-rules">Rules: {policy.get('rule_count', 0)}</p>
                <p class="policy-frameworks">Frameworks: {', '.join(policy.get('frameworks', []))}</p>
            </div>
            """

        # Recent reports HTML
        recent_reports = ""
        for report in reports[:10]:  # Show latest 10
            status_color = '#10b981' if report.get('compliant') else '#ef4444'
            status_text = 'Compliant' if report.get('compliant') else 'Non-Compliant'

            recent_reports += f"""
            <tr>
                <td>{report.get('policy_id', 'N/A')}</td>
                <td style="color: {status_color};">{status_text}</td>
                <td>{round(report.get('score', 0), 2)}</td>
                <td>{report.get('violation_count', 0)}</td>
                <td>{report.get('evaluated_at', 'N/A')[:10]}</td>
            </tr>
            """

        # Generate full HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Compliance Governance Dashboard</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}

                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}

                .header {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}

                .header h1 {{
                    font-size: 28px;
                    color: #1f2937;
                    margin-bottom: 10px;
                }}

                .header p {{
                    color: #6b7280;
                    font-size: 14px;
                }}

                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .metric-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}

                .metric-value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 10px 0;
                }}

                .metric-label {{
                    color: #6b7280;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .policies-section {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}

                .section-title {{
                    font-size: 20px;
                    color: #1f2937;
                    margin-bottom: 20px;
                    font-weight: 600;
                }}

                .policies-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 20px;
                }}

                .policy-card {{
                    background: #f9fafb;
                    padding: 16px;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                }}

                .policy-card:hover {{
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    transform: translateY(-2px);
                }}

                .policy-card h4 {{
                    color: #1f2937;
                    margin-bottom: 8px;
                    font-size: 14px;
                    font-weight: 600;
                }}

                .policy-id, .policy-level, .policy-rules, .policy-frameworks {{
                    font-size: 12px;
                    color: #6b7280;
                    margin: 4px 0;
                }}

                .reports-section {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 16px;
                }}

                th {{
                    background: #f3f4f6;
                    padding: 12px;
                    text-align: left;
                    font-size: 12px;
                    font-weight: 600;
                    color: #374151;
                    border-bottom: 2px solid #e5e7eb;
                }}

                td {{
                    padding: 12px;
                    border-bottom: 1px solid #e5e7eb;
                    font-size: 13px;
                }}

                tr:hover {{
                    background: #f9fafb;
                }}

                .footer {{
                    text-align: center;
                    color: white;
                    margin-top: 30px;
                    font-size: 12px;
                }}

                .progress-bar {{
                    height: 8px;
                    background: #e5e7eb;
                    border-radius: 4px;
                    margin: 8px 0;
                    overflow: hidden;
                }}

                .progress-fill {{
                    height: 100%;
                    background: #667eea;
                    transition: width 0.3s ease;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Compliance Governance Dashboard</h1>
                    <p>Enterprise compliance and policy management (Phase 60)</p>
                </div>

                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-label">Total Policies</div>
                        <div class="metric-value">{total_policies}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Total Evaluations</div>
                        <div class="metric-value">{total_evaluations}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Compliance Rate</div>
                        <div class="metric-value">{compliance_rate:.1f}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {compliance_rate}%;"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Average Score</div>
                        <div class="metric-value">{avg_score:.2f}</div>
                    </div>
                </div>

                <div class="policies-section">
                    <h2 class="section-title">📋 Active Policies</h2>
                    <div class="policies-grid">
                        {policy_cards if policy_cards else '<p style="color: #6b7280;">No policies registered</p>'}
                    </div>
                </div>

                <div class="reports-section">
                    <h2 class="section-title">📊 Recent Evaluations</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Policy ID</th>
                                <th>Status</th>
                                <th>Score</th>
                                <th>Violations</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recent_reports if recent_reports else '<tr><td colspan="5" style="text-align: center; color: #6b7280;">No evaluations</td></tr>'}
                        </tbody>
                    </table>
                </div>

                <div class="footer">
                    <p>Compliance Dashboard - Generated {datetime.utcnow().isoformat()}</p>
                    <p>Enterprise Pattern Registry & Policy Engine (Phase 60)</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _get_level_color(self, level: str) -> str:
        """Get color for policy level.

        Args:
            level: Policy level

        Returns:
            Color hex code
        """
        colors = {
            'strict': '#ef4444',      # Red
            'warning': '#f59e0b',     # Amber
            'advisory': '#3b82f6',    # Blue
        }
        return colors.get(level.lower(), '#6b7280')


# AC_COMPLETE: AC-PHASE60.0-S3-002 ✅
# ✅ Compliance governance dashboard HTML generation
# ✅ Metrics visualization
# ✅ Policy cards display
# ✅ Recent evaluations table
# ✅ Responsive design
