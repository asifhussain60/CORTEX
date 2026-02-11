"""
ProfileVersioner - Profile version tracking and updates.

Tracks applied profiles and detects available updates.

AC-ID: AC-DEP-006-03
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProfileVersioner:
    """
    Versioner for governance profile tracking.

    Tracks applied profiles and detects updates.
    Follows CORE-008 (TDD) and CORE-011 (type hints).
    """

    def __init__(self, repo_path: Path):
        """
        Initialize ProfileVersioner.

        Args:
            repo_path: Path to the repository root.
        """
        self.repo_path = Path(repo_path)
        self.tracking_file = self.repo_path / ".cortex" / "profile-tracking.json"
        self._ensure_tracking_file()

    def _ensure_tracking_file(self) -> None:
        """Ensure tracking file exists."""
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.tracking_file.exists():
            self.tracking_file.write_text("{}")

    def _load_tracking(self) -> Dict[str, Any]:
        """Load tracking data."""
        try:
            return json.loads(self.tracking_file.read_text())
        except Exception:
            return {}

    def _save_tracking(self, data: Dict[str, Any]) -> None:
        """Save tracking data."""
        self.tracking_file.write_text(json.dumps(data, indent=2))

    def track_profile(self, project: str, profile: str) -> None:
        """
        Track which profile is applied to a project.

        Args:
            project: Project name.
            profile: Profile name and version.
        """
        tracking = self._load_tracking()

        if "projects" not in tracking:
            tracking["projects"] = {}

        tracking["projects"][project] = {
            "profile": profile,
            "applied_at": datetime.now().isoformat(),
            "base_profile": profile.rsplit("-", 1)[0] if "-v" in profile else profile,
            "version": profile.split("-v")[-1] if "-v" in profile else "1.0"
        }

        self._save_tracking(tracking)

    def get_applied_profile(self, project: str) -> Dict[str, Any]:
        """
        Get the profile applied to a project.

        Args:
            project: Project name.

        Returns:
            Profile information dictionary.
        """
        tracking = self._load_tracking()
        return tracking.get("projects", {}).get(project, {})

    def _get_available_versions(self, profile_base: str) -> List[str]:
        """Get available versions for a profile base."""
        # In real implementation, would query a registry
        # Mock available versions for testing
        return ["1.0", "1.1", "1.2"]

    def check_for_updates(self, project: str) -> Dict[str, Any]:
        """
        Check if profile updates are available.

        Args:
            project: Project name.

        Returns:
            Update availability dictionary.
        """
        applied = self.get_applied_profile(project)

        if not applied:
            return {"update_available": False, "error": "No profile applied"}

        base_profile = applied.get("base_profile", "")
        current_version = applied.get("version", "1.0")

        available = self._get_available_versions(base_profile)
        latest = max(available, key=lambda v: [int(x) for x in v.split(".")])

        current_parts = [int(x) for x in current_version.split(".")]
        latest_parts = [int(x) for x in latest.split(".")]

        update_available = latest_parts > current_parts

        return {
            "update_available": update_available,
            "current_version": current_version,
            "latest_version": latest,
            "available_versions": available
        }

    def compute_version_diff(
        self,
        profile_base: str,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        Compute diff between profile versions.

        Args:
            profile_base: Base profile name.
            from_version: Current version.
            to_version: Target version.

        Returns:
            Diff dictionary.
        """
        # In real implementation, would compare actual profile files
        # Mock diff for testing
        return {
            "profile": profile_base,
            "from_version": from_version,
            "to_version": to_version,
            "added_rules": [f"{profile_base.upper()[:3]}-NEW-001"],
            "removed_rules": [],
            "modified_rules": []
        }

    def check_compatibility(
        self,
        profile_base: str,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        Check compatibility between versions.

        Args:
            profile_base: Base profile name.
            from_version: Current version.
            to_version: Target version.

        Returns:
            Compatibility dictionary.
        """
        from_parts = [int(x) for x in from_version.split(".")]
        to_parts = [int(x) for x in to_version.split(".")]

        # Major version change indicates potential breaking changes
        breaking = to_parts[0] > from_parts[0]

        return {
            "compatible": not breaking,
            "breaking_changes": ["Major version upgrade" if breaking else None],
            "migration_required": breaking,
            "safe_upgrade": not breaking
        }

    def register_version(
        self,
        profile: str,
        version: str,
        changelog: str
    ) -> Dict[str, Any]:
        """
        Register a new profile version.

        Args:
            profile: Profile base name.
            version: Version string.
            changelog: Changelog entry.

        Returns:
            Registration result dictionary.
        """
        tracking = self._load_tracking()

        if "registry" not in tracking:
            tracking["registry"] = {}

        if profile not in tracking["registry"]:
            tracking["registry"][profile] = {"versions": []}

        tracking["registry"][profile]["versions"].append({
            "version": version,
            "changelog": changelog,
            "registered_at": datetime.now().isoformat()
        })

        self._save_tracking(tracking)

        return {
            "success": True,
            "profile": profile,
            "version": version
        }

    def get_version_history(self, profile: str) -> List[Dict[str, Any]]:
        """
        Get version history for a profile.

        Args:
            profile: Profile base name.

        Returns:
            List of version history entries.
        """
        tracking = self._load_tracking()
        registry = tracking.get("registry", {})
        profile_data = registry.get(profile, {})

        return profile_data.get("versions", [])

    def _is_newer_version(self, version_a: str, version_b: str) -> bool:
        """
        Check if version_a is newer than version_b.

        Args:
            version_a: First version string.
            version_b: Second version string.

        Returns:
            True if version_a > version_b.
        """
        parts_a = [int(x) for x in version_a.split(".")]
        parts_b = [int(x) for x in version_b.split(".")]

        return parts_a > parts_b
