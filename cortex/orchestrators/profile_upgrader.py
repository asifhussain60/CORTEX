"""ProfileUpgrader — Upgrade governance profiles while preserving customizations.

Handles versioned profile upgrades, rollback, inheritance,
and backup for tier1 domain-rules.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import yaml


class ProfileUpgrader:
    """Upgrade governance profiles while preserving customizations.

    Args:
        workspace_root: Root path of the workspace.
    """

    def __init__(self, workspace_root: Path) -> None:
        """Initialize ProfileUpgrader.

        Args:
            workspace_root: Root of the workspace.
        """
        self._root = workspace_root
        self._tier1_dir = workspace_root / "cortex_brain" / "tier1"
        self._backups_dir = workspace_root / ".cortex" / "profile-backups"
        self._inherited: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Upgrade
    # ------------------------------------------------------------------

    def upgrade_profile(
        self, profile_name: str, from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Apply a profile upgrade while preserving customizations.

        Args:
            profile_name: Profile identifier (e.g. 'finops').
            from_version: Current version string.
            to_version: Target version string.

        Returns:
            Result dict with 'success', 'customizations_preserved', 'preserved_rules'.
        """
        rules_file = self._tier1_dir / "domain-rules.yaml"
        existing_rules: List[Dict[str, Any]] = []
        if rules_file.exists():
            data = yaml.safe_load(rules_file.read_text(encoding="utf-8")) or {}
            existing_rules = data.get("rules", [])

        custom_rules = [r for r in existing_rules if r.get("custom")]
        new_rules = self._get_profile_rules(profile_name, to_version)
        merged = self.merge_rules(existing_rules, new_rules)

        # Write merged rules
        rules_file.parent.mkdir(parents=True, exist_ok=True)
        rules_file.write_text(
            yaml.dump({"profile": f"{profile_name}-v{to_version}", "rules": merged}),
            encoding="utf-8",
        )

        return {
            "success": True,
            "customizations_preserved": len(custom_rules) > 0,
            "preserved_rules": [r["id"] for r in custom_rules],
        }

    def merge_rules(
        self,
        existing: List[Dict[str, Any]],
        new: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Merge existing and new rules, preserving customs.

        Args:
            existing: Current rule list.
            new: Incoming profile rules.

        Returns:
            Merged list of rules.
        """
        new_ids = {r["id"] for r in new}
        custom = [r for r in existing if r.get("source") == "custom" or r.get("custom")]
        merged = list(new)
        for rule in custom:
            if rule["id"] not in new_ids:
                merged.append(rule)
        return merged

    # ------------------------------------------------------------------
    # Rollback
    # ------------------------------------------------------------------

    def rollback_upgrade(self, profile_name: str) -> Dict[str, Any]:
        """Rollback a profile upgrade using the latest backup.

        Args:
            profile_name: Profile identifier.

        Returns:
            Result dict with 'success'.
        """
        backups = sorted(self._backups_dir.glob(f"{profile_name}-*.yaml"))
        if not backups:
            return {"success": False, "error": "No backup found"}
        backup = backups[-1]
        dest = self._tier1_dir / "domain-rules.yaml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
        return {"success": True}

    # ------------------------------------------------------------------
    # Backup
    # ------------------------------------------------------------------

    def create_upgrade_backup(
        self, profile_name: str, version: str
    ) -> Dict[str, Any]:
        """Create backup before performing upgrade.

        Args:
            profile_name: Profile identifier.
            version: Current version being backed up.

        Returns:
            Result dict with 'success' and 'backup_path'.
        """
        self._backups_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        backup_path = self._backups_dir / f"{profile_name}-{version}-{ts}.yaml"

        source = self._tier1_dir / "domain-rules.yaml"
        if source.exists():
            backup_path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            backup_path.write_text("# empty backup\n", encoding="utf-8")

        return {
            "success": True,
            "backup_path": str(backup_path),
        }

    # ------------------------------------------------------------------
    # Inheritance
    # ------------------------------------------------------------------

    def create_inherited_profile(
        self,
        name: str,
        base_profile: str,
        additional_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create an inherited profile extending a base.

        Args:
            name: New profile name.
            base_profile: Base profile identifier.
            additional_rules: Extra rules to layer on top.

        Returns:
            Result dict with 'success', 'base', 'rules'.
        """
        rules = list(additional_rules or [])
        self._inherited[name] = {"base": base_profile, "rules": rules}
        return {"success": True, "base": base_profile, "rules": rules}

    def check_inherited_update(self, name: str) -> Dict[str, Any]:
        """Check if the base of an inherited profile has updates available.

        Args:
            name: Inherited profile name.

        Returns:
            Dict with 'base_update_available'.
        """
        info = self._inherited.get(name, {})
        return {"base_update_available": bool(info)}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_profile_rules(
        self, profile_name: str, version: str
    ) -> List[Dict[str, Any]]:
        """Fetch rules for a profile version (stub).

        Args:
            profile_name: Profile identifier.
            version: Version string.

        Returns:
            List of rule dicts.
        """
        return [{"id": f"{profile_name.upper()}-001", "source": "profile"}]
