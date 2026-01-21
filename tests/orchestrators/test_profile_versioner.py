"""
Tests for ProfileVersioner - Profile version tracking and updates.

TDD Tests for tracking applied profiles and detecting updates.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


class TestProfileVersionerTracking:
    """Tests for tracking applied profiles."""

    def test_track_applied_profile(self, tmp_path):
        """Should track which profile is applied to a project."""
        from cortex.orchestrators.profile_versioner import ProfileVersioner
        
        versioner = ProfileVersioner(tmp_path)
        versioner.track_profile("KASHKOLE", "finops-v1.0")
        
        tracked = versioner.get_applied_profile("KASHKOLE")
        
        assert tracked["profile"] == "finops-v1.0"
        assert "applied_at" in tracked

    def test_detect_profile_updates(self, tmp_path):
        """Should detect when profile updates are available."""
        from cortex.orchestrators.profile_versioner import ProfileVersioner
        
        versioner = ProfileVersioner(tmp_path)
        versioner.track_profile("KASHKOLE", "finops-v1.0")
        
        # Mock available profiles including v1.1
        with patch.object(versioner, '_get_available_versions') as mock:
            mock.return_value = ["1.0", "1.1", "1.2"]
            
            updates = versioner.check_for_updates("KASHKOLE")
            
            assert updates["update_available"] is True
            assert updates["latest_version"] == "1.2"


class TestProfileVersionerDiff:
    """Tests for version diff computation."""

    def test_show_upgrade_diff(self, tmp_path):
        """Should show diff between profile versions."""
        from cortex.orchestrators.profile_versioner import ProfileVersioner
        
        versioner = ProfileVersioner(tmp_path)
        
        diff = versioner.compute_version_diff("finops", "1.0", "1.1")
        
        assert "added_rules" in diff
        assert "removed_rules" in diff
        assert "modified_rules" in diff

    def test_profile_compatibility_check(self, tmp_path):
        """Should check compatibility between versions."""
        from cortex.orchestrators.profile_versioner import ProfileVersioner
        
        versioner = ProfileVersioner(tmp_path)
        
        compat = versioner.check_compatibility("finops", "1.0", "1.1")
        
        assert compat["compatible"] is True
        assert "breaking_changes" in compat


class TestProfileVersionerRegistry:
    """Tests for profile version registry."""

    def test_register_profile_version(self, tmp_path):
        """Should register new profile versions."""
        from cortex.orchestrators.profile_versioner import ProfileVersioner
        
        versioner = ProfileVersioner(tmp_path)
        
        result = versioner.register_version(
            profile="finops",
            version="1.1",
            changelog="Added 3 new compliance rules"
        )
        
        assert result["success"] is True
        assert result["version"] == "1.1"

    def test_get_version_history(self, tmp_path):
        """Should retrieve version history for a profile."""
        from cortex.orchestrators.profile_versioner import ProfileVersioner
        
        versioner = ProfileVersioner(tmp_path)
        versioner.register_version("finops", "1.0", "Initial release")
        versioner.register_version("finops", "1.1", "Added compliance")
        
        history = versioner.get_version_history("finops")
        
        assert len(history) >= 2
        assert history[0]["version"] in ["1.0", "1.1"]


class TestProfileVersionerComparison:
    """Tests for version comparison utilities."""

    def test_compare_semantic_versions(self, tmp_path):
        """Should compare semantic versions correctly."""
        from cortex.orchestrators.profile_versioner import ProfileVersioner
        
        versioner = ProfileVersioner(tmp_path)
        
        # Newer versions
        assert versioner._is_newer_version("1.1", "1.0") is True
        assert versioner._is_newer_version("2.0", "1.9") is True
        
        # Older versions
        assert versioner._is_newer_version("1.0", "1.1") is False
        
    def test_detect_major_version_change(self, tmp_path):
        """Should detect major version changes."""
        from cortex.orchestrators.profile_versioner import ProfileVersioner
        
        versioner = ProfileVersioner(tmp_path)
        
        compat = versioner.check_compatibility("finops", "1.0", "2.0")
        
        # Major version change may have breaking changes
        assert "breaking_changes" in compat
