"""ProfileWizard — Quick-start wizard for governance profiles.

Detects project type, suggests profiles, applies tier1 rules,
and supports customization.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# Detection keyword maps
_FINOPS_KEYWORDS = {"pandas", "numpy", "openpyxl", "xlrd", "finance-tools", "finops"}
_AUTH_KEYWORDS = {"auth", "session", "jwt", "oauth", "oidc"}
_ML_KEYWORDS = {"tensorflow", "torch", "keras", "scikit-learn", "xgboost"}
_DEVOPS_KEYWORDS = {"ci.yml", "ci.yaml", "deploy.yml", "cd.yml"}

# Available profiles catalog
_PROFILES = [
    {"name": "finops", "description": "Financial operations governance", "domain": "finops"},
    {"name": "auth", "description": "Authentication / session governance", "domain": "auth"},
    {"name": "ml", "description": "Machine learning governance", "domain": "ml"},
    {"name": "devops", "description": "DevOps / CI-CD governance", "domain": "devops"},
    {"name": "web-v1.0", "description": "Web application governance", "domain": "web"},
    {"name": "api-v1.0", "description": "API service governance", "domain": "api"},
    {"name": "general-v1.0", "description": "General-purpose governance", "domain": "general"},
]


class ProfileWizard:
    """Quick-start wizard for governance profiles.

    Args:
        workspace_root: Root path of the workspace.
    """

    def __init__(self, workspace_root: Path) -> None:
        """Initialize ProfileWizard.

        Args:
            workspace_root: Root path.
        """
        self._root = workspace_root

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect_project_type(self) -> str:
        """Detect the project type from workspace contents.

        Returns:
            Project type string: 'finops', 'auth', 'ml', 'devops', or 'general'.
        """
        req_file = self._root / "requirements.txt"
        packages: str = ""
        if req_file.exists():
            packages = req_file.read_text(encoding="utf-8").lower()

        # Check requirements keywords — ML before finops (numpy overlaps)
        if any(kw in packages for kw in _ML_KEYWORDS):
            return "ml"
        if any(kw in packages for kw in _FINOPS_KEYWORDS):
            return "finops"

        # Check folder structure
        for child in self._root.iterdir() if self._root.exists() else []:
            name = child.name.lower()
            if name in _AUTH_KEYWORDS and child.is_dir():
                return "auth"

        # Check CI/CD
        workflows_dir = self._root / ".github" / "workflows"
        if workflows_dir.exists():
            return "devops"

        return "general"

    # ------------------------------------------------------------------
    # Suggestion
    # ------------------------------------------------------------------

    def suggest_profile(self) -> Dict[str, Any]:
        """Suggest a governance profile based on detection.

        Returns:
            Dict with 'profile', 'confidence', 'explanation'.
        """
        project_type = self.detect_project_type()
        profile_name = f"{project_type}-v1.0"
        confidence = 0.85 if project_type != "general" else 0.5
        return {
            "profile": profile_name,
            "confidence": confidence,
            "explanation": f"Detected {project_type} project type from workspace analysis.",
        }

    # ------------------------------------------------------------------
    # Customization
    # ------------------------------------------------------------------

    def customize_profile(
        self,
        profile: str,
        add_rules: Optional[List[str]] = None,
        remove_rules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Customize a profile by adding/removing rules.

        Args:
            profile: Base profile name.
            add_rules: Rule IDs to add.
            remove_rules: Rule IDs to remove.

        Returns:
            Dict with final 'rules' list.
        """
        base_rules = self._get_profile_rules(profile)
        rule_set = set(base_rules)
        for r in (remove_rules or []):
            rule_set.discard(r)
        for r in (add_rules or []):
            rule_set.add(r)
        return {"rules": sorted(rule_set)}

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    def apply_profile(self, profile: str) -> Dict[str, Any]:
        """Apply a profile to tier1 directory.

        Args:
            profile: Profile identifier (e.g. 'finops').

        Returns:
            Dict with 'success'.
        """
        tier1_dir = self._root / "cortex_intelligence" / "tier1"
        tier1_dir.mkdir(parents=True, exist_ok=True)
        rules_file = tier1_dir / "domain-rules.yaml"
        rules = self._get_profile_rules(profile)
        rules_file.write_text(
            yaml.dump({"profile": profile, "rules": [{"id": r} for r in rules]}),
            encoding="utf-8",
        )
        return {"success": True}

    # ------------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------------

    def list_available_profiles(self) -> List[Dict[str, Any]]:
        """List all available governance profiles.

        Returns:
            List of profile dicts with 'name', 'description', 'domain'.
        """
        return list(_PROFILES)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_profile_rules(self, profile: str) -> List[str]:
        """Get baseline rules for a profile.

        Args:
            profile: Profile identifier.

        Returns:
            List of rule ID strings.
        """
        base = profile.split("-v")[0].upper() if "-v" in profile else profile.upper()
        return [f"{base}-001", f"{base}-002", f"{base}-003"]
