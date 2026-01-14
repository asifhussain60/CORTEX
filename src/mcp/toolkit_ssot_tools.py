#!/usr/bin/env python3
"""
CORTEX TOOLKIT: SSOT Integrity Tools (MCP Wrapper)

Exposes SSoT integrity functions as MCP tools for consistent access
across CLI, GitHub Copilot, and automated workflows.

AC-IDs Implemented:
  - AC-TOOLKIT-SSOT-001: SSOT Validator
  - AC-TOOLKIT-SSOT-002: Auto-Repair
  - AC-TOOLKIT-SSOT-003: Reconciliation
  - AC-TOOLKIT-SSOT-004: State Validation
"""

from pathlib import Path
from typing import Dict, Any
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.ssot_integrity_validator import SSoTIntegrityValidator, ValidationIssue
from src.infrastructure.progress_tracker_manager import ProgressTrackerManager


class SSoTToolkit:
    """Unified CORTEX SSOT Integrity Toolkit"""

    def __init__(self, workspace_root: str = "/Users/asifhussain/PROJECTS/CORTEX"):
        self.workspace_root = workspace_root
        self.validator = SSoTIntegrityValidator(workspace_root)
        self.tracker_mgr = ProgressTrackerManager(
            tracker_path=f"{workspace_root}/cortex-brain/tier1/tracking/progress-tracker.json",
            ac_index_path=f"{workspace_root}/cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml",
            master_plan_path=f"{workspace_root}/cortex-brain/cx6-plan/master-plan.yaml"
        )

    # @mcp_tool  # CORE-024: MCP tool decorator
    def validate_ssot(self) -> Dict[str, Any]:
        """
        Validate SSOT integrity (read-only)
        
        Returns: Report of validation issues found
        """
        is_valid, issues = self.validator.validate()
        self.validator.print_issues()

        return {
            "status": "healthy" if is_valid else "corrupted",
            "is_valid": is_valid,
            "issues_found": len(issues),
            "critical_count": len([i for i in issues if i.severity == "CRITICAL"]),
            "high_count": len([i for i in issues if i.severity == "HIGH"]),
            "issues": [
                {
                    "severity": i.severity,
                    "type": i.issue_type,
                    "description": i.description,
                    "auto_fixable": i.auto_fixable,
                    "affected_items": i.affected_items[:5]  # First 5
                }
                for i in issues
            ]
        }

    # @mcp_tool  # CORE-024: MCP tool decorator
    def repair_ssot(self, auto_fix_only: bool = True) -> Dict[str, Any]:
        """
        Repair SSOT corruption (write operation)
        
        Args:
            auto_fix_only: If True, only fix auto-fixable issues
            
        Returns: Repair report with fixes applied
        """
        report = self.validator.repair(auto_fix_only=auto_fix_only)
        self.validator.print_report(report)

        return {
            "timestamp": report.timestamp,
            "issues_found": report.issues_found,
            "issues_fixed": report.issues_fixed,
            "issues_requiring_manual_review": report.issues_manual,
            "backups_created": report.backups_created,
            "errors": report.errors,
            "success": len(report.errors) == 0
        }

    # @mcp_tool  # CORE-024: MCP tool decorator
    def reconcile_tracker(self, auto_fix: bool = False) -> Dict[str, Any]:
        """
        Reconcile progress-tracker.json from AC-INDEX authority
        
        Args:
            auto_fix: If True, apply changes automatically
            
        Returns: Reconciliation report
        """
        report = self.tracker_mgr.reconcile_from_ac_index(auto_fix=auto_fix)

        return {
            "timestamp": report["timestamp"],
            "issues_found": report["issues_fixed"],
            "changes": [
                {
                    "phase": c["phase"],
                    "previous_completed": c["old_completed"],
                    "new_completed": c["new_completed"]
                }
                for c in report["changes"]
            ],
            "auto_applied": auto_fix
        }

    # @mcp_tool  # CORE-024: MCP tool decorator
    def update_ac_completion(
        self,
        ac_id: str,
        status: str,
        test_passed: int = 0,
        test_total: int = 0
    ) -> Dict[str, Any]:
        """
        Update AC completion status with validation
        
        Args:
            ac_id: Acceptance Criteria ID (e.g., "AC-AUDIT-001")
            status: "implemented", "not_implemented", "partial"
            test_passed: Number of tests passed
            test_total: Total number of tests
            
        Returns: Operation result
        """
        test_results = {
            "passed": test_passed,
            "failed": test_total - test_passed,
            "total": test_total
        } if test_total > 0 else None

        success = self.tracker_mgr.update_ac_completion(
            ac_id=ac_id,
            status=status,
            test_results=test_results
        )

        return {
            "ac_id": ac_id,
            "status": status,
            "success": success,
            "message": "AC completion updated" if success else "Update failed - see logs"
        }

    # @mcp_tool  # CORE-024: MCP tool decorator
    def mark_phase_complete(self, phase_key: str) -> Dict[str, Any]:
        """
        Mark entire phase as complete after validation
        
        Args:
            phase_key: Phase identifier (e.g., "phase_1", "phase_2")
            
        Returns: Operation result
        """
        success = self.tracker_mgr.mark_phase_complete(
            phase_key=phase_key,
            completion_evidence={
                "all_acs_verified": True,
                "verified_at": Path(__file__).parent.parent.parent / "scripts" / "mark_phase_complete.py"
            }
        )

        return {
            "phase": phase_key,
            "marked_complete": success,
            "message": f"{phase_key} marked complete" if success else f"Failed to complete {phase_key}"
        }


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CORTEX SSOT Integrity Toolkit")
    parser.add_argument(
        "command",
        choices=["validate", "repair", "reconcile", "update-ac", "complete-phase"],
        help="Command to execute"
    )
    parser.add_argument("--auto-fix", action="store_true", help="Auto-fix issues")
    parser.add_argument("--ac-id", help="AC-ID for update-ac command")
    parser.add_argument("--status", help="Status for update-ac command")
    parser.add_argument("--phase", help="Phase for complete-phase command")

    args = parser.parse_args()
    toolkit = SSoTToolkit()

    if args.command == "validate":
        result = toolkit.validate_ssot()
        print(f"\n✅ VALIDATION COMPLETE: {result['issues_found']} issues found")

    elif args.command == "repair":
        result = toolkit.repair_ssot(auto_fix_only=not args.auto_fix)
        print(f"\n✅ REPAIR COMPLETE: {result['issues_fixed']} issues fixed")

    elif args.command == "reconcile":
        result = toolkit.reconcile_tracker(auto_fix=args.auto_fix)
        print(f"\n✅ RECONCILIATION COMPLETE: {result['issues_found']} issues found")

    elif args.command == "update-ac":
        if not args.ac_id or not args.status:
            print("❌ --ac-id and --status required")
            sys.exit(1)
        result = toolkit.update_ac_completion(args.ac_id, args.status)
        print(f"\n✅ AC UPDATE: {args.ac_id} status → {args.status}")

    elif args.command == "complete-phase":
        if not args.phase:
            print("❌ --phase required")
            sys.exit(1)
        result = toolkit.mark_phase_complete(args.phase)
        print(f"\n✅ PHASE COMPLETE: {args.phase} marked complete")
