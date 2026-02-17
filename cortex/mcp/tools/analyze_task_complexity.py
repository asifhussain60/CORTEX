"""
MCP Tool: Analyze Task Complexity

Exposes complexity analysis as MCP tool for transparency and user control.
Allows users to understand routing decisions before execution.

Authority: WORKFLOW-COMPLEXITY-GATE-001 / MCP-FIRST
Date: 2026-02-17
"""

from typing import Dict, Any, List, Optional
from cortex.intent_router.workflow_gate import (
    WorkflowComplexityRouter,
    Intent,
)


def analyze_task_complexity(
    operation: str,
    target_files: List[str],
    dependencies: Optional[List[str]] = None,
    risk_level: str = "MEDIUM"
) -> Dict[str, Any]:
    """
    Analyze task complexity to determine routing decision.
    
    Returns complexity score, recommended route, template/orchestrator, and rationale.
    
    Args:
        operation: Operation type (create, fix, refactor, test, etc.)
        target_files: List of file paths involved in operation
        dependencies: Optional list of dependencies
        risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
    
    Returns:
        Dict with:
        - complexity_score: Float (0.0-1.0)
        - route: "workflow_template" or "direct_orchestrator"
        - template_id: Template ID if routed to workflow
        - orchestrator: Orchestrator name if routed direct
        - rationale: Explanation of routing decision
        - thresholds: Complexity thresholds for reference
    
    Example:
        >>> result = analyze_task_complexity(
        ...     operation="fix",
        ...     target_files=["src/main.py"],
        ...     risk_level="LOW"
        ... )
        >>> print(result)
        {
            "complexity_score": 0.14,
            "route": "direct_orchestrator",
            "orchestrator": "RefactoringOrchestrator",
            "rationale": "Trivial operation, no workflow overhead",
            "thresholds": {
                "trivial": 0.15,
                "simple": 0.35,
                "moderate": 0.60,
                "complex": 0.75
            }
        }
    """
    router = WorkflowComplexityRouter()
    
    # Build intent from parameters
    intent = Intent(
        operation_type=operation,
        target_files=target_files,
        dependencies=dependencies or [],
        risk_level=risk_level,
        metadata={}
    )
    
    # Get routing decision
    decision = router.route(intent)
    
    # Build response
    response = {
        "complexity_score": decision.complexity,
        "route": decision.route.value,
        "rationale": decision.rationale,
        "requires_confirmation": decision.requires_confirmation,
        "thresholds": {
            "trivial": router.TRIVIAL_THRESHOLD,
            "simple": router.SIMPLE_THRESHOLD,
            "moderate": router.MODERATE_THRESHOLD,
            "complex": router.COMPLEX_THRESHOLD,
        }
    }
    
    # Add template or orchestrator based on route
    if decision.template_id:
        response["template_id"] = decision.template_id
    if decision.orchestrator:
        response["orchestrator"] = decision.orchestrator
    if decision.governance_gate:
        response["governance_gate"] = decision.governance_gate
    
    return response
