"""
Holistic Validation MCP Tool (Phase 48 + Phase 54 S3).

Provides unified pre-implementation validation combining registry checks,
dependency analysis, risk scoring, architecture drift detection, and
challenge gate generation.

MCP Tools:
- cortex_validate_holistically: Phase 48 holistic validation gate

Author: Asif Hussain
Phase: 54 - MCP Unified Routing
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_validate_holistically",
    description="Unified pre-implementation validation gate (Phase 48)",
    parameters={
        "operation": "string",
        "target": "string",
        "scope": "array",
        "challenge_required": "boolean",
    }
)
def cortex_validate_holistically(
    operation: str,
    target: str,
    scope: Optional[List[str]] = None,
    challenge_required: bool = True,
) -> Dict[str, Any]:
    """
    Holistic validation gate for IMPLEMENT/FIX/REFACTOR operations.

    Validates:
    1. Registry consistency (orchestrators, wiring, tools)
    2. Dependency graph (circular dependencies, missing deps)
    3. Regression risk scoring (0.0 - 1.0)
    4. Architecture drift detection (CORE rules compliance)
    5. Mandatory challenge gate (alternatives with ROI)
    6. CORTEX brain context (self-analysis for CORTEX repo)

    Args:
        operation: Operation type (IMPLEMENT, FIX, REFACTOR)
        target: Target file/module path
        scope: Validation scope (orchestrators, wiring, tests, etc.)
        challenge_required: Whether to generate challenge alternatives

    Returns:
        Dict with verdict, risk_score, violations, challenge, remediation
    """
    try:
        from cortex.governance.enforcement.holistic_validator import HolisticValidator

        validator = HolisticValidator()

        # Default scope if not provided
        if not scope:
            scope = ["orchestrators", "wiring", "dependencies", "architecture"]

        # Run holistic validation
        result = validator.validate_operation(
            operation=operation,
            target=Path(target),
            scope=scope,
            challenge_required=challenge_required
        )

        # Extract validation results
        verdict = result.get("verdict", "UNKNOWN")  # PASS, WARN, BLOCK
        risk_score = result.get("risk_score", 0.0)
        violations = result.get("violations", [])
        warnings = result.get("warnings", [])
        challenge = result.get("challenge", None)
        remediation = result.get("remediation", [])

        # Format response
        response = {
            "status": "success",
            "verdict": verdict,
            "risk_score": risk_score,
            "operation": operation,
            "target": target,
            "scope": scope,
            "passed": verdict in ["PASS", "WARN"],
            "blocked": verdict == "BLOCK",
        }

        # Add violations if any
        if violations:
            response["violations"] = [
                {
                    "rule": v.get("rule", ""),
                    "severity": v.get("severity", ""),
                    "message": v.get("message", ""),
                    "location": v.get("location", "")
                }
                for v in violations
            ]

        # Add warnings if any
        if warnings:
            response["warnings"] = warnings

        # Add challenge if generated
        if challenge:
            response["challenge"] = {
                "has_disagreement": challenge.get("has_disagreement", False),
                "disagreement_type": challenge.get("disagreement_type", ""),
                "user_approach": challenge.get("user_approach", ""),
                "cortex_analysis": challenge.get("cortex_analysis", ""),
                "alternatives": challenge.get("alternatives", []),
                "recommended": challenge.get("recommended", ""),
                "reasoning": challenge.get("reasoning", "")
            }

        # Add remediation steps if blocked
        if verdict == "BLOCK" and remediation:
            response["remediation"] = remediation

        # Add evidence
        response["evidence"] = {
            "registry_check": result.get("registry_status", "unknown"),
            "dependency_graph": result.get("dependency_status", "unknown"),
            "architecture_drift": result.get("drift_detected", False),
            "cortex_brain_analysis": result.get("brain_analysis", None)
        }

        return response

    except Exception as e:
        logger.error(f"Holistic validation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Validation failed: {str(e)}",
            "verdict": "BLOCK",
            "passed": False,
            "blocked": True,
            "remediation": [
                "Fix holistic validator setup",
                f"Error: {str(e)}"
            ]
        }
