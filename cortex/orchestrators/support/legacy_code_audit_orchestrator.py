"""
Phase 61: Legacy Code Audit - LegacyCodeAuditOrchestrator

Orchestrates legacy code detection, approval workflow, and reporting.
Integrates with governance and audit trail systems.

AC_START: AC-PHASE61-003
Description: LegacyCodeAuditOrchestrator implementation
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from cortex.orchestrators.support.legacy_code_audit import (
    AuditReport,
    LegacyCodeAudit,
    LegacyCodeCategory,
    LegacyCodeIssue,
    RemovalApprovalWorkflow,
)


class LegacyCodeAuditOrchestrator:
    """
    Orchestrates complete legacy code audit workflow.

    Responsibilities:
    1. Execute comprehensive repository scan
    2. Categorize issues (deprecated, duplicate, orphaned, superseded)
    3. Generate audit reports
    4. Manage user approval workflow
    5. Integrate with governance audit trail
    """

    def __init__(self, repo_root: Path):
        """Initialize orchestrator"""
        self.repo_root = Path(repo_root)
        self.audit = LegacyCodeAudit(self.repo_root)
        self.workflow = RemovalApprovalWorkflow()
        self.report = AuditReport()
        self.issues: List[LegacyCodeIssue] = []
        self.execution_timestamp = datetime.utcnow().isoformat()

    def execute_audit(self) -> Dict[str, object]:
        """
        Execute complete audit workflow.

        Returns:
            Dict with audit results and recommendations
        """
        # Phase 1: Scan repository
        self.issues = self.audit.scan_repository()

        # Phase 2: Build report
        self.report.from_audit(self.audit)
        report_dict = self.report.generate_report()

        # Phase 3: Identify removal candidates
        candidates = self.audit.generate_removal_candidates()

        # Phase 4: Prepare for approval
        for candidate in candidates:
            self.workflow.submit_for_approval(candidate)

        return {
            "status": "audit_complete",
            "timestamp": self.execution_timestamp,
            "total_issues": len(self.issues),
            "pending_approvals": len(self.workflow.pending_removals),
            "summary": report_dict,
            "categories": {
                "deprecated": self.report.deprecated_count,
                "duplicate": self.report.duplicate_count,
                "orphaned": self.report.orphaned_count,
                "superseded": self.report.superseded_count,
            },
        }

    def get_audit_results(self) -> List[LegacyCodeIssue]:
        """Get all detected issues"""
        return self.issues

    def get_high_priority_issues(self) -> List[LegacyCodeIssue]:
        """Get HIGH severity issues"""
        return [
            issue for issue in self.issues
            if issue.severity == "HIGH"
        ]

    def get_removal_candidates(self) -> List[LegacyCodeIssue]:
        """Get safe-to-remove candidates awaiting approval"""
        return self.workflow.get_pending_approvals()

    def approve_removal(self, file_path: Path) -> bool:
        """Approve removal of file"""
        for issue in self.workflow.pending_removals:
            if issue.file_path == file_path:
                self.workflow.approve_removal(issue)
                return True
        return False

    def reject_removal(self, file_path: Path, reason: str) -> bool:
        """Reject removal of file"""
        for issue in self.workflow.pending_removals:
            if issue.file_path == file_path:
                self.workflow.reject_removal(issue, reason)
                return True
        return False

    def get_approved_removals(self) -> List[LegacyCodeIssue]:
        """Get approved removals"""
        return self.workflow.approved_removals

    def generate_audit_report(self, output_path: Path) -> None:
        """Generate and export audit report to YAML"""
        self.report.export_to_yaml(output_path)

    def get_removal_cost_analysis(self) -> Dict[str, object]:
        """Analyze impact of potential removals"""
        safe_removals = self.audit.generate_removal_candidates()

        total_lines = 0
        affected_modules = set()

        for issue in safe_removals:
            try:
                with open(issue.file_path, 'r') as f:
                    total_lines += len(f.readlines())
                    affected_modules.add(str(issue.file_path.parent))
            except Exception:
                pass

        return {
            "safe_removal_count": len(safe_removals),
            "estimated_lines_to_remove": total_lines,
            "affected_modules": len(affected_modules),
            "risk_level": "LOW" if len(safe_removals) < 10 else "MEDIUM",
            "recommendation": "Safe to proceed with batch removal" if len(safe_removals) > 0 else "No immediate removal candidates",
        }

    def generate_migration_guide(self) -> Dict[str, object]:
        """Generate migration guide for superseded code"""
        migration_items = [
            issue for issue in self.issues
            if issue.category == LegacyCodeCategory.SUPERSEDED
        ]

        guide = {
            "title": "Legacy Code Migration Guide",
            "total_items": len(migration_items),
            "migrations": []
        }

        for item in migration_items:
            guide["migrations"].append({
                "old_file": str(item.file_path),
                "reason": item.reason,
                "recommendation": item.recommendation,
                "priority": item.severity,
            })

        return guide

    def export_governance_audit(self, output_path: Path) -> None:
        """Export governance audit trail"""
        audit_data = {
            "phase": "phase-61",
            "operation": "legacy_code_audit",
            "timestamp": self.execution_timestamp,
            "repository": str(self.repo_root),
            "audit_summary": self.report.generate_report(),
            "categories": {
                "deprecated": self.report.deprecated_count,
                "duplicate": self.report.duplicate_count,
                "orphaned": self.report.orphaned_count,
                "superseded": self.report.superseded_count,
            },
            "removal_candidates": {
                "pending": len(self.workflow.pending_removals),
                "approved": len(self.workflow.approved_removals),
                "rejected": len(self.workflow.rejected_removals),
            },
        }

        with open(output_path, 'w') as f:
            json.dump(audit_data, f, indent=2)


# AC_COMPLETE: AC-PHASE61-003 ✅
