"""
CLI Router for PlannerOrchestrator

Maps Copilot-style CLI commands to PlannerOrchestrator MCP tools.
Provides user-friendly command routing and response formatting.

CLI Commands:
- `/plan create <description> [options]` - Create new planning session
- `/plan approve <plan_id> [notes]` - Approve a plan for execution
- `/plan execute <plan_id> [--confirm] [reason]` - Execute an approved plan
- `/plan list [state] [--limit N]` - List plans in various states
- `/plan show <plan_id>` - Show full details of a plan
- `/plan reject <plan_id> <reason>` - Reject a plan

AC-PLANNER-CLI-001: CLI command routing and formatting
"""

from typing import Optional
import re

from cortex.orchestrators.mcp_tools_planner import (
    PlannerOrchestratorMCPTools,
    MCP_ToolResult,
)


class PlannerCLIRouter:
    """Routes Copilot CLI commands to PlannerOrchestrator MCP tools

    Provides command parsing, validation, and response formatting for
    Copilot-style CLI commands like `/plan create <description>`.
    """

    # Command patterns for parsing
    PLAN_CREATE_PATTERN = r"/plan\s+create\s+(.+?)(?:\s+--scope\s+(\w+))?(?:\s+--impact\s+(low|medium|high))?(?:\s+--confidence\s+([\d.]+))?"
    PLAN_APPROVE_PATTERN = r"/plan\s+approve\s+(\w+)(?:\s+--notes\s+(.+))?"
    PLAN_EXECUTE_PATTERN = r"/plan\s+execute\s+(\w+)(?:\s+--confirm)?(?:\s+--reason\s+(.+))?"
    PLAN_LIST_PATTERN = r"/plan\s+list(?:\s+(temp|active))?(?:\s+--limit\s+(\d+))?"
    PLAN_SHOW_PATTERN = r"/plan\s+show\s+(\w+)"
    PLAN_REJECT_PATTERN = r"/plan\s+reject\s+(\w+)\s+(.+)"

    @staticmethod
    def route_command(command: str) -> MCP_ToolResult:
        """Route a CLI command to the appropriate MCP tool

        Args:
            command: The CLI command string
                Examples:
                - `/plan create Fix authentication bug --impact high --confidence 0.8`
                - `/plan approve abc123`
                - `/plan execute abc123 --confirm`
                - `/plan list temp --limit 5`
                - `/plan show abc123`
                - `/plan reject abc123 Needs more review`

        Returns:
            MCP_ToolResult with command execution result
        """
        command = command.strip()

        # Route to appropriate command handler
        if command.startswith("/plan create"):
            return PlannerCLIRouter._handle_create(command)
        elif command.startswith("/plan approve"):
            return PlannerCLIRouter._handle_approve(command)
        elif command.startswith("/plan execute"):
            return PlannerCLIRouter._handle_execute(command)
        elif command.startswith("/plan list"):
            return PlannerCLIRouter._handle_list(command)
        elif command.startswith("/plan show"):
            return PlannerCLIRouter._handle_show(command)
        elif command.startswith("/plan reject"):
            return PlannerCLIRouter._handle_reject(command)
        else:
            return MCP_ToolResult(
                success=False,
                error="Unknown command",
                message="Available commands: /plan create, /plan approve, /plan execute, /plan list, /plan show, /plan reject",
            )

    @staticmethod
    def _handle_create(command: str) -> MCP_ToolResult:
        """Handle `/plan create` command

        Examples:
            /plan create Fix authentication bug --impact high --confidence 0.8
            /plan create Implement user dashboard --scope module
        """
        try:
            # Remove the command prefix
            rest = command[len("/plan create") :].strip()

            # Parse options
            scope = "file"
            impact = "medium"
            confidence: Optional[float] = None

            # Extract scope if present
            scope_match = re.search(r"--scope\s+(\w+)", rest)
            if scope_match:
                scope = scope_match.group(1)
                rest = rest[: scope_match.start()] + rest[scope_match.end() :]

            # Extract impact if present
            impact_match = re.search(r"--impact\s+(low|medium|high)", rest)
            if impact_match:
                impact = impact_match.group(1)
                rest = rest[: impact_match.start()] + rest[impact_match.end() :]

            # Extract confidence if present
            confidence_match = re.search(r"--confidence\s+([\d.]+)", rest)
            if confidence_match:
                confidence = float(confidence_match.group(1))
                rest = rest[: confidence_match.start()] + rest[confidence_match.end() :]

            # Remaining text is the description
            description = rest.strip()

            if not description:
                return MCP_ToolResult(
                    success=False,
                    error="Missing description",
                    message="Usage: /plan create <description> [--scope SCOPE] [--impact IMPACT] [--confidence CONF]",
                )

            # Call MCP tool
            return PlannerOrchestratorMCPTools.cortex_create_plan(
                description=description,
                scope=scope,
                impact=impact,
                confidence=confidence,
            )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error parsing create command",
            )

    @staticmethod
    def _handle_approve(command: str) -> MCP_ToolResult:
        """Handle `/plan approve` command

        Examples:
            /plan approve abc123
            /plan approve abc123 --notes "Reviewed and approved"
        """
        try:
            # Remove the command prefix
            rest = command[len("/plan approve") :].strip()

            # Parse plan_id and optional notes
            parts = rest.split(None, 1)
            if not parts:
                return MCP_ToolResult(
                    success=False,
                    error="Missing plan_id",
                    message="Usage: /plan approve <plan_id> [--notes NOTES]",
                )

            plan_id = parts[0]
            notes: Optional[str] = None

            # Extract notes if present
            notes_match = re.search(r'--notes\s+["\']?(.+?)["\']?$', rest)
            if notes_match:
                notes = notes_match.group(1)

            # Call MCP tool
            return PlannerOrchestratorMCPTools.cortex_approve_plan(
                plan_id=plan_id,
                notes=notes,
            )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error parsing approve command",
            )

    @staticmethod
    def _handle_execute(command: str) -> MCP_ToolResult:
        """Handle `/plan execute` command

        Examples:
            /plan execute abc123
            /plan execute abc123 --confirm --reason "Ready to proceed"
        """
        try:
            # Remove the command prefix
            rest = command[len("/plan execute") :].strip()

            # Parse plan_id
            parts = rest.split(None, 1)
            if not parts:
                return MCP_ToolResult(
                    success=False,
                    error="Missing plan_id",
                    message="Usage: /plan execute <plan_id> [--confirm] [--reason REASON]",
                )

            plan_id = parts[0]
            confirmed = "--confirm" in rest
            confirmation_reason: Optional[str] = None

            # Extract reason if present
            reason_match = re.search(r'--reason\s+["\']?(.+?)["\']?$', rest)
            if reason_match:
                confirmation_reason = reason_match.group(1)

            # Call MCP tool
            return PlannerOrchestratorMCPTools.cortex_execute_plan(
                plan_id=plan_id,
                confirmed=confirmed,
                confirmation_reason=confirmation_reason,
            )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error parsing execute command",
            )

    @staticmethod
    def _handle_list(command: str) -> MCP_ToolResult:
        """Handle `/plan list` command

        Examples:
            /plan list
            /plan list temp
            /plan list active --limit 20
        """
        try:
            # Remove the command prefix
            rest = command[len("/plan list") :].strip()

            state = "active"
            limit = 10

            # Parse state if present
            if rest:
                parts = rest.split()
                if parts[0] in ("temp", "active"):
                    state = parts[0]

            # Extract limit if present
            limit_match = re.search(r"--limit\s+(\d+)", rest)
            if limit_match:
                limit = int(limit_match.group(1))

            # Call MCP tool
            return PlannerOrchestratorMCPTools.cortex_list_plans(
                state=state,
                limit=limit,
            )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error parsing list command",
            )

    @staticmethod
    def _handle_show(command: str) -> MCP_ToolResult:
        """Handle `/plan show` command

        Examples:
            /plan show abc123
        """
        try:
            # Remove the command prefix
            rest = command[len("/plan show") :].strip()

            if not rest:
                return MCP_ToolResult(
                    success=False,
                    error="Missing plan_id",
                    message="Usage: /plan show <plan_id>",
                )

            plan_id = rest.split()[0]

            # Call MCP tool
            return PlannerOrchestratorMCPTools.cortex_get_plan(plan_id=plan_id)

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error parsing show command",
            )

    @staticmethod
    def _handle_reject(command: str) -> MCP_ToolResult:
        """Handle `/plan reject` command

        Examples:
            /plan reject abc123 Needs more review
            /plan reject abc123 "Scope needs refinement"
        """
        try:
            # Remove the command prefix
            rest = command[len("/plan reject") :].strip()

            # Parse plan_id and reason
            parts = rest.split(None, 1)
            if len(parts) < 2:
                return MCP_ToolResult(
                    success=False,
                    error="Missing plan_id or reason",
                    message="Usage: /plan reject <plan_id> <reason>",
                )

            plan_id = parts[0]
            reason = parts[1]

            # Call MCP tool
            return PlannerOrchestratorMCPTools.cortex_reject_plan(
                plan_id=plan_id,
                reason=reason,
            )

        except Exception as e:
            return MCP_ToolResult(
                success=False,
                error=str(e),
                message="Error parsing reject command",
            )

    @staticmethod
    def format_response(result: MCP_ToolResult) -> str:
        """Format MCP_ToolResult for display in Copilot

        Args:
            result: The MCP_ToolResult to format

        Returns:
            Formatted string for display
        """
        if result.success:
            lines = [f"✅ {result.message}"]
            if result.data:
                # Format data based on type
                if isinstance(result.data, dict):
                    if "plans" in result.data:
                        # List response
                        plans = result.data.get("plans", [])
                        lines.append(f"\n📋 Total: {result.data.get('total', 0)} plans")
                        for i, plan in enumerate(plans, 1):
                            plan_id = plan.get("plan_id", "unknown")
                            description = plan.get("description", "No description")
                            status = plan.get("status", "unknown")
                            lines.append(
                                f"  {i}. [{status.upper()}] {plan_id}: {description[:50]}"
                            )
                    elif "plan_id" in result.data:
                        # Single plan response
                        lines.append(f"\n📋 Plan Details:")
                        lines.append(f"  • Plan ID: {result.data.get('plan_id', 'unknown')}")
                        for key, value in result.data.items():
                            if key != "plan_id":
                                formatted_key = key.replace("_", " ").title()
                                lines.append(f"  • {formatted_key}: {value}")
                    else:
                        # Generic dict response
                        lines.append(f"\n📊 Response:")
                        import json

                        lines.append(json.dumps(result.data, indent=2))
            return "\n".join(lines)
        else:
            lines = [f"❌ {result.message}"]
            if result.error:
                lines.append(f"Error: {result.error}")
            return "\n".join(lines)
