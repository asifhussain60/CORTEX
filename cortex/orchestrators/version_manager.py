"""VersionManager — CORTEX version detection and compatibility.

Reads current version from .cortex-version or pyproject.toml,
checks GitHub/PyPI for releases, and builds compatibility matrices.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests  # noqa: F401 — used dynamically via patch in tests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]


class VersionManager:
    """Manage CORTEX version detection and upgrade paths.

    Args:
        workspace_root: Root path of the workspace.
    """

    def __init__(self, workspace_root: Path) -> None:
        """Initialize VersionManager.

        Args:
            workspace_root: Root path.
        """
        self._root = workspace_root
        self.logger = logging.getLogger("VersionManager")

    # ------------------------------------------------------------------
    # Current version
    # ------------------------------------------------------------------

    def get_current_version(self) -> str:
        """Read the current CORTEX version.

        Checks (in order): .cortex-version, pyproject.toml.

        Returns:
            Version string, or '0.0.0' if not found.
        """
        version_file = self._root / ".cortex-version"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()

        pyproject = self._root / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)

        return "0.0.0"

    # ------------------------------------------------------------------
    # Remote releases
    # ------------------------------------------------------------------

    def check_github_releases(self) -> List[Dict[str, Any]]:
        """Fetch releases from the GitHub API.

        Returns:
            List of release dicts with 'version' and 'name' keys.
        """
        try:
            resp = requests.get(
                "https://api.github.com/repos/cortex/cortex/releases",
                timeout=10,
            )
            if resp.status_code != 200:
                return []
            return [
                {
                    "version": r["tag_name"].lstrip("v"),
                    "name": r.get("name", ""),
                }
                for r in resp.json()
            ]
        except Exception:
            return []

    def check_pypi_releases(self) -> List[str]:
        """Fetch available versions from PyPI.

        Returns:
            List of version strings.
        """
        try:
            resp = requests.get(
                "https://pypi.org/pypi/cortex/json",
                timeout=10,
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return sorted(data.get("releases", {}).keys())
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Compatibility
    # ------------------------------------------------------------------

    def build_compatibility_matrix(
        self, current: str, target: str
    ) -> Dict[str, Any]:
        """Build compatibility matrix for a version upgrade.

        Args:
            current: Current version string.
            target: Target version string.

        Returns:
            Dict with 'current', 'target', 'compatible',
            'upgrade_type', and optionally 'requires_migration'.
        """
        cur_parts = self._parse_version(current)
        tgt_parts = self._parse_version(target)

        if tgt_parts[0] > cur_parts[0]:
            upgrade_type = "major"
        elif tgt_parts[1] > cur_parts[1]:
            upgrade_type = "minor"
        else:
            upgrade_type = "patch"

        requires_migration = upgrade_type == "major"

        return {
            "current": current,
            "target": target,
            "compatible": not requires_migration,
            "upgrade_type": upgrade_type,
            "requires_migration": requires_migration,
        }

    def display_upgrade_path(
        self, from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Display the upgrade path with steps.

        Args:
            from_version: Source version.
            to_version: Target version.

        Returns:
            Dict with 'from', 'to', 'steps', 'safe_upgrade'.
        """
        matrix = self.build_compatibility_matrix(from_version, to_version)
        steps = [
            f"Backup current ({from_version})",
            f"Download {to_version}",
            "Run migration scripts" if matrix.get("requires_migration") else "Apply update",
            "Validate upgrade",
        ]
        return {
            "from": from_version,
            "to": to_version,
            "steps": steps,
            "safe_upgrade": matrix["compatible"],
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_version(version: str) -> List[int]:
        """Parse a semantic version into integer parts.

        Args:
            version: Semver string.

        Returns:
            List of [major, minor, patch].
        """
        parts = version.split(".")
        return [int(p) for p in parts[:3]]
