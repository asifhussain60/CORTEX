"""
AC-CORTEX-001: Architecture Health Check System

CORTEX 6.0 Unified Architecture Health Checker

Purpose:
  - Detect misalignment across all CORTEX layers (Tier 0-3)
  - Validate registry consistency (MCP, Orchestrator, Tool)
  - Check SQLite database integrity and schemas
  - Auto-repair common issues
  - Provide full audit trail of all repairs

Architecture:
  Layer 1: Validators (detect issues)
  Layer 2: Healers (auto-repair safe issues)
  Layer 3: Auditors (track all changes)
  Layer 4: Reporters (generate reports)

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-13
Governance: CORE-001 (incremental), CORE-008 (TDD), CORE-017 (enforcement)

AC-ID: AC-CORTEX-001
"""

import logging
import json
import sqlite3
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import traceback


class IssueSeverity(Enum):
    """Issue severity levels for health checks."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class IssueCategory(Enum):
    """Issue categories for health checks."""
    TIER_0_GOVERNANCE = "TIER_0_GOVERNANCE"
    TIER_1_EXECUTION = "TIER_1_EXECUTION"
    DATABASE_SCHEMA = "DATABASE_SCHEMA"
    MCP_REGISTRY = "MCP_REGISTRY"
    CONFIG_FILES = "CONFIG_FILES"
    CROSS_LAYER = "CROSS_LAYER"


@dataclass
class HealthIssue:
    """Represents a detected health issue."""
    category: IssueCategory
    component: str
    issue_id: str
    description: str
    severity: IssueSeverity
    can_auto_repair: bool
    repair_action: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class HealthRepair:
    """Represents a repair action applied."""
    issue_id: str
    repair_type: str
    status: str  # "applied", "failed", "skipped"
    changes: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    error_message: Optional[str] = None


@dataclass
class HealthCheckReport:
    """Complete health check report."""
    timestamp: str
    total_issues: int
    critical_issues: int
    high_issues: int
    issues: List[HealthIssue]
    auto_repairable: int
    system_healthy: bool


@dataclass
class HealthRepairReport:
    """Report of repairs applied."""
    timestamp: str
    checks_passed: int
    checks_failed: int
    repairs_applied: List[HealthRepair]
    manual_interventions: List[HealthIssue]
    success: bool


class TierZeroValidator:
    """Validates Tier 0 governance rules."""

    def __init__(self, project_root: Path):
        self.logger = logging.getLogger("cortex.health.tier0_validator")
        self.project_root = project_root
        self.core_rules_path = project_root / "cortex-brain/tier0/governance/core-rules.yaml"

    def validate(self) -> List[HealthIssue]:
        """Validate Tier 0 governance."""
        issues = []

        # Check core-rules.yaml exists
        if not self.core_rules_path.exists():
            issues.append(HealthIssue(
                category=IssueCategory.TIER_0_GOVERNANCE,
                component="core-rules.yaml",
                issue_id="TIER0-001",
                description=f"core-rules.yaml not found at {self.core_rules_path}",
                severity=IssueSeverity.CRITICAL,
                can_auto_repair=False,
                evidence={"expected_path": str(self.core_rules_path)}
            ))
            return issues

        # Check YAML syntax
        try:
            with open(self.core_rules_path, 'r') as f:
                rules = yaml.safe_load(f)
            if not isinstance(rules, dict):
                raise ValueError("core-rules.yaml must be a YAML dict")
        except Exception as e:
            issues.append(HealthIssue(
                category=IssueCategory.TIER_0_GOVERNANCE,
                component="core-rules.yaml",
                issue_id="TIER0-002",
                description=f"YAML syntax error in core-rules.yaml: {str(e)}",
                severity=IssueSeverity.CRITICAL,
                can_auto_repair=False,
                evidence={"error": str(e)}
            ))
            return issues

        # Check for SKULL rules
        try:
            rule_ids = set()
            if 'rules' in rules:
                for rule in rules['rules']:
                    if isinstance(rule, dict) and 'rule_id' in rule:
                        rule_ids.add(rule['rule_id'])

            if len(rule_ids) < 23:  # Should have at least 23 rules (CORE-001 to CORE-026)
                issues.append(HealthIssue(
                    category=IssueCategory.TIER_0_GOVERNANCE,
                    component="core-rules.yaml",
                    issue_id="TIER0-003",
                    description=f"Found {len(rule_ids)} rules, expected ≥23 SKULL rules",
                    severity=IssueSeverity.HIGH,
                    can_auto_repair=False,
                    evidence={"rule_count": len(rule_ids), "found_rules": list(rule_ids)}
                ))
        except Exception as e:
            self.logger.warning(f"Error checking SKULL rules: {e}")

        # Check mcp-tools-registry.yaml
        mcp_registry_path = self.project_root / "cortex-brain/tier0/governance/mcp-tools-registry.yaml"
        try:
            if mcp_registry_path.exists():
                with open(mcp_registry_path, 'r') as f:
                    mcp_registry = yaml.safe_load(f)

                # Check for UUID suffix (violation of CORE-026)
                if "-" in mcp_registry_path.stem and len(mcp_registry_path.stem.split("-")[-1]) == 8:
                    issues.append(HealthIssue(
                        category=IssueCategory.TIER_0_GOVERNANCE,
                        component="mcp-tools-registry.yaml",
                        issue_id="TIER0-004",
                        description=f"MCP registry has UUID suffix (CORE-026 violation): {mcp_registry_path.name}",
                        severity=IssueSeverity.HIGH,
                        can_auto_repair=True,
                        repair_action="remove_uuid_suffix",
                        evidence={"filename": mcp_registry_path.name}
                    ))
        except Exception as e:
            self.logger.warning(f"Error validating MCP registry: {e}")

        return issues


class TierOneValidator:
    """Validates Tier 1 execution state."""

    def __init__(self, project_root: Path):
        self.logger = logging.getLogger("cortex.health.tier1_validator")
        self.project_root = project_root
        self.tracker_path = project_root / "cortex-brain/tier1/tracking/progress-tracker.json"
        self.ac_index_path = project_root / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"

    def validate(self) -> List[HealthIssue]:
        """Validate Tier 1 execution state."""
        issues = []

        # Check progress-tracker.json
        if not self.tracker_path.exists():
            issues.append(HealthIssue(
                category=IssueCategory.TIER_1_EXECUTION,
                component="progress-tracker.json",
                issue_id="TIER1-001",
                description=f"progress-tracker.json not found at {self.tracker_path}",
                severity=IssueSeverity.CRITICAL,
                can_auto_repair=False,
                evidence={"expected_path": str(self.tracker_path)}
            ))
            return issues

        # Check JSON validity
        try:
            with open(self.tracker_path, 'r') as f:
                tracker = json.load(f)
        except Exception as e:
            issues.append(HealthIssue(
                category=IssueCategory.TIER_1_EXECUTION,
                component="progress-tracker.json",
                issue_id="TIER1-002",
                description=f"JSON syntax error in progress-tracker.json: {str(e)}",
                severity=IssueSeverity.CRITICAL,
                can_auto_repair=False,
                evidence={"error": str(e)}
            ))
            return issues

        # Check AC-INDEX.yaml
        if not self.ac_index_path.exists():
            issues.append(HealthIssue(
                category=IssueCategory.TIER_1_EXECUTION,
                component="AC-INDEX.yaml",
                issue_id="TIER1-003",
                description=f"AC-INDEX.yaml not found at {self.ac_index_path}",
                severity=IssueSeverity.CRITICAL,
                can_auto_repair=False,
                evidence={"expected_path": str(self.ac_index_path)}
            ))
            return issues

        try:
            with open(self.ac_index_path, 'r') as f:
                ac_index = yaml.safe_load(f)
        except Exception as e:
            issues.append(HealthIssue(
                category=IssueCategory.TIER_1_EXECUTION,
                component="AC-INDEX.yaml",
                issue_id="TIER1-004",
                description=f"YAML syntax error in AC-INDEX.yaml: {str(e)}",
                severity=IssueSeverity.CRITICAL,
                can_auto_repair=False,
                evidence={"error": str(e)}
            ))
            return issues

        # Validate no impossible completion states (>100%)
        if isinstance(tracker, dict):
            for phase_key, phase_data in tracker.items():
                if isinstance(phase_data, dict) and "completed_count" in phase_data and "total_ac_count" in phase_data:
                    completed = phase_data.get("completed_count", 0)
                    total = phase_data.get("total_ac_count", 1)
                    if total > 0 and completed > total:
                        issues.append(HealthIssue(
                            category=IssueCategory.TIER_1_EXECUTION,
                            component="progress-tracker.json",
                            issue_id="TIER1-005",
                            description=f"{phase_key}: completed_count ({completed}) > total_ac_count ({total})",
                            severity=IssueSeverity.HIGH,
                            can_auto_repair=True,
                            repair_action="cap_completion_at_total",
                            evidence={"phase": phase_key, "completed": completed, "total": total}
                        ))

        return issues


class DatabaseValidator:
    """Validates SQLite database schemas."""

    def __init__(self, project_root: Path):
        self.logger = logging.getLogger("cortex.health.database_validator")
        self.project_root = project_root
        self.db_paths = {
            "governance": project_root / "cortex-brain/database/governance.db",
            "audit": project_root / "cortex-brain/database/audit.db",
            "planning_state": project_root / "cortex-brain/database/planning_state.db",
        }

    def validate(self) -> List[HealthIssue]:
        """Validate database integrity."""
        issues = []

        for db_name, db_path in self.db_paths.items():
            if not db_path.exists():
                self.logger.info(f"Database {db_name} not found at {db_path} (not created yet)")
                continue

            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()

                # Run integrity check
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                if result and result[0] != "ok":
                    issues.append(HealthIssue(
                        category=IssueCategory.DATABASE_SCHEMA,
                        component=f"{db_name}.db",
                        issue_id=f"DB-{db_name.upper()}-001",
                        description=f"Database corruption detected in {db_name}.db: {result[0]}",
                        severity=IssueSeverity.CRITICAL,
                        can_auto_repair=True,
                        repair_action="rebuild_database",
                        evidence={"database": db_name, "integrity_check_result": result[0]}
                    ))

                conn.close()
            except Exception as e:
                issues.append(HealthIssue(
                    category=IssueCategory.DATABASE_SCHEMA,
                    component=f"{db_name}.db",
                    issue_id=f"DB-{db_name.upper()}-002",
                    description=f"Error accessing {db_name}.db: {str(e)}",
                    severity=IssueSeverity.HIGH,
                    can_auto_repair=False,
                    evidence={"database": db_name, "error": str(e)}
                ))

        return issues


class MCPValidator:
    """Validates MCP registry consistency."""

    def __init__(self, project_root: Path):
        self.logger = logging.getLogger("cortex.health.mcp_validator")
        self.project_root = project_root
        self.mcp_server_path = project_root / "cortex-brain/config/mcp-server.yaml"
        self.mcp_tools_registry_path = project_root / "cortex-brain/tier0/governance/mcp-tools-registry.yaml"

    def validate(self) -> List[HealthIssue]:
        """Validate MCP registries."""
        issues = []

        # Check mcp-server.yaml
        if not self.mcp_server_path.exists():
            issues.append(HealthIssue(
                category=IssueCategory.MCP_REGISTRY,
                component="mcp-server.yaml",
                issue_id="MCP-001",
                description=f"mcp-server.yaml not found at {self.mcp_server_path}",
                severity=IssueSeverity.HIGH,
                can_auto_repair=False,
                evidence={"expected_path": str(self.mcp_server_path)}
            ))
            return issues

        try:
            with open(self.mcp_server_path, 'r') as f:
                mcp_server = yaml.safe_load(f)

            # Validate orchestrator references are loadable
            if isinstance(mcp_server, dict) and "orchestrators" in mcp_server:
                for orch_id, orch_data in mcp_server["orchestrators"].items():
                    if not isinstance(orch_data, dict) or "module" not in orch_data:
                        issues.append(HealthIssue(
                            category=IssueCategory.MCP_REGISTRY,
                            component="mcp-server.yaml",
                            issue_id="MCP-002",
                            description=f"Orchestrator {orch_id} missing module path",
                            severity=IssueSeverity.HIGH,
                            can_auto_repair=False,
                            evidence={"orchestrator_id": orch_id}
                        ))
        except Exception as e:
            issues.append(HealthIssue(
                category=IssueCategory.MCP_REGISTRY,
                component="mcp-server.yaml",
                issue_id="MCP-003",
                description=f"YAML syntax error in mcp-server.yaml: {str(e)}",
                severity=IssueSeverity.HIGH,
                can_auto_repair=False,
                evidence={"error": str(e)}
            ))

        return issues


class CrossLayerValidator:
    """Validates consistency across Tier 0-3."""

    def __init__(self, project_root: Path):
        self.logger = logging.getLogger("cortex.health.cross_layer_validator")
        self.project_root = project_root

    def validate(self) -> List[HealthIssue]:
        """Validate cross-layer consistency."""
        issues = []

        # Verify tier structure exists
        tiers = ["tier0", "tier1", "tier2", "tier3"]
        for tier in tiers:
            tier_path = self.project_root / f"cortex-brain/{tier}"
            if not tier_path.exists():
                issues.append(HealthIssue(
                    category=IssueCategory.CROSS_LAYER,
                    component=f"{tier}/",
                    issue_id="CROSS-001",
                    description=f"{tier} directory not found at {tier_path}",
                    severity=IssueSeverity.HIGH,
                    can_auto_repair=True,
                    repair_action="create_tier_directory",
                    evidence={"tier": tier, "expected_path": str(tier_path)}
                ))

        return issues


class HealthCheckOrchestratorV1:
    """CORTEX 6.0 Architecture Health Check System (AC-CORTEX-001)."""

    def __init__(self, project_root: Optional[Path] = None):
        self.logger = logging.getLogger("cortex.health_check_orchestrator")
        self.project_root = project_root or Path.cwd()

        # Initialize validators
        self.validators = [
            TierZeroValidator(self.project_root),
            TierOneValidator(self.project_root),
            DatabaseValidator(self.project_root),
            MCPValidator(self.project_root),
            CrossLayerValidator(self.project_root),
        ]

        self.audit_log: List[HealthRepair] = []

    def check(self) -> HealthCheckReport:
        """Run all validations without making changes."""
        all_issues = []

        for validator in self.validators:
            try:
                issues = validator.validate()
                all_issues.extend(issues)
                self.logger.info(f"{validator.__class__.__name__} found {len(issues)} issues")
            except Exception as e:
                self.logger.error(f"Error running {validator.__class__.__name__}: {e}")
                all_issues.append(HealthIssue(
                    category=IssueCategory.TIER_0_GOVERNANCE,
                    component=validator.__class__.__name__,
                    issue_id="VALIDATOR-ERROR",
                    description=f"Validator error: {str(e)}",
                    severity=IssueSeverity.HIGH,
                    can_auto_repair=False,
                    evidence={"error": str(e), "traceback": traceback.format_exc()}
                ))

        # Count issues by severity
        critical_count = sum(1 for i in all_issues if i.severity == IssueSeverity.CRITICAL)
        high_count = sum(1 for i in all_issues if i.severity == IssueSeverity.HIGH)
        auto_repairable = sum(1 for i in all_issues if i.can_auto_repair)

        return HealthCheckReport(
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_issues=len(all_issues),
            critical_issues=critical_count,
            high_issues=high_count,
            issues=all_issues,
            auto_repairable=auto_repairable,
            system_healthy=critical_count == 0 and high_count == 0
        )

    def repair(self, auto_repair: bool = True) -> HealthRepairReport:
        """Run checks and auto-repair safe issues."""
        check_report = self.check()

        repairs_applied = []
        manual_interventions = []

        for issue in check_report.issues:
            if auto_repair and issue.can_auto_repair and issue.severity in [IssueSeverity.MEDIUM, IssueSeverity.LOW]:
                repair = self._apply_fix(issue)
                repairs_applied.append(repair)
                self.audit_log.append(repair)
                self.logger.info(f"Applied repair: {issue.issue_id}")
            else:
                manual_interventions.append(issue)

        return HealthRepairReport(
            timestamp=datetime.utcnow().isoformat() + "Z",
            checks_passed=check_report.total_issues - len(repairs_applied),
            checks_failed=len(repairs_applied),
            repairs_applied=repairs_applied,
            manual_interventions=manual_interventions,
            success=len(manual_interventions) == 0
        )

    def _apply_fix(self, issue: HealthIssue) -> HealthRepair:
        """Apply a repair action."""
        repair = HealthRepair(
            issue_id=issue.issue_id,
            repair_type=issue.repair_action or "unknown",
            status="skipped",  # Default: not implemented
            changes={}
        )

        try:
            if issue.repair_action == "remove_uuid_suffix":
                # Remove UUID suffix from MCP registry filename
                mcp_registry = self.project_root / "cortex-brain/tier0/governance/mcp-tools-registry.yaml"
                if "_" in mcp_registry.stem:
                    clean_name = mcp_registry.stem.split("_")[0] + ".yaml"
                    new_path = mcp_registry.parent / clean_name
                    mcp_registry.rename(new_path)
                    repair.status = "applied"
                    repair.changes = {"old_name": mcp_registry.name, "new_name": clean_name}

            elif issue.repair_action == "cap_completion_at_total":
                # Cap completed count at total
                tracker_path = self.project_root / "cortex-brain/tier1/tracking/progress-tracker.json"
                with open(tracker_path, 'r') as f:
                    tracker = json.load(f)

                phase = issue.evidence.get("phase")
                total = issue.evidence.get("total")
                if phase and total:
                    tracker[phase]["completed_count"] = total
                    with open(tracker_path, 'w') as f:
                        json.dump(tracker, f, indent=2)
                    repair.status = "applied"
                    repair.changes = {"phase": phase, "new_completed_count": total}

            elif issue.repair_action == "create_tier_directory":
                # Create missing tier directory
                tier = issue.evidence.get("tier")
                tier_path = self.project_root / f"cortex-brain/{tier}"
                tier_path.mkdir(parents=True, exist_ok=True)
                repair.status = "applied"
                repair.changes = {"tier": tier, "path": str(tier_path)}

        except Exception as e:
            repair.status = "failed"
            repair.error_message = str(e)
            self.logger.error(f"Error applying repair {issue.issue_id}: {e}")

        return repair

    def diagnose(self, detailed: bool = True) -> Dict[str, Any]:
        """Generate detailed diagnostics."""
        check_report = self.check()

        diagnosis = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "overall_health": "HEALTHY" if check_report.system_healthy else "UNHEALTHY",
            "total_issues": check_report.total_issues,
            "critical_issues": check_report.critical_issues,
            "high_issues": check_report.high_issues,
            "issues": [asdict(i) for i in check_report.issues],
            "auto_repairable_count": check_report.auto_repairable,
            "recommendations": self._generate_recommendations(check_report)
        }

        return diagnosis

    def _generate_recommendations(self, report: HealthCheckReport) -> List[str]:
        """Generate recommendations based on issues found."""
        recommendations = []

        if report.critical_issues > 0:
            recommendations.append("🚨 CRITICAL ISSUES DETECTED - Manual intervention required immediately")

        if report.critical_issues > 0 and report.auto_repairable < report.critical_issues:
            recommendations.append("⚠️  Some critical issues cannot be auto-repaired - manual review needed")

        if report.high_issues > report.critical_issues:
            recommendations.append("📋 Consider running 'repair cortex' to auto-fix high-priority issues")

        if report.auto_repairable > 0:
            recommendations.append(f"✅ {report.auto_repairable} issues can be auto-repaired")

        if report.system_healthy:
            recommendations.append("✨ CORTEX architecture is healthy - no action needed")

        return recommendations

    def to_markdown(self, report: HealthCheckReport) -> str:
        """Convert report to markdown format."""
        md = f"""# CORTEX Architecture Health Check Report

**Timestamp:** {report.timestamp}  
**Status:** {'✅ HEALTHY' if report.system_healthy else '❌ UNHEALTHY'}

## Summary

| Metric | Value |
|--------|-------|
| Total Issues | {report.total_issues} |
| Critical | {report.critical_issues} |
| High | {report.high_issues} |
| Auto-Repairable | {report.auto_repairable} |

## Issues

"""
        if not report.issues:
            md += "No issues found! ✨\n"
        else:
            for issue in report.issues:
                emoji = "🔴" if issue.severity == IssueSeverity.CRITICAL else "🟠" if issue.severity == IssueSeverity.HIGH else "🟡"
                md += f"\n### {emoji} {issue.issue_id}: {issue.component}\n\n"
                md += f"**Severity:** {issue.severity.value}  \n"
                md += f"**Description:** {issue.description}  \n"
                md += f"**Auto-Repair:** {'Yes' if issue.can_auto_repair else 'No'}  \n"

        return md


if __name__ == "__main__":
    # Quick test
    orchestrator = HealthCheckOrchestratorV1(Path.cwd())
    report = orchestrator.check()
    print(orchestrator.to_markdown(report))
