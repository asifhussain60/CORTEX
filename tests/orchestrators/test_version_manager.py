"""
Tests for VersionManager - CORTEX version detection and compatibility.

TDD Tests for version detection from GitHub/PyPI and compatibility matrix.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json


class TestVersionManagerCurrentVersion:
    """Tests for reading current version."""

    def test_read_current_version_from_file(self, tmp_path):
        """Should read version from .cortex-version file."""
        from cortex.orchestrators.version_manager import VersionManager
        
        version_file = tmp_path / ".cortex-version"
        version_file.write_text("7.2.0")
        
        manager = VersionManager(tmp_path)
        version = manager.get_current_version()
        
        assert version == "7.2.0"

    def test_read_version_from_pyproject(self, tmp_path):
        """Should read version from pyproject.toml as fallback."""
        from cortex.orchestrators.version_manager import VersionManager
        
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "7.1.5"')
        
        manager = VersionManager(tmp_path)
        version = manager.get_current_version()
        
        assert version == "7.1.5"

    def test_default_version_when_not_found(self, tmp_path):
        """Should return 0.0.0 when no version found."""
        from cortex.orchestrators.version_manager import VersionManager
        
        manager = VersionManager(tmp_path)
        version = manager.get_current_version()
        
        assert version == "0.0.0"


class TestVersionManagerGitHubReleases:
    """Tests for checking GitHub releases."""

    def test_check_github_releases(self):
        """Should fetch releases from GitHub API."""
        from cortex.orchestrators.version_manager import VersionManager
        
        manager = VersionManager(Path("."))
        
        with patch('cortex.orchestrators.version_manager.requests') as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"tag_name": "v7.3.0", "name": "Release 7.3.0"},
                {"tag_name": "v7.2.0", "name": "Release 7.2.0"},
            ]
            mock_requests.get.return_value = mock_response
            
            releases = manager.check_github_releases()
            
            assert len(releases) >= 2
            assert "7.3.0" in [r["version"] for r in releases]

    def test_github_releases_handles_error(self):
        """Should handle GitHub API errors gracefully."""
        from cortex.orchestrators.version_manager import VersionManager
        
        manager = VersionManager(Path("."))
        
        with patch('cortex.orchestrators.version_manager.requests') as mock_requests:
            mock_requests.get.side_effect = Exception("Network error")
            
            releases = manager.check_github_releases()
            
            assert releases == []


class TestVersionManagerPyPIReleases:
    """Tests for checking PyPI releases."""

    def test_check_pypi_releases(self):
        """Should fetch releases from PyPI API."""
        from cortex.orchestrators.version_manager import VersionManager
        
        manager = VersionManager(Path("."))
        
        with patch('cortex.orchestrators.version_manager.requests') as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "releases": {
                    "7.3.0": [],
                    "7.2.0": [],
                    "7.1.0": []
                }
            }
            mock_requests.get.return_value = mock_response
            
            releases = manager.check_pypi_releases()
            
            assert "7.3.0" in releases


class TestVersionManagerCompatibility:
    """Tests for compatibility matrix building."""

    def test_build_compatibility_matrix(self):
        """Should build compatibility matrix for version upgrade."""
        from cortex.orchestrators.version_manager import VersionManager
        
        manager = VersionManager(Path("."))
        
        matrix = manager.build_compatibility_matrix("7.2.0", "7.3.0")
        
        assert matrix["current"] == "7.2.0"
        assert matrix["target"] == "7.3.0"
        assert matrix["compatible"] is True
        assert matrix["upgrade_type"] == "minor"

    def test_major_version_requires_migration(self):
        """Should flag major version as requiring migration."""
        from cortex.orchestrators.version_manager import VersionManager
        
        manager = VersionManager(Path("."))
        
        matrix = manager.build_compatibility_matrix("7.2.0", "8.0.0")
        
        assert matrix["upgrade_type"] == "major"
        assert matrix["requires_migration"] is True

    def test_display_upgrade_path(self):
        """Should display upgrade path with steps."""
        from cortex.orchestrators.version_manager import VersionManager
        
        manager = VersionManager(Path("."))
        
        path = manager.display_upgrade_path("7.2.0", "7.3.0")
        
        assert "7.2.0" in path["from"]
        assert "7.3.0" in path["to"]
        assert len(path["steps"]) > 0
        assert path["safe_upgrade"] is True
