"""
Repository Onboarding MCP Tool (Phase 28)

Exposes repository onboarding functionality via MCP.

Authority: phase-28-repository-onboarding-system.yaml
Created: 2026-02-06
"""

from pathlib import Path
from typing import Any, Dict

from cortex.mcp.server import Tool, ToolDefinition, ToolParameter
from cortex.orchestrators.support.repository_onboarding_orchestrator import (
    get_repository_onboarding_orchestrator,
)
from cortex_brain.onboarded_repos import ProfileStore


class RepositoryOnboardingTool(Tool):
    """
    MCP Tool for repository onboarding.

    Command: /onboard {path}

    Onboards external repositories with profile generation and loose coupling.
    """

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_onboard_repository",
            description=(
                "Onboard external repository with comprehensive profiling. "
                "Creates repository profile with tech stack analysis, "
                "company domains detection, security baseline assessment, "
                "standards extraction, and loose coupling for deletion safety. "
                "Usage: /onboard /path/to/repository"
            ),
            parameters=[
                ToolParameter(
                    name="repo_path",
                    type="string",
                    required=True,
                    description="Absolute path to repository to onboard"
                ),
                ToolParameter(
                    name="profile_store_path",
                    type="string",
                    required=False,
                    description="Optional: Path to profile storage directory"
                ),
            ]
        )

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute repository onboarding.

        Args:
            repo_path: Path to repository
            profile_store_path: Optional profile storage path

        Returns:
            Onboarding result with profile
        """
        repo_path = Path(kwargs['repo_path'])
        profile_store_path = kwargs.get('profile_store_path')

        # Validate repository exists
        if not repo_path.exists():
            return {
                'success': False,
                'error': f"Repository not found: {repo_path}"
            }

        # Create profile store
        if profile_store_path:
            profile_store = ProfileStore(storage_path=Path(profile_store_path))
        else:
            profile_store = ProfileStore()

        # Get orchestrator
        orchestrator = get_repository_onboarding_orchestrator()

        try:
            # Onboard repository
            profile = orchestrator.onboard_repository_with_profile(
                repo_path=repo_path,
                profile_store=profile_store
            )

            return {
                'success': True,
                'repo_name': profile.name,
                'repo_path': str(profile.path),
                'onboarded_at': profile.onboarded_at.isoformat(),
                'profile': {
                    'tech_stack': {
                        'primary_language': profile.tech_stack.primary_language,
                        'languages': profile.tech_stack.languages,
                        'frameworks': profile.tech_stack.frameworks,
                    },
                    'structure': {
                        'has_company_domains': profile.structure.has_company_domains,
                        'domains_detected': profile.structure.domains_detected,
                        'has_tests': profile.structure.has_tests,
                    },
                    'loose_coupling': {
                        'deletion_safe': profile.loose_coupling.deletion_safe,
                    }
                },
                'message': f"✅ Repository '{profile.name}' onboarded successfully"
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Onboarding failed: {str(e)}"
            }


def register_onboarding_tool():
    """Register repository onboarding tool with MCP."""
    return RepositoryOnboardingTool()
