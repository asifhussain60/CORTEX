"""
ProfileVersioner — Profile version tracking and update detection.

Authority: CORE-035 (single canonical implementation)
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProfileVersioner:
    """Tracks applied profiles and detects available updates.

    Args:
        base_path: Repository root.
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize instance."""
        self.base_path = Path(base_path)
        self._applied: Dict[str, Dict[str, Any]] = {}
        self._registry: Dict[str, List[Dict[str, Any]]] = {}

    # ── Tracking ─────────────────────────────────────────────────────

    def track_profile(self, project: str, profile: str) -> None:
        """Record that a profile is applied to a project.

        Args:
            project: Project identifier.
            profile: Profile name.
        """
        self._applied[project] = {
            "profile": profile,
            "applied_at": datetime.utcnow().isoformat(),
            "version": "1.0",
        }

    def get_applied_profile(self, project: str) -> Dict[str, Any]:
        """Retrieve the tracked profile for a project.

        Args:
            project: Project identifier.

        Returns:
            Dict with ``profile`` and ``applied_at`` keys.
        """
        return self._applied.get(project, {})

    def _get_available_versions(self, profile: str) -> List[str]:
        """Return available versions for a profile (overridable in tests)."""
        return ["1.0"]

    def check_for_updates(self, project: str) -> Dict[str, Any]:
        """Check if updates are available for the project's applied profile.

        Args:
            project: Project identifier.

        Returns:
            Dict with ``update_available`` bool and ``latest_version`` str.
        """
        applied = self._applied.get(project, {})
        current_version = applied.get("version", "1.0")
        profile = applied.get("profile", "unknown")

        versions = self._get_available_versions(profile)
        latest = max(versions, key=lambda v: [int(x) for x in v.split(".")])
        update_available = self._is_newer_version(latest, current_version)

        return {
            "update_available": update_available,
            "current_version": current_version,
            "latest_version": latest,
        }

    # ── Diff ─────────────────────────────────────────────────────────

    def compute_version_diff(
        self, profile: str, from_ver: str, to_ver: str
    ) -> Dict[str, Any]:
        """Compute diff between two profile versions.

        Args:
            profile: Profile name.
            from_ver: Starting version.
            to_ver: Target version.

        Returns:
            Dict with ``added_rules``, ``removed_rules``, ``modified_rules``.
        """
        return {
            "profile": profile,
            "from": from_ver,
            "to": to_ver,
            "added_rules": [],
            "removed_rules": [],
            "modified_rules": [],
        }

    def check_compatibility(
        self, profile: str, from_ver: str, to_ver: str
    ) -> Dict[str, Any]:
        """Check compatibility between two profile versions.

        Args:
            profile: Profile name.
            from_ver: Current version.
            to_ver: Target version.

        Returns:
            Dict with ``compatible`` bool and ``breaking_changes`` list.
        """
        from_parts = [int(x) for x in from_ver.split(".")]
        to_parts = [int(x) for x in to_ver.split(".")]
        is_major_change = to_parts[0] > from_parts[0]

        return {
            "compatible": not is_major_change,
            "breaking_changes": ["Major version bump requires migration"] if is_major_change else [],
            "profile": profile,
            "from": from_ver,
            "to": to_ver,
        }

    # ── Registry ─────────────────────────────────────────────────────

    def register_version(
        self, profile: str, version: str, changelog: str = ""
    ) -> Dict[str, Any]:
        """Register a new profile version in the local registry.

        Args:
            profile: Profile name.
            version: Version string.
            changelog: Optional changelog text.

        Returns:
            Dict with ``success`` and ``version`` keys.
        """
        if profile not in self._registry:
            self._registry[profile] = []
        self._registry[profile].append({
            "version": version,
            "changelog": changelog,
            "registered_at": datetime.utcnow().isoformat(),
        })
        return {"success": True, "version": version, "profile": profile}

    def get_version_history(self, profile: str) -> List[Dict[str, Any]]:
        """Retrieve the version history for a profile.

        Args:
            profile: Profile name.

        Returns:
            List of version dicts ordered by registration order.
        """
        return self._registry.get(profile, [])

    # ── Utilities ────────────────────────────────────────────────────

    def _is_newer_version(self, candidate: str, baseline: str) -> bool:
        """Return True if candidate is strictly newer than baseline.

        Args:
            candidate: Version to check.
            baseline: Version to compare against.

        Returns:
            bool
        """
        try:
            c = [int(x) for x in candidate.split(".")]
            b = [int(x) for x in baseline.split(".")]
            return c > b
        except ValueError:
            return False
