"""
version_manager — CORTEX version detection and compatibility.

This is the **canonical** module.  ``orchestrator_version_manager`` re-exports
from here so that tests patching ``cortex.orchestrators.version_manager.requests``
intercept the live reference correctly.

Authority: CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

try:
    import tomllib  # type: ignore[import]  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[import,no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

# Kept at module level so unit tests can patch
# ``cortex.orchestrators.version_manager.requests``.
try:
    import requests  # type: ignore[import]
except ImportError:
    requests = None  # type: ignore[assignment]


class VersionManager:
    """Detects the installed CORTEX version and checks for upgrades.

    Args:
        base_path: Repository root (used to locate ``.cortex-version`` /
            ``pyproject.toml``).
    """

    GITHUB_API = "https://api.github.com/repos/asifhussain60/CORTEX/releases"
    PYPI_API = "https://pypi.org/pypi/cortex/json"

    def __init__(self, base_path: Path) -> None:
        """Initialize instance."""
        self.base_path = Path(base_path)

    # ── Current version detection ────────────────────────────────────

    def get_current_version(self) -> str:
        """Return the current CORTEX version string.

        Checks in order:
        1. ``.cortex-version`` file
        2. ``pyproject.toml`` ``[project].version``
        3. Falls back to ``"0.0.0"``.
        """
        version_file = self.base_path / ".cortex-version"
        if version_file.exists():
            return version_file.read_text().strip()

        pyproject = self.base_path / "pyproject.toml"
        if pyproject.exists():
            try:
                text = pyproject.read_text()
                if tomllib is not None:
                    data = tomllib.loads(text)
                    v = (
                        data.get("project", {}).get("version")
                        or data.get("tool", {}).get("poetry", {}).get("version")
                    )
                    if v:
                        return v
                m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', text)
                if m:
                    return m.group(1)
            except Exception:
                pass

        return "0.0.0"

    # ── Remote releases ──────────────────────────────────────────────

    def check_github_releases(self) -> List[Dict[str, str]]:
        """Fetch release list from GitHub.

        Returns ``[]`` on any network/parsing error.
        """
        import cortex.orchestrators.version_manager as _mod

        _requests = _mod.requests
        if _requests is None:
            return []
        try:
            response = _requests.get(self.GITHUB_API, timeout=10)
            releases = []
            for item in response.json():
                tag = item.get("tag_name", "").lstrip("v")
                releases.append({"version": tag, "name": item.get("name", tag)})
            return releases
        except Exception:
            return []

    def check_pypi_releases(self) -> List[str]:
        """Fetch release list from PyPI.

        Returns ``[]`` on error.
        """
        import cortex.orchestrators.version_manager as _mod

        _requests = _mod.requests
        if _requests is None:
            return []
        try:
            response = _requests.get(self.PYPI_API, timeout=10)
            data = response.json()
            return list(data.get("releases", {}).keys())
        except Exception:
            return []

    # ── Compatibility matrix ─────────────────────────────────────────

    def build_compatibility_matrix(
        self,
        current: str,
        target: str,
    ) -> Dict[str, Any]:
        """Build a compatibility matrix for a version upgrade."""
        cur_parts = [int(x) for x in current.split(".")]
        tgt_parts = [int(x) for x in target.split(".")]

        if tgt_parts[0] > cur_parts[0]:
            upgrade_type = "major"
            requires_migration = True
            compatible = False
        elif tgt_parts[1] > cur_parts[1]:
            upgrade_type = "minor"
            requires_migration = False
            compatible = True
        else:
            upgrade_type = "patch"
            requires_migration = False
            compatible = True

        return {
            "current": current,
            "target": target,
            "compatible": compatible,
            "upgrade_type": upgrade_type,
            "requires_migration": requires_migration,
        }

    def display_upgrade_path(
        self,
        current: str,
        target: str,
    ) -> Dict[str, Any]:
        """Return a structured upgrade path description."""
        matrix = self.build_compatibility_matrix(current, target)
        steps = [f"Upgrade from {current} to {target}"]
        if matrix.get("requires_migration"):
            steps.insert(0, "Run migration scripts")
        return {
            "from": current,
            "to": target,
            "steps": steps,
            "safe_upgrade": not matrix.get("requires_migration", False),
        }


__all__ = ["VersionManager", "requests", "tomllib"]
