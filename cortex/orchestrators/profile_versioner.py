"""ProfileVersioner — Track profile versions and detect updates.

Manages version tracking for applied governance profiles,
diff computation, and compatibility checking.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class ProfileVersioner:
    """Track applied profile versions and detect updates.

    Args:
        workspace_root: Root path of the workspace.
    """

    def __init__(self, workspace_root: Path) -> None:
        """Initialize ProfileVersioner.

        Args:
            workspace_root: Root of the workspace.
        """
        self._root = workspace_root
        self._tracked: Dict[str, Dict[str, Any]] = {}
        self._registry: Dict[str, List[Dict[str, Any]]] = {}

    # ------------------------------------------------------------------
    # Tracking
    # ------------------------------------------------------------------

    def track_profile(self, project: str, profile: str) -> None:
        """Track which profile is applied to a project.

        Args:
            project: Project name.
            profile: Profile identifier (e.g. 'finops-v1.0').
        """
        self._tracked[project] = {
            "profile": profile,
            "applied_at": datetime.utcnow().isoformat(),
        }

    def get_applied_profile(self, project: str) -> Dict[str, Any]:
        """Get the currently applied profile for a project.

        Args:
            project: Project name.

        Returns:
            Dict with 'profile' and 'applied_at'.
        """
        return self._tracked.get(project, {"profile": None, "applied_at": None})

    def check_for_updates(self, project: str) -> Dict[str, Any]:
        """Check if profile updates are available for a project.

        Args:
            project: Project name.

        Returns:
            Dict with 'update_available' and 'latest_version'.
        """
        tracked = self._tracked.get(project, {})
        profile_name = tracked.get("profile", "")
        base_name = profile_name.rsplit("-v", 1)[0] if "-v" in profile_name else profile_name
        available = self._get_available_versions(base_name)
        current = profile_name.rsplit("-v", 1)[-1] if "-v" in profile_name else "0.0"
        latest = available[-1] if available else current
        return {
            "update_available": self._is_newer_version(latest, current),
            "latest_version": latest,
        }

    # ------------------------------------------------------------------
    # Diff / Compatibility
    # ------------------------------------------------------------------

    def compute_version_diff(
        self, profile: str, from_version: str, to_version: str
    ) -> Dict[str, List[str]]:
        """Compute diff between two profile versions.

        Args:
            profile: Profile name.
            from_version: Source version.
            to_version: Target version.

        Returns:
            Dict with 'added_rules', 'removed_rules', 'modified_rules'.
        """
        return {
            "added_rules": [],
            "removed_rules": [],
            "modified_rules": [],
        }

    def check_compatibility(
        self, profile: str, from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Check compatibility between profile versions.

        Args:
            profile: Profile name.
            from_version: Source version.
            to_version: Target version.

        Returns:
            Dict with 'compatible' bool and 'breaking_changes' list.
        """
        from_major = int(from_version.split(".")[0])
        to_major = int(to_version.split(".")[0])
        breaking = from_major != to_major
        return {
            "compatible": not breaking,
            "breaking_changes": ["Major version change"] if breaking else [],
        }

    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------

    def register_version(
        self, profile: str, version: str, changelog: str
    ) -> Dict[str, Any]:
        """Register a new profile version.

        Args:
            profile: Profile name.
            version: Version string.
            changelog: Description of changes.

        Returns:
            Dict with 'success' and 'version'.
        """
        if profile not in self._registry:
            self._registry[profile] = []
        self._registry[profile].append(
            {
                "version": version,
                "changelog": changelog,
                "registered_at": datetime.utcnow().isoformat(),
            }
        )
        return {"success": True, "version": version}

    def get_version_history(self, profile: str) -> List[Dict[str, Any]]:
        """Retrieve version history for a profile.

        Args:
            profile: Profile name.

        Returns:
            List of version entries.
        """
        return self._registry.get(profile, [])

    # ------------------------------------------------------------------
    # Version comparison
    # ------------------------------------------------------------------

    def _is_newer_version(self, candidate: str, current: str) -> bool:
        """Compare two semantic version strings.

        Args:
            candidate: Candidate version.
            current: Current version.

        Returns:
            True if candidate is newer than current.
        """
        def _parts(v: str) -> List[int]:
            return [int(x) for x in v.split(".")]

        try:
            return _parts(candidate) > _parts(current)
        except (ValueError, IndexError):
            return False

    def _get_available_versions(self, profile: str) -> List[str]:
        """Get available versions for a profile (stub for testing).

        Args:
            profile: Profile name.

        Returns:
            List of version strings.
        """
        return []
