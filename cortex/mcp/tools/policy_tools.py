"""
MCP Tools for Policy Engine and Compliance Checking

AC_START: AC-PHASE60.0-S3-001
Authority: phase-60-enterprise-pattern-registry.yaml Stage 3
Purpose: Expose policy engine functionality via MCP tools
         - cortex_policy_evaluate - Evaluate data against policy
         - cortex_compliance_check - Check compliance across policies
         - cortex_policy_register - Register custom policies
         - cortex_get_compliance_report - Retrieve compliance reports

Tests Target: 8 tests (MCP tool invocation, payload validation, report generation)
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.governance.policy_engine import (
    PolicyEngine,
    PolicyLevel,
    PolicyMetadata,
)

# ============================================================================
# MCP Tool Implementation
# ============================================================================

class PolicyMCPTools:
    """MCP tools for policy engine access."""

    def __init__(self):
        """Initialize MCP tools with policy engine."""
        self.engine = PolicyEngine()

    def cortex_policy_evaluate(
        self,
        policy_id: str,
        data: Dict[str, Any],
        return_details: bool = True
    ) -> Dict[str, Any]:
        """Evaluate data against a policy.

        MCP Tool: cortex_policy_evaluate

        Args:
            policy_id: ID of policy to evaluate
            data: Data to evaluate
            return_details: Include violation details

        Returns:
            Evaluation result with compliance status
        """
        report = self.engine.evaluate_data(policy_id, data)

        result = {
            "tool": "cortex_policy_evaluate",
            "status": "success",
            "evaluated_at": report.evaluated_at,
            "policy_id": policy_id,
            "compliant": report.compliant,
            "compliance_status": report.status.value,
            "score": round(report.score, 3),
            "violation_count": len(report.violations),
            "warning_count": len(report.warnings)
        }

        if return_details:
            result["violations"] = [
                {
                    "rule_id": v.rule_id,
                    "description": v.description,
                    "severity": v.severity
                }
                for v in report.violations
            ]
            result["warnings"] = report.warnings

        return result

    def cortex_compliance_check(
        self,
        policy_ids: List[str],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance across multiple policies.

        MCP Tool: cortex_compliance_check

        Args:
            policy_ids: List of policy IDs to check
            data: Data to evaluate

        Returns:
            Compliance check results across all policies
        """
        reports = self.engine.evaluate_multiple_policies(policy_ids, data)

        compliant_count = sum(1 for r in reports if r.compliant)
        total_count = len(reports)
        avg_score = sum(r.score for r in reports) / total_count if total_count > 0 else 0

        return {
            "tool": "cortex_compliance_check",
            "status": "success",
            "evaluated_at": datetime.utcnow().isoformat(),
            "policy_count": total_count,
            "compliant_policies": compliant_count,
            "compliance_percentage": round((compliant_count / total_count * 100) if total_count > 0 else 0, 1),
            "average_score": round(avg_score, 3),
            "policies": [
                {
                    "policy_id": r.policy_id,
                    "compliant": r.compliant,
                    "score": round(r.score, 3),
                    "violation_count": len(r.violations)
                }
                for r in reports
            ]
        }

    def cortex_policy_register(
        self,
        policy_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register a custom policy.

        MCP Tool: cortex_policy_register

        Args:
            policy_definition: Policy definition (id, name, level, rules, etc.)

        Returns:
            Registration result
        """
        try:
            # Parse policy definition
            from cortex.governance.policy_engine import PolicyRule, RuleOperator

            # Convert level string to enum
            level = PolicyLevel(policy_definition.get('level', 'warning'))

            # Parse rules
            rules = []
            for rule_data in policy_definition.get('rules', []):
                operator = RuleOperator(rule_data.get('operator', 'equals'))
                rule = PolicyRule(
                    id=rule_data.get('id'),
                    description=rule_data.get('description'),
                    operator=operator,
                    field=rule_data.get('field'),
                    value=rule_data.get('value'),
                    severity=rule_data.get('severity', 'error'),
                    error_message=rule_data.get('error_message')
                )
                rules.append(rule)

            # Create and register policy
            policy = PolicyMetadata(
                id=policy_definition.get('id'),
                name=policy_definition.get('name'),
                description=policy_definition.get('description', ''),
                level=level,
                rules=rules,
                frameworks=policy_definition.get('frameworks', []),
                tags=policy_definition.get('tags', []),
                author=policy_definition.get('author', 'api'),
                version=policy_definition.get('version', '1.0')
            )

            success, message = self.engine.register_policy(policy)

            return {
                "tool": "cortex_policy_register",
                "status": "success" if success else "error",
                "message": message,
                "policy_id": policy.id if success else None
            }

        except Exception as e:
            return {
                "tool": "cortex_policy_register",
                "status": "error",
                "message": f"Error registering policy: {str(e)}"
            }

    def cortex_get_compliance_report(
        self,
        policy_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get compliance evaluation reports.

        MCP Tool: cortex_get_compliance_report

        Args:
            policy_id: Optional filter by policy ID
            limit: Maximum number of reports to return

        Returns:
            List of compliance reports
        """
        history = self.engine.get_evaluation_history(policy_id)

        # Sort by evaluated_at descending and limit
        sorted_history = sorted(
            history,
            key=lambda r: r.evaluated_at,
            reverse=True
        )[:limit]

        return {
            "tool": "cortex_get_compliance_report",
            "status": "success",
            "total_evaluations": len(history),
            "returned_count": len(sorted_history),
            "reports": [r.to_dict() for r in sorted_history]
        }

    def cortex_list_policies(self) -> Dict[str, Any]:
        """List all registered policies.

        MCP Tool: cortex_list_policies

        Returns:
            List of policies with metadata
        """
        policies = self.engine.list_policies()

        return {
            "tool": "cortex_list_policies",
            "status": "success",
            "policy_count": len(policies),
            "policies": [
                {
                    "id": p.id,
                    "name": p.name,
                    "level": p.level.value,
                    "frameworks": p.frameworks,
                    "rule_count": len(p.rules),
                    "tags": p.tags
                }
                for p in policies
            ]
        }

    def cortex_get_policies_by_framework(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """Get policies for a compliance framework.

        MCP Tool: cortex_get_policies_by_framework

        Args:
            framework: Framework name (SOC2, HIPAA, etc.)

        Returns:
            Policies matching framework
        """
        policies = self.engine.get_policies_by_framework(framework)

        return {
            "tool": "cortex_get_policies_by_framework",
            "status": "success",
            "framework": framework,
            "policy_count": len(policies),
            "policies": [
                {
                    "id": p.id,
                    "name": p.name,
                    "level": p.level.value,
                    "rule_count": len(p.rules)
                }
                for p in policies
            ]
        }


# ============================================================================
# Global MCP Tools Instance
# ============================================================================

_policy_mcp_tools = None


def get_policy_mcp_tools() -> PolicyMCPTools:
    """Get or create policy MCP tools instance."""
    global _policy_mcp_tools
    if _policy_mcp_tools is None:
        _policy_mcp_tools = PolicyMCPTools()
    return _policy_mcp_tools


# AC_COMPLETE: AC-PHASE60.0-S3-001 ✅
# ✅ 6 MCP tools for policy engine access
# ✅ Policy evaluation and compliance checking
# ✅ Batch compliance checking
# ✅ Report history retrieval
# ✅ Framework-based policy querying
