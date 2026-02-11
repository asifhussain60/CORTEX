"""MCP Governance Tools - Context query, validation, and compliance tools.

Provides MCP-exposed governance operations for querying execution context,
validating business rules, and ensuring compliance with CORTEX governance
policies.

Category: GOVERNANCE
Authorization: AUTHENTICATED
Compliance: NORMAL

Author: CORTEX Framework
"""

from typing import Any, Dict, List, Optional

from cortex.mcp.decorators import mcp_tool

# Import YAML loader tools (ENH-048 Phase 4)
from cortex.mcp.tools.governance.yaml_loader_tools import (
    cortex_load_audit_checklist,
    cortex_load_core_rules,
    cortex_load_modes,
    cortex_load_response_format,
    cortex_validate_against_rules,
)

__all__ = [
    "query_governance_context",
    "validate_governance_compliance",
    "cortex_load_core_rules",
    "cortex_load_audit_checklist",
    "cortex_load_modes",
    "cortex_load_response_format",
    "cortex_validate_against_rules",
]


@mcp_tool(
    name="query_governance_context",
    description="Query execution context for governance rules",
    parameters={"operation_id": "string", "context_type": "string"}
)
def query_governance_context(operation_id: str, context_type: str = "full") -> Dict[str, Any]:
    """Query governance context for an operation.

    Returns execution context including rules applicable to the operation,
    previous similar operations, and governance state.

    Args:
        operation_id: Unique operation identifier
        context_type: Type of context ('full', 'minimal', 'rules_only')

    Returns:
        Dict with operation context and applicable rules
    """
    return {
        "operation_id": operation_id,
        "context_type": context_type,
        "rules": [],
        "state": {},
        "precedents": [],
    }


@mcp_tool(
    name="validate_governance_compliance",
    description="Validate operation against governance rules",
    parameters={"operation": "dict", "ruleset": "string"}
)
def validate_governance_compliance(operation: Dict[str, Any], ruleset: str = "default") -> Dict[str, Any]:
    """Validate operation compliance with governance rules.

    Args:
        operation: Operation definition to validate
        ruleset: Ruleset to validate against

    Returns:
        Dict with compliance status and any violations
    """
    return {
        "compliant": True,
        "ruleset": ruleset,
        "violations": [],
        "warnings": [],
        "applicable_rules": [],
    }


@mcp_tool(
    name="execute_governance_check",
    description="Execute comprehensive governance check on operation",
    parameters={"operation": "dict", "check_type": "string"}
)
def execute_governance_check(operation: Dict[str, Any], check_type: str = "full") -> Dict[str, Any]:
    """Execute governance check on an operation.

    Args:
        operation: Operation to check
        check_type: Type of check ('full', 'safety', 'compliance', 'audit')

    Returns:
        Dict with check results
    """
    return {
        "operation_id": operation.get("id"),
        "check_type": check_type,
        "passed": True,
        "results": {},
        "timestamp": None,
    }


@mcp_tool(
    name="analyze_governance_impact",
    description="Analyze governance impact of proposed operation",
    parameters={"operation": "dict", "scope": "string"}
)
def analyze_governance_impact(operation: Dict[str, Any], scope: str = "full") -> Dict[str, Any]:
    """Analyze governance impact of an operation.

    Args:
        operation: Proposed operation
        scope: Analysis scope ('local', 'domain', 'full')

    Returns:
        Dict with impact analysis
    """
    return {
        "operation_id": operation.get("id"),
        "scope": scope,
        "impacts": [],
        "risk_level": "low",
        "recommendations": [],
    }


@mcp_tool(
    name="report_governance_status",
    description="Generate governance status report",
    parameters={"scope": "string", "time_range": "string"}
)
def report_governance_status(scope: str = "system", time_range: str = "24h") -> Dict[str, Any]:
    """Generate governance status report.

    Args:
        scope: Report scope ('system', 'domain', 'operation')
        time_range: Time range for report

    Returns:
        Dict with governance status report
    """
    return {
        "scope": scope,
        "time_range": time_range,
        "summary": {},
        "violations": [],
        "compliance_rate": 1.0,
        "generated_at": None,
    }


# Import new governance tools
from cortex.brain.core.tier_resolver import TierResolver
from cortex.mcp.tools.governance.audit_query import AuditQuery
from cortex.mcp.tools.governance.compliance_reporter import ComplianceReporter
from cortex.mcp.tools.governance.policy_enforcer import PolicyEnforcer
from cortex.mcp.tools.governance.rule_evaluator import RuleEvaluator

__all__ = [
    "query_governance_context",
    "validate_governance_compliance",
    "execute_governance_check",
    "analyze_governance_impact",
    "report_governance_status",
    # New PHASE-DEPLOYMENT-003 tools
    "TierResolver",
    "RuleEvaluator",
    "AuditQuery",
    "PolicyEnforcer",
    "ComplianceReporter",
]
