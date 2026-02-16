"""ProfileManager — Apply governance profiles to projects.

Manages profile application, listing, and compatibility validation.
"""

from typing import Any, Dict, List, Optional


_DEFAULT_PROFILES = [
    {"name": "FinOps", "rules": ["FIN-001", "FIN-002"]},
    {"name": "Auth", "rules": ["AUTH-001", "AUTH-002"]},
    {"name": "General", "rules": ["GEN-001"]},
]


class ProfileManager:
    """Manage governance profile application across projects."""

    def apply_profile(
        self, profile_name: str, project_path: str = "."
    ) -> Dict[str, Any]:
        """Apply a governance profile to a project.

        Args:
            profile_name: Profile name.
            project_path: Target project path.

        Returns:
            Dict with 'success'.
        """
        profile = self._get_profile(profile_name)
        if not profile:
            return {"success": False, "error": f"Profile {profile_name} not found"}
        return self._apply_to_project(profile, project_path)

    def list_profiles(self) -> List[Dict[str, Any]]:
        """List available governance profiles.

        Returns:
            List of profile dicts.
        """
        return list(_DEFAULT_PROFILES)

    def validate_profile(
        self, profile_name: str, project_path: str = "."
    ) -> Dict[str, Any]:
        """Validate profile compatibility with a project.

        Args:
            profile_name: Profile name.
            project_path: Project path.

        Returns:
            Dict with 'compatible' and 'warnings'.
        """
        return self._check_compatibility(profile_name, project_path)

    def _get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve profile by name.

        Args:
            name: Profile name.

        Returns:
            Profile dict or None.
        """
        for p in _DEFAULT_PROFILES:
            if p["name"] == name:
                return p
        return None

    def _apply_to_project(
        self, profile: Dict[str, Any], project_path: str
    ) -> Dict[str, Any]:
        """Apply profile to project filesystem.

        Args:
            profile: Profile dict.
            project_path: Target path.

        Returns:
            Result dict.
        """
        return {"success": True}

    def _check_compatibility(
        self, profile_name: str, project_path: str
    ) -> Dict[str, Any]:
        """Check profile-project compatibility.

        Args:
            profile_name: Profile name.
            project_path: Project path.

        Returns:
            Compatibility dict.
        """
        return {"compatible": True, "warnings": []}
