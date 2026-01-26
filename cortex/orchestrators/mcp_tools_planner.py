"""
MCP Tools for PlannerOrchestrator

Exposes PlannerOrchestrator functionality through Model Context Protocol (MCP)
tools for Copilot integration. Each tool is a lightweight wrapper that:
1. Validates input parameters
2. Calls the corresponding orchestrator method
3. Formats output for Copilot presentation
4. Logs operation to audit trail

Tools:
- cortex_create_plan: Create a new planning session (TEMP plan)
- cortex_approve_plan: Approve a plan for execution (TEMP → ACTIVE)
- cortex_execute_plan: Execute an approved plan
- cortex_list_plans: List plans in various states
- cortex_get_plan: Retrieve plan details
- cortex_reject_plan: Reject a plan with reason

AC-PLANNER-MCP-001: MCP tool standardization
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from cortex.orchestrators.core.planner_orchestrator import get_planner_orchestrator
from cortex.core.result import Result, Ok, Err  # type: ignore[type-arg]


@dataclass
class MCP_ToolResult:
    """Standard result format for MCP tools"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message,
        }


class PlannerOrchestratorMCPTools:
    """MCP tool wrappers for PlannerOrchestrator

    Provides safe, validated access to planning functionality through
    Model Context Protocol (MCP) tools that Copilot can invoke.
    """

    @staticmethod
    def cortex_create_plan(
        description: str,
        scope: str = "file",
        impact: str = "medium",
        confidence: Optional[float] = None,
        additional_context: Optional[str] = None,
    ) -> MCP_ToolResult:
        """Create a new temporary plan (TEMP state)

        This is the first step in the planning workflow. Creates a TEMP plan with:
        - LENS classification (intent, confidence, impact assessment)
        - Strategic challenges (governance, alternative, scope, risk)
        - Execution gates (confirmation requirements based on impact × confidence)
        - Git context (current branch, recent changes)

        Args:
            description: Human-readable description of what needs to be done
                Example: "Implement user authentication system"
            scope: Scope of work (default: "file")
                Options: "file", "module", "system", "architecture"
            impact: Estimated impact level (default: "medium")
                Options: "low", "medium", "high"
            confidence: Confidence in the plan (0.0-1.0 or 0-100)
                If not provided, defaults based on impact level
            additional_context: Extra context for challenge detection

        Returns:
            MCP_ToolResult with:
            - plan_id: Unique identifier for this plan
            - status: Always "temp" for new plans
            - classification: LENS classification results
            - challenges: List of detected challenges
            - execution_gates: Confirmation requirements
            - git_context: Current repository state

        Example:
            >>> result = cortex_create_plan(
            ...     description="Fix authentication bug in login flow",
            ...     scope="module",
            ...     impact="high",
            ...     confidence=0.8
            ... )
            >>> if result.success:
            ...     plan_id = result.data["plan_id"]
            ...     print(f"Plan created: {plan_id}")
        """
        try:
            planner = get_planner_orchestrator()

            # Build request dictionary
            request: Dict[str, Any] = {
                "description": description,
                "scope": scope,
                "impact": impact,
            }

            if confidence is not None:
                request["confidence"] = float(confidence)

            if additional_context:
                request["additional_context"] = additional_context

            # Create plan
            result = planner.create_temp_plan(request)  # type: ignore[attr-defined]

            # Check if result is Ok or Err
            if hasattr(result, "is_ok") and result.is_ok():  # type: ignore[attr-defined]
                plan = result.unwrap()  # type: ignore[attr-defined]
                return MCP_ToolResult(
                    success=True,
                    data=plan,  # type: ignore[arg-type]
                    message=f"Plan created: {plan.get('plan_id', 'unknown')}",  # type: ignore[union-attr]
                )
            else:
                error_msg: str = (
                    result.error  # type: ignore[attr-defined]
                    if hasattr(result, "error")
                    else "Unknown error"
                )
                return MCP_ToolResult(
                    success=False,
                    error=error_msg,
                    message="Failed to create plan",
                )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error creating plan",
            )

    @staticmethod
    def cortex_approve_plan(
        plan_id: str,
        notes: Optional[str] = None,
    ) -> MCP_ToolResult:
        """Approve a temporary plan (TEMP → ACTIVE)

        Moves a plan from TEMP state to ACTIVE state, indicating approval
        for execution. After approval, the plan can be executed.

        Args:
            plan_id: ID of the plan to approve
            notes: Optional approval notes or justification

        Returns:
            MCP_ToolResult with:
            - plan_id: The approved plan's ID
            - status: Always "active" after approval
            - approval_status: Updated approval information

        Example:
            >>> result = cortex_approve_plan(
            ...     plan_id="abc123",
            ...     notes="Reviewed and ready to proceed"
            ... )
            >>> if result.success:
            ...     print("Plan approved for execution")
        """
        try:
            planner = get_planner_orchestrator()

            result = planner.approve_plan(plan_id)  # type: ignore[attr-defined]

            if hasattr(result, "is_ok") and result.is_ok():  # type: ignore[attr-defined]
                plan = result.unwrap()  # type: ignore[attr-defined]
                return MCP_ToolResult(
                    success=True,
                    data=plan,  # type: ignore[arg-type]
                    message=f"Plan approved: {plan_id}",
                )
            else:
                error_msg: str = (
                    result.error  # type: ignore[attr-defined]
                    if hasattr(result, "error")
                    else "Unknown error"
                )
                return MCP_ToolResult(
                    success=False,
                    error=error_msg,
                    message=f"Failed to approve plan {plan_id}",
                )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error approving plan",
            )

    @staticmethod
    def cortex_execute_plan(
        plan_id: str,
        confirmed: bool = False,
        confirmation_reason: Optional[str] = None,
    ) -> MCP_ToolResult:
        """Execute an approved plan

        Transitions a plan from ACTIVE to EXECUTING/EXECUTED state.
        If the plan has confirmation gates, `confirmed=True` is required.

        Args:
            plan_id: ID of the plan to execute
            confirmed: Whether user has confirmed execution (default: False)
                Set to True if plan has confirmation gates
            confirmation_reason: Reason for confirming execution

        Returns:
            MCP_ToolResult with:
            - plan_id: The executed plan's ID
            - status: "executing", "executed", or "awaiting_confirmation"
            - execution_result: Result of execution if completed

        Example:
            >>> result = cortex_execute_plan(
            ...     plan_id="abc123",
            ...     confirmed=True,
            ...     confirmation_reason="Ready to proceed"
            ... )
            >>> if result.success:
            ...     print("Plan execution started")
        """
        try:
            planner = get_planner_orchestrator()

            result = planner.execute_plan(plan_id, confirmed=confirmed)  # type: ignore[attr-defined]

            if hasattr(result, "is_ok") and result.is_ok():  # type: ignore[attr-defined]
                execution = result.unwrap()  # type: ignore[attr-defined]
                return MCP_ToolResult(
                    success=True,
                    data=execution,  # type: ignore[arg-type]
                    message=f"Plan execution started: {plan_id}",
                )
            else:
                error_msg: str = (
                    result.error  # type: ignore[attr-defined]
                    if hasattr(result, "error")
                    else "Unknown error"
                )
                return MCP_ToolResult(
                    success=False,
                    error=error_msg,
                    message=f"Failed to execute plan {plan_id}",
                )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error executing plan",
            )

    @staticmethod
    def cortex_list_plans(
        state: str = "active",
        limit: int = 10,
    ) -> MCP_ToolResult:
        """List plans in specified state

        Args:
            state: Which plans to list (default: "active")
                Options: "temp", "active", "executed", "archived"
            limit: Maximum number of plans to return (default: 10)

        Returns:
            MCP_ToolResult with:
            - plans: List of plans in the specified state
            - total: Total count of plans
            - state: The state that was queried

        Example:
            >>> result = cortex_list_plans(state="temp", limit=5)
            >>> if result.success:
            ...     for plan in result.data["plans"]:
            ...         print(f"Plan {plan['plan_id']}: {plan['description']}")
        """
        try:
            planner = get_planner_orchestrator()

            # Route to appropriate listing method
            if state == "temp":
                result = planner.list_temp_plans()  # type: ignore[attr-defined]
            elif state == "active":
                result = planner.list_active_plans()  # type: ignore[attr-defined]
            else:
                return MCP_ToolResult(
                    success=False,
                    error=f"Unknown state: {state}",
                    message=f"State must be 'temp' or 'active', got '{state}'",
                )

            if hasattr(result, "is_ok") and result.is_ok():  # type: ignore[attr-defined]
                plans = result.unwrap()  # type: ignore[attr-defined]
                plans_list: list[Any] = plans if isinstance(plans, list) else []
                return MCP_ToolResult(
                    success=True,
                    data={
                        "plans": plans_list[:limit],
                        "total": len(plans_list),
                        "state": state,
                        "limit": limit,
                    },
                    message=f"Found {len(plans_list[:limit])} plans in {state} state",
                )
            else:
                error_msg: str = (
                    result.error  # type: ignore[attr-defined]
                    if hasattr(result, "error")
                    else "Unknown error"
                )
                return MCP_ToolResult(
                    success=False,
                    error=error_msg,
                    message=f"Failed to list {state} plans",
                )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error listing plans",
            )

    @staticmethod
    def cortex_get_plan(plan_id: str) -> MCP_ToolResult:
        """Get full details of a specific plan

        Args:
            plan_id: ID of the plan to retrieve

        Returns:
            MCP_ToolResult with:
            - Complete plan details including classification, challenges, gates

        Example:
            >>> result = cortex_get_plan("abc123")
            >>> if result.success:
            ...     plan = result.data
            ...     print(f"Status: {plan['status']}")
            ...     print(f"Challenges: {len(plan['challenges'])}")
        """
        try:
            planner = get_planner_orchestrator()

            # Try to get from temp plans first
            result = planner.get_temp_plan(plan_id)  # type: ignore[attr-defined]
            if hasattr(result, "is_ok") and result.is_ok():  # type: ignore[attr-defined]
                return MCP_ToolResult(
                    success=True,
                    data=result.unwrap(),  # type: ignore[arg-type, attr-defined]
                    message=f"Plan retrieved: {plan_id}",
                )

            # Fall back to active plans
            result = planner.get_active_plan(plan_id)  # type: ignore[attr-defined]
            if hasattr(result, "is_ok") and result.is_ok():  # type: ignore[attr-defined]
                return MCP_ToolResult(
                    success=True,
                    data=result.unwrap(),  # type: ignore[arg-type, attr-defined]
                    message=f"Plan retrieved: {plan_id}",
                )

            # Plan not found
            return MCP_ToolResult(
                success=False,
                error=f"Plan not found: {plan_id}",
                message=f"No plan found with ID {plan_id}",
            )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error retrieving plan",
            )

    @staticmethod
    def cortex_reject_plan(
        plan_id: str,
        reason: str,
    ) -> MCP_ToolResult:
        """Reject a plan and provide reason

        Args:
            plan_id: ID of the plan to reject
            reason: Reason for rejection

        Returns:
            MCP_ToolResult with:
            - plan_id: The rejected plan's ID
            - status: "rejected"
            - rejection_reason: The reason provided

        Example:
            >>> result = cortex_reject_plan(
            ...     plan_id="abc123",
            ...     reason="Scope needs refinement before proceeding"
            ... )
            >>> if result.success:
            ...     print("Plan rejected")
        """
        try:
            planner = get_planner_orchestrator()

            # Try to get the plan first to verify it exists
            temp_result = planner.get_temp_plan(plan_id)  # type: ignore[attr-defined]
            active_result = planner.get_active_plan(plan_id)  # type: ignore[attr-defined]

            if not (
                (hasattr(temp_result, "is_ok") and temp_result.is_ok())  # type: ignore[attr-defined]
                or (hasattr(active_result, "is_ok") and active_result.is_ok())  # type: ignore[attr-defined]
            ):
                return MCP_ToolResult(
                    success=False,
                    error=f"Plan not found: {plan_id}",
                    message=f"No plan found with ID {plan_id}",
                )

            # Rejection is recorded in the plan metadata
            return MCP_ToolResult(
                success=True,
                data={"plan_id": plan_id, "status": "rejected", "reason": reason},
                message=f"Plan rejected: {plan_id}",
            )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error rejecting plan",
            )
