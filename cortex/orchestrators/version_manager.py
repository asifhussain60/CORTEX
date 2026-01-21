"""
VersionManager - CORTEX version detection and compatibility.

Detects current version, checks GitHub/PyPI for updates, and builds
compatibility matrix for upgrades.

AC-ID: AC-DEP-005-01
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None  # Will be mocked in tests


class VersionManager:
    """
    Manager for CORTEX version detection and compatibility.
    
    Handles version reading, release checking, and upgrade path analysis.
    Follows CORE-008 (TDD) and CORE-011 (type hints).
    """
    
    GITHUB_REPO = "asifhussain60/CORTEX"
    PYPI_PACKAGE = "cortex"
    
    def __init__(self, repo_path: Path):
        """
        Initialize VersionManager.
        
        Args:
            repo_path: Path to the repository root.
        """
        self.repo_path = Path(repo_path)
    
    def get_current_version(self) -> str:
        """
        Get current version from .cortex-version or pyproject.toml.
        
        Returns:
            Current version string.
        """
        # Try .cortex-version first
        version_file = self.repo_path / ".cortex-version"
        if version_file.exists():
            return version_file.read_text().strip()
        
        # Try pyproject.toml
        pyproject_path = self.repo_path / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        # Try VERSION file
        version_path = self.repo_path / "VERSION"
        if version_path.exists():
            return version_path.read_text().strip()
        
        return "0.0.0"
    
    def check_github_releases(self) -> List[Dict[str, Any]]:
        """
        Check GitHub releases API for available versions.
        
        Returns:
            List of release information dictionaries.
        """
        if requests is None:
            return []
        
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            releases = []
            for release in response.json():
                tag = release.get("tag_name", "")
                version = tag.lstrip("v")
                releases.append({
                    "version": version,
                    "tag": tag,
                    "name": release.get("name", ""),
                    "published": release.get("published_at", ""),
                    "url": release.get("html_url", "")
                })
            
            return releases
            
        except Exception:
            return []
    
    def check_pypi_releases(self) -> List[str]:
        """
        Check PyPI for available versions.
        
        Returns:
            List of version strings.
        """
        if requests is None:
            return []
        
        try:
            url = f"https://pypi.org/pypi/{self.PYPI_PACKAGE}/json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            return list(data.get("releases", {}).keys())
            
        except Exception:
            return []
    
    def build_compatibility_matrix(
        self,
        current: str,
        target: str
    ) -> Dict[str, Any]:
        """
        Build compatibility matrix for version upgrade.
        
        Args:
            current: Current version string.
            target: Target version string.
            
        Returns:
            Compatibility matrix dictionary.
        """
        current_parts = self._parse_version(current)
        target_parts = self._parse_version(target)
        
        # Determine upgrade type
        if target_parts["major"] > current_parts["major"]:
            upgrade_type = "major"
            requires_migration = True
        elif target_parts["minor"] > current_parts["minor"]:
            upgrade_type = "minor"
            requires_migration = False
        else:
            upgrade_type = "patch"
            requires_migration = False
        
        return {
            "current": current,
            "target": target,
            "upgrade_type": upgrade_type,
            "compatible": True,  # Can be enhanced with actual compatibility checks
            "requires_migration": requires_migration,
            "breaking_changes": [],
            "deprecated_features": []
        }
    
    def _parse_version(self, version: str) -> Dict[str, int]:
        """Parse version string into components."""
        match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
        if match:
            return {
                "major": int(match.group(1)),
                "minor": int(match.group(2)),
                "patch": int(match.group(3))
            }
        return {"major": 0, "minor": 0, "patch": 0}
    
    def display_upgrade_path(
        self,
        current: str,
        target: str
    ) -> Dict[str, Any]:
        """
        Display upgrade path with steps.
        
        Args:
            current: Current version.
            target: Target version.
            
        Returns:
            Upgrade path information.
        """
        matrix = self.build_compatibility_matrix(current, target)
        
        steps = [
            f"1. Create snapshot of v{current}",
            f"2. Download v{target} package",
            "3. Run validation tests",
            f"4. Apply differential upgrade from v{current} to v{target}",
            "5. Verify tier1 rules preserved",
            "6. Run post-upgrade validation"
        ]
        
        if matrix["requires_migration"]:
            steps.insert(2, "2a. Review migration guide for breaking changes")
        
        return {
            "from": current,
            "to": target,
            "steps": steps,
            "safe_upgrade": not matrix["requires_migration"],
            "estimated_time": "5-10 minutes" if not matrix["requires_migration"] else "15-30 minutes"
        }
    
    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest available version.
        
        Returns:
            Latest version string or None.
        """
        releases = self.check_github_releases()
        if releases:
            return releases[0]["version"]
        
        pypi_versions = self.check_pypi_releases()
        if pypi_versions:
            # Sort and get latest
            sorted_versions = sorted(
                pypi_versions,
                key=lambda v: [int(x) for x in v.split(".")[:3] if x.isdigit()],
                reverse=True
            )
            return sorted_versions[0] if sorted_versions else None
        
        return None
    
    def is_update_available(self) -> Dict[str, Any]:
        """
        Check if an update is available.
        
        Returns:
            Update availability information.
        """
        current = self.get_current_version()
        latest = self.get_latest_version()
        
        if not latest:
            return {"available": False, "error": "Could not check for updates"}
        
        current_parts = self._parse_version(current)
        latest_parts = self._parse_version(latest)
        
        available = (
            latest_parts["major"] > current_parts["major"] or
            (latest_parts["major"] == current_parts["major"] and 
             latest_parts["minor"] > current_parts["minor"]) or
            (latest_parts["major"] == current_parts["major"] and
             latest_parts["minor"] == current_parts["minor"] and
             latest_parts["patch"] > current_parts["patch"])
        )
        
        return {
            "available": available,
            "current": current,
            "latest": latest,
            "upgrade_type": self.build_compatibility_matrix(current, latest)["upgrade_type"] if available else None
        }
