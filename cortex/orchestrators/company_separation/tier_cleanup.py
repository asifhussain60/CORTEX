"""Phase 47 S4: Tier Cleanup and Company Registry Migration.

Extract company overrides from cortex_brain/tiers/ into registry.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class TierOverride:
    """A tier override extracted from tier files."""

    tier_name: str
    override_type: str  # "domain", "governance", "config", "dashboard"
    original_path: str
    target_path: str
    content: Dict[str, Any]


class TierAnalyzer:
    """Analyze tier files for company overrides."""

    def __init__(
        self,
        tier_root: str = "/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier0",
    ):
        """Initialize analyzer.

        Args:
            tier_root: Root path to tier files
        """
        self.tier_root = tier_root
        self.overrides: List[TierOverride] = []

    def analyze_tier(self, tier_file: str) -> List[TierOverride]:
        """Analyze a tier file for company overrides.

        Args:
            tier_file: Path to tier file

        Returns:
            List of TierOverride objects found.
        """
        overrides = []

        if not Path(tier_file).exists():
            return overrides

        try:
            with open(tier_file, 'r') as f:
                content = yaml.safe_load(f) or {}
        except Exception:
            return overrides

        # Check for company-specific keys
        if isinstance(content, dict):
            for key, value in content.items():
                if self._is_company_override(key, value):
                    override = TierOverride(
                        tier_name=Path(tier_file).stem,
                        override_type=self._classify_override(key),
                        original_path=tier_file,
                        target_path=self._compute_target_path(key),
                        content={"content": value},
                    )
                    overrides.append(override)

        self.overrides.extend(overrides)
        return overrides

    def analyze_directory(self, directory: str) -> List[TierOverride]:
        """Analyze all tier files in directory.

        Args:
            directory: Directory to analyze

        Returns:
            List of all TierOverride objects found.
        """
        overrides = []

        for file_path in Path(directory).rglob("*.yaml"):
            file_overrides = self.analyze_tier(str(file_path))
            overrides.extend(file_overrides)

        return overrides

    def get_overrides_by_type(self, override_type: str) -> List[TierOverride]:
        """Get overrides by type.

        Args:
            override_type: Override type to filter by

        Returns:
            List of TierOverride objects.
        """
        return [o for o in self.overrides if o.override_type == override_type]

    def _is_company_override(self, key: str, value: Any) -> bool:
        """Check if key represents company override.

        Args:
            key: Key name
            value: Value

        Returns:
            True if company override.
        """
        company_markers = [
            "company_",
            "_company",
            "customer_",
            "_custom",
            "override_",
        ]

        return any(marker in key.lower() for marker in company_markers)

    def _classify_override(self, key: str) -> str:
        """Classify override type.

        Args:
            key: Key name

        Returns:
            Override type.
        """
        if "domain" in key.lower():
            return "domain"
        elif "governance" in key.lower():
            return "governance"
        elif "config" in key.lower():
            return "config"
        elif "dashboard" in key.lower():
            return "dashboard"
        else:
            return "generic"

    def _compute_target_path(self, key: str) -> str:
        """Compute target path in registry.

        Args:
            key: Key name

        Returns:
            Target path in registry.
        """
        override_type = self._classify_override(key)
        return f"cortex-registry/company/{override_type}/{key}.yaml"

    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary.

        Returns:
            Dictionary with summary.
        """
        return {
            "total_overrides": len(self.overrides),
            "by_type": {
                "domain": len(self.get_overrides_by_type("domain")),
                "governance": len(self.get_overrides_by_type("governance")),
                "config": len(self.get_overrides_by_type("config")),
                "dashboard": len(self.get_overrides_by_type("dashboard")),
            },
        }


class TierCleanup:
    """Clean tier files by removing company overrides."""

    def __init__(self, analyzer: TierAnalyzer):
        """Initialize cleanup.

        Args:
            analyzer: TierAnalyzer instance
        """
        self.analyzer = analyzer
        self.removals: List[str] = []
        self.migrations: List[Dict[str, str]] = []

    def cleanup_file(self, tier_file: str) -> bool:
        """Clean a tier file.

        Args:
            tier_file: Path to tier file to clean

        Returns:
            True if cleanup successful.
        """
        try:
            with open(tier_file, 'r') as f:
                content = yaml.safe_load(f) or {}
        except Exception:
            return False

        if not isinstance(content, dict):
            return False

        # Remove company overrides
        original_content = content.copy()
        for key in list(content.keys()):
            if self.analyzer._is_company_override(key, content[key]):
                del content[key]
                self.removals.append(f"{tier_file}:{key}")

        # Write back if changed
        if content != original_content:
            try:
                with open(tier_file, 'w') as f:
                    yaml.dump(content, f)
                return True
            except Exception:
                return False

        return False

    def cleanup_directory(self, directory: str) -> int:
        """Clean all tier files in directory.

        Args:
            directory: Directory to clean

        Returns:
            Count of files cleaned.
        """
        count = 0

        for file_path in Path(directory).rglob("*.yaml"):
            if self.cleanup_file(str(file_path)):
                count += 1

        return count

    def add_migration(self, source_key: str, target_path: str) -> None:
        """Add migration record.

        Args:
            source_key: Source key
            target_path: Target path in registry
        """
        self.migrations.append(
            {
                "source": source_key,
                "target": target_path,
                "status": "migrated",
            }
        )

    def get_migration_summary(self) -> Dict[str, Any]:
        """Get migration summary.

        Returns:
            Dictionary with migration summary.
        """
        return {
            "total_removals": len(self.removals),
            "total_migrations": len(self.migrations),
            "removals": self.removals[:10],  # First 10
            "migrations": self.migrations[:10],
        }


class TierBackup:
    """Create backup of tier files before cleanup."""

    def __init__(self, tier_root: str = "/Users/asifhussain/PROJECTS/CORTEX/cortex_brain"):
        """Initialize backup.

        Args:
            tier_root: Root path to tier files
        """
        self.tier_root = tier_root
        self.backup_path = f"{tier_root}/tier_backup"
        self.backed_up_files: List[str] = []

    def create_backup(self) -> bool:
        """Create backup of tier directory.

        Returns:
            True if backup created.
        """
        try:
            backup_dir = Path(self.backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Copy all tier files
            for tier_dir in Path(self.tier_root).glob("tier*"):
                if tier_dir.is_dir():
                    for file_path in tier_dir.rglob("*.yaml"):
                        relative = file_path.relative_to(self.tier_root)
                        backup_file = backup_dir / relative
                        backup_file.parent.mkdir(parents=True, exist_ok=True)
                        backup_file.write_text(file_path.read_text())
                        self.backed_up_files.append(str(relative))

            return len(self.backed_up_files) > 0
        except Exception:
            return False

    def get_backup_size(self) -> int:
        """Get number of backed-up files.

        Returns:
            Count of backed-up files.
        """
        return len(self.backed_up_files)

    def get_backup_location(self) -> str:
        """Get backup location.

        Returns:
            Path to backup directory.
        """
        return self.backup_path
