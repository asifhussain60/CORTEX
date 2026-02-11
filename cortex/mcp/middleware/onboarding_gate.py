"""
Onboarding Gate Middleware (Phase 28.3)

Enforces onboarding-first policy for external repository operations.
Blocks operations on unonboarded repositories and can auto-trigger onboarding.

Authority: phase-28-repository-onboarding-system.yaml
Created: 2026-02-06
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from cortex_brain.onboarded_repos import ProfileNotFoundError, ProfileStore

logger = logging.getLogger(__name__)


class OnboardingGate:
    """
    Middleware to enforce onboarding-first policy for external repositories.

    Checks if external repositories are onboarded before allowing operations.
    Can optionally auto-trigger onboarding for new repositories.

    Attributes:
        profile_store: ProfileStore for checking onboarding status
        auto_onboard: Whether to auto-trigger onboarding for new repos

    Example:
        >>> gate = OnboardingGate(auto_onboard=True)
        >>> result = gate.process_request({
        ...     'operation': 'analyze',
        ...     'repo_path': '/path/to/repo'
        ... })
        >>> if result['onboarded']:
        ...     # Proceed with operation
        ...     pass
    """

    def __init__(
        self,
        profile_store: Optional[ProfileStore] = None,
        auto_onboard: bool = False,
    ):
        """
        Initialize OnboardingGate.

        Args:
            profile_store: ProfileStore instance (default: new ProfileStore)
            auto_onboard: Auto-trigger onboarding for unonboarded repos
        """
        self.profile_store = profile_store or ProfileStore()
        self.auto_onboard = auto_onboard

    def check_onboarding(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if repository in request is onboarded.

        Args:
            request: Request dictionary with repo_path

        Returns:
            Dictionary with onboarding status

        Example:
            >>> result = gate.check_onboarding({'repo_path': '/path/to/repo'})
            >>> if not result['onboarded']:
            ...     print(result['error'])
        """
        repo_path = self.extract_repo_path(request)

        if not repo_path:
            return {
                'onboarded': True,  # No repo path = not external repo operation
                'skipped': True,
            }

        # Extract repo name from path
        repo_name = Path(repo_path).name

        # Check if onboarded (case-insensitive name match OR path match)
        profiles = self.profile_store.list_all()
        for profile in profiles:
            if (profile.name.upper() == repo_name.upper() or
                profile.path == repo_path or
                Path(profile.path).resolve() == Path(repo_path).resolve()):
                return {
                    'onboarded': True,
                    'repo_name': repo_name,
                    'repo_path': repo_path,
                    'profile': profile,
                }

        # Not onboarded
        return {
            'onboarded': False,
            'repo_name': repo_name,
            'repo_path': repo_path,
            'action_required': 'onboard_repository',
            'error': f"Repository '{repo_name}' is not onboarded. Run: /onboard {repo_path}",
        }

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request with onboarding enforcement.

        If auto_onboard is True and repo is not onboarded,
        automatically triggers onboarding.

        Args:
            request: Request dictionary

        Returns:
            Processing result with onboarding status
        """
        # Check if should enforce onboarding
        if not self.should_check_onboarding(request):
            return {'onboarded': True, 'skipped': True}

        # Check onboarding status
        result = self.check_onboarding(request)

        if not result['onboarded'] and self.auto_onboard:
            # Auto-trigger onboarding
            repo_path = Path(result['repo_path'])

            if repo_path.exists():
                logger.info("Auto-onboarding repository: %s", repo_path)

                try:
                    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
                        get_repository_onboarding_orchestrator,
                    )

                    orchestrator = get_repository_onboarding_orchestrator()
                    profile = orchestrator.onboard_repository_with_profile(
                        repo_path=repo_path,
                        profile_store=self.profile_store
                    )

                    result['onboarded'] = True
                    result['auto_onboarded'] = True
                    result['profile'] = profile

                    logger.info("Auto-onboarding complete: %s", repo_path)

                except Exception as e:
                    logger.error("Auto-onboarding failed: %s", e)
                    result['error'] = f"Auto-onboarding failed: {e}"

        return result

    def extract_repo_path(self, request: Dict[str, Any]) -> Optional[str]:
        """
        Extract repository path from request.

        Supports multiple request formats:
        - {'repo_path': '/path/to/repo'}
        - {'parameters': {'repo_path': '/path/to/repo'}}
        - {'target': '/path/to/repo'}

        Args:
            request: Request dictionary

        Returns:
            Repository path if found, None otherwise
        """
        # Direct repo_path
        if 'repo_path' in request:
            return request['repo_path']

        # Nested in parameters
        if 'parameters' in request and 'repo_path' in request['parameters']:
            return request['parameters']['repo_path']

        # Target field
        if 'target' in request:
            return request['target']

        return None

    def should_check_onboarding(self, request: Dict[str, Any]) -> bool:
        """
        Determine if onboarding check should be performed.

        Skips checks for:
        - CORTEX-internal operations (health_check, list_tools)
        - Operations on CORTEX itself

        Args:
            request: Request dictionary

        Returns:
            True if onboarding check should be performed
        """
        # Skip for internal operations
        internal_operations = {'health_check', 'list_tools', 'get_capabilities'}
        if request.get('operation') in internal_operations:
            return False

        # Skip for CORTEX itself
        repo_path = self.extract_repo_path(request)
        if repo_path:
            if 'CORTEX' in repo_path or 'cortex' in repo_path.lower():
                return False

        return True


def create_onboarding_gate(
    profile_store: Optional[ProfileStore] = None,
    auto_onboard: bool = False,
) -> OnboardingGate:
    """
    Factory function to create OnboardingGate instance.

    Args:
        profile_store: ProfileStore instance
        auto_onboard: Auto-trigger onboarding

    Returns:
        OnboardingGate instance
    """
    return OnboardingGate(
        profile_store=profile_store,
        auto_onboard=auto_onboard,
    )
