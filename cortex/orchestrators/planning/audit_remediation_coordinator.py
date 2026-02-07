"""
AC-ENH-059-005: AuditRemediationCoordinator - Implementation

Coordinates audit results → remediation plan → user selection flow.
Implements ENH-059: Audit-Driven Auto-Planning specification.

Authority: ENH-059 (P1, 8.5 confidence)
"""

from typing import Dict, List, Any
import logging

from cortex.orchestrators.planning.remediation_plan_generator import (
    RemediationPlanGenerator,
    RemediationPlan,
    AuditFinding
)
from cortex.orchestrators.planning.remediation_plan_formatter import (
    RemediationPlanFormatter
)

logger = logging.getLogger(__name__)


# ============================================================================
# AUDIT REMEDIATION COORDINATOR
# ============================================================================

class AuditRemediationCoordinator:
    """
    Coordinates audit-to-remediation workflow.
    
    Flow:
    1. Receives audit results
    2. Converts to AuditFinding objects
    3. Generates remediation plan
    4. Formats plan with execution options
    5. Processes user selection
    6. Returns execution mode
    """
    
    def __init__(self):
        """Initialize coordinator with generator and formatter."""
        self.generator = RemediationPlanGenerator()
        self.formatter = RemediationPlanFormatter()
        logger.info("AuditRemediationCoordinator initialized")
    
    def generate_remediation_plan(
        self,
        audit_results: Dict[str, Any]
    ) -> RemediationPlan:
        """
        Generate remediation plan from audit results.
        
        Args:
            audit_results: Dict with 'findings' key containing audit findings
            
        Returns:
            RemediationPlan object
        """
        # Convert audit results to AuditFinding objects
        findings = self._convert_audit_findings(audit_results)
        
        # Generate plan
        plan = self.generator.generate_plan(findings)
        
        logger.info(
            f"Generated plan: {len(plan.phases)} phases, "
            f"{plan.total_effort_minutes}min effort"
        )
        
        return plan
    
    def format_plan_with_prompt(
        self,
        plan: RemediationPlan,
        audit_results: Dict[str, Any]
    ) -> str:
        """
        Format plan as markdown with audit summary and user prompt.
        
        Args:
            plan: RemediationPlan to format
            audit_results: Original audit results for summary
            
        Returns:
            Markdown string with plan and prompt
        """
        # Build audit summary section
        audit_summary = self._build_audit_summary(audit_results)
        
        # Format plan
        formatted = self.formatter.format_plan(plan)
        
        # Insert audit summary after header (before "### 📊 Issues Found")
        parts = formatted.split("### 📊 Issues Found", 1)
        if len(parts) == 2:
            formatted = parts[0] + audit_summary + "\n### 📊 Issues Found" + parts[1]
        else:
            # Fallback: prepend audit summary
            formatted = audit_summary + "\n\n" + formatted
        
        logger.info("Formatted remediation plan with audit summary and user prompt")
        
        return formatted
    
    def _build_audit_summary(self, audit_results: Dict[str, Any]) -> str:
        """
        Build audit summary section from audit results.
        
        Args:
            audit_results: Audit results dict
            
        Returns:
            Markdown string with audit summary
        """
        summary = audit_results.get("summary", {})
        
        total_issues = summary.get("total_issues", 0)
        validators_run = summary.get("validators_run", 0)
        checks_executed = summary.get("checks_executed", 0)
        execution_time = audit_results.get("execution_time_seconds", 0)
        
        lines = [
            "### 🔍 Audit Summary",
            "",
            f"- **Total Issues:** {total_issues}",
            f"- **Validators Run:** {validators_run}",
            f"- **Checks Executed:** {checks_executed}",
            f"- **Execution Time:** {execution_time:.2f}s",
            ""
        ]
        
        return "\n".join(lines)
    
    def process_user_selection(self, option: int) -> Dict[str, Any]:
        """
        Process user's execution mode selection.
        
        Args:
            option: User selection (1-4)
            
        Returns:
            Dict with mode and execution parameters
        """
        if option == 1:
            # Auto-execute (autonomous mode)
            return {
                "mode": "AUTONOMOUS",
                "proceed": True,
                "autonomous": True,
                "description": "Auto-execute all phases with test gating"
            }
        
        elif option == 2:
            # Phase-by-phase (interactive, DEFAULT)
            return {
                "mode": "INTERACTIVE",
                "proceed": True,
                "autonomous": False,
                "description": "Execute phase-by-phase with step-by-step approval"
            }
        
        elif option == 3:
            # Review only (no execution)
            return {
                "mode": "REVIEW_ONLY",
                "proceed": False,
                "autonomous": False,
                "description": "Save plan for review, no execution"
            }
        
        elif option == 4:
            # Cancel
            return {
                "mode": "CANCEL",
                "proceed": False,
                "autonomous": False,
                "description": "Operation cancelled without changes"
            }
        
        else:
            # Invalid option defaults to cancel
            return {
                "mode": "CANCEL",
                "proceed": False,
                "autonomous": False,
                "message": f"Invalid option: {option}. Must be 1-4.",
                "description": "Invalid selection - cancelled"
            }
    
    def _convert_audit_findings(
        self,
        audit_results: Dict[str, Any]
    ) -> List[AuditFinding]:
        """
        Convert audit results dict to AuditFinding objects.
        
        Handles two formats:
        1. Simple format: {"findings": [{severity, category, ...}]}
        2. Audit tool format: {"validation_results": {"P0_CRITICAL": [...], "P1_HIGH": [...]}}
        
        Args:
            audit_results: Audit results with 'findings' or 'validation_results' key
            
        Returns:
            List of AuditFinding objects
        """
        findings = []
        
        # Format 1: Simple findings array
        if "findings" in audit_results:
            findings_data = audit_results.get("findings", [])
            for data in findings_data:
                finding = AuditFinding(
                    severity=data.get("severity", "P2"),
                    category=data.get("category", "Unknown"),
                    description=data.get("description", ""),
                    files_affected=data.get("files_affected", []),
                    estimated_effort_minutes=data.get("estimated_effort_minutes", 30)
                )
                findings.append(finding)
        
        # Format 2: Audit tool format (validation_results)
        elif "validation_results" in audit_results:
            validation_results = audit_results["validation_results"]
            
            # Map priority levels to severity
            priority_map = {
                "P0_CRITICAL": "P0",
                "P0": "P0",
                "P1_HIGH": "P1",
                "P1": "P1",
                "P2_MEDIUM": "P2",
                "P2": "P2",
                "P3_LOW": "P3",
                "P3": "P3"
            }
            
            for priority_key, issues in validation_results.items():
                severity = priority_map.get(priority_key, "P2")
                
                for issue in issues:
                    finding = AuditFinding(
                        severity=severity,
                        category=issue.get("check_id", "Unknown"),
                        description=issue.get("description", "") + f" ({issue.get('recommendation', '')})",
                        files_affected=[issue.get("file", "")] if issue.get("file") else [],
                        estimated_effort_minutes=self._estimate_effort(severity, issue)
                    )
                    findings.append(finding)
        
        logger.info(f"Converted {len(findings)} audit findings")
        
        return findings
    
    def _estimate_effort(self, severity: str, issue: Dict[str, Any]) -> int:
        """
        Estimate effort in minutes based on severity and issue type.
        
        Args:
            severity: P0, P1, P2, or P3
            issue: Issue data dict
            
        Returns:
            Estimated minutes
        """
        base_effort = {
            "P0": 60,  # Critical - 1 hour
            "P1": 45,  # High - 45 minutes
            "P2": 30,  # Medium - 30 minutes
            "P3": 15   # Low - 15 minutes
        }
        
        return base_effort.get(severity, 30)
