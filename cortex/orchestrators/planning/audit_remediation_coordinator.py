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
        # Format plan
        formatted = self.formatter.format_plan(plan)
        
        logger.info("Formatted remediation plan with user prompt")
        
        return formatted
    
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
                "mode": "autonomous",
                "autonomous": True,
                "should_execute": True,
                "description": "Auto-execute all phases with test gating"
            }
        
        elif option == 2:
            # Phase-by-phase (interactive, DEFAULT)
            return {
                "mode": "interactive",
                "autonomous": False,
                "should_execute": True,
                "description": "Execute phase-by-phase with approval"
            }
        
        elif option == 3:
            # Review only (no execution)
            return {
                "mode": "review",
                "autonomous": False,
                "should_execute": False,
                "description": "Save plan to file, no execution"
            }
        
        elif option == 4:
            # Cancel
            return {
                "mode": "cancel",
                "autonomous": False,
                "should_execute": False,
                "description": "Exit without changes"
            }
        
        else:
            # Invalid option
            return {
                "mode": "error",
                "autonomous": False,
                "should_execute": False,
                "message": f"Invalid option: {option}. Must be 1-4.",
                "description": "Invalid selection"
            }
    
    def _convert_audit_findings(
        self,
        audit_results: Dict[str, Any]
    ) -> List[AuditFinding]:
        """
        Convert audit results dict to AuditFinding objects.
        
        Args:
            audit_results: Audit results with 'findings' key
            
        Returns:
            List of AuditFinding objects
        """
        findings_data = audit_results.get("findings", [])
        
        findings = []
        for data in findings_data:
            finding = AuditFinding(
                severity=data.get("severity", "P2"),
                category=data.get("category", "Unknown"),
                description=data.get("description", ""),
                files_affected=data.get("files_affected", []),
                estimated_effort_minutes=data.get("estimated_effort_minutes", 30)
            )
            findings.append(finding)
        
        logger.info(f"Converted {len(findings)} audit findings")
        
        return findings
