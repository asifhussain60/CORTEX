"""
Tests for ProfileUpgrader - Profile upgrade and migration.

TDD Tests for upgrading profiles while preserving customizations.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


class TestProfileUpgraderUpgrade:
    """Tests for profile upgrades."""

    def test_apply_profile_upgrade(self, tmp_path):
        """Should apply profile upgrade while preserving customizations."""
        from cortex.orchestrators.profile_upgrader import ProfileUpgrader
        
        # Create existing tier1 with customizations
        tier1_dir = tmp_path / "cortex_brain" / "tier1"
        tier1_dir.mkdir(parents=True)
        (tier1_dir / "domain-rules.yaml").write_text("""
profile: finops-v1.0
rules:
  - id: FIN-001
    severity: high
  - id: CUSTOM-001
    severity: medium
    custom: true
""")
        
        upgrader = ProfileUpgrader(tmp_path)
        result = upgrader.upgrade_profile("finops", "1.0", "1.1")
        
        assert result["success"] is True
        assert result["customizations_preserved"] is True
        assert "CUSTOM-001" in str(result["preserved_rules"])

    def test_upgrade_preserves_custom_rules(self, tmp_path):
        """Should preserve custom rules during upgrade."""
        from cortex.orchestrators.profile_upgrader import ProfileUpgrader
        
        upgrader = ProfileUpgrader(tmp_path)
        
        existing_rules = [
            {"id": "FIN-001", "source": "profile"},
            {"id": "CUSTOM-001", "source": "custom"}
        ]
        new_rules = [
            {"id": "FIN-001", "source": "profile"},
            {"id": "FIN-002", "source": "profile"}
        ]
        
        merged = upgrader.merge_rules(existing_rules, new_rules)
        
        # Custom rule preserved, new rule added
        rule_ids = [r["id"] for r in merged]
        assert "CUSTOM-001" in rule_ids
        assert "FIN-002" in rule_ids


class TestProfileUpgraderRollback:
    """Tests for profile upgrade rollback."""

    def test_rollback_profile_upgrade(self, tmp_path):
        """Should rollback profile upgrade on failure."""
        from cortex.orchestrators.profile_upgrader import ProfileUpgrader
        
        # Create backup-able state
        tier1_dir = tmp_path / "cortex_brain" / "tier1"
        tier1_dir.mkdir(parents=True)
        (tier1_dir / "domain-rules.yaml").write_text("original: content")
        
        upgrader = ProfileUpgrader(tmp_path)
        upgrader.create_upgrade_backup("finops", "1.0")
        
        result = upgrader.rollback_upgrade("finops")
        
        assert result["success"] is True
        content = (tier1_dir / "domain-rules.yaml").read_text()
        assert "original" in content


class TestProfileUpgraderInheritance:
    """Tests for profile inheritance."""

    def test_profile_inheritance(self, tmp_path):
        """Should support profile inheritance (extends base profile)."""
        from cortex.orchestrators.profile_upgrader import ProfileUpgrader
        
        upgrader = ProfileUpgrader(tmp_path)
        
        result = upgrader.create_inherited_profile(
            name="my-finops",
            base_profile="finops-v1.0",
            additional_rules=[{"id": "MY-001", "description": "Custom rule"}]
        )
        
        assert result["success"] is True
        assert result["base"] == "finops-v1.0"
        assert "MY-001" in [r["id"] for r in result["rules"]]

    def test_inherited_profile_updates_with_base(self, tmp_path):
        """Should update inherited profile when base updates."""
        from cortex.orchestrators.profile_upgrader import ProfileUpgrader
        
        upgrader = ProfileUpgrader(tmp_path)
        
        # Create inherited profile
        upgrader.create_inherited_profile(
            name="my-finops",
            base_profile="finops-v1.0",
            additional_rules=[{"id": "MY-001"}]
        )
        
        # Check if base update available
        result = upgrader.check_inherited_update("my-finops")
        
        assert "base_update_available" in result


class TestProfileUpgraderBackup:
    """Tests for backup functionality."""

    def test_create_backup_before_upgrade(self, tmp_path):
        """Should create backup before performing upgrade."""
        from cortex.orchestrators.profile_upgrader import ProfileUpgrader
        
        # Create existing rules
        tier1_dir = tmp_path / "cortex_brain" / "tier1"
        tier1_dir.mkdir(parents=True)
        (tier1_dir / "domain-rules.yaml").write_text("rules: []\n")
        
        upgrader = ProfileUpgrader(tmp_path)
        
        result = upgrader.create_upgrade_backup("auth", "1.0")
        
        assert result["success"] is True
        assert result["backup_path"] is not None
        assert "auth" in result["backup_path"]

    def test_backup_directory_structure(self, tmp_path):
        """Should create proper backup directory structure."""
        from cortex.orchestrators.profile_upgrader import ProfileUpgrader
        
        # Create existing rules
        tier1_dir = tmp_path / "cortex_brain" / "tier1"
        tier1_dir.mkdir(parents=True)
        (tier1_dir / "domain-rules.yaml").write_text("rules: []\n")
        
        upgrader = ProfileUpgrader(tmp_path)
        upgrader.create_upgrade_backup("devops", "1.0")
        
        backups_dir = tmp_path / ".cortex" / "profile-backups"
        assert backups_dir.exists()
        assert len(list(backups_dir.glob("devops-*.yaml"))) >= 1
