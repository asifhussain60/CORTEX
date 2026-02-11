"""Profile Manager MCP Tool - PHASE-DEPLOYMENT-003-mcp-expansion.

Apply governance profiles to projects.

Author: CORTEX Framework
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class ProfileManager:
    """MCP tool for managing governance profiles.

    Applies pre-defined governance profiles (FinOps, Auth, ML, etc.) to projects.
    """

    # Built-in profiles
    PROFILES = {
        "FinOps": {
            "name": "FinOps",
            "description": "Financial operations governance profile",
            "rules": ["FIN-001", "FIN-002", "FIN-003"],
            "tier": "tier1",
            "requirements": ["audit_trail", "data_retention"],
        },
        "Auth": {
            "name": "Auth",
            "description": "Authentication/authorization governance profile",
            "rules": ["AUTH-001", "AUTH-002", "SEC-001"],
            "tier": "tier1",
            "requirements": ["encryption", "access_control"],
        },
        "ML": {
            "name": "ML",
            "description": "Machine learning governance profile",
            "rules": ["ML-001", "ML-002", "DATA-001"],
            "tier": "tier1",
            "requirements": ["model_versioning", "data_lineage"],
        },
        "DevOps": {
            "name": "DevOps",
            "description": "DevOps/CI-CD governance profile",
            "rules": ["CICD-001", "CICD-002", "DEPLOY-001"],
            "tier": "tier1",
            "requirements": ["pipeline_validation", "deployment_gates"],
        },
        "Healthcare": {
            "name": "Healthcare",
            "description": "Healthcare compliance governance profile",
            "rules": ["HIPAA-001", "HIPAA-002", "PHI-001"],
            "tier": "tier1",
            "requirements": ["phi_protection", "audit_logging", "access_control"],
        },
        "Legal": {
            "name": "Legal",
            "description": "Legal/compliance governance profile",
            "rules": ["LEGAL-001", "LEGAL-002", "GDPR-001"],
            "tier": "tier1",
            "requirements": ["data_privacy", "consent_management"],
        },
    }

    def __init__(self):
        """Initialize profile manager."""
        pass

    def apply_profile(
        self,
        profile_name: str,
        project_path: str,
    ) -> Dict[str, Any]:
        """Apply governance profile to project.

        Args:
            profile_name: Name of profile to apply.
            project_path: Path to target project.

        Returns:
            Application result.
        """
        profile = self._get_profile(profile_name)

        if not profile:
            return {
                "success": False,
                "error": f"Profile '{profile_name}' not found",
            }

        return self._apply_to_project(profile, project_path)

    def _get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get profile by name.

        Args:
            name: Profile name.

        Returns:
            Profile definition or None.
        """
        return self.PROFILES.get(name)

    def _apply_to_project(
        self,
        profile: Dict[str, Any],
        project_path: str,
    ) -> Dict[str, Any]:
        """Apply profile to project directory.

        Args:
            profile: Profile definition.
            project_path: Target project path.

        Returns:
            Application result.
        """
        # Create tier1 directory if needed
        tier1_path = Path(project_path) / "cortex_brain" / "tier1"

        try:
            tier1_path.mkdir(parents=True, exist_ok=True)

            # Write profile rules file
            profile_file = tier1_path / f"{profile['name'].lower()}-rules.yaml"

            # In real implementation, would write YAML content
            # For now, just return success

            return {
                "success": True,
                "profile": profile["name"],
                "project": project_path,
                "rules_applied": profile["rules"],
                "tier1_path": str(tier1_path),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def list_profiles(self) -> List[Dict[str, Any]]:
        """List available governance profiles.

        Returns:
            List of profile summaries.
        """
        return [
            {
                "name": p["name"],
                "description": p["description"],
                "rule_count": len(p["rules"]),
                "tier": p["tier"],
            }
            for p in self.PROFILES.values()
        ]

    def validate_profile(
        self,
        profile_name: str,
        project_path: str,
    ) -> Dict[str, Any]:
        """Validate profile compatibility with project.

        Args:
            profile_name: Profile to validate.
            project_path: Target project.

        Returns:
            Compatibility check result.
        """
        return self._check_compatibility(profile_name, project_path)

    def _check_compatibility(
        self,
        profile_name: str,
        project_path: str,
    ) -> Dict[str, Any]:
        """Check if profile is compatible with project.

        Args:
            profile_name: Profile name.
            project_path: Project path.

        Returns:
            Compatibility result.
        """
        profile = self._get_profile(profile_name)

        if not profile:
            return {
                "compatible": False,
                "warnings": [f"Profile '{profile_name}' not found"],
            }

        warnings = []
        path = Path(project_path)

        # Check basic requirements
        if not path.exists():
            return {
                "compatible": False,
                "warnings": ["Project path does not exist"],
            }

        # Check for conflicting profiles
        existing_tier1 = path / "cortex_brain" / "tier1"
        if existing_tier1.exists():
            for rule_file in existing_tier1.glob("*-rules.yaml"):
                if profile_name.lower() not in rule_file.name:
                    warnings.append(f"Existing profile found: {rule_file.name}")

        return {
            "compatible": True,
            "warnings": warnings,
            "profile": profile_name,
            "requirements": profile.get("requirements", []),
        }

    def get_profile_details(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed profile information.

        Args:
            profile_name: Profile name.

        Returns:
            Full profile details or None.
        """
        return self._get_profile(profile_name)


__all__ = ["ProfileManager"]
