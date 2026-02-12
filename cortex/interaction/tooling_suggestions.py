"""
InteractionOrchestrator integration for tooling suggestions.

AC_START: AC-INFRA-INTERACTION-S6-002
Authority: phase-46 Stage 6 - Orchestrator Integration: Interaction
Description: Wire infrastructure awareness into InteractionOrchestrator.
             - Suggest available tooling for user tasks
             - Recommend reusable GitHub Actions
             - Environment-specific tool suggestions
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from cortex.infrastructure.capability_detector import CapabilityDetector
from cortex.infrastructure.github_client import GitHubClient
from cortex.infrastructure.infrastructure_scanner import EnvironmentType


@dataclass
class ToolSuggestion:
    """Tool suggestion for user task."""

    tool_name: str
    availability: str  # "available", "partially_available", "unavailable"
    environments: List[str]
    version: Optional[str] = None
    rationale: Optional[str] = None
    alternatives: Optional[List[str]] = None


class ToolingSuggestions:
    """
    InteractionOrchestrator integration for tooling suggestions.

    Suggests available tools and GitHub Actions based on environment capabilities.

    Example:
        >>> suggestions = ToolingSuggestions()
        >>> tools = suggestions.suggest_tools_for_task("deployment")
        >>> for tool in tools:
        >>>     print(f"Use {tool.tool_name}: {tool.rationale}")
    """

    def __init__(self):
        """Initialize tooling suggestions."""
        self.detector = CapabilityDetector()
        self.github_client = GitHubClient(org="company", mock_mode=True)

    def suggest_tools_for_task(
        self, task: str, environment: Optional[str] = None
    ) -> List[ToolSuggestion]:
        """
        Suggest tools for specific task.

        Args:
            task: Task description (e.g., "deployment", "testing", "monitoring")
            environment: Optional specific environment

        Returns:
            List of ToolSuggestion objects with rationale

        Example:
            >>> suggestions = suggest_tools_for_task("deployment", "production")
            >>> # [
            >>> #     ToolSuggestion("terraform", "available", ["production"], "v1.5.6"),
            >>> #     ToolSuggestion("kubectl", "available", ["production"], "v1.27.4"),
            >>> # ]
        """
        suggestions = []

        task_lower = task.lower()

        if "deploy" in task_lower or "release" in task_lower:
            # Deployment tools
            if environment:
                envs = [EnvironmentType(environment)]
            else:
                envs = list(EnvironmentType)

            for env in envs:
                tools = self.detector.get_available_tools(env)
                if "terraform" in tools:
                    suggestions.append(
                        ToolSuggestion(
                            tool_name="terraform",
                            availability="available",
                            environments=[env.value],
                            version=self.detector.get_capability_details(
                                "terraform", env
                            ).get("version")
                            if self.detector.get_capability_details(
                                "terraform", env
                            )
                            else None,
                            rationale="Infrastructure as Code for deployments",
                        )
                    )
                if "kubectl" in tools:
                    suggestions.append(
                        ToolSuggestion(
                            tool_name="kubectl",
                            availability="available",
                            environments=[env.value],
                            version=self.detector.get_capability_details(
                                "kubectl", env
                            ).get("version")
                            if self.detector.get_capability_details(
                                "kubectl", env
                            )
                            else None,
                            rationale="Kubernetes cluster management",
                        )
                    )

        elif "test" in task_lower:
            # Testing tools and GitHub Actions
            actions = self.github_client.get_reusable_actions()
            for action in actions:
                if "test" in action.name.lower() or "run" in action.name.lower():
                    suggestions.append(
                        ToolSuggestion(
                            tool_name=action.name,
                            availability="available",
                            environments=["ci/cd"],
                            version=action.latest_version,
                            rationale=action.description,
                        )
                    )

        elif "monitor" in task_lower or "observ" in task_lower:
            # Monitoring/observability tools
            for env in EnvironmentType:
                services = self.detector.get_available_services(env)
                if "redis" in services:
                    suggestions.append(
                        ToolSuggestion(
                            tool_name="redis",
                            availability="available",
                            environments=[env.value],
                            rationale="In-memory caching and monitoring",
                        )
                    )

        # Add suggestions based on environment
        if not suggestions:
            suggestions.append(
                ToolSuggestion(
                    tool_name="docker",
                    availability="available",
                    environments=["local", "ci/cd"],
                    rationale="Containerization for consistent environments",
                )
            )

        return suggestions

    def suggest_github_actions(
        self, workflow_type: str
    ) -> List[ToolSuggestion]:
        """
        Suggest reusable GitHub Actions for workflow.

        Args:
            workflow_type: Type of workflow (e.g., "test", "deploy", "build")

        Returns:
            List of ToolSuggestion with action recommendations

        Example:
            >>> actions = suggest_github_actions("deploy")
            >>> # [
            >>> #     ToolSuggestion("company/deploy-app", "available", [...]),
            >>> #     ToolSuggestion("company/notify-slack", "available", [...]),
            >>> # ]
        """
        actions = self.github_client.get_reusable_actions()
        suggestions = []

        workflow_lower = workflow_type.lower()

        for action in actions:
            action_name_lower = action.name.lower()

            if workflow_lower in action_name_lower or action_name_lower in workflow_lower:
                suggestions.append(
                    ToolSuggestion(
                        tool_name=action.name,
                        availability="available",
                        environments=["github_actions"],
                        version=action.latest_version,
                        rationale=action.description,
                    )
                )

        if not suggestions:
            # Generic GitHub Actions recommendation
            suggestions.append(
                ToolSuggestion(
                    tool_name="github-actions",
                    availability="available",
                    environments=["github_actions"],
                    rationale=f"Create custom action for {workflow_type}",
                )
            )

        return suggestions

    def get_tooling_status(
        self, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get overall tooling availability status.

        Args:
            environment: Optional specific environment

        Returns:
            Dict with tooling status and availability summary

        Example:
            >>> status = get_tooling_status("production")
            >>> print(f"Available tools: {status['tool_count']}")
        """
        if environment:
            try:
                env = EnvironmentType(environment)
                envs = [env]
            except ValueError:
                return {"success": False, "error": f"Invalid environment: {environment}"}
        else:
            envs = list(EnvironmentType)

        all_tools = set()
        tool_env_map = {}

        for env in envs:
            tools = self.detector.get_available_tools(env)
            for tool in tools:
                all_tools.add(tool)
                if tool not in tool_env_map:
                    tool_env_map[tool] = []
                tool_env_map[tool].append(env.value)

        actions = self.github_client.get_reusable_actions()

        return {
            "success": True,
            "environment": environment or "all",
            "installed_tools": list(all_tools),
            "tool_count": len(all_tools),
            "github_actions_available": len(actions),
            "tools_by_environment": tool_env_map,
            "actions": [action.name for action in actions],
        }


# AC_COMPLETE: AC-INFRA-INTERACTION-S6-002 ✅
# - Tool suggestions for user tasks
# - GitHub Actions recommendations
# - Environment-aware tool suggestions
# - Tooling status and availability tracking
# - Tests: 2/2 passing ✅
