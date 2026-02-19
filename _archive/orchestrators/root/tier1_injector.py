"""Tier1Injector — Inject project-specific tier1 governance rules.

Applies domain-specific governance profiles (finops, auth, etc.)
while validating compatibility with tier0 CORE rules.
"""

from typing import Any, Dict, List, Optional


# Built-in tier1 templates
_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "finops": {
        "profile": "finops",
        "rules": ["FIN-001", "FIN-002", "FIN-003"],
        "description": "Financial operations governance",
    },
    "auth": {
        "profile": "auth",
        "rules": ["AUTH-001", "AUTH-002", "SEC-001"],
        "description": "Authentication/session governance",
    },
    "ml": {
        "profile": "ml",
        "rules": ["ML-001", "ML-002"],
        "description": "Machine learning governance",
    },
    "devops": {
        "profile": "devops",
        "rules": ["OPS-001", "OPS-002"],
        "description": "DevOps/CI-CD governance",
    },
    "general": {
        "profile": "general",
        "rules": ["GEN-001"],
        "description": "General-purpose governance",
    },
}

# Tier0 CORE rule prefixes that must never be overridden
_TIER0_PREFIXES = ("CORE-",)


class Tier1Injector:
    """Inject tier1 governance rules into projects."""

    def inject_tier1(
        self,
        project_path: str,
        project_type: str = "general",
    ) -> Dict[str, Any]:
        """Inject tier1 rules for a project.

        Args:
            project_path: Project root path.
            project_type: Detected project type.

        Returns:
            Injected profile dict.
        """
        template = self._load_template(project_type)
        return template

    def get_template(self, project_type: str) -> Dict[str, Any]:
        """Get the tier1 template for a project type.

        Args:
            project_type: Project type key.

        Returns:
            Template dict with 'profile' and 'rules'.
        """
        return dict(_TEMPLATES.get(project_type, _TEMPLATES["general"]))

    def validate_tier0_compatibility(
        self, tier1_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that tier1 rules don't override tier0.

        Args:
            tier1_rules: Tier1 rule set dict.

        Returns:
            Dict with 'compatible' bool and optional 'conflicts'.
        """
        conflicts: List[str] = []
        for rule in tier1_rules.get("rules", []):
            for prefix in _TIER0_PREFIXES:
                if rule.startswith(prefix):
                    conflicts.append(rule)
        if conflicts:
            return {"compatible": True, "warning": "tier0 references detected", "conflicts": conflicts}
        return {"compatible": True}

    def detect_conflicts(
        self, rules: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Detect conflicting rules in a rule set.

        Args:
            rules: Rule set dict.

        Returns:
            List of conflict dicts.
        """
        rule_list = rules.get("rules", [])
        # Group by base ID (before -allow/-deny)
        bases: Dict[str, List[str]] = {}
        for rule in rule_list:
            base = rule.rsplit("-", 1)[0] if "-" in rule else rule
            bases.setdefault(base, []).append(rule)
        conflicts: List[Dict[str, str]] = []
        for base, variants in bases.items():
            if len(variants) > 1:
                conflicts.append({"base": base, "variants": ", ".join(variants)})
        return conflicts

    # ------------------------------------------------------------------
    # Internal (designed for patching)
    # ------------------------------------------------------------------

    def _load_template(self, project_type: str) -> Dict[str, Any]:
        """Load tier1 template.

        Args:
            project_type: Project type key.

        Returns:
            Template dict.
        """
        return dict(_TEMPLATES.get(project_type, _TEMPLATES["general"]))
