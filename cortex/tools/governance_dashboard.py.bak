"""
Governance Rule Dashboard for CORTEX compliance visualization.

Provides compliance heatmap and violation trend analysis for governance rules
across all phases and domains. Used to track compliance trends and identify
persistent governance issues across the project.

Features:
- Compliance heatmap (rules × phases)
- Violation history trending
- Domain-level compliance summaries
- Phase-level violation dashboards
- Compliance trend analysis
"""

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class ComplianceLevel(Enum):
    """Compliance levels for dashboard display."""

    COMPLIANT = "compliant"      # No violations in period
    WARNING = "warning"           # 1-3 violations
    CRITICAL = "critical"         # 4+ violations
    NO_DATA = "no_data"          # No data available


@dataclass
class ViolationMetric:
    """Single violation metric."""

    rule_id: str
    domain: str
    phase_id: str
    violation_count: int
    last_violation: Optional[str]
    severity: str  # "blocked", "warning", "info"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "domain": self.domain,
            "phase_id": self.phase_id,
            "violation_count": self.violation_count,
            "last_violation": self.last_violation,
            "severity": self.severity,
        }


@dataclass
class HeatmapRow:
    """Single row in compliance heatmap."""

    rule_id: str
    rule_name: str
    phases: Dict[str, int] = field(default_factory=dict)  # phase_id -> violation_count
    domain: str = ""
    severity: str = "info"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "domain": self.domain,
            "severity": self.severity,
            "phases": self.phases,
            "max_violations": max(self.phases.values()) if self.phases else 0,
        }


@dataclass
class PhaseComplianceSummary:
    """Phase-level compliance summary."""

    phase_id: str
    total_rules: int
    compliant_rules: int
    warning_rules: int
    critical_rules: int
    total_violations: int
    compliance_percentage: float
    status: ComplianceLevel

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase_id": self.phase_id,
            "total_rules": self.total_rules,
            "compliant_rules": self.compliant_rules,
            "warning_rules": self.warning_rules,
            "critical_rules": self.critical_rules,
            "total_violations": self.total_violations,
            "compliance_percentage": self.compliance_percentage,
            "status": self.status.value,
        }


@dataclass
class GovernanceRuleDashboard:
    """Complete governance rule dashboard."""

    timestamp: str
    heatmap: List[HeatmapRow] = field(default_factory=list)
    phase_summaries: List[PhaseComplianceSummary] = field(default_factory=list)
    domain_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    violation_trends: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "heatmap": [row.to_dict() for row in self.heatmap],
            "phase_summaries": [s.to_dict() for s in self.phase_summaries],
            "domain_summaries": self.domain_summaries,
            "violation_trends": self.violation_trends,
            "recommendations": self.recommendations,
        }


class GovernanceDashboardBuilder:
    """
    Build governance compliance dashboards.

    Generates heatmaps, trends, and summaries for governance compliance.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize dashboard builder.

        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.governance_db = (
            self.workspace_root / "cortex_brain" / "state" / "governance.db"
        )
        self.rules_file = (
            self.workspace_root / "cortex_brain" / "tier0" / "governance" / "core-rules.yaml"
        )

    def build_dashboard(self, phase_id: Optional[str] = None) -> GovernanceRuleDashboard:
        """
        Build governance dashboard.

        Args:
            phase_id: Optional phase to filter dashboard by

        Returns:
            Complete governance dashboard
        """
        import datetime
        dashboard = GovernanceRuleDashboard(
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        )

        # Load governance rules
        rules_by_id = self._load_governance_rules()

        # Build heatmap
        dashboard.heatmap = self._build_heatmap(rules_by_id, phase_id)

        # Build phase summaries
        dashboard.phase_summaries = self._build_phase_summaries(rules_by_id, phase_id)

        # Build domain summaries
        dashboard.domain_summaries = self._build_domain_summaries(rules_by_id)

        # Build violation trends
        dashboard.violation_trends = self._build_violation_trends(phase_id)

        # Generate recommendations
        dashboard.recommendations = self._generate_recommendations(dashboard)

        return dashboard

    def _load_governance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load governance rules from YAML."""
        if not self.rules_file.exists():
            return {}

        try:
            with open(self.rules_file) as f:
                rules_data = yaml.safe_load(f)

            rules_by_id = {}
            if rules_data and "rules" in rules_data:
                for rule in rules_data["rules"]:
                    rules_by_id[rule.get("id")] = rule

            return rules_by_id
        except Exception:
            return {}

    def _build_heatmap(
        self, rules_by_id: Dict[str, Dict[str, Any]], phase_id: Optional[str] = None
    ) -> List[HeatmapRow]:
        """Build compliance heatmap."""
        if not self.governance_db.exists():
            return []

        try:
            conn = sqlite3.connect(str(self.governance_db))
            cursor = conn.cursor()

            # Query violation counts by rule and phase
            query = """
                SELECT rule_id, phase_id, COUNT(*) as count
                FROM violations
                GROUP BY rule_id, phase_id
                ORDER BY rule_id, phase_id
            """

            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            # Organize by rule
            rules_dict: Dict[str, HeatmapRow] = {}

            for rule_id, phase, count in rows:
                if phase_id and phase != phase_id:
                    continue

                if rule_id not in rules_dict:
                    rule_info = rules_by_id.get(rule_id, {})
                    rules_dict[rule_id] = HeatmapRow(
                        rule_id=rule_id,
                        rule_name=rule_info.get("title", "Unknown"),
                        domain=rule_info.get("domain", "unknown"),
                        severity=rule_info.get("severity", "info"),
                    )

                rules_dict[rule_id].phases[phase] = count

            return list(rules_dict.values())

        except Exception:
            return []

    def _build_phase_summaries(
        self, rules_by_id: Dict[str, Dict[str, Any]], phase_id: Optional[str] = None
    ) -> List[PhaseComplianceSummary]:
        """Build phase-level compliance summaries."""
        if not self.governance_db.exists():
            return []

        try:
            conn = sqlite3.connect(str(self.governance_db))
            cursor = conn.cursor()

            # Get phases
            query = "SELECT DISTINCT phase_id FROM violations ORDER BY phase_id"
            if phase_id:
                query = f"SELECT '{phase_id}' as phase_id"

            cursor.execute(query)
            phases = [row[0] for row in cursor.fetchall()]

            summaries = []
            total_rules = len(rules_by_id)

            for ph in phases:
                # Count violations by severity
                cursor.execute("""
                    SELECT severity, COUNT(*) as count
                    FROM violations
                    WHERE phase_id = ?
                    GROUP BY severity
                """, (ph,))

                severity_counts = {row[0]: row[1] for row in cursor.fetchall()}
                total_violations = sum(severity_counts.values())

                # Determine compliance level
                if total_violations == 0:
                    compliance_level = ComplianceLevel.COMPLIANT
                    compliant = total_rules
                    warning = 0
                    critical = 0
                elif total_violations <= 3:
                    compliance_level = ComplianceLevel.WARNING
                    compliant = total_rules - len([1 for v in severity_counts.values() if v > 0])
                    warning = len([1 for v in severity_counts.values() if v > 0])
                    critical = 0
                else:
                    compliance_level = ComplianceLevel.CRITICAL
                    compliant = max(0, total_rules - (total_violations // 2))
                    warning = total_violations // 3
                    critical = total_violations - compliant - warning

                compliance_pct = (compliant / total_rules * 100) if total_rules > 0 else 100.0

                summaries.append(
                    PhaseComplianceSummary(
                        phase_id=ph,
                        total_rules=total_rules,
                        compliant_rules=compliant,
                        warning_rules=warning,
                        critical_rules=critical,
                        total_violations=total_violations,
                        compliance_percentage=compliance_pct,
                        status=compliance_level,
                    )
                )

            conn.close()
            return summaries

        except Exception:
            return []

    def _build_domain_summaries(
        self, rules_by_id: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Build domain-level compliance summaries."""
        if not self.governance_db.exists():
            return {}

        try:
            conn = sqlite3.connect(str(self.governance_db))
            cursor = conn.cursor()

            # Get domains from rules
            domains = set()
            for rule in rules_by_id.values():
                if domain := rule.get("domain"):
                    domains.add(domain)

            domain_summaries = {}

            for domain in sorted(domains):
                # Count rules in domain
                domain_rules = [r for r in rules_by_id.values() if r.get("domain") == domain]
                total_in_domain = len(domain_rules)

                # Count violations in domain
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM violations
                    WHERE rule_id IN (
                        SELECT rule_id FROM violations
                        WHERE rule_id LIKE ?
                    )
                """, (f'{domain}%',))

                violation_count = cursor.fetchone()[0] if cursor.fetchone() else 0

                compliance_pct = (
                    ((total_in_domain - violation_count) / total_in_domain * 100)
                    if total_in_domain > 0
                    else 100.0
                )

                domain_summaries[domain] = {
                    "total_rules": total_in_domain,
                    "violations": violation_count,
                    "compliance_percentage": compliance_pct,
                    "status": (
                        "compliant" if violation_count == 0
                        else "warning" if violation_count <= 3
                        else "critical"
                    ),
                }

            conn.close()
            return domain_summaries

        except Exception:
            return {}

    def _build_violation_trends(self, phase_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Build violation trend analysis."""
        if not self.governance_db.exists():
            return []

        try:
            conn = sqlite3.connect(str(self.governance_db))
            cursor = conn.cursor()

            # Get violations by timestamp
            query = """
                SELECT DATE(timestamp) as date, COUNT(*) as count, severity
                FROM violations
            """
            params: List[Any] = []

            if phase_id:
                query += " WHERE phase_id = ?"
                params.append(phase_id)

            query += " GROUP BY DATE(timestamp), severity ORDER BY date"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            # Format trends
            trends = []
            for date, count, severity in rows:
                trends.append({
                    "date": date,
                    "violations": count,
                    "severity": severity,
                })

            return trends

        except Exception:
            return []

    def _generate_recommendations(self, dashboard: GovernanceRuleDashboard) -> List[str]:
        """Generate recommendations from dashboard data."""
        recommendations = []

        # Check phase compliance
        for phase_summary in dashboard.phase_summaries:
            if phase_summary.status == ComplianceLevel.CRITICAL:
                recommendations.append(
                    f"🔴 {phase_summary.phase_id}: {phase_summary.critical_rules} critical violations - "
                    f"focus on high-priority issues first"
                )
            elif phase_summary.status == ComplianceLevel.WARNING:
                recommendations.append(
                    f"🟡 {phase_summary.phase_id}: {phase_summary.warning_rules} warnings - "
                    f"address before phase lock"
                )

        # Check domain health
        for domain, summary in dashboard.domain_summaries.items():
            if summary["status"] == "critical":
                recommendations.append(
                    f"Domain {domain}: {summary['violations']} violations across "
                    f"{summary['total_rules']} rules - needs remediation"
                )

        # Overall recommendations
        if not recommendations:
            recommendations.append("✅ All phases showing strong compliance - maintain current practices")

        return recommendations


def main() -> int:
    """Main entry point for governance dashboard."""
    import sys

    phase_id = sys.argv[1].upper() if len(sys.argv) > 1 else None

    builder = GovernanceDashboardBuilder()
    dashboard = builder.build_dashboard(phase_id)

    print(json.dumps(dashboard.to_dict(), indent=2))

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
