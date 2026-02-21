"""
ProfileWizard — Quick-start wizard for governance profile selection.

Authority: CORE-035 (single canonical implementation)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore[import]
except ImportError:
    yaml = None  # type: ignore[assignment]


class ProfileWizard:
    """Detects project type and applies the most appropriate governance profile.

    Args:
        base_path: Repository root.
    """

    _PROFILES = [
        {"name": "finops-v1.0", "type": "finops", "rules": ["FIN-001", "FIN-002", "FIN-003"]},
        {"name": "finops-v1.1", "type": "finops", "rules": ["FIN-001", "FIN-002", "FIN-003", "FIN-004"]},
        {"name": "auth-v1.0", "type": "auth", "rules": ["AUTH-001", "AUTH-002", "SEC-001"]},
        {"name": "ml-v1.0", "type": "ml", "rules": ["ML-001", "ML-002", "ML-003"]},
        {"name": "devops-v1.0", "type": "devops", "rules": ["DEV-001", "DEV-002"]},
        {"name": "general-v1.0", "type": "general", "rules": ["CORE-002", "CORE-008"]},
    ]

    # Keyword signals for each project type
    # Order matters: more specific first (ml before finops to avoid numpy collision)
    _REQUIREMENTS_SIGNALS: Dict[str, List[str]] = {
        "ml": ["tensorflow", "torch", "keras", "scikit-learn", "sklearn", "xgboost"],
        "auth": ["jwt", "oauth", "bcrypt", "passlib", "authlib"],
        "finops": ["pandas", "openpyxl", "xlrd", "finance", "ledger"],
    }
    _FOLDER_SIGNALS: Dict[str, List[str]] = {
        "auth": ["auth", "session", "jwt", "oauth"],
        "ml": ["model", "training", "inference", "dataset"],
    }
    _CI_SIGNALS: Dict[str, List[str]] = {
        "devops": [".github/workflows", ".circleci", ".travis.yml", "Jenkinsfile"],
    }

    def __init__(self, base_path: Path) -> None:
        """Initialize instance."""
        self.base_path = Path(base_path)

    # ── Detection ────────────────────────────────────────────────────

    def detect_project_type(self) -> str:
        """Detect the project type from filesystem signals.

        Detection order:
        1. ``requirements.txt`` keyword matching (finops → ml → auth)
        2. Folder name matching (auth, ml)
        3. CI/CD configuration files (devops)
        4. Defaults to ``"general"``

        Returns:
            One of: ``"finops"``, ``"auth"``, ``"ml"``, ``"devops"``, ``"general"``
        """
        # 1. requirements.txt
        req_file = self.base_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text().lower()
            for project_type, keywords in self._REQUIREMENTS_SIGNALS.items():
                if any(kw in content for kw in keywords):
                    return project_type

        # 2. Folder structure
        try:
            subdirs = [p.name.lower() for p in self.base_path.iterdir() if p.is_dir()]
        except Exception:
            subdirs = []
        for project_type, keywords in self._FOLDER_SIGNALS.items():
            if any(kw in subdirs for kw in keywords):
                return project_type

        # 3. CI/CD files
        for project_type, paths in self._CI_SIGNALS.items():
            if any((self.base_path / p).exists() for p in paths):
                return project_type

        return "general"

    # ── Suggestion ──────────────────────────────────────────────────

    def suggest_profile(self) -> Dict[str, Any]:
        """Suggest an appropriate governance profile.

        Returns:
            Dict with ``profile`` (name string), ``confidence`` (float 0-1),
            and ``explanation`` (str).
        """
        project_type = self.detect_project_type()
        # Find the matching profiles — pick the first (stable) version
        matches = [p for p in self._PROFILES if p["type"] == project_type]
        if not matches:
            matches = [p for p in self._PROFILES if p["type"] == "general"]

        # Pick the first (lowest stable) match
        best = matches[0]
        confidence = 0.9 if project_type != "general" else 0.6

        return {
            "profile": best["name"],
            "type": project_type,
            "confidence": confidence,
            "explanation": (
                f"Detected project type '{project_type}' from filesystem signals. "
                f"Recommending profile '{best['name']}' with confidence {confidence:.0%}."
            ),
        }

    # ── Customization ────────────────────────────────────────────────

    def customize_profile(
        self,
        profile: str,
        add_rules: Optional[List[str]] = None,
        remove_rules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Apply customizations to a profile's rule set.

        Args:
            profile: Profile name (e.g. ``"finops-v1.0"``).
            add_rules: Rule IDs to add.
            remove_rules: Rule IDs to remove.

        Returns:
            Dict with ``profile`` and ``rules`` keys.
        """
        base = next((p for p in self._PROFILES if p["name"] == profile), None)
        base_rules = list(base["rules"]) if base else []

        # Remove first, then add
        remove_rules = remove_rules or []
        add_rules = add_rules or []
        rules = [r for r in base_rules if r not in remove_rules]
        for rule in add_rules:
            if rule not in rules:
                rules.append(rule)

        return {"profile": profile, "rules": rules}

    def apply_profile(self, profile: str) -> Dict[str, Any]:
        """Apply a profile to the tier1 directory.

        Args:
            profile: Profile name.

        Returns:
            Dict with ``success`` bool.
        """
        base = next((p for p in self._PROFILES if p["name"] == profile), None)
        rules = base["rules"] if base else []

        tier1_dir = self.base_path / "cortex_intelligence" / "tier1"
        tier1_dir.mkdir(parents=True, exist_ok=True)

        rules_file = tier1_dir / "domain-rules.yaml"
        if yaml is not None:
            rules_file.write_text(
                yaml.dump({"profile": profile, "rules": rules}, default_flow_style=False)
            )
        else:
            lines = [f"profile: {profile}", "rules:"] + [f"  - {r}" for r in rules]
            rules_file.write_text("\n".join(lines) + "\n")

        return {"success": True, "profile": profile, "applied_rules": rules}

    # ── Listings ────────────────────────────────────────────────────

    def list_available_profiles(self) -> List[Dict[str, Any]]:
        """Return all available profiles.

        Returns:
            List of profile dicts with at least a ``name`` key.
        """
        return list(self._PROFILES)
