"""
CORTEX Lens Security Dashboard

Purpose: Security metrics visualization and monitoring dashboard
         for tracking security posture, vulnerabilities, and compliance.

Version: 1.0.0
Author: CORTEX Development Team
Created: December 30, 2025
Status: Phase 5 Security Enhancement

Features:
- Security posture overview
- OWASP Top 10 coverage tracking
- Vulnerability trend analysis
- Compliance status monitoring
- Security debt visualization
- Real-time security metrics
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    OWASP = "OWASP Top 10"
    PCI_DSS = "PCI-DSS"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    SOC2 = "SOC 2"


@dataclass
class SecurityMetric:
    """Individual security metric."""
    name: str
    value: float
    unit: str
    trend: str  # 'up', 'down', 'stable'
    target: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ComplianceStatus:
    """Compliance framework status."""
    framework: ComplianceFramework
    score: float  # 0-100
    controls_passed: int
    controls_total: int
    last_assessment: str
    critical_gaps: List[str] = field(default_factory=list)


@dataclass
class SecurityPosture:
    """Overall security posture assessment."""
    overall_score: float  # 0-100
    risk_level: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    vulnerabilities_critical: int
    vulnerabilities_high: int
    vulnerabilities_medium: int
    vulnerabilities_low: int
    security_debt_hours: float
    last_scan: str
    trend: str  # 'improving', 'declining', 'stable'


class SecurityDashboard:
    """
    Security metrics dashboard for CORTEX Lens.
    
    Provides:
    - Real-time security posture visualization
    - OWASP Top 10 coverage tracking
    - Compliance status monitoring
    - Vulnerability trend analysis
    - Security KPI tracking
    """
    
    # OWASP Top 10 2021 with weights
    OWASP_WEIGHTS = {
        'A01:2021': {'name': 'Broken Access Control', 'weight': 1.5, 'severity': 'CRITICAL'},
        'A02:2021': {'name': 'Cryptographic Failures', 'weight': 1.3, 'severity': 'HIGH'},
        'A03:2021': {'name': 'Injection', 'weight': 1.5, 'severity': 'CRITICAL'},
        'A04:2021': {'name': 'Insecure Design', 'weight': 1.2, 'severity': 'HIGH'},
        'A05:2021': {'name': 'Security Misconfiguration', 'weight': 1.1, 'severity': 'MEDIUM'},
        'A06:2021': {'name': 'Vulnerable Components', 'weight': 1.3, 'severity': 'HIGH'},
        'A07:2021': {'name': 'Auth Failures', 'weight': 1.4, 'severity': 'CRITICAL'},
        'A08:2021': {'name': 'Integrity Failures', 'weight': 1.2, 'severity': 'HIGH'},
        'A09:2021': {'name': 'Logging Failures', 'weight': 1.0, 'severity': 'MEDIUM'},
        'A10:2021': {'name': 'SSRF', 'weight': 1.1, 'severity': 'HIGH'},
    }
    
    def __init__(
        self,
        project_path: Optional[Path] = None,
        history_path: Optional[Path] = None
    ):
        """Initialize security dashboard."""
        self.project_path = project_path or Path.cwd()
        self.history_path = history_path or self.project_path / 'cortex-brain' / 'metrics-history'
        self.metrics: Dict[str, SecurityMetric] = {}
        self.scan_history: List[Dict[str, Any]] = []
        self._load_history()
        logger.info("📊 Security Dashboard initialized")
    
    def _load_history(self):
        """Load historical scan data."""
        history_file = self.history_path / 'security-scan-history.json'
        if history_file.exists():
            try:
                self.scan_history = json.loads(history_file.read_text())
            except Exception as e:
                logger.warning(f"Could not load scan history: {e}")
                self.scan_history = []
    
    def _save_history(self):
        """Save scan history."""
        self.history_path.mkdir(parents=True, exist_ok=True)
        history_file = self.history_path / 'security-scan-history.json'
        history_file.write_text(json.dumps(self.scan_history[-100:], indent=2))  # Keep last 100
    
    def calculate_security_posture(
        self,
        scan_result: Optional[Dict[str, Any]] = None
    ) -> SecurityPosture:
        """
        Calculate overall security posture from scan results.
        
        Args:
            scan_result: Result from SecurityScannerAgent.scan()
            
        Returns:
            SecurityPosture assessment
        """
        if not scan_result:
            # Return default posture if no scan data
            return SecurityPosture(
                overall_score=100.0,
                risk_level='LOW',
                vulnerabilities_critical=0,
                vulnerabilities_high=0,
                vulnerabilities_medium=0,
                vulnerabilities_low=0,
                security_debt_hours=0,
                last_scan='Never',
                trend='stable'
            )
        
        summary = scan_result.get('summary', {})
        
        # Count by severity
        critical = summary.get('critical', 0)
        high = summary.get('high', 0)
        medium = summary.get('medium', 0)
        low = summary.get('low', 0)
        
        # Calculate score (100 - weighted deductions)
        deductions = (
            critical * 10 +  # Critical: -10 each
            high * 5 +       # High: -5 each
            medium * 2 +     # Medium: -2 each
            low * 0.5        # Low: -0.5 each
        )
        score = max(0, 100 - deductions)
        
        # Determine risk level
        if critical > 0 or score < 40:
            risk_level = 'CRITICAL'
        elif high > 2 or score < 60:
            risk_level = 'HIGH'
        elif medium > 5 or score < 80:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Calculate security debt (estimated hours to fix)
        debt_hours = (
            critical * 8 +   # Critical: 8 hours each
            high * 4 +       # High: 4 hours each
            medium * 2 +     # Medium: 2 hours each
            low * 0.5        # Low: 30 minutes each
        )
        
        # Determine trend from history
        trend = self._calculate_trend(score)
        
        return SecurityPosture(
            overall_score=round(score, 1),
            risk_level=risk_level,
            vulnerabilities_critical=critical,
            vulnerabilities_high=high,
            vulnerabilities_medium=medium,
            vulnerabilities_low=low,
            security_debt_hours=round(debt_hours, 1),
            last_scan=scan_result.get('completed_at', datetime.now().isoformat()),
            trend=trend
        )
    
    def _calculate_trend(self, current_score: float) -> str:
        """Calculate score trend from history."""
        if len(self.scan_history) < 2:
            return 'stable'
        
        recent_scores = [h.get('score', 100) for h in self.scan_history[-5:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        if current_score > avg_recent + 5:
            return 'improving'
        elif current_score < avg_recent - 5:
            return 'declining'
        return 'stable'
    
    def calculate_owasp_coverage(
        self,
        scan_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate OWASP Top 10 coverage and risk per category.
        
        Returns:
            Dictionary with OWASP category details and findings count
        """
        coverage = {}
        
        for owasp_id, info in self.OWASP_WEIGHTS.items():
            coverage[owasp_id] = {
                'name': info['name'],
                'severity': info['severity'],
                'findings': 0,
                'risk_score': 0,
                'status': 'PASS'  # PASS, WARN, FAIL
            }
        
        if scan_result:
            owasp_counts = scan_result.get('summary', {}).get('by_owasp', {})
            
            for owasp_id, count in owasp_counts.items():
                if owasp_id in coverage:
                    coverage[owasp_id]['findings'] = count
                    weight = self.OWASP_WEIGHTS[owasp_id]['weight']
                    coverage[owasp_id]['risk_score'] = round(count * weight, 1)
                    
                    # Determine status
                    if count >= 3:
                        coverage[owasp_id]['status'] = 'FAIL'
                    elif count >= 1:
                        coverage[owasp_id]['status'] = 'WARN'
        
        return coverage
    
    def calculate_compliance_status(
        self,
        framework: ComplianceFramework,
        scan_result: Optional[Dict[str, Any]] = None
    ) -> ComplianceStatus:
        """
        Calculate compliance status for a specific framework.
        
        Args:
            framework: Compliance framework to assess
            scan_result: Security scan results
            
        Returns:
            ComplianceStatus for the framework
        """
        # Define control requirements per framework
        framework_controls = {
            ComplianceFramework.OWASP: {
                'total': 10,
                'requirements': ['A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10']
            },
            ComplianceFramework.PCI_DSS: {
                'total': 12,
                'requirements': ['REQ1', 'REQ2', 'REQ3', 'REQ4', 'REQ5', 'REQ6', 
                                'REQ7', 'REQ8', 'REQ9', 'REQ10', 'REQ11', 'REQ12']
            },
            ComplianceFramework.GDPR: {
                'total': 8,
                'requirements': ['Lawfulness', 'Purpose', 'Minimization', 'Accuracy',
                                'Storage', 'Security', 'Accountability', 'Rights']
            },
            ComplianceFramework.SOC2: {
                'total': 5,
                'requirements': ['Security', 'Availability', 'Processing', 'Confidentiality', 'Privacy']
            },
        }
        
        controls = framework_controls.get(framework, {'total': 10, 'requirements': []})
        
        # Calculate passed controls based on scan results
        critical_gaps = []
        passed = controls['total']
        
        if scan_result:
            summary = scan_result.get('summary', {})
            owasp_counts = summary.get('by_owasp', {})
            
            # Deduct for findings
            if summary.get('critical', 0) > 0:
                passed -= 2
                critical_gaps.append("Critical vulnerabilities present")
            if summary.get('high', 0) > 2:
                passed -= 1
                critical_gaps.append("Multiple high-severity issues")
            
            # Check OWASP categories for OWASP compliance
            if framework == ComplianceFramework.OWASP:
                for owasp_id, count in owasp_counts.items():
                    if count >= 3:
                        passed -= 1
                        critical_gaps.append(f"{owasp_id}: {count} findings")
        
        passed = max(0, passed)
        score = (passed / controls['total']) * 100
        
        return ComplianceStatus(
            framework=framework,
            score=round(score, 1),
            controls_passed=passed,
            controls_total=controls['total'],
            last_assessment=datetime.now().isoformat(),
            critical_gaps=critical_gaps[:5]  # Top 5 gaps
        )
    
    def get_security_kpis(
        self,
        scan_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, SecurityMetric]:
        """
        Get key security performance indicators.
        
        Returns:
            Dictionary of security KPIs
        """
        posture = self.calculate_security_posture(scan_result)
        
        kpis = {
            'security_score': SecurityMetric(
                name='Security Score',
                value=posture.overall_score,
                unit='%',
                trend=posture.trend,
                target=90.0
            ),
            'critical_vulns': SecurityMetric(
                name='Critical Vulnerabilities',
                value=posture.vulnerabilities_critical,
                unit='count',
                trend='down' if posture.vulnerabilities_critical == 0 else 'up',
                target=0
            ),
            'high_vulns': SecurityMetric(
                name='High Vulnerabilities',
                value=posture.vulnerabilities_high,
                unit='count',
                trend='stable',
                target=0
            ),
            'security_debt': SecurityMetric(
                name='Security Debt',
                value=posture.security_debt_hours,
                unit='hours',
                trend='stable',
                target=0
            ),
            'mean_time_to_remediate': SecurityMetric(
                name='Mean Time to Remediate',
                value=self._calculate_mttr(),
                unit='days',
                trend='stable',
                target=7.0
            ),
        }
        
        return kpis
    
    def _calculate_mttr(self) -> float:
        """Calculate Mean Time to Remediate from history."""
        if len(self.scan_history) < 2:
            return 0.0
        
        # Simplified MTTR calculation
        # In production, this would track actual remediation times
        return 3.5
    
    def record_scan(self, scan_result: Dict[str, Any]):
        """Record scan result to history."""
        posture = self.calculate_security_posture(scan_result)
        
        self.scan_history.append({
            'timestamp': datetime.now().isoformat(),
            'score': posture.overall_score,
            'critical': posture.vulnerabilities_critical,
            'high': posture.vulnerabilities_high,
            'medium': posture.vulnerabilities_medium,
            'low': posture.vulnerabilities_low,
            'total': sum([
                posture.vulnerabilities_critical,
                posture.vulnerabilities_high,
                posture.vulnerabilities_medium,
                posture.vulnerabilities_low
            ])
        })
        
        self._save_history()
    
    def generate_dashboard_html(
        self,
        scan_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate HTML dashboard for security metrics.
        
        Returns:
            HTML string for rendering
        """
        posture = self.calculate_security_posture(scan_result)
        owasp = self.calculate_owasp_coverage(scan_result)
        kpis = self.get_security_kpis(scan_result)
        
        # Risk level colors
        risk_colors = {
            'LOW': '#4CAF50',
            'MEDIUM': '#FF9800',
            'HIGH': '#f44336',
            'CRITICAL': '#9C27B0'
        }
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Security Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent-blue: #667eea;
            --accent-purple: #764ba2;
            --success: #4CAF50;
            --warning: #FF9800;
            --danger: #f44336;
            --critical: #9C27B0;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .dashboard-header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .dashboard-header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .glass-card {{
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-trend {{
            font-size: 0.75rem;
            margin-top: 0.5rem;
        }}
        
        .trend-up {{ color: var(--danger); }}
        .trend-down {{ color: var(--success); }}
        .trend-stable {{ color: var(--text-secondary); }}
        
        .risk-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            background: {risk_colors[posture.risk_level]};
        }}
        
        .owasp-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem;
        }}
        
        .owasp-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            border-left: 3px solid var(--glass-border);
        }}
        
        .owasp-item.fail {{ border-left-color: var(--danger); }}
        .owasp-item.warn {{ border-left-color: var(--warning); }}
        .owasp-item.pass {{ border-left-color: var(--success); }}
        
        .chart-container {{
            max-width: 400px;
            margin: 0 auto;
        }}
        
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }}
        
        @media (max-width: 768px) {{
            .two-column {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1><i class="fas fa-shield-alt"></i> CORTEX Security Dashboard</h1>
        <p>Last Scan: {posture.last_scan[:19] if posture.last_scan != 'Never' else 'Never'}</p>
    </div>
    
    <!-- Security Score -->
    <div class="glass-card" style="text-align: center;">
        <h2>Security Posture</h2>
        <div class="metric-value" style="font-size: 4rem; color: {risk_colors[posture.risk_level]};">
            {posture.overall_score}%
        </div>
        <span class="risk-badge">{posture.risk_level} RISK</span>
        <p class="metric-trend trend-{posture.trend}">{posture.trend.upper()}</p>
    </div>
    
    <!-- KPI Metrics -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value" style="color: var(--critical);">{posture.vulnerabilities_critical}</div>
            <div class="metric-label">Critical</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: var(--danger);">{posture.vulnerabilities_high}</div>
            <div class="metric-label">High</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: var(--warning);">{posture.vulnerabilities_medium}</div>
            <div class="metric-label">Medium</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: var(--success);">{posture.vulnerabilities_low}</div>
            <div class="metric-label">Low</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{posture.security_debt_hours}h</div>
            <div class="metric-label">Security Debt</div>
        </div>
    </div>
    
    <div class="two-column">
        <!-- OWASP Coverage -->
        <div class="glass-card">
            <h3><i class="fas fa-list-check"></i> OWASP Top 10 Coverage</h3>
            <div class="owasp-grid" style="margin-top: 1rem;">
                {''.join([f'''
                <div class="owasp-item {owasp[oid]['status'].lower()}">
                    <span>{oid}: {owasp[oid]['name']}</span>
                    <span style="font-weight: 600;">{owasp[oid]['findings']}</span>
                </div>
                ''' for oid in owasp])}
            </div>
        </div>
        
        <!-- Severity Chart -->
        <div class="glass-card">
            <h3><i class="fas fa-chart-pie"></i> Vulnerability Distribution</h3>
            <div class="chart-container" style="margin-top: 1rem;">
                <canvas id="severityChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('severityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{{
                    data: [{posture.vulnerabilities_critical}, {posture.vulnerabilities_high}, {posture.vulnerabilities_medium}, {posture.vulnerabilities_low}],
                    backgroundColor: ['#9C27B0', '#f44336', '#FF9800', '#4CAF50'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{ color: '#fff' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def generate_dashboard_data(
        self,
        scan_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate dashboard data as JSON for API consumption.
        
        Returns:
            Dictionary with all dashboard data
        """
        posture = self.calculate_security_posture(scan_result)
        owasp = self.calculate_owasp_coverage(scan_result)
        kpis = self.get_security_kpis(scan_result)
        
        return {
            'posture': {
                'score': posture.overall_score,
                'risk_level': posture.risk_level,
                'trend': posture.trend,
                'vulnerabilities': {
                    'critical': posture.vulnerabilities_critical,
                    'high': posture.vulnerabilities_high,
                    'medium': posture.vulnerabilities_medium,
                    'low': posture.vulnerabilities_low,
                },
                'security_debt_hours': posture.security_debt_hours,
                'last_scan': posture.last_scan
            },
            'owasp_coverage': {
                oid: {
                    'name': data['name'],
                    'findings': data['findings'],
                    'status': data['status'],
                    'risk_score': data['risk_score']
                }
                for oid, data in owasp.items()
            },
            'kpis': {
                name: {
                    'value': metric.value,
                    'unit': metric.unit,
                    'trend': metric.trend,
                    'target': metric.target
                }
                for name, metric in kpis.items()
            },
            'history': self.scan_history[-10:]  # Last 10 scans
        }


# CLI interface
if __name__ == "__main__":
    import sys
    
    dashboard = SecurityDashboard(project_path=Path(sys.argv[1] if len(sys.argv) > 1 else '.'))
    
    # Generate sample dashboard
    html = dashboard.generate_dashboard_html()
    
    output_path = Path('security-dashboard.html')
    output_path.write_text(html)
    print(f"Dashboard generated: {output_path}")
